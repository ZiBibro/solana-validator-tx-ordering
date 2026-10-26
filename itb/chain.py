"""Reading blocks and transactions as getBlock and getTransaction return them
with encoding json: positions, fees, limits, write sets, the builder's tick
label and what a probe itself carries on chain (plan sections 4, 5.3 and 9)."""

import math

from . import b58

SYSTEM_PROGRAM = "11111111111111111111111111111111"
COMPUTE_BUDGET = "ComputeBudget111111111111111111111111111111"
MEMO_PROGRAMS = frozenset(["MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr",
                           "Memo1UhkJRfHyvLMcVucJwxXeuD728EqVDDwQDxFMNo"])
MARKET_TICK = "tickUcsEQegChaAuo9VYQQztB4ZGApY6ZT4FkULWY6N"
TIP_PAYMENT = "T1pyyaTNZsKv2WcRAB8oVnk93mLJw2XzjtVYqCsaHqt"
JITO_TIP_ACCOUNTS = frozenset([
    "96gYZGLnJYVFmbjzopPSU6QiEV5fGqZNyN9nmNhvrZU5", "HFqU5x63VTqvQss8hp11i4wVV8bD44PvwucfZ2bU7gRe",
    "Cw8CFyM9FkoMi7K7Crf6HNQqf4uEMzpKw6QNghXLvLkY", "ADaUMid9yfUytqMBgopwjb2DTLSokTSzL1zt6iGPaS49",
    "DfXygSm4jCyNCybVYYK6DwvWqjKee8pbDmJGcLWNDXjh", "ADuUkR4vqLUMWXxW9gh6D6L8pMSawimctcNZ5pGwDcEt",
    "DttWaMuVvTiduZRnguLF7jNxTgiMBZ1hyAumKUiL2KRL", "3AVi9Tg9Uo68tJfuvoKvqKNWKkC5wPdSSdeBnizKZ6jT",
])
LAMPORTS_PER_SIGNATURE = 5000

# Agave v4.3.2 cost model: the parts add up to the 2334 units of a two-write
# probe and the 21 032 / 2032 ratio of the denominator arm (plan section 6).
SIGNATURE_COST = 720
WRITE_LOCK_COST = 300
INSTRUCTION_DATA_BYTES_PER_UNIT = 4
LOADED_DATA_PAGE_BYTES = 32 * 1024
LOADED_DATA_PAGE_COST = 8

TRANSFER_TAG = 2  # SystemInstruction::Transfer
INCREMENT_V1_TAG = 1  # market-tick Increment V1: tag, slot, timestamp_ns, target interval ns


def agave_cost(signatures, write_locks, ix_data_bytes, cu_limit, loaded_data_limit):
    """Cost of a transaction before execution under the Agave v4.3.2 model."""
    pages = math.ceil(loaded_data_limit / LOADED_DATA_PAGE_BYTES)
    return (signatures * SIGNATURE_COST + write_locks * WRITE_LOCK_COST
            + ix_data_bytes // INSTRUCTION_DATA_BYTES_PER_UNIT + cu_limit
            + pages * LOADED_DATA_PAGE_COST)


def _u(data, offset, size):
    return int.from_bytes(data[offset:offset + size], "little")


class Tx:
    """One transaction of a block (or of getTransaction) at position index."""

    def __init__(self, entry, index=None):
        self.index = index
        version = entry.get("version")
        self.version = "legacy" if version in (None, "legacy") else "v%d" % version
        tx = entry["transaction"]
        message = tx["message"]
        meta = entry.get("meta") or {}
        self.meta = meta
        self.signatures = list(tx["signatures"])
        static = [k if isinstance(k, str) else k["pubkey"] for k in message["accountKeys"]]
        loaded = meta.get("loadedAddresses") or {}
        self.keys = static + list(loaded.get("writable") or []) + list(loaded.get("readonly") or [])
        header = message["header"]
        signed = header["numRequiredSignatures"]
        writable = []
        for i, k in enumerate(static):
            if i < signed:
                is_writable = i < signed - header["numReadonlySignedAccounts"]
            else:
                is_writable = i < len(static) - header["numReadonlyUnsignedAccounts"]
            if is_writable:
                writable.append(k)
        self.write_accounts = writable + list(loaded.get("writable") or [])
        self.fee_payer = static[0]
        self.instructions = [(self.keys[ix["programIdIndex"]],
                              [self.keys[a] for a in ix["accounts"]],
                              b58.decode(ix["data"]))
                             for ix in message["instructions"]]
        self.ix_data_bytes = sum(len(d) for _, _, d in self.instructions)
        self.fee = meta.get("fee")
        self.err = meta.get("err")
        self.cost_units = meta.get("costUnits")
        config = message.get("transactionConfig")
        if config is not None:
            self.cu_limit = config.get("computeUnitLimit")
            self.loaded_data_limit = config.get("loadedAccountsDataSizeLimit")
            self.priority_fee = config.get("priorityFee")
        else:
            self._compute_budget()

    def _compute_budget(self):
        limit = price = loaded = None
        for program, _, data in self.instructions:
            if program != COMPUTE_BUDGET or not data:
                continue
            if data[0] == 2 and len(data) >= 5:
                limit = _u(data, 1, 4)
            elif data[0] == 3 and len(data) >= 9:
                price = _u(data, 1, 8)
            elif data[0] == 4 and len(data) >= 5:
                loaded = _u(data, 1, 4)
        self.cu_limit = limit
        self.loaded_data_limit = loaded
        if not price:
            self.priority_fee = 0
        elif limit is None:
            self.priority_fee = None  # the default limit depends on the programs called
        else:
            self.priority_fee = -(-price * limit // 1_000_000)

    @property
    def fee_minus_signatures(self):
        """Second source of the priority fee: meta.fee minus 5000 per signature."""
        if self.fee is None:
            return None
        return self.fee - LAMPORTS_PER_SIGNATURE * len(self.signatures)

    def jito_tip(self):
        pre, post = self.meta.get("preBalances") or [], self.meta.get("postBalances") or []
        for i, k in enumerate(self.keys):
            if k in JITO_TIP_ACCOUNTS and i < len(pre) and i < len(post) and post[i] > pre[i]:
                return True
        return False

    def tick(self):
        """market-tick Increment V1 carried by this transaction, or None."""
        for program, accounts, data in self.instructions:
            if program == MARKET_TICK and len(data) >= 25 and data[0] == INCREMENT_V1_TAG:
                return {"index": self.index,
                        "signer": accounts[1] if len(accounts) > 1 else None,
                        "timestamp_ns": int.from_bytes(data[9:17], "little", signed=True),
                        "interval_ns": _u(data, 17, 8)}
        return None

    def crank_memo(self):
        """Memo of a tip-payment crank transaction, or None."""
        programs = [p for p, _, _ in self.instructions]
        if TIP_PAYMENT not in programs:
            return None
        for program, _, data in self.instructions:
            if program in MEMO_PROGRAMS:
                return data.decode("utf-8", "replace")
        return None

    def transfers(self):
        out = []
        for program, accounts, data in self.instructions:
            if program == SYSTEM_PROGRAM and len(data) >= 12 and _u(data, 0, 4) == TRANSFER_TAG \
                    and len(accounts) >= 2:
                out.append((accounts[0], accounts[1], _u(data, 4, 8)))
        return out

    def probe_view(self):
        """What a probe carries on chain, or None when this is not a probe: the
        self-transfer amount encodes burst_seq*16 + send_rank + 1 (section 4)."""
        own = [t for t in self.transfers() if t[0] == t[1] == self.fee_payer]
        if len(own) != 1 or own[0][2] < 1:
            return None
        burst_seq, send_rank = divmod(own[0][2] - 1, 16)
        if send_rank > 11:
            return None
        cost = None
        if self.cu_limit is not None and self.loaded_data_limit is not None:
            cost = agave_cost(len(self.signatures), len(set(self.write_accounts)),
                              self.ix_data_bytes, self.cu_limit, self.loaded_data_limit)
        return {"payer": self.fee_payer, "burst_seq": burst_seq, "send_rank": send_rank,
                "transfer_lamports": own[0][2], "priority_fee": self.priority_fee,
                "fee_minus_signatures": self.fee_minus_signatures, "cu_limit": self.cu_limit,
                "loaded_data_limit": self.loaded_data_limit,
                "write_accounts": sorted(set(self.write_accounts)), "cost": cost,
                "version": self.version}

    def block_tx_row(self, slot):
        """Raw block_tx row: inputs of the competition measure of section 10."""
        return {"v": 1, "kind": "block_tx", "slot": slot, "tx_index": self.index,
                "signatures": self.signatures, "write_accounts": self.write_accounts,
                "ix_data_bytes": self.ix_data_bytes, "cu_limit": self.cu_limit,
                "loaded_data_limit": self.loaded_data_limit,
                "priority_fee_lamports": self.priority_fee, "fee": self.fee,
                "cost_units": self.cost_units, "jito_tip": self.jito_tip(),
                "tx_version": self.version}


class Block:
    def __init__(self, slot, block):
        self.slot = slot
        self.raw = block
        self.txs = [Tx(entry, i) for i, entry in enumerate(block.get("transactions") or [])]
        self.by_signature = {tx.signatures[0]: tx for tx in self.txs if tx.signatures}
        self.block_time = block.get("blockTime")
        self.parent_slot = block.get("parentSlot")
        self.blockhash = block.get("blockhash")

    def fee_recipient(self):
        """Address of the Fee reward record: the leader's fee collector, which is
        its identity unless the operator set another (SIMD-0232, section 9)."""
        for reward in self.raw.get("rewards") or []:
            if reward.get("rewardType") == "Fee":
                return reward.get("pubkey")
        return None

    def cost_units(self):
        values = [tx.cost_units for tx in self.txs]
        return None if any(v is None for v in values) else sum(values)

    def ticks(self):
        return [t for t in (tx.tick() for tx in self.txs) if t is not None]

    def crank_memo(self):
        for tx in self.txs:
            memo = tx.crank_memo()
            if memo is not None:
                return memo
        return None


def tick_segment(ticks, tx_index):
    """Index of the inter-tick segment a position falls into, None without ticks."""
    if not ticks:
        return None
    return sum(1 for t in ticks if t["index"] < tx_index)
