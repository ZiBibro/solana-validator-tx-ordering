//! What the probe reads from the cluster besides sending: the epoch schedule and leader
//! schedule (to find the leader of a slot locally), gossip entries, and the chain side
//! of the spend journal and of burst_seq recovery (plan, sections 4 and 11).

use crate::journal::{Entry, Journal, Resolution};
use crate::rows::Log;
use crate::rpc::Rpc;
use serde_json::{json, Value};
use std::collections::{BTreeMap, HashSet};
use std::path::Path;
use std::time::{Duration, Instant};

const MINIMUM_SLOTS_PER_EPOCH: u64 = 32;
pub const SYSTEM_PROGRAM: &str = "11111111111111111111111111111111";

/// getEpochSchedule, with the warmup arithmetic of Agave's EpochSchedule.
#[derive(Clone, Copy, Debug)]
pub struct EpochSchedule {
    pub slots_per_epoch: u64,
    pub first_normal_epoch: u64,
    pub first_normal_slot: u64,
}

impl EpochSchedule {
    pub fn from_json(v: &Value) -> Result<EpochSchedule, String> {
        let f = |k: &str| v[k].as_u64().ok_or(format!("getEpochSchedule: no {k}"));
        Ok(EpochSchedule {
            slots_per_epoch: f("slotsPerEpoch")?,
            first_normal_epoch: f("firstNormalEpoch")?,
            first_normal_slot: f("firstNormalSlot")?,
        })
    }

    pub fn epoch_of(&self, slot: u64) -> u64 {
        if slot < self.first_normal_slot {
            let e = (slot + MINIMUM_SLOTS_PER_EPOCH + 1).next_power_of_two().trailing_zeros()
                - MINIMUM_SLOTS_PER_EPOCH.trailing_zeros()
                - 1;
            e as u64
        } else {
            self.first_normal_epoch + (slot - self.first_normal_slot) / self.slots_per_epoch
        }
    }

    pub fn first_slot(&self, epoch: u64) -> u64 {
        if epoch <= self.first_normal_epoch {
            ((1u64 << epoch) - 1) * MINIMUM_SLOTS_PER_EPOCH
        } else {
            (epoch - self.first_normal_epoch) * self.slots_per_epoch + self.first_normal_slot
        }
    }
}

/// Leader of every slot of one epoch, stored as indices into the identity list.
pub struct EpochLeaders {
    first: u64,
    ids: Vec<u32>,
    names: Vec<String>,
}

impl EpochLeaders {
    pub fn from_json(first: u64, v: &Value) -> Result<EpochLeaders, String> {
        let map = v.as_object().ok_or("getLeaderSchedule: no schedule for this epoch")?;
        let mut names = vec![];
        let mut ids = vec![];
        for (name, slots) in map {
            let id = names.len() as u32;
            names.push(name.clone());
            for s in slots.as_array().ok_or("getLeaderSchedule: slots are not a list")? {
                let i = s.as_u64().ok_or("getLeaderSchedule: bad slot index")? as usize;
                if ids.len() <= i {
                    ids.resize(i + 1, u32::MAX);
                }
                ids[i] = id;
            }
        }
        Ok(EpochLeaders { first, ids, names })
    }

    pub fn leader(&self, slot: u64) -> Option<&str> {
        let i = slot.checked_sub(self.first)? as usize;
        let id = *self.ids.get(i)?;
        self.names.get(id as usize).map(String::as_str)
    }
}

/// Leader schedules by epoch, fetched on first use.
pub struct Leaders {
    pub schedule: EpochSchedule,
    epochs: BTreeMap<u64, Option<EpochLeaders>>,
}

impl Leaders {
    pub fn new(schedule: EpochSchedule) -> Leaders {
        Leaders { schedule, epochs: BTreeMap::new() }
    }

    pub fn leader(&mut self, rpc: &mut Rpc, slot: u64) -> Option<String> {
        let epoch = self.schedule.epoch_of(slot);
        if !self.epochs.contains_key(&epoch) {
            let first = self.schedule.first_slot(epoch);
            let got = rpc.leader_schedule(first).ok().and_then(|v| EpochLeaders::from_json(first, &v).ok());
            self.epochs.insert(epoch, got);
        }
        self.epochs[&epoch].as_ref()?.leader(slot).map(String::from)
    }
}

/// The gossip entry of one identity from getClusterNodes.
pub fn node<'a>(nodes: &'a [Value], identity: &str) -> Option<&'a Value> {
    nodes.iter().find(|n| n["pubkey"].as_str() == Some(identity))
}

/// Highest burst_seq and every probe signature in the raw data on the volume.
pub struct DataScan {
    pub max_burst_seq: Option<u64>,
    pub signatures: HashSet<String>,
}

pub fn scan_data(data_dir: &Path) -> Result<DataScan, String> {
    let mut out = DataScan { max_burst_seq: None, signatures: HashSet::new() };
    let runs = data_dir.join("runs");
    let Ok(dir) = std::fs::read_dir(&runs) else { return Ok(out) };
    for e in dir.flatten() {
        let path = e.path().join("probes.jsonl");
        let Ok(text) = std::fs::read_to_string(&path) else { continue };
        for line in text.lines().filter(|l| !l.trim().is_empty()) {
            let Ok(v) = serde_json::from_str::<Value>(line) else { continue };
            if matches!(v["kind"].as_str(), Some("burst") | Some("probe")) {
                if let Some(s) = v["burst_seq"].as_u64() {
                    out.max_burst_seq = Some(out.max_burst_seq.map_or(s, |m| m.max(s)));
                }
            }
            if let (Some("probe"), Some(sig)) = (v["kind"].as_str(), v["signature"].as_str()) {
                out.signatures.insert(sig.to_string());
            }
        }
    }
    Ok(out)
}

/// Fee payer, fee and the probe transfer amount of a getTransaction (encoding json).
pub struct TxFacts {
    pub fee_payer: String,
    pub fee: u64,
    /// burst_seq of a probe: a first instruction that is a system transfer of the fee
    /// payer to itself, amount burst_seq*16 + send_rank + 1 (section 4).
    pub probe_burst_seq: Option<u64>,
}

pub fn tx_facts(tx: &Value) -> Option<TxFacts> {
    let message = &tx["transaction"]["message"];
    let keys: Vec<&str> = message["accountKeys"]
        .as_array()?
        .iter()
        .filter_map(|k| k.as_str().or_else(|| k["pubkey"].as_str()))
        .collect();
    let fee_payer = keys.first()?.to_string();
    let fee = tx["meta"]["fee"].as_u64()?;
    let probe_burst_seq = message["instructions"].as_array().and_then(|ixs| {
        let ix = ixs.first()?;
        let program = keys.get(ix["programIdIndex"].as_u64()? as usize)?;
        let accts: Vec<u64> = ix["accounts"].as_array()?.iter().filter_map(Value::as_u64).collect();
        let data = crate::b58::decode(ix["data"].as_str()?).ok()?;
        let self_transfer = accts.len() == 2 && accts[0] == 0 && accts[1] == 0;
        if *program != SYSTEM_PROGRAM || !self_transfer || data.len() != 12 || data[..4] != [2, 0, 0, 0] {
            return None;
        }
        let amount = u64::from_le_bytes(data[4..12].try_into().ok()?);
        amount.checked_sub(1).map(|a| a / crate::tx::RANKS_PER_BURST)
    });
    Some(TxFacts { fee_payer, fee, probe_burst_seq })
}

pub struct ChainScan {
    pub fee_total: u64,
    pub max_burst_seq: Option<u64>,
    pub signatures: usize,
    pub fetched: usize,
}

/// Section 11: fees of every transaction of the twelve payers and of the wallet's
/// transactions that carry an itb- memo or touch a payer, as the chain holds them.
/// Known fees come from settled journal entries, so a normal start fetches almost
/// nothing; a lost volume makes it fetch every transaction once. Probes missing from
/// the raw data give the chain side of burst_seq recovery.
pub fn scan_chain(
    rpc: &mut Rpc,
    journal: &mut Journal,
    wallet: &str,
    payers: &[String],
    known: &HashSet<String>,
) -> Result<ChainScan, String> {
    let ours: HashSet<&str> = payers.iter().map(String::as_str).chain([wallet]).collect();
    let mut sigs: BTreeMap<String, ()> = BTreeMap::new();
    for p in payers {
        for e in rpc.signatures_for_address(p)? {
            if let Some(s) = e["signature"].as_str() {
                sigs.insert(s.to_string(), ());
            }
        }
    }
    for e in rpc.signatures_for_address(wallet)? {
        let memo = e["memo"].as_str().unwrap_or("");
        if let (Some(s), true) = (e["signature"].as_str(), memo.contains("itb-")) {
            sigs.insert(s.to_string(), ());
        }
    }
    let mut out = ChainScan { fee_total: 0, max_burst_seq: None, signatures: sigs.len(), fetched: 0 };
    for sig in sigs.keys() {
        if let Some(Entry::Settled { lamports }) = journal.entry(sig) {
            out.fee_total += lamports;
            continue;
        }
        out.fetched += 1;
        let Some(tx) = rpc.transaction(sig)? else { continue };
        let Some(f) = tx_facts(&tx) else { continue };
        if !ours.contains(f.fee_payer.as_str()) {
            continue;
        }
        out.fee_total += f.fee;
        if let Some(Entry::Booked { .. }) = journal.entry(sig) {
            journal.settle(sig, f.fee)?;
        }
        if !known.contains(sig) && journal.entry(sig).is_none() {
            if let Some(s) = f.probe_burst_seq {
                out.max_burst_seq = Some(out.max_burst_seq.map_or(s, |m| m.max(s)));
            }
        }
    }
    Ok(out)
}

/// Settle what landed and release what expired. With `wait_for` set, polls until every
/// booking is resolved or the time is up; the rest stays booked for the next start.
pub fn resolve_pending(rpc: &mut Rpc, journal: &mut Journal, log: &mut Log, wait_for: Duration) -> Result<usize, String> {
    let deadline = Instant::now() + wait_for;
    loop {
        let pending = journal.pending();
        if pending.is_empty() {
            return Ok(0);
        }
        let sigs: Vec<String> = pending.iter().map(|p| p.0.clone()).collect();
        let statuses = rpc.signature_statuses(&sigs)?;
        let height = rpc.block_height("finalized")?;
        let (mut settled, mut released) = (0, 0);
        for ((sig, _, lvbh), status) in pending.iter().zip(&statuses) {
            match crate::journal::resolve(status.as_ref(), height, *lvbh) {
                Resolution::Included => {
                    if let Some(f) = rpc.transaction(sig)?.as_ref().and_then(tx_facts) {
                        journal.settle(sig, f.fee)?;
                        settled += 1;
                    }
                }
                Resolution::Expired => {
                    journal.release(sig)?;
                    released += 1;
                }
                Resolution::Wait => {}
            }
        }
        let left = journal.pending().len();
        if settled + released > 0 {
            log.info(
                "journal_resolved",
                None,
                json!({"settled": settled, "released": released, "pending": left, "finalized_block_height": height,
                       "committed": journal.committed()}),
            );
        }
        if left == 0 || Instant::now() >= deadline {
            return Ok(left);
        }
        std::thread::sleep(Duration::from_secs(4));
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn epoch_arithmetic_matches_agave() {
        // Mainnet: no warmup, 432 000 slots per epoch.
        let m = EpochSchedule { slots_per_epoch: 432_000, first_normal_epoch: 0, first_normal_slot: 0 };
        assert_eq!(m.epoch_of(461_810_027), 1069);
        assert_eq!(m.first_slot(1069), 461_808_000);
        // A test validator with warmup: epochs of 32, 64, 128 ... slots.
        let w = EpochSchedule { slots_per_epoch: 432_000, first_normal_epoch: 14, first_normal_slot: 524_256 };
        assert_eq!((w.epoch_of(0), w.epoch_of(31), w.epoch_of(32), w.epoch_of(95), w.epoch_of(96)), (0, 0, 1, 1, 2));
        assert_eq!((w.first_slot(1), w.first_slot(2), w.first_slot(14)), (32, 96, 524_256));
        assert_eq!(w.epoch_of(524_256 + 432_000), 15);
    }

    #[test]
    fn leader_lookup_and_probe_facts() {
        let v = json!({"A": [0, 1, 2, 3], "B": [4, 5, 6, 7]});
        let l = EpochLeaders::from_json(1000, &v).unwrap();
        assert_eq!(l.leader(1003), Some("A"));
        assert_eq!(l.leader(1004), Some("B"));
        assert_eq!(l.leader(999), None);
        assert_eq!(l.leader(1008), None);
        // burst_seq 7, send rank 3: amount 7*16 + 3 + 1 = 116.
        let mut data = vec![2, 0, 0, 0];
        data.extend_from_slice(&116u64.to_le_bytes());
        let tx = json!({"meta": {"fee": 5100}, "transaction": {"message": {
            "accountKeys": ["BAPwtQzaPZYJQYeJjQbTiPXx55Gja9gX85qv8i9Jk6u9", SYSTEM_PROGRAM],
            "instructions": [{"programIdIndex": 1, "accounts": [0, 0], "data": crate::b58::encode(&data)}]}}});
        let f = tx_facts(&tx).unwrap();
        assert_eq!((f.fee, f.probe_burst_seq), (5100, Some(7)));
        assert_eq!(f.fee_payer, "BAPwtQzaPZYJQYeJjQbTiPXx55Gja9gX85qv8i9Jk6u9");
    }
}
