"""Seeded table and pilot plan (plan sections 6 and 7).

The table fixes before any live burst the cell of every burst by class, leader
rank and round, the shared fee of the equal-fee and denominator bursts, and the
fee and send rank of every probe. It is blocked by round: in round r every
class stands in the same two cells, (arm_r, t_r) for its first leader and
(arm_r, 1 - t_r) for its second. The arms run through a seeded permutation of
the four rounds and the first leader's condition through a seeded order of
0, 0, 1, 1, so each class gets each of the 8 cells once and each leader 4
bursts. The four classes with a builder get one more equal-fee burst at the
start of slot 2, one class per round, for the rounds test of section 10. The
shared fee of each equal-fee and denominator cell gives each of the four
levels to two of the eight classes, and the four extra bursts take the four
levels, so the mean priority fee stays 277.5 lamports (section 7).

The plan puts the bursts of each round into windows of the panel leaders: in
a seeded order a burst takes its leader's nearest passing window at or past
the round's anchor slot, at least MIN_GAP_SLOTS from every window taken in the
round. The rounds follow one another: the next anchor stands MIN_GAP_SLOTS
past the last window of a round. All four rounds stay in one epoch, so each
round names the one leader schedule snapshot its windows come from.
"""

import hashlib
import json
import os
import random
import ssl
import urllib.request

from . import __version__, panel, plan, prereg

TABLE_VERSION = 1
PILOT_ROUNDS = 4
BUILDER_CLASSES = ("AgaveBam", "FireBAM", "HarmonicAgave", "HarmonicFiredancer")
EXTRA_CELL = ("equal_fee", "slot2")
SHARED_FEE_ARMS = ("equal_fee", "denominator")
BASE_FEE_LAMPORTS = 5000
VALIDATORS_APP_URL = "https://www.validators.app/api/v1/validators/%s.json?limit=9999"
VALIDATORS_APP_FIELDS = ("account", "software_client", "software_version", "updated_at",
                         "active_stake", "delinquent")
EXTRA_CA_ENV = "ITB_EXTRA_CA_PEM"


def _burst(cls, rank, arm, timing, fee, rng, extra=False):
    return {"class": cls, "leader_rank": rank, "extra": extra,
            "cell": plan.CELLS.index((arm, timing)), "arm": arm, "timing": timing,
            "equal_fee_lamports": fee,
            "send_interval_us": plan.EQUAL_FEE_INTERVAL_US if arm == "equal_fee" else 0,
            "probes": plan.probes(arm, rng, plan.PAYERS, fee)}


def pilot_table(seed):
    """The pilot table drawn from seed; the same seed gives the same table."""
    rng = random.Random("itb-pilot-table:" + seed)
    arms = list(prereg.ARMS)
    rng.shuffle(arms)
    first_t = [0, 0, 1, 1]
    rng.shuffle(first_t)
    extra_round = list(range(PILOT_ROUNDS))
    rng.shuffle(extra_round)
    extra_rank = [rng.randrange(2) for _ in BUILDER_CLASSES]
    shared = {}
    for arm in SHARED_FEE_ARMS:
        for timing in prereg.TIMINGS:
            fees = list(plan.FEES) * (len(prereg.CLASSES) // len(plan.FEES))
            rng.shuffle(fees)
            shared[(arm, timing)] = dict(zip(prereg.CLASSES, fees))
    extra_fees = list(plan.FEES)
    rng.shuffle(extra_fees)
    rounds = []
    for r in range(PILOT_ROUNDS):
        bursts = []
        for cls in prereg.CLASSES:
            for rank in (0, 1):
                timing = prereg.TIMINGS[first_t[r] if rank == 0 else 1 - first_t[r]]
                bursts.append(_burst(cls, rank, arms[r], timing, shared.get((arms[r], timing), {}).get(cls), rng))
        for i, cls in enumerate(BUILDER_CLASSES):
            if extra_round[i] == r:
                bursts.append(_burst(cls, extra_rank[i], EXTRA_CELL[0], EXTRA_CELL[1], extra_fees[i], rng, True))
        rounds.append({"round": r, "arm": arms[r], "first_leader_timing": prereg.TIMINGS[first_t[r]],
                       "bursts": bursts})
    return {"table_version": TABLE_VERSION, "stage": "pilot", "seed": seed, "rounds": rounds}


def table_problems(table):
    """Balance of the pilot table by the rules of section 6; empty when it holds."""
    out = []
    regular = [(r["round"], b) for r in table["rounds"] for b in r["bursts"] if not b["extra"]]
    extra = [(r["round"], b) for r in table["rounds"] for b in r["bursts"] if b["extra"]]
    for cls in prereg.CLASSES:
        cells = sorted(b["cell"] for _, b in regular if b["class"] == cls)
        if cells != list(range(len(plan.CELLS))):
            out.append("%s: cells %s, each of the 8 once expected" % (cls, cells))
        for rank in (0, 1):
            n = sum(1 for _, b in regular if b["class"] == cls and b["leader_rank"] == rank)
            if n != PILOT_ROUNDS:
                out.append("%s leader %d: %d bursts" % (cls, rank + 1, n))
    for r in table["rounds"]:
        cells = {(b["leader_rank"], b["arm"], b["timing"]) for b in r["bursts"] if not b["extra"]}
        if len(cells) != 2 or {c[1] for c in cells} != {r["arm"]} or {c[2] for c in cells} != set(prereg.TIMINGS):
            out.append("round %d: classes do not share the two cells of the round" % r["round"])
    firsts = [b["timing"] for r in table["rounds"] for b in r["bursts"] if not b["extra"] and b["leader_rank"] == 0
              and b["class"] == prereg.CLASSES[0]]
    if sorted(firsts) != sorted(list(prereg.TIMINGS) * 2):
        out.append("first leader conditions %s" % firsts)
    if sorted(b["class"] for _, b in extra) != sorted(BUILDER_CLASSES) \
            or sorted(r for r, _ in extra) != list(range(PILOT_ROUNDS)) \
            or any((b["arm"], b["timing"]) != EXTRA_CELL for _, b in extra):
        out.append("extra bursts: one equal-fee slot-2 burst per builder class and per round expected")
    for arm in SHARED_FEE_ARMS:
        for timing in prereg.TIMINGS:
            fees = sorted(b["equal_fee_lamports"] for _, b in regular if (b["arm"], b["timing"]) == (arm, timing))
            if fees != sorted(list(plan.FEES) * 2):
                out.append("%s %s: shared fees %s" % (arm, timing, fees))
    probes = [p["priority_fee_lamports"] for r in table["rounds"] for b in r["bursts"] for p in b["probes"]]
    if not probes or sum(probes) * len(plan.FEES) != sum(plan.FEES) * len(probes):
        out.append("mean priority fee %.1f, %.1f expected" % (sum(probes) / max(1, len(probes)),
                                                              sum(plan.FEES) / len(plan.FEES)))
    return out


def dumps(obj):
    return json.dumps(obj, indent=1) + "\n"


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def leaders_of(panel_doc):
    """{class: [first leader, second leader]} of a panel.json."""
    return {cls: [p["identity"] for p in c["leaders"]] for cls, c in panel_doc["classes"].items()}


def place(table, leaders, passing, start_slot):
    """[{"round", "anchor_slot", "slots"}]: the window of every burst of the
    table, slots in the table's burst order. passing gives each leader's passing
    window starts in slot order."""
    rng = random.Random("itb-pilot-order:" + table["seed"])
    anchor = start_slot
    out = []
    for r in table["rounds"]:
        order = list(range(len(r["bursts"])))
        rng.shuffle(order)
        taken = {}
        for i in order:
            b = r["bursts"][i]
            leader = leaders[b["class"]][b["leader_rank"]]
            slot = next((w for w in passing.get(leader, []) if w >= anchor
                         and all(abs(w - t) >= plan.MIN_GAP_SLOTS for t in taken.values())), None)
            if slot is None:
                raise ValueError("round %d: no passing window of %s leader %s from slot %d in the epoch"
                                 % (r["round"], b["class"], leader, anchor))
            taken[i] = slot
        out.append({"round": r["round"], "anchor_slot": anchor, "slots": [taken[i] for i in range(len(r["bursts"]))]})
        anchor = max(taken.values()) + plan.MIN_GAP_SLOTS
    return out


def extra_ca(env=os.environ):
    """PEM text of ITB_EXTRA_CA_PEM, or None. A machine whose antivirus re-signs
    the validators.app certificate sets it to that antivirus root; the system
    roots stay trusted next to it, and only the validators.app request uses it."""
    pem = env.get(EXTRA_CA_ENV, "").strip()
    return pem or None


def validators_app(network, opener=urllib.request.urlopen, env=os.environ):
    """(snapshot utc, {identity: trimmed record}) from validators.app, the second
    label channel of section 3."""
    utc = plan.utc_now()
    request = urllib.request.Request(VALIDATORS_APP_URL % network,
                                     headers={"user-agent": "inside-the-block/" + __version__})
    kwargs = {"timeout": 90}
    pem = extra_ca(env)
    if pem:
        kwargs["context"] = ssl.create_default_context()
        kwargs["context"].load_verify_locations(cadata=pem)
    with opener(request, **kwargs) as reply:
        records = json.loads(reply.read())
    return utc, {r["account"]: {k: r.get(k) for k in VALIDATORS_APP_FIELDS} for r in records if r.get("account")}


def plan_burst(b, slot, leader, votes, va, va_utc):
    """The plan entry of table burst b in the window at slot."""
    rec = va.get(leader) if va is not None else None
    return {
        "cell": b["cell"], "arm": b["arm"], "timing": b["timing"], "path": b.get("path", "quic"),
        "first_slot": slot, "window_len": plan.SLOTS_PER_WINDOW, "selection_class": b["class"],
        "leader": leader, "leader_vote": votes.get(leader),
        "validators_app": None if rec is None else {
            "software_client": rec["software_client"], "software_version": rec["software_version"],
            "snapshot_utc": va_utc},
        "equal_fee_lamports": b["equal_fee_lamports"], "send_interval_us": b["send_interval_us"],
        "probes": b["probes"],
    }


def build(table, table_sha, manifest_sha, panel_doc, placed, epoch, epoch_first, slots_in_epoch,
          anchor_utc, votes, va_utc, va):
    leaders = leaders_of(panel_doc)
    rounds = []
    for r, p in zip(table["rounds"], placed):
        bursts = [plan_burst(b, slot, leaders[b["class"]][b["leader_rank"]], votes, va, va_utc)
                  for b, slot in zip(r["bursts"], p["slots"])]
        bursts.sort(key=lambda x: x["first_slot"])
        rounds.append({
            "round": r["round"], "epoch": epoch,
            "part": (p["anchor_slot"] - epoch_first) * panel.EIGHTHS // slots_in_epoch,
            "anchor_utc": anchor_utc, "anchor_slot": p["anchor_slot"],
            "cluster_nodes_file": "cluster-nodes.json", "leader_schedule_file": "leader-schedule.json",
            "validators_app_file": None if va is None else "validators-app.json",
            "validators_app_utc": None if va is None else va_utc,
            "bursts": bursts,
        })
    return {"plan_version": plan.PLAN_VERSION, "network": panel_doc["network"], "stage": "pilot",
            "doubling": False, "seed_table_sha256": table_sha, "prereg_manifest_sha256": manifest_sha,
            "rounds": rounds}


def draw(client, panel_doc, table, table_sha, manifest_sha, lead_slots, va_fetch=validators_app):
    """Read the cluster once and return (plan, snapshots, notes) for a pilot that
    starts lead_slots from now."""
    info = client.call("getEpochInfo", [{"commitment": "confirmed"}])
    now_slot = info["absoluteSlot"]
    epoch_first = now_slot - info["slotIndex"]
    slots = info["slotsInEpoch"]
    anchor_utc = plan.utc_now()
    schedule = client.call("getLeaderSchedule", [epoch_first, {"commitment": "confirmed"}])
    nodes = client.call("getClusterNodes", [])
    vote_accounts = client.call("getVoteAccounts", [{"commitment": "confirmed"}])
    notes = []
    tpu = {n["pubkey"]: n.get("tpuQuic") for n in nodes}
    leaders = leaders_of(panel_doc)
    for cls, ids in leaders.items():
        if len(ids) < panel.PER_CLASS:
            raise ValueError("panel: class %s has %d leaders" % (cls, len(ids)))
        for i in ids:
            if not tpu.get(i):
                raise ValueError("panel leader %s of %s has no tpuQuic in gossip now; "
                                 "replace it by the panel rule (exclude=)" % (i, cls))
    passing = {}
    for first, _, leader, passes in panel.scan(schedule, epoch_first, tpu):
        if passes:
            passing.setdefault(leader, []).append(first)
    placed = place(table, leaders, passing, now_slot + lead_slots)
    _, votes, _ = panel.stakes(vote_accounts)
    try:
        va_utc, va = va_fetch(panel_doc["network"])
    except (OSError, ValueError) as e:
        va_utc, va = None, None
        notes.append("validators.app snapshot failed (%s); bursts carry no second label" % e)
    p = build(table, table_sha, manifest_sha, panel_doc, placed, info["epoch"], epoch_first, slots,
              anchor_utc, votes, va_utc, va)
    snapshots = {
        "cluster-nodes.json": {"utc": anchor_utc, "slot": now_slot, "nodes": nodes},
        "leader-schedule.json": {"utc": anchor_utc, "epoch": info["epoch"], "first_slot": epoch_first,
                                 "schedule": schedule},
    }
    if va is not None:
        snapshots["validators-app.json"] = va_snapshot(va_utc, va)
    return p, snapshots, notes


def va_snapshot(va_utc, va, env=os.environ):
    pem = extra_ca(env)
    return {"utc": va_utc, "extra_ca_sha256": sha256_bytes(pem.encode()) if pem else None,
            "records": list(va.values())}


def cost(plan_doc):
    """Probe count and fees of a plan in lamports."""
    probes = [pr for r in plan_doc["rounds"] for b in r["bursts"] for pr in b["probes"]]
    priority = sum(pr["priority_fee_lamports"] for pr in probes)
    return {"bursts": sum(len(r["bursts"]) for r in plan_doc["rounds"]), "probes": len(probes),
            "base_lamports": BASE_FEE_LAMPORTS * len(probes), "priority_lamports": priority,
            "fee_lamports": BASE_FEE_LAMPORTS * len(probes) + priority}


def write_table(path, table):
    data = dumps(table).encode()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    return sha256_bytes(data)
