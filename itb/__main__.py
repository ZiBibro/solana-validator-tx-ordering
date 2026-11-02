"""Command line of the Python side.

    python -m itb reproduce        selftest, then verify, then analyze with the REPORT check
    python -m itb selftest         known-answer checks only
    python -m itb verify           re-read every recorded signature from the chain
    python -m itb analyze          recompute every REPORT table from raw data
    python -m itb report           write the generated tables into REPORT.md and DETAILS.md; --check only compares
    python -m itb claim <block>    print one generated REPORT block, recomputed from raw data
    python -m itb collect [run]    write inclusion and slot rows of runs from the chain
    python -m itb check-raw FILE   validate raw files against schema/raw-format.json
    python -m itb plan             draw a test plan for the probe from the live leader schedule
    python -m itb panel            pick the leader panel of an epoch (DESIGN.md, leader schedule and leader types)
    python -m itb table            draw the seeded pilot table of arms and moments into prereg/
    python -m itb pilot            put the pilot table into windows of the panel leaders
    python -m itb minimum          minimum bursts per class and cell from the pilot runs, into prereg/
    python -m itb campaign-table   draw the seeded campaign table into prereg/
    python -m itb campaign         put one epoch of the campaign table into windows of the panel leaders
    python -m itb manifest         hash the pre-registered files of a stage into prereg/
    python -m itb channel          line health of a run round by round, getSlot round trips, campaign watch

In Docker: docker compose run --rm reproduce [subcommand ...]
"""

import argparse
import datetime
import json
import os
import sys

from . import __version__, analyze, channel, collect, rawformat, report, rpc, selftest, verify
from . import campaign as campaignmod
from . import panel as panelmod
from . import pilot as pilotmod
from . import plan as planmod

EXIT_OK = 0
EXIT_FAIL = 1
EXIT_NOT_READY = 2

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DATA = os.path.join(REPO_DIR, "data")
DEFAULT_RPC = "https://api.mainnet-beta.solana.com"
DEFAULT_TABLE = os.path.join(REPO_DIR, "prereg", "pilot-table.json")
DEFAULT_CAMPAIGN_TABLE = os.path.join(REPO_DIR, "prereg", "campaign-table.json")
DEFAULT_MINIMUM = os.path.join(REPO_DIR, "prereg", "campaign-minimum.json")
# REPORT.md is the short report and DETAILS.md every other table; each block stands in exactly one of them.
DEFAULT_REPORTS = (os.path.join(REPO_DIR, "REPORT.md"), os.path.join(REPO_DIR, "DETAILS.md"))


def _not_ready(name, when):
    print("%s: not implemented yet (%s)" % (name, when),
          file=sys.stderr)
    return EXIT_NOT_READY


def cmd_selftest(args):
    passed, failed, lines = selftest.run_all()
    for line in lines:
        print(line)
    print("selftest: %d passed, %d failed" % (passed, failed))
    if passed + failed == 0:
        print("selftest: no checks ran", file=sys.stderr)
        return EXIT_FAIL
    return EXIT_OK if failed == 0 else EXIT_FAIL


def _data_dir(args):
    return getattr(args, "data", None) or os.environ.get("ITB_ANALYZE_DATA", DEFAULT_DATA)


def _network(args):
    return getattr(args, "network", None) or os.environ.get("ITB_NETWORK", "mainnet")


def _client():
    return rpc.Client(os.environ.get("ITB_RPC_URL", DEFAULT_RPC))


def cmd_verify(args):
    data = _data_dir(args)
    network = _network(args)
    runs = verify.live_runs(analyze.load_runs(data), network)
    if not runs:
        print("verify: no live %s runs under %s" % (network, os.path.join(data, "runs")),
              file=sys.stderr)
        return EXIT_NOT_READY
    url = os.environ.get("ITB_RPC_URL", DEFAULT_RPC)
    print("verify: reading %s through %s" % (network, rpc.origin(url)))
    report = verify.verify(runs, rpc.Client(url), data, REPO_DIR)
    return EXIT_OK if not report.problems else EXIT_FAIL


def cmd_analyze(args):
    data = getattr(args, "data", None) or os.environ.get("ITB_ANALYZE_DATA", DEFAULT_DATA)
    stages = tuple(getattr(args, "stage", None) or ("campaign",))
    runs = [r for r in analyze.load_runs(data) if r.run["stage"] in stages]
    if not runs:
        print("analyze: no runs of stage %s under %s" % ("/".join(stages), os.path.join(data, "runs")),
              file=sys.stderr)
        return EXIT_NOT_READY
    result = analyze.analyze(runs, stages)
    for line in analyze.summary_lines(result):
        print(line)
    if getattr(args, "out", None):
        analyze.write_result(result, args.out)
        print("analyze: wrote " + args.out)
    return EXIT_OK


def _report_files(args):
    return [args.file] if getattr(args, "file", None) else list(DEFAULT_REPORTS)


def _runs_differ(texts, paths, generated, filled):
    """Lines naming the runs that data/ and the published runs table do not share, so a
    run measured into the published folder is named rather than shown as a changed table."""
    for path in paths:
        if "runs" not in filled[path][1]:
            continue
        old = "\n".join(line for name, lines in report.split(texts[path]) if name == "runs" for line in lines)
        new, had = report.run_ids(generated["runs"]), report.run_ids(old)
        out = []
        if new - had:
            out.append("runs in data/ the published table does not list: %s; measure in a separate clone "
                       "(RUNNING.md)" % ", ".join(sorted(new - had)))
        if had - new:
            out.append("runs the published table lists and data/ lacks: %s" % ", ".join(sorted(had - new)))
        return out
    return []


def cmd_report(args):
    paths = _report_files(args)
    missing = [p for p in paths if not os.path.exists(p)]
    if missing:
        print("report: no " + ", ".join(missing), file=sys.stderr)
        return EXIT_NOT_READY
    texts = {}
    for path in paths:
        with open(path, encoding="utf-8") as f:
            texts[path] = f.read()
    generated = report.blocks(_data_dir(args), REPO_DIR)
    try:
        filled = {path: report.fill(text, generated) for path, text in texts.items()}
        placement = report.placement([texts[p] for p in paths], generated) if len(paths) > 1 else []
    except ValueError as e:
        print("report: " + str(e), file=sys.stderr)
        return EXIT_FAIL
    by_name = {os.path.basename(p): texts[p] for p in paths}
    if "DETAILS.md" in by_name and "REPORT.md" in by_name:
        placement += report.pointer_problems(by_name["DETAILS.md"], by_name["REPORT.md"])
    names = " and ".join(os.path.basename(p) for p in paths)
    if getattr(args, "check", False):
        bad = ["%s: blocks differ from the raw data: %s" % (os.path.basename(p), ", ".join(filled[p][1]))
               for p in paths if filled[p][1]]
        bad += _runs_differ(texts, paths, generated, filled)
        if bad or placement:
            for line in placement + bad:
                print("report: " + line, file=sys.stderr)
            return EXIT_FAIL
        print("report: every generated block of %s matches the raw data" % names)
        return EXIT_OK
    for path in paths:
        new, changed = filled[path]
        if changed:
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(new)
        print("report: %s rewrote %s" % (os.path.basename(path),
                                         ", ".join(changed) if changed else "nothing, every block was current"))
    for line in placement:
        print("report: " + line, file=sys.stderr)
    return EXIT_FAIL if placement else EXIT_OK


def cmd_report_check(args):
    args.check = True
    return cmd_report(args)


def cmd_claim(args):
    generated = report.blocks(_data_dir(args), REPO_DIR)
    if args.claim_id not in generated:
        print("claim: no block %s; blocks: %s" % (args.claim_id, ", ".join(sorted(generated))),
              file=sys.stderr)
        return EXIT_FAIL
    print(generated[args.claim_id])
    return EXIT_OK


def cmd_collect(args):
    data = _data_dir(args)
    root = os.path.join(data, "runs")
    names = args.run_ids or (sorted(os.listdir(root)) if os.path.isdir(root) else [])
    client = _client()
    done = 0
    for name in names:
        run_dir = os.path.join(root, name)
        if not os.path.isfile(os.path.join(run_dir, "probes.jsonl")):
            print("collect: %s has no probes.jsonl" % run_dir, file=sys.stderr)
            return EXIT_FAIL
        if args.run_ids or analyze.load_run(run_dir).run["network"] == _network(args):
            collect.collect_run(run_dir, client)
            done += 1
    if done == 0:
        print("collect: no %s runs under %s" % (_network(args), root), file=sys.stderr)
        return EXIT_NOT_READY
    return EXIT_OK


def cmd_reproduce(args):
    for name, step in (("selftest", cmd_selftest), ("verify", cmd_verify),
                       ("analyze", cmd_analyze), ("report --check", cmd_report_check)):
        print("== reproduce: %s" % name, flush=True)
        code = step(args)
        if code != EXIT_OK:
            print("reproduce: stopped at %s (exit %d)" % (name, code), file=sys.stderr)
            return code
    print("reproduce: all steps passed")
    return EXIT_OK


def cmd_check_raw(args):
    schema = rawformat.load_schema()
    bad = 0
    if not args.files:
        print("check-raw: no files given", file=sys.stderr)
        return EXIT_FAIL
    for path in args.files:
        if os.path.basename(path) == "probes.jsonl":
            n, problems = rawformat.check_probe_file(path, schema)
        else:
            n, problems = rawformat.check_rows_file(path, schema)
        print("%s: %d rows, %d problems" % (path, n, len(problems)))
        for p in problems:
            print("  " + p)
        bad += len(problems)
    return EXIT_OK if bad == 0 else EXIT_FAIL


def _stamp():
    return planmod.utc_now().replace("-", "").replace(":", "").split(".")[0] + "Z"


def cmd_panel(args):
    network = _network(args)
    try:
        p, snapshots = panelmod.draw(_client(), network, args.epoch)
    except (ValueError, rpc.RpcError) as e:
        print("panel: %s" % e, file=sys.stderr)
        return EXIT_FAIL
    panel_dir = os.path.join(_data_dir(args), "panels", "%s-e%d-%s" % (network, p["epoch"], _stamp()))
    path = panelmod.write(panel_dir, p, snapshots)
    print("panel: %s (epoch %d, %d blocks read)" % (path, p["epoch"], p["blocks_read"]))
    for line in panelmod.summary_lines(p):
        print(line)
    return EXIT_OK if not p["short"] else EXIT_FAIL


def cmd_table(args):
    path = args.out or DEFAULT_TABLE
    if os.path.exists(path):
        print("table: %s exists; a committed table is never drawn again" % path, file=sys.stderr)
        return EXIT_FAIL
    table = pilotmod.pilot_table(args.seed or planmod.new_seed())
    problems = pilotmod.table_problems(table)
    if problems:
        print("table: %s" % "; ".join(problems), file=sys.stderr)
        return EXIT_FAIL
    digest = pilotmod.write_table(path, table)
    print("table: %s sha256 %s, seed %s" % (path, digest, table["seed"]))
    for r in table["rounds"]:
        print("  round %d: %s, first leaders %s, %d bursts" % (r["round"], r["arm"], r["first_leader_timing"],
                                                           len(r["bursts"])))
    return EXIT_OK


def cmd_minimum(args):
    path = args.out or DEFAULT_MINIMUM
    if os.path.exists(path):
        print("minimum: %s exists; a committed minimum is never computed again" % path, file=sys.stderr)
        return EXIT_FAIL
    runs = [r for r in analyze.load_runs(_data_dir(args)) if r.run["stage"] == "pilot"]
    if not runs:
        print("minimum: no pilot run in %s" % _data_dir(args), file=sys.stderr)
        return EXIT_FAIL
    if any(not r.inclusions for r in runs):
        print("minimum: a pilot run has no collect rows; run itb collect first", file=sys.stderr)
        return EXIT_FAIL
    m = campaignmod.pilot_minimum(runs)
    data = pilotmod.dumps(m).encode()
    with open(path, "wb") as f:
        f.write(data)
    print("minimum: %s sha256 %s" % (path, pilotmod.sha256_bytes(data)))
    print("minimum: %d pilot bursts, %d kept, excluded %s" % (m["pilot_bursts"], m["kept"], m["excluded"]))
    for s in m["slots"]:
        print("  %s/%s: %d bursts, df %d, sigma %s, minimum %s" % (
            s["arm"], s["tau"], s["bursts"], s["df"],
            "-" if s["sigma"] is None else "%.4f" % s["sigma"], s["min_bursts"]))
    print("minimum: B = %s per class and cell; the campaign gives %d, reached %s"
          % (m["min_bursts"], m["campaign_bursts_per_class_cell"], m["reached"]))
    return EXIT_OK


def cmd_campaign_table(args):
    path = args.out or DEFAULT_CAMPAIGN_TABLE
    if os.path.exists(path):
        print("campaign-table: %s exists; a committed table is never drawn again" % path, file=sys.stderr)
        return EXIT_FAIL
    try:
        seed = args.seed or campaignmod.seed_from_anchors(verify.read_anchors(_data_dir(args)))
    except ValueError as e:
        print("campaign-table: %s; give --seed" % e, file=sys.stderr)
        return EXIT_FAIL
    table = campaignmod.campaign_table(seed, doubling=not args.no_doubling)
    problems = campaignmod.table_problems(table)
    if problems:
        print("campaign-table: %s" % "; ".join(problems), file=sys.stderr)
        return EXIT_FAIL
    digest = campaignmod.write_table(path, table)
    bursts = [b for ep in table["epochs"] for r in ep["rounds"] for b in r["bursts"]]
    print("campaign-table: %s sha256 %s, seed %s" % (path, digest, seed))
    print("campaign-table: %d epochs, %d bursts (%d control path), %d probes, doubling %s" % (
        len(table["epochs"]), len(bursts), sum(b["path"] == "rpc" for b in bursts),
        sum(len(b["probes"]) for b in bursts), table["doubling"]))
    for ep in table["epochs"]:
        print("  epoch %d: %s" % (ep["epoch_index"], ", ".join(
            "%s/%s" % (r["arm"], r["first_leader_timing"]) for r in ep["rounds"])))
    return EXIT_OK


def cmd_campaign(args):
    with open(args.panel, "rb") as f:
        panel_doc = json.load(f)
    table_path = args.table or DEFAULT_CAMPAIGN_TABLE
    with open(table_path, "rb") as f:
        raw = f.read()
    table = json.loads(raw)
    problems = campaignmod.table_problems(table)
    if problems:
        print("campaign: table %s" % "; ".join(problems), file=sys.stderr)
        return EXIT_FAIL
    if not 0 <= args.epoch_index < len(table["epochs"]):
        print("campaign: --epoch-index %d outside the table's %d epochs" % (args.epoch_index, len(table["epochs"])),
              file=sys.stderr)
        return EXIT_FAIL
    # A live campaign run refuses a plan without the anchored manifest hash (section 10).
    manifest = args.manifest or verify.manifest_path(REPO_DIR, "campaign")
    manifest_sha = None
    if os.path.exists(manifest):
        with open(manifest, "rb") as f:
            manifest_raw = f.read()
        manifest_sha = pilotmod.sha256_bytes(manifest_raw)
        # The manifest pins the campaign panel (campaign addendum, section 8); another panel is refused.
        problem = verify.panel_pin_problem(json.loads(manifest_raw), args.panel)
        if problem:
            print("campaign: %s (manifest %s)" % (problem, manifest), file=sys.stderr)
            return EXIT_FAIL
        print("campaign: plan carries prereg manifest %s sha256 %s" % (manifest, manifest_sha))
    else:
        # The manifest pins the panel (campaign addendum, section 8), so no campaign plan is drawn without it.
        print("campaign: manifest %s not found; the campaign manifest pins the panel" % manifest, file=sys.stderr)
        return EXIT_FAIL
    nodes = args.nodes
    if args.nodes_from_first_plan and not nodes:
        # A plan drawn again scans the gossip of its index's first plan (campaign addendum, section 5).
        nodes = campaignmod.first_plan_nodes(os.path.join(_data_dir(args), "plans"), _network(args),
                                             args.epoch_index, args.epoch, manifest_sha)
        if not nodes and args.epoch_index == 0:
            # The package always carries the plan of index 0, so its absence means a wrong checkout.
            print("campaign: no first plan of epoch index 0 under this manifest in %s; the package carries it"
                  % os.path.join(_data_dir(args), "plans"), file=sys.stderr)
            return EXIT_FAIL
        print("campaign: gossip %s" % (nodes or "live, no earlier plan of this index"))
    nodes_doc = None
    if nodes:
        with open(nodes, "rb") as f:
            nodes_doc = json.load(f)
    client = _client()
    try:
        p, snapshots, notes = campaignmod.draw(client, panel_doc, table, pilotmod.sha256_bytes(raw), manifest_sha,
                                               args.epoch_index, args.epoch, args.lead_slots, nodes_doc=nodes_doc)
        slot_ms, samples = _slot_ms(client)
        now_slot = client.call("getSlot", [{"commitment": "confirmed"}])
    except (ValueError, rpc.RpcError) as e:
        print("campaign: %s" % e, file=sys.stderr)
        return EXIT_FAIL
    problems = planmod.check(p)
    if problems:
        print("campaign: %s" % "; ".join(problems), file=sys.stderr)
        return EXIT_FAIL
    snapshots["draw-notes.json"] = {"epoch_index": args.epoch_index, "epoch": args.epoch, "notes": notes}
    plan_dir = os.path.join(_data_dir(args), "plans", "campaign-%s-e%d-%s" % (p["network"], args.epoch, _stamp()))
    path = planmod.write(plan_dir, p, snapshots)
    now = datetime.datetime.now(datetime.timezone.utc)
    at = lambda slot: (now + datetime.timedelta(milliseconds=(slot - now_slot) * slot_ms)).strftime("%d.%m %H:%M UTC")
    c = pilotmod.cost(p)
    print("campaign: %s" % path)
    print("campaign: epoch index %d in epoch %d, %d bursts, %d probes, fees %d lamports (%d base, %d priority); "
          "%.1f ms per slot over %d samples" % (args.epoch_index, args.epoch, c["bursts"], c["probes"],
                                                c["fee_lamports"], c["base_lamports"], c["priority_lamports"],
                                                slot_ms, samples))
    for r in p["rounds"]:
        first, last = r["bursts"][0]["first_slot"], r["bursts"][-1]["first_slot"]
        print("  round %d (part %d): %d bursts, slots %d to %d (%d slots), about %s to %s" % (
            r["round"], r["part"], len(r["bursts"]), first, last, last - first, at(first), at(last)))
    for note in notes:
        print("campaign: note: " + note)
    return EXIT_OK


def _slot_ms(client):
    samples = client.call("getRecentPerformanceSamples", [30])
    slots = sum(x["numSlots"] for x in samples)
    return 1000.0 * sum(x["samplePeriodSecs"] for x in samples) / slots if slots else None, len(samples)


def cmd_pilot(args):
    with open(args.panel, "rb") as f:
        panel_doc = json.load(f)
    table_path = args.table or DEFAULT_TABLE
    with open(table_path, "rb") as f:
        raw = f.read()
    table = json.loads(raw)
    problems = pilotmod.table_problems(table)
    # A live pilot run refuses a plan without the anchored manifest hash (section 10).
    manifest = args.manifest or verify.manifest_path(REPO_DIR, "pilot")
    manifest_sha = None
    if os.path.exists(manifest):
        with open(manifest, "rb") as f:
            manifest_sha = pilotmod.sha256_bytes(f.read())
        print("pilot: plan carries prereg manifest %s sha256 %s" % (manifest, manifest_sha))
    elif args.manifest:
        print("pilot: manifest %s not found" % manifest, file=sys.stderr)
        return EXIT_FAIL
    else:
        print("pilot: note: no %s; a live run refuses this plan" % manifest)
    if problems:
        print("pilot: table %s" % "; ".join(problems), file=sys.stderr)
        return EXIT_FAIL
    client = _client()
    try:
        p, snapshots, notes = pilotmod.draw(client, panel_doc, table, pilotmod.sha256_bytes(raw),
                                            manifest_sha, args.lead_slots)
        slot_ms, samples = _slot_ms(client)
        now_slot = client.call("getSlot", [{"commitment": "confirmed"}])
    except (ValueError, rpc.RpcError) as e:
        print("pilot: %s" % e, file=sys.stderr)
        return EXIT_FAIL
    problems = planmod.check(p)
    if problems:
        print("pilot: %s" % "; ".join(problems), file=sys.stderr)
        return EXIT_FAIL
    plan_dir = os.path.join(_data_dir(args), "plans", "pilot-%s-%s" % (p["network"], _stamp()))
    path = planmod.write(plan_dir, p, snapshots)
    now = datetime.datetime.now(datetime.timezone.utc)
    at = lambda slot: (now + datetime.timedelta(milliseconds=(slot - now_slot) * slot_ms)).strftime("%d.%m %H:%M UTC")
    c = pilotmod.cost(p)
    print("pilot: %s" % path)
    print("pilot: %d bursts, %d probes, fees %d lamports (%d base, %d priority); %.1f ms per slot over %d samples"
          % (c["bursts"], c["probes"], c["fee_lamports"], c["base_lamports"], c["priority_lamports"], slot_ms, samples))
    for r in p["rounds"]:
        first, last = r["bursts"][0]["first_slot"], r["bursts"][-1]["first_slot"]
        print("  round %d: slots %d to %d (%d slots), about %s to %s" % (r["round"], first, last, last - first,
                                                                       at(first), at(last)))
    for note in notes:
        print("pilot: note: " + note)
    return EXIT_OK


def cmd_manifest(args):
    files = list(args.file or verify.MANIFEST_FILES.get(args.stage) or ())
    if not files:
        print("manifest: stage %s lists its files with --file" % args.stage, file=sys.stderr)
        return EXIT_FAIL
    if args.stage == "campaign":
        # The campaign manifest pins the panel it runs on (campaign addendum, section 8).
        name = (args.panel or "").replace("\\", "/")
        if not (name.startswith(verify.PANEL_PREFIX) and name.endswith("/panel.json")):
            print("manifest: stage campaign pins its panel with --panel %s<id>/panel.json"
                  % verify.PANEL_PREFIX, file=sys.stderr)
            return EXIT_FAIL
        files.append(name)
    elif args.panel:
        print("manifest: --panel belongs to stage campaign", file=sys.stderr)
        return EXIT_FAIL
    done = [a for a in verify.read_anchors(_data_dir(args)) if a["stage"] == args.stage]
    if done:
        print("manifest: stage %s is anchored by %s; its manifest is never drawn again"
              % (args.stage, done[0]["signature"]), file=sys.stderr)
        return EXIT_FAIL
    try:
        data = verify.build_manifest(REPO_DIR, args.stage, files)
    except ValueError as e:
        print("manifest: %s" % e, file=sys.stderr)
        return EXIT_FAIL
    path = verify.manifest_path(REPO_DIR, args.stage)
    with open(path, "wb") as f:
        f.write(data)
    digest = pilotmod.sha256_bytes(data)
    print("manifest: %s sha256 %s" % (path, digest))
    for name, h in sorted(json.loads(data)["files"].items()):
        print("  %s  %s" % (h, name))
    print('manifest: anchor memo "%s%s"' % (verify.PREREG_MEMO_PREFIX, digest))
    return EXIT_OK


def cmd_plan(args):
    network = _network(args)
    stage = args.stage or (network if network in ("localnet", "devnet") else None)
    if stage not in planmod.TEST_STAGES:
        print("plan: --stage must be one of %s for a drawn plan" % ", ".join(planmod.TEST_STAGES),
              file=sys.stderr)
        return EXIT_FAIL
    seed = args.seed or planmod.new_seed()
    leaders = list(args.leader or [])
    if args.panel:
        with open(args.panel, encoding="utf-8") as f:
            leaders += [i for ids in pilotmod.leaders_of(json.load(f)).values() for i in ids]
    leaders = leaders or None
    try:
        p, snapshots = planmod.draw(_client(), network, stage, args.bursts, args.lead_slots, seed,
                                    leaders, args.per_leader, args.path, args.probes)
    except (ValueError, rpc.RpcError) as e:
        print("plan: %s" % e, file=sys.stderr)
        return EXIT_FAIL
    problems = planmod.check(p)
    if problems:
        print("plan: %s" % "; ".join(problems), file=sys.stderr)
        return EXIT_FAIL
    stamp = _stamp()
    plan_dir = os.path.join(_data_dir(args), "plans", "%s-%s-%s" % (stage, network, stamp))
    path = planmod.write(plan_dir, p, snapshots)
    r = p["rounds"][0]
    print("plan: %s" % path)
    print("plan: seed %s, %d bursts from slot %d (anchor %d)"
          % (seed, len(r["bursts"]), r["bursts"][0]["first_slot"], r["anchor_slot"]))
    for b in r["bursts"]:
        print("  slot %d %s %s %s %s fee %s" % (b["first_slot"], b["leader"], b["arm"], b["timing"],
                                                b["path"], b["equal_fee_lamports"]))
    return EXIT_OK


def cmd_channel(args):
    """rounds: one JSON line per round of a run; rpc: getSlot round trips; watch:
    journal the rounds of the live runs. --gate and watch exit 3 below a threshold."""
    logs = args.logs or os.path.join(REPO_DIR, "logs")
    if args.what == "rounds":
        try:
            found = channel.run_rounds(_data_dir(args), logs, args.run_id, args.all)
        except ValueError as e:
            print("channel: %s" % e, file=sys.stderr)
            return EXIT_FAIL
        for r in found:
            print(json.dumps(r, sort_keys=True))
        if not found:
            print("channel: no finished round in run %s" % args.run_id, file=sys.stderr)
            return EXIT_NOT_READY
        return channel.EXIT_BELOW if args.gate and any(r["below"] for r in found) else EXIT_OK
    if args.what == "rpc":
        url = os.environ.get("ITB_RPC_URL", DEFAULT_RPC)
        result = channel.rpc_rtt(url, args.seconds, args.interval)
        result["rpc"] = rpc.origin(url)
        print(json.dumps(result, sort_keys=True))
        return channel.EXIT_BELOW if args.gate and result["below"] else EXIT_OK
    if not args.journal:
        print("channel watch: --journal is required", file=sys.stderr)
        return EXIT_FAIL
    return channel.watch(_data_dir(args), logs, args.journal, args.stage, args.transcript, args.poll,
                         say=lambda line: print(line, flush=True))


def main(argv=None):
    parser = argparse.ArgumentParser(prog="itb", description=__doc__.split("\n")[0])
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("reproduce", help="selftest, verify, analyze, report --check")
    sub.add_parser("selftest", help="known-answer checks")
    p = sub.add_parser("verify", help="re-read every recorded signature from the chain")
    p.add_argument("--data", help="data directory with runs/ (default: repo data/)")
    p.add_argument("--network", help="network of the runs to verify (default: ITB_NETWORK or mainnet)")
    p = sub.add_parser("analyze", help="recompute REPORT from raw data")
    p.add_argument("--data", help="data directory with runs/ (default: repo data/)")
    p.add_argument("--stage", action="append", help="run stage to include (default: campaign)")
    p.add_argument("--out", help="write the full result as JSON here")
    p = sub.add_parser("report", help="write the generated tables into REPORT.md and DETAILS.md")
    p.add_argument("--check", action="store_true", help="compare only; exit 1 when a block differs")
    p.add_argument("--file", help="one report file (default: REPORT.md and DETAILS.md)")
    p.add_argument("--data", help="data directory with runs/ (default: repo data/)")
    p = sub.add_parser("claim", help="print one generated REPORT block, recomputed from raw data")
    p.add_argument("claim_id", help="block name, as in <!-- itb:begin NAME -->")
    p.add_argument("--data", help="data directory with runs/ (default: repo data/)")
    p = sub.add_parser("collect", help="write inclusion and slot rows of runs from the chain")
    p.add_argument("run_ids", nargs="*", help="runs to collect (default: every run of the network)")
    p.add_argument("--data", help="data directory with runs/ (default: repo data/)")
    p.add_argument("--network", help="network of the runs (default: ITB_NETWORK or mainnet)")
    p = sub.add_parser("check-raw", help="validate raw files")
    p.add_argument("files", nargs="*")
    p = sub.add_parser("plan", help="draw a test plan for the probe")
    p.add_argument("--network", help="localnet, devnet or mainnet (default: ITB_NETWORK or mainnet)")
    p.add_argument("--stage", help="localnet, devnet or test (default: the network)")
    p.add_argument("--bursts", type=int, default=8, help="windows to draw (default 8)")
    p.add_argument("--lead-slots", type=int, default=900,
                   help="first window at least this many slots ahead (default 900)")
    p.add_argument("--leader", action="append", help="allowed leader identity (repeatable)")
    p.add_argument("--panel", help="allow the leaders of this panel.json (adds to --leader)")
    p.add_argument("--per-leader", type=int, help="at most this many windows per leader")
    p.add_argument("--path", choices=("quic", "rpc"), default="quic")
    p.add_argument("--probes", type=int, default=planmod.PAYERS, help="probes per burst, 2 to 12")
    p.add_argument("--seed", help="seed of the draw (default: random, printed)")
    p.add_argument("--data", help="data directory (default: repo data/)")
    p = sub.add_parser("table", help="draw the seeded pilot table")
    p.add_argument("--seed", help="seed of the table (default: random, printed)")
    p.add_argument("--out", help="table file (default: prereg/pilot-table.json)")
    p = sub.add_parser("pilot", help="put the pilot table into windows of the panel leaders")
    p.add_argument("--panel", required=True, help="panel.json from itb panel")
    p.add_argument("--table", help="pilot table (default: prereg/pilot-table.json)")
    p.add_argument("--manifest", help="prereg manifest whose sha256 the plan carries "
                                      "(default: prereg/manifest-pilot.json when it exists)")
    p.add_argument("--lead-slots", type=int, default=900, help="first window at least this many slots ahead")
    p.add_argument("--data", help="data directory (default: repo data/)")
    p = sub.add_parser("minimum", help="minimum bursts per class and cell from the pilot runs")
    p.add_argument("--data", help="data directory with runs/ (default: repo data/)")
    p.add_argument("--out", help="minimum file (default: prereg/campaign-minimum.json)")
    p = sub.add_parser("campaign-table", help="draw the seeded campaign table")
    p.add_argument("--seed", help="seed of the table (default: campaign: plus the pilot anchor's signature)")
    p.add_argument("--no-doubling", action="store_true", help="four rounds per epoch, the fallback mode")
    p.add_argument("--out", help="table file (default: prereg/campaign-table.json)")
    p.add_argument("--data", help="data directory with prereg-anchors.json (default: repo data/)")
    p = sub.add_parser("campaign", help="put one epoch of the campaign table into windows of the panel leaders")
    p.add_argument("--panel", required=True, help="panel.json from itb panel")
    p.add_argument("--epoch-index", type=int, required=True, help="epoch of the table, 0 to 3")
    p.add_argument("--epoch", type=int, required=True,
                   help="chain epoch it runs in: the panel's epoch plus the index, the current or the next")
    p.add_argument("--nodes", help="cluster-nodes.json of the epoch's first plan: a plan drawn again "
                                   "scans the same gossip, so its windows repeat")
    p.add_argument("--nodes-from-first-plan", action="store_true",
                   help="take --nodes from the first plan of this index, chain epoch and manifest under "
                        "data/plans, or live gossip when there is none")
    p.add_argument("--table", help="campaign table (default: prereg/campaign-table.json)")
    p.add_argument("--manifest", help="prereg manifest whose sha256 the plan carries "
                                      "(default: prereg/manifest-campaign.json; without it no plan is drawn)")
    p.add_argument("--lead-slots", type=int, default=900, help="no window earlier than this many slots ahead")
    p.add_argument("--data", help="data directory (default: repo data/)")
    p = sub.add_parser("panel", help="pick the leader panel of an epoch")
    p.add_argument("--network", help="network (default: ITB_NETWORK or mainnet)")
    p.add_argument("--epoch", type=int, help="current epoch (default) or the next one")
    p.add_argument("--data", help="data directory (default: repo data/)")
    p = sub.add_parser("manifest", help="hash the pre-registered files of a stage into prereg/")
    p.add_argument("--stage", required=True, choices=verify.PREREG_STAGES)
    p.add_argument("--file", action="append",
                   help="repository file to list (repeatable; default: MANIFEST_FILES of verify.py)")
    p.add_argument("--panel", help="campaign: the panel.json the campaign runs on, repository path")
    p.add_argument("--data", help="data directory with prereg-anchors.json (default: repo data/)")
    p = sub.add_parser("channel", help="line health: rounds of a run, getSlot round trips, campaign watch")
    p.add_argument("what", choices=("rounds", "rpc", "watch"))
    p.add_argument("run_id", nargs="?", help="run of rounds")
    p.add_argument("--data", help="data directory with runs/ (default: repo data/)")
    p.add_argument("--logs", help="directory of the run logs (default: repo logs/)")
    p.add_argument("--all", action="store_true", help="rounds: also rounds whose windows are not all done")
    p.add_argument("--gate", action="store_true", help="rounds, rpc: exit 3 when a threshold is missed")
    p.add_argument("--seconds", type=float, default=180.0, help="rpc: length of the series (default 180)")
    p.add_argument("--interval", type=float, default=2.0, help="rpc: seconds between requests (default 2)")
    p.add_argument("--journal", help="watch: JSON-lines journal the finished rounds are appended to")
    p.add_argument("--stage", default="campaign", help="watch: stage of the live runs (default campaign)")
    p.add_argument("--transcript", help="watch: campaign.sh transcript; its last line ends the watch")
    p.add_argument("--poll", type=float, default=60.0, help="watch: seconds between reads (default 60)")
    args = parser.parse_args(argv)
    if args.cmd == "channel" and args.what == "rounds" and not args.run_id:
        parser.error("channel rounds needs a run id")
    # Operator names carry emoji; a Windows console in a legacy code page prints them escaped.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")
    handlers = {
        "reproduce": cmd_reproduce, "selftest": cmd_selftest, "verify": cmd_verify,
        "analyze": cmd_analyze, "report": cmd_report, "claim": cmd_claim, "collect": cmd_collect,
        "check-raw": cmd_check_raw, "plan": cmd_plan, "panel": cmd_panel, "table": cmd_table,
        "pilot": cmd_pilot, "minimum": cmd_minimum, "campaign-table": cmd_campaign_table,
        "campaign": cmd_campaign, "manifest": cmd_manifest, "channel": cmd_channel, None: cmd_reproduce,
    }
    return handlers[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
