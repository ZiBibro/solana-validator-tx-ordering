//! Spend journal on the state volume (plan, section 11).
//!
//! Before a transaction leaves the machine its worst possible fee is booked here and
//! the line is fsynced; after inclusion the booking is replaced by the actual meta.fee;
//! a probe that cannot land any more (block height past its lastValidBlockHeight and no
//! status in history) releases its booking. A booking that would take the total over
//! the limit is refused, and nothing is sent. The total therefore survives a crash:
//! the file is replayed on start, and a torn last line is a booking whose send never
//! happened, because sending waits for the fsync.

use serde_json::{json, Value};
use std::collections::BTreeMap;
use std::fs::{File, OpenOptions};
use std::io::{BufRead, BufReader, Write};
use std::path::{Path, PathBuf};

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Entry {
    Booked { lamports: u64, last_valid_block_height: u64, what: String },
    Settled { lamports: u64 },
    Released,
}

#[derive(Debug, PartialEq, Eq)]
pub struct LimitRefusal {
    pub committed: u64,
    pub asked: u64,
    pub limit: u64,
}

impl std::fmt::Display for LimitRefusal {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        write!(
            f,
            "spend limit: {} committed + {} asked = {} lamports exceeds the limit {}",
            self.committed,
            self.asked,
            self.committed + self.asked,
            self.limit
        )
    }
}

pub struct Journal {
    path: PathBuf,
    file: File,
    limit: u64,
    entries: BTreeMap<String, Entry>,
    /// Fees found on the chain but not in this file (a lost volume, section 11).
    adjust: u64,
    pub torn_line: bool,
}

impl Journal {
    pub fn open(path: &Path, limit: u64) -> Result<Journal, String> {
        if let Some(dir) = path.parent() {
            std::fs::create_dir_all(dir).map_err(|e| format!("journal dir {}: {e}", dir.display()))?;
        }
        let mut entries = BTreeMap::new();
        let mut adjust = 0;
        let mut torn_at = None;
        if path.exists() {
            let f = File::open(path).map_err(|e| format!("journal {}: {e}", path.display()))?;
            let mut reader = BufReader::new(f);
            let mut offset = 0u64;
            let mut n = 0;
            loop {
                let mut line = String::new();
                let len = reader.read_line(&mut line).map_err(|e| format!("journal {}: {e}", path.display()))?;
                if len == 0 {
                    break;
                }
                n += 1;
                if !line.trim().is_empty() {
                    match serde_json::from_str::<Value>(&line) {
                        Ok(v) => apply(&mut entries, &mut adjust, &v)
                            .map_err(|e| format!("journal {} line {n}: {e}", path.display()))?,
                        // Only the last line can be torn: every record ends in "\n" before its fsync.
                        Err(_) if !line.ends_with('\n') => torn_at = Some(offset),
                        Err(e) => return Err(format!("journal {} line {n}: {e}", path.display())),
                    }
                }
                offset += len as u64;
            }
        }
        let file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(path)
            .map_err(|e| format!("journal {}: {e}", path.display()))?;
        if let Some(at) = torn_at {
            // Drop the torn record: its fsync never returned, so its send never happened.
            file.set_len(at).and_then(|_| file.sync_data()).map_err(|e| format!("journal {}: {e}", path.display()))?;
        }
        Ok(Journal { path: path.to_path_buf(), file, limit, entries, adjust, torn_line: torn_at.is_some() })
    }

    pub fn path(&self) -> &Path {
        &self.path
    }

    pub fn limit(&self) -> u64 {
        self.limit
    }

    /// Booked worst fees plus settled actual fees plus the chain adjustment.
    pub fn committed(&self) -> u64 {
        self.adjust
            + self
                .entries
                .values()
                .map(|e| match e {
                    Entry::Booked { lamports, .. } | Entry::Settled { lamports } => *lamports,
                    Entry::Released => 0,
                })
                .sum::<u64>()
    }

    pub fn entry(&self, signature: &str) -> Option<&Entry> {
        self.entries.get(signature)
    }

    pub fn pending(&self) -> Vec<(String, u64, u64)> {
        self.entries
            .iter()
            .filter_map(|(s, e)| match e {
                Entry::Booked { lamports, last_valid_block_height, .. } => {
                    Some((s.clone(), *lamports, *last_valid_block_height))
                }
                _ => None,
            })
            .collect()
    }

    pub fn settled_total(&self) -> u64 {
        self.entries
            .values()
            .map(|e| if let Entry::Settled { lamports } = e { *lamports } else { 0 })
            .sum()
    }

    /// Book several transactions at once, all or none, with one fsync.
    pub fn book(&mut self, items: &[(String, u64, u64)], what: &str) -> Result<(), String> {
        let asked: u64 = items.iter().fold(0, |a, i| a.saturating_add(i.1));
        let committed = self.committed();
        if committed.saturating_add(asked) > self.limit {
            return Err(LimitRefusal { committed, asked, limit: self.limit }.to_string());
        }
        for (sig, _, _) in items {
            if self.entries.contains_key(sig) {
                return Err(format!("journal: {sig} booked twice"));
            }
        }
        let mut lines = String::new();
        for (sig, lamports, lvbh) in items {
            let v = json!({"ts": crate::clock::utc_now(), "op": "book", "sig": sig,
                           "lamports": lamports, "last_valid_block_height": lvbh, "what": what});
            lines.push_str(&v.to_string());
            lines.push('\n');
        }
        self.write_synced(&lines)?;
        for (sig, lamports, lvbh) in items {
            self.entries.insert(
                sig.clone(),
                Entry::Booked { lamports: *lamports, last_valid_block_height: *lvbh, what: what.into() },
            );
        }
        Ok(())
    }

    pub fn settle(&mut self, signature: &str, actual_fee: u64) -> Result<(), String> {
        self.record(json!({"ts": crate::clock::utc_now(), "op": "settle", "sig": signature,
                           "lamports": actual_fee}))
    }

    pub fn release(&mut self, signature: &str) -> Result<(), String> {
        self.record(json!({"ts": crate::clock::utc_now(), "op": "release", "sig": signature}))
    }

    /// Raise the total to the chain sum when the chain shows more than the file.
    pub fn adjust_to(&mut self, chain_total: u64) -> Result<u64, String> {
        let committed = self.committed();
        if chain_total <= committed {
            return Ok(0);
        }
        let delta = chain_total - committed;
        self.record(json!({"ts": crate::clock::utc_now(), "op": "adjust", "lamports": delta}))?;
        Ok(delta)
    }

    fn record(&mut self, v: Value) -> Result<(), String> {
        let mut entries = self.entries.clone();
        let mut adjust = self.adjust;
        apply(&mut entries, &mut adjust, &v)?;
        self.write_synced(&format!("{v}\n"))?;
        self.entries = entries;
        self.adjust = adjust;
        Ok(())
    }

    fn write_synced(&mut self, text: &str) -> Result<(), String> {
        self.file
            .write_all(text.as_bytes())
            .and_then(|_| self.file.sync_data())
            .map_err(|e| format!("journal {}: write failed: {e}", self.path.display()))
    }
}

fn apply(entries: &mut BTreeMap<String, Entry>, adjust: &mut u64, v: &Value) -> Result<(), String> {
    let op = v["op"].as_str().ok_or("no op")?;
    let lamports = || v["lamports"].as_u64().ok_or("no lamports");
    if op == "adjust" {
        *adjust += lamports()?;
        return Ok(());
    }
    let sig = v["sig"].as_str().ok_or("no sig")?.to_string();
    match op {
        "book" => {
            let lvbh = v["last_valid_block_height"].as_u64().ok_or("no last_valid_block_height")?;
            let what = v["what"].as_str().unwrap_or("").to_string();
            entries.insert(sig, Entry::Booked { lamports: lamports()?, last_valid_block_height: lvbh, what });
        }
        "settle" => {
            if !entries.contains_key(&sig) {
                return Err(format!("settle of unbooked {sig}"));
            }
            entries.insert(sig, Entry::Settled { lamports: lamports()? });
        }
        "release" => match entries.get(&sig) {
            Some(Entry::Booked { .. }) => {
                entries.insert(sig, Entry::Released);
            }
            _ => return Err(format!("release of {sig}, which is not booked")),
        },
        other => return Err(format!("unknown op {other}")),
    }
    Ok(())
}

/// What a booking becomes, from getSignatureStatuses (with transaction history) and the
/// finalized block height. Released only when the transaction can no longer land.
#[derive(Debug, PartialEq, Eq)]
pub enum Resolution {
    Included,
    Expired,
    Wait,
}

pub fn resolve(status: Option<&Value>, finalized_block_height: u64, last_valid_block_height: u64) -> Resolution {
    match status {
        Some(s) if s["confirmationStatus"].as_str() == Some("finalized") => Resolution::Included,
        Some(_) => Resolution::Wait,
        None if finalized_block_height > last_valid_block_height => Resolution::Expired,
        None => Resolution::Wait,
    }
}

/// Balance check of the closed set wallet plus payers (section 11): transfers inside the
/// set cancel out, so the set loses exactly the fees, or between the settled fees and
/// settled plus pending while bookings are pending. A set that lost more paid fees the
/// journal does not hold, and the run stops. A set that lost less got lamports from
/// outside, which anyone can send to a public address: payer 2 got 6 373 and 9 078
/// lamports in two transfers during campaign-mainnet-20261029T120927Z. The journal still
/// bounds the spend then, so the check passes and returns the lamports received.
pub fn check_balances(before: u64, after: u64, settled: u64, pending: u64) -> Result<u64, String> {
    let spent = i128::from(before) - i128::from(after);
    if spent > i128::from(settled) + i128::from(pending) {
        return Err(format!(
            "balance mismatch: wallet and payers lost {spent} lamports, the journal accounts for {settled} settled and {pending} pending"
        ));
    }
    Ok((i128::from(settled) - spent).max(0) as u64)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn temp(name: &str) -> PathBuf {
        let p = std::env::temp_dir().join(format!("itb-journal-{}-{name}.jsonl", std::process::id()));
        let _ = std::fs::remove_file(&p);
        p
    }

    fn item(sig: &str, lamports: u64) -> (String, u64, u64) {
        (sig.to_string(), lamports, 1000)
    }

    #[test]
    fn refuses_a_send_one_lamport_over_the_limit() {
        let p = temp("limit");
        let mut j = Journal::open(&p, 50_000_000).unwrap();
        j.book(&[item("a", 49_994_000)], "probe").unwrap();
        // 49 994 000 + 6 001 = limit + 1: refused, and nothing is written.
        let err = j.book(&[item("b", 6_001)], "probe").unwrap_err();
        assert!(err.contains("exceeds the limit 50000000"), "{err}");
        assert_eq!(j.committed(), 49_994_000);
        // Exactly at the limit is allowed.
        j.book(&[item("b", 6_000)], "probe").unwrap();
        assert_eq!(j.committed(), 50_000_000);
        drop(j);
        assert_eq!(Journal::open(&p, 50_000_000).unwrap().committed(), 50_000_000);
        std::fs::remove_file(&p).unwrap();
    }

    #[test]
    fn burst_booking_is_all_or_nothing() {
        let p = temp("burst");
        let mut j = Journal::open(&p, 10_000).unwrap();
        let burst = vec![item("x1", 5_000), item("x2", 5_001)];
        assert!(j.book(&burst, "probe").is_err());
        assert_eq!(j.committed(), 0);
        assert!(j.pending().is_empty());
        std::fs::remove_file(&p).unwrap();
    }

    #[test]
    fn settle_release_and_adjust() {
        let p = temp("settle");
        let mut j = Journal::open(&p, 1_000_000).unwrap();
        j.book(&[item("s1", 6_000), item("s2", 6_000), item("s3", 5_100)], "probe").unwrap();
        j.settle("s1", 6_000).unwrap();
        j.release("s2").unwrap();
        assert_eq!(j.committed(), 11_100);
        assert!(j.release("s2").is_err(), "release twice");
        assert_eq!(j.adjust_to(20_000).unwrap(), 8_900);
        assert_eq!(j.adjust_to(5_000).unwrap(), 0);
        drop(j);
        let j = Journal::open(&p, 1_000_000).unwrap();
        assert_eq!(j.committed(), 20_000);
        assert_eq!(j.pending(), vec![("s3".to_string(), 5_100, 1000)]);
        std::fs::remove_file(&p).unwrap();
    }

    #[test]
    fn release_only_after_the_blockhash_expires() {
        let fin = serde_json::json!({"confirmationStatus": "finalized", "err": null});
        let conf = serde_json::json!({"confirmationStatus": "confirmed", "err": null});
        assert_eq!(resolve(Some(&fin), 10, 100), Resolution::Included);
        assert_eq!(resolve(Some(&conf), 500, 100), Resolution::Wait);
        assert_eq!(resolve(None, 100, 100), Resolution::Wait, "height equal to lastValid can still land");
        assert_eq!(resolve(None, 101, 100), Resolution::Expired);
    }

    #[test]
    fn balance_mismatch_stops() {
        assert_eq!(check_balances(1_000_000, 994_000, 6_000, 0), Ok(0));
        assert!(check_balances(1_000_000, 993_999, 6_000, 0).is_err());
        assert_eq!(check_balances(1_000_000, 994_000, 0, 6_000), Ok(0));
        assert_eq!(check_balances(1_000_000, 988_000, 6_000, 6_000), Ok(0));
        assert!(check_balances(1_000_000, 987_999, 6_000, 6_000).is_err());
    }

    #[test]
    fn balance_inflow_passes() {
        // campaign-mainnet-20261029T120927Z: 6 373 and 9 078 lamports reached payer 2 from outside.
        assert_eq!(check_balances(52_435_471, 47_933_012, 4_517_910, 0), Ok(15_451));
        assert_eq!(check_balances(1_000_000, 1_000_001, 0, 0), Ok(1));
        assert_eq!(check_balances(1_000_000, 1_000_001, 6_000, 0), Ok(6_001));
        assert_eq!(check_balances(1_000_000, 995_000, 6_000, 6_000), Ok(1_000));
    }

    #[test]
    fn torn_last_line_is_dropped() {
        let p = temp("torn");
        let mut j = Journal::open(&p, 100_000).unwrap();
        j.book(&[item("t1", 5_000)], "probe").unwrap();
        drop(j);
        let mut f = OpenOptions::new().append(true).open(&p).unwrap();
        f.write_all(b"{\"ts\":\"2026-10-26T00:00:00Z\",\"op\":\"bo").unwrap();
        drop(f);
        let mut j = Journal::open(&p, 100_000).unwrap();
        assert!(j.torn_line);
        assert_eq!(j.committed(), 5_000);
        j.book(&[item("t2", 5_000)], "probe").unwrap();
        drop(j);
        assert_eq!(Journal::open(&p, 100_000).unwrap().committed(), 10_000);
        std::fs::remove_file(&p).unwrap();
    }

    /// The child half of journal_survives_a_killed_process: books, reports, then waits
    /// to be killed. Runs only when the parent test starts it.
    #[test]
    fn journal_kill_child() {
        let Ok(path) = std::env::var("ITB_JOURNAL_CHILD") else { return };
        let mut j = Journal::open(Path::new(&path), 1_000_000).unwrap();
        for n in 0..7 {
            j.book(&[item(&format!("k{n}"), 5_000 + n)], "probe").unwrap();
        }
        println!("ITB-BOOKED {}", j.committed());
        std::io::stdout().flush().unwrap();
        std::thread::sleep(std::time::Duration::from_secs(60));
    }

    #[test]
    fn journal_survives_a_killed_process() {
        let p = temp("kill");
        let mut child = std::process::Command::new(std::env::current_exe().unwrap())
            .args(["--exact", "journal::tests::journal_kill_child", "--nocapture", "--test-threads=1"])
            .env("ITB_JOURNAL_CHILD", &p)
            .stdout(std::process::Stdio::piped())
            .spawn()
            .unwrap();
        let mut out = BufReader::new(child.stdout.take().unwrap());
        let mut booked = None;
        let mut line = String::new();
        while out.read_line(&mut line).unwrap() > 0 {
            // libtest prints "test <name> ... " before the test runs, on the same line.
            if let Some(at) = line.find("ITB-BOOKED ") {
                booked = Some(line[at + 11..].trim().parse::<u64>().unwrap());
                break;
            }
            line.clear();
        }
        child.kill().unwrap();
        child.wait().unwrap();
        let booked = booked.expect("child booked nothing");
        assert_eq!(booked, 7 * 5_000 + 21);
        assert_eq!(Journal::open(&p, 1_000_000).unwrap().committed(), booked);
        std::fs::remove_file(&p).unwrap();
    }
}
