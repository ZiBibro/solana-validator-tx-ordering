"""Selftest: checks with known answers that run before verify (section 9).

Each check returns (name, ok, detail). A failed check stops reproduce before
verify starts.
"""

import argparse
import contextlib
import copy
import gzip
import http.client
import io
import itertools
import json
import math
import os
import random
import tempfile
import types
from fractions import Fraction

from . import (analyze, b58, campaign, chain, channel, collect, fakechain, panel, pilot, plan, prereg, rawformat,
               report, rpc, stats, synth, verdict, verify)


def sample_run(burst_seq=7, n=12):
    """A valid probes.jsonl of one burst, built from the format rules."""
    run = synth.run_row("selftest")
    fees = [0, 10, 100, 1000] * 3
    probes = [{"send_rank": r, "fee": fees[r], "cu_limit": 1000} for r in range(n)]
    return [run] + synth.burst_rows(run, burst_seq, probes)


def _version3(rows):
    """The same burst as a version 3 run: the probe's leader correction in burst and
    burst_end, and the first shreds from the final anchor to slot 2 in burst_end."""
    out = copy.deepcopy(rows)
    for r in out:
        r["v"] = 3
        if r["kind"] == "burst":
            r.update({"leader_correction_ns": 80_000_000, "leader_correction_n": 12})
        elif r["kind"] == "burst_end":
            r.update({"leader_correction_ns": 80_000_000, "leader_correction_n": 12,
                      "shreds_from_slot": r["send_anchor_slot"], "shreds_node_ns": [1, None, 3]})
    return out


def _mutations(rows):
    """Single-change variants that a correct checker must reject."""
    first_probe = next(i for i, r in enumerate(rows) if r["kind"] == "probe")
    first_send = next(i for i, r in enumerate(rows) if r["kind"] == "send")

    def edit(fn):
        m = copy.deepcopy(rows)
        fn(m)
        return m

    def swap_send_before_probe(m):
        m.insert(first_probe, m.pop(first_send))

    return [
        ("transfer amount off by one",
         edit(lambda m: m[first_probe].__setitem__("transfer_lamports",
                                                   m[first_probe]["transfer_lamports"] + 1))),
        ("send rank repeated", edit(lambda m: m[first_probe + 1].__setitem__("send_rank", 0))),
        ("payer repeated", edit(lambda m: m[first_probe + 1].__setitem__("payer_index", 1))),
        ("send row before its probe row", edit(swap_send_before_probe)),
        ("unknown field", edit(lambda m: m[1].__setitem__("leader_clientid", "Agave"))),
        ("missing field", edit(lambda m: m[1].pop("blockhash"))),
        ("bad signature", edit(lambda m: m[first_probe].__setitem__("signature", "0OIl"))),
        ("null where not allowed", edit(lambda m: m[first_probe].__setitem__("cu_limit", None))),
        ("bool where int expected", edit(lambda m: m[first_probe].__setitem__("cu_limit", True))),
        ("rank out of range", edit(lambda m: m[first_probe].__setitem__("send_rank", 12))),
        ("first row is not run", edit(lambda m: m.pop(0))),
        ("schema version from the future",
         edit(lambda m: m[1].__setitem__("v", rawformat.load_schema()["version"] + 1))),
        ("version 2 field missing", edit(lambda m: m[1].pop("clock_lag_slots"))),
        ("version 2 field on a version 1 row", edit(lambda m: m[1].__setitem__("v", 1))),
        ("RPC URL with an API key in the query",
         edit(lambda m: m[0].__setitem__("rpc_url", "https://rpc.example.com/?api-key=abc"))),
        ("RPC URL with a token in the path",
         edit(lambda m: m[0].__setitem__("rpc_url", "https://x.example.com/0123abcd/"))),
        ("WS URL with userinfo",
         edit(lambda m: m[0].__setitem__("ws_url", "wss://user:pass@rpc.example.com"))),
    ]


def _write(path, rows):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def raw_format_checks():
    schema = rawformat.load_schema()
    out = []
    rows = sample_run()
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "probes.jsonl")
        _write(path, rows)
        n, problems = rawformat.check_probe_file(path, schema)
        out.append(("raw format: valid burst passes", n == len(rows) and not problems,
                    "%d rows, %d problems %s" % (n, len(problems), problems[:3])))
        v3 = _version3(rows)
        _write(path, v3)
        n, problems = rawformat.check_probe_file(path, schema)
        out.append(("raw format: version 3 burst passes", n == len(v3) and not problems,
                    "%d rows, %d problems %s" % (n, len(problems), problems[:3])))
        end = next(i for i, r in enumerate(v3) if r["kind"] == "burst_end")
        v3_muts = [
            ("version 3 field missing", [dict(r) for r in v3]),
            ("version 3 field on a version 2 row", [dict(r) for r in v3]),
        ]
        v3_muts[0][1][end].pop("shreds_node_ns")
        v3_muts[1][1][end]["v"] = 2
        for name, mrows in v3_muts:
            _write(path, mrows)
            _, problems = rawformat.check_probe_file(path, schema)
            out.append(("raw format rejects: " + name, bool(problems),
                        problems[0] if problems else "accepted"))
        muts = _mutations(rows)
        out.append(("raw format: mutation set is not empty", len(muts) > 0, "%d mutations" % len(muts)))
        for name, mrows in muts:
            _write(path, mrows)
            _, problems = rawformat.check_probe_file(path, schema)
            out.append(("raw format rejects: " + name, bool(problems),
                        problems[0] if problems else "accepted"))
        _write(path, [])
        _, problems = rawformat.check_probe_file(path, schema)
        out.append(("raw format rejects: empty file", bool(problems),
                    problems[0] if problems else "accepted"))
    for value in (b"", b"\0\0\x01", bytes(range(32)), b"\xff" * 64):
        ok = b58.decode(b58.encode(value)) == value
        out.append(("base58 round trip of %d bytes" % len(value), ok, ""))
    return out


def _brute_ties(x):
    """S of every distinct arrangement of the multiset x against positions 0..n-1."""
    out = {}
    for perm in set(itertools.permutations(x)):
        s = stats.pair_s(perm, list(range(len(perm))))
        out[s] = out.get(s, 0) + 1
    return out


def _brute_cross(fee):
    n = len(fee)
    out = {}
    for send in itertools.permutations(range(n)):
        s = 0
        for i in range(n):
            for j in range(i + 1, n):
                if fee[i] != fee[j]:
                    s += stats._sign(send[j] - send[i])
        out[s] = out.get(s, 0) + 1
    return out


def _close(a, b, tol):
    return abs(a - b) <= tol


def stats_checks():
    out = []
    for x in ([0, 0, 1, 1, 2, 2], [0, 1, 2, 3, 4, 5]):
        exact = stats.null_ties(x)
        brute = _brute_ties(x)
        out.append(("exact null equals full enumeration, ties %s" % _sizes(x), exact == brute,
                    "%d arrangements" % sum(brute.values())))
    for lay, var in (("AABB", Fraction(20, 3)), ("ABAB", Fraction(4))):
        exact = stats.null_cross(lay)
        brute = _brute_cross(lay)
        v = stats.moments(exact)[1]
        out.append(("cross null %s equals full enumeration, Var S = %s" % (lay, var),
                    exact == brute and v == var, "Var %s, %d orders" % (v, sum(brute.values()))))
    exact = stats.null_cross("AABBCC")
    out.append(("cross null AABBCC equals full enumeration", exact == _brute_cross("AABBCC"),
                "%d orders" % sum(exact.values())))
    rnd = random.Random("itb-selftest:layout")
    layouts = [("sorted", "AAABBBCCCDDD", Fraction(198)), ("alternating", "ABCDABCDABCD", Fraction(134)),
               ("seeded", "".join(stats.fisher_yates(list("AAABBBCCCDDD"), rnd)), None)]
    for name, lay, var in layouts:
        d = stats.null_cross(lay)
        v = stats.moments(d)[1]
        analytic = stats.cross_variance_analytic(lay)
        ok = v == analytic and (var is None or v == var) and sum(d.values()) == math.factorial(12)
        out.append(("cross null of 12 probes, %s %s: Var S equals analytic" % (name, lay), ok,
                    "Var %s, analytic %s" % (v, analytic)))
    for lay, want in (("AAABBBCCCDDD", 0.01834), ("ABCDABCDABCD", 0.004644)):
        d = stats.null_cross(lay)
        tail = float(Fraction(sum(c for s, c in d.items() if s >= 30), sum(d.values())))
        out.append(("P(S_cross >= 30) of %s is %s" % (lay, want), _close(tail, want, 5e-6), "%.6f" % tail))
    for df, want in ((3, 3.182446), (7, 2.364624), (31, 2.039513)):
        q = stats.t_quantile(0.975, df)
        out.append(("Student t quantile 0.975 at df %d" % df, _close(q, want, 1e-6), "%.6f" % q))
    rej = stats.holm([0.01, 0.04, 0.03, 0.005], Fraction(5, 100))
    out.append(("Holm step-down stops at the first failure", rej == [True, False, False, True], str(rej)))
    p, method, _ = stats.paired_label_test([1.0, 1.0, 1.0])
    out.append(("label test, 3 strata, exact p = 1/4", p == Fraction(1, 4) and method == "exact", str(p)))
    p, method, b = stats.paired_label_test([1.0] * 21, seed="itb-selftest:labels")
    out.append(("label test, 21 strata, Monte Carlo floor 1/(B+1)",
                method == "monte-carlo" and b == 19999 and p == Fraction(1, 20000), "%s, B %d" % (p, b)))
    return out


def _sizes(x):
    counts = {}
    for v in x:
        counts[v] = counts.get(v, 0) + 1
    return sorted(counts.values())


def min_p_checks():
    """Smallest attainable p of each test against the first Holm threshold of its family."""
    out = []
    a_v = float(stats.ALPHA) / verdict.VERDICT_FAMILY_M
    a_p = float(stats.ALPHA) / verdict.PAIR_FAMILY_M
    # Campaign floor: 2 leaders per class, each with 2 bursts per cell without doubling.
    b_cell = 4
    keys = {
        "fee": ("sizes", (3, 3, 3, 3)),
        "send": ("sizes", (1,) * 12),
        "limit": ("sizes", (6, 6)),
    }
    for name, key in keys.items():
        one = float(verdict.min_attainable_p([key]))
        cell = float(verdict.min_attainable_p([key] * b_cell))
        out.append(("min p of tau %s over %d bursts below %.6f" % (name, b_cell, a_v), cell < a_v,
                    "%.3g over %d, %.3g over 1 burst" % (cell, b_cell, one)))
    worst = 0.0
    for lay in ("AAABBBCCCDDD", "ABCDABCDABCD", "AABBCCDDABCD"):
        worst = max(worst, float(verdict.min_attainable_p([("cross", verdict._pattern(lay))])))
    out.append(("min p of tau cross over 1 burst, worst layout, below %.6f" % a_v, worst < a_v,
                "%.3g" % worst))
    for strata, need in ((16, True), (8, False)):
        p = 2.0 / (1 << strata)
        out.append(("min p of the pair test with %d strata %s %.6f" % (strata, "below" if need else "above", a_p),
                    (p < a_p) == need, "%.3g" % p))
    out.append(("min p of the Monte Carlo label test below %.6f" % a_p, 1.0 / 20000 < a_p, "%.3g" % (1.0 / 20000)))
    return out


RULE_SETS = (
    # (name, rule, arm, expected form, expected detail or None for any, burst counts)
    ("Agave exact priority", "agave", "independent", "fee-rule", None, (4, 32)),
    ("Agave exact priority, shared arm", "agave", "shared", "fee-rule", None, (4, 32)),
    ("Firedancer exact priority", "firedancer", "independent", "fee-rule", "ties-reverse-arrival", (4, 32)),
    ("Firedancer equal fee, reverse arrival", "firedancer", "equal_fee", "arrival-rule", "reverse", (4, 32)),
    ("pure FIFO", "fifo", "independent", "arrival-rule", "forward", (4, 32)),
    ("inverted fee rule", "inverted", "independent", "inverted-fee", None, (4, 32)),
    # Fee and arrival compete for the same 54 pairs, so even the most even mix
    # gives each tau a z near 4 on 4 bursts, at the first Holm threshold; over
    # 40 seeds 26.10.2026 the mix read as mixed in 0 to 18 cases on 4 bursts
    # and in 15 of 15 on 32. Section 9 does not list this set; it runs on 32.
    ("mixed fee and arrival", "mixed", "independent", "mixed-rule", None, (32,)),
    ("Agave priority, denominator arm", "agave", "denominator", "divides", None, (4, 32)),
)
RULE_FORMS = ("fee-rule", "arrival-rule", "mixed-rule", "inverted-fee", "divides", "inverted")
RANDOM_ARMS = (("independent", "no-rule-visible"), ("equal_fee", "no-rule-visible"),
               ("denominator", "does-not-divide"))


def _null_sigma(arm):
    """Largest one-burst sd of a verdict tau of the arm under the null; the
    minimum formula gets this in place of the pilot variance."""
    pieces = {
        "fee": (("sizes", (3, 3, 3, 3)), math.sqrt(54 * 66)),
        "cross": (("cross", (0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3)), 54),
        "send": (("sizes", (1,) * 12), 66),
        "limit": (("sizes", (6, 6)), math.sqrt(36 * 66)),
    }
    sds = []
    for name in verdict.VERDICT_SLOTS[arm]:
        key, d = pieces[name]
        sds.append(math.sqrt(stats.moments(verdict.null_of(key))[1]) / d)
    return max(sds)


def synthetic_checks():
    out = []
    for name, rule, arm, form, detail, counts in RULE_SETS:
        for b in counts:
            bursts = synth.cell(rule, arm, b, "itb-selftest:%s:%s:%d" % (rule, arm, b))
            got = verdict.cell_form_at_first_threshold(arm, verdict.cell_results(bursts))
            ok = got[0] == form and (detail is None or got[1] == detail)
            out.append(("synthetic %s, %d bursts: %s" % (name, b, form), ok, "%s %s" % got))
    for arm, want in RANDOM_ARMS:
        for b in (4, 32):
            bursts = synth.cell("random", arm, b, "itb-selftest:random:%s:%d" % (arm, b))
            got = verdict.cell_form_at_first_threshold(arm, verdict.cell_results(bursts))
            out.append(("synthetic random order, %s, %d bursts: no rule form" % (arm, b),
                        got[0] not in RULE_FORMS, "%s %s" % got))
        sigma = _null_sigma(arm)
        b_min = verdict.min_bursts_formula(sigma)
        bursts = synth.cell("random", arm, b_min, "itb-selftest:random:%s:min" % arm)
        got = verdict.cell_form_at_first_threshold(arm, verdict.cell_results(bursts))
        out.append(("synthetic random order, %s, %d bursts from the minimum formula: %s" % (arm, b_min, want),
                    got[0] == want, "%s %s, sigma %.4f" % (got[0], got[1], sigma)))
    return out


def end_to_end_checks():
    """A synthetic run written in the raw format of section 8 and read back by analyze.

    FireBAM bursts follow pure FIFO, Firedancer bursts the exact Firedancer rule,
    8 rounds in both different-fee arms give 16 pair strata; one more burst has a
    leader that reported another client at the burst moment and must drop out.
    """
    out = []
    plan = []
    for rnd in range(8):
        for arm in ("independent", "shared"):
            plan.append({"class": "FireBAM", "rule": "fifo", "arm": arm, "timing": "pre300", "round": rnd})
            plan.append({"class": "Firedancer", "rule": "firedancer", "arm": arm, "timing": "pre300",
                         "round": rnd, "leader": 1})
    plan.append({"class": "Firedancer", "rule": "firedancer", "arm": "independent", "timing": "pre300",
                 "round": 8, "fields": {"leader_client_id": "Frankendancer"}})
    plan.append({"class": "FireBAM", "rule": "fifo", "arm": "independent", "timing": "pre300",
                 "round": 9, "fields": {"http_slot": 461999996, "clock_lag_slots": 2}})
    schema = rawformat.load_schema()
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = os.path.join(tmp, "runs", "selftest-e2e")
        os.makedirs(run_dir)
        prows, crows = synth.campaign_rows("selftest-e2e", plan, "itb-selftest:e2e")
        _write(os.path.join(run_dir, "probes.jsonl"), prows)
        _write(os.path.join(run_dir, "collect.jsonl"), crows)
        _, p1 = rawformat.check_probe_file(os.path.join(run_dir, "probes.jsonl"), schema)
        _, p2 = rawformat.check_rows_file(os.path.join(run_dir, "collect.jsonl"), schema)
        out.append(("end to end: synthetic raw files pass the format checks", not p1 and not p2,
                    "%d probe rows, %d collect rows %s" % (len(prows), len(crows), (p1 + p2)[:2])))
        result = analyze.analyze(analyze.load_runs(tmp), stages=("test",))
    out.append(("end to end: the bursts with another client and with a late clock drop out",
                result["excluded"] == {"client-differs-from-selection": 1, "slot-clock-behind": 1}
                and result["kept"] == len(plan) - 2,
                "kept %d, excluded %s" % (result["kept"], result["excluded"])))
    forms = {(c["class"], c["arm"]): (c["form"], c["detail"]) for c in result["cells"]}
    for cls, want in (("FireBAM", ("arrival-rule", "forward")),
                      ("Firedancer", ("fee-rule", "ties-reverse-arrival"))):
        for arm in ("independent", "shared"):
            got = forms.get((cls, arm))
            out.append(("end to end: %s %s arm reads %s" % (cls, arm, " ".join(want)), got == want, str(got)))
    pairs = {(r["timing"], r["tau"]): r for r in result["pairs"]
             if r["pair"] == ["FireBAM", "Firedancer"] and r["strata"]}
    for name in ("fee", "cross"):
        r = pairs.get(("pre300", name))
        ok = r is not None and r["strata"] == 16 and r["form"] == "builder-changes-order"
        out.append(("end to end: pair FireBAM vs Firedancer, tau %s, 16 strata: builder changes order" % name,
                    ok, "%s strata, p %s, %s" % ((r or {}).get("strata"), (r or {}).get("p"), (r or {}).get("form"))))
    return out


def _quiet(_line):
    pass


def _edit_rows(path, change):
    rows = [row for _, row in rawformat.read_jsonl(path)]
    _write(path, change(rows))


def _first(rows, kind, **match):
    return next(r for r in rows if r["kind"] == kind and all(r[k] == v for k, v in match.items()))


def _move_position(rows):
    inc = _first(rows, "inclusion", status="included")
    inc["tx_index"] += 1
    return rows


def _raise_fee(rows):
    _first(rows, "probe")["priority_fee_lamports"] += 1
    return rows


def _swap_ranks(rows):
    a, b = [r for r in rows if r["kind"] == "probe" and r["burst_seq"] == 0][:2]
    a["send_rank"], b["send_rank"] = b["send_rank"], a["send_rank"]
    return rows


def _edit_tick(rows):
    row = next(r for r in rows if r["kind"] == "slot" and r["ticks"])
    row["ticks"][0]["timestamp_ns"] += 1
    return rows


def _swap_leader(rows):
    _first(rows, "slot")["leader"] = synth.key(5, 9)
    return rows


def _drop_probe(run_dir):
    """Removes one included probe from both raw files: only the chain still has it."""
    collect_path = os.path.join(run_dir, "collect.jsonl")
    crows = [row for _, row in rawformat.read_jsonl(collect_path)]
    gone = _first(crows, "inclusion", status="included")["signature"]
    _write(collect_path, [r for r in crows if r.get("signature") != gone])
    _edit_rows(os.path.join(run_dir, "probes.jsonl"),
               lambda rows: [r for r in rows if r.get("signature") != gone])


CHAIN_MUTATIONS = (
    ("a recorded position moved by one", "collect.jsonl", _move_position, False),
    ("a raw priority fee raised by 1 lamport", "probes.jsonl", _raise_fee, False),
    ("two raw send ranks swapped", "probes.jsonl", _swap_ranks, False),
    ("a tick timestamp edited", "collect.jsonl", _edit_tick, False),
    ("a slot leader replaced", "collect.jsonl", _swap_leader, False),
    ("one probe dropped from the raw data", None, _drop_probe, False),
    ("probe costs differing inside a burst", None, None, True),
)


def _fake_world(tmp, tamper_cost=False):
    run_dir = os.path.join(tmp, "runs", "fake-live")
    world, truth = fakechain.build_world(run_dir, "itb-selftest:chain", tamper_cost)
    collect.collect_run(run_dir, world, checked_utc="2026-10-26T22:00:00Z", out=_quiet)
    return run_dir, world, truth


def chain_checks():
    """collect and verify against the in-memory chain of fakechain (section 9):
    three live bursts, one probe expired, one landed with the next leader."""
    out = []
    schema = rawformat.load_schema()
    with tempfile.TemporaryDirectory() as tmp:
        run_dir, world, truth = _fake_world(tmp)
        run = analyze.load_run(run_dir)
        wrong = 0
        for sig, want in truth.items():
            inc = run.inclusions[sig]
            got = (inc["status"], inc["slot"], inc["tx_index"], inc["in_target_window"],
                   inc["tick_segment"])
            wrong += got[:len(want)] != want
        segments = {w[4] for w in truth.values() if len(w) > 1}
        out.append(("chain: collect recovers status, slot, position, window and tick segment",
                    len(truth) == 36 and wrong == 0 and {0, 1, 2} <= segments,
                    "%d probes, %d wrong, segments %s" % (len(truth), wrong, sorted(segments, key=str))))
        _, problems = rawformat.check_rows_file(os.path.join(run_dir, "collect.jsonl"), schema)
        competition = 0
        for name in sorted(os.listdir(os.path.join(run_dir, "blocks"))):
            with gzip.open(os.path.join(run_dir, "blocks", name), "rt", encoding="utf-8") as f:
                for line in f:
                    competition += 1
                    problems += rawformat.validate_row(json.loads(line), schema)
        out.append(("chain: collect rows and competition files pass the format checks",
                    not problems and competition > 0,
                    "%d competition rows %s" % (competition, problems[:2])))
        calls = [params for method, params in world.calls if method in ("getBlock", "getTransaction")]
        typed = [type(p[1].get("maxSupportedTransactionVersion")) is int
                 and p[1]["maxSupportedTransactionVersion"] == 1 for p in calls]
        out.append(("chain: every getBlock and getTransaction asks for version 1 as an integer",
                    bool(typed) and all(typed), "%d calls" % len(typed)))
        report = verify.verify([run], world, tmp, tmp, out=_quiet)
        out.append(("chain: verify finds no problem in the untouched world",
                    not report.problems and len(report.notes) == 3,
                    "%d problems, %d notes %s" % (len(report.problems), len(report.notes),
                                                  report.problems[:1])))
    for value in (None, True):
        saved = rpc.MAX_TX_VERSION
        rpc.MAX_TX_VERSION = value
        try:
            with tempfile.TemporaryDirectory() as tmp:
                _fake_world(tmp)
            refused = None
        except rpc.RpcError as e:
            refused = e.code
        finally:
            rpc.MAX_TX_VERSION = saved
        out.append(("chain mutation: maxSupportedTransactionVersion %r is refused with -32015" % value,
                    refused == -32015, "code %s" % refused))
    for name, target, change, tamper in CHAIN_MUTATIONS:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir, world, _ = _fake_world(tmp, tamper)
            if target:
                _edit_rows(os.path.join(run_dir, target), change)
            elif change:
                change(run_dir)
            report = verify.verify([analyze.load_run(run_dir)], world, tmp, tmp, out=_quiet)
        out.append(("chain mutation: %s fails verify" % name, bool(report.problems),
                    report.problems[0][:90] if report.problems else "no problem found"))
    return out


def _collect_with(tmp, change):
    """Collect the fakechain world after change(world, landed), where landed is
    the (signature, slot) of one included probe. Returns (inclusions or the
    RpcError collect raised, world, landed, probes)."""
    run_dir = os.path.join(tmp, "runs", "fake-live")
    world, truth = fakechain.build_world(run_dir, "itb-selftest:chain")
    sig = sorted(s for s, w in truth.items() if w[0] == "included")[0]
    landed = (sig, truth[sig][1])
    change(world, landed)
    try:
        collect.collect_run(run_dir, world, checked_utc="2026-10-26T22:00:00Z", out=_quiet)
    except rpc.RpcError as e:
        return e, world, landed, None
    run = analyze.load_run(run_dir)
    return run.inclusions, world, landed, run.probes


def collect_checks():
    """collect takes slots from the payer listing, asks the status cache, never
    the history search, for recent probes the listing lacks, and asks getBlock
    again when a slot it knows to hold a probe answers null or -32004."""
    out = []
    with tempfile.TemporaryDirectory() as tmp:
        got, world, _, probes = _collect_with(tmp, lambda world, landed: None)
        listed = [params[0] for method, params in world.calls if method == "getSignaturesForAddress"]
        payers = {p["payer"] for p in probes.values()}
        asked = [params for method, params in world.calls if method == "getSignatureStatuses"]
        missing = sorted(s for s, inc in got.items() if inc["status"] != "included")
        out.append(("collect: one listing per payer; the status cache, no history search, for the rest",
                    sorted(listed) == sorted(payers) and len(asked) == 1
                    and asked[0][1] == {"searchTransactionHistory": False} and sorted(asked[0][0]) == missing,
                    "%d listings of %d payers, %d status calls %s" % (
                        len(listed), len(payers), len(asked), [a[1] for a in asked])))
    with tempfile.TemporaryDirectory() as tmp:
        old = synth.burst_rows(synth.run_row("x"), 0, [])[0]["last_valid_block_height"] \
            + collect.STATUS_CACHE_BLOCKS + 1
        got, world, _, _ = _collect_with(tmp, lambda world, landed: setattr(world, "block_height", old))
        asked = [params for method, params in world.calls if method == "getSignatureStatuses"]
        expired = sum(1 for inc in got.values() if inc["status"] == "expired")
        out.append(("collect: probes expired over 300 blocks below the height skip the status cache",
                    not asked and expired == 3, "%d status calls, %d expired" % (len(asked), expired)))
    with tempfile.TemporaryDirectory() as tmp:
        got, _, (sig, slot), _ = _collect_with(tmp, lambda world, landed: world.unlisted.add(landed[0]))
        inc = got[sig]
        out.append(("collect: a recent probe missing from the listing is found in the status cache",
                    (inc["status"], inc["slot"]) == ("included", slot),
                    "%s at slot %s" % (inc["status"], inc["slot"])))
    with tempfile.TemporaryDirectory() as tmp:
        got, world, (sig, slot), _ = _collect_with(
            tmp, lambda world, landed: world.flaky.update({landed[1]: [None, -32004]}))
        inc = got[sig] if isinstance(got, dict) else {"status": str(got)[:60], "slot": None}
        out.append(("collect: getBlock of an inclusion slot is asked again after null and -32004",
                    (inc["status"], inc["slot"]) == ("included", slot) and world.slept == [1.0, 2.0],
                    "%s at slot %s, pauses %s" % (inc["status"], inc["slot"], world.slept)))
    with tempfile.TemporaryDirectory() as tmp:
        got, _, _, _ = _collect_with(
            tmp, lambda world, landed: world.flaky.update({landed[1]: [None] * collect.BLOCK_ATTEMPTS}))
        out.append(("collect: an inclusion slot that stays null fails the collect",
                    isinstance(got, rpc.RpcError) and "null" in str(got),
                    str(got)[:90] if isinstance(got, rpc.RpcError) else "no error raised"))
    return out


class _StageRun:
    """The fields of a loaded run that prereg_check reads: one probe at block time 2000."""

    def __init__(self, stage, manifest_sha):
        self.run = {"run_id": "fake-%s" % stage, "stage": stage, "prereg_manifest_sha256": manifest_sha}
        self.inclusions = {"probe": {"status": "included", "block_time": 2000}}


def _anchor_check(memo_hash=None, memo_time=1000, run_hash=None, record=True, edit_after=None):
    """prereg_check over a repository with the pilot manifest and its anchor on a fake chain.
    Returns the problems; each argument breaks one link of the section 10 chain."""
    with tempfile.TemporaryDirectory() as tmp:
        repo, data = os.path.join(tmp, "repo"), os.path.join(tmp, "data")
        for d in ("prereg", "itb"):
            os.makedirs(os.path.join(repo, d))
        os.makedirs(data)
        for rel in verify.PILOT_MANIFEST_FILES:
            with open(os.path.join(repo, *rel.split("/")), "w", encoding="utf-8", newline="\n") as f:
                f.write("selftest copy of %s\n" % rel)
        manifest = verify.build_manifest(repo, "pilot", verify.PILOT_MANIFEST_FILES)
        with open(verify.manifest_path(repo, "pilot"), "wb") as f:
            f.write(manifest)
        digest = pilot.sha256_bytes(manifest)
        entry = fakechain.anchor_entry(verify.PREREG_MEMO_PREFIX + (memo_hash or digest), 1)
        world = fakechain.FakeChain()
        world.add_block(500, [entry], synth.key(5, 1), memo_time)
        anchors = [{"stage": "pilot", "file": "prereg/manifest-pilot.json", "manifest": True,
                    "signature": entry["transaction"]["signatures"][0], "sha256": digest}]
        with open(os.path.join(data, verify.ANCHORS_FILE), "w", encoding="utf-8") as f:
            json.dump(anchors if record else [], f)
        if edit_after:
            with open(os.path.join(repo, *edit_after.split("/")), "a", encoding="utf-8") as f:
                f.write("changed after the anchor\n")
        report = verify.Report(_quiet)
        verify.prereg_check([_StageRun("pilot", run_hash or digest)], world, report, data, repo)
        return report.problems


def prereg_checks():
    """Pre-registration anchor of section 10: the manifest and what verify asks of it."""
    out = []
    problems = _anchor_check()
    out.append(("prereg: verify accepts an anchor whose memo, files, plan and time agree",
                not problems, "%s" % problems[:1]))
    mutations = (
        ("the memo carries another hash", {"memo_hash": "0" * 64}),
        ("the memo lands after the first probe", {"memo_time": 2500}),
        ("the run was planned against another manifest", {"run_hash": "f" * 64}),
        ("no anchor is recorded for the stage", {"record": False}),
    ) + tuple(("%s changed after the anchor" % rel, {"edit_after": rel}) for rel in verify.PILOT_MANIFEST_FILES)
    for name, kwargs in mutations:
        problems = _anchor_check(**kwargs)
        out.append(("prereg mutation: %s fails verify" % name, len(problems) == 1,
                    problems[0][:90] if problems else "no problem found"))
    refused = 0
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, "a.txt"), "w") as f:
            f.write("a")
        for stage, files in (("pilot", []), ("test", ["a.txt"]), ("pilot", ["../a.txt"]),
                             ("pilot", ["missing.txt"])):
            try:
                verify.build_manifest(tmp, stage, files)
            except ValueError:
                refused += 1
        doc = json.loads(verify.build_manifest(tmp, "campaign", ["a.txt"]))
    out.append(("prereg: a manifest refuses no files, an unknown stage and paths outside the repository",
                refused == 4 and doc["files"] == {"a.txt": pilot.sha256_bytes(b"a")},
                "%d of 4 refused" % refused))
    return out


class _PlanCluster:
    """Answers the four calls plan.draw makes: two leaders over 4000 slots."""

    def call(self, method, params):
        if method == "getEpochInfo":
            return {"epoch": 5, "absoluteSlot": 10100, "slotIndex": 100, "slotsInEpoch": 4000}
        if method == "getLeaderSchedule":
            a = [i for i in range(4000) if (i // 4) % 2 == 0]
            return {"LeaderA": a, "LeaderB": [i for i in range(4000) if (i // 4) % 2 == 1]}
        if method == "getClusterNodes":
            return [{"pubkey": "LeaderA", "tpuQuic": "10.0.0.1:8009", "clientId": "Agave"},
                    {"pubkey": "LeaderB", "tpuQuic": None, "clientId": "Firedancer"}]
        if method == "getVoteAccounts":
            return {"current": [{"nodePubkey": "LeaderA", "votePubkey": "VoteA"}], "delinquent": []}
        raise AssertionError(method)


def plan_checks():
    """The test-plan draw: windows, spacing, cells and the probe specs of each arm."""
    out = []
    wins = plan.windows({"L": [0, 1, 2, 3, 4, 5, 6, 7, 12, 13]}, 1000)
    out.append(("plan: leader runs split at 4-slot boundaries", wins == [(1000, 4, "L"), (1004, 4, "L"), (1012, 2, "L")],
                str(wins)))
    p, snaps = plan.draw(_PlanCluster(), "localnet", "localnet", 16, 300, "selftest")
    bursts = p["rounds"][0]["bursts"]
    slots = [b["first_slot"] for b in bursts]
    out.append(("plan: 16 windows of the reachable leader, 160 slots apart, past the lead",
                len(bursts) == 16 and {b["leader"] for b in bursts} == {"LeaderA"} and slots[0] >= 10400
                and all(b - a >= plan.MIN_GAP_SLOTS for a, b in zip(slots, slots[1:])), str(slots[:3])))
    cells = [(b["arm"], b["timing"]) for b in bursts]
    out.append(("plan: each of the 8 cells twice in 16 bursts", sorted(cells) == sorted(list(plan.CELLS) * 2), ""))
    fee_ok = all(sorted(pr["priority_fee_lamports"] for pr in b["probes"]) == sorted(list(plan.FEES) * 3)
                 for b in bursts if b["arm"] in ("independent", "shared"))
    eq_ok = all(len({pr["priority_fee_lamports"] for pr in b["probes"]}) == 1
                and b["probes"][0]["priority_fee_lamports"] == b["equal_fee_lamports"]
                for b in bursts if b["arm"] in ("equal_fee", "denominator"))
    den_ok = all(sorted(pr["cu_limit"] for pr in b["probes"]) == [1000] * 6 + [20000] * 6
                 for b in bursts if b["arm"] == "denominator")
    gap_ok = all(b["send_interval_us"] == (5000 if b["arm"] == "equal_fee" else 0) for b in bursts)
    out.append(("plan: fee levels, equal fees, CU halves and send interval by arm",
                fee_ok and eq_ok and den_ok and gap_ok, ""))
    out.append(("plan: the drawn plan passes the probe's checks", plan.check(p) == [], "; ".join(plan.check(p))))
    out.append(("plan: same seed, same plan", plan.draw(_PlanCluster(), "localnet", "localnet", 16, 300, "selftest")[0]["rounds"][0]["bursts"] == bursts, ""))
    bad = json.loads(json.dumps(p))
    bad["rounds"][0]["bursts"][1]["first_slot"] = slots[0] + 8
    out.append(("plan: windows closer than 160 slots are refused", any("closer" in x for x in plan.check(bad)), ""))
    leak = json.loads(json.dumps(p))
    leak["rounds"][0]["cluster_nodes_file"] = "/run/secrets/wallet_key"
    leak["rounds"][0]["bursts"][0]["probes"][0]["priority_fee_lamports"] = 2 ** 64
    found = plan.check(leak)
    out.append(("plan: a snapshot path and a fee above the limit are refused",
                any("plain file name" in x for x in found) and any("priority fee above" in x for x in found), "; ".join(found)))
    out.append(("plan: snapshots carry nodes and schedule",
                len(snaps["cluster-nodes.json"]["nodes"]) == 2 and snaps["leader-schedule.json"]["first_slot"] == 10000, ""))
    return out


_PANEL_SPEC = (
    ("AB1", "AgaveBam", 900), ("AB2", "AgaveBam", 800), ("AB3", "AgaveBam", 700), ("AB4", "AgaveBam", 600),
    ("JL1", "JitoLabs", 900), ("JL2", "JitoLabs", 800), ("JL3", "JitoLabs", 700), ("JL4", "JitoLabs", 600),
    ("HA1", "HarmonicAgave", 900), ("HA2", "HarmonicAgave", 800), ("HA3", "HarmonicAgave", 700),
    ("HF1", "HarmonicFiredancer", 900), ("HF2", "HarmonicFiredancer", 800),
    ("HF3", "HarmonicFiredancer", 700), ("HF4", "HarmonicFiredancer", 600),
    ("FD1", "Firedancer", 900), ("FD2", "Firedancer", 800), ("FD3", "Firedancer", 700),
    ("FB1", "FireBAM", 900), ("FB2", "FireBAM", 800), ("FB3", "FireBAM", 700),
    ("RK1", "Rakurai", 900), ("RK2", "Rakurai", 800), ("RK3", "Rakurai", 700), ("RK4", "Rakurai", 600),
    ("AG0", "Agave", 1000), ("AG1", "Agave", 900), ("AG2", "Agave", 800), ("AG3", "Agave", 700),
    ("AG4", "Agave", 600),
)
_PANEL_EPOCH_FIRST = 10000
_PANEL_WINDOWS_PER_EIGHTH = 64


def _panel_world():
    """A cluster where each panel rule turns away exactly one candidate: two
    windows per eighth for every node, 16 in the epoch, except RK1 with 15;
    in eighth 3 both windows of HF1 follow XS, which shares its tpuQuic."""
    nodes = []
    for k, (ident, cls, _) in enumerate(_PANEL_SPEC):
        ip = "10.0.%d.1" % k
        nodes.append({"pubkey": ident, "clientId": cls, "version": "v1",
                      "gossip": ip + ":8001", "tpuQuic": ip + ":8009"})
    by = {n["pubkey"]: n for n in nodes}
    by["FB1"]["version"] = "v0"
    by["JL1"]["tpuQuic"] = "10.0.4.1:%d" % prereg.RELAYER_PORT
    by["JL2"]["tpuQuic"] = "10.9.9.9:8009"
    by["AG0"]["tpuQuic"] = None
    nodes.append({"pubkey": "XS", "clientId": "Unknown(9)", "version": "v1",
                  "gossip": "10.8.8.8:8001", "tpuQuic": by["HF1"]["tpuQuic"]})
    vote_accounts = {
        "current": [{"nodePubkey": i, "votePubkey": "V" + i, "activatedStake": s}
                    for i, _, s in _PANEL_SPEC if i != "AG1"],
        "delinquent": [{"nodePubkey": "AG1", "votePubkey": "VAG1", "activatedStake": 900}],
    }
    leaders = [i for i, _, _ in _PANEL_SPEC]
    seq = []
    for e in range(panel.EIGHTHS):
        part = leaders + leaders
        if e == 3:
            part = [x for i in part for x in (("XS", i) if i == "HF1" else (i,))]
        if e == 5:
            part.remove("RK1")
        seq += part + ["FILL"] * (_PANEL_WINDOWS_PER_EIGHTH - len(part))
    schedule = {}
    for w, leader in enumerate(seq):
        schedule.setdefault(leader, []).extend(range(w * 4, w * 4 + 4))
    blocks = {i: {"slot": 100 + k, "crank_memo": None, "fee_recipient": i,
                  "ticks": 3 if cls in panel.TICK_CLASSES else 0}
              for k, (i, cls, _) in enumerate(_PANEL_SPEC)}
    blocks["AB1"]["ticks"] = 0
    blocks["FD1"]["crank_memo"] = "BUN"
    blocks["FD3"]["crank_memo"] = "BAL"
    for i, memo in (("HA1", "MRV"), ("HA2", "MRV"), ("HA3", "FBA")):
        blocks[i]["crank_memo"] = memo
    blocks["RK2"]["fee_recipient"] = "Collector1"
    del blocks["HF2"]
    names = {"AG2": ["Op One"], "AG3": [" op  ONE "]}
    return nodes, vote_accounts, schedule, blocks, names


def _panel_select(world, exclude=()):
    nodes, vote_accounts, schedule, blocks, names = world
    stake, votes, late = panel.stakes(vote_accounts)
    slots = panel.EIGHTHS * _PANEL_WINDOWS_PER_EIGHTH * plan.SLOTS_PER_WINDOW
    facts = panel.window_facts(schedule, _PANEL_EPOCH_FIRST, slots, {n["pubkey"]: n.get("tpuQuic") for n in nodes})
    asked = []

    def block_of(identity):
        asked.append(identity)
        return blocks.get(identity)

    return panel.select(nodes, stake, votes, late, names, facts, block_of, exclude), asked


def panel_checks():
    """Leader panel (plan section 3): each rule turns away the candidate built to fail it."""
    out = []
    world = _panel_world()
    got, asked = _panel_select(world)
    picks = {cls: [p["identity"] for p in got[cls]["leaders"]] for cls in prereg.CLASSES}
    why = {r["identity"]: r["reason"] for c in got.values() for r in c["rejected"]}

    def turned(cls, want, ident, reason):
        return picks[cls] == want and why.get(ident, "").startswith(reason)

    out.append(("panel: two leaders in each of the 8 classes",
                all(len(v) == panel.PER_CLASS for v in picks.values()), str(picks)))
    for name, cls, want, ident, reason in (
            ("a version off the largest stake share of the class", "FireBAM", ["FB2", "FB3"], "FB1", "version v0"),
            ("a delinquent vote account", "Agave", ["AG2", "AG4"], "AG1", "delinquent"),
            ("a node without tpuQuic", "Agave", ["AG2", "AG4"], "AG0", "no tpuQuic"),
            ("tpuQuic off the gossip IP in a class without a builder", "JitoLabs", ["JL3", "JL4"], "JL2",
             "tpuQuic 10.9.9.9"),
            ("tpuQuic on the relayer port", "JitoLabs", ["JL3", "JL4"], "JL1", "tpuQuic on the relayer port"),
            ("15 windows in the epoch, while 16 pass", "Rakurai", ["RK3", "RK4"], "RK1", "15 leader windows"),
            ("an eighth whose windows all follow another validator on the same tpuQuic",
             "HarmonicFiredancer", ["HF3", "HF4"], "HF1", "no passing window in eighth 3"),
            ("no block in the last windows", "HarmonicFiredancer", ["HF3", "HF4"], "HF2", "no block"),
            ("a Fee reward to another collector", "Rakurai", ["RK3", "RK4"], "RK2", "Fee reward"),
            ("a BAM leader without ticks", "AgaveBam", ["AB2", "AB3"], "AB1", "no tick"),
            ("a Firedancer crank memo outside PRF and BAL, while no memo passes", "Firedancer", ["FD2", "FD3"],
             "FD1", "crank memo 'BUN'"),
            ("a second MRV leader in HarmonicAgave, which takes one MRV and one FBA", "HarmonicAgave",
             ["HA1", "HA3"], "HA2", "strategy MRV already"),
            ("the operator name of the first leader, compared without case and spacing", "Agave",
             ["AG2", "AG4"], "AG3", "operator"),
    ):
        out.append(("panel: turns away %s" % name, turned(cls, want, ident, reason),
                    "%s picks %s, %s: %s" % (cls, picks[cls], ident, why.get(ident))))
    cheap_only = {"JL1", "JL2", "HF1", "FB1", "RK1", "AG0", "AG1", "AG3"}
    out.append(("panel: blocks are read only past the rules without a block, and only until two leaders",
                not cheap_only & set(asked) and "AB4" not in asked and len(asked) == len(set(asked)) == 21,
                "%d reads" % len(asked)))
    again, _ = _panel_select(_panel_world(), exclude=("AB2",))
    out.append(("panel: an excluded leader gives way to the next one by the same rule",
                [p["identity"] for p in again["AgaveBam"]["leaders"]] == ["AB3", "AB4"], ""))
    out.append(("panel: same inputs, same panel", _panel_select(_panel_world())[0] == got, ""))
    out.append(("panel: relayer port stake share of a class",
                got["JitoLabs"]["relayer_port_stake_share"] == 0.3 and got["Agave"]["relayer_port_stake_share"] == 0,
                str(got["JitoLabs"]["relayer_port_stake_share"])))
    info = [{"account": {"data": {"parsed": {"type": "validatorInfo", "info": {
        "keys": [{"pubkey": "Va1idator1nfo111111111111111111111111111111", "signer": False},
                 {"pubkey": "AG2", "signer": True}], "configData": {"name": " Op One "}}}}}},
            {"account": {"data": {"parsed": {"type": "config", "info": {}}}}},
            {"account": {"data": ["", "base64"]}}]
    out.append(("panel: operator names come from the signer key of validator info",
                panel.operator_names(info) == {"AG2": ["Op One"]}, str(panel.operator_names(info))))
    out.append(("panel: host and port of IPv4 and IPv6 addresses",
                panel.host_port("1.2.3.4:8009") == ("1.2.3.4", 8009) and panel.host_port("[::1]:9") == ("::1", 9)
                and panel.host_port(None) == (None, None), ""))
    return out


def _first_burst(table, **match):
    return next(b for r in table["rounds"] for b in r["bursts"] if all(b[k] == v for k, v in match.items()))


def _flip_timing(table):
    b = _first_burst(table, extra=False, leader_rank=0)
    b["timing"] = "slot2" if b["timing"] == "pre300" else "pre300"
    b["cell"] = plan.CELLS.index((b["arm"], b["timing"]))


def _move_extra(table):
    rounds = table["rounds"]
    extra = next(b for b in rounds[0]["bursts"] if b["extra"])
    rounds[0]["bursts"].remove(extra)
    rounds[1]["bursts"].append(extra)


def pilot_checks():
    """Seeded pilot table and the placement of its bursts in windows (plan sections 6 and 7)."""
    out = []
    t = pilot.pilot_table("selftest")
    problems = pilot.table_problems(t)
    out.append(("pilot table: each class gets each cell once, classes share the cells of a round, fees balanced",
                problems == [], "; ".join(problems)))
    out.append(("pilot table: 68 bursts, 4 of them extra equal-fee bursts of builder classes",
                sum(len(r["bursts"]) for r in t["rounds"]) == 68
                and sorted(b["class"] for r in t["rounds"] for b in r["bursts"] if b["extra"]) == sorted(pilot.BUILDER_CLASSES),
                ""))
    out.append(("pilot table: same seed, same table; another seed, another table",
                pilot.pilot_table("selftest") == t and pilot.pilot_table("other") != t, ""))
    for name, change in (
            ("a class with one cell twice", _flip_timing),
            ("an extra burst in another cell", lambda x: _first_burst(x, extra=True).update(arm="independent")),
            ("two extra bursts in one round", _move_extra),
            ("a shared fee level moved", lambda x: _first_burst(x, extra=False, arm="denominator").update(
                equal_fee_lamports=_first_burst(x, extra=False, arm="denominator")["equal_fee_lamports"] + 1)),
            ("a probe fee raised by 1 lamport", lambda x: _first_burst(x, arm="independent")["probes"][0].update(
                priority_fee_lamports=_first_burst(x, arm="independent")["probes"][0]["priority_fee_lamports"] + 1)),
    ):
        bad = copy.deepcopy(t)
        change(bad)
        out.append(("pilot table: the balance check catches %s" % name, bool(pilot.table_problems(bad)), ""))
    leaders = {cls: ["%s-a" % cls, "%s-b" % cls] for cls in prereg.CLASSES}
    idents = [i for cls in prereg.CLASSES for i in leaders[cls]]
    passing = {ident: list(range(1000 + 4 * k, 400000, 4 * 40)) for k, ident in enumerate(idents)}
    placed = pilot.place(t, leaders, passing, 5000)
    ok, prev_end = True, None
    for r, p in zip(t["rounds"], placed):
        slots = sorted(p["slots"])
        ok &= all(b - a >= 160 for a, b in zip(slots, slots[1:])) and slots[0] >= p["anchor_slot"]
        ok &= all(s in passing[leaders[b["class"]][b["leader_rank"]]] for b, s in zip(r["bursts"], p["slots"]))
        ok &= prev_end is None or p["anchor_slot"] == prev_end + 160
        prev_end = slots[-1]
    out.append(("pilot plan: windows of the burst's leader, 160 slots apart, rounds one after another",
                ok and placed[0]["anchor_slot"] == 5000, str([p["anchor_slot"] for p in placed])))
    doc = {"network": "mainnet", "classes": {cls: {"leaders": [{"identity": i} for i in leaders[cls]]}
                                             for cls in prereg.CLASSES}}
    built = pilot.build(t, "aa", None, doc, placed, 7, 0, 432000, "2026-10-27T00:00:00Z", {}, None, None)
    out.append(("pilot plan: the built plan passes the probe's checks with stage pilot",
                plan.check(built) == [] and built["stage"] == "pilot"
                and pilot.cost(built)["priority_lamports"] * 4 == pilot.cost(built)["probes"] * sum(plan.FEES),
                "; ".join(plan.check(built))))
    out.append(("pilot plan: same table and windows, same placement", pilot.place(t, leaders, passing, 5000) == placed, ""))
    try:
        pilot.place(t, leaders, dict(passing, **{leaders["Rakurai"][1]: [900]}), 5000)
        refused = False
    except ValueError:
        refused = True
    out.append(("pilot plan: a leader without a window past the anchor stops the draw", refused, ""))
    return out


def _campaign_burst(t, **match):
    return next(b for ep in t["epochs"] for r in ep["rounds"] for b in r["bursts"]
                if all(b[k] == v for k, v in match.items()))


def _move_control(t):
    ep = t["epochs"][0]
    src = next(r for r in ep["rounds"] if any(b["path"] == "rpc" for b in r["bursts"]))
    dst = next(r for r in ep["rounds"] if r["arm"] != campaign.CONTROL_ARM)
    b = next(b for b in src["bursts"] if b["path"] == "rpc")
    src["bursts"].remove(b)
    dst["bursts"].append(b)


def campaign_checks():
    """Seeded campaign table, epoch placement and the pilot minimum (plan sections
    5.2, 6 and 7; analysis plan section 5)."""
    out = []
    t = campaign.campaign_table("selftest")
    problems = campaign.table_problems(t)
    bursts = [b for ep in t["epochs"] for r in ep["rounds"] for b in r["bursts"]]
    out.append(("campaign table: each leader gets each cell 4 times and one independent condition per epoch, "
                "classes share the cells of a round, fees balanced", problems == [], "; ".join(problems)))
    out.append(("campaign table: 576 bursts, 64 of them on the control path, 6912 probes",
                len(bursts) == 576 and sum(b["path"] == "rpc" for b in bursts) == 64
                and sum(len(b["probes"]) for b in bursts) == 6912, ""))
    single = campaign.campaign_table("selftest", doubling=False)
    out.append(("campaign table without doubling: 320 bursts, each cell twice per leader, balanced",
                campaign.table_problems(single) == []
                and sum(len(r["bursts"]) for ep in single["epochs"] for r in ep["rounds"]) == 320,
                "; ".join(campaign.table_problems(single))))
    out.append(("campaign table: same seed, same table; another seed, another table",
                campaign.campaign_table("selftest") == t and campaign.campaign_table("other") != t, ""))
    out.append(("campaign table: its seed comes from the one pilot anchor",
                campaign.seed_from_anchors([{"stage": "pilot", "signature": "abc"}]) == "campaign:abc", ""))
    for name, change in (
            ("a leader with one cell twice", lambda x: _campaign_burst(x, path="quic", arm="shared").update(
                timing=prereg.TIMINGS[1 - prereg.TIMINGS.index(_campaign_burst(x, path="quic", arm="shared")["timing"])],
                cell=plan.CELLS.index(("shared", prereg.TIMINGS[1 - prereg.TIMINGS.index(
                    _campaign_burst(x, path="quic", arm="shared")["timing"])])))),
            ("a control burst in a round of another arm", _move_control),
            ("a control burst in the other condition", lambda x: _campaign_burst(x, path="rpc").update(
                timing=prereg.TIMINGS[1 - prereg.TIMINGS.index(_campaign_burst(x, path="rpc")["timing"])])),
            ("a shared fee level moved", lambda x: _campaign_burst(x, arm="equal_fee").update(
                equal_fee_lamports=_campaign_burst(x, arm="equal_fee")["equal_fee_lamports"] + 1)),
            ("a probe fee raised by 1 lamport", lambda x: _campaign_burst(x, arm="independent")["probes"][0].update(
                priority_fee_lamports=_campaign_burst(x, arm="independent")["probes"][0]["priority_fee_lamports"] + 1)),
    ):
        bad = copy.deepcopy(t)
        change(bad)
        out.append(("campaign table: the balance check catches %s" % name, bool(campaign.table_problems(bad)), ""))

    leaders = {cls: ["%s-a" % cls, "%s-b" % cls] for cls in prereg.CLASSES}
    idents = [i for cls in prereg.CLASSES for i in leaders[cls]]
    first, n = 1_000_000, 432_000
    passing = {ident: list(range(first + 4 * k, first + n, 4 * 40)) for k, ident in enumerate(idents)}
    placed, notes = campaign.place_epoch(t["epochs"][0], t["seed"], leaders, passing, first, n, first - 900)
    slots = sorted(s for p in placed for s in p["slots"])
    ok = not notes and len(slots) == 144 and all(b - a >= plan.MIN_GAP_SLOTS for a, b in zip(slots, slots[1:]))
    for r, p in zip(t["epochs"][0]["rounds"], placed):
        lo, hi = campaign.part_bounds(r["round"], len(placed), first, n)
        ok &= lo <= p["anchor_slot"] < hi
        ok &= all(s in passing[leaders[b["class"]][b["leader_rank"]]] for b, s in zip(r["bursts"], p["slots"]))
    out.append(("campaign plan: windows of the burst's leader, each round anchored in its eighth, "
                "160 slots apart over the epoch", ok, "%d windows, notes %s" % (len(slots), notes[:2])))
    doc = {"network": "mainnet", "classes": {cls: {"leaders": [{"identity": i} for i in leaders[cls]]}
                                             for cls in prereg.CLASSES}}
    built = campaign.build(t, 0, "aa", "bb", doc, placed, 1071, first, n, "2026-10-28T00:00:00Z", {}, None, None)
    out.append(("campaign plan: the built plan passes the probe's checks with stage campaign and doubling",
                plan.check(built) == [] and built["stage"] == "campaign" and built["doubling"]
                and [r["part"] for r in built["rounds"]] == list(range(8))
                and sum(b["path"] == "rpc" for r in built["rounds"] for b in r["bursts"]) == 16,
                "; ".join(plan.check(built))))
    out.append(("campaign plan: same table and windows, same placement",
                campaign.place_epoch(t["epochs"][0], t["seed"], leaders, passing, first, n, first - 900)[0] == placed, ""))
    cut = min(placed[4]["slots"])
    late, late_notes = campaign.place_epoch(t["epochs"][0], t["seed"], leaders, passing, first, n, cut)
    out.append(("campaign plan: drawn again mid-epoch, it keeps the windows of the rounds ahead and leaves out "
                "the round in progress", late == placed[4:] and len(late_notes) == 4, str(late_notes[-1:])))
    late, late_notes = campaign.place_epoch(t["epochs"][0], t["seed"], leaders, passing, first, n, cut + 1)
    out.append(("campaign plan: a round with one window already passed is left out whole",
                late == placed[5:] and len(late_notes) == 5, ""))
    gone = dict(passing, **{leaders["Rakurai"][1]: []})
    _, gone_notes = campaign.place_epoch(t["epochs"][0], t["seed"], leaders, gone, first, n, first - 900)
    out.append(("campaign plan: a leader without windows loses its bursts with a note, the epoch goes on",
                len(gone_notes) == 9 and all("Rakurai" in x for x in gone_notes), str(len(gone_notes))))

    rnd = random.Random("itb-selftest-sigma")
    a = {cls: rnd.uniform(-0.3, 0.3) for cls in prereg.CLASSES}
    pts = [(cls, k, a[cls] + 0.1 * j + rnd.gauss(0, 0.2)) for cls in prereg.CLASSES
           for j, k in enumerate(prereg.TIMINGS)]
    y = {(c, k): v for c, k, v in pts}
    row = {c: sum(y[(c, k)] for k in prereg.TIMINGS) / 2 for c in prereg.CLASSES}
    col = {k: sum(y[(c, k)] for c in prereg.CLASSES) / 8 for k in prereg.TIMINGS}
    grand = sum(y.values()) / 16
    rss = sum((y[(c, k)] - row[c] - col[k] + grand) ** 2 for c in prereg.CLASSES for k in prereg.TIMINGS)
    fit = campaign.slot_sigma(pts)
    out.append(("minimum: class plus cell residual sd equals the two-way closed form, 7 degrees of freedom",
                fit["df"] == 7 and abs(fit["sigma"] - math.sqrt(rss / 7)) < 1e-12,
                "%s vs %.6f" % (fit["sigma"], math.sqrt(rss / 7))))
    exact = campaign.slot_sigma([(c, k, a[c] + 0.1 * j) for c in prereg.CLASSES for j, k in enumerate(prereg.TIMINGS)])
    one = campaign.slot_sigma([(c, prereg.TIMINGS[0], a[c]) for c in prereg.CLASSES])
    out.append(("minimum: an exactly additive slot leaves no residual; one burst per class leaves no degree of freedom",
                exact["sigma"] < 1e-9 and one["sigma"] is None and one["df"] == 0, ""))
    null = _null_sigma("independent")
    out.append(("minimum: the null sigma of one burst gives a minimum above the 8 bursts the doubled campaign has",
                verdict.min_bursts_formula(null) > 8, str(verdict.min_bursts_formula(null))))

    class Reply:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def read(self):
            return b'[{"account": "A", "software_client": "Agave", "software_version": "4.3.2"}]'

    seen = []
    pilot.validators_app("mainnet", lambda req, **kw: seen.append(kw) or Reply(), env={})
    try:
        pilot.validators_app("mainnet", lambda req, **kw: Reply(), env={pilot.EXTRA_CA_ENV: "not a pem"})
        bad_root = None
    except OSError as e:
        bad_root = e
    out.append(("validators.app: no extra root, no own TLS context; a broken extra root fails as OSError, "
                "which the draw turns into a note", seen == [{"timeout": 90}] and bad_root is not None, ""))
    snap = pilot.va_snapshot("u", {"A": {}}, env={pilot.EXTRA_CA_ENV: "pem"})
    out.append(("validators.app: the snapshot records the sha256 of an extra root and null without one",
                snap["extra_ca_sha256"] == pilot.sha256_bytes(b"pem")
                and pilot.va_snapshot("u", {}, env={})["extra_ca_sha256"] is None, ""))
    with tempfile.TemporaryDirectory() as d:
        root = os.path.join(d, "root.pem")
        with open(root, "w", encoding="ascii") as f:
            f.write("pem\n")
        from_file = pilot.extra_ca({pilot.EXTRA_CA_FILE_ENV: root})
        text_first = pilot.extra_ca({pilot.EXTRA_CA_ENV: "text", pilot.EXTRA_CA_FILE_ENV: root})
        try:
            pilot.extra_ca({pilot.EXTRA_CA_FILE_ENV: os.path.join(d, "missing.pem")})
            missing = None
        except OSError as e:
            missing = e
    out.append(("validators.app: ITB_EXTRA_CA_FILE gives the root from its file, the PEM text wins over it, "
                "and a missing file fails as OSError",
                from_file == "pem" and text_first == "text" and missing is not None, ""))
    return out


def _rounds_unit(cls, segments, arm="equal_fee", timing="slot2", reverse=False, seq=0):
    n = len(segments)
    block = [{"pos": i, "fee": 100, "send_rank": n - 1 - i if reverse else i, "cu_limit": 1400, "segment": s}
             for i, s in enumerate(segments)]
    burst = {"arm": arm, "timing": timing, "selection_class": cls}
    return analyze.Unit("r", seq, burst, [block], [], None)


def rounds_checks():
    """Pilot rounds test (analysis plan section 10) on blocks with known segments."""
    out = []
    rounds = [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3]
    piece = verdict.segment_piece(_rounds_unit("a", rounds).blocks[0])
    tau, s, d = stats.tau_b(list(range(12)), rounds)
    out.append(("rounds test: a block in four rounds of three gives S 54 and the tau-b of send rank and segment",
                piece.s == 54 and _close(piece.s / piece.d, tau, 1e-12) and _close(tau, math.sqrt(54 / 66), 1e-12),
                "%.6f" % tau))
    rt = analyze.rounds_test([_rounds_unit("a", rounds)])
    out.append(("rounds test: one such burst is supported with the exact p 2/369600",
                rt["form"] == "supported" and rt["pooled"]["p_exact"] == "1/184800", rt["pooled"]["p_exact"]))
    one = _rounds_unit("a", [5] * 12)
    blind = _rounds_unit("a", [None] * 12)
    out.append(("rounds test: one segment or no ticks leaves a block out",
                verdict.segment_piece(one.blocks[0]) is None and verdict.segment_piece(blind.blocks[0]) is None
                and analyze.rounds_test([one, blind])["form"] == "no data", ""))
    noise = [_rounds_unit("b", rounds, reverse=True, timing="pre300"),
             _rounds_unit("b", rounds, reverse=True, arm="independent")]
    rt = analyze.rounds_test([_rounds_unit("a", rounds)] + noise)
    out.append(("rounds test: the pre-window condition and other arms stay out",
                rt["bursts"] == 1 and list(rt["classes"]) == ["a"], str(rt["bursts"])))
    rt = analyze.rounds_test([_rounds_unit("a", rounds), _rounds_unit("b", rounds, reverse=True, seq=1),
                              _rounds_unit("b", rounds, reverse=True, seq=2)])
    out.append(("rounds test: later-sent probes more often in earlier segments refute it, per class taus apart",
                rt["form"] == "refuted" and rt["pooled"]["S"] == -54 and _close(rt["negative_share"], 2 / 3, 1e-12)
                and rt["classes"]["a"]["S"] == 54 and rt["classes"]["b"]["S"] == -108, rt["form"]))
    return out


def timing_checks():
    """Moment bands (plan sections 5.1 and 10): the slot-2 reference and the final aim."""
    out = []
    burst = {"timing": "slot2", "slot_ms": 243.0, "rtt_ns": 300_000_000,
             "send_at_ns": 0, "predicted_first_slot_ns": 0}
    aimed = {"first_shred_ns": [None, None], "first_send_offset_ns": None,
             "send_predicted_first_slot_ns": 1_000_000_000, "send_target_arrival_ns": 1_145_000_000,
             "send_rtt_ns": 40_000_000}
    seen = dict(aimed, first_shred_ns=[1_000_000_000, 1_042_000_000], first_send_offset_ns=110_000_000)
    out.append(("timing: slot 2 starts where its first shred was seen",
                analyze.slot2_ms(burst, seen) == 42.0, str(analyze.slot2_ms(burst, seen))))
    out.append(("timing: without both shreds the final aim gives slot 2",
                analyze.slot2_ms(burst, aimed) == 145.0, str(analyze.slot2_ms(burst, aimed))))
    out.append(("timing: without an aim the mean slot length gives slot 2",
                analyze.slot2_ms(burst, None) == 243.0, ""))
    est = analyze.arrival_ms(burst, seen)
    out.append(("timing: arrival takes half the RTT of the final aim", est == 130.0, str(est)))
    out.append(("timing: 130 ms is in the band of a slot 2 seen at 42 ms, out of one at 243 ms",
                analyze.timing_in_band(burst, est, seen) and not analyze.timing_in_band(burst, est, None), ""))
    pre = dict(burst, timing="pre300")
    inside = [ms for ms in (-550.0, -500.0, -450.0, -300.0, -200.0, -150.0) if analyze.timing_in_band(pre, ms)]
    out.append(("timing: the pre-window band runs from 500 ms to 200 ms before the first slot",
                inside == [-500.0, -450.0, -300.0, -200.0], str(inside)))
    # Schema version 2: the node timestamps hold when a WebSocket backlog delays receipt.
    late = dict(seen, first_shred_ns=[3_000_000_000, 3_400_000_000], first_send_offset_ns=-1_890_000_000,
                node_ts_ms=[1_793_044_800_000, 1_793_044_800_044], first_send_node_offset_ns=110_000_000)
    out.append(("timing: node timestamps give slot 2 when receipt was delayed",
                analyze.slot2_ms(burst, late) == 44.0, str(analyze.slot2_ms(burst, late))))
    out.append(("timing: arrival takes the send offset on node time first",
                analyze.arrival_ms(burst, late) == 130.0, str(analyze.arrival_ms(burst, late))))
    return out


def clock_guard_checks():
    """Slot clock guard (plan section 5.1): the lag bound and the version 1 rule."""
    out = []
    rows = sample_run()
    b = rows[1]
    lag = lambda n: dict(b, clock_lag_slots=n)
    out.append(("clock guard: a lag of 2 slots keeps the burst out, 1 slot and an unknown lag do not",
                analyze.clock_behind(lag(2)) and not analyze.clock_behind(lag(1))
                and not analyze.clock_behind(lag(None)), ""))
    v1 = {k: val for k, val in b.items() if k not in ("slot_clock_basis", "clock_offset_ns", "http_slot",
                                                      "http_slot_rtt_ns", "clock_slot_at_http", "clock_lag_slots")}
    first = v1["first_slot"]
    out.append(("clock guard: a version 1 burst with a blockhash from the slot of the fetch is late, 3 slots earlier is not",
                analyze.clock_behind(dict(v1, blockhash_context_slot=first - 6))
                and not analyze.clock_behind(dict(v1, blockhash_context_slot=first - 9)), ""))
    schema = rawformat.load_schema()
    old = []
    for r in rows:
        r = dict(r, v=1)
        for name, spec in schema["kinds"][r["kind"]]["fields"].items():
            if spec.get("since", 1) > 1:
                r.pop(name, None)
        old.append(r)
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "probes.jsonl")
        _write(path, old)
        n, problems = rawformat.check_probe_file(path, schema)
    out.append(("clock guard: version 1 rows without the guard fields stay valid",
                n == len(old) and not problems, "%d rows, %s" % (n, problems[:3])))
    return out


def _channel_run(arrivals, rtt_ms=40.0):
    """Rows and log events of a live run with one round of len(arrivals) pre300
    windows; an arrival of None is a burst the probe skipped for its clock."""
    rows = [{"kind": "run", "run_id": "c", "stage": "campaign", "mode": "live"},
            {"kind": "round", "run_id": "c", "round": 0, "epoch": 1,
             "windows": [{"burst_seq": s, "leader": "L", "first_slot": 100 * s} for s in range(len(arrivals))]}]
    events = []
    for s, ms in enumerate(arrivals):
        if ms is None:
            events.append({"event": "burst_skipped", "burst_seq": s,
                           "data": {"reason": "slot clock 3 slots behind getSlot processed 5 (first_shred on node_ts)"}})
            continue
        rows.append({"kind": "burst", "run_id": "c", "burst_seq": s, "round": 0, "timing": "pre300", "path": "quic",
                     "slot_ms": 400.0, "rtt_ns": int(rtt_ms * 1e6), "send_at_ns": 0, "predicted_first_slot_ns": 0,
                     "handshake": None, "clock_lag_slots": 0, "http_slot_rtt_ns": 50_000_000})
        # arrival_ms adds half the RTT to the send offset, so the offset gives ms exactly.
        rows.append({"kind": "burst_end", "run_id": "c", "burst_seq": s, "send_rtt_ns": int(rtt_ms * 1e6),
                     "first_send_node_offset_ns": int(ms * 1e6 - rtt_ms * 5e5), "reconnects": 0})
    return rows, events


class _FakeRpc:
    """HTTPS connection stand-in for channel.rpc_rtt: each reply takes 50 ms on the
    fake clock and request number fail_at raises."""

    def __init__(self, now, count, fail_at):
        self.now, self.count, self.fail_at = now, count, fail_at

    def request(self, *a):
        self.count[0] += 1
        if self.count[0] == self.fail_at:
            raise OSError("reset")

    def getresponse(self):
        return self

    status = 200

    def read(self):
        self.now[0] += 0.05
        return b'{"jsonrpc":"2.0","id":1,"result":5}'

    def close(self):
        pass


def channel_checks():
    """Line health of plan-implementation section 11: round summaries, thresholds,
    the journal of the campaign watch and getSlot round trips."""
    out = []
    one = lambda arrivals, **kw: channel.rounds(*_channel_run(arrivals, **kw))
    r = one([-300.0] * 4 + [0.0])
    out.append(("channel: 4 of 5 bursts in the band pass the three-quarter share",
                len(r) == 1 and r[0]["in_band"] == 4 and r[0]["in_band_share"] == 0.8 and not r[0]["below"], str(r)))
    r = one([-300.0] * 3 + [0.0, 0.0])
    out.append(("channel: 3 of 5 in the band miss it", r[0]["below"] == ["in_band_share"], str(r[0]["below"])))
    r = one([-300.0] * 2 + [0.0])
    out.append(("channel: a round of 3 written bursts gets no share verdict", r[0]["below"] == [], str(r[0]["below"])))
    r = one([-300.0] * 8 + [None, None])
    out.append(("channel: 2 clock skips of 10 windows miss the skip share, the 8 written stay in the band",
                r[0]["skipped_clock"] == 2 and r[0]["written"] == 8 and r[0]["below"] == ["clock_skip_share"],
                str(r[0])))
    rows, events = _channel_run([-300.0] * 5)
    cut = rows[:-1]
    out.append(("channel: a round with a window not done waits; partial shows it, the run summary ends it",
                channel.rounds(cut, events) == [] and channel.rounds(cut, events, partial=True)[0]["complete"] is False
                and channel.rounds(cut, events + [{"event": "summary"}])[0]["complete"] is True, ""))
    hs = [{"event": "quic_connected", "burst_seq": s, "data": {"rtt_ns": 200_000_000}} for s in range(5)]
    r = channel.rounds(rows, events + hs)
    out.append(("channel: the handshake RTT of the run log wins over the burst row and misses 150 ms",
                r[0]["quic_rtt_ms"] == [200.0, 200.0, 200.0] and r[0]["below"] == ["quic_rtt_median"], str(r[0])))
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "x.jsonl")
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write('{"a": 1}\n{"b": ')
        try:
            got = channel.read_rows(path)
        except ValueError as e:
            got = e
        out.append(("channel: a cut last line waits for the next read", got == [{"a": 1}], str(got)))
        rows, events = _channel_run([-300.0] * 3 + [0.0, 0.0])
        os.makedirs(os.path.join(tmp, "data", "runs", "c"))
        os.makedirs(os.path.join(tmp, "logs"))
        _write(os.path.join(tmp, "data", "runs", "c", "probes.jsonl"), rows)
        _write(os.path.join(tmp, "logs", "c.jsonl"), events)
        journal = os.path.join(tmp, "logs", "channel.jsonl")
        args = (os.path.join(tmp, "data"), os.path.join(tmp, "logs"), journal)
        first = channel.watch(*args, once=True, say=lambda line: None)
        second = channel.watch(*args, once=True, say=lambda line: None)
        lines = channel.read_rows(journal)
    out.append(("channel: the watch journals a round below a threshold once and stops at it",
                first == channel.EXIT_BELOW and second == 0 and len(lines) == 1 and lines[0]["below"] == ["in_band_share"],
                "%s %s %d" % (first, second, len(lines))))
    now, count = [0.0], [0]
    res = channel.rpc_rtt("https://rpc.example", 10, 1.0, clock=lambda: now[0],
                          sleep=lambda s: now.__setitem__(0, now[0] + s), connect=lambda: _FakeRpc(now, count, 4))
    out.append(("channel: getSlot round trips leave out the first request of each connection and count a failure",
                res["samples"] == 7 and res["failed"] == 1 and res["http_rtt_ms"] == [50.0, 50.0, 50.0]
                and res["below"] == ["rpc_fail_share"], str(res)))
    return out


class _Reply:
    def __init__(self, body, error=None):
        self.body, self.error, self.headers = body, error, {}

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self):
        if self.error is not None:
            raise self.error
        return self.body


def rpc_checks():
    """A reply cut short or a dropped connection is retried, an RPC error is not."""
    out = []
    good = json.dumps({"jsonrpc": "2.0", "id": 1, "result": 7}).encode()
    cases = (("a body cut short", _Reply(b"", http.client.IncompleteRead(b"x" * 10)), 7),
             ("a dropped connection", ConnectionResetError("reset"), 7),
             ("a broken gzip stream", EOFError("compressed file ended"), 7))
    saved = rpc.urllib.request.urlopen
    try:
        for name, error, want in cases:
            replies = [error, _Reply(good)]

            def fake(request, timeout=None):
                r = replies.pop(0)
                if isinstance(r, BaseException):
                    raise r
                return r
            rpc.urllib.request.urlopen = fake
            client = rpc.Client("https://rpc.example", sleep=lambda s: None)
            try:
                got = client.call("getSlot", [])
            except Exception as e:  # an escaping error is the failure this check looks for
                got = "%s: %s" % (type(e).__name__, e)
            out.append(("rpc: %s is retried" % name, got == want, "got %r" % (got,)))
        replies = [_Reply(json.dumps({"jsonrpc": "2.0", "id": 1, "error": {"code": -32004}}).encode()),
                   _Reply(good)]
        rpc.urllib.request.urlopen = lambda request, timeout=None: replies.pop(0)
        try:
            rpc.Client("https://rpc.example", sleep=lambda s: None).call("getBlock", [1])
            code = None
        except rpc.RpcError as e:
            code = e.code
        out.append(("rpc: an RPC error answer is not retried", code == -32004 and len(replies) == 1,
                    "code %s, %d replies left" % (code, len(replies))))
        storage = json.dumps({"jsonrpc": "2.0", "id": 1, "error": {
            "code": -32019, "message": "Failed to query long-term storage; please try again"}}).encode()
        replies = [_Reply(storage), _Reply(good)]
        rpc.urllib.request.urlopen = lambda request, timeout=None: replies.pop(0)
        try:
            got = rpc.Client("https://rpc.example", sleep=lambda s: None).call("getSignaturesForAddress", [])
        except rpc.RpcError as e:
            got = e.code
        out.append(("rpc: a long-term storage error (-32019) is retried", got == 7 and not replies,
                    "got %r, %d replies left" % (got, len(replies))))
    finally:
        rpc.urllib.request.urlopen = saved
    pages = _Pages([[{"signature": "sig%d" % i} for i in range(1000)],
                    [{"signature": "sig%d" % i} for i in range(1000, 1003)],
                    [{"signature": "sig1003"}]])
    got = rpc.signatures_for_address(pages, "payer")
    out.append(("rpc: the signature listing stops at a page shorter than 1000",
                len(got) == 1003 and pages.before == [None, "sig999"],
                "%d entries, before %s" % (len(got), pages.before)))
    return out


class _Pages:
    """getSignaturesForAddress over fixed pages; records the before of each call."""

    def __init__(self, pages):
        self.pages, self.before = list(pages), []

    def call(self, method, params):
        self.before.append(params[1].get("before"))
        return self.pages.pop(0) if self.pages else []


def report_checks():
    """Generated REPORT blocks: fill rewrites only the blocks, the control-path
    label test is exact on a small case, and every per-stage table runs on a
    synthetic run with control-path bursts, which the pilot did not have."""
    out = []
    text = ("# T\n\nprose\n<!-- itb:begin a -->\nold\n<!-- itb:end a -->\nmore\n"
            "<!-- itb:begin b -->\nsame\n<!-- itb:end b -->\n")
    fresh = {"a": "new\nrows", "b": "same"}
    new, changed = report.fill(text, fresh)
    out.append(("report: fill rewrites a stale block and keeps the prose and a current block",
                changed == ["a"] and new == text.replace("old", "new\nrows"), "changed %s" % changed))
    again, changed = report.fill(new, fresh)
    out.append(("report: a second fill changes nothing", again == new and not changed, "changed %s" % changed))
    for name, bad in (("a block without its end line", "<!-- itb:begin a -->\nx\n"),
                      ("an unknown block", "<!-- itb:begin zz -->\n<!-- itb:end zz -->\n")):
        try:
            report.fill(bad, fresh)
            got = "no error"
        except ValueError as e:
            got = str(e)
        out.append(("report: %s is an error" % name, got != "no error", got))
    p, method, smallest = report._path_label_p([([1.0, 2.0, 3.0, 4.0], 2)])
    out.append(("report: the path label test is exact on a small stratum and names its smallest p",
                p == 2 / 6 and method == "exact over 6" and smallest == 2 / 6,
                "p %s, %s, smallest %s" % (p, method, smallest)))
    tx = {"signatures": ["s"], "write_accounts": ["w", "w"], "ix_data_bytes": 12, "cu_limit": 1000,
          "loaded_data_limit": None}
    got = report._requested_cost(tx) - chain.agave_cost(1, 1, 12, 1000, 0)
    out.append(("report: a transaction without a loaded-data limit pays the 64 MiB allowance", got == 16384,
                "%d units over a zero allowance" % got))
    spec = [{"class": "FireBAM", "rule": "fifo", "arm": "independent", "timing": "pre300", "round": rnd,
             "fields": {"path": path}} for rnd in range(3) for path in ("quic", "rpc")]
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = os.path.join(tmp, "runs", "selftest-report")
        os.makedirs(run_dir)
        prows, crows = synth.campaign_rows("selftest-report", spec, "itb-selftest:report")
        _write(os.path.join(run_dir, "probes.jsonl"), prows)
        _write(os.path.join(run_dir, "collect.jsonl"), crows)
        runs = analyze.load_runs(tmp)
        items = report._items(runs)
        tables = {}
        try:
            for name, make in (("timing", report.timing_block), ("labels", report.labels_block),
                               ("latency", report.latency_block), ("loads", report.loads_block),
                               ("first-slot", report.first_slot_block), ("strategy", report.strategy_block),
                               ("epochs", report.epochs_block), ("control", report.control_block)):
                tables[name] = make(items)
            tables["elsewhere"] = report.elsewhere_block(runs)
            tables["competition"] = report.competition_block(items, tmp)
            error = None
        except Exception as e:  # a table that cannot be built is the failure this check looks for
            error = "%s: %s" % (type(e).__name__, e)
    out.append(("report: every per-stage table builds on a synthetic run", error is None and len(tables) == 10,
                error or "%d tables" % len(tables)))
    control = tables.get("control", "")
    # Three control and three direct bursts in one stratum: no arrangement reaches p <= 0.05.
    out.append(("report: the control table compares both measures in one stratum and, with too few bursts "
                "to reach 0.05, prints them descriptive without a p",
                "| tau fee | 1 | -0.134 | - | descriptive: smallest attainable p 0.1, exact over 20 |" in control
                and "| inclusion share | 1 | 0.000 | - | descriptive: smallest attainable p 1, exact over 20 |"
                in control, repr(control.split("\n")[2:4])))
    _, _, smallest = report._path_label_p([([float(v) for v in range(8)], 4)])
    out.append(("report: four control and four direct bursts can reach 0.05, so their stratum is tested",
                smallest == 2 / 70 and smallest <= stats.ALPHA, "smallest %s" % smallest))
    calls = []
    real = stats.fisher_yates
    stats.fisher_yates = lambda items, rnd: calls.append(1) or real(items, rnd)
    try:
        _, method, _ = report._path_label_p([([float(v) for v in range(10)], 5)] * 3)
    finally:
        stats.fisher_yates = real
    out.append(("report: a stratum set past the exact limit draws its labels with the own Fisher-Yates",
                method.startswith("%d draws, seed %s, Monte Carlo SE " % (prereg.LABEL_TEST_B, prereg.LABEL_TEST_SEED))
                and len(calls) == 3 * prereg.LABEL_TEST_B,
                "%s, %d shuffles" % (method, len(calls))))
    parts = [[[c.strip() for c in line.split("|")[1:-1]] for line in part.split("\n")[2:]]
             for part in tables.get("elsewhere", "").split("\n\n")]
    by_class = parts[1] if len(parts) == 2 else []
    out.append(("report: probes outside their window add up per class of the target",
                [r[0] for r in by_class] == ["FireBAM"]
                and [int(c) for c in by_class[0][1:]] == [sum(int(r[i]) for r in parts[0]) for i in range(2, 7)],
                repr(by_class)))
    # Leader A holds two windows: the first follows N on A's IP with another port, the second follows O
    # on another IP. The whole-address rule keeps both, and the table counts only the first.
    with tempfile.TemporaryDirectory() as tmp:
        d = os.path.join(tmp, "panels", "p")
        os.makedirs(d)
        for name, body in (("panel.json", {"classes": {"HarmonicAgave": {"leaders": [{"identity": "A"}]}}}),
                           ("cluster-nodes.json", {"nodes": [{"pubkey": "A", "tpuQuic": "10.0.0.1:8009"},
                                                             {"pubkey": "N", "tpuQuic": "10.0.0.1:9007"},
                                                             {"pubkey": "O", "tpuQuic": "10.0.0.2:8009"}]}),
                           ("leader-schedule.json", {"first_slot": 1000, "schedule": {
                               "N": [0, 1, 2, 3], "A": [4, 5, 6, 7, 12, 13, 14, 15], "O": [8, 9, 10, 11]}})):
            with open(os.path.join(d, name), "w", encoding="utf-8") as f:
                json.dump(body, f)
        near = report.neighbours_block(tmp)
    out.append(("report: a neighbour on the same IP with another port is counted, one on another IP is not",
                "| `p` | HarmonicAgave | 2 | 1 | 0.500 |" in near, near.split("\n")[-1]))

    def hyp_cell(cls, tau, sig, eq):
        return {"class": cls, "arm": "equal_fee", "timing": "pre300", "bursts": 10, "significant": {"send": sig},
                "equivalent": {"send": eq}, "taus": {"send": {"tau": tau, "ci95": [tau - 0.1, tau + 0.1], "p": 0.001}}}

    def outcomes(cells):
        text = report.hypotheses_block({"cells": cells})
        return {row.split(" | ")[0].strip("| "): row.rstrip(" |").rsplit(" | ", 1)[1]
                for row in text.split("\n")[2:]}

    negative = outcomes([hyp_cell("Firedancer", -0.3, True, False), hyp_cell("Agave", -0.3, True, False),
                         hyp_cell("FireBAM", -0.3, True, False)])
    flat = outcomes([hyp_cell("Firedancer", 0.0, False, True), hyp_cell("Agave", 0.0, False, True)])
    out.append(("report: H3 holds on a negative significant tau send of Firedancer, H4 on Agave never holds and "
                "agrees with the fresh-key part or, on a passed TOST, the recycled-key part; other classes compare",
                negative["Firedancer"] == "holds" and negative["Agave"] == "agrees with the fresh-key part"
                and negative["FireBAM"] == "-" and flat["Firedancer"] == "fails"
                and flat["Agave"] == "agrees with the recycled-key part" and negative["AgaveBam"] == "-",
                "%s; %s" % (negative, flat)))
    return out


class _EpochClient:
    """RPC stand-in for campaign.draw: chain epoch now, and no leader schedule yet."""

    def __init__(self, epoch):
        self.epoch = epoch

    def call(self, method, params):
        if method == "getEpochInfo":
            return {"epoch": self.epoch, "absoluteSlot": 432000 * self.epoch + 100, "slotIndex": 100,
                    "slotsInEpoch": 432000}
        return None


class _GossipClient(_EpochClient):
    """campaign.draw's calls in a chain epoch whose live gossip has moved leader A to another IP."""

    def call(self, method, params):
        if method == "getLeaderSchedule":
            return {"A": [0, 1, 2, 3]}
        if method == "getClusterNodes":
            return [{"pubkey": "A", "tpuQuic": "10.0.0.9:8009"}]
        if method == "getVoteAccounts":
            return {"current": [], "delinquent": []}
        return super().call(method, params)


def _module_copy(name, old=None, new=None):
    """A fresh copy of itb/<name>.py with the text old replaced once by new: a mutant of the
    source itself, for a rule that lives in a line of a command rather than in a function."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name + ".py")
    with open(path, encoding="utf-8") as f:
        src = f.read()
    if old is not None:
        if src.count(old) != 1:
            raise RuntimeError("selftest: the mutant text occurs %d times in itb/%s.py" % (src.count(old), name))
        src = src.replace(old, new)
    ns = {"__name__": "itb._selftest_" + name.strip("_"), "__package__": __package__, "__file__": path}
    exec(compile(src, path, "exec"), ns)
    return ns


def _patched(owner, name, value, fn):
    """fn() with owner.name replaced by value, the original put back after."""
    real = getattr(owner, name)
    setattr(owner, name, value)
    try:
        return fn()
    finally:
        setattr(owner, name, real)


def _raises(fn):
    try:
        fn()
    except ValueError as e:
        return str(e)
    return None


def addendum_checks():
    """Rules the campaign addendum states in words (sections 5 to 9). Each
    check comes with a mutant that removes the rule and must turn it red."""
    out = []
    # Section 8: A's first window follows N on A's IP with another port, its second follows O on another IP.
    schedule = {"N": [0, 1, 2, 3], "A": [4, 5, 6, 7, 12, 13, 14, 15], "O": [8, 9, 10, 11]}
    tpu = {"A": "10.0.0.1:8009", "N": "10.0.0.1:9007", "O": "10.0.0.2:8009"}

    def windows_of_a():
        return [(first, passes) for first, _, leader, passes in panel.scan(schedule, 1000, tpu) if leader == "A"]

    want = [(1004, False), (1012, True)]
    got = windows_of_a()
    whole = _patched(panel, "_shared_tpu_before",
                     lambda prev, leader, t: prev not in (None, leader) and t.get(prev) == t.get(leader), windows_of_a)
    out.append(("addendum: a window right after another validator on the leader's IP fails whatever the port; "
                "the mutant comparing the whole address lets it pass",
                got == want and whole != want, "%s; mutant %s" % (got, whole)))

    # Section 8: the manifest pins the panel by its sha256.
    with tempfile.TemporaryDirectory() as tmp:
        pinned_path, other_path = os.path.join(tmp, "pinned.json"), os.path.join(tmp, "other.json")
        for path, body in ((pinned_path, b'{"epoch": 1071}\n'), (other_path, b'{"epoch": 1071} \n')):
            with open(path, "wb") as f:
                f.write(body)
        doc = {"files": {"data/panels/x/panel.json": verify.sha256_file(pinned_path),
                         "prereg/ANALYSIS-PLAN.md": "00"}}
        same = verify.panel_pin_problem(doc, pinned_path)
        other = verify.panel_pin_problem(doc, other_path)
        none = verify.panel_pin_problem({"files": {"prereg/ANALYSIS-PLAN.md": "00"}}, pinned_path)
        mutant = _patched(verify, "sha256_file", lambda path: doc["files"]["data/panels/x/panel.json"],
                          lambda: verify.panel_pin_problem(doc, other_path))
    out.append(("addendum: a campaign plan takes the pinned panel and refuses one with another hash or a "
                "manifest without a panel; the mutant that skips the hash takes the other panel",
                same is None and other is not None and "hashes" in other and none is not None and mutant is None,
                "%s; %s; mutant %s" % (same, other, mutant)))

    # Section 5: index e runs only in chain epoch panel epoch + e; once that epoch has passed the
    # index draws no more rounds, and its rounds that have not run are lost.
    doc = {"epoch": 1071, "network": "mainnet", "classes": {}}

    def draw(index, epoch, now):
        return _raises(lambda: campaign.draw(_EpochClient(now), doc, {"epochs": [], "seed": "s"}, "aa", "bb",
                                             index, epoch, 150))

    moved = draw(1, 1071, 1071)
    passed = draw(0, 1071, 1072)
    own = draw(1, 1072, 1072)
    out.append(("addendum: the draw refuses index 1 in chain epoch 1071 and index 0 once epoch 1071 has passed; "
                "index 1 in epoch 1072 gets past both gates",
                moved is not None and "runs only in chain epoch 1072" in moved
                and passed is not None and "has passed" in passed and "rounds that have not run are lost" in passed
                and own is not None and "not known yet" in own,
                "%s; %s; %s" % (moved, passed, own)))

    # Sections 5 and 7 on synthetic runs: FireBAM against Firedancer, 8 rounds in both different-fee arms.
    spec = []
    for rnd in range(8):
        for arm in ("independent", "shared"):
            spec.append({"class": "FireBAM", "rule": "fifo", "arm": arm, "timing": "pre300", "round": rnd,
                         "tick": rnd >= 2})
            spec.append({"class": "Firedancer", "rule": "firedancer", "arm": arm, "timing": "pre300",
                         "round": rnd, "leader": 1})

    def analyze_spec(rows_spec, name):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = os.path.join(tmp, "runs", name)
            os.makedirs(run_dir)
            prows, crows = synth.campaign_rows(name, rows_spec, "itb-selftest:" + name)
            _write(os.path.join(run_dir, "probes.jsonl"), prows)
            _write(os.path.join(run_dir, "collect.jsonl"), crows)
            runs = analyze.load_runs(tmp)
        return lambda: analyze.analyze(runs, stages=("test",))

    def fee_rows(result):
        rows = [r for r in result["pairs"] if r["pair"] == ["FireBAM", "Firedancer"]
                and r["timing"] == "pre300" and r["tau"] == "fee"]
        tested = next((r["strata"] for r in rows if not r.get("without_label")), None)
        bare = next((r for r in rows if r.get("without_label")), {})
        return tested, bare.get("strata"), bare.get("form"), "p" in bare

    run = analyze_spec(spec, "selftest-tick")
    got = fee_rows(run())
    whole = fee_rows(_patched(analyze, "builder_blocks", lambda unit, cls, labelled=True: unit.blocks, run))
    out.append(("addendum: the pair test takes the FireBAM blocks with the BAM tick (12 strata) and shows the "
                "4 without it as a descriptive row; the mutant without the filter tests all 16",
                got == (12, 4, "descriptive", False) and whole[0] == 16, "%s; mutant %s" % (got, whole)))

    # Section 9: the control burst of round 0 lands outside its window; the inclusion share keeps it at 0.
    control_spec = [{"class": "FireBAM", "rule": "fifo", "arm": "independent", "timing": "pre300", "round": rnd,
                     "fields": {"path": path}} for rnd in range(3) for path in ("quic", "rpc")]
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = os.path.join(tmp, "runs", "selftest-control")
        os.makedirs(run_dir)
        prows, crows = synth.campaign_rows("selftest-control", control_spec, "itb-selftest:control")
        for r in crows:
            if r["kind"] == "inclusion" and r["burst_seq"] == 1:
                r["in_target_window"] = False
        _write(os.path.join(run_dir, "probes.jsonl"), prows)
        _write(os.path.join(run_dir, "collect.jsonl"), crows)
        items = report._items(analyze.load_runs(tmp))
        control = report.control_block(items)
        narrow = dict(report.CONTROL_KEEPS, **{"inclusion share": {"control-path"}})
        mutant = _patched(report, "CONTROL_KEEPS", narrow, lambda: report.control_block(items))
    out.append(("addendum: the control inclusion share counts a control burst that missed its window as 0; "
                "the mutant that drops such bursts reads no difference",
                "| inclusion share | 1 | -0.333 |" in control and "| tau fee | 1 |" in control
                and "| inclusion share | 1 | 0.000 |" in mutant,
                "%s; mutant %s" % (control.split("\n")[2], mutant.split("\n")[2])))

    twice = analyze_spec(spec[:2] + spec[:1], "selftest-repeat")
    res = twice()
    got = (res["units"], res["excluded"].get("repeated-burst", 0))
    res_m = _patched(analyze, "later_copies", lambda runs, stages=None: frozenset(), twice)
    mut = (res_m["units"], res_m["excluded"].get("repeated-burst", 0))
    out.append(("addendum: a table burst sent twice keeps its earliest send and the later copy leaves the tests "
                "with the reason repeated-burst; the mutant without the rule keeps both",
                got == (3, 1) and mut == (3, 0), "%s; mutant %s" % (got, mut)))

    # Section 7: a BAM tick in a Firedancer slot fails the BAM label; the FireBAM pair keeps its tests in the
    # family of 16 with p 1 and reads as a failed label.
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = os.path.join(tmp, "runs", "selftest-label")
        os.makedirs(run_dir)
        prows, crows = synth.campaign_rows("selftest-label", spec, "itb-selftest:label")
        fd_slot = min(r["slot"] for r in crows if r["kind"] == "inclusion" and r["actual_leader_class"] == "Firedancer")
        for r in crows:
            if r["kind"] == "slot" and r["slot"] == fd_slot:
                r["ticks"] = [{"index": 0, "signer": analyze.BAM_SIGNER, "timestamp_ns": 1793044800 * 10 ** 9,
                               "interval_ns": 50_000_000}]
        _write(os.path.join(run_dir, "probes.jsonl"), prows)
        _write(os.path.join(run_dir, "collect.jsonl"), crows)
        label_runs = analyze.load_runs(tmp)

    def label_rows():
        result = analyze.analyze(label_runs, stages=("test",))
        rows = [r for r in result["pairs"] if r["pair"] == ["FireBAM", "Firedancer"] and r["strata"]
                and not r.get("without_label")]
        return sorted({(r["form"], r["p"], r["tost_p"]) for r in rows}), result["label_failures"]

    got = label_rows()
    mut = _patched(analyze, "label_failures", lambda runs, stages=None: {}, label_rows)
    out.append(("addendum: a BAM tick in a Firedancer slot fails the BAM label and the FireBAM pair keeps its "
                "tests with p 1 as builder-label-failed; the mutant without the label check tests the pair",
                got == ([("builder-label-failed", 1.0, 1.0)], {analyze.BAM_SIGNER: [fd_slot]})
                and mut[0] and all(form != "builder-label-failed" for form, _, _ in mut[0]),
                "%s; mutant %s" % (got, mut)))

    # Section 7 over every slot row: a BAM tick in a Firedancer slot that holds no included probe fails the
    # label too, since a slot takes the class gossip showed for its leader at the burst; the copy of
    # analyze.py that classes slots by their included probes misses it. REPORT's tick table counts that
    # slot under Firedancer, and the copy of report.py that classes slots by included probes does not.
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = os.path.join(tmp, "runs", "selftest-label-quiet")
        os.makedirs(run_dir)
        prows, crows = synth.campaign_rows("selftest-label-quiet", spec, "itb-selftest:label-quiet")
        fd = next(r for r in prows if r["kind"] == "burst" and r["leader_client_id"] == "Firedancer")
        taken = {r["slot"] for r in crows if r["kind"] == "slot"}
        quiet = next(s for s in range(fd["first_slot"], fd["first_slot"] + fd["window_len"]) if s not in taken)
        crows.append(synth.slot_row("selftest-label-quiet", quiet, fd["leader"], ticks=[{
            "index": 0, "signer": analyze.BAM_SIGNER, "timestamp_ns": 1793044800 * 10 ** 9,
            "interval_ns": 50_000_000}]))
        _write(os.path.join(run_dir, "probes.jsonl"), prows)
        _write(os.path.join(run_dir, "collect.jsonl"), crows)
        quiet_runs = analyze.load_runs(tmp)
    by_probe = _module_copy("analyze", "        cls_of, _ = slot_classes(run)\n",
                            "        cls_of = {}\n"
                            "        for inc in run.inclusions.values():\n"
                            "            if inc[\"status\"] == \"included\" and inc[\"slot\"] is not None:\n"
                            "                cls_of[inc[\"slot\"]] = inc.get(\"actual_leader_class\")\n")
    got = analyze.label_failures(quiet_runs)
    mut = by_probe["label_failures"](quiet_runs)
    out.append(("addendum: a BAM tick in a Firedancer slot without an included probe fails the BAM label by the "
                "class of the slot's leader; the copy of analyze.py that classes slots by included probes misses it",
                got == {analyze.BAM_SIGNER: [quiet]} and mut == {}, "%s; mutant %s" % (got, mut)))

    for r in quiet_runs:
        r.run.update(mode="live", network="mainnet")

    def tick_cells(text, cls):
        row = next((line for line in text.split("\n") if line.startswith("| `") and "| %s |" % cls in line), "")
        return [c.strip() for c in row.split("|")[4:7]]

    ticks = report.tick_runs_block(quiet_runs)
    ticks_m = _module_copy("report", "cls_of, unknown = analyze.slot_classes(r)",
                           "cls_of, unknown = {i[\"slot\"]: i[\"actual_leader_class\"] for i in _included(r)}, []"
                           )["tick_runs_block"](quiet_runs)
    fd_cells, bam_cells, fd_cells_m = tick_cells(ticks, "Firedancer"), tick_cells(ticks, "FireBAM"), \
        tick_cells(ticks_m, "Firedancer")
    out.append(("addendum: REPORT's tick table gives each class of the slot's leader its own share and counts the "
                "BAM tick of the Firedancer slot without an included probe; the copy that classes slots by included "
                "probes leaves that slot out",
                bool(fd_cells) and fd_cells[1].startswith("1 (") and bool(bam_cells) and bam_cells[1] != "0 (0.0%)"
                and bool(fd_cells_m) and fd_cells_m[1].startswith("0 (") and int(fd_cells_m[0]) == int(fd_cells[0]) - 1
                and "left out because no burst row names their leader" in ticks,
                "Firedancer %s, FireBAM %s; mutant Firedancer %s" % (fd_cells, bam_cells, fd_cells_m)))

    # Section 7: a pair whose label failed reads builder-label-failed even with no strata; the copy of
    # analyze.py without that rule reads such rows undetermined.
    def empty_forms(analyze_fn):
        result = analyze_fn(label_runs, stages=("test",))
        return sorted({(r["pair"][0], r["form"]) for r in result["pairs"]
                       if not r["strata"] and not r.get("without_label")})

    empty = empty_forms(analyze.analyze)
    empty_m = empty_forms(_module_copy("analyze", "                    if BUILDER_SIGNER.get(a) in failed:\n"
                                                  "                        row[\"label_failed\"] = "
                                                  "failed[BUILDER_SIGNER[a]]\n", "")["analyze"])
    builder_bam = [(c, f) for c, f in empty if c in ("AgaveBam", "FireBAM")]
    out.append(("addendum: a pair with a failed label and no strata reads builder-label-failed; the copy without "
                "the rule reads it undetermined",
                bool(builder_bam) and all(f == "builder-label-failed" for _, f in builder_bam)
                and all(f == "undetermined" for c, f in empty_m if c in ("AgaveBam", "FireBAM")),
                "%s; mutant %s" % (builder_bam, empty_m)))

    # Section 3: the load split of REPORT reads Agave's equal-fee arm in the pre-window condition only
    # (plan line 79); the copy of report.py without the timing filter also takes Agave's slot2 bursts.
    fake_run = types.SimpleNamespace(slots={s: {"cost_units": 1000 * s, "tx_count": s} for s in range(1, 9)})
    fake = [report.Item(fake_run, types.SimpleNamespace(
        burst={"selection_class": cls, "timing": timing, "arm": "equal_fee"}, reasons=[], blocks=[],
        run_id="selftest-loads", burst_seq=s), [s])
        for s, (cls, timing) in enumerate([("Agave", "pre300"), ("Agave", "slot2")] * 3
                                          + [("Firedancer", "pre300"), ("Agave", "pre300")], start=1)]

    def agave_column(ns):
        seen, real = [], ns["_arms"]

        def arms(items, which):
            seen.append({(it.unit.burst["selection_class"], it.unit.burst["timing"]) for it in items})
            return real(items, which)

        saved = ns["_arms"], ns["_pooled"]
        ns["_arms"], ns["_pooled"] = arms, lambda bursts, name: None
        try:
            ns["loads_block"](fake)
        finally:
            ns["_arms"], ns["_pooled"] = saved
        return set().union(*seen[2::3]) if seen else set()

    cells = agave_column(_module_copy("report"))
    cells_m = agave_column(_module_copy("report", '\n                     and it.unit.burst["timing"] == "pre300"]',
                                        "]"))
    out.append(("addendum: the Agave column of REPORT's load split takes Agave's pre300 bursts only; the copy "
                "without the timing filter also takes slot2",
                cells == {("Agave", "pre300")} and ("Agave", "slot2") in cells_m,
                "%s; mutant %s" % (sorted(cells), sorted(cells_m))))

    # Section 6: with a standard error of zero the TOST of the code gives p 0 when the difference lies inside
    # plus or minus delta and 1 otherwise, so a pair with zero spread inside delta reads as
    # builder-does-not-change-order, as the pilot's FireBAM against Firedancer did; df below 1 or a NaN
    # standard error give 1.
    d = verdict.DELTA_PAIR

    def pair_forms():
        res = []
        for diffs in ([0.0, 0.0], [d / 2, d / 2], [d, d], [2 * d, 2 * d]):
            p, _, _, _, _, _, tost = verdict.pair_test(diffs, seed=prereg.LABEL_TEST_SEED)
            sig = verdict.holm_decisions({"k": p}, m=verdict.PAIR_FAMILY_M)["k"]
            eq = verdict.holm_decisions({"k": tost}, m=verdict.PAIR_FAMILY_M)["k"]
            res.append((tost, verdict.pair_form(sig, eq)))
        return res

    same = "builder-does-not-change-order"
    want = [(0.0, same), (0.0, same), (1.0, "undetermined"), (1.0, "undetermined")]
    got = pair_forms()
    edges = (stats.tost_p(0.0, float("nan"), 3, d), stats.tost_p(0.0, 0.0, 0, d))
    rule = "return 0.0 if -delta < theta < delta else 1.0"
    wide = _patched(stats, "tost_p", _module_copy("stats", rule, "return 0.0")["tost_p"], pair_forms)
    never = _patched(stats, "tost_p", _module_copy("stats", rule, "return 1.0")["tost_p"], pair_forms)
    out.append(("addendum: at zero spread the pair TOST gives 0 inside delta and 1 at or past it, and 1 at df 0 or "
                "a NaN error; the mutant without delta passes 2 delta, the mutant without the rule fails 0",
                got == want and edges == (1.0, 1.0) and wide[3][1] == same and never[0][1] == "undetermined",
                "%s; %s; mutants %s, %s" % (got, edges, wide[3], never[0])))

    # Section 5: a plan drawn again scans the windows with the gossip snapshot it is given (--nodes), not
    # live gossip that has moved a leader since the first plan.
    snapshot = {"utc": "2026-10-28T00:00:00Z", "nodes": [{"pubkey": "A", "tpuQuic": "10.0.0.1:8009"}]}

    def scanned(draw_fn, nodes_doc):
        seen = []

        def scan(schedule, first, tpu):
            seen.append(dict(tpu))
            raise ValueError("selftest stops at the scan")

        _patched(panel, "scan", scan, lambda: _raises(lambda: draw_fn(
            _GossipClient(1071), doc, {"epochs": [], "seed": "s"}, "aa", "bb", 0, 1071, 150, nodes_doc=nodes_doc)))
        return seen[0] if seen else None

    live = scanned(campaign.draw, None)
    again = scanned(campaign.draw, snapshot)
    gossip = 'client.call("getClusterNodes", []) if nodes_doc is None else nodes_doc["nodes"]'
    mutant = scanned(_module_copy("campaign", gossip, 'client.call("getClusterNodes", [])')["draw"], snapshot)
    out.append(("addendum: a plan drawn again with --nodes scans the snapshot's address of the leader, not the "
                "live one; the mutant that ignores the snapshot scans the live address",
                live == {"A": "10.0.0.9:8009"} and again == {"A": "10.0.0.1:8009"} and mutant == live,
                "%s; %s; mutant %s" % (live, again, mutant)))

    # Sections 5 and 8 through the command: cmd_campaign refuses a panel the manifest does not pin and a
    # missing manifest before any draw, and --nodes-from-first-plan hands the draw the gossip of the first
    # plan of the index, chain epoch and manifest under data/plans.
    with tempfile.TemporaryDirectory() as tmp:
        def put(rel, obj):
            path = os.path.join(tmp, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                json.dump(obj, f)
                f.write("\n")
            return path

        panel_path = put("panel.json", {"epoch": 1071, "network": "mainnet", "classes": {}})
        other_panel = put("other-panel.json", {"epoch": 1071, "network": "mainnet", "classes": {}, "x": 1})
        manifest = put("manifest.json", {"files": {"data/panels/x/panel.json": verify.sha256_file(panel_path)}})
        absent = os.path.join(tmp, "absent.json")
        unplanned = put("manifest-unplanned.json", {"files": {"data/panels/x/panel.json":
                                                              verify.sha256_file(panel_path)}, "plans": 0})
        with open(manifest, "rb") as f:
            sha = pilot.sha256_bytes(f.read())
        for stamp, index, msha, utc in (("20261028T000000Z", 0, "ff" * 32, "another manifest"),
                                        ("20261028T010000Z", 1, sha, "another index"),
                                        ("20261028T020000Z", 0, sha, "first plan"),
                                        ("20261028T030000Z", 0, sha, "second plan")):
            plan_dir = os.path.join("plans", "campaign-mainnet-e1071-" + stamp)
            put(os.path.join(plan_dir, "draw-notes.json"), {"epoch_index": index, "epoch": 1071, "notes": []})
            put(os.path.join(plan_dir, "plan.json"), {"stage": "campaign", "prereg_manifest_sha256": msha})
            put(os.path.join(plan_dir, "cluster-nodes.json"), {"utc": utc, "nodes": []})

        def command(ns, panel_file, manifest_file, epoch_index=0, epoch=1071):
            got = {}

            def draw(client, panel_doc, table, table_sha, manifest_sha, epoch_index, epoch, lead_slots,
                     nodes_doc=None):
                got["nodes"] = nodes_doc["utc"] if nodes_doc else "live"
                raise ValueError("selftest stops before the chain")

            ns["_client"] = lambda: None
            args = argparse.Namespace(panel=panel_file, table=None, epoch_index=epoch_index, epoch=epoch,
                                      nodes=None,
                                      nodes_from_first_plan=True, manifest=manifest_file, lead_slots=900,
                                      data=tmp, network="mainnet")
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                code = _patched(campaign, "draw", draw, lambda: ns["cmd_campaign"](args))
            return code, got.get("nodes"), err.getvalue()

        main = _module_copy("__main__")
        resumed = command(main, panel_path, manifest)
        foreign = command(main, other_panel, manifest)
        missing = command(main, panel_path, absent)
        no_pin = command(_module_copy("__main__", "problem = verify.panel_pin_problem(json.loads(manifest_raw), "
                                                  "args.panel)", "problem = None"), other_panel, manifest)
        no_refusal = command(_module_copy("__main__", 'pins the panel" % manifest, file=sys.stderr)\n'
                                                      "        return EXIT_FAIL\n",
                                          'pins the panel" % manifest, file=sys.stderr)\n'), panel_path, absent,
                             epoch_index=2, epoch=1073)
        no_lookup = command(_module_copy("__main__", "if args.nodes_from_first_plan and not nodes:", "if False:"),
                            panel_path, manifest)
        index0 = command(main, panel_path, unplanned)
        index2 = command(main, panel_path, unplanned, epoch_index=2, epoch=1073)
        index0_m = command(_module_copy("__main__", 'the package carries it"\n'
                                                    '                  % os.path.join(_data_dir(args), "plans"), '
                                                    'file=sys.stderr)\n            return EXIT_FAIL\n',
                                        'the package carries it"\n'
                                        '                  % os.path.join(_data_dir(args), "plans"), '
                                        'file=sys.stderr)\n'), panel_path, unplanned)
    out.append(("addendum: cmd_campaign refuses a panel the manifest does not pin and a missing manifest before "
                "any draw; the copies of __main__.py without the pin check or without the refusal reach the draw",
                foreign[:2] == (1, None) and "hashes" in foreign[2] and missing[:2] == (1, None)
                and "not found" in missing[2] and no_pin[1] is not None and no_refusal[1] is not None,
                "%s; %s; mutants %s, %s" % (foreign[:2], missing[:2], no_pin[1], no_refusal[1])))
    out.append(("addendum: cmd_campaign --nodes-from-first-plan hands the draw the gossip of the first plan of "
                "the index, chain epoch and manifest; the copy without the lookup draws with live gossip",
                resumed[1] == "first plan" and no_lookup[1] == "live", "%s; mutant %s" % (resumed[1], no_lookup[1])))
    out.append(("addendum: the draw of epoch index 0 refuses without a first plan of that index under the manifest, "
                "while index 2 draws with live gossip; the copy without the refusal draws index 0 live",
                index0[:2] == (1, None) and "no first plan" in index0[2] and index2[1] == "live"
                and index0_m[1] == "live", "%s; index 2 %s; mutant %s" % (index0[:2], index2[1], index0_m[1])))
    return out


def run_all():
    """Run every selftest group; return (passed, failed, lines)."""
    checks = (raw_format_checks() + stats_checks() + min_p_checks() + synthetic_checks()
              + end_to_end_checks() + chain_checks() + collect_checks() + prereg_checks() + plan_checks()
              + panel_checks()
              + pilot_checks()
              + campaign_checks()
              + rounds_checks()
              + timing_checks()
              + clock_guard_checks()
              + channel_checks()
              + rpc_checks()
              + report_checks()
              + addendum_checks())
    lines = []
    failed = 0
    for name, ok, detail in checks:
        lines.append("%s  %s%s" % ("PASS" if ok else "FAIL", name, ("  (" + detail + ")") if detail else ""))
        if not ok:
            failed += 1
    return len(checks) - failed, failed, lines
