# Campaign addendum to the analysis plan

The pilot anchor pinned [ANALYSIS-PLAN.md](ANALYSIS-PLAN.md) and `itb/prereg.py`, so neither file changes after the pilot. This addendum joins them in the campaign manifest (`CAMPAIGN_MANIFEST_FILES` in `itb/verify.py`) and goes on chain with the campaign memo before the first campaign burst. It states in words each rule that the plan leaves open and each rule that the campaign code carries beyond the plan text. Where the plan and this file differ, this file governs the campaign; the pilot stays under the plan alone. Section numbers are this file's own, and "plan section" or "plan line" points into ANALYSIS-PLAN.md.

## 1. Stability across epochs is descriptive

Plan section 7 calls a class stable when a TOST of each epoch against the other epochs passes in a stability family, and unstable when tau fee shows significant heterogeneity across the four epochs. The plan names neither the heterogeneity test nor the size of that family, and it does not say how the difference of an epoch from the rest and its standard error are computed. In the campaign plan section 7 is therefore descriptive: REPORT shows tau fee per class and epoch and its spread over rounds, without a test of stability and without a stability family. The blocked table gives a class 2 bursts per cell in each epoch, so a test of one epoch against the rest would rest on a quarter of the bursts behind a class verdict, and those verdicts already cannot reach equivalence (section 2). Rounds are described the same way.

## 2. The campaign minimum was not reached

`prereg/campaign-minimum.json` holds the minimum of plan section 5 for each of the six verdict slots. The anchored number is the largest of them, 177 bursts per class and cell, from tau send of the equal-fee arm. The campaign table has 8 per class and cell, and the file records `"reached": false`. That has these consequences.

- The campaign runs the four epochs of `prereg/campaign-table.json` and nothing more. No epoch is added, and no burst is added to any cell.
- A form that rests on a TOST is expected out of reach at the pilot's pooled spread. With B bursts and a standard error above zero, the TOST of plan section 3 passes at the first Holm threshold alpha of its family only when

  ```
  |tau| + t[B-1; 1 - alpha] * SD / sqrt(B) <= delta
  ```

  where SD is the standard deviation of burst tau; for full bursts the jackknife standard error of the pooled tau equals SD / sqrt(B). Later Holm thresholds open only after a smaller p has passed. At an estimate of exactly zero the bound allows at most this SD:

  | Form | Family and first threshold | B | t quantile | Largest SD that passes | Pilot's pooled SD |
  |---|---|---|---|---|---|
  | no rule visible, independent and shared arms | equivalence, 96 tests, 0.05/96 | 8 | 5.370 | 0.105 | 0.332 to 0.462 (tau fee, tau cross) |
  | no rule visible, equal-fee arm | equivalence, 96 tests, 0.05/96 | 8 | 5.370 | 0.105 | 0.533 (tau send) |
  | does not divide, denominator arm | equivalence, 96 tests, 0.05/96 | 8 | 5.370 | 0.105 | 0.195 (tau limit) |
  | builder does not change order | pair equivalence, 16 tests, 0.05/16 | 16 strata | 3.177 | 0.252, SD of the stratum differences | about 0.47 to 0.65 |

  The t quantiles come from `stats.t_quantile` at 7 and 15 degrees of freedom. The pilot's SDs are the residual SDs of burst tau in `prereg/campaign-minimum.json`. The difference of two bursts that vary independently has about 1.41 times their SD, which gives the last row at the pilot's spread of tau fee and tau cross. Each pilot SD lies above the largest SD that passes, so the expectation rests on the pilot's spread and is no bound of the test itself.

  The exception is a spread of zero or close to it. With a standard error of exactly zero the code's TOST (`stats.tost_p`) gives p 0 when the absolute estimate lies below delta and p 1 when it reaches delta or beyond; with fewer than one degree of freedom or a standard error that is not a number it gives p 1. A p of 0 passes at every Holm threshold, and a standard error close to zero gives a p close to 0. The pilot holds such a case: FireBAM against Firedancer in the pre-window condition, tau fee, had 2 strata whose differences were both 0, so its TOST p was 0 and the pair read builder-does-not-change-order.
- Forms that rest on a significant tau (inverted fee sign, mixed rule, fee rule, arrival rule, divides, builder changes order) do not depend on the minimum.
- "Undetermined" means that the data did not decide between the forms. It is no evidence that a rule is absent.
- After the data no cells, classes, moment conditions or epochs are pooled, and no test is added. Verdicts stay per class, moment condition and arm, as plan section 4 sets them.

## 3. Hypotheses H3 and H4

The README states both hypotheses before any data, from the code of the base clients.

- **H3, Firedancer.** The pack keeps transactions of equal priority in a treap ordered by insertion, and the scheduler walks the treap in reverse. Of two probes with the same fee the later one goes first: reverse arrival order.
- **H4, Agave.** The scheduler queue is a `BTreeSet` keyed by priority and then by a `Slab` key, and `Slab` reuses the last freed key first. On fresh keys a later probe with the same fee goes first; on recycled keys the order does not depend on arrival.

**Statistic.** Both hypotheses are judged on one slot only: tau send of the equal-fee arm in the pre-window condition (plan line 79), with its test in the 96-test verdict family and its TOST in the 96-test equivalence family. Tau ties of the independent and the shared arm stays the descriptive subform of the fee rule at alpha 0.05 outside every Holm family, and it decides nothing about H3 or H4. The slot-2 condition describes tie order and judges neither hypothesis.

**Classes.** H3 is judged on the class Firedancer and H4 on the class Agave. The code reading covered the forks only for what they inherit from the base clients, and each other class can reorder probes before the base scheduler sees them: four classes put a builder in front of it (AgaveBam, FireBAM, HarmonicAgave, HarmonicFiredancer), and two change the scheduling path itself (the bundle stage of JitoLabs, the own scheduler of Rakurai). REPORT shows their equal-fee results next to H3 and H4 as a comparison, without a judgement on either hypothesis.

**Rules.**

- H3 holds when tau send of Firedancer is negative and significant after Holm. It fails when that tau is positive and significant, or when it passes the TOST, which section 2 expects out of reach at the pilot's spread. Otherwise H3 stays undecided.
- H4 allows reverse arrival order on fresh keys and no dependence on arrival on recycled keys, and a mix of both gives a value in between. The `Slab` key is invisible from outside, so no test separates the two parts, and H4 has no outcome "holds". H4 fails when tau send of Agave is positive and significant after Holm, since neither part predicts forward arrival order. A negative significant tau send reads "agrees with the fresh-key part", and a TOST pass reads "agrees with the recycled-key part". Otherwise H4 stays undecided.
- REPORT's hypothesis table (`campaign-hypotheses`) gives the rows of H3 and H4 with these outcomes and the other classes as comparison rows without an outcome. REPORT also splits the Agave equal-fee arm of the pre-window condition by load quartile descriptively (plan line 79).

## 4. Bursts left out of the tests

`analyze.units_of` gives each burst a list of reasons. A burst enters the verdict tests, the pair tests and the comparison of the moment conditions only with an empty list, and REPORT counts each reason. A burst can carry several. The reasons are eight.

1. `control-path`: the burst went through the RPC control path, which enters only the control comparison (section 9).
2. `relayer-port`: the leader's `tpuQuic` at the burst moment stood on port 11228, the Jito relayer default (`RELAYER_PORT`), by the probe's flag or by the recorded port.
3. `client-differs-from-selection`: the leader's `clientId` in gossip at the burst moment differs from the class the panel chose the leader for.
4. `outside-timing-band`: the arrival estimate (section 10) lies outside the band `TIMING_BAND_MS` of its moment condition. Plan line 75 sets such bursts apart from the comparison of the two conditions; they also stay out of every verdict and pair test, and REPORT counts them per condition.
5. `slot-clock-behind`: `getSlot` at processed commitment ran `CLOCK_LAG_SKIP_SLOTS` = 2 or more slots ahead of the slot clock. For rows of schema version 1 the confirmed blockhash came from slot `first_slot - BLOCKHASH_LEAD_SLOTS` or later, with `BLOCKHASH_LEAD_SLOTS` = 6.
6. `foreign-probe-in-block`: a slot that holds included probes of the burst in its target window also holds included probes of another burst of the same run.
7. `fewer-than-two-in-a-block`: no block of the target window holds two or more probes of the burst. Only probes included in the target window count, and a block with one probe adds no pair.
8. `repeated-burst`: the burst repeats a table burst that was sent earlier (section 5). Only the earliest send of a table burst enters the tests.

## 5. Epoch indexes, lost rounds and repeated bursts

- Epoch index e of the campaign table runs only in chain epoch E + e, where E is the epoch of the pinned panel (section 8). The plan command refuses any other chain epoch. For a panel of epoch 1071 the indexes 0 to 3 run in epochs 1071 to 1074.
- A failed run of an index is drawn again in the same chain epoch after a pause, from the gossip snapshot (`cluster-nodes.json`) of that index's first plan. `itb campaign --nodes-from-first-plan` takes the snapshot from the earliest plan under `data/plans` with the same epoch index, chain epoch and manifest hash, and `scripts/campaign.sh` passes that flag on every draw, so a campaign resumed with FROM_INDEX scans the same gossip. For epoch index 0 the first plan is the one committed with the campaign manifest, so the live plan of index 0 scans its windows with that plan's snapshot and keeps the windows of its rounds still ahead. The new plan keeps the windows of the rounds still ahead and leaves out the round in progress. Three failed attempts on one index stop the campaign, and a resumed campaign continues only with indexes whose chain epoch has not passed.
- When the chain epoch of an index passes, every round of it that has not run is lost. Such rounds never move to a later epoch, and the plan command refuses a chain epoch that has passed.
- A table burst is identified by stage, epoch, round, leader, arm, moment condition and path. When one appears more than once in the data, its earliest send counts, ordered by the UTC of the burst row and then by run and burst sequence, and every later copy leaves the tests with the reason `repeated-burst` (section 4).
- A campaign with fewer than four epochs, or with lost rounds, is read by the same rules on the bursts that ran: the families keep their 96 and 16 tests and alpha 0.05, and nothing replaces a lost burst. REPORT counts the bursts behind each verdict, and the plan notes and the campaign log name each round left out and each index lost. A class pair has 4 strata per epoch in each moment condition. Three epochs give 12, which can pass the first pair threshold (section 6). Two epochs give at most 8 strata to every pair, and a smallest p of 0.0078 does not pass the first threshold of 0.003125; no p of the pair family passes it then, so the step-down Holm rejects none of the 16 tests.

## 6. Class pairs

- Up to 20 strata the pair test enumerates every sign pattern, so with k strata its smallest two-sided p is 2/2^k. The 16-test pair family runs Holm step-down: its threshold after r smaller rejected p values is 0.05/(16 - r). The first threshold, 0.003125, needs at least 10 strata, since 2/2^9 = 0.0039 is too large. A pair with fewer strata passes only after other tests of the family: 9 strata after at least 4 smaller p values, 8 strata after 10, 7 strata after 13, 6 strata after 15. With 5 strata or fewer the smallest p of 0.0625 lies above every threshold.
- The pair TOST is expected out of reach at the campaign's 16 strata at the pilot's spread of stratum differences, for the reason section 2 gives. The exception of section 2 holds here too: stratum differences with zero or nearly zero spread inside plus or minus delta pass the TOST at any number of strata from 2, as FireBAM against Firedancer did in the pilot.
- Pair strata come from bursts without any reason of section 4, and the builder side counts only labelled blocks (section 7).

## 7. The builder label

Plan section 8 counts only slots with a tick from a known signer for the builder rule. The known signers are two keys, fixed here and in `BUILDER_SIGNER` of `itb/analyze.py`:

| Classes | Tick signer |
|---|---|
| AgaveBam, FireBAM | `BAMgx3XPWrXkNUuQiVWUZU6eB2HQZdwz9HNnT4tpo8LG` |
| HarmonicAgave, HarmonicFiredancer | `Harmonic8SoAfZixJqUxxdSeyWzr6q7XFjuiXS5Z2zPg` |

- The rule applies to the pair tests of plan section 8. In each stratum the burst of the builder class counts only its blocks whose slot carries a tick of its class's signer, and the burst of the base class counts all its blocks. A builder burst without such a block leaves the labelled test in that stratum.
- The blocks of the builder class without that tick form the group without a label: one row per pair, moment condition and tau, with its number of strata and its mean difference, outside every Holm family and without a p.
- The class verdicts of plan section 4 take every block of a class's bursts, because the class is the client that gossip showed for the leader at the burst moment.
- Plan line 89 says when the label holds; this file sets what follows when it fails. If a tick of a known signer appears in the campaign data in a slot whose leader belongs to a class without a builder, the label of that signer fails. The tests of the two pairs whose builder class carries that signer stay in the 16-test family with p 1 and TOST p 1, so the family keeps its size, and their rows read `builder-label-failed`. REPORT names the slots that failed the label.
- REPORT section 7 prints for each run the share of slots with a BAM tick and with a Harmonic tick separately for each class of the slot's leader, builder classes and the remaining ones alike.

## 8. The panel

- The campaign manifest pins one panel, `data/panels/<id>/panel.json`, by its SHA-256. The plan command refuses a panel with another hash and a manifest that pins none. Without the manifest file it draws no plan at all. The 16 leaders of that panel run all four epochs, and its epoch E fixes the chain epochs of section 5.
- A leader window passes when it holds all four slots and the window right before it does not belong to another validator whose `tpuQuic` stands on the same IP as the leader's, whatever the port. The pilot panel compared the whole address, IP and port. Several validators share one receiver of a builder, and no documentation says what such a receiver does with a transaction that reaches it during the window of another validator it serves. In the pilot all 12 probes of burst 52, sent to `JUPiTERr...` on `198.13.140.105:12349`, landed one slot early in the block of `nymsGg7Z...`, which advertises `198.13.140.105:9007`. An independent public measurement found that 596 of 603 direct-TPU probes that landed with a leader other than their target landed with a leader advertising the target's IP ([fomoles/superteam-inside-the-block](https://github.com/fomoles/superteam-inside-the-block)).
- REPORT's neighbour table counts, for each panel, the windows that pass the whole-address rule and those of them that follow a leader on the same IP with another port. The latter are the windows the campaign rule removes.
- The window scan of a plan uses the gossip snapshot the plan stores; the probe reads `tpuQuic` and `clientId` again at each burst.

## 9. Control path

Plan lines 39 and 96 cite "plan section 5.2", which belongs to the implementation plan, a document outside this repository. This section states what the campaign takes from it.

- The campaign table puts one control burst per leader and epoch into the independent arm, 64 bursts in all. The table gives a leader one moment condition per arm and epoch, with two direct bursts in it, and the control burst takes that condition of the independent arm.
- A stratum is one leader, epoch, arm and moment condition. It holds the control bursts of that leader and the direct-path bursts with the same arm and condition in the same epoch.
- Two measures are compared. Tau fee needs two probes in one block of the target window, as a verdict burst does. The inclusion share in the target window, over delivered probes, also keeps a burst whose probes formed no pair in a block of the window (reason 7 of section 4), since leaving it out would select on the outcome. Any other reason of section 4 except `control-path` keeps a burst out of both measures.
- One test per measure swaps path labels within each stratum. Its statistic sums over the strata the RPC mean minus the direct mean, and the test is two-sided. Up to 20 000 arrangements (`LABEL_TEST_B` + 1) it enumerates every one. Beyond that it draws `LABEL_TEST_B` = 19 999 arrangements, each stratum's RPC labels taken as the first k items of the own Fisher-Yates shuffle (`stats.fisher_yates`) on `random()` of `random.Random(LABEL_TEST_SEED)`, and p = (b + 1)/(B + 1). Beyond 20 strata the pair test of section 6 draws its 19 999 sign patterns the same way, with one Fisher-Yates shuffle of the two labels per stratum. REPORT prints the Monte Carlo standard error sqrt(p(1 - p)/B) next to each p that comes from draws, in the same cell as the number of draws and the seed.
- "Few" in plan line 96 means that no arrangement of the strata can reach p of 0.05 or below. The smallest attainable p is the share of arrangements whose absolute statistic equals the largest one, or 1/(B + 1) with draws; when it exceeds 0.05 the measure is descriptive, and REPORT prints that smallest p in place of a p of the data. The control comparison stays outside every Holm family and changes no verdict.

## 10. Measures stated more exactly

- **Plan line 29.** The 95% interval belongs to the pooled class tau: a jackknife over bursts with the Student t quantile at bursts minus one degrees of freedom. REPORT prints the mean of burst taus next to it in the cell tables as a point value.
- **Plan line 31.** Strictness in the independent and the shared arm takes the fee order as the predicted order: a pair with different fees is violated when the lower fee stands earlier. Every probe of these arms requests 1 000 compute units with the same loaded-data limit, so the fee carries the intended difference of client priority between two probes of a burst; strictness does not use the recomputed cost.
- **Plan line 71.** Sigma comes from the 61 pilot bursts without any reason of section 4; of the 68, six lay outside the timing band and one had fewer than two probes in a block. The anchored minimum is the largest of the six slot minima. "The main campaign checks" names no action: section 2 governs what follows from the minimum, and the campaign's own spread shows in the intervals of its verdict tables.
- **Plan line 75.** `analyze.arrival_ms` takes the send offset from the first slot's start by the first source present: the node's `firstShredReceived` timestamp (`first_send_node_offset_ns`); then the local receipt of the first shred (`first_send_offset_ns`); then the final aim at the send, target arrival minus half the RTT minus the predicted start of the first slot; then the aim at signing, send moment minus the predicted start. Half the RTT is added to the offset, with the RTT of the final aim (`send_rtt_ns`) or else of the burst row (`rtt_ns`). `analyze.slot2_ms` takes the start of slot 2 from the gap of the node timestamps, then from the gap of local receipts, then from the final aim, target arrival minus the predicted start of the first slot, and last from the mean slot length `slot_ms`.
- **Plan line 83.** Load quartiles are formed twice, once by `costUnits` and once by transaction count, each over the mean of a burst's blocks; the two are never summed.
- **Plan section 10.** The rounds test runs on the campaign data with the same rule and refutation criterion, and REPORT shows it in the campaign part, outside every Holm family.
