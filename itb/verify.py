"""verify: re-reads every recorded signature from the chain (plan section 9).

Channel 1 pages through getSignaturesForAddress of every payer and checks the
slot and transactionIndex of each probe. Channel 2 reads every recorded slot
once with getBlock (full, rewards, maxSupportedTransactionVersion 1) and
re-derives the position, the leader, the builder's tick label and what each
probe itself carries: priority fee, CU limit, write set, burst and send rank.
The reverse check makes the chain confirm the raw data is complete: every
probe in a payer's history must have a raw row. Pre-registration anchors are
checked against their files and against the first included probe of a stage.

Problems fail the command; notes are printed data without a failure.
"""

import hashlib
import json
import os

from . import chain, rpc

PUBLIC_GETBLOCK_LIMIT = 6  # x-ratelimit-method-limit of the public node, 2026-10-26
FULL_BLOCK_MB = (1.87, 2.69)  # one getBlock full answer on three slots, 2026-10-26
PREREG_MEMO_PREFIX = "itb-prereg "
PREREG_STAGES = ("pilot", "campaign")
# Files the pilot manifest fixes (section 10): the plan text, the seeded table and the
# analysis constants. Code that carries out the plan stays outside, so a bug fix after
# the anchor does not break the hash; the plan and its numbers bind that code.
PILOT_MANIFEST_FILES = ("prereg/ANALYSIS-PLAN.md", "prereg/pilot-table.json", "itb/prereg.py")
ANCHORS_FILE = "prereg-anchors.json"


class Report:
    def __init__(self, out=print):
        self.out = out
        self.problems = []
        self.notes = []
        self.bad = set()

    def problem(self, text, signature=None):
        self.problems.append(text)
        if signature:
            self.bad.add(signature)
        self.out("FAIL  " + text)

    def note(self, text):
        self.notes.append(text)
        self.out("note  " + text)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def manifest_path(repo_dir, stage):
    return os.path.join(repo_dir, "prereg", "manifest-%s.json" % stage)


def read_anchors(data_dir):
    """Anchors the probe recorded in data/prereg-anchors.json; no file means none."""
    path = os.path.join(data_dir, ANCHORS_FILE)
    if not os.path.exists(path):
        return []
    with open(path, "rb") as f:
        return json.load(f)


def build_manifest(repo_dir, stage, files):
    """Bytes of a stage manifest (section 10): the SHA-256 of each listed repository
    file. The anchor memo carries the SHA-256 of these bytes as written."""
    if stage not in PREREG_STAGES:
        raise ValueError("stage %r; expected %s" % (stage, " or ".join(PREREG_STAGES)))
    if not files:
        raise ValueError("a manifest lists at least one file")
    listed = {}
    for name in files:
        parts = name.replace("\\", "/").split("/")
        path = os.path.join(repo_dir, *parts)
        if os.path.isabs(name) or ".." in parts or not os.path.isfile(path):
            raise ValueError("%s is no file inside the repository" % name)
        listed["/".join(parts)] = sha256_file(path)
    doc = {"manifest_version": 1, "stage": stage, "files": listed}
    return (json.dumps(doc, indent=2, sort_keys=True) + "\n").encode("utf-8")


def live_runs(runs, network):
    return [r for r in runs if r.run["mode"] == "live" and r.run["network"] == network]


def plan_lines(runs):
    probes = sum(len(r.probes) for r in runs)
    slots = {s for r in runs for s in r.slots} | {
        i["slot"] for r in runs for i in r.inclusions.values() if i["status"] == "included"}
    payers = {p for r in runs for p in r.run["payers"]}
    low, high = (len(slots) * mb for mb in FULL_BLOCK_MB)
    seconds = len(slots) * rpc.RATE_WINDOW_S / PUBLIC_GETBLOCK_LIMIT
    return [
        "verify: %d runs, %d probes, %d payers, %d slots" % (len(runs), probes, len(payers), len(slots)),
        "verify: getBlock full downloads about %.0f-%.0f MB; on the public node "
        "(%d getBlock per %.0f s) that takes at least %.0f s" % (
            low, high, PUBLIC_GETBLOCK_LIMIT, rpc.RATE_WINDOW_S, seconds),
    ]


def channel_one(runs, client, report, histories):
    """Slot and transactionIndex of every probe from its payer's history."""
    for r in runs:
        for p in r.probes.values():
            inc = r.inclusions.get(p["signature"])
            entry = histories.get(p["payer"], {}).get(p["signature"])
            short = p["signature"][:16]

            def bad(text, _sig=p["signature"]):
                report.problem(text, _sig)

            if inc is None or inc["status"] != "included":
                if entry is not None:
                    bad("ch1 %s: on chain in slot %s, raw says %s" % (
                        short, entry.get("slot"), inc["status"] if inc else "no inclusion row"))
                continue
            if entry is None:
                bad("ch1 %s: not in the history of payer %s" % (short, p["payer"]))
                continue
            if entry.get("slot") != inc["slot"]:
                bad("ch1 %s: slot %s on chain, %s in raw" % (
                    short, entry.get("slot"), inc["slot"]))
            if "transactionIndex" not in entry:
                report.note("ch1 %s: node returned no transactionIndex, channel 2 checks it" % short)
            elif entry["transactionIndex"] != inc["tx_index"]:
                bad("ch1 slot %d %s: transactionIndex %s on chain, %s in raw" % (
                    inc["slot"], short, entry["transactionIndex"], inc["tx_index"]))


def _slot_rows(runs):
    out = {}
    for r in runs:
        for slot, row in r.slots.items():
            out.setdefault(slot, []).append(row)
    return out


def channel_two(runs, client, report, panel):
    """Every recorded slot read once; positions, labels and probe fields re-derived."""
    by_slot = {}
    for r in runs:
        for sig, inc in r.inclusions.items():
            if inc["status"] != "included":
                continue
            if sig not in r.probes:
                report.problem("raw %s: inclusion row without a probe row" % sig[:16], sig)
                continue
            by_slot.setdefault(inc["slot"], []).append((r, r.probes[sig], inc))
    slot_rows = _slot_rows(runs)
    costs = {}
    blocks = {}
    for slot in sorted(set(by_slot) | set(slot_rows)):
        raw = rpc.get_block(client, slot)
        if raw is None:
            report.problem("ch2 slot %d: no block on chain" % slot)
            continue
        block = blocks[slot] = chain.Block(slot, raw)
        for row in slot_rows.get(slot, []):
            if row["leader"] != block.fee_recipient():
                report.problem("ch2 slot %d: Fee record %s, raw leader %s" % (
                    slot, block.fee_recipient(), row["leader"]))
            if row["ticks"] != block.ticks():
                report.problem("ch2 slot %d: tick label differs from the block" % slot)
            if row["crank_memo"] != block.crank_memo():
                report.problem("ch2 slot %d: crank memo %r, raw %r" % (
                    slot, block.crank_memo(), row["crank_memo"]))
            if row["tx_count"] != len(block.txs):
                report.problem("ch2 slot %d: %d transactions, raw %d" % (
                    slot, len(block.txs), row["tx_count"]))
        ours = set()
        for r, p, inc in by_slot.get(slot, []):
            ours.add(p["signature"])
            _check_probe(r, p, inc, block, report, costs)
        for tx in block.txs:
            if tx.fee_payer in panel and tx.signatures[0] not in ours:
                view = tx.probe_view()
                report.note("ch2 slot %d: panel payer transaction %s at %d%s" % (
                    slot, tx.signatures[0][:16], tx.index,
                    " (burst %d)" % view["burst_seq"] if view else ""))
    for (seq, cu_limit), values in sorted(costs.items()):
        if len(values) > 1:
            report.problem("ch2 burst %d: costs %s differ at CU limit %d" % (
                seq, sorted(values), cu_limit))
    return blocks


def _check_probe(r, p, inc, block, report, costs):
    slot = block.slot
    short = p["signature"][:16]

    def bad(text, _sig=p["signature"]):
        report.problem(text, _sig)

    tx = block.by_signature.get(p["signature"])
    if tx is None:
        bad("ch2 slot %d %s: signature not in the block" % (slot, short))
        return
    if tx.index != inc["tx_index"]:
        bad("ch2 slot %d %s: position %d in the block, %s in raw" % (
            slot, short, tx.index, inc["tx_index"]))
    burst = r.bursts[p["burst_seq"]]
    recipient = block.fee_recipient()
    leader = burst["leader"] if recipient == (burst.get("fee_collector") or burst["leader"]) \
        else recipient
    if leader != inc["actual_leader"]:
        bad("ch2 slot %d %s: leader %s, raw %s" % (slot, short, leader, inc["actual_leader"]))
    elif leader != burst["leader"]:
        report.note("ch2 slot %d %s: landed with %s, target was %s" % (
            slot, short, leader, burst["leader"]))
    if tx.fee != inc["fee"]:
        bad("ch2 slot %d %s: meta.fee %s, raw %s" % (slot, short, tx.fee, inc["fee"]))
    view = tx.probe_view()
    if view is None:
        bad("ch2 slot %d %s: the transaction is not a probe" % (slot, short))
        return
    expected = {"payer": p["payer"], "burst_seq": p["burst_seq"], "send_rank": p["send_rank"],
                "transfer_lamports": p["transfer_lamports"],
                "priority_fee": p["priority_fee_lamports"], "cu_limit": p["cu_limit"],
                "loaded_data_limit": p["loaded_data_limit"],
                "write_accounts": sorted(set(p["write_accounts"]))}
    for field, want in expected.items():
        if view[field] != want:
            bad("ch2 slot %d %s: %s %r on chain, %r in raw" % (
                slot, short, field, view[field], want))
    if view["fee_minus_signatures"] != view["priority_fee"]:
        report.note("ch2 slot %d %s: meta.fee minus signatures %s, priorityFee %s" % (
            slot, short, view["fee_minus_signatures"], view["priority_fee"]))
    if view["cost"] is not None:
        costs.setdefault((p["burst_seq"], view["cu_limit"]), set()).add(view["cost"])


def reverse_check(runs, client, report, histories, panel, wallets):
    """Every probe in a payer's history must have a raw row (section 9)."""
    known = {sig for r in runs for sig in r.probes}
    seen = set()
    for payer in sorted(histories):
        for sig, entry in histories[payer].items():
            if sig in known or sig in seen:
                continue
            seen.add(sig)
            got = rpc.get_transaction(client, sig)
            if got is None:
                report.note("reverse %s: getTransaction returned nothing" % sig[:16])
                continue
            tx = chain.Tx(got)
            if tx.fee_payer not in panel and tx.fee_payer not in wallets:
                report.note("reverse %s: foreign transaction touching payer %s" % (sig[:16], payer))
                continue
            view = tx.probe_view()
            if view is not None:
                report.problem("reverse %s: probe of burst %d in slot %s has no raw row" % (
                    sig[:16], view["burst_seq"], got.get("slot")))
            else:
                report.note("reverse %s: wallet or payer transaction that is not a probe "
                            "(account creation or closing)" % sig[:16])
    seqs = sorted({p["burst_seq"] for r in runs for p in r.probes.values()})
    if seqs:
        gaps = sorted(set(range(seqs[0], seqs[-1] + 1)) - set(seqs))
        if gaps:
            report.note("burst_seq gaps: %s" % gaps)


def prereg_check(runs, client, report, data_dir, repo_dir):
    """Anchors of pre-registration: memo hash equals the file hash, files listed
    in the manifest hash as recorded, every run of the stage was planned against
    that manifest, memo lands before the stage's first probe."""
    stages = sorted({r.run["stage"] for r in runs} & set(PREREG_STAGES))
    if not stages:
        return
    path = os.path.join(data_dir, ANCHORS_FILE)
    if not os.path.exists(path):
        report.problem("prereg: %s missing while %s runs exist" % (path, "/".join(stages)))
        return
    by_stage = {a["stage"]: a for a in read_anchors(data_dir)}
    for stage in stages:
        anchor = by_stage.get(stage)
        if anchor is None:
            report.problem("prereg: no anchor for stage %s" % stage)
            continue
        target = os.path.join(repo_dir, anchor["file"])
        digest = sha256_file(target)
        got = rpc.get_transaction(client, anchor["signature"])
        if got is None:
            report.problem("prereg %s: anchor transaction not found" % stage)
            continue
        memos = [d.decode("utf-8", "replace") for prog, _, d in chain.Tx(got).instructions
                 if prog in chain.MEMO_PROGRAMS]
        if PREREG_MEMO_PREFIX + digest not in memos:
            report.problem("prereg %s: memo %r does not carry sha256 %s of %s" % (
                stage, memos, digest, anchor["file"]))
        if anchor.get("manifest"):
            with open(target, "rb") as f:
                manifest = json.load(f)
            for name, want in sorted(manifest["files"].items()):
                have = sha256_file(os.path.join(repo_dir, name))
                if have != want:
                    report.problem("prereg %s: %s hashes %s, manifest says %s" % (
                        stage, name, have, want))
            for r in runs:
                planned = r.run.get("prereg_manifest_sha256")
                if r.run["stage"] == stage and planned != digest:
                    report.problem("prereg %s: run %s was planned against manifest %s, the anchor holds %s" % (
                        stage, r.run["run_id"], planned, digest))
        times = [i["block_time"] for r in runs if r.run["stage"] == stage
                 for i in r.inclusions.values()
                 if i["status"] == "included" and i["block_time"] is not None]
        if times and (got.get("blockTime") is None or got["blockTime"] >= min(times)):
            report.problem("prereg %s: memo blockTime %s is not before the first probe %s" % (
                stage, got.get("blockTime"), min(times)))


def slot_leader_check(runs, client, report):
    """Optional third source of the leader; a refused epoch is a closed channel."""
    for r in runs:
        for inc in r.inclusions.values():
            if inc["status"] != "included":
                continue
            try:
                leaders = client.call("getSlotLeaders", [inc["slot"], 1])
            except rpc.RpcError as e:
                report.note("getSlotLeaders slot %d: channel unavailable (%s)" % (inc["slot"], e))
                return
            if leaders and leaders[0] != inc["actual_leader"]:
                report.note("getSlotLeaders slot %d: %s, Fee record gives %s" % (
                    inc["slot"], leaders[0], inc["actual_leader"]))


def verify(runs, client, data_dir, repo_dir, out=print, slot_leaders=True):
    report = Report(out)
    for line in plan_lines(runs):
        out(line)
    panel = {p for r in runs for p in r.run["payers"]}
    wallets = {r.run["wallet"] for r in runs if r.run.get("wallet")}
    histories = {}
    for payer in sorted(panel):
        histories[payer] = {e["signature"]: e for e in rpc.signatures_for_address(client, payer)}
    channel_one(runs, client, report, histories)
    channel_two(runs, client, report, panel)
    reverse_check(runs, client, report, histories, panel, wallets)
    prereg_check(runs, client, report, data_dir, repo_dir)
    if slot_leaders:
        slot_leader_check(runs, client, report)
    checked = 0
    out("signature         slot        index  result")
    for r in runs:
        rows = sorted(r.inclusions.items(), key=lambda kv: (kv[1]["slot"] or 0, kv[1]["tx_index"] or 0))
        for sig, inc in rows:
            if inc["status"] != "included":
                continue
            checked += 1
            out("%-16s  %-10d  %5d  %s" % (sig[:16], inc["slot"], inc["tx_index"],
                                           "MISMATCH" if sig in report.bad else "match"))
    out("verify: %d included probes checked on two channels, %d problems, %d notes" % (
        checked, len(report.problems), len(report.notes)))
    return report
