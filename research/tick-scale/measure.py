"""The builder's tick mark over one whole epoch.

README rests the builder classes on a mark in the block: market-tick
transactions signed by BAMgx3XP... in slots of BAM leaders and by
Harmonic8So... in slots of Harmonic leaders. Five samples on 2026-10-26 showed
it; this script measures it over a random sample of every class's slots in one
finished epoch.

The class of a leader is the clientId of its node in the gossip snapshot of a
panel, and the slots are those of the panel's leader schedule, so the sample
covers the whole epoch. Within each class the slots are drawn without
replacement with a fixed seed, which makes the class share a plain estimate of
that epoch's share with a binomial interval. Blocks are read through itb.rpc,
which keeps getBlock under the public node's method limit.

    python research/tick-scale/measure.py sample --panel data/panels/<dir> \\
        --per-class 400 --seed 1069 --out research/tick-scale/sample-e1069.json
    python research/tick-scale/measure.py fetch --sample research/tick-scale/sample-e1069.json \\
        --raw research/tick-scale/blocks-e1069.jsonl
    python research/tick-scale/measure.py report --sample research/tick-scale/sample-e1069.json \\
        --raw research/tick-scale/blocks-e1069.jsonl

fetch appends one row per slot and resumes where it stopped; slots past the
latest finalized slot wait for the next call, which then exits 0.
"""

import argparse
import json
import math
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from itb import chain, prereg, rpc  # noqa: E402

BAM_SIGNER = "BAMgx3XPWrXkNUuQiVWUZU6eB2HQZdwz9HNnT4tpo8LG"
HARMONIC_SIGNER = "Harmonic8SoAfZixJqUxxdSeyWzr6q7XFjuiXS5Z2zPg"
BAM_CLASSES = ("AgaveBam", "FireBAM")
# The BAM node whose leaders post no ticks (README); its leaders stay out of the panel.
SILENT_BAM_HOST = "88.216.192.50"
DEFAULT_RPC = "https://api.mainnet-beta.solana.com"
Z95 = 1.959964


def host(addr):
    return addr.rpartition(":")[0].strip("[]") if addr and ":" in addr else None


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def draw(panel_dir, per_class, seed):
    """Sample of slots per class from the panel's leader schedule and gossip snapshot."""
    schedule = load_json(os.path.join(panel_dir, "leader-schedule.json"))
    gossip = load_json(os.path.join(panel_dir, "cluster-nodes.json"))
    nodes = {n["pubkey"]: n for n in gossip["nodes"]}
    first = schedule["first_slot"]
    population = {}
    for leader, indices in schedule["schedule"].items():
        cls = (nodes.get(leader) or {}).get("clientId") or "not in gossip"
        for i in indices:
            population.setdefault(cls, []).append((first + i, leader))
    rnd = random.Random(seed)
    slots = []
    for cls in prereg.CLASSES:
        pool = sorted(population.get(cls, []))
        for slot, leader in rnd.sample(pool, min(per_class, len(pool))):
            slots.append({"slot": slot, "leader": leader, "class": cls,
                          "tpu_quic": (nodes.get(leader) or {}).get("tpuQuic")})
    return {
        "epoch": schedule["epoch"], "first_slot": first, "panel": os.path.basename(os.path.normpath(panel_dir)),
        "gossip_utc": gossip["utc"], "per_class": per_class, "seed": seed,
        "population": {cls: {"slots": len(v), "leaders": len({l for _, l in v})}
                       for cls, v in sorted(population.items())},
        "slots": sorted(slots, key=lambda s: s["slot"]),
    }


def block_row(item, block):
    """Facts of one sampled slot: ticks counted by signer, plus what ties the block to its leader."""
    row = dict(item)
    if block is None:
        row["status"] = "skipped"
        return row
    b = chain.Block(item["slot"], block)
    by_signer = {}
    for t in b.ticks():
        s = by_signer.setdefault(t["signer"], {"ticks": 0, "interval_ns": t["interval_ns"]})
        s["ticks"] += 1
    row.update({"status": "block", "transactions": len(b.txs), "blockhash": b.blockhash,
                "block_time": b.block_time, "fee_recipient": b.fee_recipient(), "tick_signers": by_signer})
    return row


def read_rows(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.endswith("\n") and line.strip()]


def fetch(sample, raw, client, say=print):
    """Read every sampled slot not yet in raw, up to the latest finalized slot.
    Returns the number of slots left for a later call."""
    done = {r["slot"] for r in read_rows(raw)}
    finalized = client.call("getSlot", [{"commitment": "finalized"}])
    todo = [s for s in sample["slots"] if s["slot"] not in done and s["slot"] <= finalized]
    later = sum(1 for s in sample["slots"] if s["slot"] not in done and s["slot"] > finalized)
    say("fetch: %d done, %d to read now, %d past finalized slot %d" % (len(done), len(todo), later, finalized))
    with open(raw, "a", encoding="utf-8", newline="\n") as f:
        for n, item in enumerate(todo, 1):
            f.write(json.dumps(block_row(item, rpc.get_block(client, item["slot"])), sort_keys=True) + "\n")
            f.flush()
            if n % 100 == 0:
                say("fetch: %d of %d" % (n, len(todo)))
    return later


def pct(k, n):
    return round(100 * k / n, 2) if n else None


def wilson(k, n, z=Z95):
    """95% Wilson interval of k successes in n, in percent, or None for n = 0."""
    if not n:
        return None
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [round(100 * max(0.0, centre - half), 2), round(100 * min(1.0, centre + half), 2)]


def share(k, n):
    return {"k": k, "n": n, "pct": pct(k, n), "ci95": wilson(k, n)}


def summary(sample, rows):
    by_slot = {r["slot"]: r for r in rows}
    out = {"epoch": sample["epoch"], "per_class": sample["per_class"], "seed": sample["seed"],
           "gossip_utc": sample["gossip_utc"], "sampled": len(sample["slots"]),
           "read": sum(1 for s in sample["slots"] if s["slot"] in by_slot),
           "population": sample["population"], "classes": {}}
    for cls in prereg.CLASSES:
        items = [by_slot[s["slot"]] for s in sample["slots"] if s["class"] == cls and s["slot"] in by_slot]
        # A block without transactions has no room for a tick, so it stays out of the shares.
        blocks = [r for r in items if r["status"] == "block" and r["transactions"]]
        none = [r for r in blocks if not r["tick_signers"]]
        n = len(blocks)
        c = {"population_slots": sample["population"].get(cls, {}).get("slots"),
             "population_leaders": sample["population"].get(cls, {}).get("leaders"),
             "sampled": sum(1 for s in sample["slots"] if s["class"] == cls), "read": len(items),
             "skipped": sum(1 for r in items if r["status"] == "skipped"),
             "empty": sum(1 for r in items if r["status"] == "block" and not r["transactions"]),
             "blocks": n, "leaders_in_blocks": len({r["leader"] for r in blocks}),
             "bam_tick": share(sum(1 for r in blocks if BAM_SIGNER in r["tick_signers"]), n),
             "harmonic_tick": share(sum(1 for r in blocks if HARMONIC_SIGNER in r["tick_signers"]), n),
             "other_signer": sum(1 for r in blocks if set(r["tick_signers"]) - {BAM_SIGNER, HARMONIC_SIGNER}),
             "no_tick": share(len(none), n),
             "no_tick_leaders": sorted({r["leader"] for r in none})}
        if cls in BAM_CLASSES:
            hosts = {}
            for r in none:
                e = hosts.setdefault(host(r.get("tpu_quic")) or "no tpuQuic", {"slots": 0, "leaders": set()})
                e["slots"] += 1
                e["leaders"].add(r["leader"])
            c["no_tick_by_tpu_host"] = {h: {"slots": e["slots"], "leaders": sorted(e["leaders"])}
                                        for h, e in sorted(hosts.items(), key=lambda kv: -kv[1]["slots"])}
            c["no_tick_all_on_silent_host"] = bool(none) and set(hosts) == {SILENT_BAM_HOST}
            silent = [r for r in blocks if host(r.get("tpu_quic")) == SILENT_BAM_HOST]
            rest = [r for r in blocks if host(r.get("tpu_quic")) != SILENT_BAM_HOST]
            c["silent_host"] = {"blocks": len(silent), "leaders": len({r["leader"] for r in silent}),
                                "with_tick": sum(1 for r in silent if r["tick_signers"])}
            c["bam_tick_off_silent_host"] = share(sum(1 for r in rest if BAM_SIGNER in r["tick_signers"]),
                                                  len(rest))
        out["classes"][cls] = c
    return out


def table(s):
    """Markdown table for REPORT: count, percent and 95% Wilson interval per cell."""
    def cell(x):
        if not x["n"]:
            return "-"
        return "%d (%.1f%%; %.1f to %.1f)" % (x["k"], x["pct"], x["ci95"][0], x["ci95"][1])

    lines = ["| Class | Slots in epoch | Blocks read | Leaders read | BAM tick | Harmonic tick | No tick |",
             "|---|---:|---:|---:|---|---|---|"]
    for cls, c in s["classes"].items():
        lines.append("| %s | %s | %d | %d | %s | %s | %s |" % (
            cls, c["population_slots"], c["blocks"], c["leaders_in_blocks"],
            cell(c["bam_tick"]), cell(c["harmonic_tick"]), cell(c["no_tick"])))
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("sample")
    a.add_argument("--panel", required=True)
    a.add_argument("--per-class", type=int, default=400)
    a.add_argument("--seed", type=int, required=True)
    a.add_argument("--out", required=True)
    for name in ("fetch", "report"):
        b = sub.add_parser(name)
        b.add_argument("--sample", required=True)
        b.add_argument("--raw", required=True)
    sub.choices["report"].add_argument("--json")
    args = p.parse_args(argv)
    if args.cmd == "sample":
        s = draw(args.panel, args.per_class, args.seed)
        with open(args.out, "w", encoding="utf-8", newline="\n") as f:
            json.dump(s, f, indent=1, sort_keys=True)
            f.write("\n")
        print("sample: %d slots of epoch %d, %d per class, seed %d"
              % (len(s["slots"]), s["epoch"], args.per_class, args.seed))
        return 0
    sample = load_json(args.sample)
    if args.cmd == "fetch":
        client = rpc.Client(os.environ.get("ITB_RPC_URL", DEFAULT_RPC))
        later = fetch(sample, args.raw, client)
        print("fetch: getBlock calls %d, %.1f MB" % (client.calls.get("getBlock", 0), client.bytes / 1e6))
        return 0 if not later else 3
    s = summary(sample, read_rows(args.raw))
    if args.json:
        with open(args.json, "w", encoding="utf-8", newline="\n") as f:
            json.dump(s, f, indent=1, sort_keys=True)
            f.write("\n")
    print(table(s))
    return 0


if __name__ == "__main__":
    sys.exit(main())
