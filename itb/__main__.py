"""Command line of the Python side.

    python -m itb reproduce        selftest, then verify, then analyze with the REPORT check
    python -m itb selftest         known-answer checks only
    python -m itb verify           re-read every recorded signature from the chain
    python -m itb analyze          recompute every REPORT table from raw data
    python -m itb claim <id>       recompute one REPORT claim and re-check its slots
    python -m itb collect          append inclusion rows for a run
    python -m itb check-raw FILE   validate raw files against schema/raw-format.json

In Docker: docker compose run --rm reproduce [subcommand ...]
"""

import argparse
import os
import sys

from . import __version__, analyze, rawformat, selftest

EXIT_OK = 0
EXIT_FAIL = 1
EXIT_NOT_READY = 2

DEFAULT_DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


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


def cmd_verify(args):
    return _not_ready("verify", "build stage 3 of plan-implementation")


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
    return _not_ready("collect", "build stage 3 of plan-implementation")


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


def main(argv=None):
    parser = argparse.ArgumentParser(prog="itb", description=__doc__.split("\n")[0])
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("reproduce", help="selftest, verify, analyze")
    sub.add_parser("selftest", help="known-answer checks")
    sub.add_parser("verify", help="re-read every recorded signature from the chain")
    p = sub.add_parser("analyze", help="recompute REPORT from raw data")
    p.add_argument("--data", help="data directory with runs/ (default: repo data/)")
    p.add_argument("--stage", action="append", help="run stage to include (default: campaign)")
    p.add_argument("--out", help="write the full result as JSON here")
    p = sub.add_parser("claim", help="recompute one REPORT claim")
    p.add_argument("claim_id")
    sub.add_parser("collect", help="append inclusion rows for a run")
    p = sub.add_parser("check-raw", help="validate raw files")
    p.add_argument("files", nargs="*")
    args = parser.parse_args(argv)
    handlers = {
        "reproduce": cmd_reproduce, "selftest": cmd_selftest, "verify": cmd_verify,
        "analyze": cmd_analyze, "claim": cmd_claim, "collect": cmd_collect,
        "check-raw": cmd_check_raw, None: cmd_reproduce,
    }
    return handlers[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
