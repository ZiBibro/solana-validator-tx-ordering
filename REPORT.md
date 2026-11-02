# Report

This report gives the answer of the campaign on Solana mainnet over epochs 1071 to 1074 and the conditions it ran under; [DETAILS.md](DETAILS.md) holds the pilot of 2026-10-27 with every other table, and section 9 tells how each table comes from the raw data.

## 1. The answer

Before the leader's window opens, the fee sets the order. Probes that write only their own payer follow a fee rule in 7 of 8 classes, and probes that conflict on one account follow it in 8 of 8. In 7 of 8 classes the leader divides the fee by the requested compute-unit limit. The order key is thus the fee per requested cost, as in Agave's scheduler code ([DESIGN.md](DESIGN.md#why-this-design)). HarmonicAgave stays undetermined in the independent and denominator arms.

Conflict makes the rule strict. With conflicting probes, 6 of 8 classes put no pair with different fees out of fee order before the window. With probes that can run in parallel, Agave and JitoLabs break fee order in 111 and 116 of 432 such pairs (26% and 27%), Rakurai in 130 (30%).

At the start of slot 2, while the leader already builds the block, arrival order shows more often. With the fee held equal, the earlier-sent probe goes first in 6 of 8 classes. With random fees, Agave and Rakurai order by arrival when the probes can run in parallel, and JitoLabs and Rakurai when they conflict.

Firedancer is the strictest client. In its four fee cells no pair breaks fee order, and equal fees go in reverse arrival, as its code predicts (H3, section 4.1). FireBAM keeps Firedancer's fee order, while HarmonicFiredancer changes it (section 4.2). No cell reaches "no rule visible". At the pilot's spread of tau an equivalence verdict needs 28 to 177 bursts per cell, and the campaign had 8 (section 5).

Verdicts stand on the client class, which the analysis plan tests, since one leader carries at most 4 of its cell's 8 bursts. [DETAILS.md, section 6.15](DETAILS.md#615-each-leader-on-its-own) describes each of the 16 leaders without a verdict.

### 1.1 Form of each class and cell

In `independent` each probe has its own payer, and in `shared` all 12 write one account. `equal_fee` pays one fee to all 12, and `denominator` asks half of them for 1000 CU and half for 20 000. Brackets give the share of pairs against the order the arm predicts: the lower fee first in the fee arms, the 20 000 CU probe first in `denominator` and the later send first in `equal_fee`, so Firedancer's 1.00 there before the window means every pair in reverse send order. `pre300` aims the burst 300 ms before the window's first slot and `slot2` at the start of its second slot. Forms follow the [analysis plan](prereg/ANALYSIS-PLAN.md), and [DETAILS.md, section 6.2](DETAILS.md#62-verdicts-by-class-and-cell) gives the taus behind them.

<!-- itb:begin campaign-forms -->
| Class | independent pre300 | independent slot2 | shared pre300 | shared slot2 | equal_fee pre300 | equal_fee slot2 | denominator pre300 | denominator slot2 |
|---|---|---|---|---|---|---|---|---|
| Agave | fee-rule ties-unordered (0.26) | arrival-rule forward (0.48) | fee-rule ties-unordered (0.00) | mixed-rule (0.27) | undetermined (0.45) | arrival-rule forward (0.00) | divides (0.07) | undetermined (0.38) |
| AgaveBam | fee-rule ties-unordered (0.01) | fee-rule ties-unordered (0.06) | fee-rule ties-unordered (0.00) | fee-rule ties-reverse-arrival (0.00) | undetermined (0.51) | arrival-rule forward (0.11) | divides (0.00) | divides (0.00) |
| FireBAM | fee-rule ties-unordered (0.02) | fee-rule ties-unordered (0.06) | fee-rule ties-unordered (0.00) | fee-rule ties-unordered (0.00) | undetermined (0.53) | undetermined (0.48) | divides (0.00) | divides (0.06) |
| Firedancer | fee-rule ties-reverse-arrival (0.00) | fee-rule ties-reverse-arrival (0.00) | fee-rule ties-reverse-arrival (0.00) | fee-rule ties-reverse-arrival (0.00) | arrival-rule reverse (1.00) | undetermined (0.40) | divides (0.00) | divides (0.07) |
| HarmonicAgave | undetermined (0.38) | undetermined (0.40) | fee-rule ties-unordered (0.07) | fee-rule ties-unordered (0.08) | undetermined (0.52) | arrival-rule forward (0.16) | undetermined (0.40) | divides (0.19) |
| HarmonicFiredancer | fee-rule ties-unordered (0.09) | undetermined (0.41) | fee-rule ties-unordered (0.10) | fee-rule ties-unordered (0.07) | undetermined (0.41) | arrival-rule forward (0.18) | divides (0.05) | undetermined (0.42) |
| JitoLabs | fee-rule ties-unordered (0.27) | undetermined (0.54) | fee-rule ties-arrival (0.00) | arrival-rule forward (0.40) | undetermined (0.42) | arrival-rule forward (0.00) | divides (0.24) | undetermined (0.39) |
| Rakurai | fee-rule ties-unordered (0.30) | arrival-rule forward (0.46) | fee-rule ties-unordered (0.00) | arrival-rule forward (0.45) | undetermined (0.53) | arrival-rule forward (0.00) | divides (0.15) | undetermined (0.39) |
<!-- itb:end campaign-forms -->

## 2. Panel and runs

The campaign panel holds two leaders from each of 8 classes by gossip `clientId`, 16 validators. Agave-based builds 4.3.2 and 4.4.0 run under five classes, and Firedancer 26.10.4 and 26.10.5 under the other three. Fourteen leaders stayed from the pilot and two joined, `4VRs6A9z...` (Firedancer) and `LA1NEzry...` (FireBAM), 18 validators over both stages. In each class, 0 of 62 campaign bursts found the leader under another `clientId` than at selection.

The pilot ran 68 bursts on 2026-10-27 in epoch 1069. From 2026-10-29 to 2026-11-02 the campaign wrote 560 of the 576 bursts of its seeded table, one plan per epoch from 1071 to 1074. The 16 it lacks are round 3 of epoch 1071 (section 6). Run `034521Z` funded the payers and was stopped before its first window so that the campaign could start on the leader correction of commit `6fdceca`. [DETAILS.md](DETAILS.md#2-validators-and-clients) gives the panel and run tables in sections 2 and 3.

## 3. Spend

<!-- itb:begin spend -->
| Item | UTC | What | Probe fees (lamports) | Funding and closing fees | Paid | Spend journal growth | Limit of the run (lamports) |
|---|---|---|---|---|---|---|---|
| anchor of pilot | 2026-10-27 08:52:11 | `3jmFZBgsQoXTnKVS`... | - | - | 5000 | - | - |
| anchor of campaign | 2026-10-28 01:21:59 | `3s1dQY9ZyEMQrHZs`... | - | - | 5000 | - | - |
| `campaign-mainnet-20261028T034521Z` | 2026-10-28 03:46:01 | 0 probes included, 1 funding and closing transactions | 0 | 5000 | 5000 | 5000 | 13527630 |
| `campaign-mainnet-20261028T055501Z` | 2026-10-28 05:55:36 | 652 probes included, 0 funding and closing transactions | 3400800 | 0 | 3400800 | - | 13532630 |
| `campaign-mainnet-20261029T120927Z` | 2026-10-29 12:15:03 | 852 probes included, 0 funding and closing transactions | 4517910 | 0 | 4517910 | 4517910 | 12519350 |
| `campaign-mainnet-20261030T015219Z` | 2026-10-30 01:52:56 | 1728 probes included, 1 funding and closing transactions | 9108840 | 5000 | 9113840 | 9113840 | 21452780 |
| `campaign-mainnet-20261031T014357Z` | 2026-10-31 01:46:50 | 1704 probes included, 1 funding and closing transactions | 8946510 | 5000 | 8951510 | 8951510 | 30539620 |
| `campaign-mainnet-20261101T041655Z` | 2026-11-01 04:17:34 | 1716 probes included, 1 funding and closing transactions | 9118800 | 5000 | 9123800 | 9123800 | 39589290 |
| `pilot-mainnet-20261027T085253Z` | 2026-10-27 08:53:32 | 811 probes included, 13 funding and closing transactions | 4280230 | 65000 | 4345230 | 4345230 | 4376440 |
| `close-mainnet-20261102T055032Z` | 2026-11-02 05:50:32 | 12 closing transactions | - | 60000 | 60000 | - | - |
| **total** |  |  |  |  | **39528090** (0.039528 SOL) |  | code cap 0.05 SOL |
<!-- itb:end spend -->

Probe fees are `meta.fee` of each included probe, and each funding or closing transaction pays the 5000-lamport base fee. The spend journal settles against the chain at each start, so its growth equals what the run paid; the start of `120927Z` settled the 652 included probes of `055501Z`, the 3 400 800 lamports of that run. After the closing transactions of 2026-11-02 the journal holds the table's total.

## 4. Campaign results

The campaign ran the [analysis plan](prereg/ANALYSIS-PLAN.md) with the [campaign addendum](prereg/CAMPAIGN-ADDENDUM.md), the rules the plan leaves to the code. Their manifest went on chain at 01:21:59 UTC on 2026-10-28 (`data/prereg-anchors.json`), before the first campaign probe, and no later commit changes a file it pins ([DETAILS.md, section 6](DETAILS.md#6-campaign)). The order tests keep these bursts:

<!-- itb:begin campaign-exclusions -->
560 bursts: 411 kept for the order tests, 149 left out, 11 of them for more than one reason. Reasons: control-path 64, fewer-than-two-in-a-block 6, outside-timing-band 90.
<!-- itb:end campaign-exclusions -->

Burst 194 of `055501Z` (JitoLabs, denominator, slot 2) met a connection the leader closed: its 12 sends read `connection_closed`, no probe landed, and the order tests leave it out ([tests/test_campaign_data.py](tests/test_campaign_data.py)).

### 4.1 Hypotheses H3 and H4

Both hypotheses come from the base clients' code before any data ([README](README.md#two-hypotheses-from-the-code)) and read tau send of the equal-fee arm before the window ([campaign addendum, section 3](prereg/CAMPAIGN-ADDENDUM.md)). H3 holds: Firedancer put each equal-fee pair of its 8 bursts in reverse send order. H4 stays undecided, since Agave's tau 0.095 (p 0.266) is neither significant nor equivalent to zero after Holm.

<!-- itb:begin campaign-hypotheses -->
| Class | Hypothesis | Bursts | tau send, equal fee, pre300 (95% CI) | p | Significant after Holm | TOST passed after Holm | Outcome |
|---|---|---|---|---|---|---|---|
| AgaveBam | comparison | 8 | -0.011 (-0.289 to 0.266) | 0.904 | no | no | - |
| JitoLabs | comparison | 7 | 0.160 (-0.119 to 0.439) | 0.0583 | no | no | - |
| HarmonicAgave | comparison | 7 | -0.047 (-0.164 to 0.071) | 0.606 | no | no | - |
| HarmonicFiredancer | comparison | 6 | 0.187 (-0.225 to 0.599) | 0.0407 | no | no | - |
| Firedancer | H3 | 8 | -1.000 (-1.000 to -1.000) | 7.22e-70 | yes | no | holds |
| FireBAM | comparison | 6 | -0.061 (-0.482 to 0.361) | 0.521 | no | no | - |
| Rakurai | comparison | 8 | -0.057 (-0.230 to 0.116) | 0.483 | no | no | - |
| Agave | H4 | 7 | 0.095 (-0.085 to 0.275) | 0.266 | no | no | undecided |
<!-- itb:end campaign-hypotheses -->

### 4.2 Builder against its base

Each builder class stands against its base client within the same round and arm. FireBAM passes the equivalence test on tau fee against Firedancer at both moments (TOST p 8.03e-08 and 0.00131). HarmonicFiredancer lowers tau fee against Firedancer by 0.172 before the window and by 0.518 at slot 2 (p 0.000122 and 0.000977). The other 12 rows stay undetermined.

<!-- itb:begin campaign-pairs -->
| Pair | Timing | Statistic | Strata | Mean difference | p | TOST p | Label test | Form |
|---|---|---|---|---|---|---|---|---|
| AgaveBam vs JitoLabs | pre300 | fee | 11 | 0.286 | 0.0156 | 0.859 | exact over 2048 | undetermined |
| AgaveBam vs JitoLabs | pre300 | cross | 11 | -0.054 | 0.585 | 0.0561 | exact over 2048 | undetermined |
| AgaveBam vs JitoLabs | slot2 | fee | 5 | 0.750 | 0.0625 | 0.982 | exact over 32 | undetermined |
| AgaveBam vs JitoLabs | slot2 | cross | 5 | -0.467 | 0.375 | 0.77 | exact over 32 | undetermined |
| FireBAM vs Firedancer | pre300 | fee | 10 | -0.027 | 0.125 | 8.03e-08 | exact over 1024 | builder-does-not-change-order |
| FireBAM vs Firedancer | pre300 | cross | 10 | 0.130 | 0.273 | 0.262 | exact over 1024 | undetermined |
| FireBAM vs Firedancer | slot2 | fee | 13 | -0.064 | 0.0312 | 0.00131 | exact over 8192 | builder-does-not-change-order |
| FireBAM vs Firedancer | slot2 | cross | 13 | -0.165 | 0.17 | 0.376 | exact over 8192 | undetermined |
| HarmonicAgave vs Agave | pre300 | fee | 12 | -0.193 | 0.00488 | 0.439 | exact over 4096 | undetermined |
| HarmonicAgave vs Agave | pre300 | cross | 12 | 0.003 | 1 | 0.0314 | exact over 4096 | undetermined |
| HarmonicAgave vs Agave | slot2 | fee | 10 | 0.298 | 0.111 | 0.725 | exact over 1024 | undetermined |
| HarmonicAgave vs Agave | slot2 | cross | 10 | -0.359 | 0.0391 | 0.856 | exact over 1024 | undetermined |
| HarmonicFiredancer vs Firedancer | pre300 | fee | 15 | -0.172 | 0.000122 | 0.154 | exact over 32768 | builder-changes-order |
| HarmonicFiredancer vs Firedancer | pre300 | cross | 15 | 0.141 | 0.246 | 0.304 | exact over 32768 | undetermined |
| HarmonicFiredancer vs Firedancer | slot2 | fee | 11 | -0.518 | 0.000977 | 0.992 | exact over 2048 | builder-changes-order |
| HarmonicFiredancer vs Firedancer | slot2 | cross | 11 | -0.222 | 0.104 | 0.567 | exact over 2048 | undetermined |
<!-- itb:end campaign-pairs -->

### 4.3 Segments between ticks

The analysis plan asks whether the segments between two market ticks in builder slots are rounds in time. Of the 50 equal-fee bursts at slot 2, 18 spread their probes over two segments or more and carry the test; the other 32 sit in one segment and give no pair to compare. Over those 18, send rank against segment gives tau 0.757, and none has a negative tau numerator, so the form reads supported.

<!-- itb:begin campaign-rounds -->
Arm equal_fee, timing slot2: 50 bursts, 18 with probes in two segments or more, share of bursts with a negative S 0.00. Pooled: tau 0.757, p 6.56e-59. Form: **supported**.

| Class | Bursts | tau send rank against segment | p |
|---|---|---|---|
| AgaveBam | 6 | 0.854 | 1.31e-27 |
| FireBAM | 1 | 0.769 | 0.000505 |
| HarmonicAgave | 5 | 0.705 | 1.11e-14 |
| HarmonicFiredancer | 6 | 0.669 | 1.13e-14 |
<!-- itb:end campaign-rounds -->

### 4.4 Control path

The control path sends the same kind of burst through `sendTransaction` on `api.mainnet-beta.solana.com` with `skipPreflight` and `maxRetries` 0, once per leader and epoch, 64 bursts in all. Within the same leader and epoch its share of probes in the target window is lower than on the direct path by 0.208 and its tau fee by 0.483, both at p 5e-05 over 54 strata. Of its 768 probes 166 landed in another leader's block, against 3 of 5892 delivered direct probes ([DETAILS.md, section 6.7](DETAILS.md#67-probes-outside-their-window)). Through public RPC a class verdict measures the route together with the scheduler.

<!-- itb:begin campaign-control -->
| Measure | Strata (leader, epoch, arm, condition) | Mean RPC minus QUIC | p | Label test |
|---|---|---|---|---|
| inclusion share | 54 | -0.208 | 5e-05 | 19999 draws, seed itb-prereg-label-v1, Monte Carlo SE 5e-05 |
| tau fee | 54 | -0.483 | 5e-05 | 19999 draws, seed itb-prereg-label-v1, Monte Carlo SE 5e-05 |

Path latency: quic median 0.0 slots after the window's first slot (4944 probes); rpc median 1.0 slots after the window's first slot (660 probes).
<!-- itb:end campaign-control -->

## 5. Conditions of the measurement

Each condition limits what the tables can say.

- **A spend cap of 0.05 SOL in code**. The cap allowed 8 bursts per class and cell ([DETAILS.md, section 5.15](DETAILS.md#515-minimum-for-the-campaign)), so an undetermined cell reads as lack of power.
- **One sending machine on one network line**. Median one-way estimates ran from 16 to 82 ms by leader ([DETAILS.md, section 6.8](DETAILS.md#68-path-latency)); with the send moment corrected for half the round trip, 218 of 248 pre-window and 197 of 248 slot-2 bursts had their arrival estimate in the band. Probes from much further away stay unmeasured.
- **The public RPC node as the eye on the chain**. The slot clock runs on its `firstShredReceived` events, so shred propagation from the leader to that node enters the arrival estimate as error of unknown source ([DESIGN.md](DESIGN.md#what-it-does-not-separate)).
- **Four epochs and two leaders per class**. Stability is described without a test, and the split between a client's rule and one operator's setup rests on two leaders. Firedancer gives tau fee 0.905 in each epoch, while Rakurai falls from 0.645 in epoch 1071 to 0.264 in 1074 ([DETAILS.md, section 6.12](DETAILS.md#612-epochs-and-rounds)).
- **One control route**. Section 4.4 describes one public endpoint with preflight off.

## 6. What went wrong in the campaign

Round 3 of epoch 1071 is lost. The run started on 2026-10-28 sent rounds 0 to 2 on 2026-10-29, from 03:00 to 09:41 UTC. Four starts between 11:10 and 11:56 UTC sent no burst; three logged a public-node error, two of them -32019 from `getSignaturesForAddress`, while settling the earlier run's bookings ([logs/campaign-20261029T111032Z.txt](logs/campaign-20261029T111032Z.txt), [logs/campaign-20261029T113554Z.txt](logs/campaign-20261029T113554Z.txt)). Commit `c062eb8` settles such bookings from one listing of the payers' history, which `c3ae1f6` and `18a543c` retry on -32019 and run once per start.

The plan drawn at 11:55 UTC left round 3 out, since its first window 462872092 lay before slot 462872795 ([draw-notes.json](data/plans/campaign-mainnet-e1071-20261029T115552Z/draw-notes.json)). The run started at 12:15 UTC on `18a543c` sent rounds 4 to 7, and later epochs ran on the same commit. A lost round moves to no other hour, which would break the blocking by round. [DETAILS.md, section 9](DETAILS.md#9-what-went-wrong) gives the planned, written and unreached bursts of each run.

## 7. Other measurements of the same question

Eight public repositories measured the ordering rule on mainnet after Alpenglow; the first four read on 2026-10-27, the rest on 2026-11-02.

- [fomoles/superteam-inside-the-block](https://github.com/fomoles/superteam-inside-the-block), epoch 1066. Probe pairs go straight to the leader's TPU. It reads the key as fee per estimated cost unit (check C6, -0.61) and Firedancer 26.10.4 giving fee ties to the later arrival, as our denominator arm and H3 do.
- [eternally-black/alpenglow-validator-ordering](https://github.com/eternally-black/alpenglow-validator-ordering), 2026-10-24 to 2026-10-26, pre-registered in a mainnet Memo. Six core targets, five in our panel, order by Agave's `reward / (cost + 1)`, and Firedancer lands the later of two identical probes first in 50 of 54 pairs.
- [ukraineopt/inside-the-block](https://github.com/ukraineopt/inside-the-block), 5296 probes at 27 validators without pre-registration. It reads arrival order in short batches for both Harmonic classes; our slot-2 equal-fee cells agree, while before the window HarmonicFiredancer follows a fee rule.
- [zdfgu113/inside-the-block](https://github.com/zdfgu113/inside-the-block), from 2026-10-23. Of 135 same-block pairs, AgaveBam puts the higher fee first in 25 of 32, and both Harmonic classes stay near chance at its price range.
- [factoruuu/inside-the-block-solana](https://github.com/factoruuu/inside-the-block-solana), epoch 1071, sent 612 transactions in 51 bursts through one public RPC endpoint with preflight on. It detects no rule in any class, Firedancer at fee concordance 0.589 (0.442 to 0.736), and states that it does not separate RPC forwarding from the scheduler, the split our control path measures (section 4.4).
- [tempometer/inside-the-block](https://github.com/tempometer/inside-the-block), runs of 2026-10-26 and 2026-10-27 through public RPC relays whose forwarding its operator log puts at 8 to 30 s; each of its 398 rows is attributed afterwards to the leader of its landing slot.
- [9xj89gzrtw-hue/solana-validator-block-ordering](https://github.com/9xj89gzrtw-hue/solana-validator-block-ordering), epoch 1074, passive: over 5430 transactions of other senders in 24 blocks of 6 validators, Kendall tau-b -0.0424 between `tx_index` and priority fee per compute unit, read as no fee rule. That tau mixes arrival time with bundles of many senders; our probes leave in a send order drawn apart from the fee, so the zero does not contradict our fee rule.
- [AndrewInUA/solana-block-order](https://github.com/AndrewInUA/solana-block-order), epoch 1075, 83 included probes through Helius RPC at six validators of six classes: no fee rule (price tau -0.196 to 0.400, no p under 0.05), send order in 3 classes. Its rank sorts by slot first, while each of the 11 batches with included probes spread over two slots or more and 32 of the 83 landed outside the target's four slots, so arrival enters the rank. Our control path loses fee order through RPC too (section 4.4); the fee rule stands on direct probes waiting together before the window.

## 8. Measurement plan

Each step lifts one condition of section 5.

- **Bursts per cell at the pilot's minimum**. With 28 to 177 bursts per cell an undetermined cell can read "no rule visible", and a builder pair can show at each moment whether the builder keeps its base order.
- **Senders in several regions**. Bursts from several places into the same windows separate distance from rule and test the half-round-trip correction beyond 82 ms one way.
- **An own RPC node**. A slot clock and block reads from the kit's own node take the public node's event queue out of the arrival estimate.
- **More epochs and more leaders per class**. A stability test fixed before data turns the epoch table into a verdict. Three or more leaders per class separate a client's rule from one operator's setup.
- **More control routes**. Other RPC providers and staked connections, with preflight on and off, each stand against the direct path within one leader and epoch.

## 9. How the tables are made

`python -m itb report` writes each table between its `<!-- itb:begin NAME -->` and `<!-- itb:end NAME -->` lines from `data/` and `logs/` alone, and `--check` fails when a table differs from the raw data, stands in neither file, or is missing from the section a pointer of DETAILS.md names. `tx_index` in `collect.jsonl` gives each probe's index among its block's signatures, which one `getBlock` call shows; full details need `maxSupportedTransactionVersion` 1 ([README.md](README.md#who-can-use-the-data)).
