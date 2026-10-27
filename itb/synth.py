"""Synthetic bursts with a known ordering rule (section 9).

Every burst has 12 probes that all land in one block. The arm decides fees and
CU limits the way section 6 assigns them; the rule decides the block order.
Seeds are strings, which random.Random hashes the same way on every Python 3,
and shuffles go through the own Fisher-Yates on random(), the one method whose
output the Python documentation keeps across versions.
"""

import random

from . import b58
from .stats import fisher_yates

FEE_LEVELS = (0, 10, 100, 1000)
PROBES = 12
# Half of the 5000-lamport signature fee reaches the leader; the priority fee
# reaches it whole. Agave and Firedancer rank by reward * 1e6 / (cost + 1).
BASE_REWARD = 2500
# Section 6: 2334 units for both arms with two writable accounts, and in the
# denominator arm cost + 1 equals 2032 or 21032 for limits 1000 and 20000.
COST_TWO_WRITES = 2334
COST_ONE_WRITE_BASE = 1031


def priority(fee, cost):
    return (fee + BASE_REWARD) * 1_000_000 // (cost + 1)


def make_probes(rnd, arm):
    """Probes in send order: list of dicts with send_rank, fee, cu_limit, cost."""
    if arm in ("independent", "shared"):
        fees = list(FEE_LEVELS) * (PROBES // len(FEE_LEVELS))
        fisher_yates(fees, rnd)
        return [{"send_rank": r, "fee": fees[r], "cu_limit": 1000, "cost": COST_TWO_WRITES}
                for r in range(PROBES)]
    if arm == "equal_fee":
        fee = FEE_LEVELS[int(rnd.random() * len(FEE_LEVELS))]
        return [{"send_rank": r, "fee": fee, "cu_limit": 1000, "cost": COST_ONE_WRITE_BASE + 1000}
                for r in range(PROBES)]
    if arm == "denominator":
        fee = FEE_LEVELS[int(rnd.random() * len(FEE_LEVELS))]
        limits = [1000] * (PROBES // 2) + [20000] * (PROBES // 2)
        fisher_yates(limits, rnd)
        return [{"send_rank": r, "fee": fee, "cu_limit": limits[r],
                 "cost": COST_ONE_WRITE_BASE + limits[r]} for r in range(PROBES)]
    raise ValueError("unknown arm " + arm)


def _prio(p):
    return priority(p["fee"], p["cost"])


def block_order(rule, probes, rnd):
    """Return the probes in block order under the named rule."""
    noise = {p["send_rank"]: rnd.random() for p in probes}
    if rule == "agave":
        # Exact Agave priority; ties from Slab keys taken off the free list,
        # which carry no arrival order.
        key = lambda p: (-_prio(p), noise[p["send_rank"]])
    elif rule == "firedancer":
        # Exact priority; equal priority leaves in reverse arrival (hypothesis G3).
        key = lambda p: (-_prio(p), -p["send_rank"])
    elif rule == "fifo":
        key = lambda p: p["send_rank"]
    elif rule == "random":
        key = lambda p: noise[p["send_rank"]]
    elif rule == "inverted":
        key = lambda p: (_prio(p), noise[p["send_rank"]])
    elif rule == "mixed":
        # Fee level moves a probe 4 send slots ahead per level, so both the fee
        # and the arrival order shape the block.
        key = lambda p: (p["send_rank"] - 4 * FEE_LEVELS.index(p["fee"]), noise[p["send_rank"]])
    else:
        raise ValueError("unknown rule " + rule)
    return sorted(probes, key=key)


def cell(rule, arm, bursts, seed):
    """Bursts of one synthetic cell in the input format of verdict.cell_results:
    each burst is a list with one block, all 12 probes in it."""
    rnd = random.Random(seed)
    out = []
    for _ in range(bursts):
        probes = make_probes(rnd, arm)
        ordered = block_order(rule, probes, rnd)
        out.append([[dict(p, pos=i) for i, p in enumerate(ordered)]])
    return out


# ---------------------------------------------------------------- raw rows

def key(tag, n):
    """Deterministic base58 string of 32 bytes; looks like a pubkey, owns nothing."""
    return b58.encode(bytes([tag % 256, n % 256]) + b"\x01" * 30)


def sig(seq, rank):
    return b58.encode(seq.to_bytes(4, "little") + bytes([rank]) + b"\x02" * 59)


def run_row(run_id, stage="test"):
    return {
        "v": 2, "kind": "run", "run_id": run_id, "stage": stage, "network": "localnet",
        "mode": "dry-run", "spend_limit_lamports": 50_000_000,
        "code_limit_lamports": 50_000_000, "rpc_url": "http://127.0.0.1:8899",
        "ws_url": "ws://127.0.0.1:8900", "tool_version": "0.1.0", "git_commit": None,
        "started_utc": "2026-10-26T20:00:00Z", "wallet": None,
        "payers": [key(1, i) for i in range(1, PROBES + 1)],
        "doubling": True, "prereg_manifest_sha256": None, "seed_table_sha256": None,
    }


def burst_rows(run, seq, probes, **fields):
    """burst, probe, send and burst_end rows of one burst; probes in send order."""
    run_id = run["run_id"]
    burst = {
        "v": 2, "kind": "burst", "run_id": run_id, "burst_seq": seq, "round": 0,
        "cell": 0, "arm": "independent", "timing": "pre300", "path": "quic", "epoch": 1069,
        "first_slot": 462000000, "window_len": 4, "selection_class": "Agave",
        "leader": key(2, 1), "leader_vote": key(2, 2), "leader_client_id": "Agave",
        "leader_version": "4.3.2", "tpu_quic": "192.0.2.10:8009", "tpu_quic_port": 8009,
        "gossip_ip": "192.0.2.10", "relayer_default_port": False, "fee_collector": None,
        "validators_app": None, "cluster_nodes_file": None, "equal_fee_lamports": None,
        "blockhash": key(3, 1), "last_valid_block_height": 440000150,
        "blockhash_context_slot": 461999994, "utc": "2026-10-26T20:00:01Z",
        "slot_clock_source": "first_shred", "slot_clock_basis": "node_ts",
        "clock_offset_ns": -1_793_044_800_000_000_000, "http_slot": 461999993,
        "http_slot_rtt_ns": 55_000_000, "clock_slot_at_http": 461999994, "clock_lag_slots": -1,
        "slot_ms": 213.2, "anchor_slot": 461999996,
        "anchor_leader": key(2, 3), "predicted_first_slot_ns": 1_000_000_000,
        "target_arrival_ns": 700_000_000, "rtt_ns": 30_000_000, "send_at_ns": 685_000_000,
        "handshake": None,
    }
    burst.update(fields)
    rows = [burst]
    for p in probes:
        rank = p["send_rank"]
        payer = run["payers"][rank]
        rows.append({
            "v": 2, "kind": "probe", "run_id": run_id, "burst_seq": seq,
            "signature": sig(seq, rank), "payer_index": rank + 1, "payer": payer,
            "send_rank": rank, "transfer_lamports": seq * 16 + rank + 1,
            "priority_fee_lamports": p["fee"], "cu_limit": p["cu_limit"],
            "loaded_data_limit": 32768, "write_accounts": [payer], "tx_version": "v1",
            "worst_fee_lamports": 5000 + p["fee"], "wire_bytes": 196, "tx_b64": None,
        })
    for p in probes:
        rank = p["send_rank"]
        rows.append({
            "v": 2, "kind": "send", "run_id": run_id, "burst_seq": seq,
            "signature": sig(seq, rank), "result": "finished", "code": None,
            "send_end_ns": 685_000_000 + rank * 1000, "stopped_ns": 700_000_000 + rank * 1000,
            "rpc_response": None, "simulate": None, "error": None,
        })
    rows.append({
        "v": 2, "kind": "burst_end", "run_id": run_id, "burst_seq": seq,
        "quic_stats": {"rtt_ns": 30_000_000, "lost_packets": 0},
        "first_shred_ns": [1_010_000_000, None], "node_ts_ms": [None, None],
        "first_shred_node_ns": [None, None], "clock_offset_ns": burst["clock_offset_ns"],
        "first_send_offset_ns": -325_000_000, "last_send_offset_ns": -324_989_000,
        "first_send_node_offset_ns": None,
        "prediction_residual_ns": 10_000_000,
        # The final aim equals the aim at signing here.
        "send_anchor_slot": burst["anchor_slot"], "send_anchor_leader": burst["anchor_leader"],
        "send_predicted_first_slot_ns": burst["predicted_first_slot_ns"],
        "send_target_arrival_ns": burst["target_arrival_ns"],
        "send_rtt_ns": burst["rtt_ns"], "reconnects": 0,
        "utc_end": "2026-10-26T20:00:02Z",
    })
    return rows


def inclusion_row(run_id, seq, rank, slot, tx_index, leader, leader_class):
    return {
        "v": 1, "kind": "inclusion", "run_id": run_id, "burst_seq": seq,
        "signature": sig(seq, rank), "status": "included", "slot": slot, "slot_in_window": 1,
        "tx_index": tx_index, "block_tx_count": 400, "block_cost_units": 30_000_000,
        "fee": 5000, "err": None, "actual_leader": leader, "actual_leader_class": leader_class,
        "in_target_window": True, "tick_segment": None, "block_time": 1793044801,
        "checked_utc": "2026-10-26T20:05:00Z",
    }


def slot_row(run_id, slot, leader):
    return {
        "v": 1, "kind": "slot", "run_id": run_id, "slot": slot, "block_time": 1793044801,
        "parent_slot": slot - 1, "blockhash": key(4, slot % 256), "leader": leader,
        "tx_count": 400, "cost_units": 30_000_000, "ticks": [], "crank_memo": None,
        "competition_file": None,
    }


CLASS_INDEX = {"AgaveBam": 1, "JitoLabs": 2, "HarmonicAgave": 3, "HarmonicFiredancer": 4,
                     "Firedancer": 5, "FireBAM": 6, "Rakurai": 7, "Agave": 8}


def campaign_rows(run_id, plan, seed):
    """Raw rows of a synthetic run. plan: list of dicts with class, rule, arm,
    timing, round and optional extra burst fields; every burst lands whole in
    the first slot of its window, its probes spread between foreign transactions.
    Returns (probe_rows, collect_rows)."""
    rnd = random.Random(seed)
    run = run_row(run_id)
    probe_rows = [run]
    collect_rows = []
    for seq, spec in enumerate(plan):
        probes = make_probes(rnd, spec["arm"])
        ordered = block_order(spec["rule"], probes, rnd)
        slot = 462000000 + 200 * seq
        leader = key(5, CLASS_INDEX.get(spec["class"], 0) * 2 + spec.get("leader", 0))
        fields = {"arm": spec["arm"], "timing": spec["timing"], "round": spec["round"],
                  "cell": spec.get("cell", 0), "selection_class": spec["class"],
                  "leader_client_id": spec["class"], "leader": leader, "first_slot": slot}
        fields.update(spec.get("fields", {}))
        probe_rows.extend(burst_rows(run, seq, probes, **fields))
        for i, p in enumerate(ordered):
            collect_rows.append(inclusion_row(run_id, seq, p["send_rank"], slot, 40 + 3 * i,
                                              leader, spec["class"]))
        collect_rows.append(slot_row(run_id, slot, leader))
    return probe_rows, collect_rows
