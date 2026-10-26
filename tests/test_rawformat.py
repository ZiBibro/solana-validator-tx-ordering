"""Unit tests of the raw format and base58: python -m unittest discover -s tests"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from itb import b58, rawformat, selftest  # noqa: E402


class Base58(unittest.TestCase):
    def test_system_program_is_32_zero_bytes(self):
        self.assertEqual(b58.decode("11111111111111111111111111111111"), bytes(32))

    def test_token_program_bytes(self):
        # spl-token program id as the byte array published in its source.
        want = bytes([6, 221, 246, 225, 215, 101, 161, 147, 217, 203, 225, 70, 206, 235, 121,
                      172, 28, 180, 133, 237, 95, 91, 55, 145, 58, 140, 245, 133, 126, 255, 0, 169])
        self.assertEqual(b58.decode("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), want)
        self.assertEqual(b58.encode(want), "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")

    def test_rejects_non_alphabet(self):
        with self.assertRaises(ValueError):
            b58.decode("0OIl")


class RawFormat(unittest.TestCase):
    def test_schema_kinds(self):
        schema = rawformat.load_schema()
        for kind in ("run", "round", "burst", "probe", "send", "burst_end", "slot",
                     "inclusion", "block_tx", "log"):
            self.assertIn(kind, schema["kinds"])

    def test_selftest_group_passes(self):
        checks = selftest.raw_format_checks()
        self.assertGreater(len(checks), 0)
        failed = [(n, d) for n, ok, d in checks if not ok]
        self.assertEqual(failed, [])


if __name__ == "__main__":
    unittest.main()
