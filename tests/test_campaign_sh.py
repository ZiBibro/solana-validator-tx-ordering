"""scripts/campaign.sh with stand-ins for docker and git on PATH.

An epoch index whose chain epoch has passed is lost at once and never drawn again
(campaign addendum, section 5); a copy of the script without that branch must retry and
stop. On the happy path the stand-in answers with the lines the plan command and
`probe status` printed at the first campaign start (2026-10-28 02:12 UTC), and the script
must call the live run under the limit of committed plus fees plus overhead; a copy that
reads the journal with the pattern of the run line finds no number and never sends.
Needs bash; skipped where there is none."""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SCRIPT = os.path.join(REPO, "scripts", "campaign.sh")
PASSED_BRANCH = '                *"has passed"*) echo "epoch index $e is lost: its chain epoch has passed"; break ;;\n'
STATUS_PATTERN = r"'s|^spend journal [^:]*: \([0-9][0-9]*\) lamports committed,.*|\1|p'"
RUN_LINE_PATTERN = r"'s|^spend journal: \([0-9][0-9]*\) of .*|\1|p'"

DOCKER_PASSED = """#!/usr/bin/env bash
echo "$*" >> "$ITB_TEST_CALLS"
case "$*" in
    *"plan campaign"*) echo "campaign: chain epoch 1071 has passed (now 1072); epoch index 0 is lost" >&2; exit 1 ;;
esac
exit 0
"""

DOCKER_LIVE = """#!/usr/bin/env bash
echo "$*" >> "$ITB_TEST_CALLS"
case "$*" in
    *"plan campaign"*) cat "$ITB_TEST_REPLIES/plan.txt" ;;
    *"probe status"*) cat "$ITB_TEST_REPLIES/status.txt" ;;
    *"probe run"*) cat "$ITB_TEST_REPLIES/run.txt" ;;
esac
exit 0
"""

GIT = """#!/usr/bin/env bash
case "$*" in
    *rev-parse*) echo 0000000000000000000000000000000000000000 ;;
esac
exit 0
"""

# Verbatim from logs/campaign-20261028T021227Z.txt and the probe status of that start.
FIRST_PLAN = """\
campaign: plan carries prereg manifest /repo/prereg/manifest-campaign.json sha256 8e7d834a090444b4b9f84b5faa6311a74233a468d3c074ab9a779c7ac12e480d
campaign: gossip /repo/data/plans/campaign-mainnet-e1071-20261028T005742Z/cluster-nodes.json
campaign: /repo/data/plans/campaign-mainnet-e1071-20261028T021233Z/plan.json
campaign: epoch index 0 in epoch 1071, 144 bursts, 1728 probes, fees 9107400 lamports (8640000 base, 467400 priority); 213.3 ms per slot over 30 samples
  round 0 (part 0): 16 bursts, slots 462721436 to 462725996 (4560 slots), about 29.10 03:00 UTC to 29.10 03:17 UTC
  round 1 (part 1): 24 bursts, slots 462769692 to 462785280 (15588 slots), about 29.10 05:52 UTC to 29.10 06:47 UTC
  round 2 (part 2): 16 bursts, slots 462830128 to 462834240 (4112 slots), about 29.10 09:27 UTC to 29.10 09:41 UTC
  round 3 (part 3): 16 bursts, slots 462872092 to 462876816 (4724 slots), about 29.10 11:56 UTC to 29.10 12:13 UTC
  round 4 (part 4): 16 bursts, slots 462895568 to 462901120 (5552 slots), about 29.10 13:19 UTC to 29.10 13:39 UTC
  round 5 (part 5): 16 bursts, slots 462989656 to 462995168 (5512 slots), about 29.10 18:54 UTC to 29.10 19:13 UTC
  round 6 (part 6): 16 bursts, slots 463008832 to 463012868 (4036 slots), about 29.10 20:02 UTC to 29.10 20:16 UTC
  round 7 (part 7): 24 bursts, slots 463092440 to 463102024 (9584 slots), about 30.10 00:59 UTC to 30.10 01:33 UTC
campaign: note: windows scanned with the gossip snapshot of 2026-10-28T00:57:37.293394Z
"""
FIRST_STATUS = """\
spend journal /state/spend-journal-mainnet.jsonl: 4355230 lamports committed, 4355230 settled, 0 bookings pending (0 lamports)
raw data /data: 1884 probes, next burst_seq from data 157
"""
# The line probe/src/session.rs prints when a live run starts.
LIVE_RUN = "itb-probe LIVE run campaign-mainnet-20261028T021300Z: 144 bursts, spend limit 13527630 lamports\n"
LIMIT = 4355230 + 9107400 + 65000


def _bash():
    found = shutil.which("bash")
    # On Windows, System32\\bash.exe starts WSL, which does not see this PATH.
    if found and sys.platform == "win32" and "system32" in found.lower():
        return None
    return found


@unittest.skipIf(_bash() is None, "no bash")
class CampaignScript(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = self.tmp.name
        self.repo = os.path.join(root, "repo")
        os.makedirs(os.path.join(self.repo, "scripts"))
        os.makedirs(os.path.join(self.repo, "prereg"))
        os.makedirs(os.path.join(self.repo, "data", "panels", "p"))
        for path in (os.path.join("prereg", "manifest-campaign.json"), os.path.join("data", "panels", "p", "panel.json")):
            with open(os.path.join(self.repo, path), "w") as f:
                f.write("{}\n")
        self.key = os.path.join(root, "key.json")
        with open(self.key, "w") as f:
            f.write("[]\n")
        self.bin = os.path.join(root, "bin")
        os.makedirs(self.bin)
        self.write_exe("git", GIT)
        self.replies = os.path.join(root, "replies")
        os.makedirs(self.replies)
        for name, body in (("plan.txt", FIRST_PLAN), ("status.txt", FIRST_STATUS), ("run.txt", LIVE_RUN)):
            with open(os.path.join(self.replies, name), "w", newline="\n") as f:
                f.write(body)
        self.calls = os.path.join(root, "calls.txt")

    def tearDown(self):
        self.tmp.cleanup()

    def write_exe(self, name, body):
        path = os.path.join(self.bin, name)
        with open(path, "w", newline="\n") as f:
            f.write(body)
        os.chmod(path, 0o755)

    def run_script(self, docker, drop=None, swap=None):
        self.write_exe("docker", docker)
        with open(SCRIPT, encoding="utf-8") as f:
            text = f.read()
        self.assertEqual(text.count("pause=600"), 1)
        text = text.replace("pause=600", "pause=0")
        if drop is not None:
            self.assertEqual(text.count(drop), 1)
            text = text.replace(drop, "")
        if swap is not None:
            self.assertEqual(text.count(swap[0]), 1)
            text = text.replace(swap[0], swap[1])
        script = os.path.join(self.repo, "scripts", "campaign.sh")
        with open(script, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        env = dict(os.environ, PATH=self.bin + os.pathsep + os.environ.get("PATH", ""),
                   ITB_WALLET_KEY_FILE=self.key.replace("\\", "/"), ITB_TEST_CALLS=self.calls.replace("\\", "/"),
                   ITB_TEST_REPLIES=self.replies.replace("\\", "/"))
        for name in ("ITB_EXTRA_CA_PEM", "ITB_EXTRA_CA_FILE"):
            env.pop(name, None)
        done = subprocess.run([_bash(), script.replace("\\", "/"), "data/panels/p/panel.json", "1071", "0", "0"],
                              env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
        with open(self.calls) as f:
            calls = f.read().splitlines()
        return done.returncode, done.stdout.decode("utf-8", "replace"), calls

    def test_passed_epoch_is_lost_without_a_retry(self):
        code, out, calls = self.run_script(DOCKER_PASSED)
        self.assertEqual(code, 0, out)
        self.assertIn("epoch index 0 is lost: its chain epoch has passed", out)
        self.assertIn("campaign done", out)
        self.assertEqual(len(calls), 1, calls)
        self.assertIn("--nodes-from-first-plan", calls[0])

    def test_script_without_the_branch_retries_and_stops(self):
        code, out, calls = self.run_script(DOCKER_PASSED, drop=PASSED_BRANCH)
        self.assertEqual(code, 1, out)
        self.assertIn("campaign stopped at epoch index 0 after 3 attempts", out)
        self.assertEqual(len(calls), 3, calls)

    def test_live_run_gets_the_limit_from_the_status_line(self):
        code, out, calls = self.run_script(DOCKER_LIVE)
        self.assertEqual(code, 0, out)
        self.assertIn("== live run: limit %d lamports = committed 4355230 + plan fees 9107400 + overhead 65000" % LIMIT, out)
        runs = [c for c in calls if "probe run" in c]
        self.assertEqual(len(runs), 1, calls)
        self.assertTrue(runs[0].endswith("-T probe run --plan /data/plans/campaign-mainnet-e1071-20261028T021233Z/plan.json"
                                         " --live --max-spend-lamports %d --close-after" % LIMIT), runs[0])
        self.assertTrue(any(c.endswith("collect collect campaign-mainnet-20261028T021300Z --network mainnet") for c in calls), calls)
        self.assertTrue(any(c.endswith("plan channel rounds campaign-mainnet-20261028T021300Z --all") for c in calls), calls)
        self.assertIn("campaign done", out)

    def test_run_line_pattern_finds_no_number_and_never_sends(self):
        code, out, calls = self.run_script(DOCKER_LIVE, swap=(STATUS_PATTERN, RUN_LINE_PATTERN))
        self.assertEqual(code, 1, out)
        self.assertIn("plan path, fee total or committed lamports missing", out)
        self.assertIn("campaign stopped at epoch index 0 after 3 attempts", out)
        self.assertFalse([c for c in calls if "probe run" in c], calls)


if __name__ == "__main__":
    unittest.main()
