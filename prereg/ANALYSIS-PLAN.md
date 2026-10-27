# Analysis plan, fixed before live data

This file states how the measurements are analysed. It was written before the first live burst of the pilot, and the chain holds the proof of that order.

`python -m itb manifest --stage pilot` writes `prereg/manifest-pilot.json`, which lists the SHA-256 of this file and of the two files that fix the pilot's numbers, `prereg/pilot-table.json` and `itb/prereg.py`. Before the first live burst, `itb-probe anchor --stage pilot` sends one legacy transaction from the measuring wallet with a single Memo v2 instruction that reads `itb-prereg <SHA-256 of the manifest>`, and records its signature in `data/prereg-anchors.json`. `itb verify` then checks two things. Every file listed in the manifest must still carry its hash, and the memo's block time must come before the first inclusion of any burst of the stage. A second memo before the first burst of the main campaign anchors the minimum number of bursts computed from the pilot (section 5).

Constants written in capitals live in `itb/prereg.py`. The code that carries out this plan is `itb/verdict.py` together with `itb/stats.py`, and `itb/analyze.py` draws the REPORT tables from them. Analysis uses the Python standard library only, so anyone can run it without Docker.

## 1. Data

No block below slot 459653000 enters the analysis. Alpenglow consensus runs from the slot after its genesis block 459652999; campaign slots lie in epoch 1069 and later and pass this bound by themselves.

A probe's position is its `transactionIndex` inside its block. Positions count only inside a block, so a burst whose probes landed in several blocks of the target window contributes the pairs inside each block.

The burst table is drawn from a seed before any live burst: `prereg/pilot-table.json` for the pilot. For each class and round it fixes the cell (arm and moment condition) of the burst at each of the class's two leaders. It also fixes the shared fee of equal-fee and denominator bursts, and every probe's payer, fee, compute-unit limit and send rank. Leaders come from the panel that `itb panel` draws by the rule of `itb/panel.py`; a delinquent vote account does not enter the panel.

## 2. Measures

Every tau is Kendall's tau-b, signed so that the rule it looks for reads positive.

- **tau fee**: priority fee against minus position. Higher fee earlier in the block is positive.
- **tau send**: send rank against position. Arrival order kept in the block is positive; reversed arrival order (hypotheses H3 and H4) is negative.
- **tau cross**: tau send over the probe pairs with different fee only (54 pairs in a full burst of the independent and the shared arm). It enters the Holm family.
- **tau ties**: tau send over the pairs with equal fee (12 in a full burst). It is descriptive and gives the subform of the fee rule.
- **tau limit**: requested compute-unit limit against position in the denominator arm, where every probe pays the same fee. Division of the fee by the limit puts the low limit first and reads positive.

tau send splits in the arms with different fee because an exact fee rule that breaks ties in reverse arrival order gives tau send of -0.182 over all 66 pairs, although send order does not touch the 54 cross pairs. That value passes the first Holm threshold of the 96-test family from 18 bursts of a cell, and the fee rule would read as mixed.

A class tau pools the pairs inside bursts and forms no pairs across bursts. The mean of burst taus with equal weight stands next to it as a robustness check. Its 95% interval comes from the jackknife over bursts with the Student t quantile at bursts minus one degrees of freedom.

Strictness of a rule is the share of violated pairs among probe pairs with different predicted position. In the independent and the shared arm the prediction is the client priority `reward * 1 000 000 / (cost + 1)` with cost recomputed by verify, so an unequal cost does not count as a violation. In the equal-fee arm the prediction is send order, and in the denominator arm it is the limit (36 pairs with different limit in a full burst). The share carries the same jackknife interval, and the share of bursts with no violation stands next to it. For pairs without ties tau equals one minus twice the violated share, so both read on one scale.

Values for a single leader rest on 2 bursts per arm and condition (4 with doubled windows). They are descriptive and carry no verdict.

## 3. Tests

**Within-burst permutation test.** Positions and send ranks inside a burst are all distinct, so the burst numerator S of tau equals the number of pairs with different values of the second variable minus twice the number of inversions. The null distribution of inversions is exact: the product of (1 + q + ... + q^(i-1)) over i from 1 to n for distinct values (Mahonian numbers, OEIS A008302), and the q-multinomial coefficient for fee or limit levels. For tau cross the pairs with equal fee drop out, so the null depends on how the fee levels lie across send ranks; dynamic programming over subsets of the burst's probes (2^12 states for 12 probes) gives it exactly, and the code caches it by layout. The tau-b denominator does not change under permutation, so a test on the sum of S over the bursts of a class is a test on the class tau. The sum's distribution is an integer convolution, and p is an exact fraction, identical on any Python version. Tests are two-sided.

**Label permutation across bursts** (class pairs, control path of plan section 5.2). With at most 20 strata the test enumerates all 2^k label assignments over k strata. With more it draws `LABEL_TEST_B` = 19 999 permutations, p = (b + 1)/(B + 1), by its own Fisher-Yates on the `random()` method of `random.Random` seeded with `LABEL_TEST_SEED`. Python documents that method as stable across versions for a given seed. REPORT prints the Monte Carlo error of each such p together with B and the seed.

**Holm families.** Alpha is 0.05 in every family.

- Verdict family, 96 tests: one exact permutation test per verdict slot, class and moment condition, 8 x 2 x 6. The six slots are tau fee and tau cross of the independent arm, the same two of the shared arm, tau send of the equal-fee arm and tau limit of the denominator arm.
- Equivalence family, 96 tests: one TOST per tau of the same slots.
- Class-pair family, 16 tests: 4 pairs x 2 moment conditions x 2 taus (fee and cross), first threshold 0.003125. Its equivalence family has the same 16.
- Stability across epochs has a family of its own.

**Equivalence (TOST).** The equivalence p is the larger of the two one-sided p against -delta and +delta, both from the jackknife with the Student t quantile. `DELTA_CLASS` = 0.2 for classes and `DELTA_PAIR` = 0.2 for pairs. For pairs without ties, delta 0.2 means a violated share shown to lie between 0.4 and 0.6. REPORT also prints the raw 95% intervals.

## 4. Verdicts

The verdict is given per class and moment condition, by arm. For the independent and the shared arm the forms are checked in this order.

1. **Inverted fee sign**: tau fee negative and significant after Holm, so higher fee stands later in the block; tau cross is reported alongside.
2. **Mixed rule**: tau fee positive and significant, and tau cross significant.
3. **Fee rule**: tau fee positive and significant, tau cross not significant. Its subform comes from tau ties at alpha 0.05 outside every Holm family.
4. **Arrival rule**: tau cross significant, tau fee not significant; forward or reverse by the sign of tau cross.
5. **No rule visible**: both tau fee and tau cross pass TOST against zero in the equivalence family.
6. **Undetermined**: none of the five holds, so the test lacks power.

In the equal-fee arm tau send takes the place of tau cross. A significant tau send gives the arrival rule, forward or reverse by its sign. A tau send that passes TOST gives no rule visible, and otherwise the arm is undetermined. In the denominator arm the forms are four. It divides when tau limit is positive and significant, and the sign is inverted when tau limit is significant and negative. It does not divide when tau limit passes TOST in the equivalence family. Otherwise it is undetermined. REPORT puts tau limit next to tau send of the same arm.

## 5. Minimum number of bursts

The pilot fixes the formula; the number itself comes from the pilot and goes on chain with the second memo. The minimum is the smallest number of bursts B per class and cell with

```
(t[B-1; 1 - alpha_e] + t[B-1; (1 + POWER_PER_TAU) / 2]) * sigma / sqrt(B) <= DELTA_CLASS
```

where alpha_e = 0.05/96 is the first Holm threshold of the equivalence family and `POWER_PER_TAU` = 0.9, so a form that needs two taus keeps a joint power near 0.8. sigma is the residual standard deviation of burst tau in the additive class plus cell model over all pilot bursts: the eight pilot bursts of a cell belong to eight different classes, so their raw variance also carries the true differences between classes. REPORT prints the raw variance of each cell next to it. Both are small-sample estimates that the main campaign checks.

## 6. Moment conditions

The arrival estimate of a burst is the send offset from the node's `firstShredReceived` timestamp of the window's first slot plus half the RTT at the final aim. The pre-window condition targets -300 ms (`TIMING_TARGET_MS`). The slot-2 condition targets the start of the second slot, taken as the gap between the node's `firstShredReceived` timestamps of the first and the second slot. Without node timestamps the gap between local receipts stands in. Without both events the probe's final aim is used, and the mean slot duration only after that, because slot steps inside a window are uneven. A burst counts for its condition when the estimate lies in the band `TIMING_BAND_MS` around the target; bursts outside the band form a separate group and stay out of the comparison of the two conditions. The pre-window band runs from 200 ms before its target to 100 ms after it, so it takes arrivals from 500 to 200 ms before the first slot. Its late edge guards the condition. The early edge sits further out because in the mainnet dry-run of the pilot plan on 27.10.2026 every miss of a band 100 ms either side was early, by 118 to 170 ms, and each matched a window start that came later than the slot clock predicted by the same amount. Agave v4.3.2 holds in its buffer every transaction that arrives less than 20 slots before its window (`core/src/banking_stage/decision_maker.rs`), so for Agave such an arrival meets the same condition. The four misses came from the JitoLabs, FireBAM, AgaveBam and Rakurai classes, and a narrower early edge would drop bursts selectively by leader class. The buffering of these clients before their window is not verified in code; that limit applies to the -300 ms target itself, and REPORT states it. The slot-2 band runs 100 ms either side of the start of slot 2. REPORT prints the share of bursts inside the band for each condition.

A burst also stays out of that comparison when `getSlot` at processed commitment ran `CLOCK_LAG_SKIP_SLOTS` = 2 or more slots ahead of the slot clock, since its arrival estimate rests on a lagging clock. Rows of schema version 1 predate this guard; for them the confirmed blockhash, fetched `BLOCKHASH_LEAD_SLOTS` = 6 slots before the window by the clock, must come from a slot before that point.

The conclusion on tie resolution (H3 and H4) is drawn only from pre-window bursts, where all probes reach one scheduling pass. REPORT prints the median one-way latency estimate per class and per leader of each pair next to the pair test, so a reader sees whether a pair difference follows a difference in distance.

## 7. Stability across epochs

A class is stable when the difference of its tau fee in each epoch from the other epochs passes TOST within plus or minus `DELTA_CLASS` in the stability family. It is unstable when tau fee shows significant heterogeneity across the four epochs. When neither holds, stability is undetermined. The epoch tau fee is the equal-weight mean over cells, and the blocked table gives each epoch the same set of cells. Stability across rounds is reported the same way. Quartiles of block load (sum of `costUnits` and transaction count) split tau fee and tau send descriptively, outside the verdict.

## 8. Class pairs

Each of the four pairs in `PAIRS` sets a fork with a builder against the code base it stands on. The differences of tau fee and of tau cross between the two classes are tested by swapping class labels inside each stratum (round and cell), where each class of the pair has exactly one burst. In each moment condition the test sums the differences over both arms with different fee: 8 strata without doubled windows give a smallest p of 0.0078, and 16 strata with doubling give 0.00003. The form "builder changes order" is therefore reachable only with doubling, which is the default. The pair forms are three, each judged on its own line. The builder changes order when the difference is significant after Holm in the 16-test family. The builder does not change order when the difference passes TOST within plus or minus `DELTA_PAIR` in its own 16-test equivalence family. Otherwise the pair is undetermined.

The builder rule counts only slots with a tick from a known signer. The group without a label is reported on its own line, and HarmonicAgave is split by the strategy in its memo descriptively, outside every Holm family. Each run prints the share of tick slots among BAM and Harmonic classes and among the remaining classes; the label holds when no known signer's tick appears in a slot of a class without a builder.

## 9. Descriptive quantities

These stand next to the verdicts and never change them.

- Inclusion share in the target window by fee level, per class and moment condition, next to tau fee: Agave drops transactions at the priority edge when its buffer is full and Firedancer evicts the worst from a full pool, so positions are conditional on fee.
- Control path (plan section 5.2): the difference of tau fee and of the inclusion share between paths within leader and epoch, by permuting path labels across bursts of the same leader. Path latency is the inclusion slot relative to the first slot of the target window. When few RPC-path probes land in the target window, the comparison is descriptive.
- Competition inside the block: each probe's rank among all transactions of its block by client priority, from requested limits, with the rank by `meta.costUnits` as a second column. Transactions that tip a Jito tip account are flagged and left out of the rank.
- Bursts that landed in the window's first slot against the rest, as a secondary stratum of tau fee.

## 10. Pilot rounds test

The rounds test uses only equal-fee bursts in the slot-2 condition; in the pre-window condition every probe waits in the queue before the first pass. In each such burst tau is computed between send moment and the number of the segment between ticks. The hypothesis predicts a positive pooled class tau under the exact within-burst test of section 3. A single burst with negative tau does not refute it, because clock and network noise give such bursts under true rounds too; REPORT prints their share. The refutation is this: among probe pairs of one burst that fell into different segments, the later-sent probe stands more often in the earlier segment.
