"""Statistics of section 10, standard library only.

Every permutation p-value here is an exact fraction: the null distribution of
the burst statistic S is counted exactly (Mahonian numbers, q-multinomial
coefficients, or a dynamic programme over subsets for the cross tau), the
class statistic is the sum of S over bursts, and the sum's distribution is the
convolution of the burst distributions in integers. Random permutations appear
only in label-permutation tests with more than 20 strata.
"""

import math
import random
from fractions import Fraction

ALPHA = Fraction(5, 100)


def _sign(v):
    return (v > 0) - (v < 0)


# ---------------------------------------------------------------- burst statistics

def pair_s(x, y, include=None):
    """S = sum over pairs i<j of sign(x_i - x_j) * sign(y_i - y_j).

    include(i, j) -> bool restricts the pairs (cross tau: pairs with different fee).
    """
    n = len(x)
    s = 0
    for i in range(n):
        for j in range(i + 1, n):
            if include is not None and not include(i, j):
                continue
            s += _sign(x[i] - x[j]) * _sign(y[i] - y[j])
    return s


def tau_b(x, y):
    """Kendall tau-b and its pieces: (tau, S, denominator)."""
    n = len(x)
    n0 = n * (n - 1) // 2
    n1 = sum(c * (c - 1) // 2 for c in _counts(x).values())
    n2 = sum(c * (c - 1) // 2 for c in _counts(y).values())
    s = pair_s(x, y)
    d = math.sqrt((n0 - n1) * (n0 - n2))
    return (s / d if d else float("nan")), s, d


def _counts(values):
    out = {}
    for v in values:
        out[v] = out.get(v, 0) + 1
    return out


# ---------------------------------------------------------------- exact nulls

def _poly_mul(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                out[i + j] += ai * bj
    return out


_QBINOM = {}


def q_binomial(n, k):
    """Coefficients of the Gaussian binomial [n choose k]_q (index = power of q)."""
    if k < 0 or k > n:
        return [0]
    if k == 0 or k == n:
        return [1]
    key = (n, k)
    if key not in _QBINOM:
        a = q_binomial(n - 1, k - 1)
        b = [0] * k + q_binomial(n - 1, k)
        size = max(len(a), len(b))
        _QBINOM[key] = [(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)
                        for i in range(size)]
    return _QBINOM[key]


def inversion_dist(tie_sizes):
    """Inversions of a random arrangement of a multiset with the given tie sizes.

    Product of q-binomials = q-multinomial; all sizes 1 gives the Mahonian numbers.
    """
    poly = [1]
    total = 0
    for k in tie_sizes:
        total += k
        poly = _poly_mul(poly, q_binomial(total, k))
    return poly


def null_ties(x):
    """Exact null of S for x against distinct positions: {S: count}."""
    return null_ties_sizes(list(_counts(x).values()))


def null_ties_sizes(sizes):
    """Same null from the tie sizes alone.

    Pairs with distinct x number P; S = P - 2 * discordant pairs, and the number
    of discordant pairs follows the q-multinomial of the tie sizes.
    """
    sizes = list(sizes)
    n = sum(sizes)
    p = n * (n - 1) // 2 - sum(c * (c - 1) // 2 for c in sizes)
    return {p - 2 * inv: cnt for inv, cnt in enumerate(inversion_dist(sizes)) if cnt}


def _lane_bytes(max_count):
    return max_count.bit_length() // 8 + 1


def _unpack(packed, lane_bytes, offset):
    """Split a big integer of byte-aligned lanes into {exponent + offset: count}."""
    raw = packed.to_bytes((packed.bit_length() + 7) // 8 or 1, "little")
    out = {}
    for e in range(0, len(raw), lane_bytes):
        cnt = int.from_bytes(raw[e:e + lane_bytes], "little")
        if cnt:
            out[e // lane_bytes + offset] = cnt
    return out


def null_cross(fee_by_position):
    """Exact null of S_cross under a random permutation of send ranks.

    fee_by_position lists the fee level of each probe in block-position order.
    S_cross = sum over pairs with different fee of sign(send_j - send_i) * sign(pos_j - pos_i).
    Send ranks are assigned in increasing order over subsets (2^n states); adding
    probe j after the set A contributes sum over i in A with a different fee of
    sign(j - i). Counts are packed as lanes of one big integer per state, with the
    exponent offset so that every increment is non-negative.
    """
    fee = list(fee_by_position)
    n = len(fee)
    lane_bytes = _lane_bytes(math.factorial(n))
    width = 8 * lane_bytes
    dp = {0: 1}
    for size in range(n):
        nxt = {}
        for mask, poly in dp.items():
            for j in range(n):
                bit = 1 << j
                if mask & bit:
                    continue
                c = 0
                cnt = 0
                for i in range(n):
                    if mask >> i & 1 and fee[i] != fee[j]:
                        c += 1 if j > i else -1
                        cnt += 1
                shifted = poly << ((c + cnt) * width)
                nm = mask | bit
                nxt[nm] = nxt.get(nm, 0) + shifted
        dp = nxt
    p = sum(1 for i in range(n) for j in range(i + 1, n) if fee[i] != fee[j])
    return _unpack(dp[(1 << n) - 1], lane_bytes, -p)


def convolve(dists):
    """Distribution of the sum of independent statistics, exact counts.

    Each distribution becomes a polynomial packed into one big integer with lanes
    wide enough for the product of all totals, so integer products do the
    convolution without carries between lanes. The products run as a balanced
    tree, where big-integer multiplication is fastest.
    """
    dists = list(dists)
    total = 1
    offset = 0
    for d in dists:
        total *= sum(d.values())
        offset += min(d)
    lane_bytes = _lane_bytes(total)
    width = 8 * lane_bytes
    polys = []
    for d in dists:
        lo = min(d)
        poly = 0
        for s, c in d.items():
            poly |= c << ((s - lo) * width)
        polys.append(poly)
    if not polys:
        return {0: 1}
    while len(polys) > 1:
        polys = [polys[i] * polys[i + 1] if i + 1 < len(polys) else polys[i]
                 for i in range(0, len(polys), 2)]
    return _unpack(polys[0], lane_bytes, offset)


def p_two_sided(dist, observed):
    """P(|T| >= |observed|) as an exact fraction; the nulls here are symmetric."""
    total = sum(dist.values())
    tail = sum(c for s, c in dist.items() if abs(s) >= abs(observed))
    return Fraction(tail, total)


def min_p_two_sided(dist):
    """Smallest attainable two-sided p of a symmetric exact null."""
    top = max(abs(s) for s in dist)
    return p_two_sided(dist, top)


def moments(dist):
    total = sum(dist.values())
    mean = Fraction(sum(s * c for s, c in dist.items()), total)
    var = Fraction(sum(s * s * c for s, c in dist.items()), total) - mean * mean
    return mean, var


def cross_variance_analytic(fee_by_position):
    """Var(S_cross) under random send ranks, from pairwise sign covariances.

    With e_ij = [fee_i != fee_j] * sign(pos_i - pos_j) and s_ij = sign(r_i - r_j),
    S = sum_{i<j} e_ij s_ij. For a random permutation E[s_ij s_ij] = 1, two pairs
    sharing one index have E = +1/3 when the shared index sits on the same side
    and -1/3 otherwise, and disjoint pairs are uncorrelated.
    """
    fee = list(fee_by_position)
    n = len(fee)

    def e(i, j):
        return _sign(i - j) if fee[i] != fee[j] else 0

    var = Fraction(0)
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    for (i, j) in pairs:
        for (k, l) in pairs:
            w = e(i, j) * e(k, l)
            if not w:
                continue
            if (i, j) == (k, l):
                var += w
            elif i == k or j == l:
                var += Fraction(w, 3)
            elif i == l or j == k:
                var -= Fraction(w, 3)
    return var


# ---------------------------------------------------------------- Student t

def _betacf(a, b, x):
    """Continued fraction of the incomplete beta (modified Lentz)."""
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 1000):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-15:
            return h
    raise ArithmeticError("incomplete beta did not converge")


def betainc(a, b, x):
    """Regularized incomplete beta I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x)
    if x < (a + 1.0) / (a + b + 2.0):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbt) * _betacf(b, a, 1.0 - x) / b


def t_cdf(t, df):
    x = df / (df + t * t)
    tail = 0.5 * betainc(df / 2.0, 0.5, x)
    return 1.0 - tail if t > 0 else tail


def t_quantile(p, df):
    """Inverse of t_cdf by bisection; accurate to about 1e-12."""
    if not 0.0 < p < 1.0:
        raise ValueError("p must lie in (0, 1)")
    lo, hi = -1e6, 1e6
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if t_cdf(mid, df) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


# ---------------------------------------------------------------- class estimate

def pooled_tau(bursts):
    """bursts: list of (S, D). Pooled tau = sum S / sum D over pairs inside bursts."""
    ss = sum(s for s, _ in bursts)
    dd = sum(d for _, d in bursts)
    return ss / dd if dd else float("nan")


def jackknife(bursts, estimator=pooled_tau):
    """Leave-one-burst-out estimate: (theta, se, df). Needs at least two bursts."""
    b = len(bursts)
    if b < 2:
        return estimator(bursts), float("nan"), 0
    theta = estimator(bursts)
    loo = [estimator(bursts[:i] + bursts[i + 1:]) for i in range(b)]
    mean = sum(loo) / b
    var = (b - 1) / b * sum((v - mean) ** 2 for v in loo)
    return theta, math.sqrt(var), b - 1


def interval(theta, se, df, level=0.95):
    if df < 1 or math.isnan(se):
        return float("nan"), float("nan")
    q = t_quantile(0.5 + level / 2.0, df)
    return theta - q * se, theta + q * se


def tost_p(theta, se, df, delta):
    """Two one-sided tests against -delta and +delta; p is the larger one."""
    if df < 1 or math.isnan(se):
        return 1.0
    if se == 0:
        return 0.0 if -delta < theta < delta else 1.0
    p_low = 1.0 - t_cdf((theta + delta) / se, df)
    p_high = t_cdf((theta - delta) / se, df)
    return max(p_low, p_high)


def min_bursts(sigma, delta, alpha, power=0.8, cap=10000):
    """Smallest B with (t_{B-1,1-alpha} + t_{B-1,(1+power)/2}) * sigma / sqrt(B) <= delta.

    TOST at a true tau of zero passes with the given power when the interval
    half-width at the Holm level plus the sampling spread fits inside delta.
    """
    for b in range(2, cap + 1):
        df = b - 1
        need = (t_quantile(1.0 - alpha, df) + t_quantile((1.0 + power) / 2.0, df)) * sigma / math.sqrt(b)
        if need <= delta:
            return b
    return None


# ---------------------------------------------------------------- multiplicity

def holm(pvalues, alpha=ALPHA):
    """Holm step-down: list of booleans (rejected) in the input order."""
    m = len(pvalues)
    order = sorted(range(m), key=lambda i: pvalues[i])
    rejected = [False] * m
    for rank, i in enumerate(order):
        if pvalues[i] <= alpha / (m - rank):
            rejected[i] = True
        else:
            break
    return rejected


def holm_first_threshold(m, alpha=ALPHA):
    return alpha / m


# ---------------------------------------------------------------- label permutation

def fisher_yates(items, rnd):
    """In-place shuffle built on random.Random.random(), whose output for a given
    seed the Python documentation keeps stable across versions."""
    for i in range(len(items) - 1, 0, -1):
        j = int(rnd.random() * (i + 1))
        items[i], items[j] = items[j], items[i]
    return items


def paired_label_test(diffs, exact_max_strata=20, b=19999, seed=None):
    """Two-sided test of mean(diffs) = 0 by swapping the two labels inside each stratum.

    diffs: one difference per stratum (class A burst minus class B burst). Swapping
    labels flips the sign of a stratum's difference. Up to 20 strata every sign
    pattern is enumerated and p is exact; above that b random swaps give
    p = (hits + 1) / (b + 1). Returns (p, method, b_used).
    """
    k = len(diffs)
    if k == 0:
        return Fraction(1), "empty", 0
    obs = abs(sum(diffs))
    eps = 1e-12 * max(1.0, obs)
    if k <= exact_max_strata:
        hits = 0
        for pattern in range(1 << k):
            s = sum(-d if pattern >> i & 1 else d for i, d in enumerate(diffs))
            if abs(s) >= obs - eps:
                hits += 1
        return Fraction(hits, 1 << k), "exact", 1 << k
    if seed is None:
        raise ValueError("Monte Carlo label test needs the seed from the prereg manifest")
    rnd = random.Random(seed)
    hits = 0
    for _ in range(b):
        s = 0.0
        for d in diffs:
            pair = fisher_yates([0, 1], rnd)
            s += d if pair[0] == 0 else -d
        if abs(s) >= obs - eps:
            hits += 1
    return Fraction(hits + 1, b + 1), "monte-carlo", b
