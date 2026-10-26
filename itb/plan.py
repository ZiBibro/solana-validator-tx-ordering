"""Plan files the probe executes (plan sections 6 and 7).

Every random choice of a run lives here: windows, arm and timing cell of each
burst, fee and send rank of each probe. The probe only checks the file and
sends what it says. This module draws plans for localnet, devnet and mainnet
test runs from the live leader schedule; pilot and campaign plans come from the
panel and the seeded table, which are committed with the analysis plan.

A plan directory holds plan.json and the snapshots it was drawn from; the probe
copies the snapshots into data/runs/<run_id>/snapshots/.
"""

import datetime
import json
import os
import random
import secrets

from . import prereg

PLAN_VERSION = 1
MIN_GAP_SLOTS = 160          # section 7, probe/src/plan.rs MIN_GAP_SLOTS
SLOTS_PER_WINDOW = 4         # consecutive leader slots
FEES = (0, 10, 100, 1000)    # section 6
PROBE_CU = 1000
DENOMINATOR_CU = 20000
LOADED_DATA = 32768
EQUAL_FEE_INTERVAL_US = 5000
PAYERS = 12
CELLS = tuple((arm, timing) for arm in prereg.ARMS for timing in prereg.TIMINGS)
TEST_STAGES = ("localnet", "devnet", "test")


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def probes(arm, rng, n=PAYERS, fee=None):
    """Probe specs of one burst. Fees of the varied arms give each of the four
    levels to n/4 probes; the rank permutation is drawn apart from the fees."""
    ranks = list(range(n))
    rng.shuffle(ranks)
    if arm in ("independent", "shared"):
        fees = [FEES[i % len(FEES)] for i in range(n)]
        rng.shuffle(fees)
    else:
        fees = [fee] * n
    cus = [PROBE_CU] * n
    if arm == "denominator":
        cus = [PROBE_CU] * (n // 2) + [DENOMINATOR_CU] * (n - n // 2)
        rng.shuffle(cus)
    return [{"payer_index": i + 1, "send_rank": ranks[i], "priority_fee_lamports": fees[i],
             "cu_limit": cus[i], "loaded_data_limit": LOADED_DATA} for i in range(n)]


def windows(schedule, epoch_first_slot):
    """[(first_slot, length, leader)] from getLeaderSchedule, split at the
    4-slot boundaries leader rotation uses, in slot order."""
    out = []
    for leader, indices in schedule.items():
        run = []
        for i in sorted(indices):
            if run and (i != run[-1] + 1 or i % SLOTS_PER_WINDOW == 0):
                out.append((epoch_first_slot + run[0], len(run), leader))
                run = []
            run.append(i)
        if run:
            out.append((epoch_first_slot + run[0], len(run), leader))
    out.sort()
    return out


def pick(candidates, after_slot, count, allowed=None, per_leader=None):
    """Earliest windows from after_slot on, MIN_GAP_SLOTS apart, full length."""
    chosen, used = [], {}
    for first, length, leader in candidates:
        if first < after_slot or length != SLOTS_PER_WINDOW:
            continue
        if allowed is not None and leader not in allowed:
            continue
        if per_leader and used.get(leader, 0) >= per_leader:
            continue
        if chosen and first - chosen[-1][0] < MIN_GAP_SLOTS:
            continue
        chosen.append((first, length, leader))
        used[leader] = used.get(leader, 0) + 1
        if len(chosen) == count:
            break
    return chosen


def bursts(chosen, nodes, votes, rng, path="quic", n_probes=PAYERS):
    """One burst per window; cells run through a seeded order of the eight
    arm and timing pairs, so every pair comes once in each eight bursts."""
    order = list(CELLS)
    rng.shuffle(order)
    out = []
    for k, (first, length, leader) in enumerate(chosen):
        cell = k % len(order)
        arm, timing = order[cell]
        fee = rng.choice(FEES) if arm in ("equal_fee", "denominator") else None
        node = nodes.get(leader, {})
        out.append({
            "cell": cell, "arm": arm, "timing": timing, "path": path,
            "first_slot": first, "window_len": length,
            "selection_class": node.get("clientId") or "unknown",
            "leader": leader, "leader_vote": votes.get(leader), "validators_app": None,
            "equal_fee_lamports": fee,
            "send_interval_us": EQUAL_FEE_INTERVAL_US if arm == "equal_fee" else 0,
            "probes": probes(arm, rng, n_probes, fee),
        })
    return out


def check(plan):
    """The probe's own checks (probe/src/plan.rs), so a bad plan fails here first."""
    problems = []
    slots = sorted(b["first_slot"] for r in plan["rounds"] for b in r["bursts"])
    if not slots:
        problems.append("no bursts")
    for a, b in zip(slots, slots[1:]):
        if b - a < MIN_GAP_SLOTS:
            problems.append("windows at %d and %d closer than %d slots" % (a, b, MIN_GAP_SLOTS))
    for r in plan["rounds"]:
        for b in r["bursts"]:
            ps = b["probes"]
            if sorted(p["send_rank"] for p in ps) != list(range(len(ps))):
                problems.append("slot %d: send ranks" % b["first_slot"])
            if len({p["payer_index"] for p in ps}) != len(ps):
                problems.append("slot %d: payers repeat" % b["first_slot"])
            if b["arm"] == "shared" and not any(p["payer_index"] == 1 for p in ps):
                problems.append("slot %d: shared arm without payer 1" % b["first_slot"])
    return problems


def draw(client, network, stage, count, lead_slots, seed, leaders=None, per_leader=None,
         path="quic", n_probes=PAYERS):
    """Read the cluster once and return (plan, snapshots) for the next windows."""
    if network == "mainnet" and stage not in ("test",):
        raise ValueError("mainnet pilot and campaign plans come from the panel and the seeded table; "
                         "a mainnet plan drawn here is a test plan (--stage test)")
    rng = random.Random(seed)
    info = client.call("getEpochInfo", [{"commitment": "confirmed"}])
    now_slot = info["absoluteSlot"]
    epoch_first = now_slot - info["slotIndex"]
    anchor_utc = utc_now()
    schedule = client.call("getLeaderSchedule", [None, {"commitment": "confirmed"}])
    node_list = client.call("getClusterNodes", [])
    vote_accounts = client.call("getVoteAccounts", [{"commitment": "confirmed"}])
    nodes = {n["pubkey"]: n for n in node_list}
    votes = {v["nodePubkey"]: v["votePubkey"]
             for group in ("current", "delinquent") for v in vote_accounts.get(group, [])}
    reachable = {k for k, n in nodes.items() if (n.get("tpuQuic") if path == "quic" else True)}
    allowed = reachable & set(leaders) if leaders else reachable
    chosen = pick(windows(schedule, epoch_first), now_slot + lead_slots, count, allowed, per_leader)
    if not chosen:
        raise ValueError("no window of a reachable leader from slot %d in epoch %d"
                         % (now_slot + lead_slots, info["epoch"]))
    plan = {
        "plan_version": PLAN_VERSION, "network": network, "stage": stage, "doubling": False,
        "seed_table_sha256": None, "prereg_manifest_sha256": None,
        "rounds": [{
            "round": 0, "epoch": info["epoch"],
            "part": min(7, info["slotIndex"] * 8 // info["slotsInEpoch"]),
            "anchor_utc": anchor_utc, "anchor_slot": now_slot,
            "cluster_nodes_file": "cluster-nodes.json", "leader_schedule_file": "leader-schedule.json",
            "validators_app_file": None, "validators_app_utc": None,
            "bursts": bursts(chosen, nodes, votes, rng, path, n_probes),
        }],
    }
    snapshots = {
        "cluster-nodes.json": {"utc": anchor_utc, "slot": now_slot, "nodes": node_list},
        "leader-schedule.json": {"utc": anchor_utc, "epoch": info["epoch"],
                                 "first_slot": epoch_first, "schedule": schedule},
    }
    return plan, snapshots


def write(plan_dir, plan, snapshots):
    os.makedirs(plan_dir, exist_ok=False)
    for name, body in snapshots.items():
        with open(os.path.join(plan_dir, name), "w", encoding="utf-8", newline="") as f:
            json.dump(body, f, separators=(",", ":"))
    path = os.path.join(plan_dir, "plan.json")
    with open(path, "w", encoding="utf-8", newline="") as f:
        json.dump(plan, f, indent=1)
        f.write("\n")
    return path


def new_seed():
    return secrets.token_hex(16)
