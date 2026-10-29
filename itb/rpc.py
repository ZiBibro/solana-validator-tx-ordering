"""JSON-RPC client of the Python side, standard library only.

Every getBlock and getTransaction goes through get_block and get_transaction,
which always pass maxSupportedTransactionVersion 1 as an integer. Probes are v1
transactions, and without that field a node answers -32015 for such a
transaction and for the whole block that holds one (plan section 9).

The public node limits getBlock through x-ratelimit-method-limit (6 on
2026-10-26). The client reads that header and keeps each method under it, so a
long verify paces itself instead of collecting 429 answers.
"""

import gzip
import http.client
import json
import time
import urllib.error
import urllib.parse
import urllib.request

from . import __version__

MAX_TX_VERSION = 1
RATE_WINDOW_S = 10.0  # the public node counts method limits per 10 s window
SIGNATURE_PAGE = 1000  # getSignaturesForAddress returns at most 1000 per call
STATUS_BATCH = 256  # getSignatureStatuses takes at most 256 signatures

# Answers that mean "no block here" rather than a failure of the node.
NO_BLOCK_CODES = (-32004, -32007, -32009)
BLOCK_NOT_AVAILABLE = -32004  # the node has not rooted the slot yet

# JSON-RPC errors the node asks to retry. In Agave's custom_error.rs only -32019,
# LongTermStorageUnreachable, says "please try again", and only reads of long-term
# storage return it. A public node returned it to getSignaturesForAddress on
# 2026-10-29 and failed a campaign run at its start.
TRANSIENT_CODES = (-32019,)


class RpcError(Exception):
    def __init__(self, method, error):
        self.method = method
        self.error = error
        self.code = error.get("code") if isinstance(error, dict) else None
        super().__init__("%s: %s" % (method, json.dumps(error)))


def origin(url):
    """scheme://host[:port] of a URL: paid RPC URLs carry API keys in the path or
    query, and raw data is published (schema format "endpoint")."""
    parts = urllib.parse.urlsplit(url)
    host = parts.hostname or ""
    if ":" in host:
        host = "[%s]" % host
    port = ":%d" % parts.port if parts.port else ""
    return "%s://%s%s" % (parts.scheme, host, port)


def _retry_after(headers):
    try:
        return max(0.0, float(headers.get("retry-after")))
    except (TypeError, ValueError):
        return None


class Client:
    """Synchronous JSON-RPC over HTTP(S). call() returns the result field."""

    def __init__(self, url, timeout=90, retries=6, sleep=time.sleep, clock=time.monotonic):
        self.url = url
        self.timeout = timeout
        self.retries = retries
        self.sleep = sleep
        self.clock = clock
        self.method_limit = {}
        self.last_call = {}
        self.calls = {}
        self.bytes = 0

    def interval(self, method):
        limit = self.method_limit.get(method)
        return RATE_WINDOW_S / limit if limit else 0.0

    def _pace(self, method):
        gap = self.interval(method)
        last = self.last_call.get(method)
        if gap and last is not None:
            wait = last + gap - self.clock()
            if wait > 0:
                self.sleep(wait)
        self.last_call[method] = self.clock()

    def _note(self, method, headers):
        try:
            limit = int(headers.get("x-ratelimit-method-limit"))
        except (TypeError, ValueError):
            return
        if limit > 0:
            self.method_limit[method] = limit

    def call(self, method, params):
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method,
                           "params": params}).encode()
        headers = {"content-type": "application/json", "accept-encoding": "gzip",
                   "user-agent": "inside-the-block/" + __version__}
        last = None
        for attempt in range(self.retries):
            self._pace(method)
            request = urllib.request.Request(self.url, body, headers)
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as reply:
                    raw = reply.read()
                    self._note(method, reply.headers)
                    if reply.headers.get("content-encoding") == "gzip":
                        raw = gzip.decompress(raw)
            except urllib.error.HTTPError as e:
                self._note(method, e.headers)
                if e.code == 429 or e.code >= 500:
                    last = "HTTP %d" % e.code
                    self.sleep(_retry_after(e.headers) or min(30.0, 2.0 ** attempt))
                    continue
                raise RpcError(method, {"message": "HTTP %d" % e.code})
            except (OSError, EOFError, http.client.HTTPException) as e:
                # OSError covers URLError, timeouts, resets and a broken gzip stream;
                # HTTPException covers a body cut short (IncompleteRead), which the
                # public node sent on a 0.9 MB getBlock on 2026-10-27.
                last = "%s: %s" % (type(e).__name__, str(e)[:120])
                self.sleep(min(30.0, 2.0 ** attempt))
                continue
            self.calls[method] = self.calls.get(method, 0) + 1
            self.bytes += len(raw)
            answer = json.loads(raw)
            if "error" not in answer:
                return answer["result"]
            error = RpcError(method, answer["error"])
            if error.code not in TRANSIENT_CODES or attempt + 1 == self.retries:
                raise error
            last = "RPC error %s" % error.code
            self.sleep(min(30.0, 2.0 ** attempt))
        raise RpcError(method, {"message": "gave up after %d attempts: %s" % (self.retries, last)})


def block_params(details="full", rewards=True, commitment="finalized"):
    return {"encoding": "json", "transactionDetails": details, "rewards": rewards,
            "commitment": commitment, "maxSupportedTransactionVersion": MAX_TX_VERSION}


def get_block(client, slot, details="full", rewards=True, commitment="finalized", attempts=1):
    """Block of a slot, or None when the slot was skipped or is not stored.

    A caller that knows the slot holds a finalized block passes attempts above 1:
    a null result and -32004 are then asked again, and the last one raises.
    Agave's get_block keeps only BlockNotFound of long-term storage as an error
    and answers null on every other failure there (rpc.rs, master on 2026-10-29),
    so null proves no skipped slot; a skipped one comes back as -32007 or -32009."""
    params = [slot, block_params(details, rewards, commitment)]
    for attempt in range(attempts):
        try:
            block = client.call("getBlock", params)
        except RpcError as e:
            if e.code not in NO_BLOCK_CODES:
                raise
            if attempts == 1 or e.code != BLOCK_NOT_AVAILABLE:
                return None
            why = "error %s" % e.code
        else:
            if block is not None or attempts == 1:
                return block
            why = "a null result"
        if attempt + 1 < attempts:
            client.sleep(min(30.0, 2.0 ** attempt))
    raise RpcError("getBlock", {"message": "slot %d: %s after %d attempts" % (slot, why, attempts)})


def get_transaction(client, signature, commitment="finalized"):
    return client.call("getTransaction", [signature, {
        "encoding": "json", "commitment": commitment,
        "maxSupportedTransactionVersion": MAX_TX_VERSION}])


def signature_statuses(client, signatures, history=True):
    """{signature: status or None}. With history the node searches long-term
    storage once per signature missing from its status cache, and Agave answers
    null when that search fails; without it only the status cache answers."""
    out = {}
    for i in range(0, len(signatures), STATUS_BATCH):
        part = signatures[i:i + STATUS_BATCH]
        result = client.call("getSignatureStatuses",
                             [part, {"searchTransactionHistory": history}])
        for signature, status in zip(part, result["value"]):
            out[signature] = status
    return out


def signatures_for_address(client, address, commitment="finalized"):
    """Whole history of an address, newest first: pages through `before`,
    because one call returns at most 1000 entries (section 9). A page shorter
    than that is the last one: Agave fills a page from long-term storage when
    its own ledger runs short and reports a failure there as -32019, never as a
    short page, so asking once more would only buy a slow empty answer."""
    out = []
    before = None
    while True:
        options = {"limit": SIGNATURE_PAGE, "commitment": commitment}
        if before:
            options["before"] = before
        page = client.call("getSignaturesForAddress", [address, options])
        out.extend(page)
        if len(page) < SIGNATURE_PAGE:
            return out
        before = page[-1]["signature"]
