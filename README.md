# Inside the Block

A measurement kit for one question about Solana mainnet: by what rule each leader orders transactions inside its block, and how strictly that rule holds. "No rule" is one of the possible answers and has a test of its own. The kit sends small bursts of its own probe transactions into chosen leader windows, reads the blocks back and tests the order against rules fixed before any live data.

Status: the campaign measured 16 leaders in 8 client classes over epochs 1071 to 1074, from 2026-10-29 to 2026-11-02, after a pilot on 2026-10-27. [REPORT.md](REPORT.md) gives the answer and [DETAILS.md](DETAILS.md) every table behind it.

## Result

Before the leader's window, the fee per requested cost sets the order in 7 of 8 classes. With conflicting probes, 6 of 8 classes keep that order without a single broken pair. At the start of slot 2 arrival order shows, and with equal fees the earlier-sent probe goes first in 6 of 8 classes. Firedancer orders strictly by fee and breaks ties in reverse arrival. FireBAM keeps Firedancer's fee order, while its order of equal fees stays undetermined; HarmonicFiredancer changes the fee order. No cell reaches "no rule visible": 18 of 64 cells stay undetermined, since an equivalence verdict needs 28 to 177 bursts per cell and the campaign had 8. Through public RPC the same bursts land in the target window less often and keep the fee order less ([REPORT.md, section 4.4](REPORT.md#44-control-path)).

## Two hypotheses from the code

For equal fees, code gives two hypotheses before any data. Firedancer should order ties in reverse arrival (H3). Agave's scheduler queue keys on priority and a `Slab` key that reuses the last freed key first, so on fresh keys a later probe goes first and on recycled keys arrival does not count (H4). The campaign finds H3 holding and leaves H4 undecided ([REPORT.md, section 4.1](REPORT.md#41-hypotheses-h3-and-h4)).

## How it works

A burst is 12 probe transactions from 12 payers, sent over one QUIC connection straight to the leader's `tpuQuic`. Four arms vary one property each: own accounts only, one shared account, one fee for all, and two compute-unit limits at one fee. Each burst aims 300 ms before the window or at the start of its second slot. The analysis plan and the seeded tables went on chain as manifest hashes before the first live probe of each stage ([prereg/](prereg/)).

## How the design handles each consideration

- **Leader schedule and leader types.** Windows come from the leader schedule, and the class is the leader's gossip `clientId` at each burst, with validators.app as a second label. Builder classes leave a tick transaction in their slots, which sets each builder against its base client ([DESIGN.md](DESIGN.md#leader-schedule-and-leader-types)).
- **The path from the sender to the executing node.** No RPC node stands in between, and one connection carries the send order up to the leader's QUIC server. A public RPC control path measures the common route beside it ([DESIGN.md](DESIGN.md#the-path-from-the-sender-to-the-executing-node)).
- **Interaction of the probes with each other.** Each probe has its own payer, so the shared arm is the only conflict in a burst, and windows of one round stand 160 slots apart ([DESIGN.md](DESIGN.md#interaction-of-the-probes-with-each-other)).
- **Competition inside the block.** Every block with a probe is stored whole, and DETAILS.md ranks each probe among all its transactions by load quartile; no verdict depends on load ([DESIGN.md](DESIGN.md#competition-inside-the-block)).
- **Send order.** Send order is random and independent of the fee. Tau cross over pairs with different fees tells an arrival rule from a fee rule ([DESIGN.md](DESIGN.md#send-order)).
- **Noise versus rule.** Exact null distributions and Holm families decide each cell, "no rule visible" needs its own equivalence test, and a cell short of bursts reads undetermined ([DESIGN.md](DESIGN.md#noise-versus-rule)).

## What it does NOT separate

From outside the leader the kit cannot see shred propagation to the RPC node, the leg from a builder's receiver to the leader, the way from the QUIC server to the scheduler queue, or a Jito relayer on a port other than the default. Inside the clients, the spread over execution threads and eviction from a full buffer stay out of reach. [DESIGN.md](DESIGN.md#what-it-does-not-separate) lists each item, and [DETAILS.md, section 8](DETAILS.md#8-noise-and-what-the-kit-does-not-separate) names the tables it touches.

## Who can use the data

Raw rows in `data/runs/<run>/` give each probe's signature and slot, and `tx_index` in `collect.jsonl` its index among the block's signatures, which one call shows; full transaction details need `maxSupportedTransactionVersion` 1:

```bash
curl -s https://api.mainnet-beta.solana.com -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"getBlock","params":[462895568,{"encoding":"json","transactionDetails":"signatures","rewards":false,"commitment":"finalized","maxSupportedTransactionVersion":1}]}'
```

- Senders of urgent transactions see where in a window a higher fee buys an earlier position ([REPORT.md, section 1](REPORT.md#1-the-answer)).
- Wallets and RPC providers see what the public route does to inclusion and order ([section 4.4](REPORT.md#44-control-path)).
- Client and builder teams get their rule measured from outside against the base client ([sections 4.1 and 4.2](REPORT.md#41-hypotheses-h3-and-h4)).
- Researchers can rerun the kit on later epochs, and the measurement plan names what each larger measurement settles ([section 8](REPORT.md#8-measurement-plan)).

The data can carry further tools. A fee estimate can weigh the leader's class and the moment of arrival, and a monitor can rerun the panel each epoch and flag a changed rule. A client release can be checked against the rule its code states, and a route against the direct path.

## Reproduce every number with one command

```bash
docker compose run --rm reproduce
```

Without a key or a Rust build it runs the known-answer selftest, re-reads each recorded signature from the chain and compares every generated table of REPORT.md and DETAILS.md with the verdicts recomputed from the raw data. On 2026-11-02 it ran 1 h 35 min against the public node, peak memory 425 MiB. `docker compose run --rm reproduce selftest` and `docker compose run --rm reproduce report --check` recompute the tables from the raw data in minutes without the chain.

The run checks the published `data/`, so a new run in the same folder fails `report --check`, which names it; measure in a separate clone. A new measurement follows [RUNNING.md](RUNNING.md#measuring): with a funded key file, `probe run --live --max-spend-lamports N` sends a drawn plan, and `scripts/campaign.sh` runs a campaign.

## License

MIT
