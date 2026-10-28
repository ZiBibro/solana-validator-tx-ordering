"""Analysis of raw runs without network (sections 6, 8 and 10).

Reads data/runs/<run_id>/probes.jsonl and collect.jsonl, builds the order
groups of section 6, runs the class tests with both Holm families, the class
pair tests, strictness and inclusion shares, and returns one result dict that
REPORT tables are generated from.
"""

import json
import os
from collections import namedtuple

from . import prereg, rawformat, stats, verdict

Run = namedtuple("Run", "run bursts probes sends ends inclusions slots")
# signers: one frozenset per order block, the market-tick signers of that block's slot.
Unit = namedtuple("Unit", "run_id burst_seq burst blocks reasons arrival_ms signers", defaults=(None,))

DELIVERED = ("finished", "rpc_ok")

# The known tick signer of each builder class (analysis plan section 8, campaign addendum section 7):
# a slot of such a class enters the builder rule only with a tick of this key.
BAM_SIGNER = "BAMgx3XPWrXkNUuQiVWUZU6eB2HQZdwz9HNnT4tpo8LG"
HARMONIC_SIGNER = "Harmonic8SoAfZixJqUxxdSeyWzr6q7XFjuiXS5Z2zPg"
BUILDER_SIGNER = {"AgaveBam": BAM_SIGNER, "FireBAM": BAM_SIGNER,
                  "HarmonicAgave": HARMONIC_SIGNER, "HarmonicFiredancer": HARMONIC_SIGNER}


def load_run(run_dir):
    run = None
    bursts, probes, sends, ends, inclusions, slots = {}, {}, {}, {}, {}, {}
    for _, row in rawformat.read_jsonl(os.path.join(run_dir, "probes.jsonl")):
        kind = row.get("kind")
        if kind == "run":
            run = row
        elif kind == "burst":
            bursts[row["burst_seq"]] = row
        elif kind == "probe":
            probes[row["signature"]] = row
        elif kind == "send":
            sends[row["signature"]] = row
        elif kind == "burst_end":
            ends[row["burst_seq"]] = row
    collect = os.path.join(run_dir, "collect.jsonl")
    if os.path.exists(collect):
        for _, row in rawformat.read_jsonl(collect):
            if row.get("kind") == "inclusion":
                inclusions[row["signature"]] = row
            elif row.get("kind") == "slot":
                slots[row["slot"]] = row
    if run is None:
        raise ValueError(run_dir + ": no run row")
    return Run(run, bursts, probes, sends, ends, inclusions, slots)


def load_runs(data_dir):
    root = os.path.join(data_dir, "runs")
    if not os.path.isdir(root):
        return []
    out = []
    for name in sorted(os.listdir(root)):
        path = os.path.join(root, name)
        if os.path.isfile(os.path.join(path, "probes.jsonl")):
            out.append(load_run(path))
    return out


def arrival_ms(burst, end):
    """Estimated arrival at the leader relative to the first slot start, ms.

    Send offset from the first-shred moment of the first slot on node time
    (schema version 2: the node timestamp moved onto the local clock, so a
    WebSocket backlog does not shift it), else on local receipt, else from the
    predicted slot start; plus half the RTT. The final aim in burst_end, taken
    right before the send, wins over the aim at signing time in the burst row.
    """
    end = end or {}
    rtt = end.get("send_rtt_ns")
    if rtt is None:
        rtt = burst.get("rtt_ns") or 0
    offset = end.get("first_send_node_offset_ns")
    if offset is None:
        offset = end.get("first_send_offset_ns")
    if offset is None:
        if end.get("send_predicted_first_slot_ns") is not None:
            offset = end["send_target_arrival_ns"] - rtt / 2.0 - end["send_predicted_first_slot_ns"]
        else:
            offset = burst["send_at_ns"] - burst["predicted_first_slot_ns"]
    return (offset + rtt / 2.0) / 1e6


def slot2_ms(burst, end):
    """Start of slot 2 from the start of slot 1, ms. Slot steps are uneven
    inside a leader window (plan section 5.1), so the observed firstShredReceived
    gap wins, by the node timestamps first and local receipt second; then the
    probe's final aim; then the mean slot length."""
    end = end or {}
    ts = end.get("node_ts_ms") or [None, None]
    if ts[0] is not None and ts[1] is not None:
        return float(ts[1] - ts[0])
    shreds = end.get("first_shred_ns") or [None, None]
    if shreds[0] is not None and shreds[1] is not None:
        return (shreds[1] - shreds[0]) / 1e6
    if end.get("send_predicted_first_slot_ns") is not None:
        return (end["send_target_arrival_ns"] - end["send_predicted_first_slot_ns"]) / 1e6
    return float(burst["slot_ms"])


def timing_in_band(burst, est_ms, end=None):
    target = prereg.TIMING_TARGET_MS[burst["timing"]]
    if target is None:
        target = slot2_ms(burst, end)
    low, high = prereg.TIMING_BAND_MS[burst["timing"]]
    return target + low <= est_ms <= target + high


def clock_behind(burst):
    """Slot clock behind the cluster when the burst was signed (section 5.1)."""
    if "clock_lag_slots" in burst:
        lag = burst["clock_lag_slots"]
        return lag is not None and lag >= prereg.CLOCK_LAG_SKIP_SLOTS
    ctx = burst.get("blockhash_context_slot")
    return ctx is not None and ctx >= burst["first_slot"] - prereg.BLOCKHASH_LEAD_SLOTS


def units_of(run, later=frozenset()):
    """One Unit per burst with its order blocks and the reasons it stays out of
    the verdict (section 6, last paragraph, and section 8); later holds the
    (run_id, burst_seq) of table bursts sent again after their first copy."""
    by_burst = {}
    for sig, p in run.probes.items():
        by_burst.setdefault(p["burst_seq"], []).append(p)
    slot_bursts = {}
    for inc in run.inclusions.values():
        if inc["status"] == "included" and inc["slot"] is not None:
            slot_bursts.setdefault(inc["slot"], set()).add(inc["burst_seq"])
    out = []
    for seq, b in sorted(run.bursts.items()):
        reasons = []
        if b["path"] != "quic":
            reasons.append("control-path")
        if b["relayer_default_port"] or b.get("tpu_quic_port") == prereg.RELAYER_PORT:
            reasons.append("relayer-port")
        if b.get("leader_client_id") != b["selection_class"]:
            reasons.append("client-differs-from-selection")
        est = arrival_ms(b, run.ends.get(seq))
        if not timing_in_band(b, est, run.ends.get(seq)):
            reasons.append("outside-timing-band")
        if clock_behind(b):
            reasons.append("slot-clock-behind")
        per_slot = {}
        for p in by_burst.get(seq, []):
            inc = run.inclusions.get(p["signature"])
            if not inc or inc["status"] != "included" or not inc["in_target_window"]:
                continue
            per_slot.setdefault(inc["slot"], []).append({
                "pos": inc["tx_index"], "fee": p["priority_fee_lamports"],
                "send_rank": p["send_rank"], "cu_limit": p["cu_limit"],
                "segment": inc.get("tick_segment"),
            })
        order = [(slot, probes) for slot, probes in sorted(per_slot.items()) if len(probes) >= 2]
        blocks = [probes for _, probes in order]
        signers = [frozenset(t.get("signer") for t in (run.slots.get(slot) or {}).get("ticks") or [])
                   for slot, _ in order]
        if any(slot_bursts.get(slot, set()) - {seq} for slot in per_slot):
            reasons.append("foreign-probe-in-block")
        if not blocks:
            reasons.append("fewer-than-two-in-a-block")
        if (run.run["run_id"], seq) in later:
            reasons.append("repeated-burst")
        out.append(Unit(run.run["run_id"], seq, b, blocks, reasons, est, signers))
    return out


def burst_key(burst):
    """A burst of the table: one leader, round, cell and path in one chain epoch."""
    return (burst.get("epoch"), burst.get("round"), burst["leader"], burst["arm"], burst["timing"], burst["path"])


def repeated_bursts(runs, stages=None):
    """[(key, first, again)] for every table burst sent more than once, first and again as
    "run_id/burst_seq" (campaign addendum, section 5). The earliest send counts, by the burst
    row's UTC and then run and sequence; every later copy is again and leaves the tests."""
    sent = []
    for run in runs:
        if stages is not None and run.run["stage"] not in stages:
            continue
        for seq, b in run.bursts.items():
            sent.append((b.get("utc") or "", run.run["run_id"], seq, (run.run["stage"],) + burst_key(b)))
    seen, out = {}, []
    for _, run_id, seq, key in sorted(sent, key=lambda x: x[:3]):
        if key in seen:
            out.append((key, seen[key], "%s/%d" % (run_id, seq)))
        else:
            seen[key] = "%s/%d" % (run_id, seq)
    return out


def later_copies(runs, stages=None):
    """{(run_id, burst_seq)} of the copies repeated_bursts leaves out."""
    out = set()
    for _, _, again in repeated_bursts(runs, stages):
        run_id, seq = again.rsplit("/", 1)
        out.add((run_id, int(seq)))
    return frozenset(out)


def label_failures(runs, stages=None):
    """{signer: [slot, ...]} of every known tick signer whose tick appears in a slot whose
    leader belongs to a class without a builder (analysis plan line 89, campaign addendum
    section 7): that signer's label fails for the data of these runs."""
    out = {}
    for run in runs:
        if stages is not None and run.run["stage"] not in stages:
            continue
        cls_of = {}
        for inc in run.inclusions.values():
            if inc["status"] == "included" and inc["slot"] is not None:
                cls_of[inc["slot"]] = inc.get("actual_leader_class")
        for slot, row in sorted(run.slots.items()):
            cls = cls_of.get(slot)
            if cls is None or cls in BUILDER_SIGNER:
                continue
            for t in row.get("ticks") or []:
                if t.get("signer") in set(BUILDER_SIGNER.values()):
                    out.setdefault(t["signer"], [])
                    if slot not in out[t["signer"]]:
                        out[t["signer"]].append(slot)
    return out


def violations(blocks, arm):
    """(violated pairs, pairs with a different predicted position) of a burst."""
    bad = total = 0
    for block in blocks:
        pr = sorted(block, key=lambda p: p["pos"])
        for i in range(len(pr)):
            for j in range(i + 1, len(pr)):
                a, z = pr[i], pr[j]  # a stands earlier in the block
                if arm in ("independent", "shared"):
                    if a["fee"] == z["fee"]:
                        continue
                    total += 1
                    bad += a["fee"] < z["fee"]
                elif arm == "equal_fee":
                    total += 1
                    bad += a["send_rank"] > z["send_rank"]
                else:
                    if a["cu_limit"] == z["cu_limit"]:
                        continue
                    total += 1
                    bad += a["cu_limit"] > z["cu_limit"]
    return bad, total


def strictness(bursts, arm):
    """Pooled violation share with a jackknife interval, and the share of bursts
    without any violation (section 10)."""
    per = [violations(blocks, arm) for blocks in bursts]
    per = [(bad, tot) for bad, tot in per if tot]
    if not per:
        return None
    share, se, df = stats.jackknife(per, estimator=lambda xs: sum(b for b, _ in xs) / sum(t for _, t in xs))
    low, high = stats.interval(share, se, df)
    clean = sum(1 for bad, _ in per if bad == 0) / len(per)
    return {"share": share, "se": se, "df": df, "low": low, "high": high,
            "bursts": len(per), "bursts_without_violation": clean}


def inclusion_shares(runs):
    """Included in the target window over delivered, by class, timing, path and fee."""
    acc = {}
    for run in runs:
        for sig, p in run.probes.items():
            b = run.bursts.get(p["burst_seq"])
            send = run.sends.get(sig)
            if b is None or send is None or send["result"] not in DELIVERED:
                continue
            key = (b["selection_class"], b["timing"], b["path"], p["priority_fee_lamports"])
            inc = run.inclusions.get(sig)
            hit = bool(inc and inc["status"] == "included" and inc["in_target_window"])
            n, k = acc.get(key, (0, 0))
            acc[key] = (n + 1, k + hit)
    return [{"class": c, "timing": t, "path": path, "fee": fee, "delivered": n, "in_window": k,
             "share": k / n} for (c, t, path, fee), (n, k) in sorted(acc.items())]


def _tau_dict(r):
    if r is None:
        return None
    return {"bursts": r.bursts, "S": r.s, "p": float(r.p), "p_exact": "%d/%d" % (r.p.numerator, r.p.denominator),
            "tau": r.tau, "se": r.se, "df": r.df, "ci95": [r.low, r.high], "tost_p": r.tost_p,
            "mean_burst_tau": r.mean_burst_tau}


def analyze(runs, stages=("campaign",)):
    later = later_copies(runs, stages)
    units = []
    for run in runs:
        if run.run["stage"] in stages:
            units.extend(units_of(run, later))
    kept = [u for u in units if not u.reasons]
    excluded = {}
    for u in units:
        for r in u.reasons:
            excluded[r] = excluded.get(r, 0) + 1

    cells = {}
    for u in kept:
        key = (u.burst["selection_class"], u.burst["arm"], u.burst["timing"])
        cells.setdefault(key, []).append(u)
    results = {key: verdict.cell_results([u.blocks for u in us]) for key, us in cells.items()}

    vtests, etests = {}, {}
    for (cls, arm, timing), res in results.items():
        for name in verdict.VERDICT_SLOTS[arm]:
            if res.get(name) is not None:
                vtests[(cls, arm, timing, name)] = res[name].p
                etests[(cls, arm, timing, name)] = res[name].tost_p
    sig = verdict.holm_decisions(vtests, m=verdict.VERDICT_FAMILY_M)
    eq = verdict.holm_decisions(etests, m=verdict.EQUIV_FAMILY_M)

    cell_rows = []
    for (cls, arm, timing), res in sorted(results.items()):
        s = {n: sig.get((cls, arm, timing, n), False) for n in res}
        e = {n: eq.get((cls, arm, timing, n), False) for n in res}
        form, detail = verdict.cell_form(arm, res, s, e)
        cell_rows.append({
            "class": cls, "arm": arm, "timing": timing, "form": form, "detail": detail,
            "bursts": len(cells[(cls, arm, timing)]),
            "taus": {n: _tau_dict(r) for n, r in res.items()},
            "significant": s, "equivalent": e,
            "strictness": strictness([u.blocks for u in cells[(cls, arm, timing)]], arm),
        })

    failed = label_failures(runs, stages)
    pair_rows = pair_tests(kept, failed)
    return {
        "stages": list(stages), "units": len(units), "kept": len(kept), "excluded": excluded,
        "families": {"verdict": verdict.VERDICT_FAMILY_M, "equivalence": verdict.EQUIV_FAMILY_M,
                     "pair": verdict.PAIR_FAMILY_M},
        "cells": cell_rows, "pairs": pair_rows, "label_failures": failed, "rounds_test": rounds_test(kept),
        "inclusion": inclusion_shares([r for r in runs if r.run["stage"] in stages]),
    }


ROUNDS_ARM, ROUNDS_TIMING = "equal_fee", "slot2"


def rounds_test(kept):
    """Pilot rounds test (section 10) over the kept equal-fee bursts of the slot-2
    condition: tau of send rank against tick segment per class and pooled over every
    burst. The prediction is a positive tau; a negative pooled S, the later-sent probe
    more often in the earlier segment, refutes it."""
    by_class = {}
    for u in kept:
        if u.burst["arm"] == ROUNDS_ARM and u.burst["timing"] == ROUNDS_TIMING:
            pieces = [p for p in map(verdict.segment_piece, u.blocks) if p is not None]
            by_class.setdefault(u.burst["selection_class"], []).append(pieces)
    every = [b for bursts in by_class.values() for b in bursts if b]
    pooled = verdict.class_test("segment", every)
    if pooled is None:
        form = "no data"
    elif pooled.s < 0:
        form = "refuted"
    elif pooled.p < stats.ALPHA:
        form = "supported"
    else:
        form = "not shown"
    negative = sum(1 for b in every if sum(p.s for p in b) < 0)
    return {"arm": ROUNDS_ARM, "timing": ROUNDS_TIMING, "bursts": sum(len(b) for b in by_class.values()),
            "with_two_segments": len(every), "negative_share": negative / len(every) if every else None,
            "classes": {cls: _tau_dict(verdict.class_test("segment", b)) for cls, b in sorted(by_class.items())},
            "pooled": _tau_dict(pooled), "form": form}


def builder_blocks(unit, cls, labelled=True):
    """Order blocks of a burst of class cls for the builder rule (analysis plan section 8):
    for a builder class the blocks whose slot carries a tick of BUILDER_SIGNER[cls]
    (labelled) or the rest; a class without a builder keeps every block."""
    want = BUILDER_SIGNER.get(cls)
    if want is None:
        return unit.blocks
    signers = unit.signers if unit.signers is not None else [frozenset()] * len(unit.blocks)
    return [blk for blk, sg in zip(unit.blocks, signers) if (want in sg) == labelled]


def pair_tests(kept, failed=None):
    """Class differences inside the pairs of section 1 by label swaps per stratum
    (epoch, round, arm, timing); both different-fee arms go into one test. The
    builder class counts only blocks with its builder's tick; its blocks without
    one form the group without a label, one descriptive row per pair, condition
    and tau, outside the Holm family. A pair whose builder's signer is in failed
    (label_failures) keeps its tests in the family of 16 with p 1 and TOST p 1,
    and its row reads as a failed label (campaign addendum, section 7)."""
    failed = failed or {}
    strata = {}
    for u in kept:
        b = u.burst
        if b["arm"] not in ("independent", "shared") or b["round"] is None:
            continue
        key = (b["epoch"], b["round"], b["arm"], b["timing"])
        strata.setdefault(key, {}).setdefault(b["selection_class"], []).append(u)
    rows = []
    ptests, etests = {}, {}
    for a, z in prereg.PAIRS:
        for timing in prereg.TIMINGS:
            for name in ("fee", "cross"):
                diffs, bare = [], []
                for (ep, rnd, arm, t), by_class in sorted(strata.items()):
                    if t != timing or len(by_class.get(a, [])) != 1 or len(by_class.get(z, [])) != 1:
                        continue
                    tz = verdict.burst_tau(by_class[z][0].blocks, name)
                    for labelled, into in ((True, diffs), (False, bare)):
                        ta = verdict.burst_tau(builder_blocks(by_class[a][0], a, labelled), name)
                        if ta is not None and tz is not None:
                            into.append(ta - tz)
                key = (a, z, timing, name)
                if not diffs:
                    rows.append({"pair": [a, z], "timing": timing, "tau": name, "strata": 0})
                else:
                    p, method, b_used, mean, se, df, tost = verdict.pair_test(diffs, seed=prereg.LABEL_TEST_SEED)
                    row = {"pair": [a, z], "timing": timing, "tau": name, "strata": len(diffs),
                           "p": float(p), "method": method, "permutations": b_used,
                           "mean_diff": mean, "se": se, "df": df, "tost_p": tost}
                    if BUILDER_SIGNER.get(a) in failed:
                        p = tost = 1
                        row.update({"p": 1.0, "tost_p": 1.0, "label_failed": failed[BUILDER_SIGNER[a]]})
                    ptests[key] = p
                    etests[key] = tost
                    rows.append(row)
                if bare:
                    rows.append({"pair": [a, z], "timing": timing, "tau": name, "strata": len(bare),
                                 "without_label": True, "mean_diff": sum(bare) / len(bare),
                                 "form": "descriptive"})
    sig = verdict.holm_decisions(ptests, m=verdict.PAIR_FAMILY_M)
    eq = verdict.holm_decisions(etests, m=verdict.PAIR_FAMILY_M)
    for row in rows:
        key = (row["pair"][0], row["pair"][1], row["timing"], row["tau"])
        if row.get("without_label"):
            continue
        if row.get("label_failed"):
            row["form"] = "builder-label-failed"
        elif key in ptests:
            row["form"] = verdict.pair_form(sig[key], eq[key])
        else:
            row["form"] = "undetermined"
    return rows


def write_result(result, path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(result, f, indent=1, sort_keys=True)
        f.write("\n")


def summary_lines(result):
    lines = ["units %d, kept %d, excluded %s" % (result["units"], result["kept"],
                                                 json.dumps(result["excluded"], sort_keys=True))]
    for c in result["cells"]:
        taus = " ".join("%s %.3f (p %.3g)" % (n, t["tau"], t["p"]) for n, t in sorted(c["taus"].items()) if t)
        lines.append("%-18s %-11s %-6s %3d bursts  %-16s %s  %s" % (
            c["class"], c["arm"], c["timing"], c["bursts"], c["form"], c["detail"] or "", taus))
    for r in result["pairs"]:
        if r.get("without_label"):
            lines.append("pair %s vs %s %-6s %-5s %2d strata  diff %.3f  without its tick, %s" % (
                r["pair"][0], r["pair"][1], r["timing"], r["tau"], r["strata"], r["mean_diff"], r["form"]))
        elif r["strata"]:
            lines.append("pair %s vs %s %-6s %-5s %2d strata  diff %.3f  p %.3g  %s" % (
                r["pair"][0], r["pair"][1], r["timing"], r["tau"], r["strata"], r["mean_diff"], r["p"], r["form"]))
    rt = result.get("rounds_test")
    if rt and rt["pooled"]:
        lines.append("rounds test %s %s: %d bursts, %d with two segments, negative %.2f, pooled tau %.3f (p %.3g)  %s"
                     % (rt["arm"], rt["timing"], rt["bursts"], rt["with_two_segments"], rt["negative_share"],
                        rt["pooled"]["tau"], rt["pooled"]["p"], rt["form"]))
    elif rt:
        lines.append("rounds test %s %s: %d bursts, none with two segments  %s"
                     % (rt["arm"], rt["timing"], rt["bursts"], rt["form"]))
    return lines
