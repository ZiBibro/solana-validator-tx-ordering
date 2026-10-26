//! Slot clock check (plan, section 5.1). The mainnet dry-run of 2026-10-26 found the
//! WebSocket node of the public RPC 5-24 slots behind the cluster, with the lag moving
//! between bursts, while the run's own arrival estimates stood on those late events
//! and could not see it. This check measures the lag directly: K subscriptions run
//! side by side, each on its own connection, and once a second getSlot at processed
//! commitment over HTTP gives a slot the cluster has reached at least. The gap of a
//! subscription is that slot minus its newest firstShredReceived slot, so a node that
//! falls behind shows a growing gap, and the fused gap shows what the earliest of the
//! K connections would give. Delivery is the local wall time of receipt minus the
//! node's own timestamp of the event; it moves when the path from the node lags.
//!
//!   itb-probe clock [--seconds N] [--connections K]

use crate::clock::{mono_ns, sleep_until_ns, utc_now};
use crate::rpc::Rpc;
use crate::session::Settings;
use crate::slots;
use serde_json::{json, Value};
use std::time::{SystemTime, UNIX_EPOCH};

const SAMPLE_NS: i64 = 1_000_000_000;
/// Gaps from this many slots count as lagging in the summary.
const LAG_SLOTS: i64 = 3;

struct Newest {
    shred_slot: Option<u64>,
    shred_age_ms: Option<f64>,
    delivery_ms: Option<f64>,
    slot_slot: Option<u64>,
    reconnects: u64,
}

fn wall_ms() -> f64 {
    SystemTime::now().duration_since(UNIX_EPOCH).map(|d| d.as_secs_f64() * 1e3).unwrap_or(0.0)
}

fn newest(clock: &slots::Shared, now_mono: i64, now_wall_ms: f64) -> Newest {
    let st = clock.lock().unwrap();
    let shred = st.first_shred.iter().next_back().map(|(s, (t, ts))| (*s, *t, *ts));
    Newest {
        shred_slot: shred.map(|x| x.0),
        shred_age_ms: shred.map(|x| (now_mono - x.1) as f64 / 1e6),
        delivery_ms: shred.and_then(|(_, t, ts)| ts.map(|ts| now_wall_ms - (now_mono - t) as f64 / 1e6 - ts as f64)),
        slot_slot: st.slot_events.keys().next_back().copied(),
        reconnects: st.reconnects,
    }
}

/// Median, 90th percentile and maximum of a sample; None when it is empty.
fn spread(v: &mut [f64]) -> Value {
    if v.is_empty() {
        return Value::Null;
    }
    v.sort_by(|a, b| a.total_cmp(b));
    let at = |p: f64| v[(((v.len() - 1) as f64) * p).round() as usize];
    json!({"median": at(0.5), "p90": at(0.9), "max": at(1.0)})
}

pub fn check(settings: &Settings, seconds: u64, connections: usize) -> Result<(), String> {
    let mut rpc = Rpc::new(&settings.rpc_url);
    let clocks: Vec<slots::Shared> = (0..connections).map(|_| slots::start(settings.ws_url.clone())).collect();
    println!(
        "clock check {}: {connections} WebSocket connections to {}, getSlot processed over {} once a second for {seconds} s",
        utc_now(),
        crate::rows::origin(&settings.ws_url),
        crate::rows::origin(&settings.rpc_url)
    );
    let start = mono_ns();
    let end = start + seconds as i64 * SAMPLE_NS;
    let mut gaps: Vec<Vec<f64>> = vec![vec![]; connections];
    let mut slot_gaps: Vec<Vec<f64>> = vec![vec![]; connections];
    let mut delivery: Vec<Vec<f64>> = vec![vec![]; connections];
    let mut fused: Vec<f64> = vec![];
    let mut http_ms: Vec<f64> = vec![];
    let mut next = start + SAMPLE_NS;
    while next <= end {
        sleep_until_ns(next);
        next += SAMPLE_NS;
        let t0 = mono_ns();
        let http = match rpc.call("getSlot", json!([{"commitment": "processed"}])) {
            Ok(v) => v.as_u64(),
            Err(e) => {
                println!("{}", json!({"utc": utc_now(), "http_error": e.to_string()}));
                continue;
            }
        };
        let t1 = mono_ns();
        let Some(h) = http else { continue };
        let (now_mono, now_wall) = (mono_ns(), wall_ms());
        let rows: Vec<Newest> = clocks.iter().map(|c| newest(c, now_mono, now_wall)).collect();
        let mut ws = vec![];
        for (i, n) in rows.iter().enumerate() {
            let gap = n.shred_slot.map(|s| h as i64 - s as i64);
            if let Some(g) = gap {
                gaps[i].push(g as f64);
            }
            if let Some(s) = n.slot_slot {
                slot_gaps[i].push(h as f64 - s as f64);
            }
            if let Some(d) = n.delivery_ms {
                delivery[i].push(d);
            }
            ws.push(json!({"shred_slot": n.shred_slot, "gap": gap, "age_ms": n.shred_age_ms,
                           "delivery_ms": n.delivery_ms, "slot_gap": n.slot_slot.map(|s| h as i64 - s as i64),
                           "reconnects": n.reconnects}));
        }
        let best = rows.iter().filter_map(|n| n.shred_slot).max();
        if let Some(b) = best {
            fused.push(h as f64 - b as f64);
        }
        http_ms.push((t1 - t0) as f64 / 1e6);
        println!("{}", json!({"utc": utc_now(), "http_slot": h, "http_ms": (t1 - t0) as f64 / 1e6,
                              "fused_gap": best.map(|b| h as i64 - b as i64), "ws": ws}));
    }
    if fused.is_empty() {
        return Err("clock check: no sample had both an HTTP slot and a firstShredReceived event".into());
    }
    let share = |v: &[f64]| v.iter().filter(|g| **g >= LAG_SLOTS as f64).count() as f64 / v.len().max(1) as f64;
    let mut per = vec![];
    for i in 0..connections {
        let errors = clocks[i].lock().unwrap().last_error.clone();
        per.push(json!({"connection": i, "samples": gaps[i].len(), "lagging_share": share(&gaps[i]),
                        "gap_slots": spread(&mut gaps[i]), "slot_subscribe_gap_slots": spread(&mut slot_gaps[i]),
                        "delivery_ms": spread(&mut delivery[i]), "last_error": errors}));
    }
    let summary = json!({"samples": fused.len(), "lag_from_slots": LAG_SLOTS, "fused_lagging_share": share(&fused),
                         "fused_gap_slots": spread(&mut fused), "http_ms": spread(&mut http_ms), "connections": per});
    println!("summary: {summary}");
    Ok(())
}
