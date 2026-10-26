"""Burst statistics, class tests and verdict forms of section 10.

A burst enters as a list of blocks, and a block as the list of the burst's
probes that landed in one block of the target window, each a dict with pos
(any sortable block position), fee (priority fee in lamports), send_rank and
cu_limit. Positions count only inside a block (section 6), the exact null of a
burst is the convolution over its blocks, and the jackknife leaves out whole
bursts. Every tau is signed so that the rule it looks for reads positive:

  fee    tau(fee, -position): higher fee earlier in the block is positive.
  cross  send order against position over pairs with different fee.
  ties   the same over pairs with equal fee; descriptive, gives the subform.
  send   send order against position over all pairs; only where every fee is
         equal (equal-fee arm, denominator arm).
  limit  tau(cu_limit, position): division of the fee by the requested limit
         puts the low limit first and reads positive.

Families. The verdict family holds one exact permutation test per tau of the
six verdict slots (fee and cross of the independent and the shared arm, send
of the equal-fee arm, limit of the denominator arm) per class and moment
condition: 8 x 2 x 6 = 96 tests. The equivalence family has the same
composition: one TOST per tau of those slots, 96 tests; "no rule visible"
needs both of its taus rejected there and "does not divide" its limit tau.
The class-pair family has 16 tests (4 pairs x 2 moment conditions x 2 taus),
its equivalence family the same 16.
"""

import math
from collections import namedtuple
from fractions import Fraction

from . import prereg, stats

VERDICT_FAMILY_M = 96
EQUIV_FAMILY_M = 96
PAIR_FAMILY_M = 16

VERDICT_SLOTS = {
    "independent": ("fee", "cross"),
    "shared": ("fee", "cross"),
    "equal_fee": ("send",),
    "denominator": ("limit",),
}

DELTA_CLASS = prereg.DELTA_CLASS
DELTA_PAIR = prereg.DELTA_PAIR
POWER_PER_TAU = prereg.POWER_PER_TAU
# Ties subform is descriptive, outside every Holm family.
ALPHA_DESCRIPTIVE = Fraction(5, 100)

Piece = namedtuple("Piece", "s d key")
TauResult = namedtuple("TauResult", "name bursts s p tau se df low high tost_p mean_burst_tau")


def _sign(v):
    return (v > 0) - (v < 0)


def _tie_pairs(values):
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    return sum(c * (c - 1) // 2 for c in counts.values()), tuple(sorted(counts.values()))


def _pattern(values):
    """Equality structure only: relabel values by first appearance."""
    seen = {}
    return tuple(seen.setdefault(v, len(seen)) for v in values)


def burst_pieces(probes):
    """Per-burst S, denominator and null key of every tau the burst defines."""
    pr = sorted(probes, key=lambda p: p["pos"])
    n = len(pr)
    if n < 2:
        return {}
    fee = [p["fee"] for p in pr]
    send = [p["send_rank"] for p in pr]
    lim = [p["cu_limit"] for p in pr]
    idx = list(range(n))
    n0 = n * (n - 1) // 2
    out = {}
    fee_ties, fee_sizes = _tie_pairs(fee)
    if len(fee_sizes) > 1:
        s_fee = stats.pair_s(fee, [-i for i in idx])
        out["fee"] = Piece(s_fee, math.sqrt((n0 - fee_ties) * n0), ("sizes", fee_sizes))
        s_cross = 0
        s_ties = 0
        for i in range(n):
            for j in range(i + 1, n):
                v = _sign(send[j] - send[i])
                if fee[i] != fee[j]:
                    s_cross += v
                else:
                    s_ties += v
        out["cross"] = Piece(s_cross, n0 - fee_ties, ("cross", _pattern(fee)))
        if fee_ties:
            groups = tuple(sorted(c for c in fee_sizes if c > 1))
            out["ties"] = Piece(s_ties, fee_ties, ("groups", groups))
    else:
        out["send"] = Piece(stats.pair_s(send, idx), n0, ("sizes", (1,) * n))
    lim_ties, lim_sizes = _tie_pairs(lim)
    if len(lim_sizes) > 1:
        out["limit"] = Piece(stats.pair_s(lim, idx), math.sqrt((n0 - lim_ties) * n0),
                             ("sizes", lim_sizes))
    return out


_NULLS = {}


def null_of(key):
    """Exact null of a burst statistic, cached by its key (section 10)."""
    if key not in _NULLS:
        kind, arg = key
        if kind == "sizes":
            _NULLS[key] = stats.null_ties_sizes(arg)
        elif kind == "cross":
            _NULLS[key] = stats.null_cross(arg)
        elif kind == "groups":
            _NULLS[key] = stats.convolve(stats.null_ties_sizes((1,) * g) for g in arg)
        else:
            raise ValueError("unknown null kind " + kind)
    return _NULLS[key]


def class_test(name, bursts, delta=DELTA_CLASS):
    """Exact test of the summed S, pooled tau with jackknife interval and TOST.

    bursts: one list of Pieces per burst, one Piece per block.
    """
    bursts = [b for b in bursts if b]
    if not bursts:
        return None
    dist = stats.convolve(null_of(p.key) for b in bursts for p in b)
    pairs = [(sum(p.s for p in b), sum(p.d for p in b)) for b in bursts]
    s = sum(x for x, _ in pairs)
    tau, se, df = stats.jackknife(pairs)
    low, high = stats.interval(tau, se, df)
    mean_tau = sum(x / d for x, d in pairs) / len(pairs)
    return TauResult(name, len(bursts), s, stats.p_two_sided(dist, s), tau, se, df, low, high,
                     stats.tost_p(tau, se, df, delta), mean_tau)


def burst_tau(blocks, name):
    """Tau of one burst over its blocks, or None when the burst does not define it."""
    s = d = 0
    for block in blocks:
        piece = burst_pieces(block).get(name)
        if piece is not None:
            s += piece.s
            d += piece.d
    return s / d if d else None


def cell_results(bursts, delta=DELTA_CLASS):
    """All tau results of one class and cell (arm and moment condition).

    bursts: list of bursts, each a list of blocks, each a list of probes.
    """
    per = {}
    for blocks in bursts:
        mine = {}
        for block in blocks:
            for name, piece in burst_pieces(block).items():
                mine.setdefault(name, []).append(piece)
        for name, pieces in mine.items():
            per.setdefault(name, []).append(pieces)
    return {name: class_test(name, pieces, delta) for name, pieces in per.items()}


def min_attainable_p(keys):
    """Smallest two-sided p of the summed statistic over bursts with these nulls."""
    return stats.min_p_two_sided(stats.convolve(null_of(k) for k in keys))


# ---------------------------------------------------------------- forms

def ties_subform(ties):
    if ties is None or ties.p > ALPHA_DESCRIPTIVE:
        return "ties-unordered"
    return "ties-arrival" if ties.s > 0 else "ties-reverse-arrival"


def form_different_fee(sig_fee, fee_tau, sig_cross, cross_tau, equivalent, ties=None):
    """Six forms for the independent and the shared arm."""
    if sig_fee and fee_tau < 0:
        return "inverted-fee", None
    if sig_fee and sig_cross:
        return "mixed-rule", None
    if sig_fee:
        return "fee-rule", ties_subform(ties)
    if sig_cross:
        return "arrival-rule", "forward" if cross_tau > 0 else "reverse"
    if equivalent:
        return "no-rule-visible", None
    return "undetermined", None


def form_equal_fee(sig_send, send_tau, equivalent):
    """Equal-fee arm: tau send stands in the place of tau cross."""
    if sig_send:
        return "arrival-rule", "forward" if send_tau > 0 else "reverse"
    if equivalent:
        return "no-rule-visible", None
    return "undetermined", None


def form_denominator(sig_limit, limit_tau, equivalent):
    if sig_limit:
        return ("divides", None) if limit_tau > 0 else ("inverted", None)
    if equivalent:
        return "does-not-divide", None
    return "undetermined", None


def cell_form(arm, results, sig, eq):
    """Form of one class and cell given the Holm decisions.

    sig[name] and eq[name] are booleans from the verdict and the equivalence
    family; results come from cell_results.
    """
    r = results
    if arm in ("independent", "shared"):
        if "fee" not in r or "cross" not in r:
            return "undetermined", "no burst with two fee levels"
        return form_different_fee(sig["fee"], r["fee"].tau, sig["cross"], r["cross"].tau,
                                  eq["fee"] and eq["cross"], r.get("ties"))
    if arm == "equal_fee":
        if "send" not in r:
            return "undetermined", "no burst with equal fee"
        return form_equal_fee(sig["send"], r["send"].tau, eq["send"])
    if arm == "denominator":
        if "limit" not in r:
            return "undetermined", "no burst with two limits"
        return form_denominator(sig["limit"], r["limit"].tau, eq["limit"])
    raise ValueError("unknown arm " + arm)


def cell_form_at_first_threshold(arm, results, alpha=stats.ALPHA,
                                 m_verdict=VERDICT_FAMILY_M, m_equiv=EQUIV_FAMILY_M):
    """Form of a single cell judged at the first Holm threshold of each family.

    This is the strictest step of Holm, so a form found here survives any
    position in the family; selftest uses it on synthetic cells.
    """
    a_v = alpha / m_verdict
    a_e = alpha / m_equiv
    sig = {name: res.p <= a_v for name, res in results.items()}
    eq = {name: res.tost_p <= a_e for name, res in results.items()}
    return cell_form(arm, results, sig, eq)


def holm_decisions(tests, alpha=stats.ALPHA, m=None):
    """tests: {key: p}. Holm over the family; m pads the family to its planned size
    when some tests are missing, which only makes the correction stricter."""
    keys = list(tests)
    pvals = [tests[k] for k in keys]
    if m is not None and m > len(pvals):
        pvals = pvals + [1] * (m - len(pvals))
    rej = stats.holm(pvals, alpha)
    return {k: rej[i] for i, k in enumerate(keys)}


# ---------------------------------------------------------------- class pairs

def pair_test(diffs, seed=None, delta=DELTA_PAIR):
    """Difference of a tau between the two classes of a pair, one diff per stratum.

    Returns (p_label, method, b_used, mean, se, df, tost_p).
    """
    p, method, b_used = stats.paired_label_test(diffs, seed=seed)
    k = len(diffs)
    mean = sum(diffs) / k if k else float("nan")
    if k >= 2:
        var = sum((d - mean) ** 2 for d in diffs) / (k - 1)
        se = math.sqrt(var / k)
        df = k - 1
    else:
        se, df = float("nan"), 0
    return p, method, b_used, mean, se, df, stats.tost_p(mean, se, df, delta)


def pair_form(sig, equivalent):
    if sig:
        return "builder-changes-order"
    if equivalent:
        return "builder-does-not-change-order"
    return "undetermined"


def min_bursts_formula(sigma, delta=DELTA_CLASS, alpha=stats.ALPHA, m_equiv=EQUIV_FAMILY_M,
                       power=POWER_PER_TAU):
    """Minimum bursts per class and cell for "no rule visible" (section 10)."""
    return stats.min_bursts(sigma, delta, float(alpha) / m_equiv, power)
