"""The report over two files: python -m unittest discover -s tests

REPORT.md holds the answer and DETAILS.md every other table, and `python -m itb report`
writes the blocks of both. A generated block that stands in neither file would drop out
of the report unnoticed, and one that stands in both would be written twice; placement
names each case, and the command fails on it both when it writes and when it checks. The table of forms puts each class and cell on one line with its violated
pair share, and a cell without data reads "-". A pointer in DETAILS must lead to the
REPORT section that holds its block, a run missing from the published table is named,
and a run without a recorded commit reads "-"."""

import argparse
import contextlib
import io
import os
import shutil
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from itb import __main__ as cli  # noqa: E402
from itb import analyze, report  # noqa: E402


def _block(name, body="x"):
    return "\n".join(["<!-- itb:begin %s -->" % name, body, report.END % name])


class Placement(unittest.TestCase):
    def test_each_block_once_passes(self):
        texts = ["# Report\n\n" + _block("a") + "\n", "# Details\n\n" + _block("b") + "\n"]
        self.assertEqual(report.placement(texts, {"a": "", "b": ""}), [])

    def test_a_block_in_no_file_is_named(self):
        texts = ["# Report\n\n" + _block("a") + "\n", "# Details\n"]
        self.assertEqual(report.placement(texts, {"a": "", "b": ""}), ["blocks in no report file: b"])

    def test_a_block_in_two_files_is_named(self):
        texts = [_block("a") + "\n" + _block("b"), _block("b")]
        self.assertEqual(report.placement(texts, {"a": "", "b": ""}), ["blocks in more than one place: b"])

    def test_a_block_twice_in_one_file_is_named(self):
        texts = [_block("a") + "\n" + _block("a")]
        self.assertEqual(report.placement(texts, {"a": ""}), ["blocks in more than one place: a"])


class Command(unittest.TestCase):
    """python -m itb report over two temporary files, with two generated blocks stood in."""

    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="itb-report-")
        self.addCleanup(shutil.rmtree, self.dir)
        saved = (cli.DEFAULT_REPORTS, report.blocks)
        self.addCleanup(self._restore, saved)
        report.blocks = lambda data_dir, repo_dir: {"a": "A", "b": "B"}

    @staticmethod
    def _restore(saved):
        cli.DEFAULT_REPORTS, report.blocks = saved

    def _run(self, check, first, second):
        paths = []
        for name, text in (("REPORT.md", first), ("DETAILS.md", second)):
            paths.append(os.path.join(self.dir, name))
            with open(paths[-1], "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
        cli.DEFAULT_REPORTS = tuple(paths)
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            code = cli.cmd_report(argparse.Namespace(check=check, file=None, data=self.dir))
        return code, err.getvalue()

    def test_check_passes_with_each_block_once(self):
        self.assertEqual(self._run(True, _block("a", "A") + "\n", _block("b", "B") + "\n")[0], cli.EXIT_OK)

    def test_check_fails_on_a_block_in_no_file(self):
        code, err = self._run(True, _block("a", "A") + "\n", "# Details\n")
        self.assertEqual(code, cli.EXIT_FAIL)
        self.assertIn("blocks in no report file: b", err)

    def test_write_fails_on_a_block_in_two_files(self):
        code, err = self._run(False, _block("a", "A") + "\n" + _block("b", "B") + "\n", _block("b", "B") + "\n")
        self.assertEqual(code, cli.EXIT_FAIL)
        self.assertIn("blocks in more than one place: b", err)

    def test_check_names_a_run_the_published_table_lacks(self):
        report.blocks = lambda data_dir, repo_dir: {"runs": _runs("old", "new"), "b": "B"}
        code, err = self._run(True, _block("runs", _runs("old")) + "\n", _block("b", "B") + "\n")
        self.assertEqual(code, cli.EXIT_FAIL)
        self.assertIn("runs in data/ the published table does not list: new;", err)

    def test_check_fails_on_a_pointer_to_the_wrong_section(self):
        report.blocks = lambda data_dir, repo_dir: {"a": "A", "b": "B"}
        details = "## 6.1 Exclusions\n\n<!-- itb:in-report a -->\nIt stands in [REPORT.md](REPORT.md#2-other).\n"
        code, err = self._run(True, "## 1 Answer\n\n" + _block("a", "A") + "\n\n## 2 Other\n\n"
                              + _block("b", "B") + "\n", details)
        self.assertEqual(code, cli.EXIT_FAIL)
        self.assertIn("pointer a under '## 6.1 Exclusions' leads to REPORT #2-other", err)


def _runs(*ids):
    return "\n".join(["| Run | Commit |", "|---|---|"] + ["| `%s` | `-` |" % i for i in ids])


class Commit(unittest.TestCase):
    """A run records the commit it measured on, with -dirty for uncommitted changes, or
    none when ITB_GIT_COMMIT was not set; the runs table shows each without failing."""

    def test_suffix_stays(self):
        self.assertEqual(report._commit("b82bfd4c0ffee-dirty"), "b82bfd4-dirty")
        self.assertEqual(report._commit("b82bfd4c0ffee"), "b82bfd4")

    def test_a_run_without_a_commit_reads_dash(self):
        run = {"run_id": "r", "stage": "test", "network": "devnet", "mode": "dry-run",
               "started_utc": "2026-11-02T10:00:00Z", "git_commit": None}
        rows = report.runs_block([analyze.Run(run, {}, {}, {}, {}, {}, {})]).split("\n")
        self.assertEqual([c.strip() for c in rows[2].strip("|").split("|")][-1], "`-`")


class Pointers(unittest.TestCase):
    """A pointer in DETAILS names the block a REPORT section holds right under its heading,
    and a campaign subsection names the campaign twin of its pilot subsection's block."""

    REPORT = "## 4 Campaign results\n\n" + _block("campaign-exclusions") + "\n\n### 4.2 Pairs\n\n" \
        + _block("campaign-pairs") + "\n"

    def _details(self, name, anchor):
        return ("## 5 Pilot\n\n### 5.3 Pairs\n\n" + _block("pilot-pairs") + "\n\n## 6 Campaign\n\n"
                "### 6.3 Pairs\n\n<!-- itb:in-report %s -->\nThis table stands in "
                "[REPORT.md, section 4.2](REPORT.md#%s).\n" % (name, anchor))

    def test_a_true_pointer_passes(self):
        self.assertEqual(report.pointer_problems(self._details("campaign-pairs", "42-pairs"), self.REPORT), [])

    def test_a_section_without_the_block_is_named(self):
        out = report.pointer_problems(self._details("campaign-pairs", "4-campaign-results"), self.REPORT)
        self.assertEqual(len(out), 1)
        self.assertIn("leads to REPORT #4-campaign-results", out[0])

    def test_the_wrong_twin_is_named(self):
        out = report.pointer_problems(self._details("campaign-exclusions", "4-campaign-results"), self.REPORT)
        self.assertEqual(len(out), 1)
        self.assertIn("the pilot twin of this subsection holds pilot-pairs", out[0])

    def test_a_pointer_without_a_link_is_named(self):
        details = "### 6.3 Pairs\n\n<!-- itb:in-report campaign-pairs -->\nSee the report.\n"
        self.assertEqual(report.pointer_problems(details, self.REPORT),
                         ["pointer campaign-pairs under '### 6.3 Pairs' links no REPORT section"])

    def test_the_anchor_drops_dots_and_marks(self):
        self.assertEqual(report.slug("### 4.1 Hypotheses H3 and H4"), "41-hypotheses-h3-and-h4")


def _cell(cls, arm, timing, form, detail=None, share=None):
    return {"class": cls, "arm": arm, "timing": timing, "form": form, "detail": detail,
            "strictness": {"share": share} if share is not None else None}


class Forms(unittest.TestCase):
    def test_no_runs(self):
        self.assertEqual(report.forms_block(None), report.NO_RUNS)

    def test_one_line_per_class_in_column_order(self):
        result = {"cells": [
            _cell("Firedancer", "equal_fee", "pre300", "arrival-rule", "reverse", 1.0),
            _cell("Firedancer", "independent", "pre300", "fee-rule", "ties-reverse-arrival", 0.0),
            _cell("Agave", "denominator", "slot2", "undetermined", None, 0.381),
            _cell("Agave", "shared", "pre300", "fee-rule", "ties-unordered", None),
        ]}
        lines = report.forms_block(result).split("\n")
        self.assertEqual(len(lines), 4)
        head = [c.strip() for c in lines[0].strip("|").split("|")]
        self.assertEqual(head[0], "Class")
        self.assertEqual(head[1:], ["%s %s" % col for col in report.FORM_COLUMNS])
        fire = [c.strip() for c in lines[2].strip("|").split("|")]
        agave = [c.strip() for c in lines[3].strip("|").split("|")]
        col = {name: i for i, name in enumerate(head)}
        self.assertEqual(fire[0], "Firedancer")
        self.assertEqual(fire[col["equal_fee pre300"]], "arrival-rule reverse (1.00)")
        self.assertEqual(fire[col["independent pre300"]], "fee-rule ties-reverse-arrival (0.00)")
        self.assertEqual(fire[col["shared slot2"]], "-")
        self.assertEqual(agave[0], "Agave")
        self.assertEqual(agave[col["denominator slot2"]], "undetermined (0.38)")
        self.assertEqual(agave[col["shared pre300"]], "fee-rule ties-unordered")


if __name__ == "__main__":
    unittest.main()
