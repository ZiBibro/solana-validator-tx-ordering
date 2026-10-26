"""Selftest: checks with known answers that run before verify (section 9).

Each check returns (name, ok, detail). A failed check stops reproduce before
verify starts.
"""

import copy
import itertools
import json
import math
import os
import random
import tempfile
from fractions import Fraction

from . import analyze, b58, rawformat, stats, synth, verdict


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


def run_all():
    """Run every selftest group; return (passed, failed, lines)."""
    checks = (raw_format_checks() + stats_checks() + min_p_checks() + synthetic_checks()
              + end_to_end_checks())
    lines = []
    failed = 0
    for name, ok, detail in checks:
        lines.append("%s  %s%s" % ("PASS" if ok else "FAIL", name, ("  (" + detail + ")") if detail else ""))
        if not ok:
            failed += 1
    return len(checks) - failed, failed, lines
