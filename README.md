# Inside the Block

A measurement kit for one question about Solana mainnet: by what rule each leader orders transactions inside its block, and how strictly that rule holds. "No rule" is one of the possible answers and has a test of its own. The kit sends small bursts of its own probe transactions into chosen leader windows and reads the blocks back. The ordering is then tested against rules fixed before any live data.

Status: the tool and the analysis plan are finished and have passed dry-runs on mainnet. The live measurement and its REPORT come next.

## Why this design

Most stake on mainnet no longer hands its block to a plain validator scheduler. Gossip labels each node with a `clientId`, and on 2026-10-25 the stake split over eight classes like this:

| Class | Stake | Builder in the path | Measured against |
|---|---|---|---|
| AgaveBam | 35.50% | BAM node | JitoLabs |
| JitoLabs | 23.06% | none | |
| HarmonicAgave | 21.66% | Harmonic builder | Agave |
| HarmonicFiredancer | 8.68% | Harmonic builder | Firedancer |
| Firedancer | 7.01% | none | |
| FireBAM | 1.62% | BAM node | Firedancer |
| Rakurai | 1.17% | none | |
| Agave | 1.08% | none | |

The builder classes leave a mark in the block itself. The market-tick program `tickUcsEQegChaAuo9VYQQztB4ZGApY6ZT4FkULWY6N` receives tick transactions from the signer `BAMgx3XP…` with a 20 ms target interval in slots of AgaveBam and FireBAM leaders, and from `Harmonic8So…` with a 50 ms interval in slots of Harmonic leaders. In five samples on 2026-10-26 between 02:01 and 04:08 UTC every Harmonic slot carried a tick, and no slot of a JitoLabs, Agave, Firedancer or Rakurai leader did.

So a probe in a slot with a tick measures the builder's rule, and a probe in a slot of the same code base without a builder measures the validator's scheduler. The table pairs each builder class with its base. The builder's contribution is the difference in tau between the two classes of a pair, with a jackknife interval over the bursts of both. Two verdicts read one by one cannot show that difference, because the difference between a significant and a non-significant result is not itself significant (Gelman and Stern, The American Statistician 60(4), 2006).

The mark works one way. A tick from a known signer marks a builder slot, while a slot without a tick proves nothing: one BAM node (tpuQuic 88.216.192.50) posts no ticks, and its leaders stay out of the panel. Every BAM node shares one tick signer and every Harmonic builder shares another, so the mark names the kind of builder; which particular node built the slot stays unknown.

Open source code gives the base rules every verdict is read against. Agave v4.3.2 ranks transactions by `reward * 1 000 000 / (cost + 1)`, where cost is the full cost of the transaction including the requested compute-unit limit. Firedancer v26.10.4 ranks by `rewards / compute_est` and writes into the block exactly the order its pack tile picks, one transaction per microblock. A fork is measured with the same arms as everyone else and read against the client it is built on.

## How a measurement works

A burst is 12 probe transactions from 12 different payers, sent into one window of one leader over one QUIC connection. Inside a burst the priority fee and the send order are random and independent of each other, so the position in the block shows the effect of the fee apart from the effect of arrival order.

A probe is a v1 transaction with a transfer to the payer itself. The amount encodes the burst and the send rank, `burst_seq * 16 + send_rank + 1`, so every message is unique at no extra compute cost and the send rank is fixed by the signature before sending. Simulation prices a probe at the 5000-lamport base fee and 150 CU. The compute-unit limit (1000) and the loaded-data limit (32768 bytes) are set explicitly, because an unset field in a v1 message equals zero and fails the transaction. The fee is read back from `meta.fee` after inclusion.

Arms differ in exactly one property each:

| Arm | Write accounts | What varies | What it tests |
|---|---|---|---|
| independent | the payer's own | fee drawn from 0, 10, 100 and 1000 lamports; random send order | fee and arrival order for transactions a leader can run in parallel |
| shared | the payer's own plus payer 1, to whom every probe sends 0 lamports | as in the independent arm | the rule for conflicting transactions |
| equal fee | the payer's own | one fee for all 12, sent 5 ms apart | how ties between equal fees break |
| denominator | the payer's own | one fee for all 12, half with a 1000 CU limit and half with 20 000 | whether the leader divides the fee by the requested limit |

Each burst also draws one of two moment conditions, defined by the target arrival at the leader's tpuQuic. One target is 300 ms before the first slot of the window, when every probe waits in the queue for the first scheduling pass. The other is the start of the second slot, when the scheduler takes transactions as they arrive. The sender fires the first probe at the target minus half the round-trip time of the same connection, measured just before the burst. Without that correction the condition would mix with distance, since the average RTT from the measuring machine ran from 29 ms to a BAM node in Frankfurt up to 244 ms to one in Tokyo on 2026-10-26. A burst counts for its condition when its estimated arrival lies in a band fixed before live data: 500 to 200 ms before the first slot for the pre-window condition, and 100 ms either side of the start of slot 2 for the other ([prereg/ANALYSIS-PLAN.md](prereg/ANALYSIS-PLAN.md), section 6).

The panel holds two leaders from each class, 16 validators in all, picked by a rule fixed before live data. A candidate is not delinquent, runs the most common version of its class, holds at least 16 leader windows per epoch, and has a window that passes the filters in every eighth of the epoch. Among candidates the largest stake wins, and the two leaders of a class belong to different operators by validator-info name whenever the name is set, so a difference inside a class can come from the client's rule apart from one operator's setup. The campaign measures the same panel over four epochs in rounds spread through each epoch. A pilot of 68 bursts runs first to measure inclusion and the spread of tau between bursts. It also tests whether the segments between ticks are rounds in time: in the equal-fee bursts sent at the start of slot 2, a later-sent probe should not stand in an earlier segment (analysis plan, section 10). The budget fixes the campaign at 8 bursts per class and cell; the spread from the pilot gives the minimum number of bursts an equivalence verdict needs, and that number goes on chain before the campaign, so REPORT shows in advance which cells can reach such a verdict.

Before any live probe, every file that fixes the analysis, the seeded pilot table included, is hashed into a manifest ([prereg/manifest-pilot.json](prereg/manifest-pilot.json)). A memo transaction puts `itb-prereg <sha256>` of that manifest on chain, and the sender refuses a live run of a stage until the anchor for the same manifest exists. The campaign gets a second manifest of the same kind ([prereg/manifest-campaign.json](prereg/manifest-campaign.json)). It adds the seeded campaign table, whose seed is `campaign:` plus the signature of the pilot anchor and so was fixed before any pilot data existed, and the minimum computed from the pilot.

## Design considerations

### Leader schedule and leader types

The class comes from `clientId` in `getClusterNodes` at the moment of each burst, together with the version, and both go into the raw row. A second label comes from validators.app (`software_client`), taken once per round with the snapshot time as its date; on 2026-10-26 the stake shares by both labels agreed within 0.07 percentage points for all eight classes. REPORT prints both labels of every panel leader side by side.

Jito-Solana switches its `clientId` between JitoLabs and AgaveBam with the state of its BAM connection. A verdict therefore uses only bursts whose leader showed the selection class at the moment of the burst; the rest form a separate group, and REPORT gives its share per class.

Windows come from the leader schedule in rounds. Each round fixes a random reference time. Leaders then take windows in random order, each getting the window nearest to that time that passes the filters and lies at least 160 slots from the windows already taken. Many validators share one builder address (198.13.141.173:5010 serves 100 staked nodes), and BAM documentation does not say what its receiver does with a transaction that arrives during the window of another validator behind the same address. Windows right after such a window are skipped.

Raiku (0.08% of stake) and Frankendancer (no voting nodes) are not in the panel. The collector still labels them, together with any `Unknown(n)` value, so no leader of an observed slot stays unlabelled.

### The path from the sender to the executing node

The sender opens one QUIC connection to the leader's tpuQuic from gossip a few slots before the window and sends each probe on its own unidirectional stream, in the assigned order. No RPC node stands in between. The connection setup copies Agave's own client: a client certificate from `solana-tls-utils` (built with the `agave-unstable-api` feature), ALPN `solana-tpu`, `send_fairness(false)` so that the streams of one connection go out in the order they were opened, and the transport `anza-quinn 0.11.11-rustsec20260339`, the exact version Agave v4.3.2 pins. The ready-made `solana-tpu-client-next` crate is not used. Its `send_transaction` only puts the transaction into a channel, and stream errors end up in aggregate counters. After an error its worker sleeps 1600 ms, longer than a leader window.

The send timestamp is the end of `write_all`, a lower bound for the probe leaving the machine; the completion of `stopped()` is recorded as the upper bound together with the stream's result. The Agave v4.3.2 QUIC server reads the streams of one connection one at a time, in the order it accepted them (`streamer/src/nonblocking/quic.rs`), so one connection per leader carries the send order up to the exit of the server.

For the builder classes the tpuQuic address in gossip already leads into the builder's receiver. Nodes that accept transactions on an IP other than their gossip IP held 100.0% of the stake of the four builder classes on 2026-10-26, against 6.4% in JitoLabs and 1.6% in Firedancer; Agave and Rakurai had none. The kit uses no Block Engine API and builds no bundles. The base classes must accept on their gossip IP, and JitoLabs and Rakurai leaders must not announce port 11228, the default QUIC port of the Jito relayer, which holds every transaction 50 ms before forwarding it.

The slot clock runs on `slotsUpdatesSubscribe` events `firstShredReceived`, with `slotSubscribe` as a fallback. The public node delivers these events through a queue (on 2026-10-26 at 23:43 UTC each of four connections lagged `getSlot` at processed commitment by 12 to 14 slots at the median), so an event is placed on the local clock at the node's own timestamp plus the smallest receipt offset over the last 1500 slots. Slot steps are uneven, since the slots of one leader follow each other faster than the hand-over to the next leader, so the forecast adds median steps by position in the window and re-aims every 5 ms until 2 ms before the send. Before writing a burst the sender asks `getSlot` at processed commitment and skips the burst when that slot runs 2 or more ahead of the clock.

Before any run the sender checks who issued the TLS certificates of the RPC and WebSocket endpoints and stops when the chain does not verify against public roots, so it never measures through an intercepting proxy.

A control path sends the same kind of burst through `sendTransaction` on the public RPC endpoint with `maxRetries` 0: one burst per leader per epoch, 64 bursts in the campaign. It is compared with the direct path only within the same leader and epoch, and no class verdict uses it.

### Interaction of the probes with each other

Every probe of a burst has its own payer, so the only conflict inside a burst is the one the shared arm builds on purpose. In that arm payer 1 sends its 0 lamports on to payer 2, so all 12 probes write two accounts and cost the same 2334 units under the Agave v4.3.2 cost model. Had payer 1 sent only to itself, its probe would cost 2034 units and carry a 14.7% higher priority at the same fee.

Windows of one round lie at least 160 slots apart. The gap covers the 150-block lifetime of a blockhash and the 151-slot transaction expiry in the Firedancer pack tile, so a probe that misses its window cannot land in the block of a neighbouring burst signed by the same payers. Without the gap, the nearest-window rule produced directly adjacent windows in 70.5% of rounds.

Positions count only among probes of the same burst that landed in the same block of the target window. A burst with fewer than two probes in such a block feeds the inclusion share alone. Probes that landed in another leader's block leave the order tests, and REPORT gives their share per path and condition together with the class of the leader that took them. A burst whose block received a probe of another burst leaves the order tests too, with the reason recorded.

### Competition inside the block

For every slot that includes a probe the collector stores the whole block as compressed JSON Lines: transaction index, signatures, write accounts, instruction data size, requested limits, priority fee and `meta.costUnits`. REPORT ranks each probe among all transactions of its block by client priority computed from requested limits, with the rank by `meta.costUnits` as a second column; transactions that tip a Jito tip account are flagged and left out of the rank.

No verdict depends on load; REPORT describes it. The sum of `costUnits` and the transaction count of a block give load quartiles, and tau fee and tau send are shown by quartile. Inclusion share by fee level stands next to tau fee, because Agave drops transactions at the priority edge when its buffer is full and Firedancer evicts the worst one from a full pool, so a position is always conditional on getting in. The rounds spread the bursts of different classes over the same hours: over 7.1 hours on 2026-10-26 the network carried between 210.8 and 570.6 non-vote transactions per slot, with a median of 301.4.

### Send order

Send order is randomised independently of the fee, which gives tau send. Over the pairs with different fee (54 in a full burst) it becomes tau cross, the measure that tells an arrival rule from a fee rule. Without that split an exact fee rule could read as mixed: if it breaks ties in reverse arrival order, it gives a tau send of -0.182 over all 66 pairs, which passes the first Holm threshold from 18 bursts of a cell.

The equal-fee arm isolates tie-breaking. Code gives two hypotheses before any data. For Firedancer it predicts reverse arrival order (H3). For Agave the scheduler queue is a `BTreeSet` of priority and a `Slab` key, and `Slab` reuses the last freed key first, so on fresh keys a later probe with the same fee goes first and on recycled keys order does not depend on arrival (H4); REPORT shows that arm by load quartile for Agave. The conclusion on tie-breaking comes only from the pre-window condition, where all probes reach the same scheduling call.

### Noise versus rule

Each measure is a Kendall tau-b against block position. Every within-burst test uses an exact null distribution: Mahonian numbers and their q-multinomial form for tied fee levels, and for tau cross a dynamic program over subsets of the 12 probes. Every p is therefore an exact fraction that comes out the same on any Python version. Verdicts run through Holm families at alpha 0.05, 96 tests in the verdict family, and every class and condition gets one of six forms: inverted fee sign, mixed rule, fee rule, arrival rule, no rule visible, or undetermined. "No rule visible" is a claim with its own test: both tau fee and tau cross must pass a TOST that bounds them within 0.2 of zero, in a 96-test equivalence family. A cell without enough power reads undetermined.

Strictness is the share of violated pairs among probe pairs with a different predicted position, with a jackknife interval over bursts and the share of bursts without a single violation beside it. Two leaders per class show whether a rule belongs to the client or to one operator, and four epochs show whether it holds over time. The whole plan sits in [prereg/ANALYSIS-PLAN.md](prereg/ANALYSIS-PLAN.md) and is anchored on chain before the first live probe.

## What it does NOT separate

These stay out of reach from outside the leader, and REPORT names them next to the results they touch.

- Shred propagation from the leader to the RPC node. The `firstShredReceived` event arrives later than the leader's own slot start, and the delay changes from window to window with the leader of the anchor slot. Every burst records the forecast residual, so its size is visible, while its source is not.
- The leg from a BAM node or a Harmonic region to the leader itself. RTT from the measuring machine ends at the builder's receiver.
- The way from the exit of the leader's QUIC server to the scheduler queue, through packet batching and signature verification. The send timestamp lies before both.
- A Jito relayer on a port other than 11228. Panel selection avoids the default port, and a relayer on any other port cannot be seen from outside.
- Buffering before the window in clients other than Agave. Agave v4.3.2 holds every transaction that arrives less than 20 slots before its window (`core/src/banking_stage/decision_maker.rs`); the same was not verified in the code of JitoLabs, FireBAM, AgaveBam, Rakurai or Firedancer, and that limit applies to the 300 ms target itself.
- Inside Agave: the boundaries of entries and the spread over execution threads, the pacing state, drops at the priority edge when the buffer is saturated, and the first slot after a restart, which needs about 350 ms to fill.
- Inside Firedancer: the choice of execution tile, penalty treaps, probabilistic eviction from a full pool, and the pack strategy, which an operator may change between windows and which shows only in the memo of a crank transaction when the window has one.
- Inside builders: the particular BAM node or Harmonic builder, because the tick signer is shared, and the BAM priority score, which is closed together with the node's code.
- Strategy against operator in HarmonicAgave. The panel takes one leader with the FBA strategy and one with MRV, so the comparison of strategies in that class is descriptive.

## Reproduce every number with one command

```bash
docker compose run --rm reproduce
```

It needs no key and no Rust build. Before touching any data it runs the known-answer selftest. Then verify re-reads every recorded signature from the chain. Last, analyze recomputes every REPORT number from the raw data, and the first mismatch fails the run. A single step runs alone with `docker compose run --rm reproduce verify` or `analyze`.

## Measuring

The sender is dry-run by default: it opens the connections, simulates every probe and sends nothing. A live run needs both `--live` and `--max-spend-lamports N`, and a compiled cap of 0.05 SOL (50 000 000 lamports) stands above any limit given on the command line. Before the first send the sender prices the whole plan at its worst-case fee and refuses when the limit does not cover it.

```bash
docker compose --profile measure run --rm plan panel
docker compose --profile measure run --rm plan pilot --panel data/panels/<id>/panel.json
docker compose --profile measure run --rm probe anchor --stage pilot
docker compose --profile measure run --rm probe run --plan /data/plans/<id>/plan.json
```

The commands draw the panel, place the seeded pilot table into its windows, simulate the anchor memo, and dry-run the plan. The live form of the last two adds `--live --max-spend-lamports N`.

The campaign follows the same steps. On the host, `python -m itb minimum` reads the collected pilot runs and `python -m itb manifest --stage campaign` hashes the campaign files; containers mount `prereg/` read-only. Each epoch gets its own plan, drawn once the leader schedule of that epoch is known:

```bash
docker compose --profile measure run --rm plan campaign --panel data/panels/<id>/panel.json --epoch-index 0 --epoch <epoch>
```

A round whose first window has already passed when the plan is drawn is left out and noted in `draw-notes.json` beside the plan; its cells are not moved to another hour, because that would break the blocking by round. Placement depends on the seed and the leader schedule only, so a plan drawn again after a stopped run keeps the windows of the rounds still ahead.

[scripts/campaign.sh](scripts/campaign.sh) runs the four epochs live one after another, since they share the payers and the spend journal. For each epoch it draws the plan, sets the limit to the committed lamports plus the plan's worst-case fees plus the funding and closing overhead, closes the payers at the end and collects the run. A failed run is collected and its epoch drawn again after ten minutes, up to three attempts:

```bash
scripts/campaign.sh data/panels/<id>/panel.json <first epoch>
```

The comments at the top of [compose.yaml](compose.yaml) list every command.

Keys are never part of the repository. The sender reads the wallet key from a Compose secret whose file is given by `ITB_WALLET_KEY_FILE` (by default the git-ignored `secrets/wallet-key.json`), or from an environment variable through `compose.key-from-env.yaml`. Logs and raw rows never carry key bytes, and `tests/keyscan.py` searches everything a run wrote for them in every encoding.

## Development without spending

A local test validator is not part of the kit. The Linux release of `solana-test-validator` 4.3.2 needs `io_uring`, which Docker's default seccomp profile blocks, and the kit does not loosen that profile. The kit tests itself in two other ways. The selftest runs collect, verify and analyze over a fake chain with a known answer, including the exact zero of tau cross. The pipeline test [tests/devnet.sh](tests/devnet.sh) runs on devnet: it draws a plan from the devnet leader schedule, starts a live run under a limit below the plan's cost and expects a refusal before the first send, dry-runs the same plan, and with test SOL on a throwaway key runs a second plan live with collect and verify, then scans everything for key bytes. The refusal is on record in [logs/devnet-devnet-20261026T231740Z.jsonl](logs/devnet-devnet-20261026T231740Z.jsonl).

The probe image runs `cargo test` while it builds, and a failing test fails the build.

## Building the probe behind a TLS-inspecting proxy

The probe image fetches crates from crates.io while it builds. An antivirus web shield or a corporate proxy that re-signs HTTPS makes that fetch fail with a certificate error. Export the proxy's root certificate as PEM and pass it as a build secret. Only the dependency fetch sees it, through the system roots of the build stage, and the built image does not contain it:

```bash
docker build --secret id=extra_ca,src=proxy-root.pem -f probe/Dockerfile -t inside-the-block-probe:local .
```

The probe itself refuses to measure through such a proxy, as described above.

The plan step reads the second client label from validators.app, and a web shield may re-sign that host too. `ITB_EXTRA_CA_PEM`, set to the PEM text of the same root, adds it next to the system roots for that one request; RPC calls never use it, and the snapshot records the root's SHA-256. Without it the plan still draws and notes that its bursts carry no second label.

## Layout

| Path | What it holds |
|---|---|
| `compose.yaml` | four services: `reproduce`, `plan`, `collect`, `probe`; all but the first need the profile `measure` |
| `probe/` | the sender, Rust on Agave's QUIC stack; dry-run by default, live sending only with `--live --max-spend-lamports N` under a compiled 0.05 SOL cap |
| `itb/` | panel, plan, collect, verify, analyze and selftest, Python standard library only |
| `prereg/` | everything fixed before live data: the analysis plan, the seeded pilot and campaign tables, the minimum from the pilot, and the manifests whose hashes go on chain |
| `schema/raw-format.json` | the format of every raw row, shared by both languages |
| `data/` | inputs and raw data of every run, failed ones included |
| `logs/` | operational logs, kept apart from raw data |
| `scripts/` | the live campaign runner, one epoch after another |
| `tests/` | the devnet pipeline test, the mainnet dry-run, the key scanner, and unit tests for the scanner and the raw format |

## License

MIT
