//! One measurement session over a plan file (plan, sections 4-8 and 11).
//!
//! Start: TLS issuer check, slot clock, key (live only), payers, spend journal reconciled
//! with the chain, burst_seq recovery, funding, run row. Each burst: gossip and QUIC
//! connection about 30 slots before the window, blockhash 6 slots before, probes built,
//! signed and fsynced as rows, the whole burst booked in the journal, then sent at the
//! target moment minus RTT/2. End: bookings resolved, balance check, optional close.
//! Dry-run follows the same path with the dry-run wallet, opens the real connection and
//! closes it without a stream, and simulates the probes instead of sending them.

use crate::chain::{self, Leaders};
use crate::clock::{mono_ns, sleep_until_ns, utc_now};
use crate::journal::{check_balances, Journal};
use crate::keys::{self, Signer};
use crate::plan::{self, Burst, Plan, ProbeSpec, Round};
use crate::quic::{self, SendOutcome, StreamResult, Transport};
use crate::rows::{self, Level, Log, RowFile};
use crate::rpc::Rpc;
use crate::slots::{self, Model};
use crate::tx::{self, Config};
use crate::{Mode, SPEND_LIMIT_LAMPORTS};
use base64::Engine as _;
use serde_json::{json, Value};
use std::collections::BTreeSet;
use std::net::SocketAddr;
use std::path::{Path, PathBuf};
use std::time::Duration;

/// Gossip lookup and QUIC handshake this many slots before the window (section 5.1).
const PREPARE_SLOTS: u64 = 30;
/// Blockhash with commitment confirmed 4 to 8 slots before the window (section 4).
const BLOCKHASH_SLOTS: u64 = 6;
const LATEST_BLOCKHASH_SLOTS: u64 = 4;
const PRE300_NS: i64 = 300_000_000;
/// Waiting after the predicted window end before burst_end is written.
const WINDOW_TAIL_NS: i64 = 300_000_000;
/// Further waiting for the firstShredReceived events of the first two window slots. The
/// public mainnet WebSocket delivered events up to 36 slots late on 2026-10-26, about
/// 7.6 s; windows of a round stand MIN_GAP_SLOTS apart, so the next burst keeps its time.
const SHRED_WAIT_NS: i64 = 10_000_000_000;
const SHRED_POLL: Duration = Duration::from_millis(20);
/// Gossip entries kept per burst: leaders from a few slots before the window to the end
/// of the blockhash lifetime, where a late probe could still land (section 8).
const SNAPSHOT_SLOTS_BEFORE: u64 = 8;
const SNAPSHOT_SLOTS_AFTER: u64 = 160;
const CLOCK_WAIT: Duration = Duration::from_secs(150);
const CLOSE_FEE: u64 = tx::LAMPORTS_PER_SIGNATURE;
const RESOLVE_WAIT: Duration = Duration::from_secs(180);
/// Moment-condition bands of itb/prereg.py: estimated arrival within 100 ms of the target.
const BAND_HALF_MS: f64 = 100.0;
/// The send moment is re-aimed from the freshest slot event until this close to it.
const AIM_FINAL_NS: i64 = 2_000_000;
/// Clock guard (section 5.1): a burst is skipped when getSlot at processed commitment is
/// this many slots ahead of the slot the clock gives for the same moment. On node time
/// the clock leads processed (devnet 2026-10-26: gap -1 at the median, 0 at most), and
/// itb/prereg.py CLOCK_LAG_SKIP_SLOTS holds the same bound for the analysis.
pub const CLOCK_LAG_SKIP_SLOTS: i64 = 2;
const AIM_POLL: Duration = Duration::from_millis(5);

pub struct Settings {
    pub network: String,
    pub rpc_url: String,
    pub ws_url: String,
    pub data_dir: PathBuf,
    pub log_dir: PathBuf,
    pub state_dir: PathBuf,
    pub key_path: PathBuf,
    pub log_level: Level,
    /// Funded public address the dry-run simulates from (section 13); mainnet default
    /// is the address of the craft measurement.
    pub sim_payer: Option<String>,
    pub tool_version: String,
    pub git_commit: Option<String>,
}

impl Settings {
    pub fn from_env() -> Settings {
        let var = |k: &str, d: &str| std::env::var(k).unwrap_or_else(|_| d.to_string());
        let network = var("ITB_NETWORK", "mainnet");
        let sim_default = if network == "mainnet" { Some("BAPwtQzaPZYJQYeJjQbTiPXx55Gja9gX85qv8i9Jk6u9".to_string()) } else { None };
        Settings {
            rpc_url: var("ITB_RPC_URL", "https://api.mainnet-beta.solana.com"),
            ws_url: var("ITB_WS_URL", "wss://api.mainnet-beta.solana.com"),
            data_dir: var("ITB_DATA_DIR", "data").into(),
            log_dir: var("ITB_LOG_DIR", "logs").into(),
            state_dir: var("ITB_STATE_DIR", "state").into(),
            key_path: var("ITB_KEY_PATH", "/run/secrets/wallet_key").into(),
            log_level: Level::parse(&var("ITB_LOG_LEVEL", "info")),
            sim_payer: std::env::var("ITB_SIM_PAYER").ok().filter(|s| !s.is_empty()).or(sim_default),
            tool_version: env!("CARGO_PKG_VERSION").to_string(),
            git_commit: std::env::var("ITB_GIT_COMMIT").ok().filter(|s| !s.is_empty()),
            network,
        }
    }

    fn journal_path(&self) -> PathBuf {
        self.state_dir.join(format!("spend-journal-{}.jsonl", self.network))
    }
}

/// Section 11: the probe refuses to measure through a TLS-inspecting proxy. Plain http
/// and ws (a local test validator) have no certificate to check.
fn check_tls(s: &Settings, log: &mut Log) -> Result<(), String> {
    let mut seen = BTreeSet::new();
    for url in [&s.rpc_url, &s.ws_url] {
        let origin = rows::origin(url).replacen("wss://", "https://", 1);
        if !origin.starts_with("https://") || !seen.insert(origin.clone()) {
            continue;
        }
        let i = crate::tls::https_issuer(&origin)?;
        log.info("tls_issuer", None, json!({"host": i.host, "issuer": i.issuer, "verified": i.verified, "error": i.error}));
        println!("TLS issuer of {}: {} ({})", i.host, i.issuer, if i.verified { "verified" } else { "NOT verified" });
        if i.intercepted() {
            return Err(format!(
                "{} is re-signed by a local TLS-inspecting proxy ({}); add an exception for this host in the antivirus, the measurement does not run through it",
                i.host, i.issuer
            ));
        }
        if !i.verified {
            return Err(format!("{}: certificate not verified: {}", i.host, i.error.unwrap_or_default()));
        }
    }
    Ok(())
}

fn compact_utc() -> String {
    utc_now().replace(['-', ':'], "").split('.').next().unwrap_or("").to_string() + "Z"
}

fn wait_for_model(clock: &slots::Shared, log: &mut Log) -> Result<Model, String> {
    let start = std::time::Instant::now();
    loop {
        if let Some(m) = clock.lock().unwrap().model() {
            log.info(
                "slot_clock_ready",
                None,
                json!({"source": m.source.name(), "basis": m.basis.name(), "slot_ms": m.slot_ns / 1e6, "anchor_slot": m.anchor_slot,
                       "step_ms_by_window_position": m.step_ns.map(|s| s.map(|x| x / 1e6))}),
            );
            return Ok(m);
        }
        if start.elapsed() > CLOCK_WAIT {
            let st = clock.lock().unwrap();
            return Err(format!(
                "slot clock: no model after {} s ({} first-shred and {} slot events, last error {:?})",
                CLOCK_WAIT.as_secs(),
                st.first_shred.len(),
                st.slot_events.len(),
                st.last_error
            ));
        }
        std::thread::sleep(Duration::from_millis(500));
    }
}

/// One built probe of a burst.
struct Built {
    spec: ProbeSpec,
    payer: String,
    config: Config,
    message: tx::Message,
    signed: tx::Signed,
    signature: String,
    worst_fee: u64,
}

/// firstShredReceived of a slot: local receipt ns, node timestamp ms, node time ns.
type FirstShred = (Option<i64>, Option<u64>, Option<i64>);

/// What a burst left for the dry-run summary.
struct BurstNote {
    timing: String,
    /// Start of slot 2 from the start of slot 1, ms: the reference of the slot2 band.
    slot2_ms: f64,
    arrival_ms: Option<f64>,
    handshake_ok: Option<bool>,
    rtt_ms: Option<f64>,
}

/// The send moment as finally aimed, from the freshest slot event before it (section 5.1).
struct Aim {
    anchor_slot: u64,
    predicted: i64,
    target: i64,
    rtt_ns: Option<i64>,
    send_at: i64,
}

enum BurstEnd {
    Done(BurstNote),
    Skipped(String),
}

/// getSlot at processed commitment next to the clock (section 5.1).
struct ClockCheck {
    http_slot: Option<u64>,
    rtt_ns: i64,
    clock_slot: u64,
    lag: Option<i64>,
}

struct Session {
    live: bool,
    run_id: String,
    run_dir: PathBuf,
    rpc: Rpc,
    log: Log,
    rows: RowFile,
    journal: Option<Journal>,
    clock: slots::Shared,
    leaders: Leaders,
    rt: tokio::runtime::Runtime,
    transport: Transport,
    payers: Vec<Signer>,
    sim_payer: Option<[u8; 32]>,
    plan_dir: PathBuf,
}

pub fn run(s: &Settings, mode: &Mode, plan_path: &Path, close_after: bool) -> Result<(), String> {
    let mut payers = None;
    let result = run_session(s, mode, plan_path, close_after, &mut payers);
    // Every exit prints the payer balances (section 11), a failed one too.
    if let Some(addrs) = payers {
        print_balances(&mut Rpc::new(&s.rpc_url), &addrs);
    }
    result
}

fn run_session(s: &Settings, mode: &Mode, plan_path: &Path, close_after: bool, shown: &mut Option<Vec<String>>) -> Result<(), String> {
    let text = std::fs::read_to_string(plan_path).map_err(|e| format!("plan {}: {e}", plan_path.display()))?;
    let plan = plan::parse(&text)?;
    if plan.network != s.network {
        return Err(format!("plan is for {}, ITB_NETWORK is {}", plan.network, s.network));
    }
    // Snapshots the plan was drawn from travel with the run (schema files: snapshots/).
    let plan_dir = plan_path.parent().map(Path::to_path_buf).unwrap_or_default();
    for r in &plan.rounds {
        for name in [Some(&r.cluster_nodes_file), Some(&r.leader_schedule_file), r.validators_app_file.as_ref()].into_iter().flatten() {
            if !plan_dir.join(name).is_file() {
                return Err(format!("plan round {}: snapshot {name} not found next to the plan", r.round));
            }
        }
    }
    let live = matches!(mode, Mode::Live { .. });
    let limit = match mode {
        Mode::Live { max_spend_lamports } => *max_spend_lamports,
        Mode::DryRun => SPEND_LIMIT_LAMPORTS,
    };
    let stage = if live { plan.stage.clone() } else { "dry-run".to_string() };
    let run_id = format!("{stage}-{}-{}", s.network, compact_utc());
    let run_dir = s.data_dir.join("runs").join(&run_id);
    let mut log = Log::open(&s.log_dir.join(format!("{run_id}.jsonl")), s.log_level, &run_id)?;
    let bursts = plan::bursts_in_order(&plan);
    log.info(
        "start",
        None,
        json!({"mode": if live { "live" } else { "dry-run" }, "spend_limit_lamports": limit, "code_limit_lamports": SPEND_LIMIT_LAMPORTS,
               "network": s.network, "rpc": rows::origin(&s.rpc_url), "ws": rows::origin(&s.ws_url),
               "plan": plan_path.display().to_string(), "bursts": bursts.len()}),
    );
    println!("itb-probe {} run {run_id}: {} bursts, spend limit {limit} lamports", if live { "LIVE" } else { "dry-run" }, bursts.len());

    check_tls(s, &mut log)?;

    // Dry-run never reads the key (section 11); live without one refuses by name.
    let wallet = if live {
        match keys::load_wallet(&s.key_path)? {
            Some(w) => w,
            None => {
                let e = format!("live mode needs the wallet key at {}; found none (a missing secret file mounts as an empty directory)", s.key_path.display());
                log.error("no_key", None, json!({"path": s.key_path.display().to_string()}));
                return Err(e);
            }
        }
    } else {
        keys::dry_run_wallet()
    };
    let payers = keys::derive_payers(&wallet);
    let payer_addrs: Vec<String> = payers.iter().map(Signer::address).collect();
    *shown = Some(payer_addrs.clone());
    let wallet_addr = wallet.address();

    let mut rpc = Rpc::new(&s.rpc_url);
    let clock = slots::start(s.ws_url.clone());
    let data = chain::scan_data(&s.data_dir)?;

    let mut journal = None;
    let mut chain_seq = None;
    if live {
        let mut j = Journal::open(&s.journal_path(), limit)?;
        if j.torn_line {
            log.warn("journal_torn_line_dropped", None, json!({"path": j.path().display().to_string()}));
        }
        chain::resolve_pending(&mut rpc, &mut j, &mut log, Duration::ZERO)?;
        let cs = chain::scan_chain(&mut rpc, &mut j, &wallet_addr, &payer_addrs, &data.signatures)?;
        let adjust = j.adjust_to(cs.fee_total)?;
        log.info(
            "journal_reconciled",
            None,
            json!({"committed": j.committed(), "chain_fee_total": cs.fee_total, "adjust": adjust,
                   "chain_signatures": cs.signatures, "fetched": cs.fetched, "chain_max_burst_seq": cs.max_burst_seq}),
        );
        chain_seq = cs.max_burst_seq;
        journal = Some(j);
    }
    let first_seq = data.max_burst_seq.max(chain_seq).map_or(0, |m| m + 1);

    // The whole plan must fit under the limit before anything is sent.
    let plan_worst: u64 = bursts
        .iter()
        .flat_map(|(_, b)| b.probes.iter())
        .map(|p| tx::worst_fee(1, config_of(p)))
        .fold(0, u64::saturating_add);
    let overhead = CLOSE_FEE + if close_after { CLOSE_FEE * keys::PAYERS as u64 } else { 0 };
    let committed = journal.as_ref().map_or(0, Journal::committed);
    log.info("plan_cost", None, json!({"worst_fee_lamports": plan_worst, "overhead_lamports": overhead, "committed": committed, "limit": limit}));
    println!(
        "plan worst-case fees {plan_worst} lamports plus {overhead} for funding and closing; committed {committed}; limit {limit} ({:.1}% used after the plan)",
        100.0 * committed.saturating_add(plan_worst).saturating_add(overhead) as f64 / limit as f64
    );
    if committed.saturating_add(plan_worst).saturating_add(overhead) > limit {
        let e = format!(
            "spend limit: the plan needs up to {} lamports, the limit {limit} leaves {}",
            plan_worst.saturating_add(overhead),
            limit.saturating_sub(committed)
        );
        log.error("limit_refusal", None, json!({"message": e}));
        return Err(e);
    }

    let schedule = chain::EpochSchedule::from_json(&rpc.epoch_schedule()?)?;
    let model = wait_for_model(&clock, &mut log)?;
    println!("slot clock: {} at {:.1} ms per slot", model.source.name(), model.slot_ns / 1e6);

    let mut before_total = None;
    let mut settled_before = 0;
    if live {
        let j = journal.as_mut().unwrap();
        let now_slot = model.slot_at(mono_ns());
        let mut needs = vec![CLOSE_FEE; keys::PAYERS];
        for (_, b) in &bursts {
            if b.first_slot > now_slot + PREPARE_SLOTS {
                for p in &b.probes {
                    needs[p.payer_index as usize - 1] += tx::worst_fee(1, config_of(p));
                }
            }
        }
        let mut all = vec![wallet_addr.clone()];
        all.extend(payer_addrs.iter().cloned());
        before_total = Some(rpc.balances(&all)?.iter().sum::<u64>());
        settled_before = j.settled_total();
        fund(&mut rpc, j, &mut log, &wallet, &payers, &needs)?;
    }

    let mut rows = RowFile::create_new(&run_dir.join("probes.jsonl"))?;
    rows.write(
        "run",
        json!({"run_id": run_id, "stage": stage, "network": s.network, "mode": if live { "live" } else { "dry-run" },
               "spend_limit_lamports": limit, "code_limit_lamports": SPEND_LIMIT_LAMPORTS,
               "rpc_url": rows::origin(&s.rpc_url), "ws_url": rows::origin(&s.ws_url),
               "tool_version": s.tool_version, "git_commit": s.git_commit, "started_utc": utc_now(),
               "wallet": if live { Some(wallet_addr.clone()) } else { None }, "payers": payer_addrs,
               "doubling": plan.doubling, "prereg_manifest_sha256": plan.prereg_manifest_sha256,
               "seed_table_sha256": plan.seed_table_sha256}),
    )?;
    rows.sync()?;

    let rt = tokio::runtime::Builder::new_multi_thread()
        .worker_threads(2)
        .enable_all()
        .build()
        .map_err(|e| format!("tokio runtime: {e}"))?;
    let transport = {
        let _guard = rt.enter();
        Transport::new()?
    };
    let sim_payer = s.sim_payer.as_deref().map(crate::b58::decode32).transpose().map_err(|e| format!("ITB_SIM_PAYER: {e}"))?;
    let mut ses = Session {
        live,
        run_id: run_id.clone(),
        run_dir: run_dir.clone(),
        rpc,
        log,
        rows,
        journal,
        clock,
        leaders: Leaders::new(schedule),
        rt,
        transport,
        payers,
        sim_payer,
        plan_dir,
    };

    // finish runs after a failed burst loop too: bookings get resolved and balances checked.
    let result = ses.run_bursts(&plan, &bursts, first_seq);
    let result = result.and(ses.finish(&wallet_addr, &payer_addrs, before_total, settled_before, close_after));
    if !ses.rows.schema_problems.is_empty() {
        let n = ses.rows.schema_problems.len();
        ses.log.error("schema_problems", None, json!({"count": n, "first": ses.rows.schema_problems[..n.min(5)]}));
        return Err(format!("{n} rows of this run do not match schema/raw-format.json; first: {}", ses.rows.schema_problems[0]));
    }
    result
}

/// Copy one snapshot of the plan into the run; returns its name relative to the run.
fn copy_snapshot(plan_dir: &Path, run_dir: &Path, round: u64, name: &str) -> Result<String, String> {
    // plan::check already refused paths; this copy refuses them again on its own.
    if !crate::plan::plain_file_name(name) {
        return Err(format!("snapshot {name:?} is not a plain file name beside the plan"));
    }
    // A symlink beside the plan could still point at the key; only a regular file is copied.
    // A hard link cannot reach /run/secrets, a separate mount from the data volume.
    let src = plan_dir.join(name);
    let meta = std::fs::symlink_metadata(&src).map_err(|e| format!("snapshot {name}: {e}"))?;
    if !meta.file_type().is_file() {
        return Err(format!("snapshot {name:?} is not a regular file"));
    }
    // The copy reads the handle opened here, so a swap after the check above cannot redirect it.
    let mut file = open_regular(&src).map_err(|e| format!("snapshot {name:?} is not a regular file: {e}"))?;
    let rel = format!("snapshots/round{round}-{name}");
    let dst = run_dir.join(&rel);
    std::fs::create_dir_all(dst.parent().unwrap()).map_err(|e| e.to_string())?;
    // create_new refuses an existing name, a planted symlink included.
    let mut out = std::fs::OpenOptions::new().write(true).create_new(true).open(&dst).map_err(|e| format!("snapshot {rel}: {e}"))?;
    std::io::copy(&mut file, &mut out).map_err(|e| format!("snapshot {name}: {e}"))?;
    Ok(rel)
}

/// Open a file for reading only if the name itself is a regular file: on Unix the open refuses
/// a symlink (O_NOFOLLOW) and the type check runs on the open handle. Windows builds serve
/// development only and rely on the symlink_metadata check before this call.
fn open_regular(path: &Path) -> std::io::Result<std::fs::File> {
    let mut opts = std::fs::OpenOptions::new();
    opts.read(true);
    #[cfg(unix)]
    {
        use std::os::unix::fs::OpenOptionsExt;
        // O_NONBLOCK keeps a FIFO from stalling the open; a regular file reads as usual.
        opts.custom_flags(libc::O_NOFOLLOW | libc::O_NONBLOCK);
    }
    let file = opts.open(path)?;
    if !file.metadata()?.is_file() {
        return Err(std::io::Error::new(std::io::ErrorKind::InvalidInput, "not a regular file"));
    }
    Ok(file)
}

fn config_of(p: &ProbeSpec) -> Config {
    Config { priority_fee: p.priority_fee_lamports, cu_limit: p.cu_limit, loaded_data_limit: p.loaded_data_limit }
}

/// Lamports a v1 transaction pays with no priority fee: one signature.
fn plain_config(instructions: usize) -> Config {
    Config { priority_fee: 0, cu_limit: tx::PROBE_CU_LIMIT + 300 * instructions as u32, loaded_data_limit: tx::PROBE_LOADED_DATA }
}

/// Top up each payer to rent plus what this session can spend from it, in one v1
/// transaction from the wallet. The funding fee goes through the journal like any other.
fn fund(rpc: &mut Rpc, journal: &mut Journal, log: &mut Log, wallet: &Signer, payers: &[Signer], needs: &[u64]) -> Result<(), String> {
    let rent = rpc.min_rent(0)?;
    let addrs: Vec<String> = payers.iter().map(Signer::address).collect();
    let balances = rpc.balances(&addrs)?;
    let deficits: Vec<u64> = balances.iter().zip(needs).map(|(b, n)| (rent + n).saturating_sub(*b)).collect();
    let total: u64 = deficits.iter().fold(0, |a, &d| a.saturating_add(d));
    log.info("payer_balances", None, json!({"balances": balances, "rent": rent, "needs": needs, "deficits": deficits}));
    if total == 0 {
        return Ok(());
    }
    let wallet_balance = rpc.balances(&[wallet.address()])?[0];
    if wallet_balance < total + CLOSE_FEE + rent {
        return Err(format!(
            "wallet {} holds {wallet_balance} lamports; funding the payers needs {total} plus {CLOSE_FEE} fee and {rent} wallet rent",
            wallet.address()
        ));
    }
    let ixs: Vec<tx::Instruction> = payers
        .iter()
        .zip(&deficits)
        .filter(|(_, d)| **d > 0)
        .map(|(p, d)| tx::transfer(wallet.pubkey(), p.pubkey(), *d))
        .collect();
    let (hash, lvbh, _) = rpc.latest_blockhash("confirmed")?;
    let msg = tx::message_v1(wallet.pubkey(), &ixs, crate::b58::decode32(&hash)?, plain_config(ixs.len()))?;
    let signed = tx::sign(&msg, &[wallet])?;
    let sig = crate::b58::encode(&signed.signature);
    journal.book(&[(sig.clone(), CLOSE_FEE, lvbh)], "fund")?;
    log.info("fund_send", None, json!({"signature": sig, "lamports": total, "payers": deficits.iter().filter(|d| **d > 0).count()}));
    rpc.send(&signed.wire, false, None)?;
    let left = chain::resolve_pending(rpc, journal, log, RESOLVE_WAIT)?;
    match journal.entry(&sig) {
        Some(crate::journal::Entry::Settled { .. }) => {}
        _ => return Err(format!("funding transaction {sig} did not finalize ({left} bookings pending)")),
    }
    let after = rpc.balances(&addrs)?;
    if after.iter().zip(needs).any(|(b, n)| *b < rent + n) {
        return Err(format!("funding transaction {sig} finalized but the payers hold {after:?}"));
    }
    log.info("funded", None, json!({"signature": sig, "balances": after}));
    Ok(())
}

/// Return every payer's balance minus its fee to the wallet (section 11). Fees are booked
/// first, all at once; a payer at or below the fee keeps its dust.
pub fn close_payers(rpc: &mut Rpc, journal: &mut Journal, log: &mut Log, wallet: &str, payers: &[Signer]) -> Result<Vec<u64>, String> {
    let addrs: Vec<String> = payers.iter().map(Signer::address).collect();
    let balances = rpc.balances(&addrs)?;
    let to = crate::b58::decode32(wallet)?;
    let (hash, lvbh, _) = rpc.latest_blockhash("confirmed")?;
    let hash = crate::b58::decode32(&hash)?;
    let mut txs = vec![];
    for (p, b) in payers.iter().zip(&balances) {
        if *b <= CLOSE_FEE {
            if *b > 0 {
                log.warn("close_dust", None, json!({"payer": p.address(), "lamports": b}));
            }
            continue;
        }
        let msg = tx::message_v1(p.pubkey(), &[tx::transfer(p.pubkey(), to, b - CLOSE_FEE)], hash, plain_config(1))?;
        let signed = tx::sign(&msg, &[p])?;
        txs.push((crate::b58::encode(&signed.signature), signed.wire, p.address(), *b));
    }
    if txs.is_empty() {
        return Ok(balances);
    }
    let items: Vec<(String, u64, u64)> = txs.iter().map(|t| (t.0.clone(), CLOSE_FEE, lvbh)).collect();
    journal.book(&items, "close")?;
    for (sig, wire, payer, lamports) in &txs {
        log.info("close_send", None, json!({"signature": sig, "payer": payer, "lamports": lamports}));
        if let Err(e) = rpc.send(wire, false, None) {
            log.error("close_send_failed", None, json!({"signature": sig, "payer": payer, "error": e.to_string()}));
        }
    }
    chain::resolve_pending(rpc, journal, log, RESOLVE_WAIT)?;
    let after = rpc.balances(&addrs)?;
    log.info("closed", None, json!({"balances": after}));
    Ok(after)
}

impl Session {
    fn run_bursts(&mut self, plan: &Plan, bursts: &[(&Round, &Burst)], first_seq: u64) -> Result<(), String> {
        let mut written_rounds = BTreeSet::new();
        let mut notes = vec![];
        let seqs: Vec<u64> = (0..bursts.len() as u64).map(|k| first_seq + k).collect();
        for (k, (round, burst)) in bursts.iter().enumerate() {
            let seq = seqs[k];
            if written_rounds.insert(round.round) {
                let windows: Vec<Value> = bursts
                    .iter()
                    .zip(&seqs)
                    .filter(|((r, _), _)| r.round == round.round)
                    .map(|((_, b), q)| json!({"leader": b.leader, "first_slot": b.first_slot, "burst_seq": q}))
                    .collect();
                let nodes_file = self.copy_snapshot(round.round, &round.cluster_nodes_file)?;
                let schedule_file = self.copy_snapshot(round.round, &round.leader_schedule_file)?;
                let va_file = round.validators_app_file.as_ref().map(|f| self.copy_snapshot(round.round, f)).transpose()?;
                self.rows.write(
                    "round",
                    json!({"run_id": self.run_id, "round": round.round, "epoch": round.epoch, "part": round.part,
                           "anchor_utc": round.anchor_utc, "anchor_slot": round.anchor_slot,
                           "cluster_nodes_file": nodes_file, "leader_schedule_file": schedule_file,
                           "validators_app_file": va_file, "validators_app_utc": round.validators_app_utc,
                           "windows": windows}),
                )?;
                self.rows.sync()?;
            }
            match self.burst(round, burst, seq) {
                Ok(BurstEnd::Done(n)) => notes.push(n),
                Ok(BurstEnd::Skipped(why)) => {
                    self.log.warn("burst_skipped", Some(seq), json!({"reason": why, "first_slot": burst.first_slot, "leader": burst.leader}));
                    println!("burst {seq} at slot {} skipped: {why}", burst.first_slot);
                }
                Err(e) if e.starts_with("spend limit") => {
                    self.log.error("limit_refusal", Some(seq), json!({"message": e}));
                    return Err(e);
                }
                Err(e) => {
                    self.log.error("burst_failed", Some(seq), json!({"error": e, "first_slot": burst.first_slot}));
                    println!("burst {seq} at slot {} failed: {e}", burst.first_slot);
                }
            }
        }
        self.summary(plan, &notes);
        Ok(())
    }

    fn copy_snapshot(&self, round: u64, name: &str) -> Result<String, String> {
        copy_snapshot(&self.plan_dir, &self.run_dir, round, name)
    }

    fn summary(&mut self, _plan: &Plan, notes: &[BurstNote]) {
        let done = notes.len();
        let in_band = notes
            .iter()
            .filter(|n| {
                let target = if n.timing == "pre300" { -300.0 } else { n.slot2_ms };
                n.arrival_ms.is_some_and(|a| (a - target).abs() <= BAND_HALF_MS)
            })
            .count();
        let mut arrivals: Vec<f64> = notes.iter().filter_map(|n| n.arrival_ms).collect();
        arrivals.sort_by(|a, b| a.total_cmp(b));
        let hs: Vec<bool> = notes.iter().filter_map(|n| n.handshake_ok).collect();
        let mut rtts: Vec<f64> = notes.iter().filter_map(|n| n.rtt_ms).collect();
        rtts.sort_by(|a, b| a.total_cmp(b));
        let q = |v: &[f64], p: f64| if v.is_empty() { None } else { Some(v[((v.len() - 1) as f64 * p).round() as usize]) };
        let data = json!({"bursts_done": done, "in_timing_band": in_band,
                          "arrival_ms_min_median_max": [q(&arrivals, 0.0), q(&arrivals, 0.5), q(&arrivals, 1.0)],
                          "handshakes_ok": hs.iter().filter(|x| **x).count(), "handshakes": hs.len(),
                          "rtt_ms_min_median_max": [q(&rtts, 0.0), q(&rtts, 0.5), q(&rtts, 1.0)]});
        self.log.info("summary", None, data.clone());
        println!("summary: {data}");
    }

    fn model(&self) -> Option<Model> {
        self.clock.lock().unwrap().model()
    }

    /// Wait up to SHRED_WAIT_NS for the firstShredReceived events of the first two window
    /// slots, which a WebSocket backlog delivers seconds late; a skipped slot has none.
    fn wait_first_shreds(&self, first_slot: u64) {
        let deadline = mono_ns() + SHRED_WAIT_NS;
        loop {
            let seen = {
                let st = self.clock.lock().unwrap();
                st.first_shred.contains_key(&first_slot) && st.first_shred.contains_key(&(first_slot + 1))
            };
            if seen || mono_ns() >= deadline {
                return;
            }
            std::thread::sleep(SHRED_POLL);
        }
    }

    /// firstShredReceived of a slot: local receipt, node timestamp, and node time on the
    /// local clock, which is the receipt the event would have had without backlog.
    fn first_shred(&self, slot: u64) -> FirstShred {
        let st = self.clock.lock().unwrap();
        let node = st.node_time(slot, st.node_offset_ns());
        match st.first_shred.get(&slot) {
            Some((ns, ts)) => (Some(*ns), *ts, node),
            None => (None, None, None),
        }
    }

    fn clock_check(&mut self, model: &Model) -> ClockCheck {
        let t0 = mono_ns();
        let http = match self.rpc.call("getSlot", json!([{"commitment": "processed"}])) {
            Ok(v) => v.as_u64(),
            Err(e) => {
                self.log.warn("clock_check_failed", None, json!({"error": e.to_string()}));
                None
            }
        };
        let t1 = mono_ns();
        let clock_slot = model.slot_at(t0 + (t1 - t0) / 2);
        ClockCheck { http_slot: http, rtt_ns: t1 - t0, clock_slot, lag: http.map(|h| h as i64 - clock_slot as i64) }
    }

    fn burst(&mut self, round: &Round, b: &Burst, seq: u64) -> Result<BurstEnd, String> {
        let Some(model) = self.model() else { return Ok(BurstEnd::Skipped("slot clock has no model".into())) };
        if mono_ns() > model.predict(b.first_slot.saturating_sub(LATEST_BLOCKHASH_SLOTS)) {
            return Ok(BurstEnd::Skipped("window too close or past".into()));
        }
        for slot in b.first_slot..b.first_slot + b.window_len {
            let l = self.leaders.leader(&mut self.rpc, slot);
            if l.as_deref() != Some(b.leader.as_str()) {
                return Ok(BurstEnd::Skipped(format!("leader schedule gives {l:?} for slot {slot}, the plan {}", b.leader)));
            }
        }
        sleep_until_ns(model.predict(b.first_slot.saturating_sub(PREPARE_SLOTS)));

        // Gossip at the burst (section 5.3): clientId and tpuQuic can change between windows.
        let nodes = self.rpc.cluster_nodes()?;
        let node = chain::node(&nodes, &b.leader).cloned();
        let tpu_quic = node.as_ref().and_then(|n| n["tpuQuic"].as_str()).map(String::from);
        let tpu_addr: Option<SocketAddr> = tpu_quic.as_deref().and_then(|t| t.parse().ok());
        let snapshot_file = self.snapshot(&nodes, b, seq)?;

        let mut reconnects = 0u64;
        let mut handshake = None;
        let mut conn = None;
        if b.path == "quic" {
            match tpu_addr {
                Some(addr) => match self.rt.block_on(self.transport.connect(addr)) {
                    Ok(c) => {
                        self.log.info("quic_connected", Some(seq), json!({"tpu_quic": addr.to_string(), "rtt_ns": c.rtt().as_nanos() as u64}));
                        conn = Some(c);
                    }
                    Err(e) => {
                        self.log.warn("quic_connect_failed", Some(seq), json!({"tpu_quic": addr.to_string(), "error": e}));
                        handshake = Some(json!({"ok": false, "close_code": null, "rtt_ns": null, "error": e}));
                    }
                },
                None => {
                    handshake = Some(json!({"ok": false, "close_code": null, "rtt_ns": null, "error": "no tpuQuic in gossip"}));
                }
            }
        }

        let model = self.model().unwrap_or(model);
        sleep_until_ns(model.predict(b.first_slot.saturating_sub(BLOCKHASH_SLOTS)));
        let (hash, lvbh, hash_slot) = self.rpc.latest_blockhash("confirmed")?;
        let hash32 = crate::b58::decode32(&hash)?;
        if conn.is_none() && b.path == "quic" {
            if let Some(addr) = tpu_addr {
                if let Ok(c) = self.rt.block_on(self.transport.connect(addr)) {
                    reconnects += 1;
                    handshake = None;
                    conn = Some(c);
                }
            }
        }

        let built = self.build(b, seq, hash32)?;
        let model = self.model().unwrap_or(model);
        // A clock behind the cluster would aim the burst at the wrong window and the
        // arrival estimate would not show it, so the burst stops here, before any row.
        let check = self.clock_check(&model);
        if let Some(lag) = check.lag.filter(|l| *l >= CLOCK_LAG_SKIP_SLOTS) {
            if let Some(c) = conn.as_ref() {
                quic::close(c, b"clock behind");
            }
            return Ok(BurstEnd::Skipped(format!(
                "slot clock {lag} slots behind getSlot processed {} ({} on {})",
                check.http_slot.unwrap_or(0),
                model.source.name(),
                model.basis.name()
            )));
        }
        let predicted = model.predict(b.first_slot);
        let target = if b.timing == "pre300" { predicted - PRE300_NS } else { model.predict(b.first_slot + 1) };
        let rtt_ns = conn.as_ref().map(|c| c.rtt().as_nanos() as i64);
        let send_at = target - rtt_ns.unwrap_or(0) / 2;
        let anchor_leader = self.leaders.leader(&mut self.rpc, model.anchor_slot);
        let host = tpu_quic.as_deref().and_then(|t| t.rsplit_once(':'));
        let gossip_ip = node.as_ref().and_then(|n| n["gossip"].as_str()).and_then(|g| g.rsplit_once(':')).map(|x| x.0.to_string());
        if !self.live && b.path == "quic" && handshake.is_none() {
            handshake = Some(json!({"ok": conn.is_some(), "close_code": null, "rtt_ns": rtt_ns, "error": null}));
        }
        // Schema version 2 fields of the clock guard; one json! of all fields would pass
        // the macro recursion limit.
        let guard = json!({"slot_clock_basis": model.basis.name(), "clock_offset_ns": model.offset_ns,
                           "http_slot": check.http_slot, "http_slot_rtt_ns": check.rtt_ns,
                           "clock_slot_at_http": check.clock_slot, "clock_lag_slots": check.lag});
        let mut row = json!({"run_id": self.run_id, "burst_seq": seq, "round": round.round, "cell": b.cell, "arm": b.arm,
                   "timing": b.timing, "path": b.path, "epoch": self.leaders.schedule.epoch_of(b.first_slot),
                   "first_slot": b.first_slot, "window_len": b.window_len, "selection_class": b.selection_class,
                   "leader": b.leader, "leader_vote": b.leader_vote,
                   "leader_client_id": node.as_ref().and_then(|n| n["clientId"].as_str()),
                   "leader_version": node.as_ref().and_then(|n| n["version"].as_str()),
                   "tpu_quic": tpu_quic, "tpu_quic_port": host.and_then(|h| h.1.parse::<u64>().ok()),
                   "gossip_ip": gossip_ip, "relayer_default_port": host.is_some_and(|h| h.1 == "11228"),
                   "fee_collector": null, "validators_app": b.validators_app, "cluster_nodes_file": snapshot_file,
                   "equal_fee_lamports": b.equal_fee_lamports, "blockhash": hash, "last_valid_block_height": lvbh,
                   "blockhash_context_slot": hash_slot, "utc": utc_now(), "slot_clock_source": model.source.name(),
                   "slot_ms": model.slot_ns / 1e6, "anchor_slot": model.anchor_slot, "anchor_leader": anchor_leader,
                   "predicted_first_slot_ns": predicted, "target_arrival_ns": target, "rtt_ns": rtt_ns,
                   "send_at_ns": send_at, "handshake": handshake});
        if let (Some(r), Value::Object(g)) = (row.as_object_mut(), guard) {
            r.extend(g);
        }
        self.rows.write("burst", row)?;
        let b64 = base64::engine::general_purpose::STANDARD;
        for p in &built {
            self.rows.write(
                "probe",
                json!({"run_id": self.run_id, "burst_seq": seq, "signature": p.signature, "payer_index": p.spec.payer_index,
                       "payer": p.payer, "send_rank": p.spec.send_rank,
                       "transfer_lamports": tx::probe_amount(seq, p.spec.send_rank),
                       "priority_fee_lamports": p.config.priority_fee, "cu_limit": p.config.cu_limit,
                       "loaded_data_limit": p.config.loaded_data_limit,
                       "write_accounts": p.message.write_accounts.iter().map(|k| crate::b58::encode(k)).collect::<Vec<_>>(),
                       "tx_version": "v1", "worst_fee_lamports": p.worst_fee, "wire_bytes": p.signed.wire.len(),
                       "tx_b64": b64.encode(&p.signed.wire)}),
            )?;
        }
        // Rows reach the disk before anything leaves the machine (section 8).
        self.rows.sync()?;

        let deliverable = b.path == "rpc" || conn.is_some();
        if self.live && deliverable {
            let items: Vec<(String, u64, u64)> = built.iter().map(|p| (p.signature.clone(), p.worst_fee, lvbh)).collect();
            if let Err(e) = self.journal.as_mut().unwrap().book(&items, "probe") {
                self.not_sent(seq, &built, &e)?;
                return Err(e);
            }
        }
        if self.live && !deliverable {
            let why = handshake.as_ref().and_then(|h| h["error"].as_str()).unwrap_or("no connection").to_string();
            self.not_sent(seq, &built, &format!("not sent: {why}"))?;
            self.end_row(seq, None, b, predicted, None, &[], reconnects)?;
            let slot2_ms = (model.predict(b.first_slot + 1) - predicted) as f64 / 1e6;
            return Ok(BurstEnd::Done(BurstNote { timing: b.timing.clone(), slot2_ms, arrival_ms: None, handshake_ok: Some(false), rtt_ms: None }));
        }

        let aim = self.aim(b, conn.as_ref(), model);
        let send_at = aim.send_at;
        sleep_until_ns(send_at);
        let interval = b.send_interval_us as i64 * 1000;
        let mut outcomes: Vec<SendOutcome> = vec![];
        let mut rpc_responses: Vec<Option<Value>> = vec![];
        if self.live && b.path == "quic" {
            let mut handles = vec![];
            for (i, p) in built.iter().enumerate() {
                if interval > 0 {
                    sleep_until_ns(send_at + i as i64 * interval);
                }
                let c = conn.as_ref().unwrap();
                if c.close_reason().is_some() {
                    let addr = tpu_addr.unwrap();
                    self.log.warn("quic_reconnect", Some(seq), json!({"reason": c.close_reason().map(|r| r.to_string())}));
                    if let Ok(n) = self.rt.block_on(self.transport.connect(addr)) {
                        reconnects += 1;
                        conn = Some(n);
                    }
                }
                let c = conn.as_ref().unwrap();
                handles.push(self.rt.block_on(self.transport.send(c, p.signed.wire.clone())));
            }
            for h in handles {
                outcomes.push(self.rt.block_on(h).map_err(|e| format!("send task: {e}"))?);
            }
        } else if self.live {
            for (i, p) in built.iter().enumerate() {
                if interval > 0 {
                    sleep_until_ns(send_at + i as i64 * interval);
                }
                let t0 = mono_ns();
                let r = self.rpc.send(&p.signed.wire, true, Some(0));
                let t1 = mono_ns();
                let (result, error, resp) = match r {
                    Ok(sig) => (StreamResult::Finished, None, Some(json!({"result": sig}))),
                    Err(e) => (StreamResult::ConnectionClosed(None), Some(e.to_string()), Some(json!({"error": {"code": e.code, "message": e.message}}))),
                };
                outcomes.push(SendOutcome { send_end_ns: Some(t0), stopped_ns: Some(t1), result, error });
                rpc_responses.push(resp);
            }
        } else {
            // Dry-run: the marks a send would have, no stream (section 11).
            for i in 0..built.len() {
                if interval > 0 {
                    sleep_until_ns(send_at + i as i64 * interval);
                }
                outcomes.push(SendOutcome { send_end_ns: Some(mono_ns()), stopped_ns: None, result: StreamResult::Finished, error: None });
            }
            if let Some(c) = conn.as_ref() {
                quic::close(c, b"dry-run");
            }
            if self.transport.streams_opened() != 0 {
                return Err(format!("dry-run opened {} streams", self.transport.streams_opened()));
            }
        }

        sleep_until_ns(self.model().unwrap_or(model).predict(b.first_slot + b.window_len) + WINDOW_TAIL_NS);
        self.wait_first_shreds(b.first_slot);
        for (i, p) in built.iter().enumerate() {
            let o = &outcomes[i];
            let (result, simulate, error) = if self.live {
                let name = if b.path == "rpc" {
                    if o.error.is_none() { "rpc_ok" } else { "rpc_error" }
                } else {
                    o.result.name()
                };
                (name.to_string(), Value::Null, o.error.clone())
            } else {
                self.simulate(b, seq, p, hash32)
            };
            self.rows.write(
                "send",
                json!({"run_id": self.run_id, "burst_seq": seq, "signature": p.signature, "result": result,
                       "code": if self.live && b.path == "quic" { o.result.code() } else { None },
                       "send_end_ns": o.send_end_ns, "stopped_ns": o.stopped_ns,
                       "rpc_response": rpc_responses.get(i).cloned().flatten(), "simulate": simulate, "error": error}),
            )?;
        }
        let first_send = outcomes.first().and_then(|o| o.send_end_ns);
        let sends: Vec<i64> = outcomes.iter().filter_map(|o| o.send_end_ns).collect();
        // The log line and the summary read the same events as burst_end, so they agree
        // with itb/analyze.py.
        let [(fs1, ts1, n1), (fs2, ts2, _)] = self.end_row(seq, conn.as_ref(), b, predicted, Some(&aim), &sends, reconnects)?;
        if let Some(c) = conn.as_ref() {
            if self.live {
                quic::close(c, b"burst end");
            }
        }
        self.rows.sync()?;

        let base = n1.or(fs1).unwrap_or(aim.predicted);
        let arrival_ms = first_send.map(|t| (t - base + aim.rtt_ns.unwrap_or(0) / 2) as f64 / 1e6);
        let note = BurstNote {
            timing: b.timing.clone(),
            // Start of slot 2 as observed on node time, else on receipt, else as finally
            // aimed (itb/analyze.py slot2_ms).
            slot2_ms: match (ts1, ts2, fs1, fs2) {
                (Some(a), Some(c), _, _) => c as f64 - a as f64,
                (_, _, Some(a), Some(c)) => (c - a) as f64 / 1e6,
                _ if b.timing == "slot2" => (aim.target - aim.predicted) as f64 / 1e6,
                _ => (self.model().unwrap_or(model).predict(b.first_slot + 1) - aim.predicted) as f64 / 1e6,
            },
            arrival_ms,
            handshake_ok: (b.path == "quic").then_some(conn.is_some()),
            rtt_ms: aim.rtt_ns.map(|r| r as f64 / 1e6),
        };
        let results: Vec<String> = outcomes.iter().map(|o| o.result.name().to_string()).collect();
        self.log.info(
            "burst_done",
            Some(seq),
            json!({"first_slot": b.first_slot, "leader": b.leader, "arm": b.arm, "timing": b.timing, "path": b.path,
                   "arrival_ms": arrival_ms, "rtt_ms": note.rtt_ms, "results": if self.live { json!(results) } else { Value::Null }}),
        );
        println!(
            "burst {seq} slot {} {} {} {}: est. arrival {} ms from slot start, rtt {} ms",
            b.first_slot,
            b.arm,
            b.timing,
            b.path,
            arrival_ms.map_or("?".into(), |a| format!("{a:.1}")),
            note.rtt_ms.map_or("-".into(), |r| format!("{r:.1}"))
        );
        Ok(BurstEnd::Done(note))
    }

    fn build(&self, b: &Burst, seq: u64, hash: [u8; 32]) -> Result<Vec<Built>, String> {
        let mut out = vec![];
        for spec in b.in_send_order() {
            let payer = &self.payers[spec.payer_index as usize - 1];
            let shared_with = b.shared().then(|| if spec.payer_index == 1 { self.payers[1].pubkey() } else { self.payers[0].pubkey() });
            let config = config_of(&spec);
            let message = tx::probe_message(payer.pubkey(), shared_with, seq, spec.send_rank, config, hash)?;
            let signed = tx::sign(&message, &[payer])?;
            out.push(Built {
                spec,
                payer: payer.address(),
                config,
                signature: crate::b58::encode(&signed.signature),
                worst_fee: tx::worst_fee(message.signers.len(), config),
                message,
                signed,
            });
        }
        Ok(out)
    }

    /// Dry-run: the same probe from the funded simulation payer, sigVerify false and
    /// the blockhash replaced by the node (section 11). Returns (result, simulate, error).
    fn simulate(&mut self, b: &Burst, seq: u64, p: &Built, hash: [u8; 32]) -> (String, Value, Option<String>) {
        let Some(sim) = self.sim_payer else {
            return ("not_sent".into(), Value::Null, Some("dry-run: no ITB_SIM_PAYER for this network".into()));
        };
        let shared_with = b.shared().then(|| self.payers[if p.spec.payer_index == 1 { 1 } else { 0 }].pubkey());
        let msg = match tx::probe_message(sim, shared_with, seq, p.spec.send_rank, p.config, hash) {
            Ok(m) => m,
            Err(e) => return ("not_sent".into(), Value::Null, Some(e)),
        };
        let mut wire = msg.bytes.clone();
        wire.extend(std::iter::repeat_n(0u8, 64 * msg.signers.len()));
        match self.rpc.simulate(&wire, false) {
            Ok(v) => (
                "simulated".into(),
                json!({"err": v["err"], "unitsConsumed": v["unitsConsumed"], "fee": v.get("fee").cloned().unwrap_or(Value::Null),
                       "loadedAccountsDataSize": v.get("loadedAccountsDataSize").cloned().unwrap_or(Value::Null)}),
                None,
            ),
            Err(e) => ("simulated".into(), Value::Null, Some(e.to_string())),
        }
    }

    fn not_sent(&mut self, seq: u64, built: &[Built], why: &str) -> Result<(), String> {
        for p in built {
            self.rows.write(
                "send",
                json!({"run_id": self.run_id, "burst_seq": seq, "signature": p.signature, "result": "not_sent", "code": null,
                       "send_end_ns": null, "stopped_ns": null, "rpc_response": null, "simulate": null, "error": why}),
            )?;
        }
        self.rows.sync()
    }

    /// Re-aim the send from the freshest slot event and RTT until the moment is close;
    /// the burst row keeps the aim at signing time, burst_end the final one.
    fn aim(&self, b: &Burst, conn: Option<&quinn::Connection>, fallback: Model) -> Aim {
        loop {
            let m = self.model().unwrap_or(fallback);
            let predicted = m.predict(b.first_slot);
            let target = if b.timing == "pre300" { predicted - PRE300_NS } else { m.predict(b.first_slot + 1) };
            let rtt_ns = conn.map(|c| c.rtt().as_nanos() as i64);
            let send_at = target - rtt_ns.unwrap_or(0) / 2;
            let left = send_at - mono_ns();
            if left <= AIM_FINAL_NS {
                return Aim { anchor_slot: m.anchor_slot, predicted, target, rtt_ns, send_at };
            }
            std::thread::sleep(Duration::from_nanos((left - AIM_FINAL_NS) as u64).min(AIM_POLL));
        }
    }

    #[allow(clippy::too_many_arguments)]
    fn end_row(
        &mut self,
        seq: u64,
        conn: Option<&quinn::Connection>,
        b: &Burst,
        predicted: i64,
        aim: Option<&Aim>,
        sends: &[i64],
        reconnects: u64,
    ) -> Result<[FirstShred; 2], String> {
        let (fs1, ts1, n1) = self.first_shred(b.first_slot);
        let (fs2, ts2, n2) = self.first_shred(b.first_slot + 1);
        let offset = self.clock.lock().unwrap().node_offset_ns();
        let send_anchor_leader = aim.and_then(|a| self.leaders.leader(&mut self.rpc, a.anchor_slot));
        let final_prediction = aim.map_or(predicted, |a| a.predicted);
        self.rows.write(
            "burst_end",
            json!({"run_id": self.run_id, "burst_seq": seq, "quic_stats": conn.map(quic::stats_json),
                   "first_shred_ns": [fs1, fs2], "node_ts_ms": [ts1, ts2],
                   "first_shred_node_ns": [n1, n2], "clock_offset_ns": offset,
                   "first_send_offset_ns": fs1.and_then(|f| sends.first().map(|s| s - f)),
                   "last_send_offset_ns": fs1.and_then(|f| sends.last().map(|s| s - f)),
                   "first_send_node_offset_ns": n1.and_then(|f| sends.first().map(|s| s - f)),
                   "prediction_residual_ns": n1.or(fs1).map(|f| f - final_prediction),
                   "send_anchor_slot": aim.map(|a| a.anchor_slot), "send_anchor_leader": send_anchor_leader,
                   "send_predicted_first_slot_ns": aim.map(|a| a.predicted),
                   "send_target_arrival_ns": aim.map(|a| a.target), "send_rtt_ns": aim.and_then(|a| a.rtt_ns),
                   "reconnects": reconnects, "utc_end": utc_now()}),
        )?;
        Ok([(fs1, ts1, n1), (fs2, ts2, n2)])
    }

    /// Gossip entries of the leaders a probe of this burst could land with.
    fn snapshot(&mut self, nodes: &[Value], b: &Burst, seq: u64) -> Result<String, String> {
        let lo = b.first_slot.saturating_sub(SNAPSHOT_SLOTS_BEFORE);
        let hi = b.first_slot + SNAPSHOT_SLOTS_AFTER;
        let mut ids = BTreeSet::new();
        let mut slot = lo;
        while slot < hi {
            if let Some(l) = self.leaders.leader(&mut self.rpc, slot) {
                ids.insert(l);
            }
            slot += 1;
        }
        ids.insert(b.leader.clone());
        let kept: Vec<&Value> = nodes.iter().filter(|n| n["pubkey"].as_str().is_some_and(|p| ids.contains(p))).collect();
        let name = format!("snapshots/cluster-nodes-{seq}.json");
        let path = self.run_dir.join(&name);
        std::fs::create_dir_all(path.parent().unwrap()).map_err(|e| e.to_string())?;
        let body = json!({"utc": utc_now(), "slots": [lo, hi], "leaders": ids.len(), "nodes": kept});
        std::fs::write(&path, body.to_string()).map_err(|e| format!("{}: {e}", path.display()))?;
        Ok(name)
    }

    fn finish(
        &mut self,
        wallet: &str,
        payer_addrs: &[String],
        before_total: Option<u64>,
        settled_before: u64,
        close_after: bool,
    ) -> Result<(), String> {
        if !self.live {
            let _ = self.rows.sync();
            println!("dry-run: no key read, nothing sent, payers of the dry-run wallet hold no funds");
            return Ok(());
        }
        let j = self.journal.as_mut().unwrap();
        let pending = chain::resolve_pending(&mut self.rpc, j, &mut self.log, RESOLVE_WAIT)?;
        let mut all = vec![wallet.to_string()];
        all.extend(payer_addrs.iter().cloned());
        let after_total: u64 = self.rpc.balances(&all)?.iter().sum();
        let pending_sum: u64 = j.pending().iter().map(|p| p.1).sum();
        let settled = j.settled_total() - settled_before;
        let check = check_balances(before_total.unwrap_or(after_total), after_total, settled, pending_sum);
        self.log.info(
            "balance_check",
            None,
            json!({"before": before_total, "after": after_total, "settled_this_session": settled, "pending": pending,
                   "pending_lamports": pending_sum, "ok": check.is_ok(), "committed": j.committed(), "limit": j.limit()}),
        );
        if let Err(e) = check {
            self.log.error("balance_mismatch", None, json!({"message": e}));
            return Err(e);
        }
        if close_after {
            close_payers(&mut self.rpc, j, &mut self.log, wallet, &self.payers)?;
        }
        println!("spend journal: {} of {} lamports committed", j.committed(), j.limit());
        Ok(())
    }
}

/// Every exit prints the payer balances (section 11).
pub fn print_balances(rpc: &mut Rpc, payer_addrs: &[String]) {
    match rpc.balances(payer_addrs) {
        Ok(b) => {
            for (i, (a, l)) in payer_addrs.iter().zip(&b).enumerate() {
                println!("payer {:2} {a}: {l} lamports", i + 1);
            }
            println!("payers total: {} lamports", b.iter().sum::<u64>());
        }
        Err(e) => println!("payer balances unavailable: {e}"),
    }
}

/// `close` subcommand: return the payers' balances to the wallet after a crash.
pub fn close(s: &Settings, mode: &Mode) -> Result<(), String> {
    let wallet = keys::load_wallet(&s.key_path)?.ok_or_else(|| format!("close needs the wallet key at {}; found none", s.key_path.display()))?;
    let payers = keys::derive_payers(&wallet);
    let addrs: Vec<String> = payers.iter().map(Signer::address).collect();
    let mut rpc = Rpc::new(&s.rpc_url);
    let run_id = format!("close-{}-{}", s.network, compact_utc());
    let mut log = Log::open(&s.log_dir.join(format!("{run_id}.jsonl")), s.log_level, &run_id)?;
    let mut tls_log = Log::stderr_only(s.log_level);
    check_tls(s, &mut tls_log)?;
    let Mode::Live { max_spend_lamports } = mode else {
        let b = rpc.balances(&addrs)?;
        let closable = b.iter().filter(|x| **x > CLOSE_FEE).count();
        println!("dry-run: {closable} payers would return their balance to {} for {CLOSE_FEE} lamports each", wallet.address());
        print_balances(&mut rpc, &addrs);
        return Ok(());
    };
    let mut j = Journal::open(&s.journal_path(), *max_spend_lamports)?;
    chain::resolve_pending(&mut rpc, &mut j, &mut log, Duration::ZERO)?;
    let data = chain::scan_data(&s.data_dir)?;
    let cs = chain::scan_chain(&mut rpc, &mut j, &wallet.address(), &addrs, &data.signatures)?;
    j.adjust_to(cs.fee_total)?;
    close_payers(&mut rpc, &mut j, &mut log, &wallet.address(), &payers)?;
    println!("spend journal: {} of {} lamports committed", j.committed(), j.limit());
    print_balances(&mut rpc, &addrs);
    Ok(())
}

/// `status` subcommand: journal, pending bookings, payer balances and the next burst_seq,
/// with no transaction and no write.
pub fn status(s: &Settings) -> Result<(), String> {
    let wallet = match keys::load_wallet(&s.key_path)? {
        Some(w) => w,
        None => {
            println!("no wallet key at {}; showing the payers of the public dry-run wallet", s.key_path.display());
            keys::dry_run_wallet()
        }
    };
    let addrs: Vec<String> = keys::derive_payers(&wallet).iter().map(Signer::address).collect();
    let path = s.journal_path();
    if path.exists() {
        let j = Journal::open(&path, SPEND_LIMIT_LAMPORTS)?;
        let pending = j.pending();
        println!(
            "spend journal {}: {} lamports committed, {} settled, {} bookings pending ({} lamports){}",
            path.display(),
            j.committed(),
            j.settled_total(),
            pending.len(),
            pending.iter().map(|p| p.1).sum::<u64>(),
            if j.torn_line { "; a torn last line was dropped" } else { "" }
        );
    } else {
        println!("spend journal {}: none yet", path.display());
    }
    let data = chain::scan_data(&s.data_dir)?;
    println!(
        "raw data {}: {} probes, next burst_seq from data {}",
        s.data_dir.display(),
        data.signatures.len(),
        data.max_burst_seq.map_or(0, |m| m + 1)
    );
    println!("wallet {}", wallet.address());
    let mut rpc = Rpc::new(&s.rpc_url);
    print_balances(&mut rpc, &addrs);
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn snapshot_copy_takes_only_regular_files_beside_the_plan() {
        let base = std::env::temp_dir().join(format!("itb-snapshots-{}", std::process::id()));
        let (plan_dir, run_dir) = (base.join("plan"), base.join("run"));
        std::fs::create_dir_all(&plan_dir).unwrap();
        std::fs::write(plan_dir.join("cluster-nodes.json"), b"{}").unwrap();
        std::fs::write(base.join("wallet-key.json"), b"secret").unwrap();
        assert_eq!(copy_snapshot(&plan_dir, &run_dir, 0, "cluster-nodes.json").unwrap(), "snapshots/round0-cluster-nodes.json");
        assert!(copy_snapshot(&plan_dir, &run_dir, 0, "../wallet-key.json").unwrap_err().contains("plain file name"));
        #[cfg(unix)]
        {
            std::os::unix::fs::symlink(base.join("wallet-key.json"), plan_dir.join("link.json")).unwrap();
            assert!(copy_snapshot(&plan_dir, &run_dir, 0, "link.json").unwrap_err().contains("not a regular file"));
            assert!(!run_dir.join("snapshots/round0-link.json").exists());
            // The open itself refuses a symlink, whatever a check before it saw.
            assert!(open_regular(&plan_dir.join("link.json")).is_err());
            assert!(open_regular(&plan_dir.join("cluster-nodes.json")).is_ok());
            // A symlink planted at the destination is not written through.
            std::os::unix::fs::symlink(base.join("wallet-key.json"), run_dir.join("snapshots/round1-cluster-nodes.json")).unwrap();
            assert!(copy_snapshot(&plan_dir, &run_dir, 1, "cluster-nodes.json").is_err());
            assert_eq!(std::fs::read(base.join("wallet-key.json")).unwrap(), b"secret");
        }
        std::fs::remove_dir_all(&base).unwrap();
    }

    /// Live, read-only check against a cluster, run by hand:
    ///   ITB_RPC_URL=... cargo test -- --ignored v1_signature_verifies_on_chain
    /// A correctly signed v1 probe from an unfunded payer fails on the account and never
    /// on the signature; the same probe with one signature bit flipped fails verification.
    #[test]
    #[ignore]
    fn v1_signature_verifies_on_chain() {
        let url = std::env::var("ITB_RPC_URL").unwrap_or_else(|_| "https://api.mainnet-beta.solana.com".into());
        let mut rpc = Rpc::new(&url);
        let payers = keys::derive_payers(&keys::dry_run_wallet());
        let (hash, _, _) = rpc.latest_blockhash("confirmed").unwrap();
        let config = Config { priority_fee: 10, cu_limit: tx::PROBE_CU_LIMIT, loaded_data_limit: tx::PROBE_LOADED_DATA };
        let msg = tx::probe_message(payers[0].pubkey(), Some(payers[1].pubkey()), 0, 0, config, crate::b58::decode32(&hash).unwrap()).unwrap();
        let signed = tx::sign(&msg, &[&payers[0]]).unwrap();
        let good = rpc.simulate(&signed.wire, true);
        println!("signed: {good:?}");
        let good = good.expect("a valid signature passes sigVerify");
        assert!(!good["err"].to_string().to_lowercase().contains("signature"), "{}", good["err"]);
        let mut bad = signed.wire.clone();
        let last = bad.len() - 1;
        bad[last] ^= 1;
        let bad = rpc.simulate(&bad, true);
        println!("flipped: {bad:?}");
        let failed_on_signature = match &bad {
            Err(e) => e.message.to_lowercase().contains("signature"),
            Ok(v) => v["err"].to_string().to_lowercase().contains("signature"),
        };
        assert!(failed_on_signature, "a flipped signature bit must fail verification");
    }
}
