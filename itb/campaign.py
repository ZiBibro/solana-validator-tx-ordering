"""Seeded campaign table, the minimum from the pilot and epoch plans (plan
sections 5.2, 6 and 7; analysis plan section 5).

The campaign table fixes, before the first campaign burst, the cell of every
burst by epoch, round, class and leader rank, the shared fee of every
equal-fee and denominator burst, the control path bursts and the fee and send
rank of every probe. It is blocked by round like the pilot table: in round k
of an epoch every class stands in the same two cells, (arm_k, t) for its
first leader and (arm_k, 1 - t) for its second. The first leader's set of an
epoch has one cell per arm; the condition of each arm in that set runs over
the four epochs as a seeded order of 0, 0, 1, 1. With doubled windows an
epoch has eight rounds, and each half of four rounds goes through the set in
its own seeded order of the arms. So over four epochs each leader gets each
cell 4 times (2 without doubling) and in each epoch exactly one condition of
the independent arm.

The shared fee of each class and equal-fee or denominator cell takes each of
the four levels equally often over the campaign, so the mean priority fee
stays 277.5 lamports. Each leader gets one control path burst per epoch: the
independent arm through the public RPC, in the condition of its independent
cell of that epoch and in one of the rounds where that cell runs. The two
leaders of a class take different halves, so each independent round carries
one control burst per class.

An epoch plan puts the rounds into their eighths (quarters without doubling):
each round fixes a seeded anchor slot inside its part, and in a seeded order
each burst takes its leader's passing window nearest the anchor, at or past
the earliest slot the plan allows, at least MIN_GAP_SLOTS from every window
already taken in the epoch.

The minimum (analysis plan section 5) reads the pilot runs: for every verdict
slot it fits the additive class plus cell model to the burst taus of kept
pilot bursts, takes sigma as the residual standard deviation and puts it
into the minimum formula. The largest minimum over the six slots is the one
the second memo anchors.
"""

import json
import math
import os
import random
import statistics

from . import analyze, panel, pilot, plan, prereg, stats, verdict

TABLE_VERSION = 1
CAMPAIGN_EPOCHS = 4
CONTROL_ARM = "independent"
MINIMUM_VERSION = 1


# ---------------------------------------------------------------- the table

def _burst(cls, rank, arm, timing, path):
    return {"class": cls, "leader_rank": rank, "path": path,
            "cell": plan.CELLS.index((arm, timing)), "arm": arm, "timing": timing,
            "equal_fee_lamports": None,
            "send_interval_us": plan.EQUAL_FEE_INTERVAL_US if arm == "equal_fee" else 0,
            "probes": None}


def campaign_table(seed, epochs=CAMPAIGN_EPOCHS, doubling=True):
    """The campaign table drawn from seed; the same seed gives the same table."""
    if epochs % len(prereg.TIMINGS):
        raise ValueError("campaign: %d epochs do not split evenly over the moment conditions" % epochs)
    rng = random.Random("itb-campaign-table:" + seed)
    halves = 2 if doubling else 1
    first_t = {}
    for arm in prereg.ARMS:
        seq = list(range(len(prereg.TIMINGS))) * (epochs // len(prereg.TIMINGS))
        rng.shuffle(seq)
        first_t[arm] = seq
    out_epochs = []
    for e in range(epochs):
        control_half = {cls: rng.randrange(halves) for cls in prereg.CLASSES}
        rounds = []
        for h in range(halves):
            arms = list(prereg.ARMS)
            rng.shuffle(arms)
            for j, arm in enumerate(arms):
                t = first_t[arm][e]
                bursts = []
                for cls in prereg.CLASSES:
                    for rank in (0, 1):
                        bursts.append(_burst(cls, rank, arm, prereg.TIMINGS[t if rank == 0 else 1 - t], "quic"))
                if arm == CONTROL_ARM:
                    for cls in prereg.CLASSES:
                        for rank in (0, 1):
                            if (control_half[cls] + rank) % halves == h:
                                bursts.append(_burst(cls, rank, arm, prereg.TIMINGS[t if rank == 0 else 1 - t],
                                                     "rpc"))
                rounds.append({"round": h * len(prereg.ARMS) + j, "half": h, "arm": arm,
                               "first_leader_timing": prereg.TIMINGS[t], "bursts": bursts})
        out_epochs.append({"epoch_index": e, "rounds": rounds,
                           "first_leader_timing": {arm: prereg.TIMINGS[first_t[arm][e]] for arm in prereg.ARMS}})
    for arm in pilot.SHARED_FEE_ARMS:
        for cls in prereg.CLASSES:
            for timing in prereg.TIMINGS:
                mine = [b for ep in out_epochs for r in ep["rounds"] for b in r["bursts"]
                        if (b["class"], b["arm"], b["timing"]) == (cls, arm, timing)]
                fees = list(plan.FEES) * (len(mine) // len(plan.FEES))
                rng.shuffle(fees)
                for b, fee in zip(mine, fees):
                    b["equal_fee_lamports"] = fee
    for ep in out_epochs:
        for r in ep["rounds"]:
            for b in r["bursts"]:
                b["probes"] = plan.probes(b["arm"], rng, plan.PAYERS, b["equal_fee_lamports"])
    return {"table_version": TABLE_VERSION, "stage": "campaign", "seed": seed, "doubling": doubling,
            "epochs": out_epochs}


def table_problems(table):
    """Balance of the campaign table by the rules of sections 5.2 and 6; empty when it holds."""
    out = []
    epochs = table["epochs"]
    halves = 2 if table["doubling"] else 1
    per_cell = len(epochs) // len(prereg.TIMINGS) * halves
    main = [(ep["epoch_index"], r, b) for ep in epochs for r in ep["rounds"] for b in r["bursts"]
            if b["path"] == "quic"]
    control = [(ep["epoch_index"], r, b) for ep in epochs for r in ep["rounds"] for b in r["bursts"]
               if b["path"] == "rpc"]
    if len(main) + len(control) != sum(len(r["bursts"]) for ep in epochs for r in ep["rounds"]):
        out.append("bursts with a path other than quic and rpc")
    for cls in prereg.CLASSES:
        for rank in (0, 1):
            cells = [b["cell"] for _, _, b in main if (b["class"], b["leader_rank"]) == (cls, rank)]
            if sorted(cells) != sorted(list(range(len(plan.CELLS))) * per_cell):
                out.append("%s leader %d: cells %s, each of the 8 %d times expected"
                           % (cls, rank + 1, sorted(cells), per_cell))
            for ep in epochs:
                e = ep["epoch_index"]
                ind = {b["timing"] for ee, _, b in main if ee == e and b["arm"] == CONTROL_ARM
                       and (b["class"], b["leader_rank"]) == (cls, rank)}
                if len(ind) != 1:
                    out.append("%s leader %d epoch %d: independent conditions %s, one expected"
                               % (cls, rank + 1, e, sorted(ind)))
                ctl = [(r, b) for ee, r, b in control if ee == e and (b["class"], b["leader_rank"]) == (cls, rank)]
                if len(ctl) != 1:
                    out.append("%s leader %d epoch %d: %d control bursts, one expected" % (cls, rank + 1, e, len(ctl)))
                elif (ctl[0][1]["arm"], {ctl[0][1]["timing"]}) != (CONTROL_ARM, ind) \
                        or ctl[0][0]["arm"] != CONTROL_ARM:
                    out.append("%s leader %d epoch %d: the control burst leaves the leader's independent cell"
                               % (cls, rank + 1, e))
        for ep in epochs:
            halves_of = [r["half"] for r in ep["rounds"] for b in r["bursts"]
                         if b["path"] == "rpc" and b["class"] == cls]
            if halves > 1 and sorted(halves_of) != list(range(halves)):
                out.append("%s epoch %d: control bursts in halves %s" % (cls, ep["epoch_index"], halves_of))
    for ep in epochs:
        if len(ep["rounds"]) != halves * len(prereg.ARMS) \
                or [r["round"] for r in ep["rounds"]] != list(range(len(ep["rounds"]))):
            out.append("epoch %d: %d rounds" % (ep["epoch_index"], len(ep["rounds"])))
        for h in range(halves):
            arms = sorted(r["arm"] for r in ep["rounds"] if r["half"] == h)
            if arms != sorted(prereg.ARMS):
                out.append("epoch %d half %d: arms %s" % (ep["epoch_index"], h, arms))
        for r in ep["rounds"]:
            regular = [b for b in r["bursts"] if b["path"] == "quic"]
            cells = {(b["leader_rank"], b["arm"], b["timing"]) for b in regular}
            if len(regular) != 2 * len(prereg.CLASSES) or len(cells) != 2 or {c[1] for c in cells} != {r["arm"]} \
                    or {c[2] for c in cells} != set(prereg.TIMINGS):
                out.append("epoch %d round %d: classes do not share the two cells of the round"
                           % (ep["epoch_index"], r["round"]))
    for arm in prereg.ARMS:
        firsts = [ep["first_leader_timing"][arm] for ep in epochs]
        if sorted(firsts) != sorted(list(prereg.TIMINGS) * (len(epochs) // len(prereg.TIMINGS))):
            out.append("%s: first leader conditions %s over the epochs" % (arm, firsts))
    for arm in pilot.SHARED_FEE_ARMS:
        for cls in prereg.CLASSES:
            for timing in prereg.TIMINGS:
                fees = sorted(b["equal_fee_lamports"] for _, _, b in main
                              if (b["class"], b["arm"], b["timing"]) == (cls, arm, timing))
                if fees != sorted(list(plan.FEES) * (2 * per_cell // len(plan.FEES))):
                    out.append("%s %s %s: shared fees %s" % (cls, arm, timing, fees))
    probes = [p["priority_fee_lamports"] for ep in epochs for r in ep["rounds"] for b in r["bursts"]
              for p in b["probes"]]
    if not probes or sum(probes) * len(plan.FEES) != sum(plan.FEES) * len(probes):
        out.append("mean priority fee %.1f, %.1f expected" % (sum(probes) / max(1, len(probes)),
                                                              sum(plan.FEES) / len(plan.FEES)))
    return out


def dumps(table):
    """The table with one burst per line, so a 576-burst table stays readable in a diff."""
    lines = ['{"table_version": %d, "stage": %s, "seed": %s, "doubling": %s, "epochs": ['
             % (table["table_version"], json.dumps(table["stage"]), json.dumps(table["seed"]),
                json.dumps(table["doubling"]))]
    for i, ep in enumerate(table["epochs"]):
        lines.append(' {"epoch_index": %d, "first_leader_timing": %s, "rounds": ['
                     % (ep["epoch_index"], json.dumps(ep["first_leader_timing"], sort_keys=True)))
        for j, r in enumerate(ep["rounds"]):
            lines.append('  {"round": %d, "half": %d, "arm": %s, "first_leader_timing": %s, "bursts": ['
                         % (r["round"], r["half"], json.dumps(r["arm"]), json.dumps(r["first_leader_timing"])))
            for k, b in enumerate(r["bursts"]):
                lines.append("   " + json.dumps(b, separators=(",", ":")) + ("," if k + 1 < len(r["bursts"]) else ""))
            lines.append("  ]}" + ("," if j + 1 < len(ep["rounds"]) else ""))
        lines.append(" ]}" + ("," if i + 1 < len(table["epochs"]) else ""))
    lines.append("]}")
    return "\n".join(lines) + "\n"


def write_table(path, table):
    data = dumps(table).encode()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    return pilot.sha256_bytes(data)


def seed_from_anchors(anchors):
    """Seed of the campaign table from the pilot anchor's signature: public and
    fixed before any pilot data existed, so no one picks it after seeing them."""
    sigs = [a["signature"] for a in anchors if a["stage"] == "pilot"]
    if len(sigs) != 1:
        raise ValueError("campaign: %d pilot anchors, one expected" % len(sigs))
    return "campaign:" + sigs[0]


# ---------------------------------------------------------------- the minimum

def _project_out(v, basis):
    for _ in range(2):  # twice keeps Gram-Schmidt orthogonal in floating point
        for q in basis:
            d = sum(a * b for a, b in zip(v, q))
            v = [a - d * b for a, b in zip(v, q)]
    return v


def residual_fit(points):
    """(rss, rank, n) of the additive class plus cell model over [(class, cell, y)]."""
    classes = sorted({c for c, _, _ in points})
    cells = sorted({k for _, k, _ in points})
    columns = [[1.0] * len(points)]
    columns += [[1.0 if c == x else 0.0 for c, _, _ in points] for x in classes[1:]]
    columns += [[1.0 if k == x else 0.0 for _, k, _ in points] for x in cells[1:]]
    basis = []
    for col in columns:
        v = _project_out(col, basis)
        norm = math.sqrt(sum(a * a for a in v))
        if norm > 1e-9 * math.sqrt(sum(a * a for a in col)):
            basis.append([a / norm for a in v])
    r = _project_out([y for _, _, y in points], basis)
    return sum(a * a for a in r), len(basis), len(points)


def slot_sigma(points):
    """{"bursts", "rank", "df", "sigma"} of one verdict slot; sigma is None without residual degrees of freedom."""
    if not points:
        return {"bursts": 0, "rank": 0, "df": 0, "sigma": None}
    rss, rank, n = residual_fit(points)
    df = n - rank
    return {"bursts": n, "rank": rank, "df": df, "sigma": math.sqrt(rss / df) if df > 0 else None}


def pilot_minimum(runs, epochs=CAMPAIGN_EPOCHS, doubling=True):
    """The minimum of section 5 from the pilot runs among runs."""
    units = [u for run in runs if run.run["stage"] == "pilot" for u in analyze.units_of(run)]
    kept = [u for u in units if not u.reasons]
    excluded = {}
    for u in units:
        for reason in u.reasons:
            excluded[reason] = excluded.get(reason, 0) + 1
    slots, minima = [], []
    for arm in prereg.ARMS:
        for name in verdict.VERDICT_SLOTS[arm]:
            points = []
            for u in kept:
                if u.burst["arm"] == arm:
                    t = verdict.burst_tau(u.blocks, name)
                    if t is not None:
                        points.append((u.burst["selection_class"], u.burst["timing"], t))
            fit = slot_sigma(points)
            b = verdict.min_bursts_formula(fit["sigma"]) if fit["sigma"] is not None else None
            cells = {}
            for timing in prereg.TIMINGS:
                ts = [t for _, k, t in points if k == timing]
                cells[timing] = {"bursts": len(ts), "classes": len({c for c, k, _ in points if k == timing}),
                                 "raw_variance": statistics.variance(ts) if len(ts) > 1 else None}
            slots.append(dict(fit, arm=arm, tau=name, min_bursts=b, cells=cells))
            if b is not None:
                minima.append(b)
    capacity = len(prereg.TIMINGS) * (epochs // len(prereg.TIMINGS)) * (2 if doubling else 1)
    undefined = ["%s/%s" % (s["arm"], s["tau"]) for s in slots if s["min_bursts"] is None]
    minimum = max(minima) if minima else None
    return {
        "minimum_version": MINIMUM_VERSION, "stage": "campaign",
        "formula": "(t[B-1; 1 - alpha_e] + t[B-1; (1 + POWER_PER_TAU) / 2]) * sigma / sqrt(B) <= DELTA_CLASS",
        "alpha_e": float(stats.ALPHA) / verdict.EQUIV_FAMILY_M,
        "power_per_tau": prereg.POWER_PER_TAU, "delta_class": prereg.DELTA_CLASS,
        "pilot_runs": sorted(run.run["run_id"] for run in runs if run.run["stage"] == "pilot"),
        "pilot_bursts": len(units), "kept": len(kept), "excluded": excluded,
        "slots": slots, "undefined_slots": undefined,
        "min_bursts": minimum,
        "campaign_bursts_per_class_cell": capacity,
        "reached": minimum is not None and not undefined and minimum <= capacity,
    }


# ---------------------------------------------------------------- epoch plans

def part_bounds(round_index, rounds, epoch_first, slots_in_epoch):
    return (epoch_first + round_index * slots_in_epoch // rounds,
            epoch_first + (round_index + 1) * slots_in_epoch // rounds)


def place_epoch(epoch_table, seed, leaders, passing, epoch_first, slots_in_epoch, not_before):
    """([{"round", "anchor_slot", "slots"}], notes) for one epoch of the table.

    Anchors and orders come from the seed alone, and the whole epoch is placed
    before not_before is looked at, so the same table and schedule give the same
    windows whenever the plan is drawn. A plan drawn again after a stopped run
    therefore keeps the windows of the rounds still ahead and leaves out every
    round with a window before not_before, the one in progress included, so no
    burst of the table runs twice. A burst without a free passing window of its
    leader gets slot None."""
    rng = random.Random("itb-campaign-order:%s:%d" % (seed, epoch_table["epoch_index"]))
    rounds = epoch_table["rounds"]
    draws = []
    for r in rounds:
        lo, hi = part_bounds(r["round"], len(rounds), epoch_first, slots_in_epoch)
        order = list(range(len(r["bursts"])))
        anchor = rng.randrange(lo, hi)
        rng.shuffle(order)
        draws.append((anchor, order))
    taken, placed, notes = [], [], []
    for r, (anchor, order) in zip(rounds, draws):
        slots = [None] * len(r["bursts"])
        for i in order:
            b = r["bursts"][i]
            leader = leaders[b["class"]][b["leader_rank"]]
            nearest = sorted(passing.get(leader, []), key=lambda w: (abs(w - anchor), w))
            slots[i] = next((w for w in nearest if all(abs(w - t) >= plan.MIN_GAP_SLOTS for t in taken)), None)
            if slots[i] is None:
                notes.append("round %d: no free passing window of %s leader %s; burst left out"
                             % (r["round"], b["class"], leader))
                continue
            taken.append(slots[i])
        placed.append({"round": r["round"], "anchor_slot": anchor, "slots": slots})
    out = []
    for p in placed:
        got = [s for s in p["slots"] if s is not None]
        if got and min(got) < not_before:
            notes.append("round %d: its first window %d lies before slot %d; round left out"
                         % (p["round"], min(got), not_before))
            continue
        out.append(p)
    return out, notes


def build(table, epoch_index, table_sha, manifest_sha, panel_doc, placed, epoch, epoch_first, slots_in_epoch,
          drawn_utc, votes, va_utc, va):
    leaders = pilot.leaders_of(panel_doc)
    by_round = {r["round"]: r for r in table["epochs"][epoch_index]["rounds"]}
    rounds = []
    for p in placed:
        r = by_round[p["round"]]
        bursts = [pilot.plan_burst(b, slot, leaders[b["class"]][b["leader_rank"]], votes, va, va_utc)
                  for b, slot in zip(r["bursts"], p["slots"]) if slot is not None]
        if not bursts:
            continue
        bursts.sort(key=lambda x: x["first_slot"])
        rounds.append({
            "round": r["round"], "epoch": epoch,
            "part": (p["anchor_slot"] - epoch_first) * panel.EIGHTHS // slots_in_epoch,
            "anchor_utc": drawn_utc, "anchor_slot": p["anchor_slot"],
            "cluster_nodes_file": "cluster-nodes.json", "leader_schedule_file": "leader-schedule.json",
            "validators_app_file": None if va is None else "validators-app.json",
            "validators_app_utc": None if va is None else va_utc,
            "bursts": bursts,
        })
    return {"plan_version": plan.PLAN_VERSION, "network": panel_doc["network"], "stage": "campaign",
            "doubling": table["doubling"], "seed_table_sha256": table_sha, "prereg_manifest_sha256": manifest_sha,
            "rounds": rounds}


def draw(client, panel_doc, table, table_sha, manifest_sha, epoch_index, epoch, lead_slots,
         va_fetch=pilot.validators_app, nodes_doc=None):
    """Read the cluster once and return (plan, snapshots, notes) for epoch index
    epoch_index of the table, run in chain epoch epoch (the current or the next).

    Index e runs only in chain epoch panel epoch + e (campaign addendum, section 5):
    another epoch is refused, and an index whose chain epoch has passed is lost.
    nodes_doc, the cluster-nodes.json of the epoch's first plan, makes a plan drawn
    again after a failed run scan the same gossip, so its windows repeat exactly."""
    if epoch != panel_doc["epoch"] + epoch_index:
        raise ValueError("campaign: epoch index %d runs only in chain epoch %d (panel epoch %d plus the index), "
                         "not %d" % (epoch_index, panel_doc["epoch"] + epoch_index, panel_doc["epoch"], epoch))
    info = client.call("getEpochInfo", [{"commitment": "confirmed"}])
    now_slot = info["absoluteSlot"]
    slots = info["slotsInEpoch"]
    if epoch < info["epoch"]:
        raise ValueError("campaign: chain epoch %d has passed (now %d); epoch index %d is lost"
                         % (epoch, info["epoch"], epoch_index))
    if epoch > info["epoch"] + 1:
        raise ValueError("campaign: epoch %d is neither the current epoch %d nor the next" % (epoch, info["epoch"]))
    epoch_first = now_slot - info["slotIndex"] + (epoch - info["epoch"]) * slots
    drawn_utc = plan.utc_now()
    schedule = client.call("getLeaderSchedule", [epoch_first, {"commitment": "confirmed"}])
    if not schedule:
        raise ValueError("campaign: the leader schedule of epoch %d is not known yet" % epoch)
    nodes = client.call("getClusterNodes", []) if nodes_doc is None else nodes_doc["nodes"]
    vote_accounts = client.call("getVoteAccounts", [{"commitment": "confirmed"}])
    tpu = {n["pubkey"]: n.get("tpuQuic") for n in nodes}
    leaders = pilot.leaders_of(panel_doc)
    notes = []
    for cls, ids in leaders.items():
        if len(ids) < panel.PER_CLASS:
            raise ValueError("panel: class %s has %d leaders" % (cls, len(ids)))
        notes.extend("panel leader %s of %s has no tpuQuic in gossip now" % (i, cls) for i in ids if not tpu.get(i))
    passing = {}
    for first, _, leader, passes in panel.scan(schedule, epoch_first, tpu):
        if passes:
            passing.setdefault(leader, []).append(first)
    placed, place_notes = place_epoch(table["epochs"][epoch_index], table["seed"], leaders, passing,
                                      epoch_first, slots, now_slot + lead_slots)
    notes.extend(place_notes)
    _, votes, _ = panel.stakes(vote_accounts)
    try:
        va_utc, va = va_fetch(panel_doc["network"])
    except (OSError, ValueError) as e:
        va_utc, va = None, None
        notes.append("validators.app snapshot failed (%s); bursts carry no second label" % e)
    p = build(table, epoch_index, table_sha, manifest_sha, panel_doc, placed, epoch, epoch_first, slots,
              drawn_utc, votes, va_utc, va)
    if not p["rounds"]:
        raise ValueError("campaign: no burst of epoch index %d found a window from slot %d"
                         % (epoch_index, now_slot + lead_slots))
    if nodes_doc is not None:
        notes.append("windows scanned with the gossip snapshot of %s" % nodes_doc["utc"])
    snapshots = {
        "cluster-nodes.json": nodes_doc or {"utc": drawn_utc, "slot": now_slot, "nodes": nodes},
        "leader-schedule.json": {"utc": drawn_utc, "epoch": epoch, "first_slot": epoch_first,
                                 "schedule": schedule},
    }
    if va is not None:
        snapshots["validators-app.json"] = pilot.va_snapshot(va_utc, va)
    return p, snapshots, notes
