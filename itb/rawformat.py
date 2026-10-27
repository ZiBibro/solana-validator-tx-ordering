"""Raw row format: validation of single rows and of whole run files.

The canonical definition lives in schema/raw-format.json. This module only
interprets it, so the Rust probe (which checks its rows against the same file
in cargo test) and the Python side read one source.
"""

import gzip
import json
import os
import re

SCHEMA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "schema", "raw-format.json")

_B58 = re.compile(r"^[1-9A-HJ-NP-Za-km-z]+$")
_UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d{1,9})?)?Z$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
# Origin only: paid RPC endpoints carry API keys in userinfo, path or query, and
# raw rows are published, so anything after host[:port] is refused.
_ENDPOINT = re.compile(r"^(https?|wss?)://[A-Za-z0-9.-]+(:\d{1,5})?/?$")

# Section 4: transfer amount encodes the burst and the send rank.
RANKS_PER_BURST = 16


def load_schema(path=SCHEMA_PATH):
    with open(path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    if not schema.get("kinds"):
        raise ValueError("schema has no kinds: " + path)
    return schema


def _check_format(fmt, value):
    if fmt == "pubkey" or fmt == "hash":
        return bool(_B58.match(value)) and 32 <= len(value) <= 44
    if fmt == "signature":
        return bool(_B58.match(value)) and 64 <= len(value) <= 88
    if fmt == "utc":
        return bool(_UTC.match(value))
    if fmt == "sha256":
        return bool(_SHA256.match(value))
    if fmt == "endpoint":
        return bool(_ENDPOINT.match(value))
    raise ValueError("unknown format in schema: " + fmt)


def _check_scalar(base, value):
    """Return None when value matches the base type, else a short reason."""
    if base == "str":
        return None if isinstance(value, str) else "expected str"
    if base == "int":
        ok = isinstance(value, int) and not isinstance(value, bool)
        return None if ok else "expected int"
    if base == "num":
        ok = isinstance(value, (int, float)) and not isinstance(value, bool)
        return None if ok else "expected number"
    if base == "bool":
        return None if isinstance(value, bool) else "expected bool"
    if base == "obj":
        return None if isinstance(value, dict) else "expected object"
    if base.startswith("enum:"):
        allowed = base[len("enum:"):].split("|")
        return None if value in allowed else "expected one of " + ", ".join(allowed)
    raise ValueError("unknown type in schema: " + base)


def _check_value(spec, value):
    """Check one field value against its spec; return a list of reasons."""
    typ = spec["type"]
    nullable = typ.endswith("?")
    if nullable:
        typ = typ[:-1]
    if value is None:
        return [] if nullable else ["null not allowed"]
    if typ.startswith("list<"):
        inner = typ[len("list<"):-1]
        inner_nullable = inner.endswith("?")
        if inner_nullable:
            inner = inner[:-1]
        if not isinstance(value, list):
            return ["expected list"]
        out = []
        for i, item in enumerate(value):
            if item is None:
                if not inner_nullable:
                    out.append("[%d] null not allowed" % i)
                continue
            why = _check_scalar(inner, item)
            if why:
                out.append("[%d] %s" % (i, why))
            elif "format" in spec and not _check_format(spec["format"], item):
                out.append("[%d] bad %s" % (i, spec["format"]))
        return out
    why = _check_scalar(typ, value)
    if why:
        return [why]
    out = []
    if "format" in spec and not _check_format(spec["format"], value):
        out.append("bad " + spec["format"])
    if "min" in spec and value < spec["min"]:
        out.append("below min %s" % spec["min"])
    if "max" in spec and value > spec["max"]:
        out.append("above max %s" % spec["max"])
    return out


def validate_row(row, schema):
    """Return a list of problems for one decoded row (empty when valid).

    Rows of an older schema version stay valid: a field marked since N is
    required from version N on and may not appear in an older row.
    """
    if not isinstance(row, dict):
        return ["row is not an object"]
    problems = []
    v = row.get("v")
    if type(v) is not int or not 1 <= v <= schema["version"]:
        problems.append("v: expected 1 to %d" % schema["version"])
        v = schema["version"]
    kind = row.get("kind")
    spec = schema["kinds"].get(kind)
    if spec is None:
        return problems + ["kind: unknown %r" % (kind,)]
    fields = spec["fields"]
    for name in row:
        if name not in fields and name not in ("v", "kind"):
            problems.append(name + ": unknown field")
        elif name in fields and fields[name].get("since", 1) > v:
            problems.append("%s: not in version %d" % (name, v))
    for name, fspec in fields.items():
        if fspec.get("since", 1) > v:
            continue
        if name not in row:
            problems.append(name + ": missing")
            continue
        for why in _check_value(fspec, row[name]):
            problems.append(name + ": " + why)
    return problems


def read_jsonl(path):
    """Yield (line_number, row) for every non-empty line (gzip when .gz); bad JSON raises."""
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield n, json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError("%s:%d: not JSON (%s)" % (path, n, e))


def check_probe_file(path, schema):
    """Row and cross-row checks of one probes.jsonl. Returns (rows, problems).

    Cross-row rules (sections 4 and 8): the file opens with a run row; a probe
    follows its burst row; a send follows its probe row; send ranks and payers
    are unique inside a burst; the transfer amount equals
    burst_seq*16 + send_rank + 1.
    """
    problems = []
    rows = 0
    run_id = None
    bursts = {}
    probes = {}
    sent = set()
    for n, row in read_jsonl(path):
        rows += 1
        where = "%s:%d" % (os.path.basename(path), n)
        for why in validate_row(row, schema):
            problems.append("%s: %s" % (where, why))
        kind = row.get("kind") if isinstance(row, dict) else None
        if rows == 1:
            if kind != "run":
                problems.append(where + ": first row must be kind run")
            run_id = row.get("run_id") if isinstance(row, dict) else None
            continue
        if kind == "run":
            problems.append(where + ": second run row")
            continue
        if isinstance(row, dict) and row.get("run_id") != run_id:
            problems.append(where + ": run_id differs from the run row")
        seq = row.get("burst_seq") if isinstance(row, dict) else None
        if kind == "burst":
            if seq in bursts:
                problems.append("%s: burst_seq %s repeated" % (where, seq))
            bursts[seq] = {"ranks": set(), "payers": set(), "ended": False}
        elif kind in ("probe", "send", "burst_end"):
            b = bursts.get(seq)
            if b is None:
                problems.append("%s: %s before its burst row" % (where, kind))
                continue
            if kind == "probe":
                sig = row.get("signature")
                if sig in probes:
                    problems.append(where + ": signature repeated")
                probes[sig] = seq
                rank = row.get("send_rank")
                if rank in b["ranks"]:
                    problems.append("%s: send_rank %s repeated in burst" % (where, rank))
                b["ranks"].add(rank)
                payer = row.get("payer_index")
                if payer in b["payers"]:
                    problems.append("%s: payer_index %s repeated in burst" % (where, payer))
                b["payers"].add(payer)
                if isinstance(seq, int) and isinstance(rank, int):
                    want = seq * RANKS_PER_BURST + rank + 1
                    if row.get("transfer_lamports") != want:
                        problems.append("%s: transfer_lamports %s, expected %d" %
                                        (where, row.get("transfer_lamports"), want))
            elif kind == "send":
                sig = row.get("signature")
                if probes.get(sig) != seq:
                    problems.append(where + ": send without an earlier probe row")
                if sig in sent:
                    problems.append(where + ": second send row for the signature")
                sent.add(sig)
            else:
                b["ended"] = True
    if rows == 0:
        problems.append(os.path.basename(path) + ": empty file")
    return rows, problems


def check_rows_file(path, schema):
    """Row-level checks of any other raw file (collect.jsonl, logs)."""
    problems = []
    rows = 0
    for n, row in read_jsonl(path):
        rows += 1
        for why in validate_row(row, schema):
            problems.append("%s:%d: %s" % (os.path.basename(path), n, why))
    if rows == 0:
        problems.append(os.path.basename(path) + ": empty file")
    return rows, problems
