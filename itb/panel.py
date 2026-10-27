"""Leader panel of the pilot and the campaign (plan section 3).

Two leaders for each class of prereg.CLASSES, picked before any live burst by
the rule fixed with the analysis plan. The candidates of a class are its nodes
on the version that holds the largest stake share of the class, taken by
stake, largest first. A candidate needs a current vote account, a tpuQuic in
gossip, at least MIN_WINDOWS leader windows in the epoch and a passing window
in each eighth of it. A window passes when it is full and the window right
before it does not belong to another validator on the same tpuQuic (section
5.3). Class rules come on top of that:

- JitoLabs, Firedancer, Agave and Rakurai: tpuQuic on the gossip IP, so the
  base of each pair takes transactions without a node in between;
- JitoLabs and Rakurai: a tpuQuic port other than the Jito relayer port;
- AgaveBam and FireBAM: the leader's block carries ticks of its BAM node;
- Firedancer: the crank memo of the stock pack (PRF or BAL), or none;
- HarmonicAgave: one leader on the FBA strategy, the other on MRV.

The Fee reward of every leader's block goes to its identity, since verify
takes the slot leader from that record (section 9), and the two leaders of a
class carry different operator names in validator info when names are set.

The block rules read one recent block of the candidate: the first slot of its
latest finalized window, going back up to BLOCK_TRIES windows past skipped
slots. select() asks for that block only once the rules without a block pass.
A leader replaced later is picked by the same rule with exclude=.
"""

import json
import os

from . import chain, plan, prereg, rpc

PANEL_VERSION = 1
PER_CLASS = 2
MIN_WINDOWS = 16
EIGHTHS = 8
BLOCK_TRIES = 3
CONFIG_PROGRAM = "Config1111111111111111111111111111111111111"
OWN_IP_CLASSES = ("JitoLabs", "Firedancer", "Agave", "Rakurai")
RELAYER_PORT_CLASSES = ("JitoLabs", "Rakurai")
TICK_CLASSES = ("AgaveBam", "FireBAM")
STOCK_FIREDANCER_MEMOS = ("PRF", "BAL")
HARMONIC_STRATEGIES = ("FBA", "MRV")


def host_port(addr):
    """(host, port) of "1.2.3.4:8009" or "[::1]:8009"; (None, None) without an address."""
    if not addr or ":" not in addr:
        return None, None
    host, _, port = addr.rpartition(":")
    try:
        return host.strip("[]"), int(port)
    except ValueError:
        return host.strip("[]"), None


def operator_names(config_accounts):
    """{identity: sorted names} from the validatorInfo records of the Config program.
    The identity is the one signer key of a record."""
    names = {}
    for acc in config_accounts:
        data = (acc.get("account") or {}).get("data")
        parsed = data.get("parsed") if isinstance(data, dict) else None
        if not parsed or parsed.get("type") != "validatorInfo":
            continue
        info = parsed.get("info") or {}
        signers = [k.get("pubkey") for k in info.get("keys") or [] if k.get("signer")]
        name = ((info.get("configData") or {}).get("name") or "").strip()
        if len(signers) == 1 and name:
            names.setdefault(signers[0], set()).add(name)
    return {k: sorted(v) for k, v in names.items()}


def _same_name(a, b):
    return " ".join(a.split()).casefold() == " ".join(b.split()).casefold()


def stakes(vote_accounts):
    """({identity: activated stake of its vote accounts}, {identity: vote account},
    identities whose vote accounts are all delinquent). Candidates are ranked by
    the activated stake, so a delinquent node is turned away where its stake puts
    it; class shares count current vote accounts only."""
    stake, votes, current, late = {}, {}, set(), set()
    for group in ("current", "delinquent"):
        for v in vote_accounts.get(group, []):
            stake[v["nodePubkey"]] = stake.get(v["nodePubkey"], 0) + int(v.get("activatedStake", 0))
            votes.setdefault(v["nodePubkey"], v["votePubkey"])
            (current if group == "current" else late).add(v["nodePubkey"])
    return stake, votes, late - current


def _shared_tpu_before(prev, leader, tpu):
    return prev is not None and prev != leader and tpu.get(prev) is not None \
        and tpu.get(prev) == tpu.get(leader)


def scan(schedule, epoch_first, tpu):
    """[(first_slot, length, leader, passes)] of one epoch in slot order."""
    owner = {}
    for leader, indices in schedule.items():
        for i in indices:
            owner[i] = leader
    return [(first, length, leader, length == plan.SLOTS_PER_WINDOW
             and not _shared_tpu_before(owner.get(first - epoch_first - 1), leader, tpu))
            for first, length, leader in plan.windows(schedule, epoch_first)]


def window_facts(schedule, epoch_first, slots_in_epoch, tpu):
    """{leader: {"windows": n, "passing_by_eighth": [8 counts]}} of one epoch."""
    facts = {}
    for first, _, leader, passes in scan(schedule, epoch_first, tpu):
        f = facts.setdefault(leader, {"windows": 0, "passing_by_eighth": [0] * EIGHTHS})
        f["windows"] += 1
        if passes:
            f["passing_by_eighth"][(first - epoch_first) * EIGHTHS // slots_in_epoch] += 1
    return facts


def class_versions(nodes, stake):
    """{class: (version, its share of the class stake)} for the version with the
    largest stake in each class."""
    by = {}
    for n in nodes:
        s = stake.get(n["pubkey"], 0)
        if n.get("clientId") in prereg.CLASSES and s:
            versions = by.setdefault(n["clientId"], {})
            versions[n.get("version")] = versions.get(n.get("version"), 0) + s
    out = {}
    for cls, versions in by.items():
        top = max(versions, key=lambda v: (versions[v], str(v)))
        out[cls] = (top, versions[top] / sum(versions.values()))
    return out


def relayer_port_shares(nodes, stake):
    """{class: stake share of its nodes with tpuQuic on the relayer port}, for REPORT."""
    total, on_port = {}, {}
    for n in nodes:
        cls, s = n.get("clientId"), stake.get(n["pubkey"], 0)
        if cls in prereg.CLASSES and s:
            total[cls] = total.get(cls, 0) + s
            if host_port(n.get("tpuQuic"))[1] == prereg.RELAYER_PORT:
                on_port[cls] = on_port.get(cls, 0) + s
    return {cls: on_port.get(cls, 0) / t for cls, t in total.items()}


# Rules without a block. Each returns the reason a candidate is turned away, or None.

def _version(cls, node, ctx, picked):
    want = ctx["versions"][cls][0]
    if node.get("version") != want:
        return "version %s, the class runs %s" % (node.get("version"), want)
    return None


def _vote(cls, node, ctx, picked):
    if node["pubkey"] in ctx["late"]:
        return "delinquent vote account"
    if not ctx["stake"].get(node["pubkey"]):
        return "no current vote account with stake"
    return None


def _tpu(cls, node, ctx, picked):
    return None if node.get("tpuQuic") else "no tpuQuic in gossip"


def _own_ip(cls, node, ctx, picked):
    if cls not in OWN_IP_CLASSES:
        return None
    gossip_host = host_port(node.get("gossip"))[0]
    if host_port(node.get("tpuQuic"))[0] != gossip_host:
        return "tpuQuic %s off the gossip IP %s" % (node.get("tpuQuic"), gossip_host)
    return None


def _relayer_port(cls, node, ctx, picked):
    if cls in RELAYER_PORT_CLASSES and host_port(node.get("tpuQuic"))[1] == prereg.RELAYER_PORT:
        return "tpuQuic on the relayer port %d" % prereg.RELAYER_PORT
    return None


def _windows(cls, node, ctx, picked):
    n = ctx["facts"].get(node["pubkey"], {}).get("windows", 0)
    return "%d leader windows in the epoch, fewer than %d" % (n, MIN_WINDOWS) if n < MIN_WINDOWS else None


def _eighths(cls, node, ctx, picked):
    by = ctx["facts"].get(node["pubkey"], {}).get("passing_by_eighth", [0] * EIGHTHS)
    empty = [str(i) for i, n in enumerate(by) if n == 0]
    return "no passing window in eighth %s" % ",".join(empty) if empty else None


def _operator(cls, node, ctx, picked):
    for p in picked:
        for a in ctx["names"].get(node["pubkey"], []):
            for b in p["names"]:
                if _same_name(a, b):
                    return "operator %r already on the panel with %s" % (a, p["identity"])
    return None


def cheap_reason(cls, node, ctx, picked):
    return (_version(cls, node, ctx, picked) or _vote(cls, node, ctx, picked)
            or _tpu(cls, node, ctx, picked) or _own_ip(cls, node, ctx, picked)
            or _relayer_port(cls, node, ctx, picked) or _windows(cls, node, ctx, picked)
            or _eighths(cls, node, ctx, picked) or _operator(cls, node, ctx, picked))


# Rules on the candidate's recent block: {"slot", "crank_memo", "ticks", "fee_recipient"}.

def _block(cls, node, block, picked):
    return "no block in its last %d windows" % BLOCK_TRIES if block is None else None


def _collector(cls, node, block, picked):
    if block["fee_recipient"] != node["pubkey"]:
        return "Fee reward of slot %d goes to %s" % (block["slot"], block["fee_recipient"])
    return None


def _tick(cls, node, block, picked):
    if cls in TICK_CLASSES and not block["ticks"]:
        return "no tick in slot %d" % block["slot"]
    return None


def _firedancer_memo(cls, node, block, picked):
    if cls == "Firedancer" and block["crank_memo"] not in STOCK_FIREDANCER_MEMOS + (None,):
        return "crank memo %r in slot %d" % (block["crank_memo"], block["slot"])
    return None


def _strategy(cls, node, block, picked):
    if cls != "HarmonicAgave":
        return None
    memo = block["crank_memo"]
    if memo not in HARMONIC_STRATEGIES:
        return "crank memo %r in slot %d names no strategy of the class" % (memo, block["slot"])
    if any(p["crank_memo"] == memo for p in picked):
        return "strategy %s already on the panel" % memo
    return None


def block_reason(cls, node, block, picked):
    why = _block(cls, node, block, picked)
    if why or block is None:
        return why
    return (_collector(cls, node, block, picked) or _tick(cls, node, block, picked)
            or _firedancer_memo(cls, node, block, picked) or _strategy(cls, node, block, picked))


def select(nodes, stake, votes, late, names, facts, block_of, exclude=()):
    """{class: picks and turned-away candidates} by the section 3 rule.
    block_of(identity) returns the block facts of a candidate or None."""
    live = {k: s for k, s in stake.items() if k not in late}
    versions = class_versions(nodes, live)
    ports = relayer_port_shares(nodes, live)
    ctx = {"versions": versions, "stake": stake, "late": late, "names": names, "facts": facts}
    out = {}
    for cls in prereg.CLASSES:
        members = sorted((n for n in nodes if n.get("clientId") == cls),
                         key=lambda n: (-stake.get(n["pubkey"], 0), n["pubkey"]))
        class_stake = sum(live.get(n["pubkey"], 0) for n in members)
        picked, rejected = [], []
        for n in members if cls in versions else []:
            if len(picked) == PER_CLASS:
                break
            if n["pubkey"] in exclude:
                continue
            why = cheap_reason(cls, n, ctx, picked)
            block = None
            if why is None:
                block = block_of(n["pubkey"])
                why = block_reason(cls, n, block, picked)
            if why:
                rejected.append({"identity": n["pubkey"], "stake_lamports": stake.get(n["pubkey"], 0),
                                 "block_slot": (block or {}).get("slot"), "reason": why})
                continue
            s = stake.get(n["pubkey"], 0)
            f = facts.get(n["pubkey"], {})
            picked.append({
                "identity": n["pubkey"], "vote": votes.get(n["pubkey"]), "names": names.get(n["pubkey"], []),
                "client_id": cls, "version": n.get("version"), "stake_lamports": s,
                "class_stake_share": round(s / class_stake, 6) if class_stake else None,
                "tpu_quic": n.get("tpuQuic"), "gossip": n.get("gossip"),
                "windows": f.get("windows", 0), "passing_by_eighth": f.get("passing_by_eighth"),
                "block_slot": (block or {}).get("slot"), "crank_memo": (block or {}).get("crank_memo"),
                "ticks": (block or {}).get("ticks"), "fee_recipient": (block or {}).get("fee_recipient"),
            })
        version, share = versions.get(cls, (None, None))
        out[cls] = {"class_stake_lamports": class_stake, "version": version,
                    "version_stake_share": None if share is None else round(share, 6),
                    "relayer_port_stake_share": None if cls not in ports else round(ports[cls], 6),
                    "leaders": picked, "rejected": rejected}
    return out


def block_facts(slot, block):
    b = chain.Block(slot, block)
    memo = b.crank_memo()
    return {"slot": slot, "crank_memo": memo.strip("\x00").strip() if memo else memo,
            "ticks": len(b.ticks()), "fee_recipient": b.fee_recipient()}


def draw(client, network, epoch=None):
    """Read the cluster once and return (panel, snapshots) for the given epoch,
    the current one by default or the next one once its schedule is known."""
    info = client.call("getEpochInfo", [{"commitment": "finalized"}])
    finalized = info["absoluteSlot"]
    slots = info["slotsInEpoch"]
    current_first = finalized - info["slotIndex"]
    target = info["epoch"] if epoch is None else epoch
    if target not in (info["epoch"], info["epoch"] + 1):
        raise ValueError("panel: epoch %d is neither the current epoch %d nor the next" % (target, info["epoch"]))
    target_first = current_first + (target - info["epoch"]) * slots
    drawn_utc = plan.utc_now()
    schedule = client.call("getLeaderSchedule", [target_first, {"commitment": "finalized"}])
    if not schedule:
        raise ValueError("panel: the leader schedule of epoch %d is not known yet" % target)
    nodes = client.call("getClusterNodes", [])
    vote_accounts = client.call("getVoteAccounts", [{"commitment": "finalized"}])
    names = operator_names(client.call("getProgramAccounts", [CONFIG_PROGRAM, {"encoding": "jsonParsed"}]))
    stake, votes, late = stakes(vote_accounts)
    facts = window_facts(schedule, target_first, slots, {n["pubkey"]: n.get("tpuQuic") for n in nodes})

    recent = {}
    for first_slot in (current_first, current_first - slots):
        sched = schedule if first_slot == target_first else \
            client.call("getLeaderSchedule", [first_slot, {"commitment": "finalized"}]) or {}
        for first, _, leader in reversed(plan.windows(sched, first_slot)):
            if first + plan.SLOTS_PER_WINDOW - 1 <= finalized:
                recent.setdefault(leader, []).append(first)
    reads = {}

    def block_of(identity):
        if identity not in reads:
            reads[identity] = None
            for slot in recent.get(identity, [])[:BLOCK_TRIES]:
                block = rpc.get_block(client, slot)
                if block is not None:
                    reads[identity] = block_facts(slot, block)
                    break
        return reads[identity]

    classes = select(nodes, stake, votes, late, names, facts, block_of)
    panel = {
        "panel_version": PANEL_VERSION, "network": network, "epoch": target,
        "epoch_first_slot": target_first, "slots_in_epoch": slots,
        "drawn_utc": drawn_utc, "anchor_epoch": info["epoch"], "finalized_slot": finalized,
        "rule": {"per_class": PER_CLASS, "min_windows": MIN_WINDOWS, "eighths": EIGHTHS,
                 "block_tries": BLOCK_TRIES, "own_ip_classes": list(OWN_IP_CLASSES),
                 "relayer_port_classes": list(RELAYER_PORT_CLASSES), "relayer_port": prereg.RELAYER_PORT,
                 "tick_classes": list(TICK_CLASSES), "stock_firedancer_memos": list(STOCK_FIREDANCER_MEMOS),
                 "harmonic_strategies": list(HARMONIC_STRATEGIES)},
        "classes": classes,
        "short": [cls for cls in prereg.CLASSES if len(classes[cls]["leaders"]) < PER_CLASS],
        "blocks_read": sum(1 for v in reads.values() if v is not None),
        "cluster_nodes_file": "cluster-nodes.json", "leader_schedule_file": "leader-schedule.json",
        "vote_accounts_file": "vote-accounts.json", "validator_info_file": "validator-info.json",
    }
    snapshots = {
        "cluster-nodes.json": {"utc": drawn_utc, "slot": finalized, "nodes": nodes},
        "leader-schedule.json": {"utc": drawn_utc, "epoch": target, "first_slot": target_first,
                                 "schedule": schedule},
        "vote-accounts.json": {"utc": drawn_utc, "slot": finalized, "vote_accounts": vote_accounts},
        "validator-info.json": {"utc": drawn_utc, "names": names},
    }
    return panel, snapshots


def write(panel_dir, panel, snapshots):
    os.makedirs(panel_dir, exist_ok=False)
    for name, body in snapshots.items():
        with open(os.path.join(panel_dir, name), "w", encoding="utf-8", newline="") as f:
            json.dump(body, f, separators=(",", ":"))
    path = os.path.join(panel_dir, "panel.json")
    with open(path, "w", encoding="utf-8", newline="") as f:
        json.dump(panel, f, indent=1)
        f.write("\n")
    return path


def summary_lines(panel):
    lines = []
    for cls in prereg.CLASSES:
        c = panel["classes"][cls]
        lines.append("%s: version %s (%.1f%% of class stake), %d turned away"
                     % (cls, c["version"], 100 * (c["version_stake_share"] or 0), len(c["rejected"])))
        for p in c["leaders"]:
            lines.append("  %s %5.2f%% %d windows memo %s ticks %s %s"
                         % (p["identity"], 100 * p["class_stake_share"], p["windows"], p["crank_memo"],
                            p["ticks"], " / ".join(p["names"]) or "-"))
        for r in c["rejected"]:
            lines.append("    - %s %s" % (r["identity"][:8], r["reason"]))
    if panel["short"]:
        lines.append("short of %d leaders: %s" % (PER_CLASS, ", ".join(panel["short"])))
    return lines
