//! The plan file the probe executes (plan, sections 6 and 7). Python `itb plan` draws the
//! rounds, windows, arms, timing conditions, payer order and fees from the seeded table;
//! the probe only checks the file and sends what it says, so every random choice lives
//! in one committed place and the sender has none of its own.

use crate::keys::PAYERS;
use serde::Deserialize;
use serde_json::Value;

pub const PLAN_VERSION: u64 = 1;
/// Section 7: windows of one round stand at least 160 slots apart, past the blockhash
/// lifetime (150 blocks) and the Firedancer pack expiry (151 slots), so a probe cannot
/// land in the block of the next burst of the same payers. The probe holds every pair
/// of consecutive bursts to it, across rounds too.
pub const MIN_GAP_SLOTS: u64 = 160;
pub const MAX_SEND_INTERVAL_US: u64 = 50_000;

#[derive(Deserialize, Debug, Clone)]
#[serde(deny_unknown_fields)]
pub struct Plan {
    pub plan_version: u64,
    pub network: String,
    pub stage: String,
    pub doubling: bool,
    pub seed_table_sha256: Option<String>,
    pub prereg_manifest_sha256: Option<String>,
    pub rounds: Vec<Round>,
}

#[derive(Deserialize, Debug, Clone)]
#[serde(deny_unknown_fields)]
pub struct Round {
    pub round: u64,
    pub epoch: u64,
    pub part: u64,
    pub anchor_utc: String,
    pub anchor_slot: u64,
    pub cluster_nodes_file: String,
    pub leader_schedule_file: String,
    pub validators_app_file: Option<String>,
    pub validators_app_utc: Option<String>,
    pub bursts: Vec<Burst>,
}

#[derive(Deserialize, Debug, Clone)]
#[serde(deny_unknown_fields)]
pub struct Burst {
    pub cell: Option<u64>,
    pub arm: String,
    pub timing: String,
    pub path: String,
    pub first_slot: u64,
    pub window_len: u64,
    pub selection_class: String,
    pub leader: String,
    pub leader_vote: Option<String>,
    pub validators_app: Option<Value>,
    pub equal_fee_lamports: Option<u64>,
    /// Gap between consecutive sends; 5000 in the equal-fee arm (section 6), else 0.
    pub send_interval_us: u64,
    pub probes: Vec<ProbeSpec>,
}

#[derive(Deserialize, Debug, Clone, Copy)]
#[serde(deny_unknown_fields)]
pub struct ProbeSpec {
    pub payer_index: u8,
    pub send_rank: u8,
    pub priority_fee_lamports: u64,
    pub cu_limit: u32,
    pub loaded_data_limit: u32,
}

impl Burst {
    /// Probes in send order.
    pub fn in_send_order(&self) -> Vec<ProbeSpec> {
        let mut p = self.probes.clone();
        p.sort_by_key(|s| s.send_rank);
        p
    }

    pub fn shared(&self) -> bool {
        self.arm == "shared"
    }
}

const ARMS: [&str; 4] = ["independent", "shared", "equal_fee", "denominator"];
const TIMINGS: [&str; 2] = ["pre300", "slot2"];
const PATHS: [&str; 2] = ["quic", "rpc"];
const STAGES: [&str; 5] = ["pilot", "campaign", "devnet", "localnet", "test"];
const NETWORKS: [&str; 3] = ["mainnet", "devnet", "localnet"];

pub fn parse(text: &str) -> Result<Plan, String> {
    let plan: Plan = serde_json::from_str(text).map_err(|e| format!("plan: {e}"))?;
    let problems = check(&plan);
    if problems.is_empty() {
        Ok(plan)
    } else {
        Err(format!("plan: {}", problems.join("; ")))
    }
}

/// Every problem of the plan; the probe sends nothing from a plan with any.
pub fn check(plan: &Plan) -> Vec<String> {
    let mut out = vec![];
    if plan.plan_version != PLAN_VERSION {
        out.push(format!("plan_version {} (this probe reads {PLAN_VERSION})", plan.plan_version));
    }
    if !NETWORKS.contains(&plan.network.as_str()) {
        out.push(format!("network {:?}", plan.network));
    }
    if !STAGES.contains(&plan.stage.as_str()) {
        out.push(format!("stage {:?}", plan.stage));
    }
    let mut slots = vec![];
    for r in &plan.rounds {
        if r.part > 7 {
            out.push(format!("round {}: part {} above 7", r.round, r.part));
        }
        for (i, b) in r.bursts.iter().enumerate() {
            let at = format!("round {} burst {i}", r.round);
            if !ARMS.contains(&b.arm.as_str()) {
                out.push(format!("{at}: arm {:?}", b.arm));
            }
            if !TIMINGS.contains(&b.timing.as_str()) {
                out.push(format!("{at}: timing {:?}", b.timing));
            }
            if !PATHS.contains(&b.path.as_str()) {
                out.push(format!("{at}: path {:?}", b.path));
            }
            if !(1..=4).contains(&b.window_len) {
                out.push(format!("{at}: window_len {}", b.window_len));
            }
            if crate::b58::decode32(&b.leader).is_err() {
                out.push(format!("{at}: leader is not a pubkey"));
            }
            if b.send_interval_us > MAX_SEND_INTERVAL_US {
                out.push(format!("{at}: send_interval_us {} above {MAX_SEND_INTERVAL_US}", b.send_interval_us));
            }
            out.extend(check_probes(b).into_iter().map(|p| format!("{at}: {p}")));
            slots.push(b.first_slot);
        }
    }
    if slots.is_empty() {
        out.push("no bursts".into());
    }
    slots.sort_unstable();
    for w in slots.windows(2) {
        if w[1] - w[0] < MIN_GAP_SLOTS {
            out.push(format!("windows at slots {} and {} stand closer than {MIN_GAP_SLOTS} slots", w[0], w[1]));
        }
    }
    out
}

fn check_probes(b: &Burst) -> Vec<String> {
    let mut out = vec![];
    let n = b.probes.len();
    if !(2..=PAYERS).contains(&n) {
        out.push(format!("{n} probes (2 to {PAYERS})"));
        return out;
    }
    let mut payers: Vec<u8> = b.probes.iter().map(|p| p.payer_index).collect();
    let mut ranks: Vec<u8> = b.probes.iter().map(|p| p.send_rank).collect();
    payers.sort_unstable();
    ranks.sort_unstable();
    payers.dedup();
    if payers.len() != n || payers.iter().any(|&p| p == 0 || p as usize > PAYERS) {
        out.push("payer_index values must be distinct, 1 to 12".into());
    }
    if ranks != (0..n as u8).collect::<Vec<_>>() {
        out.push("send_rank values must be 0..n-1, each once".into());
    }
    if b.shared() && !b.probes.iter().any(|p| p.payer_index == 1) {
        out.push("shared arm without payer 1, the shared account".into());
    }
    for p in &b.probes {
        if p.cu_limit == 0 || p.loaded_data_limit == 0 {
            out.push("an unset v1 limit is zero and fails the transaction (section 4)".into());
            break;
        }
    }
    let fees: Vec<u64> = b.probes.iter().map(|p| p.priority_fee_lamports).collect();
    let equal = fees.iter().all(|&f| f == fees[0]);
    match b.arm.as_str() {
        "equal_fee" | "denominator" => {
            if !equal || b.equal_fee_lamports != Some(fees[0]) {
                out.push(format!("{} arm needs one fee equal to equal_fee_lamports", b.arm));
            }
        }
        _ => {
            if b.equal_fee_lamports.is_some() {
                out.push("equal_fee_lamports set outside the equal_fee and denominator arms".into());
            }
        }
    }
    if b.arm != "equal_fee" && b.send_interval_us != 0 {
        out.push("send interval outside the equal_fee arm".into());
    }
    out
}

/// Bursts of the whole plan with their round, in window order.
pub fn bursts_in_order(plan: &Plan) -> Vec<(&Round, &Burst)> {
    let mut v: Vec<(&Round, &Burst)> = plan.rounds.iter().flat_map(|r| r.bursts.iter().map(move |b| (r, b))).collect();
    v.sort_by_key(|(_, b)| b.first_slot);
    v
}

#[cfg(test)]
pub mod tests {
    use super::*;
    use serde_json::json;

    pub fn sample(first_slots: &[u64]) -> Value {
        let probes: Vec<Value> = (0..12)
            .map(|i| {
                let fee = [0, 10, 100, 1000][i % 4];
                json!({"payer_index": i + 1, "send_rank": (i * 5) % 12, "priority_fee_lamports": fee,
                       "cu_limit": 1000, "loaded_data_limit": 32768})
            })
            .collect();
        let bursts: Vec<Value> = first_slots
            .iter()
            .map(|s| json!({"cell": 0, "arm": "independent", "timing": "pre300", "path": "quic", "first_slot": s,
                            "window_len": 4, "selection_class": "Agave", "leader": "tickUcsEQegChaAuo9VYQQztB4ZGApY6ZT4FkULWY6N",
                            "leader_vote": null, "validators_app": null, "equal_fee_lamports": null, "send_interval_us": 0,
                            "probes": probes}))
            .collect();
        json!({"plan_version": 1, "network": "localnet", "stage": "localnet", "doubling": false,
               "seed_table_sha256": null, "prereg_manifest_sha256": null,
               "rounds": [{"round": 0, "epoch": 0, "part": 0, "anchor_utc": "2026-10-26T00:00:00Z", "anchor_slot": 1,
                           "cluster_nodes_file": "c.json", "leader_schedule_file": "l.json",
                           "validators_app_file": null, "validators_app_utc": null, "bursts": bursts}]})
    }

    #[test]
    fn a_good_plan_parses_and_orders_sends() {
        let plan = parse(&sample(&[1000, 1200]).to_string()).unwrap();
        let b = &plan.rounds[0].bursts[0];
        let order: Vec<u8> = b.in_send_order().iter().map(|p| p.send_rank).collect();
        assert_eq!(order, (0..12).collect::<Vec<u8>>());
        assert_eq!(bursts_in_order(&plan).len(), 2);
    }

    #[test]
    fn plan_problems_are_named() {
        let close = sample(&[1000, 1100]);
        assert!(parse(&close.to_string()).unwrap_err().contains("closer than 160"));
        let mut dup = sample(&[1000]);
        dup["rounds"][0]["bursts"][0]["probes"][1]["payer_index"] = json!(1);
        assert!(parse(&dup.to_string()).unwrap_err().contains("distinct"));
        let mut zero = sample(&[1000]);
        zero["rounds"][0]["bursts"][0]["probes"][0]["cu_limit"] = json!(0);
        assert!(parse(&zero.to_string()).unwrap_err().contains("unset v1 limit"));
        let mut eq = sample(&[1000]);
        eq["rounds"][0]["bursts"][0]["arm"] = json!("equal_fee");
        assert!(parse(&eq.to_string()).unwrap_err().contains("equal_fee_lamports"));
        let mut extra = sample(&[1000]);
        extra["surprise"] = json!(1);
        assert!(parse(&extra.to_string()).unwrap_err().contains("unknown field"));
    }
}
