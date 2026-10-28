"""Generated tables of REPORT.md (plan sections 8 and 9).

REPORT.md is prose with generated blocks in it. A block runs from the line
<!-- itb:begin NAME --> to the line <!-- itb:end NAME -->, and everything
between the two comes from blocks(): after a new run `python -m itb report`
rewrites the numbers and leaves the prose alone, and `python -m itb report
--check` names every block that no longer matches the raw data. The pilot and
the campaign get blocks of their own, so pilot numbers never stand in a
campaign verdict.

Every table here is computed from data/runs without network; the tick table
of one whole epoch comes from research/tick-scale, where its script and raw
rows live. The descriptive tables (analysis plan sections 5 to 9) stand next to
the verdicts and never change them: their taus are pooled over bursts with a
jackknife interval and carry no test, except the label permutation of the
control path, which the plan asks for.
"""

import datetime
import gzip
import itertools
import json
import math
import os
import random
import re
import statistics
from collections import namedtuple

from . import analyze, chain, panel, plan, prereg, rawformat, stats, verdict

BEGIN = re.compile(r"^<!-- itb:begin ([a-z0-9-]+) -->$")
END = "<!-- itb:end %s -->"
LAMPORTS_PER_SOL = 1_000_000_000
ANCHOR_FEE_LAMPORTS = 5000
BAM_SIGNER = analyze.BAM_SIGNER
HARMONIC_SIGNER = analyze.HARMONIC_SIGNER
EXPECTED_SIGNER = analyze.BUILDER_SIGNER
STAGES = ("pilot", "campaign")
NO_RUNS = "No runs of this stage yet."
DIFFERENT_FEE = ("independent", "shared")
# Agave burns half of each signature fee; the rest and the whole priority fee
# reach the leader, and its scheduler ranks by that reward per unit of cost.
BURNED_SIGNATURE_SHARE = 0.5
# Loaded-accounts allowance of a transaction without SetLoadedAccountsDataSizeLimit
# in Agave's compute budget: 64 MiB, which costs 16 384 units on its own.
DEFAULT_LOADED_DATA_BYTES = 64 * 1024 * 1024

# A burst of a stage with the slots of its order blocks, in the order of unit.blocks.
Item = namedtuple("Item", "run unit slots")


def _utc(seconds):
    return datetime.datetime.fromtimestamp(seconds, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _short(key):
    return key[:8] + "..." if key else "-"


def _table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"]
    out += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return "\n".join(out)


def _p(x):
    return "%.3g" % x


def _drawn(p, b):
    """How a p drawn from b arrangements came about (analysis plan line 39)."""
    return "%d draws, seed %s, Monte Carlo SE %.2g" % (b, prereg.LABEL_TEST_SEED, math.sqrt(p * (1 - p) / b))


def _interval(low, high):
    if low is None or math.isnan(low):
        return "no interval"
    return "%.3f to %.3f" % (low, high)


def _median(xs):
    return statistics.median(xs) if xs else None


def _ms(x):
    return "-" if x is None else "%.0f" % x


def live(runs):
    return [r for r in runs if r.run["mode"] == "live" and r.run["network"] == "mainnet"]


def _included(run):
    return [i for i in run.inclusions.values() if i["status"] == "included"]


def _delivered(run):
    return sum(1 for s in run.sends.values() if s["result"] in analyze.DELIVERED)


def runs_block(runs):
    rows = []
    for r in runs:
        inc = _included(r)
        rows.append(["`%s`" % r.run["run_id"], r.run["stage"], r.run["network"], r.run["mode"],
                     r.run["started_utc"][:19].replace("T", " "), len(r.bursts), len(r.probes), _delivered(r),
                     len(inc) if r.inclusions else "-",
                     sum(1 for i in inc if i["in_target_window"]) if r.inclusions else "-",
                     "`%s`" % r.run["git_commit"][:7]])
    return _table(["Run", "Stage", "Network", "Mode", "Started (UTC)", "Bursts", "Probes", "Delivered",
                   "Included", "In target window", "Commit"], rows)


def _payer_moves(logs_dir, run_id):
    """(transactions that fund or close the payers, growth of the spend journal)
    from the run's log; the journal lives in a Docker volume and the log keeps
    its totals. (None, None) without a log."""
    path = os.path.join(logs_dir, run_id + ".jsonl")
    if not os.path.exists(path):
        return None, None
    moves, start, end = 0, None, None
    with open(path, encoding="utf-8") as f:
        for line in f:
            e = json.loads(line)
            data = e.get("data") or {}
            if e.get("event") in ("fund_send", "close_send"):
                moves += 1
            elif e.get("event") == "journal_reconciled" and start is None:
                start = data.get("committed")
            elif e.get("event") == "journal_resolved":
                end = data.get("committed")
    return moves, (end - start if start is not None and end is not None else None)


def spend_block(runs, anchors, logs_dir):
    """Every fee paid: anchors, probes by meta.fee, and one signature fee for each
    transaction that funds or closes the payers, which the log names by signature."""
    rows, total = [], 0
    for a in anchors:
        total += ANCHOR_FEE_LAMPORTS
        rows.append(["anchor of %s" % a["stage"], _utc(a["block_time"]), "`%s`" % a["signature"][:16] + "...",
                     "-", "-", ANCHOR_FEE_LAMPORTS, "-", "-"])
    for r in live(runs):
        fees = sum(i["fee"] or 0 for i in _included(r))
        moves, journal = _payer_moves(logs_dir, r.run["run_id"])
        overhead = None if moves is None else moves * chain.LAMPORTS_PER_SIGNATURE
        total += fees + (overhead or 0)
        rows.append(["`%s`" % r.run["run_id"], r.run["started_utc"][:19].replace("T", " "),
                     "%d probes included, %s funding and closing transactions" % (
                         len(_included(r)), "-" if moves is None else moves),
                     fees, "-" if overhead is None else overhead, fees + (overhead or 0),
                     "-" if journal is None else journal, r.run["spend_limit_lamports"]])
    rows.append(["**total**", "", "", "", "", "**%d** (%.6f SOL)" % (total, total / LAMPORTS_PER_SOL), "",
                 "code cap %.2f SOL" % (max([r.run["code_limit_lamports"] for r in live(runs)] or [0])
                                        / LAMPORTS_PER_SOL)])
    return _table(["Item", "UTC", "What", "Probe fees (lamports)", "Funding and closing fees", "Paid",
                   "Spend journal growth", "Limit of the run (lamports)"], rows)


def panel_block(runs):
    leaders = {}
    for r in live(runs):
        for b in r.bursts.values():
            e = leaders.setdefault(b["leader"], {"class": b["selection_class"], "gossip": set(), "va": set(),
                                                 "bursts": 0, "included": 0, "stages": set()})
            e["gossip"].add("%s %s" % (b.get("leader_client_id"), b.get("leader_version")))
            va = b.get("validators_app")
            e["va"].add("%s %s" % (va["software_client"], va["software_version"]) if va else "not taken")
            e["bursts"] += 1
            e["stages"].add(r.run["stage"])
        for i in _included(r):
            b = r.bursts.get(i["burst_seq"])
            if b and i["in_target_window"]:
                leaders[b["leader"]]["included"] += 1
    order = {c: n for n, c in enumerate(prereg.CLASSES)}
    rows = [["`%s`" % k, e["class"], ", ".join(sorted(e["gossip"])), ", ".join(sorted(e["va"])),
             ", ".join(s for s in STAGES if s in e["stages"]), e["bursts"], e["included"]]
            for k, e in sorted(leaders.items(), key=lambda kv: (order.get(kv[1]["class"], 99), kv[0]))]
    clients = {e["class"] for e in leaders.values()}
    return (_table(["Leader identity", "Class at selection", "gossip clientId and version at the bursts",
                    "validators.app label", "Stages", "Bursts", "Probes in window"], rows)
            + "\n\n%d validators, %d classes by gossip clientId." % (len(leaders), len(clients)))


def neighbours_block(data_dir):
    """Full windows of each panel's leaders that pass the pilot's rule (no other validator on the
    whole tpuQuic address right before), and among them those after another leader on the same IP
    with a different port (section 8): the windows the campaign's IP rule in panel.py turns away."""
    root = os.path.join(data_dir, "panels")
    rows = []
    for name in sorted(os.listdir(root)) if os.path.isdir(root) else []:
        files = [os.path.join(root, name, f) for f in ("panel.json", "cluster-nodes.json", "leader-schedule.json")]
        if not all(os.path.exists(f) for f in files):
            continue
        loaded = []
        for f in files:
            with open(f, encoding="utf-8") as fh:
                loaded.append(json.load(fh))
        drawn, nodes, schedule = loaded
        tpu = {n["pubkey"]: n.get("tpuQuic") for n in nodes["nodes"]}
        first = schedule["first_slot"]
        owner = {i: leader for leader, indices in schedule["schedule"].items() for i in indices}
        windows = []
        for start, length, leader in plan.windows(schedule["schedule"], first):
            prev = owner.get(start - first - 1)
            other = prev not in (None, leader)
            if length != plan.SLOTS_PER_WINDOW or (other and tpu.get(prev) is not None
                                                   and tpu.get(prev) == tpu.get(leader)):
                continue
            host = panel.host_port(tpu.get(prev))[0] if other else None
            windows.append((leader, host is not None and host == panel.host_port(tpu.get(leader))[0]))
        for cls in prereg.CLASSES:
            ids = {l["identity"] for l in drawn["classes"].get(cls, {}).get("leaders", [])}
            mine = [w for w in windows if w[0] in ids]
            near = sum(1 for _, same_ip in mine if same_ip)
            if mine:
                rows.append(["`%s`" % name, cls, len(mine), near, "%.3f" % (near / len(mine))])
    if not rows:
        return "No panel yet."
    return _table(["Panel", "Class", "Windows of its panel leaders passing the whole-address rule",
                   "After a leader on the same IP with another port", "Share"], rows)


def bursts_block(runs):
    rows = []
    for r in live(runs):
        by_burst = {}
        for i in _included(r):
            by_burst.setdefault(i["burst_seq"], []).append(i)
        sent = {}
        for sig, s in r.sends.items():
            if s["result"] in analyze.DELIVERED:
                p = r.probes.get(sig)
                if p:
                    sent[p["burst_seq"]] = sent.get(p["burst_seq"], 0) + 1
        for seq, b in sorted(r.bursts.items()):
            inc = by_burst.get(seq, [])
            if inc:
                when = _utc(min(i["block_time"] for i in inc))
            else:
                end = r.ends.get(seq) or {}
                when = (end.get("utc_end", "")[:19].replace("T", " ") + " (tool clock)") if end.get("utc_end") else "-"
            actual = sorted({i["actual_leader_class"] or "?" for i in inc if not i["in_target_window"]})
            rows.append(["`%s`" % r.run["run_id"], seq, when, b["epoch"],
                         "%d-%d" % (b["first_slot"], b["first_slot"] + 3), "`%s`" % _short(b["leader"]),
                         b["selection_class"], b.get("leader_client_id") or "-", b["arm"], b["timing"],
                         sent.get(seq, 0), sum(1 for i in inc if i["in_target_window"]),
                         ", ".join(actual) or "-", sum(i["fee"] or 0 for i in inc)])
    return _table(["Run", "Burst", "UTC (blockTime)", "Epoch", "Window slots", "Leader", "Class",
                   "clientId at burst", "Arm", "Timing", "Delivered", "In window", "Other leaders' class",
                   "Fee (lamports)"], rows)


def _stage_runs(runs, stage):
    return [r for r in live(runs) if r.run["stage"] == stage]


def _items(runs):
    """Every burst of the runs with the reasons it stays out and the slots of its order blocks."""
    out = []
    later = analyze.later_copies(runs)
    for r in runs:
        per = {}
        for sig, p in r.probes.items():
            inc = r.inclusions.get(sig)
            if inc and inc["status"] == "included" and inc["in_target_window"]:
                count = per.setdefault(p["burst_seq"], {})
                count[inc["slot"]] = count.get(inc["slot"], 0) + 1
        for u in analyze.units_of(r, later):
            slots = [s for s, n in sorted(per.get(u.burst_seq, {}).items()) if n >= 2]
            if len(slots) != len(u.blocks):
                raise ValueError("report: blocks of burst %s/%d do not match analyze" % (u.run_id, u.burst_seq))
            out.append(Item(r, u, slots))
    return out


def _kept(items):
    return [it for it in items if not it.unit.reasons]


def _pooled(bursts, name):
    """Pooled tau of one measure over bursts (each a list of blocks) with its
    jackknife interval, without a test: (tau, low, high, bursts) or None."""
    pairs = []
    for blocks in bursts:
        s = d = 0
        for block in blocks:
            piece = verdict.burst_pieces(block).get(name)
            if piece is not None:
                s += piece.s
                d += piece.d
        if d:
            pairs.append((s, d))
    if not pairs:
        return None
    tau, se, df = stats.jackknife(pairs)
    low, high = stats.interval(tau, se, df)
    return tau, low, high, len(pairs)


def _tau_text(r):
    if r is None:
        return "-"
    tau, low, high, n = r
    return "%.3f (%s), %d bursts" % (tau, _interval(low, high), n)


def _arms(items, arms):
    return [it.unit.blocks for it in items if it.unit.burst["arm"] in arms]


def exclusions_block(result):
    if result is None:
        return NO_RUNS
    reasons = ", ".join("%s %d" % kv for kv in sorted(result["excluded"].items())) or "none"
    return "%d bursts, %d kept for the order tests. Reasons a burst stays out: %s." % (
        result["units"], result["kept"], reasons)


def cells_block(result):
    if result is None:
        return NO_RUNS
    rows = []
    for c in result["cells"]:
        taus = "; ".join("%s %.3f (%s; p %s; mean of burst taus %s)" % (
            n, t["tau"], _interval(*t["ci95"]), _p(t["p"]),
            "-" if t.get("mean_burst_tau") is None else "%.3f" % t["mean_burst_tau"])
            for n, t in sorted(c["taus"].items()) if t)
        st = c["strictness"]
        strict = "-" if not st else "%.3f (%s); %d of %d bursts without a violation" % (
            st["share"], _interval(st["low"], st["high"]), round(st["bursts_without_violation"] * st["bursts"]),
            st["bursts"])
        rows.append([c["class"], c["arm"], c["timing"], c["bursts"], c["form"], c["detail"] or "-", taus, strict])
    return _table(["Class", "Arm", "Timing", "Bursts", "Form", "Detail", "tau (95% CI; p)",
                   "Violated pair share (95% CI)"], rows)


def inclusion_block(result):
    if result is None:
        return NO_RUNS
    rows = [[x["class"], x["timing"], x["path"], x["fee"], x["delivered"], x["in_window"], "%.2f" % x["share"]]
            for x in result["inclusion"]]
    return _table(["Class", "Timing", "Path", "Priority fee (lamports)", "Delivered", "In target window", "Share"],
                  rows)


def rounds_block(result):
    if result is None:
        return NO_RUNS
    rt = result["rounds_test"]
    rows = [[cls, t["bursts"], "%.3f" % t["tau"], _p(t["p"])] for cls, t in rt["classes"].items() if t]
    head = ("Arm %s, timing %s: %d bursts, %d with probes in two segments or more, share of bursts with a "
            "negative S %s. Pooled: %s. Form: **%s**." % (
                rt["arm"], rt["timing"], rt["bursts"], rt["with_two_segments"],
                "-" if rt["negative_share"] is None else "%.2f" % rt["negative_share"],
                "-" if not rt["pooled"] else "tau %.3f, p %s" % (rt["pooled"]["tau"], _p(rt["pooled"]["p"])),
                rt["form"]))
    return head + ("\n\n" + _table(["Class", "Bursts", "tau send rank against segment", "p"], rows) if rows else "")


def pairs_block(result):
    if result is None:
        return NO_RUNS
    rows = []
    for r in result["pairs"]:
        if r.get("without_label"):
            rows.append(["%s vs %s" % tuple(r["pair"]), r["timing"], r["tau"] + ", builder blocks without its tick",
                         r["strata"], "%.3f" % r["mean_diff"], "-", "-", "-", r["form"]])
        elif not r["strata"]:
            rows.append(["%s vs %s" % tuple(r["pair"]), r["timing"], r["tau"], 0, "-", "-", "-", "-", r["form"]])
        else:
            test = ("exact over %d" % r["permutations"] if r["method"] == "exact"
                    else _drawn(r["p"], r["permutations"]))
            if r.get("label_failed"):
                test = "label failed, p set to 1"
            rows.append(["%s vs %s" % tuple(r["pair"]), r["timing"], r["tau"], r["strata"], "%.3f" % r["mean_diff"],
                         _p(r["p"]), _p(r["tost_p"]), test, r["form"]])
    out = _table(["Pair", "Timing", "Statistic", "Strata", "Mean difference", "p", "TOST p", "Label test", "Form"],
                 rows)
    failed = result.get("label_failures") or {}
    for signer, slots in sorted(failed.items()):
        out += ("\n\nThe label of signer `%s` failed: its tick stands in %d slots of classes without a builder "
                "(%s). The pairs of its classes keep their tests in the family of %d with p 1."
                % (signer, len(slots), ", ".join(str(x) for x in slots), verdict.PAIR_FAMILY_M))
    return out


def hypotheses_block(result):
    """H3 on Firedancer and H4 on Agave from tau send of the equal-fee arm in pre300, with the
    other classes beside them as comparison only (campaign addendum, section 3)."""
    if result is None:
        return NO_RUNS
    rows = []
    for cls in prereg.CLASSES:
        cell = next((c for c in result["cells"] if (c["class"], c["arm"], c["timing"]) == (cls, "equal_fee", "pre300")),
                    None)
        t = cell and cell["taus"].get("send")
        hyp = {"Firedancer": "H3", "Agave": "H4"}.get(cls, "comparison")
        if not t:
            rows.append([cls, hyp, cell["bursts"] if cell else 0, "-", "-", "-", "-",
                         "undecided" if hyp != "comparison" else "-"])
            continue
        sig, eq = cell["significant"].get("send", False), cell["equivalent"].get("send", False)
        neg, pos = sig and t["tau"] < 0, sig and t["tau"] > 0
        if hyp == "H3":
            outcome = "holds" if neg else "fails" if pos or eq else "undecided"
        elif hyp == "H4":
            outcome = ("fails" if pos else "agrees with the fresh-key part" if neg
                       else "agrees with the recycled-key part" if eq else "undecided")
        else:
            outcome = "-"
        rows.append([cls, hyp, cell["bursts"], "%.3f (%s)" % (t["tau"], _interval(*t["ci95"])), _p(t["p"]),
                     "yes" if sig else "no", "yes" if eq else "no", outcome])
    return _table(["Class", "Hypothesis", "Bursts", "tau send, equal fee, pre300 (95% CI)", "p",
                   "Significant after Holm", "TOST passed after Holm", "Outcome"], rows)


def _target_ms(item):
    b = item.unit.burst
    target = prereg.TIMING_TARGET_MS[b["timing"]]
    return target if target is not None else analyze.slot2_ms(b, item.run.ends.get(item.unit.burst_seq))


def timing_block(items):
    """Share of bursts in the timing band per condition and class (plan section 6)."""
    mine = [it for it in items if it.unit.burst["path"] == "quic"]
    if not mine:
        return NO_RUNS
    rows = []
    for timing in prereg.TIMINGS:
        group = [it for it in mine if it.unit.burst["timing"] == timing]
        if not group:
            continue
        inband = sum(1 for it in group if "outside-timing-band" not in it.unit.reasons)
        offsets = sorted(it.unit.arrival_ms - _target_ms(it) for it in group)
        rows.append([timing, len(group), inband, "%.2f" % (inband / len(group)), _ms(_median(offsets)),
                     "%s to %s" % (_ms(offsets[0]), _ms(offsets[-1])),
                     sum(1 for it in group if "slot-clock-behind" in it.unit.reasons)])
    by_class = []
    for cls in prereg.CLASSES:
        cells = []
        for timing in prereg.TIMINGS:
            group = [it for it in mine if it.unit.burst["selection_class"] == cls and it.unit.burst["timing"] == timing]
            inband = sum(1 for it in group if "outside-timing-band" not in it.unit.reasons)
            cells.append("%d of %d" % (inband, len(group)) if group else "-")
        by_class.append([cls] + cells)
    return (_table(["Condition", "Bursts", "In the band", "Share", "Median arrival estimate from the target (ms)",
                    "Range (ms)", "Slot clock behind"], rows)
            + "\n\n" + _table(["Class"] + ["In the band, %s" % t for t in prereg.TIMINGS], by_class))


def labels_block(items):
    """Bursts whose leader showed another clientId than at selection (README, leader types)."""
    mine = [it for it in items if it.unit.burst["path"] == "quic"]
    if not mine:
        return NO_RUNS
    rows = []
    for cls in prereg.CLASSES:
        group = [it for it in mine if it.unit.burst["selection_class"] == cls]
        if not group:
            continue
        other = [it for it in group if "client-differs-from-selection" in it.unit.reasons]
        shown = sorted({it.unit.burst.get("leader_client_id") or "none" for it in other})
        rows.append([cls, len(group), len(other), "%.2f" % (len(other) / len(group)), ", ".join(shown) or "-"])
    return _table(["Class at selection", "Bursts", "Leader showed another clientId", "Share", "clientId shown"], rows)


def elsewhere_block(runs):
    """Where delivered probes landed, per path and moment condition and per class of the target
    (README, interaction of probes)."""
    acc, by_class = {}, {}
    for r in runs:
        for sig, p in r.probes.items():
            b = r.bursts.get(p["burst_seq"])
            send = r.sends.get(sig)
            if b is None or send is None or send["result"] not in analyze.DELIVERED:
                continue
            e = acc.setdefault((b["path"], b["timing"]), {"delivered": 0, "window": 0, "same": 0, "other": 0,
                                                           "classes": {}})
            t = by_class.setdefault(b["selection_class"], {"delivered": 0, "window": 0, "same": 0, "other": 0})
            e["delivered"] += 1
            t["delivered"] += 1
            inc = r.inclusions.get(sig)
            if not inc or inc["status"] != "included":
                continue
            if inc["in_target_window"]:
                kind = "window"
            elif inc["actual_leader"] == b["leader"]:
                kind = "same"
            else:
                kind = "other"
                c = inc["actual_leader_class"] or "unknown"
                e["classes"][c] = e["classes"].get(c, 0) + 1
            e[kind] += 1
            t[kind] += 1
    if not acc:
        return NO_RUNS

    def counts(e):
        missing = e["delivered"] - e["window"] - e["same"] - e["other"]
        return [e["delivered"], e["window"], e["same"], e["other"], missing]

    landed = ["Delivered", "In target window", "Same leader, outside the window", "Another leader's block",
              "Not included"]
    rows = [[path, timing] + counts(e) + [", ".join("%s %d" % kv for kv in sorted(e["classes"].items())) or "-"]
            for (path, timing), e in sorted(acc.items())]
    order = list(prereg.CLASSES) + sorted(set(by_class) - set(prereg.CLASSES))
    class_rows = [[cls] + counts(by_class[cls]) for cls in order if cls in by_class]
    return (_table(["Path", "Timing"] + landed + ["Class of the other leaders"], rows)
            + "\n\n" + _table(["Class of the target"] + landed, class_rows))


def latency_block(items):
    """Median one-way latency estimate, half the RTT at the send, per class and leader (plan section 6)."""
    per = {}
    for it in items:
        b = it.unit.burst
        if b["path"] != "quic":
            continue
        end = it.run.ends.get(it.unit.burst_seq) or {}
        rtt = end.get("send_rtt_ns") or b.get("rtt_ns")
        if rtt:
            per.setdefault((b["selection_class"], b["leader"]), []).append(rtt / 2e6)
    if not per:
        return NO_RUNS
    rows = []
    for cls in prereg.CLASSES:
        mine = sorted((leader, v) for (c, leader), v in per.items() if c == cls)
        every = [x for _, v in mine for x in v]
        for leader, v in mine:
            rows.append([cls, "`%s`" % leader, len(v), "%.1f" % _median(v), "%.1f" % _median(every)])
    return _table(["Class", "Leader", "Bursts", "Median one-way estimate (ms)", "Class median (ms)"], rows)


def _load_of(item, field):
    vals = [item.run.slots[s][field] for s in item.slots if s in item.run.slots]
    return sum(vals) / len(vals) if vals else None


def loads_block(items):
    """Tau fee and tau send by quartile of block load, outside the verdict (plan section 7)."""
    kept = _kept(items)
    if not kept:
        return NO_RUNS
    rows = []
    for field, label in (("cost_units", "costUnits"), ("tx_count", "transactions")):
        loaded = sorted(((_load_of(it, field), it.unit.run_id, it.unit.burst_seq, it) for it in kept
                         if _load_of(it, field) is not None), key=lambda x: x[:3])
        n = len(loaded)
        for q in range(4):
            part = [x for i, x in enumerate(loaded) if i * 4 // n == q]
            if not part:
                continue
            group = [x[3] for x in part]
            agave = [it for it in group if it.unit.burst["selection_class"] == "Agave"
                     and it.unit.burst["timing"] == "pre300"]
            rows.append([label, "Q%d" % (q + 1), "%d to %d" % (part[0][0], part[-1][0]), len(group),
                         _tau_text(_pooled(_arms(group, DIFFERENT_FEE), "fee")),
                         _tau_text(_pooled(_arms(group, ("equal_fee",)), "send")),
                         _tau_text(_pooled(_arms(agave, ("equal_fee",)), "send"))])
    return _table(["Load by", "Quartile", "Mean load of the burst's blocks", "Bursts",
                   "tau fee, independent and shared", "tau send, equal fee", "tau send, equal fee, Agave, pre300"],
                  rows)


def first_slot_block(items):
    """Bursts that landed in the window's first slot against the rest (plan section 9)."""
    kept = _kept(items)
    if not kept:
        return NO_RUNS
    rows = []
    for label, first in (("first slot of the window", True), ("later slots", False)):
        def pick(it):
            return [blk for blk, s in zip(it.unit.blocks, it.slots) if (s == it.unit.burst["first_slot"]) == first]
        rows.append([label, _tau_text(_pooled([pick(it) for it in kept if it.unit.burst["arm"] in DIFFERENT_FEE],
                                              "fee")),
                     _tau_text(_pooled([pick(it) for it in kept if it.unit.burst["arm"] in DIFFERENT_FEE], "cross")),
                     _tau_text(_pooled([pick(it) for it in kept if it.unit.burst["arm"] == "equal_fee"], "send"))])
    return _table(["Blocks", "tau fee", "tau cross", "tau send, equal fee"], rows)


def strategy_block(items):
    """HarmonicAgave split by the strategy in the crank memo of the block, outside every Holm family."""
    kept = [it for it in _kept(items) if it.unit.burst["selection_class"] == "HarmonicAgave"]
    if not kept:
        return NO_RUNS
    memos = sorted({(it.run.slots.get(s) or {}).get("crank_memo") or "no memo" for it in kept for s in it.slots})
    rows = []
    for memo in memos:
        def pick(it):
            return [blk for blk, s in zip(it.unit.blocks, it.slots)
                    if ((it.run.slots.get(s) or {}).get("crank_memo") or "no memo") == memo]
        leaders = sorted({it.unit.burst["leader"] for it in kept if pick(it)})
        rows.append([memo, ", ".join("`%s`" % _short(k) for k in leaders),
                     _tau_text(_pooled([pick(it) for it in kept if it.unit.burst["arm"] in DIFFERENT_FEE], "fee")),
                     _tau_text(_pooled([pick(it) for it in kept if it.unit.burst["arm"] in DIFFERENT_FEE], "cross")),
                     _tau_text(_pooled([pick(it) for it in kept if it.unit.burst["arm"] == "equal_fee"], "send"))])
    return _table(["Strategy in the memo", "Leaders", "tau fee", "tau cross", "tau send, equal fee"], rows)


def _cell_mean_fee(group):
    """Equal-weight mean of tau fee over the different-fee cells present (plan section 7)."""
    cells = {}
    for it in group:
        b = it.unit.burst
        if b["arm"] in DIFFERENT_FEE:
            cells.setdefault((b["arm"], b["timing"]), []).append(it.unit.blocks)
    taus = [r[0] for r in (_pooled(v, "fee") for v in cells.values()) if r is not None]
    return (sum(taus) / len(taus), len(taus)) if taus else None


def epochs_block(items):
    """Tau fee per class and epoch, and its spread over rounds, described only (plan section 7)."""
    kept = _kept(items)
    if not kept:
        return NO_RUNS
    epochs = sorted({it.unit.burst["epoch"] for it in kept})
    rows = []
    for cls in prereg.CLASSES:
        mine = [it for it in kept if it.unit.burst["selection_class"] == cls]
        if not mine:
            continue
        row = [cls]
        for ep in epochs:
            m = _cell_mean_fee([it for it in mine if it.unit.burst["epoch"] == ep])
            row.append("-" if m is None else "%.3f (%d cells)" % m)
        rounds = {}
        for it in mine:
            rounds.setdefault((it.unit.burst["epoch"], it.unit.burst["round"]), []).append(it)
        means = [m[0] for m in (_cell_mean_fee(v) for v in rounds.values()) if m is not None]
        row.append("%d rounds, %.3f to %.3f" % (len(means), min(means), max(means)) if means else "-")
        rows.append(row)
    return _table(["Class"] + ["tau fee, epoch %d" % ep for ep in epochs] + ["Round means of tau fee"], rows)


def _priority(tx, cost):
    reward = tx["fee"] - BURNED_SIGNATURE_SHARE * chain.LAMPORTS_PER_SIGNATURE * len(tx["signatures"])
    return reward * 1_000_000 / (cost + 1)


def _requested_cost(tx):
    if tx["cu_limit"] is None:
        return None
    loaded = tx["loaded_data_limit"]
    return chain.agave_cost(len(tx["signatures"]), len(set(tx["write_accounts"])), tx["ix_data_bytes"],
                            tx["cu_limit"], DEFAULT_LOADED_DATA_BYTES if loaded is None else loaded)


def _rank(value, others):
    """Share of the other transactions ranked strictly above value, 0 for the top."""
    return sum(1 for v in others if v > value) / len(others) if others else None


def competition_block(items, data_dir):
    """Each probe's rank among the block's other transactions by client priority
    (plan section 9). Jito tips stay out of the rank; a transaction without a
    compute-unit limit stays out of the rank by requested limits only."""
    kept = _kept(items)
    if not kept:
        return NO_RUNS
    cache = {}

    def block_rows(run, slot):
        key = (run.run["run_id"], slot)
        if key not in cache:
            row = run.slots.get(slot) or {}
            path = os.path.join(data_dir, "runs", run.run["run_id"], row.get("competition_file") or "")
            cache[key] = None
            if row.get("competition_file") and os.path.isfile(path):
                with gzip.open(path, "rt", encoding="utf-8") as f:
                    cache[key] = {t["tx_index"]: t for t in map(json.loads, f) if t.get("kind") == "block_tx"}
        return cache[key]

    acc = {}
    for it in kept:
        for blk, slot in zip(it.unit.blocks, it.slots):
            txs = block_rows(it.run, slot)
            if not txs:
                continue
            ranked = [t for t in txs.values() if not t["jito_tip"]]
            req = {t["tx_index"]: _priority(t, _requested_cost(t)) for t in ranked if _requested_cost(t) is not None}
            used = {t["tx_index"]: _priority(t, t["cost_units"]) for t in ranked if t["cost_units"] is not None}
            n = len(txs)
            e = acc.setdefault(it.unit.burst["selection_class"], {"pos": [], "req": [], "used": [], "tips": 0,
                                                                  "nolimit": 0, "txs": 0})
            e["txs"] += n
            e["tips"] += n - len(ranked)
            e["nolimit"] += len(ranked) - len(req)
            for probe in blk:
                i = probe["pos"]
                e["pos"].append(i / (n - 1) if n > 1 else 0.0)
                if i in req:
                    e["req"].append(_rank(req[i], [v for k, v in req.items() if k != i]))
                if i in used:
                    e["used"].append(_rank(used[i], [v for k, v in used.items() if k != i]))
    if not acc:
        return NO_RUNS
    rows = []
    for cls in prereg.CLASSES:
        e = acc.get(cls)
        if not e:
            continue
        rows.append([cls, len(e["pos"]), "%.2f" % _median(e["pos"]),
                     "%.2f" % _median(e["req"]) if e["req"] else "-",
                     "%.2f" % _median(e["used"]) if e["used"] else "-",
                     "%.1f%%" % (100 * e["tips"] / e["txs"]), "%.1f%%" % (100 * e["nolimit"] / e["txs"])])
    return _table(["Class", "Probes", "Median position (share of block)",
                   "Median rank by requested-limit priority", "Median rank by costUnits priority",
                   "Jito tip transactions", "Transactions without a CU limit"], rows)


def _path_label_p(strata):
    """Two-sided p of the summed RPC-minus-QUIC difference under swaps of path
    labels within each stratum; strata: [(values, k)] with the first k values
    from the RPC path. Exact up to LABEL_TEST_B arrangements, else LABEL_TEST_B
    draws, each stratum's RPC labels taken as the first k of stats.fisher_yates
    on random() (analysis plan line 39). Returns (p, method, smallest p the
    arrangements allow)."""
    options = [list(itertools.combinations(range(len(v)), k)) for v, k in strata]

    def total(choice):
        t = 0.0
        for (values, _), chosen in zip(strata, choice):
            a = [values[i] for i in chosen]
            rest = [values[i] for i in range(len(values)) if i not in chosen]
            t += sum(a) / len(a) - sum(rest) / len(rest)
        return t

    obs = abs(total([tuple(range(k)) for _, k in strata]))
    eps = 1e-12 * max(1.0, obs)
    size = math.prod(len(o) for o in options)
    if size <= prereg.LABEL_TEST_B + 1:
        totals = [abs(total(choice)) for choice in itertools.product(*options)]
        top = max(totals)
        smallest = sum(1 for t in totals if t >= top - 1e-12 * max(1.0, top)) / size
        return sum(1 for t in totals if t >= obs - eps) / size, "exact over %d" % size, smallest
    rnd = random.Random(prereg.LABEL_TEST_SEED)

    def draw():
        return [tuple(sorted(stats.fisher_yates(list(range(len(v))), rnd)[:k])) for v, k in strata]

    hits = sum(1 for _ in range(prereg.LABEL_TEST_B) if abs(total(draw())) >= obs - eps)
    p = (hits + 1) / (prereg.LABEL_TEST_B + 1)
    return p, _drawn(p, prereg.LABEL_TEST_B), 1 / (prereg.LABEL_TEST_B + 1)


# Exclusion reasons a burst may carry and still enter each control-path measure (campaign
# addendum section 9). The inclusion share keeps a burst with fewer than two probes in one
# block of the window, since leaving it out would select on the outcome; tau fee needs two.
CONTROL_KEEPS = {"tau fee": {"control-path"}, "inclusion share": {"control-path", "fewer-than-two-in-a-block"}}


def control_block(items):
    """Control path against the direct path within leader and epoch, in the same arm and moment
    condition (analysis plan section 9, campaign addendum section 9). A measure whose label test cannot
    reach p <= ALPHA even at its most extreme arrangement is descriptive and prints no p."""
    allowed = CONTROL_KEEPS
    value_of = {"tau fee": lambda it: verdict.burst_tau(it.unit.blocks, "fee"), "inclusion share": _window_share}
    usable = [it for it in items if set(it.unit.reasons) <= allowed["inclusion share"]]
    measures = {}
    for name in ("tau fee", "inclusion share"):
        per = {}
        for it in usable:
            if set(it.unit.reasons) <= allowed[name]:
                b = it.unit.burst
                per.setdefault((b["leader"], b["epoch"], b["arm"], b["timing"]), []).append(it)
        for group in per.values():
            vals = [(value_of[name](it), it.unit.burst["path"] == "rpc") for it in group]
            vals = [(v, r) for v, r in vals if v is not None]
            k = sum(1 for _, r in vals if r)
            if 0 < k < len(vals):
                ordered = [v for v, r in vals if r] + [v for v, r in vals if not r]
                measures.setdefault(name, []).append((ordered, k))
    if not measures:
        return "No control-path bursts in this stage."
    rows = []
    for name, strata in sorted(measures.items()):
        diff = sum(sum(v[:k]) / k - sum(v[k:]) / (len(v) - k) for v, k in strata) / len(strata)
        p, method, smallest = _path_label_p(strata)
        if smallest > stats.ALPHA:
            rows.append([name, len(strata), "%.3f" % diff, "-",
                         "descriptive: smallest attainable p %s, %s" % (_p(smallest), method)])
        else:
            rows.append([name, len(strata), "%.3f" % diff, _p(p), method])
    latency = {}
    for it in usable:
        for inc in it.run.inclusions.values():
            if inc["burst_seq"] == it.unit.burst_seq and inc["status"] == "included" and inc["slot"] is not None:
                latency.setdefault(it.unit.burst["path"], []).append(inc["slot"] - it.unit.burst["first_slot"])
    lat = "; ".join("%s median %s slots after the window's first slot (%d probes)" % (
        path, _median(v), len(v)) for path, v in sorted(latency.items()))
    return (_table(["Measure", "Strata (leader, epoch, arm, condition)", "Mean RPC minus QUIC", "p", "Label test"], rows)
            + "\n\nPath latency: " + (lat or "-") + ".")


def _window_share(item):
    run, seq = item.run, item.unit.burst_seq
    delivered = hits = 0
    for sig, p in run.probes.items():
        if p["burst_seq"] != seq:
            continue
        send = run.sends.get(sig)
        if send is None or send["result"] not in analyze.DELIVERED:
            continue
        delivered += 1
        inc = run.inclusions.get(sig)
        hits += bool(inc and inc["status"] == "included" and inc["in_target_window"])
    return hits / delivered if delivered else None


def _count_cells(node, acc):
    if isinstance(node, dict):
        if {"class", "arm", "timing"} <= set(node) and node.get("path", "quic") == "quic":
            key = (node["class"], node["arm"], node["timing"])
            acc[key] = acc.get(key, 0) + 1
            return
        for v in node.values():
            _count_cells(v, acc)
    elif isinstance(node, list):
        for v in node:
            _count_cells(v, acc)


def minimum_block(repo_dir):
    """Minimum bursts per class and cell from the pilot against the campaign table (plan section 5)."""
    path = os.path.join(repo_dir, "prereg", "campaign-minimum.json")
    table_path = os.path.join(repo_dir, "prereg", "campaign-table.json")
    if not os.path.exists(path):
        return "No minimum yet."
    with open(path, encoding="utf-8") as f:
        m = json.load(f)
    planned = {}
    if os.path.exists(table_path):
        with open(table_path, encoding="utf-8") as f:
            _count_cells(json.load(f), planned)
    rows = []
    for s in m["slots"]:
        counts = [n for (cls, arm, timing), n in planned.items() if arm == s["arm"]]
        least = min(counts) if counts else None
        raw = "; ".join("%s %.3f (%d bursts)" % (t, c["raw_variance"], c["bursts"])
                        for t, c in sorted(s["cells"].items()))
        rows.append([s["arm"], s["tau"], s["bursts"], "%.3f" % s["sigma"], raw, s["min_bursts"],
                     "-" if least is None else least,
                     "-" if least is None else ("yes" if least >= s["min_bursts"] else "no")])
    return (_table(["Arm", "tau", "Pilot bursts", "sigma (residual)", "Raw variance by cell", "Minimum bursts",
                    "Campaign bursts per class and cell", "Equivalence reachable at the pilot's spread"], rows)
            + "\n\nFrom %d pilot bursts, %d kept; alpha_e %.6f, power per tau %.2f, delta %.2f." % (
                m["pilot_bursts"], m["kept"], m["alpha_e"], m["power_per_tau"], m["delta_class"]))


def tick_runs_block(runs):
    """Share of slots with a tick of each known signer, by run and by the class of the slot's
    leader (analysis plan line 88)."""
    rows = []
    for r in live(runs):
        cls_of = {i["slot"]: i["actual_leader_class"] for i in _included(r)}
        counts = {}  # class: [slots, with a BAM tick, with a Harmonic tick]
        for slot, row in r.slots.items():
            cls = cls_of.get(slot)
            if cls is None:
                continue
            signers = {t["signer"] for t in row.get("ticks") or []}
            c = counts.setdefault(cls, [0, 0, 0])
            c[0] += 1
            c[1] += BAM_SIGNER in signers
            c[2] += HARMONIC_SIGNER in signers
        order = list(prereg.CLASSES)
        for cls in sorted(counts, key=lambda x: (order.index(x) if x in order else len(order), x)):
            n, bam, harmonic = counts[cls]
            rows.append(["`%s`" % r.run["run_id"], cls, EXPECTED_SIGNER.get(cls) and (
                "BAM" if EXPECTED_SIGNER[cls] == BAM_SIGNER else "Harmonic") or "none", n,
                "%d (%.1f%%)" % (bam, 100.0 * bam / n), "%d (%.1f%%)" % (harmonic, 100.0 * harmonic / n)])
    return _table(["Run", "Class of the slot's leader", "Its builder", "Slots", "With a BAM tick",
                   "With a Harmonic tick"], rows)


def tick_epoch_block(repo_dir):
    root = os.path.join(repo_dir, "research", "tick-scale")
    found = sorted(f for f in os.listdir(root) if f.startswith("summary-e") and f.endswith(".json")) \
        if os.path.isdir(root) else []
    if not found:
        return "No epoch sample yet."
    out = []
    for name in found:
        with open(os.path.join(root, name), encoding="utf-8") as f:
            s = json.load(f)

        def cell(x):
            return "-" if not x["n"] else "%d (%.1f%%; %.1f to %.1f)" % (x["k"], x["pct"], x["ci95"][0], x["ci95"][1])

        rows = [[cls, c["population_slots"], c["blocks"], c["leaders_in_blocks"], c["skipped"] + c["empty"],
                 cell(c["bam_tick"]), cell(c["harmonic_tick"]), cell(c["no_tick"])]
                for cls, c in s["classes"].items()]
        out.append("Epoch %d, %d slots per class drawn with seed %d, classes by gossip at %s (`research/tick-scale/%s`):"
                   % (s["epoch"], s["per_class"], s["seed"], s["gossip_utc"][:19].replace("T", " "), name))
        out.append(_table(["Class", "Slots in epoch", "Blocks read", "Leaders read", "Skipped or empty",
                           "BAM tick (95% CI)", "Harmonic tick (95% CI)", "No tick (95% CI)"], rows))
    return "\n\n".join(out)


def wrong_block(runs, data_dir, logs_dir):
    rows = []
    later = analyze.later_copies(live(runs))
    for r in live(runs):
        planned = sum(len(row["windows"]) for row in _rounds(os.path.join(data_dir, "runs", r.run["run_id"])))
        skipped, failed = {}, 0
        path = os.path.join(logs_dir, r.run["run_id"] + ".jsonl")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                for line in f:
                    e = json.loads(line)
                    if e.get("event") == "burst_skipped":
                        reason = ((e.get("data") or {}).get("reason") or "").split(":")[0].split(" (")[0]
                        reason = "slot clock behind" if reason.startswith("slot clock") else reason
                        skipped[reason] = skipped.get(reason, 0) + 1
                    elif e.get("event") == "burst_failed":
                        failed += 1
        excluded = {}
        for u in analyze.units_of(r, later):
            for reason in u.reasons:
                excluded[reason] = excluded.get(reason, 0) + 1
        rows.append(["`%s`" % r.run["run_id"], planned, len(r.bursts),
                     ", ".join("%s %d" % kv for kv in sorted(skipped.items())) or "none", failed,
                     ", ".join("%s %d" % kv for kv in sorted(excluded.items())) or "none"])
    return _table(["Run", "Windows planned", "Bursts written", "Skipped before sending", "Failed",
                   "Left out of the order tests"], rows)


def _rounds(run_dir):
    """Round rows of a run; analyze.Run leaves them out."""
    return [row for _, row in rawformat.read_jsonl(os.path.join(run_dir, "probes.jsonl"))
            if row.get("kind") == "round"]


def blocks(data_dir, repo_dir):
    """{name: markdown} of every generated block."""
    runs = analyze.load_runs(data_dir)
    anchors_path = os.path.join(data_dir, "prereg-anchors.json")
    anchors = []
    if os.path.exists(anchors_path):
        with open(anchors_path, encoding="utf-8") as f:
            anchors = json.load(f)
    logs_dir = os.path.join(repo_dir, "logs")
    out = {"runs": runs_block(runs), "spend": spend_block(runs, anchors, logs_dir), "panel": panel_block(runs),
           "bursts": bursts_block(runs), "neighbours": neighbours_block(data_dir), "tick-runs": tick_runs_block(runs),
           "tick-epoch": tick_epoch_block(repo_dir), "minimum": minimum_block(repo_dir),
           "what-went-wrong": wrong_block(runs, data_dir, logs_dir)}
    for stage in STAGES:
        chosen = _stage_runs(runs, stage)
        result = analyze.analyze(chosen, (stage,)) if chosen else None
        items = _items(chosen)
        out[stage + "-exclusions"] = exclusions_block(result)
        out[stage + "-cells"] = cells_block(result)
        out[stage + "-inclusion"] = inclusion_block(result)
        out[stage + "-rounds"] = rounds_block(result)
        out[stage + "-pairs"] = pairs_block(result)
        out[stage + "-hypotheses"] = hypotheses_block(result)
        out[stage + "-timing"] = timing_block(items)
        out[stage + "-labels"] = labels_block(items)
        out[stage + "-elsewhere"] = elsewhere_block(chosen)
        out[stage + "-latency"] = latency_block(items)
        out[stage + "-loads"] = loads_block(items)
        out[stage + "-first-slot"] = first_slot_block(items)
        out[stage + "-strategy"] = strategy_block(items)
        out[stage + "-epochs"] = epochs_block(items)
        out[stage + "-competition"] = competition_block(items, data_dir)
        out[stage + "-control"] = control_block(items) if chosen else NO_RUNS
    return out


def split(text):
    """[(name or None, lines)]: prose pieces and generated blocks in file order."""
    pieces, prose, lines = [], [], text.split("\n")
    i = 0
    while i < len(lines):
        m = BEGIN.match(lines[i])
        if not m:
            prose.append(lines[i])
            i += 1
            continue
        name = m.group(1)
        try:
            j = lines.index(END % name, i + 1)
        except ValueError:
            raise ValueError("REPORT: block %s has no end line" % name)
        pieces.append((None, prose + [lines[i]]))
        pieces.append((name, lines[i + 1:j]))
        prose = [lines[j]]
        i = j + 1
    pieces.append((None, prose))
    return pieces


def fill(text, generated):
    """text with every generated block rewritten; (new text, names that changed)."""
    out, changed = [], []
    for name, lines in split(text):
        if name is None:
            out.extend(lines)
            continue
        if name not in generated:
            raise ValueError("REPORT: unknown block %s" % name)
        body = generated[name].split("\n")
        if lines != body:
            changed.append(name)
        out.extend(body)
    return "\n".join(out), changed
