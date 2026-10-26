"""Selftest: checks with known answers that run before verify (section 9).

Each check returns (name, ok, detail). A failed check stops reproduce before
verify starts.
"""

import copy
import gzip
import itertools
import json
import math
import os
import random
import tempfile
from fractions import Fraction

from . import analyze, b58, collect, fakechain, plan, rawformat, rpc, stats, synth, verdict, verify


def sample_run(burst_seq=7, n=12):
    """A valid probes.jsonl of one burst, built from the format rules."""
    run = synth.run_row("selftest")
    fees = [0, 10, 100, 1000] * 3
    probes = [{"send_rank": r, "fee": fees[r], "cu_limit": 1000} for r in range(n)]
    return [run] + synth.burst_rows(run, burst_seq, probes)


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
        ("schema version", edit(lambda m: m[1].__setitem__("v", 2))),
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
    out.append(("end to end: the burst with another client drops out",
                result["excluded"] == {"client-differs-from-selection": 1} and result["kept"] == len(plan) - 1,
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
    return out


def run_all():
    """Run every selftest group; return (passed, failed, lines)."""
    checks = (raw_format_checks() + stats_checks() + min_p_checks() + synthetic_checks()
              + end_to_end_checks() + chain_checks() + plan_checks() + timing_checks())
    lines = []
    failed = 0
    for name, ok, detail in checks:
        lines.append("%s  %s%s" % ("PASS" if ok else "FAIL", name, ("  (" + detail + ")") if detail else ""))
        if not ok:
            failed += 1
    return len(checks) - failed, failed, lines
