# Inside the Block

A measurement kit for one question about Solana mainnet: by what rule each leader orders transactions inside its block, and how strictly that rule holds. "No rule" is one of the possible answers and has a test of its own. The kit sends small bursts of its own probe transactions into chosen leader windows and reads the blocks back. The ordering is then tested against rules fixed before any live data.

Status: the campaign measured 16 leaders in 8 client classes over epochs 1071 to 1074, from 2026-10-29 to 2026-11-02, after a pilot on 2026-10-27. [REPORT.md](REPORT.md) gives the answer and [DETAILS.md](DETAILS.md) every table behind it.

## Result

Before the leader's window, the fee per requested cost sets the order in 7 of 8 classes. With conflicting probes, 6 of 8 classes keep that order without a single broken pair. At the start of slot 2 arrival order shows, and with equal fees the earlier-sent probe goes first in 6 of 8 classes. Firedancer orders strictly by fee and breaks ties in reverse arrival; FireBAM keeps that order, while HarmonicFiredancer changes it. Sent through public RPC, the same bursts land in the target window less often and keep the fee order less ([REPORT.md, section 4.4](REPORT.md#44-control-path)).

## Two hypotheses from the code

The equal-fee arm isolates tie-breaking, and code gives two hypotheses before any data. For Firedancer it predicts reverse arrival order (H3). For Agave the scheduler queue is a `BTreeSet` of priority and a `Slab` key, and `Slab` reuses the last freed key first. On fresh keys a later probe with the same fee then goes first, and on recycled keys order does not depend on arrival (H4). The conclusion on tie-breaking comes only from the pre-window condition, where all probes reach the same scheduling call. The campaign finds H3 holding and leaves H4 undecided ([REPORT.md, section 4.1](REPORT.md#41-hypotheses-h3-and-h4)).

## How it works

A burst is 12 probe transactions from 12 payers, sent over one QUIC connection straight to the leader's `tpuQuic`, with no RPC node between. Fee and send order inside a burst are random and independent of each other, so the block position separates the effect of the fee from that of arrival. Four arms vary one property each: own accounts only, one shared account, one fee for all, and two compute-unit limits at one fee. Each burst aims at one of two moments, 300 ms before the window or the start of its second slot.

Builder classes leave a tick transaction in their slots. A probe in a slot with a tick measures the builder, and a probe in a slot of the same code base without one measures the validator, so each builder class is set against its base client within the same round. The analysis plan and the seeded tables are hashed into manifests, whose hashes went on chain before the first live probe of each stage ([prereg/](prereg/)). [DESIGN.md](DESIGN.md) gives the reasons for each choice.

## What it does NOT separate

From outside the leader the kit cannot see four stretches of the path: shred propagation from the leader to the RPC node, the leg from a builder's receiver to the leader, the way from the leader's QUIC server to its scheduler queue, and a Jito relayer on a port other than the default. Inside the clients, the spread over execution threads and eviction from a full buffer stay out of reach as well. [DESIGN.md](DESIGN.md#what-it-does-not-separate) lists each item, and [DETAILS.md, section 8](DETAILS.md#8-noise-and-what-the-kit-does-not-separate) names the tables it touches.

## Who can use the data

Each raw row gives a probe's signature and slot with the class and version its leader showed at the burst, so any position in the tables can be checked against the chain.

- Senders of time-critical transactions can see in which part of a leader's window a higher fee buys an earlier position, and where arrival time counts more ([REPORT.md, section 1](REPORT.md#1-the-answer)).
- Wallets and RPC providers can see what the public route does to inclusion and order next to a direct connection ([section 4.4](REPORT.md#44-control-path)).
- Client and builder teams get their own rule measured from outside and set against the base client ([sections 4.1 and 4.2](REPORT.md#41-hypotheses-h3-and-h4)).
- Researchers can run the kit on later epochs under the same pre-registered plan, and the measurement plan names what each larger measurement would settle ([section 8](REPORT.md#8-measurement-plan)).

The data can carry further tools. A fee estimate can take the leader's class and the moment of arrival into account, and a monitor can rerun the panel each epoch and flag a rule that changed. A client release can be checked against the ordering rule its code states, and a route can be compared with the direct path before a sender relies on it.

## Reproduce every number with one command

```bash
docker compose run --rm reproduce
```

It needs no key and no Rust build. It runs the known-answer selftest, re-reads each recorded signature from the chain, recomputes the verdicts from the raw data, and compares each generated table of REPORT.md and DETAILS.md with them; the first mismatch fails the run. A single step runs alone with `docker compose run --rm reproduce verify` or `analyze`. [RUNNING.md](RUNNING.md) covers measuring, development without spending, builds behind a TLS-inspecting proxy and the layout of the repository.

## License

MIT
