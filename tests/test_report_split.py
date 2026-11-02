"""The report over two files: python -m unittest discover -s tests

REPORT.md holds the answer and DETAILS.md every other table, and `python -m itb report`
writes the blocks of both. A generated block that stands in neither file would drop out
of the report unnoticed, and one that stands in both would be written twice; placement
names each case, and the command fails on it both when it writes and when it checks. The table of forms puts each class and cell on one line with its violated
pair share, and a cell without data reads "-"."""

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
from itb import report  # noqa: E402


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
