//! Slot clock (plan, section 5.1). slotsUpdatesSubscribe gives firstShredReceived, the
//! main source; slotSubscribe is the fallback, because the first subscription is marked
//! unstable. Every event is stamped on receipt with the monotonic clock of the process.
//! The send moment is predicted from the last event plus the slot duration measured in
//! this run.

use crate::clock::mono_ns;
use serde_json::{json, Value};
use std::collections::BTreeMap;
use std::sync::{Arc, Mutex};
use std::time::Duration;

const KEEP_SLOTS: u64 = 20_000;
/// Slots of history the slot duration is fitted on.
const FIT_SLOTS: u64 = 3_000;
pub const MIN_FIT_SLOTS: u64 = 150;
/// The main source counts as live when its last event is this fresh.
const FRESH_NS: i64 = 2_000_000_000;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Source {
    FirstShred,
    SlotSubscribe,
}

impl Source {
    pub fn name(self) -> &'static str {
        match self {
            Source::FirstShred => "first_shred",
            Source::SlotSubscribe => "slot_subscribe",
        }
    }
}

#[derive(Default)]
pub struct State {
    /// slot -> (local monotonic ns of receipt, node timestamp ms)
    pub first_shred: BTreeMap<u64, (i64, Option<u64>)>,
    pub slot_events: BTreeMap<u64, i64>,
    pub reconnects: u64,
    pub last_error: Option<String>,
}

#[derive(Clone, Copy, Debug)]
pub struct Model {
    pub source: Source,
    pub anchor_slot: u64,
    pub anchor_ns: i64,
    pub slot_ns: f64,
}

impl Model {
    pub fn predict(&self, slot: u64) -> i64 {
        self.anchor_ns + ((slot as f64 - self.anchor_slot as f64) * self.slot_ns).round() as i64
    }

    pub fn slot_at(&self, ns: i64) -> u64 {
        let s = self.anchor_slot as f64 + (ns - self.anchor_ns) as f64 / self.slot_ns;
        s.max(0.0) as u64
    }
}

/// Least-squares slope of receipt time over slot number, on the last FIT_SLOTS slots.
fn fit(points: &BTreeMap<u64, i64>) -> Option<f64> {
    let last = *points.keys().next_back()?;
    let pts: Vec<(f64, f64)> = points
        .range(last.saturating_sub(FIT_SLOTS)..)
        .map(|(s, t)| (*s as f64, *t as f64))
        .collect();
    let span = pts.last()?.0 - pts.first()?.0;
    if pts.len() < 10 || span < MIN_FIT_SLOTS as f64 {
        return None;
    }
    let n = pts.len() as f64;
    let (mx, my) = (pts.iter().map(|p| p.0).sum::<f64>() / n, pts.iter().map(|p| p.1).sum::<f64>() / n);
    let sxy: f64 = pts.iter().map(|p| (p.0 - mx) * (p.1 - my)).sum();
    let sxx: f64 = pts.iter().map(|p| (p.0 - mx).powi(2)).sum();
    (sxx > 0.0).then(|| sxy / sxx)
}

impl State {
    pub fn model(&self) -> Option<Model> {
        let now = mono_ns();
        let shred: BTreeMap<u64, i64> = self.first_shred.iter().map(|(s, (t, _))| (*s, *t)).collect();
        let fresh = |m: &BTreeMap<u64, i64>| m.iter().next_back().filter(|(_, t)| now - **t < FRESH_NS).map(|(s, t)| (*s, *t));
        if let (Some((slot, ns)), Some(slope)) = (fresh(&shred), fit(&shred)) {
            return Some(Model { source: Source::FirstShred, anchor_slot: slot, anchor_ns: ns, slot_ns: slope });
        }
        let (slot, ns) = fresh(&self.slot_events)?;
        let slope = fit(&self.slot_events)?;
        Some(Model { source: Source::SlotSubscribe, anchor_slot: slot, anchor_ns: ns, slot_ns: slope })
    }

    fn trim(&mut self) {
        for m in [&mut self.slot_events] {
            if let Some(&last) = m.keys().next_back() {
                *m = m.split_off(&last.saturating_sub(KEEP_SLOTS));
            }
        }
        if let Some(&last) = self.first_shred.keys().next_back() {
            self.first_shred = self.first_shred.split_off(&last.saturating_sub(KEEP_SLOTS));
        }
    }

    /// Apply one WebSocket message; returns false for messages that are not events.
    pub fn apply(&mut self, msg: &Value, received_ns: i64) -> bool {
        let r = &msg["params"]["result"];
        match msg["method"].as_str() {
            Some("slotsUpdatesNotification") if r["type"] == "firstShredReceived" => {
                if let Some(slot) = r["slot"].as_u64() {
                    self.first_shred.entry(slot).or_insert((received_ns, r["timestamp"].as_u64()));
                    self.trim();
                    return true;
                }
            }
            Some("slotNotification") => {
                if let Some(slot) = r["slot"].as_u64() {
                    self.slot_events.entry(slot).or_insert(received_ns);
                    self.trim();
                    return true;
                }
            }
            _ => {}
        }
        false
    }
}

pub type Shared = Arc<Mutex<State>>;

/// Run the subscriptions on their own thread, reconnecting on any error.
pub fn start(ws_url: String) -> Shared {
    let state: Shared = Arc::new(Mutex::new(State::default()));
    let s = state.clone();
    std::thread::Builder::new()
        .name("slot-clock".into())
        .spawn(move || loop {
            if let Err(e) = run_once(&ws_url, &s) {
                let mut st = s.lock().unwrap();
                st.reconnects += 1;
                st.last_error = Some(e);
            }
            std::thread::sleep(Duration::from_millis(500));
        })
        .expect("slot clock thread");
    state
}

fn run_once(ws_url: &str, state: &Shared) -> Result<(), String> {
    let (mut ws, _) = tungstenite::connect(ws_url).map_err(|e| format!("ws connect: {e}"))?;
    for (id, method) in [(1, "slotsUpdatesSubscribe"), (2, "slotSubscribe")] {
        let req = json!({"jsonrpc": "2.0", "id": id, "method": method});
        ws.send(tungstenite::Message::Text(req.to_string())).map_err(|e| format!("ws send: {e}"))?;
    }
    loop {
        let msg = ws.read().map_err(|e| format!("ws read: {e}"))?;
        let received = mono_ns();
        let text = match msg {
            tungstenite::Message::Text(t) => t,
            tungstenite::Message::Close(_) => return Err("ws closed by the node".into()),
            _ => continue,
        };
        if let Ok(v) = serde_json::from_str::<Value>(&text) {
            state.lock().unwrap().apply(&v, received);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn shred(slot: u64, ts: u64) -> Value {
        json!({"method": "slotsUpdatesNotification",
               "params": {"result": {"type": "firstShredReceived", "slot": slot, "timestamp": ts}}})
    }

    #[test]
    fn fits_the_slot_duration_and_predicts() {
        let mut st = State::default();
        let now = mono_ns();
        // 400 slots at 215.1 ms, ending now.
        for i in 0..400u64 {
            let t = now - ((399 - i) as f64 * 215_100_000.0) as i64;
            assert!(st.apply(&shred(1000 + i, 0), t));
        }
        assert!(!st.apply(&json!({"method": "slotsUpdatesNotification",
            "params": {"result": {"type": "completed", "slot": 2000}}}), now));
        let m = st.model().expect("model");
        assert_eq!(m.source, Source::FirstShred);
        assert!((m.slot_ns - 215_100_000.0).abs() < 1.0, "{}", m.slot_ns);
        assert_eq!(m.anchor_slot, 1399);
        assert!((m.predict(1409) - (now + 2_151_000_000)).abs() < 10);
        assert_eq!(m.slot_at(m.predict(1500) + 1), 1500);
    }

    #[test]
    fn falls_back_to_slot_subscribe_when_shreds_stop() {
        let mut st = State::default();
        let now = mono_ns();
        for i in 0..200u64 {
            st.apply(&shred(i, 0), now - 10_000_000_000 - ((199 - i) * 200_000_000) as i64);
            st.apply(&json!({"method": "slotNotification", "params": {"result": {"slot": 500 + i}}}),
                     now - ((199 - i) * 210_000_000) as i64);
        }
        let m = st.model().expect("model");
        assert_eq!(m.source, Source::SlotSubscribe);
        assert_eq!(m.anchor_slot, 699);
    }
}
