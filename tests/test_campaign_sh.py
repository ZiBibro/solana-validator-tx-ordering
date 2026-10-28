"""scripts/campaign.sh with stand-ins for docker and git on PATH: an epoch index whose
chain epoch has passed is lost at once and never drawn again (campaign addendum,
section 5). A copy of the script without that branch must retry and stop, which the
second test shows. Needs bash; skipped where there is none."""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SCRIPT = os.path.join(REPO, "scripts", "campaign.sh")
PASSED_BRANCH = '                *"has passed"*) echo "epoch index $e is lost: its chain epoch has passed"; break ;;\n'

DOCKER = """#!/usr/bin/env bash
echo "$*" >> "$ITB_TEST_CALLS"
case "$*" in
    *"plan campaign"*) echo "campaign: chain epoch 1071 has passed (now 1072); epoch index 0 is lost" >&2; exit 1 ;;
esac
exit 0
"""

GIT = """#!/usr/bin/env bash
case "$*" in
    *rev-parse*) echo 0000000000000000000000000000000000000000 ;;
esac
exit 0
"""


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
        for name, body in (("docker", DOCKER), ("git", GIT)):
            path = os.path.join(self.bin, name)
            with open(path, "w", newline="\n") as f:
                f.write(body)
            os.chmod(path, 0o755)
        self.calls = os.path.join(root, "calls.txt")

    def tearDown(self):
        self.tmp.cleanup()

    def run_script(self, drop=None):
        with open(SCRIPT, encoding="utf-8") as f:
            text = f.read()
        self.assertEqual(text.count("pause=600"), 1)
        text = text.replace("pause=600", "pause=0")
        if drop is not None:
            self.assertEqual(text.count(drop), 1)
            text = text.replace(drop, "")
        script = os.path.join(self.repo, "scripts", "campaign.sh")
        with open(script, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        env = dict(os.environ, PATH=self.bin + os.pathsep + os.environ.get("PATH", ""),
                   ITB_WALLET_KEY_FILE=self.key.replace("\\", "/"), ITB_TEST_CALLS=self.calls.replace("\\", "/"))
        for name in ("ITB_EXTRA_CA_PEM", "ITB_EXTRA_CA_FILE"):
            env.pop(name, None)
        done = subprocess.run([_bash(), script.replace("\\", "/"), "data/panels/p/panel.json", "1071", "0", "0"],
                              env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
        with open(self.calls) as f:
            calls = f.read().splitlines()
        return done.returncode, done.stdout.decode("utf-8", "replace"), calls

    def test_passed_epoch_is_lost_without_a_retry(self):
        code, out, calls = self.run_script()
        self.assertEqual(code, 0, out)
        self.assertIn("epoch index 0 is lost: its chain epoch has passed", out)
        self.assertIn("campaign done", out)
        self.assertEqual(len(calls), 1, calls)
        self.assertIn("--nodes-from-first-plan", calls[0])

    def test_script_without_the_branch_retries_and_stops(self):
        code, out, calls = self.run_script(drop=PASSED_BRANCH)
        self.assertEqual(code, 1, out)
        self.assertIn("campaign stopped at epoch index 0 after 3 attempts", out)
        self.assertEqual(len(calls), 3, calls)


if __name__ == "__main__":
    unittest.main()
