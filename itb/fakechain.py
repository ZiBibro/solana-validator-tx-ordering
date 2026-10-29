"""An in-memory chain that answers the RPC methods collect and verify use, so
selftest can run both against a world whose answer is known, without network.

Like a real node it refuses getBlock and getTransaction with -32015 when the
answer holds a v1 transaction and the request does not carry
maxSupportedTransactionVersion as an integer of at least 1 (plan section 9).
"""

import copy
import json
import os
import random

from . import b58, chain, rpc, synth

LOADED_DATA_LIMIT = 32768
CU_LIMIT = 1000


def _transfer(amount):
    return b58.encode(chain.TRANSFER_TAG.to_bytes(4, "little") + amount.to_bytes(8, "little"))


def probe_entry(payer, signature, amount, priority_fee, cu_limit, other=None, extra_ix=b""):
    """A v1 probe as getBlock returns it: a self-transfer carrying the code and,
    in the shared arm, a 0-lamport transfer that write-locks `other`."""
    keys = [payer] + ([other] if other else []) + [chain.SYSTEM_PROGRAM]
    system = len(keys) - 1
    ixs = [{"programIdIndex": system, "accounts": [0, 0], "data": _transfer(amount),
            "stackHeight": 1}]
    if other:
        ixs.append({"programIdIndex": system, "accounts": [0, 1], "data": _transfer(0),
                    "stackHeight": 1})
    if extra_ix:
        keys.append(sorted(chain.MEMO_PROGRAMS)[0])
        ixs.append({"programIdIndex": len(keys) - 1, "accounts": [], "data": b58.encode(extra_ix),
                    "stackHeight": 1})
    message = {"accountKeys": keys,
               "header": {"numRequiredSignatures": 1, "numReadonlySignedAccounts": 0,
                          "numReadonlyUnsignedAccounts": len(keys) - 1 - (1 if other else 0)},
               "instructions": ixs, "recentBlockhash": synth.key(3, 1),
               "transactionConfig": {"computeUnitLimit": cu_limit, "heapSize": None,
                                     "loadedAccountsDataSizeLimit": LOADED_DATA_LIMIT,
                                     "priorityFee": priority_fee}}
    meta = {"err": None, "fee": chain.LAMPORTS_PER_SIGNATURE + priority_fee, "costUnits": 1484,
            "computeUnitsConsumed": 150, "loadedAddresses": {"writable": [], "readonly": []},
            "preBalances": [10 ** 7] * len(keys), "postBalances": [10 ** 7] * len(keys),
            "innerInstructions": [], "logMessages": [], "rewards": [], "status": {"Ok": None}}
    return {"transaction": {"signatures": [signature], "message": message}, "meta": meta,
            "version": 1}


def foreign_entry(rnd, n):
    """A legacy transaction of somebody else."""
    payer, dest = synth.key(200, n), synth.key(201, n)
    message = {"accountKeys": [payer, dest, chain.SYSTEM_PROGRAM],
               "header": {"numRequiredSignatures": 1, "numReadonlySignedAccounts": 0,
                          "numReadonlyUnsignedAccounts": 1},
               "instructions": [{"programIdIndex": 2, "accounts": [0, 1],
                                 "data": _transfer(rnd.randrange(1, 10 ** 6)), "stackHeight": 1}],
               "recentBlockhash": synth.key(3, 2)}
    meta = {"err": None, "fee": 5000, "costUnits": 1500, "computeUnitsConsumed": 150,
            "loadedAddresses": {"writable": [], "readonly": []},
            "preBalances": [10 ** 9, 0, 1], "postBalances": [10 ** 9, 0, 1],
            "innerInstructions": [], "logMessages": [], "rewards": [], "status": {"Ok": None}}
    return {"transaction": {"signatures": [synth.sig(900000 + n, 0)], "message": message},
            "meta": meta, "version": "legacy"}


def tick_entry(signer, index, timestamp_ns, slot):
    data = bytes([chain.INCREMENT_V1_TAG]) + slot.to_bytes(8, "little") \
        + timestamp_ns.to_bytes(8, "little", signed=True) + (50_000_000).to_bytes(8, "little")
    message = {"accountKeys": [signer, synth.key(210, 1), chain.MARKET_TICK],
               "header": {"numRequiredSignatures": 1, "numReadonlySignedAccounts": 0,
                          "numReadonlyUnsignedAccounts": 1},
               "instructions": [{"programIdIndex": 2, "accounts": [1, 0], "data": b58.encode(data),
                                 "stackHeight": 1}],
               "recentBlockhash": synth.key(3, 3)}
    meta = {"err": None, "fee": 5000, "costUnits": 1400, "computeUnitsConsumed": 100,
            "loadedAddresses": {"writable": [], "readonly": []},
            "preBalances": [1, 1, 1], "postBalances": [1, 1, 1], "innerInstructions": [],
            "logMessages": [], "rewards": [], "status": {"Ok": None}}
    return {"transaction": {"signatures": [synth.sig(800000 + index, slot % 256)], "message": message},
            "meta": meta, "version": "legacy"}


def crank_entry(memo, n):
    keys = [synth.key(220, 1), chain.TIP_PAYMENT, sorted(chain.MEMO_PROGRAMS)[0]]
    message = {"accountKeys": keys,
               "header": {"numRequiredSignatures": 1, "numReadonlySignedAccounts": 0,
                          "numReadonlyUnsignedAccounts": 2},
               "instructions": [{"programIdIndex": 1, "accounts": [0], "data": b58.encode(b"\x01"),
                                 "stackHeight": 1},
                                {"programIdIndex": 2, "accounts": [], "data": b58.encode(memo.encode()),
                                 "stackHeight": 1}],
               "recentBlockhash": synth.key(3, 4)}
    meta = {"err": None, "fee": 5000, "costUnits": 1400, "computeUnitsConsumed": 100,
            "loadedAddresses": {"writable": [], "readonly": []},
            "preBalances": [1, 1, 1], "postBalances": [1, 1, 1], "innerInstructions": [],
            "logMessages": [], "rewards": [], "status": {"Ok": None}}
    return {"transaction": {"signatures": [synth.sig(700000 + n, 1)], "message": message},
            "meta": meta, "version": "legacy"}


def anchor_entry(memo, n):
    """Prereg anchor of section 10: one Memo v2 instruction from the wallet, legacy."""
    message = {"accountKeys": [synth.key(230, 1), "MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr"],
               "header": {"numRequiredSignatures": 1, "numReadonlySignedAccounts": 0,
                          "numReadonlyUnsignedAccounts": 1},
               "instructions": [{"programIdIndex": 1, "accounts": [], "data": b58.encode(memo.encode()),
                                 "stackHeight": 1}],
               "recentBlockhash": synth.key(3, 5)}
    meta = {"err": None, "fee": 5000, "costUnits": 1400, "computeUnitsConsumed": 9000,
            "loadedAddresses": {"writable": [], "readonly": []},
            "preBalances": [1, 1], "postBalances": [1, 1], "innerInstructions": [],
            "logMessages": [], "rewards": [], "status": {"Ok": None}}
    return {"transaction": {"signatures": [synth.sig(800000 + n, 1)], "message": message},
            "meta": meta, "version": "legacy"}


class FakeChain:
    def __init__(self, block_height=440000200):
        self.blocks = {}
        self.where = {}
        self.leaders = {}
        self.block_height = block_height
        self.calls = []
        self.unlisted = set()  # landed in a block the listing has not finalized yet
        self.flaky = {}  # slot: answers getBlock gives first, None or an error code
        self.slept = []

    def sleep(self, seconds):
        self.slept.append(seconds)

    def add_block(self, slot, entries, leader, block_time):
        self.blocks[slot] = {
            "blockTime": block_time, "blockhash": synth.key(4, slot % 256),
            "previousBlockhash": synth.key(4, (slot - 1) % 256), "parentSlot": slot - 1,
            "blockHeight": slot - 22000000,
            "rewards": [{"pubkey": leader, "lamports": 1, "postBalance": 1,
                         "rewardType": "Fee", "commission": None}],
            "transactions": entries}
        self.leaders[slot] = leader
        for i, entry in enumerate(entries):
            self.where[entry["transaction"]["signatures"][0]] = (slot, i)

    @staticmethod
    def _version_ok(options, entries):
        if not any(e.get("version") == 1 for e in entries):
            return True
        v = (options or {}).get("maxSupportedTransactionVersion")
        return type(v) is int and v >= 1

    def _refuse(self, method):
        raise rpc.RpcError(method, {"code": -32015, "message": "Transaction version (1) is not "
                                    "supported by the requesting client"})

    def call(self, method, params):
        self.calls.append((method, json.loads(json.dumps(params))))
        handler = getattr(self, "_" + method, None)
        if handler is None:
            raise rpc.RpcError(method, {"code": -32601, "message": "Method not found"})
        return handler(*params)

    def _getBlock(self, slot, options=None):
        if self.flaky.get(slot):
            code = self.flaky[slot].pop(0)
            if code is None:
                return None
            raise rpc.RpcError("getBlock", {"code": code, "message": "Block not available for slot %d" % slot})
        block = self.blocks.get(slot)
        if block is None:
            raise rpc.RpcError("getBlock", {"code": -32007, "message": "Slot %d was skipped" % slot})
        if not self._version_ok(options, block["transactions"]):
            self._refuse("getBlock")
        return copy.deepcopy(block)

    def _getTransaction(self, signature, options=None):
        if signature not in self.where:
            return None
        slot, i = self.where[signature]
        entry = self.blocks[slot]["transactions"][i]
        if not self._version_ok(options, [entry]):
            self._refuse("getTransaction")
        out = copy.deepcopy(entry)
        out.update({"slot": slot, "blockTime": self.blocks[slot]["blockTime"]})
        return out

    def _getSignatureStatuses(self, signatures, options=None):
        value = []
        for s in signatures:
            if s in self.where:
                value.append({"slot": self.where[s][0], "confirmations": None, "err": None,
                              "confirmationStatus": "finalized", "status": {"Ok": None}})
            else:
                value.append(None)
        return {"context": {"slot": max(self.blocks or [0])}, "value": value}

    def _getSignaturesForAddress(self, address, options=None):
        options = options or {}
        hits = []
        for slot, block in self.blocks.items():
            for i, entry in enumerate(block["transactions"]):
                if address in entry["transaction"]["message"]["accountKeys"] \
                        and entry["transaction"]["signatures"][0] not in self.unlisted:
                    hits.append((slot, i, entry))
        hits.sort(key=lambda h: (h[0], h[1]), reverse=True)
        out = [{"signature": e["transaction"]["signatures"][0], "slot": s, "transactionIndex": i,
                "err": None, "memo": None, "blockTime": self.blocks[s]["blockTime"],
                "confirmationStatus": "finalized"} for s, i, e in hits]
        before = options.get("before")
        if before:
            names = [o["signature"] for o in out]
            out = out[names.index(before) + 1:] if before in names else []
        return out[:options.get("limit", 1000)]

    def _getBlockHeight(self, options=None):
        return self.block_height

    def _getSlotLeaders(self, start, limit):
        return [self.leaders.get(start + k) for k in range(limit)]


def build_world(run_dir, seed="itb-fakechain-v1", tamper_cost=False):
    """A live mainnet run of three bursts written to run_dir/probes.jsonl and the
    chain it landed on. Returns (chain, truth): truth maps signature to the
    expected (status, slot, tx_index, in_target_window, tick_segment)."""
    rnd = random.Random(seed)
    run = synth.run_row("fake-live", stage="test")
    run.update({"mode": "live", "network": "mainnet", "wallet": synth.key(9, 1),
                "rpc_url": "https://api.mainnet-beta.solana.com",
                "ws_url": "wss://api.mainnet-beta.solana.com"})
    payers = run["payers"]
    world = FakeChain()
    rows = [run]
    truth = {}
    target, other_leader = synth.key(5, 1), synth.key(5, 2)
    specs = [("independent", 462000000, None), ("shared", 462000200, None),
             ("denominator", 462000400, None)]
    filler = 0
    for seq, (arm, first_slot, _) in enumerate(specs):
        probes = synth.make_probes(rnd, arm)
        burst_fields = {"arm": arm, "first_slot": first_slot, "leader": target,
                        "selection_class": "Agave", "leader_client_id": "Agave"}
        burst = synth.burst_rows(run, seq, probes, **burst_fields)
        for row in burst:
            if row["kind"] == "probe" and arm == "shared":
                rank = row["send_rank"]
                other = payers[0] if rank != 0 else payers[1]
                row["write_accounts"] = [row["payer"], other]
        rows.extend(burst)
        by_rank = {r["send_rank"]: r for r in burst if r["kind"] == "probe"}
        order = sorted(by_rank)
        rnd.shuffle(order)
        lost, late = order[-1], order[-2]
        landing = {first_slot: [], first_slot + 1: [], first_slot + 4: []}
        for rank in order:
            if rank == lost:
                truth[by_rank[rank]["signature"]] = ("expired",)
                continue
            landing[first_slot + 4 if rank == late else first_slot + (rank % 2)].append(rank)
        for slot, ranks in landing.items():
            entries = []
            if slot == first_slot:
                entries.append(crank_entry("BAL", seq))
            placed = 0
            for rank in ranks:
                for _ in range(rnd.randrange(0, 3)):
                    filler += 1
                    entries.append(foreign_entry(rnd, filler))
                p = by_rank[rank]
                other = None
                if arm == "shared":
                    other = payers[0] if rank != 0 else payers[1]
                extra = b"cost-tamper" if tamper_cost and arm == "denominator" and rank == ranks[0] \
                    else b""
                entries.append(probe_entry(p["payer"], p["signature"], p["transfer_lamports"],
                                           p["priority_fee_lamports"], p["cu_limit"], other, extra))
                placed += 1
                if seq == 0 and slot == first_slot + 1 and placed in (1, 3):
                    entries.append(tick_entry(synth.key(230, 1), placed,
                                              1_793_000_000_000_000_000 + placed * 50_000_000, slot))
            leader = other_leader if slot == first_slot + 4 else target
            world.add_block(slot, entries, leader, 1793044801 + slot - 462000000)
            ticks = [i for i, e in enumerate(entries)
                     if chain.MARKET_TICK in e["transaction"]["message"]["accountKeys"]]
            for i, e in enumerate(entries):
                sig = e["transaction"]["signatures"][0]
                if sig in {by_rank[r]["signature"] for r in ranks}:
                    segment = sum(1 for t in ticks if t < i) if ticks else None
                    truth[sig] = ("included", slot, i, slot < first_slot + 4, segment)
    os.makedirs(run_dir, exist_ok=True)
    with open(os.path.join(run_dir, "probes.jsonl"), "wb") as f:
        f.write("".join(json.dumps(r) + chr(10) for r in rows).encode("utf-8"))
    return world, truth
