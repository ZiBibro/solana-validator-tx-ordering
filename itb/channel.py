"""Health of the operator's line, round by round (plan-implementation, section 11).

Other traffic on a home line shows in a run before it spoils the verdict: the
estimated arrival leaves the timing band, the slot clock fed by first-shred
events falls behind getSlot and the probe skips the burst, QUIC handshakes to
the leaders and getSlot round trips to the RPC node grow. rounds() reads these
per round from probes.jsonl and the run log, below() names the thresholds a
round misses, rpc_rtt() times getSlot round trips over a kept-alive
connection, and watch() journals every finished round of the live runs and
stops at the first round below a threshold.

THRESHOLDS rest on the mainnet pilot of 2026-10-27 (run
pilot-mainnet-20261027T085253Z, 68 bursts in four rounds of 17): 62 bursts in
the band, rounds from 14 to 17 of 17; no clock skip and no failed handshake;
round medians of 38.5 to 43.2 ms for QUIC handshakes and 48.2 to 54.0 ms for
getSlot.
"""

import http.client
import json
import os
import statistics
import time
import urllib.parse

from . import analyze

THRESHOLDS = {
    # A class and cell of the campaign holds 8 bursts; three quarters keeps 6 of them.
    # At the pilot's 62 of 68 a round of 16 falls below by chance with probability
    # 0.010 and one of 24 with 0.004, about one false alarm in four campaigns of 32
    # rounds; a line that drops the share to 0.6 is caught in 83 to 90 rounds of 100.
    # 0.80 would raise a false alarm in four campaigns of five.
    "in_band_share_min": 0.75,
    # Bursts the probe skipped because its slot clock lagged getSlot by 2 slots or more.
    "clock_skip_share_max": 0.10,
    "handshake_fail_share_max": 0.10,
    # Arrival is aimed at half the RTT, so growth that sits on one direction only
    # moves the true arrival by half of it: 100 ms over the pilot median moves it
    # 50 ms, half of the slot2 band.
    "quic_rtt_median_ms_max": 150.0,
    # About three times the pilot medians; the RPC node also feeds the slot clock
    # its first-shred events, so a slow line to it delays the clock as well.
    "http_rtt_median_ms_max": 150.0,
}
# A share over fewer bursts says little; such a round gets no share verdict.
MIN_BURSTS = 4
RPC_FAIL_SHARE_MAX = 0.05

EXIT_BELOW = 3
EXIT_STOPPED = 4


def read_rows(path):
    """Rows of a JSON-lines file another process may still be writing: a missing
    file gives none, and a last line without its newline waits for the next read."""
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.endswith("\n"):
                break
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def spread(values):
    """[min, median, max] in ms, one decimal, or None for no values."""
    if not values:
        return None
    return [round(min(values), 1), round(statistics.median(values), 1), round(max(values), 1)]


def _clock_skip(reason):
    return reason.startswith("slot clock") and "behind" in reason


def rounds(rows, events, partial=False):
    """One dict per round of a run whose windows are all done (every round when
    the run log has its summary, any round with partial). rows are the run's
    probes.jsonl rows, events its log rows."""
    bursts = {r["burst_seq"]: r for r in rows if r.get("kind") == "burst"}
    ends = {r["burst_seq"]: r for r in rows if r.get("kind") == "burst_end"}
    skipped, failed, handshake_rtt = {}, set(), {}
    finished = False
    for e in events:
        ev, seq = e.get("event"), e.get("burst_seq")
        if ev == "burst_skipped":
            skipped[seq] = (e.get("data") or {}).get("reason", "")
        elif ev == "burst_failed":
            failed.add(seq)
        elif ev == "quic_connected" and seq not in handshake_rtt:
            handshake_rtt[seq] = (e.get("data") or {}).get("rtt_ns")
        elif ev == "summary":
            finished = True
    done = set(ends) | set(skipped) | failed
    out = []
    for rd in (r for r in rows if r.get("kind") == "round"):
        seqs = [w["burst_seq"] for w in rd["windows"]]
        complete = finished or all(s in done for s in seqs)
        if not complete and not partial:
            continue
        written = [s for s in seqs if s in bursts]
        in_band = sum(1 for s in written
                      if analyze.timing_in_band(bursts[s], analyze.arrival_ms(bursts[s], ends.get(s)), ends.get(s)))
        lags = [bursts[s]["clock_lag_slots"] for s in written if bursts[s].get("clock_lag_slots") is not None]
        quic = [s for s in written if bursts[s].get("path") == "quic"]
        hs_fail = sum(1 for s in quic if isinstance(bursts[s].get("handshake"), dict) and not bursts[s]["handshake"]["ok"])
        rtt = []
        for s in quic:
            ns = handshake_rtt.get(s) or bursts[s].get("rtt_ns")
            if ns:
                rtt.append(ns / 1e6)
        http = [bursts[s]["http_slot_rtt_ns"] / 1e6 for s in written if bursts[s].get("http_slot_rtt_ns")]
        clock_skips = sum(1 for s in seqs if _clock_skip(skipped.get(s, "")))
        out.append({
            "kind": "round_channel", "run_id": rd["run_id"], "round": rd["round"], "epoch": rd.get("epoch"),
            "complete": complete, "planned": len(seqs), "written": len(written),
            "skipped_clock": clock_skips, "skipped_other": sum(1 for s in seqs if s in skipped) - clock_skips,
            "failed": sum(1 for s in seqs if s in failed),
            "in_band": in_band, "in_band_share": round(in_band / len(written), 3) if written else None,
            "clock_lag_max": max(lags) if lags else None, "clock_lag_ge1": sum(1 for x in lags if x >= 1),
            "handshake_fail": hs_fail, "quic_rtt_ms": spread(rtt),
            "reconnects": sum(ends[s].get("reconnects") or 0 for s in written if s in ends),
            "http_rtt_ms": spread(http),
        })
    for r in out:
        r["below"] = below(r)
    return out


def below(r, t=THRESHOLDS):
    """Names of the thresholds a round summary misses."""
    out = []
    if r["written"] >= MIN_BURSTS and r["in_band_share"] < t["in_band_share_min"]:
        out.append("in_band_share")
    if r["planned"] and r["skipped_clock"] / r["planned"] > t["clock_skip_share_max"]:
        out.append("clock_skip_share")
    if r["written"] and r["handshake_fail"] / r["written"] > t["handshake_fail_share_max"]:
        out.append("handshake_fail_share")
    if r["quic_rtt_ms"] and r["quic_rtt_ms"][1] > t["quic_rtt_median_ms_max"]:
        out.append("quic_rtt_median")
    if r["http_rtt_ms"] and r["http_rtt_ms"][1] > t["http_rtt_median_ms_max"]:
        out.append("http_rtt_median")
    return out


def run_rounds(data_dir, logs_dir, run_id, partial=False):
    rows = read_rows(os.path.join(data_dir, "runs", run_id, "probes.jsonl"))
    if not rows:
        raise ValueError("no probes.jsonl rows for run " + run_id)
    return rounds(rows, read_rows(os.path.join(logs_dir, run_id + ".jsonl")), partial)


def rpc_rtt(url, seconds, interval, clock=time.monotonic, sleep=time.sleep, connect=None):
    """getSlot round trips to url over one kept-alive HTTPS connection, the way
    the probe reaches its RPC node; a failed request drops the connection and
    counts. The first request also pays the handshakes and is left out."""
    parts = urllib.parse.urlsplit(url)
    connect = connect or (lambda: http.client.HTTPSConnection(parts.hostname, parts.port, timeout=10))
    path = parts.path or "/"
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "getSlot", "params": [{"commitment": "processed"}]})
    headers = {"content-type": "application/json"}
    conn, warm, rtts, failed = None, False, [], 0
    end = clock() + seconds
    while clock() < end:
        t0 = clock()
        try:
            if conn is None:
                conn, warm = connect(), False
            conn.request("POST", path, body, headers)
            reply = conn.getresponse()
            data = reply.read()
            if reply.status != 200 or "result" not in json.loads(data):
                raise ValueError("HTTP %d" % reply.status)
            if warm:
                rtts.append((clock() - t0) * 1000.0)
            warm = True
        except (OSError, ValueError, http.client.HTTPException):
            failed += 1
            if conn is not None:
                conn.close()
            conn = None
        sleep(max(0.0, t0 + interval - clock()))
    if conn is not None:
        conn.close()
    rtts.sort()
    p90 = round(rtts[int(0.9 * (len(rtts) - 1))], 1) if rtts else None
    tries = len(rtts) + failed
    result = {"kind": "rpc_channel", "samples": len(rtts), "failed": failed,
              "http_rtt_ms": spread(rtts), "http_rtt_p90_ms": p90}
    result["below"] = []
    if tries and failed / tries > RPC_FAIL_SHARE_MAX:
        result["below"].append("rpc_fail_share")
    if result["http_rtt_ms"] and result["http_rtt_ms"][1] > THRESHOLDS["http_rtt_median_ms_max"]:
        result["below"].append("http_rtt_median")
    return result


def _live_runs(data_dir, stage):
    root = os.path.join(data_dir, "runs")
    if not os.path.isdir(root):
        return []
    out = []
    for name in sorted(os.listdir(root)):
        rows = read_rows(os.path.join(root, name, "probes.jsonl"))
        if rows and rows[0].get("kind") == "run" and rows[0].get("stage") == stage and rows[0].get("mode") == "live":
            out.append((name, rows))
    return out


def watch(data_dir, logs_dir, journal, stage="campaign", transcript=None, poll=60.0,
          sleep=time.sleep, say=print, once=False):
    """Append every finished round of the live runs of a stage to journal, once.
    Returns EXIT_BELOW at the first round below a threshold, 0 once the campaign
    transcript says the campaign is done, EXIT_STOPPED when it says it stopped."""
    seen = {(r["run_id"], r["round"]) for r in read_rows(journal)}
    while True:
        for run_id, rows in _live_runs(data_dir, stage):
            for r in rounds(rows, read_rows(os.path.join(logs_dir, run_id + ".jsonl"))):
                if (r["run_id"], r["round"]) in seen:
                    continue
                r["utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                with open(journal, "a", encoding="utf-8", newline="\n") as f:
                    f.write(json.dumps(r, sort_keys=True) + "\n")
                seen.add((r["run_id"], r["round"]))
                say(json.dumps(r, sort_keys=True))
                if r["below"]:
                    return EXIT_BELOW
        if transcript and os.path.exists(transcript):
            with open(transcript, encoding="utf-8", errors="replace") as f:
                text = f.read()
            if "campaign done" in text:
                return 0
            if "campaign stopped" in text:
                return EXIT_STOPPED
        if once:
            return 0
        sleep(poll)
