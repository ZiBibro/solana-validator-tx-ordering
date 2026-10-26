"""Command line of the Python side.

    python -m itb reproduce        selftest, then verify, then analyze with the REPORT check
    python -m itb selftest         known-answer checks only
    python -m itb verify           re-read every recorded signature from the chain
    python -m itb analyze          recompute every REPORT table from raw data
    python -m itb claim <id>       recompute one REPORT claim and re-check its slots
    python -m itb collect [run]    write inclusion and slot rows of runs from the chain
    python -m itb check-raw FILE   validate raw files against schema/raw-format.json
    python -m itb plan             draw a test plan for the probe from the live leader schedule

In Docker: docker compose run --rm reproduce [subcommand ...]
"""

import argparse
import os
import sys

from . import __version__, analyze, collect, rawformat, rpc, selftest, verify
from . import plan as planmod

EXIT_OK = 0
EXIT_FAIL = 1
EXIT_NOT_READY = 2

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DATA = os.path.join(REPO_DIR, "data")
DEFAULT_RPC = "https://api.mainnet-beta.solana.com"


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


def cmd_claim(args):
    return _not_ready("claim", "comes with the REPORT writer, which needs the pilot data")


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
                       ("analyze", cmd_analyze)):
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


def cmd_plan(args):
    network = _network(args)
    stage = args.stage or (network if network in ("localnet", "devnet") else None)
    if stage not in planmod.TEST_STAGES:
        print("plan: --stage must be one of %s for a drawn plan" % ", ".join(planmod.TEST_STAGES),
              file=sys.stderr)
        return EXIT_FAIL
    seed = args.seed or planmod.new_seed()
    leaders = args.leader or None
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
    stamp = planmod.utc_now().replace("-", "").replace(":", "").split(".")[0] + "Z"
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


def main(argv=None):
    parser = argparse.ArgumentParser(prog="itb", description=__doc__.split("\n")[0])
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("reproduce", help="selftest, verify, analyze")
    sub.add_parser("selftest", help="known-answer checks")
    p = sub.add_parser("verify", help="re-read every recorded signature from the chain")
    p.add_argument("--data", help="data directory with runs/ (default: repo data/)")
    p.add_argument("--network", help="network of the runs to verify (default: ITB_NETWORK or mainnet)")
    p = sub.add_parser("analyze", help="recompute REPORT from raw data")
    p.add_argument("--data", help="data directory with runs/ (default: repo data/)")
    p.add_argument("--stage", action="append", help="run stage to include (default: campaign)")
    p.add_argument("--out", help="write the full result as JSON here")
    p = sub.add_parser("claim", help="recompute one REPORT claim")
    p.add_argument("claim_id")
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
    p.add_argument("--per-leader", type=int, help="at most this many windows per leader")
    p.add_argument("--path", choices=("quic", "rpc"), default="quic")
    p.add_argument("--probes", type=int, default=planmod.PAYERS, help="probes per burst, 2 to 12")
    p.add_argument("--seed", help="seed of the draw (default: random, printed)")
    p.add_argument("--data", help="data directory (default: repo data/)")
    args = parser.parse_args(argv)
    handlers = {
        "reproduce": cmd_reproduce, "selftest": cmd_selftest, "verify": cmd_verify,
        "analyze": cmd_analyze, "claim": cmd_claim, "collect": cmd_collect,
        "check-raw": cmd_check_raw, "plan": cmd_plan, None: cmd_reproduce,
    }
    return handlers[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
