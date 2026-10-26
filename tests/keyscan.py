"""Search everything a run wrote for the bytes of its wallet key.

Usage: python keyscan.py KEY_FILE ROOT [ROOT ...]

The secrets are the wallet seed and the twelve payer seeds the probe derives from
it (probe/src/keys.rs). Each is searched raw, as hex, as base64 at every byte
alignment, as base58, and as the decimal list of the solana-keygen file. Files
ending in .gz are searched after decompression. The scanner first proves it can
see every form in a file it writes itself, and refuses to pass on zero files.

Exit 0: no hit. Exit 1: a hit (printed with file and form). Exit 2: the scanner
failed its own check or found nothing to scan.
"""

import base64
import gzip
import hashlib
import hmac
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from itb import b58  # noqa: E402

PAYERS = 12


def secrets_of(key_bytes):
    """[(label, secret bytes)]: wallet seed, wallet keypair, payer seeds."""
    seed = bytes(key_bytes[:32])
    out = [("wallet seed", seed), ("wallet keypair", bytes(key_bytes))]
    for n in range(1, PAYERS + 1):
        mac = hmac.new(seed, ("itb-payer-%d" % n).encode(), hashlib.sha512).digest()
        out.append(("payer %d seed" % n, mac[:32]))
    return out


def b64_cores(s, alphabet):
    """Base64 text of s at each of the three byte alignments, cut to the characters
    that depend on s alone, so a match inside a longer base64 string is found."""
    out = []
    for k in range(3):
        enc = alphabet(b"\0" * k + s).decode()
        first = -(-8 * k // 6)
        last = (8 * (k + len(s)) - 6) // 6
        out.append(enc[first:last + 1])
    return out


def forms(label, s):
    """[(form name, needle bytes)] for one secret."""
    out = [("raw", s), ("hex", s.hex().encode()), ("HEX", s.hex().upper().encode()),
           ("base58", b58.encode(s).encode())]
    for i, core in enumerate(b64_cores(s, base64.b64encode)):
        out.append(("base64@%d" % i, core.encode()))
    for i, core in enumerate(b64_cores(s, base64.urlsafe_b64encode)):
        out.append(("base64url@%d" % i, core.encode()))
    head = [str(b) for b in s[:12]]
    out.append(("decimal list", ",".join(head).encode()))
    out.append(("decimal list, spaced", ", ".join(head).encode()))
    return [("%s %s" % (label, name), needle) for name, needle in out]


def read(path):
    with open(path, "rb") as f:
        data = f.read()
    if path.endswith(".gz"):
        data = gzip.decompress(data)
    return data


def scan(paths, needles):
    hits = []
    for path in paths:
        data = read(path)
        for name, needle in needles:
            if needle in data:
                hits.append((path, name))
    return hits


def walk(roots, skip):
    out = []
    for root in roots:
        if os.path.isfile(root):
            out.append(root)
            continue
        for d, _, files in os.walk(root):
            for f in files:
                p = os.path.join(d, f)
                if os.path.realpath(p) not in skip:
                    out.append(p)
    return sorted(out)


def self_check(needles, seed):
    """Every form of every secret must be found in a file holding it in context."""
    missed = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, needle in needles:
            p = os.path.join(tmp, "probe.gz" if "base58" in name else "probe.txt")
            body = b"{\"x\": \"" + b"A" + needle + b"Z" + b"\"}"
            with open(p, "wb") as f:
                f.write(gzip.compress(body) if p.endswith(".gz") else body)
            if not scan([p], [(name, needle)]):
                missed.append(name)
        # A base64 blob that carries the wallet seed one byte in must be caught too.
        seed_needles = [n for n in needles if n[0].startswith("wallet seed base64@")]
        p = os.path.join(tmp, "blob.txt")
        with open(p, "wb") as f:
            f.write(base64.b64encode(b"\x07" + seed + b"\x09"))
        if not scan([p], seed_needles):
            missed.append("wallet seed inside a longer base64 blob")
    return missed


def main(argv):
    if len(argv) < 3:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    key_file, roots = argv[1], argv[2:]
    with open(key_file) as f:
        key_bytes = json.load(f)
    if len(key_bytes) != 64:
        print("keyscan: %s is not a 64-byte solana-keygen file" % key_file, file=sys.stderr)
        return 2
    needles = [n for label, s in secrets_of(key_bytes) for n in forms(label, s)]
    missed = self_check(needles, bytes(key_bytes[:32]))
    # The key file itself is the positive control on real input.
    if not any(name.startswith("wallet seed decimal list") for _, name in scan([key_file], needles)):
        missed.append("the key file itself")
    if missed:
        print("keyscan: self-check failed, cannot see: %s" % "; ".join(missed), file=sys.stderr)
        return 2
    files = walk(roots, {os.path.realpath(key_file)})
    if not files:
        print("keyscan: nothing to scan under %s" % ", ".join(roots), file=sys.stderr)
        return 2
    total = sum(len(read(p)) for p in files)
    hits = scan(files, needles)
    print("keyscan: %d secrets in %d forms each, %d files, %d bytes after decompression, %d hits"
          % (len(secrets_of(key_bytes)), len(needles) // len(secrets_of(key_bytes)), len(files), total, len(hits)))
    for path, name in hits:
        print("  HIT %s: %s" % (path, name))
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
