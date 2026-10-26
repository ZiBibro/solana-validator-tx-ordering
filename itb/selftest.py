"""Selftest: checks with known answers that run before verify (section 9).

Each check returns (name, ok, detail). A failed check stops reproduce before
verify starts.
"""

import copy
import json
import os
import tempfile

from . import b58, rawformat


def _key(tag, n):
    """Deterministic base58 string of 32 bytes; looks like a pubkey, owns nothing."""
    return b58.encode(bytes([tag, n]) + b"\x01" * 30)


def _sig(seq, rank):
    return b58.encode(bytes([seq % 256, rank]) + b"\x02" * 62)


def sample_run(burst_seq=7, n=12):
    """A valid probes.jsonl of one burst, built from the format rules."""
    run_id = "selftest"
    payers = [_key(1, i) for i in range(1, 13)]
    rows = [{
        "v": 1, "kind": "run", "run_id": run_id, "stage": "test", "network": "localnet",
        "mode": "dry-run", "spend_limit_lamports": 50_000_000,
        "code_limit_lamports": 50_000_000, "rpc_url": "http://127.0.0.1:8899",
        "ws_url": "ws://127.0.0.1:8900", "tool_version": "0.1.0", "git_commit": None,
        "started_utc": "2026-10-26T20:00:00Z", "wallet": None, "payers": payers,
        "doubling": True, "prereg_manifest_sha256": None, "seed_table_sha256": None,
    }, {
        "v": 1, "kind": "burst", "run_id": run_id, "burst_seq": burst_seq, "round": 0,
        "cell": 0, "arm": "independent", "timing": "pre300", "path": "quic", "epoch": 1069,
        "first_slot": 462000000, "window_len": 4, "selection_class": "Agave",
        "leader": _key(2, 1), "leader_vote": _key(2, 2), "leader_client_id": "Agave",
        "leader_version": "4.3.2", "tpu_quic": "192.0.2.10:8009", "tpu_quic_port": 8009,
        "gossip_ip": "192.0.2.10", "relayer_default_port": False, "fee_collector": None,
        "validators_app": None, "cluster_nodes_file": None, "equal_fee_lamports": None,
        "blockhash": _key(3, 1), "last_valid_block_height": 440000150,
        "blockhash_context_slot": 461999994, "utc": "2026-10-26T20:00:01Z",
        "slot_clock_source": "first_shred", "slot_ms": 213.2, "anchor_slot": 461999996,
        "anchor_leader": _key(2, 3), "predicted_first_slot_ns": 1_000_000_000,
        "target_arrival_ns": 700_000_000, "rtt_ns": 30_000_000, "send_at_ns": 685_000_000,
        "handshake": None,
    }]
    fees = [0, 10, 100, 1000] * 3
    for rank in range(n):
        payer_index = rank + 1
        rows.append({
            "v": 1, "kind": "probe", "run_id": run_id, "burst_seq": burst_seq,
            "signature": _sig(burst_seq, rank), "payer_index": payer_index,
            "payer": payers[payer_index - 1], "send_rank": rank,
            "transfer_lamports": burst_seq * 16 + rank + 1,
            "priority_fee_lamports": fees[rank], "cu_limit": 1000, "loaded_data_limit": 32768,
            "write_accounts": [payers[payer_index - 1]], "tx_version": "v1",
            "worst_fee_lamports": 5000 + fees[rank], "wire_bytes": 196, "tx_b64": None,
        })
    for rank in range(n):
        rows.append({
            "v": 1, "kind": "send", "run_id": run_id, "burst_seq": burst_seq,
            "signature": _sig(burst_seq, rank), "result": "finished", "code": None,
            "send_end_ns": 685_000_000 + rank * 1000, "stopped_ns": 700_000_000 + rank * 1000,
            "rpc_response": None, "simulate": None, "error": None,
        })
    rows.append({
        "v": 1, "kind": "burst_end", "run_id": run_id, "burst_seq": burst_seq,
        "quic_stats": {"rtt_ns": 30_000_000, "lost_packets": 0},
        "first_shred_ns": [1_010_000_000, None], "node_ts_ms": [None, None],
        "first_send_offset_ns": -325_000_000, "last_send_offset_ns": -324_989_000,
        "prediction_residual_ns": 10_000_000, "reconnects": 0,
        "utc_end": "2026-10-26T20:00:02Z",
    })
    return rows


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


def run_all():
    """Run every selftest group; return (passed, failed, lines)."""
    checks = raw_format_checks()
    lines = []
    failed = 0
    for name, ok, detail in checks:
        lines.append("%s  %s%s" % ("PASS" if ok else "FAIL", name, ("  (" + detail + ")") if detail else ""))
        if not ok:
            failed += 1
    return len(checks) - failed, failed, lines
