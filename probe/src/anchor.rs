//! `anchor` subcommand: the memo transaction that ties a stage's pre-registration
//! manifest to the chain before its first live burst (plan-implementation, section 10).
//!
//! The memo reads "itb-prereg <sha256 of prereg/manifest-<stage>.json>". It goes out once
//! per stage, as a legacy transaction with one Memo v2 instruction from the wallet, through
//! the spend journal and the limit like every other fee. Its signature lands in
//! data/prereg-anchors.json, which `itb verify` reads (section 9). Dry-run, the default,
//! simulates the same message from the funded simulation payer and writes nothing.

use crate::chain;
use crate::journal::{Entry, Journal};
use crate::keys::{self, Signer};
use crate::rows::Log;
use crate::rpc::Rpc;
use crate::session::{self, Settings};
use crate::tx;
use crate::Mode;
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::path::Path;

pub const STAGES: [&str; 2] = ["pilot", "campaign"];
pub const MEMO_PREFIX: &str = "itb-prereg ";
const ANCHORS_FILE: &str = "prereg-anchors.json";
/// One signature and no priority fee (research/craft-probe.md, 1.8: 5000 lamports).
const ANCHOR_FEE: u64 = tx::LAMPORTS_PER_SIGNATURE;

pub fn manifest_name(stage: &str) -> String {
    format!("manifest-{stage}.json")
}

/// SHA-256 hex of a manifest whose "files" object lists at least one file, each with a
/// lowercase SHA-256 hex; a malformed manifest would anchor a hash nobody can check.
pub fn manifest_digest(bytes: &[u8]) -> Result<String, String> {
    let v: Value = serde_json::from_slice(bytes).map_err(|e| format!("manifest: {e}"))?;
    let files = v["files"].as_object().ok_or("manifest: no \"files\" object")?;
    if files.is_empty() {
        return Err("manifest: \"files\" lists nothing".into());
    }
    for (name, h) in files {
        let ok = h.as_str().is_some_and(|h| h.len() == 64 && h.bytes().all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b)));
        if !ok {
            return Err(format!("manifest: {name} carries no lowercase sha256 hex"));
        }
    }
    Ok(Sha256::digest(bytes).iter().map(|b| format!("{b:02x}")).collect())
}

/// Anchors recorded so far; no file means none.
fn read_anchors(path: &Path) -> Result<Vec<Value>, String> {
    match std::fs::read(path) {
        Ok(b) => serde_json::from_slice(&b).map_err(|e| format!("{}: {e}", path.display())),
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => Ok(vec![]),
        Err(e) => Err(format!("{}: {e}", path.display())),
    }
}

/// A stage is anchored once: a second memo would leave two hashes for one stage.
pub fn anchored<'a>(anchors: &'a [Value], stage: &str) -> Option<&'a Value> {
    anchors.iter().find(|a| a["stage"] == stage)
}

/// A live run of a pre-registered stage starts only after its anchor, and only from a plan
/// drawn against the anchored manifest; otherwise verify would fail the stage after the spend.
pub fn require_anchor(data_dir: &Path, stage: &str, plan_manifest: Option<&str>) -> Result<(), String> {
    if !STAGES.contains(&stage) {
        return Ok(());
    }
    let anchors = read_anchors(&data_dir.join(ANCHORS_FILE))?;
    let a = anchored(&anchors, stage)
        .ok_or_else(|| format!("live {stage} run needs its prereg anchor first: itb-probe anchor --stage {stage} --live --max-spend-lamports N"))?;
    match (plan_manifest, a["sha256"].as_str()) {
        (Some(p), Some(h)) if p == h => Ok(()),
        (p, h) => Err(format!(
            "plan carries prereg manifest {p:?}, the {stage} anchor holds {h:?}; draw the plan again with prereg/{}",
            manifest_name(stage)
        )),
    }
}

/// Write the list through a temporary file and a rename, so a crash leaves the old list.
fn write_anchors(path: &Path, anchors: &[Value]) -> Result<(), String> {
    let tmp = path.with_extension("json.tmp");
    let mut text = serde_json::to_string_pretty(anchors).map_err(|e| e.to_string())?;
    text.push('\n');
    std::fs::write(&tmp, text).map_err(|e| format!("{}: {e}", tmp.display()))?;
    std::fs::rename(&tmp, path).map_err(|e| format!("{}: {e}", path.display()))
}

pub fn anchor(s: &Settings, mode: &Mode, stage: &str) -> Result<(), String> {
    if !STAGES.contains(&stage) {
        return Err(format!("stage {stage:?}; expected {}", STAGES.join(" or ")));
    }
    let name = manifest_name(stage);
    let file = s.prereg_dir.join(&name);
    let bytes = std::fs::read(&file).map_err(|e| format!("{}: {e} (draw it with python -m itb manifest --stage {stage})", file.display()))?;
    let digest = manifest_digest(&bytes)?;
    let memo = format!("{MEMO_PREFIX}{digest}");
    let rel = format!("prereg/{name}");
    let anchors_path = s.data_dir.join(ANCHORS_FILE);
    let mut anchors = read_anchors(&anchors_path)?;
    if let Some(a) = anchored(&anchors, stage) {
        return Err(format!("stage {stage} is anchored already by {}", a["signature"]));
    }
    let run_id = format!("anchor-{stage}-{}-{}", s.network, session::compact_utc());
    let mut log = Log::open(&s.log_dir.join(format!("{run_id}.jsonl")), s.log_level, &run_id)?;
    log.info("anchor_start", None, json!({"stage": stage, "file": rel, "sha256": digest, "network": s.network,
                                          "mode": if matches!(mode, Mode::Live { .. }) { "live" } else { "dry-run" }}));
    println!("anchor {stage}: memo \"{memo}\" for {rel}");
    session::check_tls(s, &mut log)?;
    let mut rpc = Rpc::new(&s.rpc_url);

    let Mode::Live { max_spend_lamports } = mode else {
        return simulate(s, &mut rpc, &mut log, &memo, &anchors_path);
    };
    let wallet = keys::load_wallet(&s.key_path)?
        .ok_or_else(|| format!("live anchor needs the wallet key at {}; found none", s.key_path.display()))?;
    let payers: Vec<String> = keys::derive_payers(&wallet).iter().map(Signer::address).collect();
    let mut j = Journal::open(&s.journal_path(), *max_spend_lamports)?;
    let data = chain::scan_data(&s.data_dir)?;
    let cs = chain::reconcile(&mut rpc, &mut j, &mut log, &wallet.address(), &payers, &data.signatures)?;
    j.adjust_to(cs.fee_total)?;

    let (hash, lvbh, _) = rpc.latest_blockhash("confirmed")?;
    let msg = tx::legacy_message(wallet.pubkey(), &[tx::memo(&memo)?], crate::b58::decode32(&hash)?)?;
    let signed = tx::sign_legacy(&msg, &[&wallet])?;
    let sig = crate::b58::encode(&signed.signature);
    // Booking first: the journal refuses the fee above the limit before anything is sent.
    j.book(&[(sig.clone(), ANCHOR_FEE, lvbh)], "anchor")?;
    log.info("anchor_send", None, json!({"signature": sig, "wallet": wallet.address(), "fee_lamports": ANCHOR_FEE}));
    rpc.send(&signed.wire, false, None)?;
    let left = chain::resolve_pending(&mut rpc, &mut j, &mut log, session::RESOLVE_WAIT)?;
    if !matches!(j.entry(&sig), Some(Entry::Settled { .. })) {
        return Err(format!("anchor transaction {sig} did not finalize ({left} bookings pending); run anchor again once it settles or expires"));
    }
    let got = rpc.transaction(&sig)?.ok_or_else(|| format!("anchor transaction {sig} finalized but getTransaction returns nothing"))?;
    anchors.push(json!({"stage": stage, "file": rel, "signature": sig, "manifest": true, "sha256": digest,
                        "slot": got["slot"], "block_time": got["blockTime"]}));
    write_anchors(&anchors_path, &anchors)?;
    log.info("anchored", None, json!({"signature": sig, "slot": got["slot"], "block_time": got["blockTime"]}));
    println!("anchored {stage}: {sig} in slot {}, block time {}; recorded in {}", got["slot"], got["blockTime"], anchors_path.display());
    println!("spend journal: {} of {} lamports committed", j.committed(), j.limit());
    Ok(())
}

/// Dry-run: the same memo from the funded simulation payer, sigVerify off and the
/// blockhash replaced by the node; a failed simulation stops here, before any word on live.
fn simulate(s: &Settings, rpc: &mut Rpc, log: &mut Log, memo: &str, anchors_path: &Path) -> Result<(), String> {
    let payer = match s.sim_payer.as_deref() {
        Some(p) => crate::b58::decode32(p)?,
        None => return Err("dry-run anchor needs ITB_SIM_PAYER on this network".into()),
    };
    let (hash, _, _) = rpc.latest_blockhash("confirmed")?;
    let msg = tx::legacy_message(payer, &[tx::memo(memo)?], crate::b58::decode32(&hash)?)?;
    let v = rpc.simulate(&tx::unsigned_legacy_wire(&msg), false)?;
    let out = json!({"err": v["err"], "fee": v.get("fee").cloned().unwrap_or(Value::Null), "unitsConsumed": v["unitsConsumed"],
                     "loadedAccountsDataSize": v.get("loadedAccountsDataSize").cloned().unwrap_or(Value::Null), "logs": v["logs"]});
    log.info("anchor_simulated", None, out.clone());
    println!(
        "dry-run: simulation from {} err {}, fee {}, {} CU, {} bytes loaded; nothing sent, {} unchanged",
        crate::b58::encode(&payer),
        out["err"],
        out["fee"],
        out["unitsConsumed"],
        out["loadedAccountsDataSize"],
        anchors_path.display()
    );
    if !v["err"].is_null() {
        return Err(format!("the anchor memo fails simulation: {}", v["err"]));
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    const FILE_HASH: &str = "0000000000000000000000000000000000000000000000000000000000000000";

    #[test]
    fn manifest_must_list_files_with_their_hashes() {
        let good = format!("{{\"files\": {{\"prereg/pilot-table.json\": \"{FILE_HASH}\"}}}}");
        let digest = manifest_digest(good.as_bytes()).unwrap();
        assert_eq!(digest.len(), 64);
        let expect: String = Sha256::digest(good.as_bytes()).iter().map(|b| format!("{b:02x}")).collect();
        assert_eq!(digest, expect);
        assert!(manifest_digest(b"{\"files\": {}}").is_err());
        assert!(manifest_digest(b"{\"stage\": \"pilot\"}").is_err());
        assert!(manifest_digest(b"{\"files\": {\"a\": \"ABC\"}}").is_err());
        let upper = format!("{{\"files\": {{\"a\": \"{}\"}}}}", "A".repeat(64));
        assert!(manifest_digest(upper.as_bytes()).is_err());
    }

    #[test]
    fn a_stage_is_anchored_once() {
        let base = std::env::temp_dir().join(format!("itb-anchors-{}", std::process::id()));
        std::fs::create_dir_all(&base).unwrap();
        let path = base.join(ANCHORS_FILE);
        assert!(read_anchors(&path).unwrap().is_empty());
        let list = vec![json!({"stage": "pilot", "file": "prereg/manifest-pilot.json", "signature": "s1", "manifest": true})];
        write_anchors(&path, &list).unwrap();
        let back = read_anchors(&path).unwrap();
        assert_eq!(back, list);
        assert!(anchored(&back, "pilot").is_some());
        assert!(anchored(&back, "campaign").is_none());
        assert!(!path.with_extension("json.tmp").exists());
        std::fs::remove_dir_all(&base).unwrap();
    }

    #[test]
    fn a_live_stage_run_needs_its_anchor_and_manifest() {
        let base = std::env::temp_dir().join(format!("itb-require-{}", std::process::id()));
        std::fs::create_dir_all(&base).unwrap();
        assert!(require_anchor(&base, "pilot", Some(FILE_HASH)).is_err());
        assert!(require_anchor(&base, "devnet", None).is_ok());
        let list = vec![json!({"stage": "pilot", "signature": "s1", "manifest": true, "sha256": FILE_HASH})];
        write_anchors(&base.join(ANCHORS_FILE), &list).unwrap();
        assert!(require_anchor(&base, "pilot", Some(FILE_HASH)).is_ok());
        assert!(require_anchor(&base, "pilot", None).is_err());
        assert!(require_anchor(&base, "pilot", Some(&"f".repeat(64))).is_err());
        assert!(require_anchor(&base, "campaign", Some(FILE_HASH)).is_err());
        std::fs::remove_dir_all(&base).unwrap();
    }
}
