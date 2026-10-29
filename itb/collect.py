"""Collector: reads where every probe of a run landed and writes collect.jsonl
plus one competition file per inclusion slot (plan section 8).

It finds the slot of every probe in the finalized listing of its payer, reads
each inclusion slot and the first slot of each target window once with getBlock
(full, with rewards, maxSupportedTransactionVersion 1), and derives the
position, the actual leader from the Fee reward record, the builder's tick
label and the crank memo from that one answer. A run is re-collected whole:
collect.jsonl is rewritten from the chain, never appended to twice.
"""

import datetime
import gzip
import json
import os

from . import analyze, chain, rawformat, rpc

ROW_ORDER = ("slot", "inclusion")
# Agave's status cache keeps the statuses of its last MAX_RECENT_BLOCKHASHES (300)
# rooted blocks (MAX_ROOT_ENTRIES in status_cache.rs), so a probe whose blockhash
# expired more than 300 blocks below the finalized height is no longer in it.
STATUS_CACHE_BLOCKS = 300
# getBlock of an inclusion slot or a window's first slot: a null result or -32004
# is asked again with pauses of 1 to 16 s, 31 s in all, which outlasts the
# finalization lag of a node behind the one that listed the slot.
BLOCK_ATTEMPTS = 6


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _dump(row):
    return json.dumps(row, separators=(",", ":"), ensure_ascii=False)


def load_cluster_nodes(run_dir, name, cache):
    """{identity: clientId} from a getClusterNodes snapshot of the run."""
    if not name:
        return {}
    if name not in cache:
        with open(os.path.join(run_dir, name), "rb") as f:
            nodes = json.load(f)
        if isinstance(nodes, dict):
            nodes = nodes.get("result") or nodes.get("nodes") or []
        cache[name] = {n.get("pubkey"): n.get("clientId") for n in nodes}
    return cache[name]


def leader_of(block, burst):
    """Identity of the slot's leader: the Fee record holds the fee collector,
    which the burst row names when it differs from the leader's identity."""
    recipient = block.fee_recipient()
    if recipient is not None and recipient == (burst.get("fee_collector") or burst["leader"]):
        return burst["leader"]
    return recipient


def slot_row(run_id, block, competition_file):
    return {"v": 1, "kind": "slot", "run_id": run_id, "slot": block.slot,
            "block_time": block.block_time, "parent_slot": block.parent_slot,
            "blockhash": block.blockhash, "leader": block.fee_recipient(),
            "tx_count": len(block.txs), "cost_units": block.cost_units(),
            "ticks": block.ticks(), "crank_memo": block.crank_memo(),
            "competition_file": competition_file}


def inclusion_row(run_id, probe, burst, status, checked_utc, block=None, tx=None, nodes=None):
    row = {"v": 1, "kind": "inclusion", "run_id": run_id, "burst_seq": probe["burst_seq"],
           "signature": probe["signature"], "status": status, "slot": None,
           "slot_in_window": None, "tx_index": None, "block_tx_count": None,
           "block_cost_units": None, "fee": None, "err": None, "actual_leader": None,
           "actual_leader_class": None, "in_target_window": None, "tick_segment": None,
           "block_time": None, "checked_utc": checked_utc}
    if tx is None:
        return row
    first = burst["first_slot"]
    in_range = first <= block.slot < first + burst["window_len"]
    leader = leader_of(block, burst)
    row.update({
        "slot": block.slot, "tx_index": tx.index,
        "slot_in_window": block.slot - first + 1 if in_range else None,
        "block_tx_count": len(block.txs), "block_cost_units": block.cost_units(),
        "fee": tx.fee, "err": None if tx.err is None else {"value": tx.err},
        "actual_leader": leader, "actual_leader_class": (nodes or {}).get(leader),
        "in_target_window": bool(in_range and leader == burst["leader"]),
        "tick_segment": chain.tick_segment(block.ticks(), tx.index),
        "block_time": block.block_time})
    return row


def write_competition(run_dir, block):
    name = "blocks/%d.jsonl.gz" % block.slot
    path = os.path.join(run_dir, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    body = "".join(_dump(tx.block_tx_row(block.slot)) + "\n" for tx in block.txs)
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(gzip.compress(body.encode("utf-8"), mtime=0))
    os.replace(tmp, path)
    return name


def landing_slots(client, probes, bursts, height):
    """{signature: slot} of the probes found on chain.

    The finalized listing of each payer gives the slot of every probe in a
    finalized block. getSignatureStatuses with the history search asks
    long-term storage once per signature: on 2026-10-29 it timed out six times
    on probes 4 to 12 hours old, and Agave answers null when that search fails,
    which would read as an expired probe. The height is read before the
    listing, so a probe whose blockhash expired below it landed, if at all, in
    a block the listing covers. A probe of the last 300 blocks may sit in a
    block not finalized yet or one the listing node has not rooted; the status
    cache answers for those without the history search."""
    wanted = {p["signature"] for p in probes}
    slots = {}
    for payer in sorted({p["payer"] for p in probes}):
        for entry in rpc.signatures_for_address(client, payer):
            if entry["signature"] in wanted:
                slots[entry["signature"]] = entry["slot"]
    recent = [p["signature"] for p in probes if p["signature"] not in slots
              and bursts[p["burst_seq"]]["last_valid_block_height"] >= height - STATUS_CACHE_BLOCKS]
    for signature, status in rpc.signature_statuses(client, recent, history=False).items():
        if status:
            slots[signature] = status["slot"]
    return slots


def collect_run(run_dir, client, checked_utc=None, out=print):
    """Collect one run; returns the number of collect rows written."""
    run = analyze.load_run(run_dir)
    run_id = run.run["run_id"]
    if run.run["mode"] != "live":
        out("collect: %s is a %s run, nothing reached the chain" % (run_id, run.run["mode"]))
        return 0
    checked_utc = checked_utc or utc_now()
    probes = sorted(run.probes.values(), key=lambda p: (p["burst_seq"], p["send_rank"]))
    height = client.call("getBlockHeight", [{"commitment": "finalized"}])
    slots = landing_slots(client, probes, run.bursts, height)
    with_probe = sorted(set(slots.values()))
    first_slots = sorted({b["first_slot"] for b in run.bursts.values()})
    out("collect: %s, %d probes, %d inclusion slots, %d window first slots"
        % (run_id, len(probes), len(with_probe), len(first_slots)))
    blocks = {}
    for slot in sorted(set(with_probe) | set(first_slots)):
        raw = rpc.get_block(client, slot, attempts=BLOCK_ATTEMPTS)
        blocks[slot] = None if raw is None else chain.Block(slot, raw)
    rows = []
    for slot in sorted(blocks):
        block = blocks[slot]
        if block is None:
            continue
        name = write_competition(run_dir, block) if slot in with_probe else None
        rows.append(slot_row(run_id, block, name))
    cache = {}
    for p in probes:
        burst = run.bursts[p["burst_seq"]]
        slot = slots.get(p["signature"])
        if slot is None:
            expired = height > burst["last_valid_block_height"]
            rows.append(inclusion_row(run_id, p, burst, "expired" if expired else "not_found",
                                      checked_utc))
            continue
        block = blocks.get(slot)
        tx = block.by_signature.get(p["signature"]) if block else None
        if tx is None:
            rows.append(inclusion_row(run_id, p, burst, "error", checked_utc))
            continue
        nodes = load_cluster_nodes(run_dir, burst.get("cluster_nodes_file"), cache)
        rows.append(inclusion_row(run_id, p, burst, "included", checked_utc, block, tx, nodes))
    schema = rawformat.load_schema()
    for row in rows:
        problems = rawformat.validate_row(row, schema)
        if problems:
            raise ValueError("collect wrote an invalid %s row: %s" % (row["kind"], problems))
    path = os.path.join(run_dir, "collect.jsonl")
    with open(path + ".tmp", "wb") as f:
        f.write("".join(_dump(r) + "\n" for r in rows).encode("utf-8"))
    os.replace(path + ".tmp", path)
    included = sum(1 for r in rows if r["kind"] == "inclusion" and r["status"] == "included")
    out("collect: %s, %d of %d probes included, wrote %s" % (run_id, included, len(probes), path))
    return len(rows)
