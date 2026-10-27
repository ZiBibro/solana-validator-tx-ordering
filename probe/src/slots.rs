//! Slot clock (plan, section 5.1). slotsUpdatesSubscribe gives firstShredReceived, the
//! main source; slotSubscribe is the fallback, because the first subscription is marked
//! unstable. Every event is stamped on receipt with the monotonic clock of the process.
//! The send moment is predicted from the last event plus the slot durations measured in
//! this run. Slots inside one leader window run faster than the handoff to the next
//! leader (devnet dry-run 2026-10-26: 145-149 ms between slots 1 and 2 of a window at a
//! 238 ms mean), so near the anchor each step uses the median duration of its position
//! in the 4-slot window; far from it the fitted mean slot duration is used.
//!
//! The public mainnet node delivers events late at times: on 2026-10-26 at 23:43 UTC
//! every connection lagged the cluster by 12-14 slots at the median, while the slot
//! numbers lined up with the excess delivery time, receipt minus the node timestamp of
//! firstShredReceived. The node received the shreds on time and the delay sat in the
//! WebSocket stream. So the clock runs on node time: each event's node timestamp plus
//! the smallest receipt-minus-node-time offset of recent events, which is the delivery
//! of an event that met no backlog. Receipt times remain the basis when events carry no
//! timestamp or too few do.

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
/// Consecutive leader slots; window starts sit at multiples of it.
pub const WINDOW_SLOTS: u64 = 4;
/// Per-position steps are used up to this many slots past the anchor.
const STEP_HORIZON: u64 = 16;
/// Recent slots the node time offset is the minimum over, about 5 minutes: short enough
/// for drift between the local and the node clock to stay at a few ms.
const OFFSET_SLOTS: u64 = 1_500;
/// Observed consecutive pairs needed per position.
const MIN_STEP_SAMPLES: usize = 5;

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

/// Which time of an event the model stands on.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Basis {
    /// Node timestamp plus the offset of the least delayed recent event.
    NodeTs,
    /// Local receipt, backlog included.
    Receipt,
}

impl Basis {
    pub fn name(self) -> &'static str {
        match self {
            Basis::NodeTs => "node_ts",
            Basis::Receipt => "receipt",
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
    pub basis: Basis,
    /// Local monotonic ns minus node ms * 1e6 of the least delayed recent event.
    pub offset_ns: Option<i64>,
    pub anchor_slot: u64,
    pub anchor_ns: i64,
    pub slot_ns: f64,
    /// Median duration from a slot to the next by the slot's position in its window.
    pub step_ns: Option<[f64; WINDOW_SLOTS as usize]>,
}

impl Model {
    pub fn predict(&self, slot: u64) -> i64 {
        if let Some(steps) = self.step_ns {
            if slot >= self.anchor_slot && slot - self.anchor_slot <= STEP_HORIZON {
                let t: f64 = (self.anchor_slot..slot).map(|s| steps[(s % WINDOW_SLOTS) as usize]).sum();
                return self.anchor_ns + t.round() as i64;
            }
        }
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

/// Median step to the next slot by window position, from pairs of consecutive slots
/// that both have an event, over the same history as the fit.
fn steps(points: &BTreeMap<u64, i64>) -> Option<[f64; WINDOW_SLOTS as usize]> {
    let last = *points.keys().next_back()?;
    let mut by_pos: Vec<Vec<f64>> = vec![vec![]; WINDOW_SLOTS as usize];
    let range: Vec<(u64, i64)> = points.range(last.saturating_sub(FIT_SLOTS)..).map(|(s, t)| (*s, *t)).collect();
    for w in range.windows(2) {
        if w[1].0 == w[0].0 + 1 {
            by_pos[(w[0].0 % WINDOW_SLOTS) as usize].push((w[1].1 - w[0].1) as f64);
        }
    }
    let mut out = [0.0; WINDOW_SLOTS as usize];
    for (i, v) in by_pos.iter_mut().enumerate() {
        if v.len() < MIN_STEP_SAMPLES {
            return None;
        }
        v.sort_by(|a, b| a.total_cmp(b));
        out[i] = v[v.len() / 2];
    }
    Some(out)
}

impl State {
    /// Smallest receipt minus node time over the last OFFSET_SLOTS slots, once at least
    /// MIN_FIT_SLOTS events there carry a node timestamp.
    pub fn node_offset_ns(&self) -> Option<i64> {
        let last = *self.first_shred.keys().next_back()?;
        let d: Vec<i64> = self
            .first_shred
            .range(last.saturating_sub(OFFSET_SLOTS)..)
            .filter_map(|(_, (recv, ts))| ts.map(|ts| recv - ts as i64 * 1_000_000))
            .collect();
        (d.len() as u64 >= MIN_FIT_SLOTS).then(|| *d.iter().min().unwrap())
    }

    /// firstShredReceived of a slot on the local monotonic clock, from the node
    /// timestamp; None without a timestamp or an offset.
    pub fn node_time(&self, slot: u64, offset_ns: Option<i64>) -> Option<i64> {
        let ts = self.first_shred.get(&slot)?.1?;
        Some(ts as i64 * 1_000_000 + offset_ns?)
    }

    pub fn model(&self) -> Option<Model> {
        let now = mono_ns();
        let shred: BTreeMap<u64, i64> = self.first_shred.iter().map(|(s, (t, _))| (*s, *t)).collect();
        let fresh = |m: &BTreeMap<u64, i64>| m.iter().next_back().filter(|(_, t)| now - **t < FRESH_NS).map(|(s, t)| (*s, *t));
        // The stream counts as live by receipt; the anchor and the fit stand on node time.
        if fresh(&shred).is_some() {
            if let Some(off) = self.node_offset_ns() {
                let node: BTreeMap<u64, i64> = self
                    .first_shred
                    .iter()
                    .filter_map(|(s, (_, ts))| ts.map(|ts| (*s, ts as i64 * 1_000_000 + off)))
                    .collect();
                if let (Some((&slot, &ns)), Some(slope)) = (node.iter().next_back(), fit(&node)) {
                    return Some(Model { source: Source::FirstShred, basis: Basis::NodeTs, offset_ns: Some(off),
                                        anchor_slot: slot, anchor_ns: ns, slot_ns: slope, step_ns: steps(&node) });
                }
            }
        }
        if let (Some((slot, ns)), Some(slope)) = (fresh(&shred), fit(&shred)) {
            return Some(Model { source: Source::FirstShred, basis: Basis::Receipt, offset_ns: None,
                                anchor_slot: slot, anchor_ns: ns, slot_ns: slope, step_ns: steps(&shred) });
        }
        let (slot, ns) = fresh(&self.slot_events)?;
        let slope = fit(&self.slot_events)?;
        Some(Model { source: Source::SlotSubscribe, basis: Basis::Receipt, offset_ns: None,
                     anchor_slot: slot, anchor_ns: ns, slot_ns: slope, step_ns: steps(&self.slot_events) })
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

/// firstShredReceived drives the clock and slotSubscribe is its fallback.
pub const BOTH: &[&str] = &["slotsUpdatesSubscribe", "slotSubscribe"];
/// slotSubscribe alone: one light event a slot, kept apart from the slotsUpdates stream.
pub const SLOT_ONLY: &[&str] = &["slotSubscribe"];

/// Run both subscriptions on their own thread, reconnecting on any error.
pub fn start(ws_url: String) -> Shared {
    start_with(ws_url, BOTH)
}

/// Run the given subscriptions on one connection on their own thread.
pub fn start_with(ws_url: String, methods: &'static [&'static str]) -> Shared {
    let state: Shared = Arc::new(Mutex::new(State::default()));
    let s = state.clone();
    std::thread::Builder::new()
        .name("slot-clock".into())
        .spawn(move || loop {
            if let Err(e) = run_once(&ws_url, methods, &s) {
                let mut st = s.lock().unwrap();
                st.reconnects += 1;
                // The log gets the origin only: a paid WebSocket URL carries an API key.
                st.last_error = Some(e.replace(&ws_url, &crate::rows::origin(&ws_url)));
            }
            std::thread::sleep(Duration::from_millis(500));
        })
        .expect("slot clock thread");
    state
}

fn run_once(ws_url: &str, methods: &[&str], state: &Shared) -> Result<(), String> {
    let (mut ws, _) = tungstenite::connect(ws_url).map_err(|e| format!("ws connect: {e}"))?;
    for (id, method) in methods.iter().enumerate() {
        let req = json!({"jsonrpc": "2.0", "id": id + 1, "method": method});
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

    /// ts 0 leaves the timestamp out, so the clock stays on receipt times.
    fn shred(slot: u64, ts: u64) -> Value {
        let mut r = json!({"type": "firstShredReceived", "slot": slot});
        if ts > 0 {
            r["timestamp"] = json!(ts);
        }
        json!({"method": "slotsUpdatesNotification", "params": {"result": r}})
    }

    #[test]
    fn node_time_clock_ignores_the_delivery_backlog() {
        let mut st = State::default();
        let now = mono_ns();
        // Slots 210 ms apart on the node; the first 300 events arrive 40 ms after the node
        // stamp, the last 100 meet a backlog growing to 3 s, as on mainnet 2026-10-26.
        let node0_ms: u64 = 1_800_000_000_000;
        let base = now - 399 * 210_000_000 - 40_000_000 - 99 * 30_000_000;
        for i in 0..400u64 {
            let node_ms = node0_ms + i * 210;
            let backlog = if i < 300 { 0 } else { (i - 300) as i64 * 30_000_000 };
            let recv = base + (i * 210) as i64 * 1_000_000 + 40_000_000 + backlog;
            assert!(st.apply(&shred(5000 + i, node_ms), recv));
        }
        let off = st.node_offset_ns().expect("offset");
        assert_eq!(off, base + 40_000_000 - node0_ms as i64 * 1_000_000);
        let m = st.model().expect("model");
        assert_eq!((m.source, m.basis), (Source::FirstShred, Basis::NodeTs));
        assert_eq!(m.anchor_slot, 5399);
        // The anchor sits where an event without backlog would have arrived, 2.97 s
        // before its actual receipt.
        assert_eq!(m.anchor_ns, base + 399 * 210_000_000 + 40_000_000);
        assert!((m.slot_ns - 210e6).abs() < 1.0, "{}", m.slot_ns);
        assert_eq!(st.node_time(5100, m.offset_ns), Some(base + 100 * 210_000_000 + 40_000_000));
        let recv_anchor = st.first_shred[&5399].0;
        assert_eq!(recv_anchor - m.anchor_ns, 99 * 30_000_000);
    }

    #[test]
    fn receipt_basis_without_timestamps() {
        let mut st = State::default();
        let now = mono_ns();
        for i in 0..200u64 {
            st.apply(&shred(i, 0), now - ((199 - i) * 200_000_000) as i64);
        }
        assert_eq!(st.node_offset_ns(), None);
        let m = st.model().expect("model");
        assert_eq!((m.source, m.basis, m.offset_ns), (Source::FirstShred, Basis::Receipt, None));
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
    fn steps_by_window_position_near_the_anchor() {
        let mut st = State::default();
        // Window slots 150 ms apart, the handoff to the next window 450 ms: 900 ms a window.
        let step = |s: u64| if s % 4 == 3 { 450_000_000i64 } else { 150_000_000 };
        let mut t = mono_ns() - (0..399u64).map(step).sum::<i64>();
        for s in 0..400u64 {
            st.apply(&shred(s, 0), t);
            t += step(s);
        }
        let m = st.model().expect("model");
        assert_eq!(m.anchor_slot, 399);
        assert_eq!(m.step_ns, Some([150e6, 150e6, 150e6, 450e6]));
        assert!((m.slot_ns - 225e6).abs() < 1e6, "{}", m.slot_ns);
        // Slot 399 ends a window: the next window starts one handoff later, its second
        // slot 150 ms after that.
        assert_eq!(m.predict(400) - m.anchor_ns, 450_000_000);
        assert_eq!(m.predict(401) - m.anchor_ns, 600_000_000);
        assert_eq!(m.predict(404) - m.anchor_ns, 1_350_000_000);
        // Far ahead the fitted mean takes over.
        assert_eq!(m.predict(799) - m.anchor_ns, (400.0 * m.slot_ns).round() as i64);
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
