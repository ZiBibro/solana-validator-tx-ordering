"""Known-answer tests of tests/keyscan.py: it finds every form of the key, stays
quiet on clean output, and refuses to pass on nothing."""

import base64
import gzip
import hashlib
import hmac
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import keyscan  # noqa: E402


class KeyScan(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        # Any 64 bytes do: the scanner never checks the public half.
        self.key = list(hashlib.sha512(b"itb-keyscan-test").digest())
        self.key_file = os.path.join(self.dir, "key.json")
        with open(self.key_file, "w") as f:
            json.dump(self.key, f)
        self.out = os.path.join(self.dir, "out")
        os.makedirs(self.out)

    def tearDown(self):
        self.tmp.cleanup()

    def run_scan(self):
        with redirect_stdout(io.StringIO()) as o, redirect_stderr(io.StringIO()):
            code = keyscan.main(["keyscan", self.key_file, self.out])
        return code, o.getvalue()

    def write(self, name, data):
        with open(os.path.join(self.out, name), "wb") as f:
            f.write(data)

    def test_clean_output_passes(self):
        self.write("log.jsonl", b'{"event": "start", "payer": "9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin"}\n')
        self.assertEqual(self.run_scan()[0], 0)

    def test_nothing_to_scan_fails(self):
        self.assertEqual(self.run_scan()[0], 2)

    def test_every_form_is_found(self):
        seed = bytes(self.key[:32])
        payer = hmac.new(seed, b"itb-payer-7", hashlib.sha512).digest()[:32]
        cases = {
            "raw": seed,
            "hex": b"x" + seed.hex().encode(),
            "base64 shifted": base64.b64encode(b"\x01\x02" + seed),
            "keypair base58": keyscan.b58.encode(bytes(self.key)).encode(),
            "decimal list": json.dumps(self.key).encode(),
            "payer seed hex, compressed": gzip.compress(payer.hex().upper().encode()),
        }
        for name, data in cases.items():
            with self.subTest(name):
                for f in os.listdir(self.out):
                    os.remove(os.path.join(self.out, f))
                self.write("probe.jsonl.gz" if "compressed" in name else "probe.jsonl", data)
                code, text = self.run_scan()
                self.assertEqual(code, 1, text)
                self.assertIn("HIT", text)


if __name__ == "__main__":
    unittest.main()
