# Report

This report holds the pilot of 2026-10-27 in full and the frame of the campaign, which measures the same panel on mainnet over four epochs from epoch 1071. Until the campaign data is collected, its tables read "No runs of this stage yet."

Every table sits between a pair of `<!-- itb:begin NAME -->` and `<!-- itb:end NAME -->` lines and is written by `python -m itb report` from `data/` and `logs/` alone. `python -m itb report --check` fails when any table differs from what the raw data gives, and `docker compose run --rm reproduce` runs that check after verify and analyze. `python -m itb claim NAME` prints one table on its own. Every probe behind these tables has its signature and slot in `data/runs/<run>/probes.jsonl` and `collect.jsonl`, so any row can be checked against `getBlock`.

## 1. The answer

The verdict for each class and moment condition comes from the campaign (section 6). Each class and cell gets one of the six forms of the [analysis plan](prereg/ANALYSIS-PLAN.md), and the share of violated pairs gives its strictness. The pilot reads no verdict by design: most of its cells hold one burst, and the analysis plan uses it to measure inclusion and the spread of tau between bursts (section 5).

## 2. Validators and clients

<!-- itb:begin panel -->
| Leader identity | Class at selection | gossip clientId and version at the bursts | validators.app label | Stages | Bursts | Probes in window |
|---|---|---|---|---|---|---|
| `5Cchr1XGEg7dbBXByV5NY2ad8jfxAM7HA3x8D56rq9Ux` | AgaveBam | AgaveBam 4.3.2 | not taken | pilot | 4 | 48 |
| `DRpbCBMxVnDK7maPM5tGv6MvB3v1sRMC86PZ8okm21hy` | AgaveBam | AgaveBam 4.3.2 | not taken | pilot | 5 | 60 |
| `E1r4Psq84tHfQ6aPTvvDka4U3u8zPVD7gEUrH25RdxHL` | JitoLabs | JitoLabs 4.3.2 | not taken | pilot | 4 | 48 |
| `HEL1USMZKAL2odpNBj2oCjffnFGaYwmbGmyewGv1e2TU` | JitoLabs | JitoLabs 4.3.2 | not taken | pilot | 4 | 48 |
| `CAo1dCGYrB6NhHh5xb1cGjUiu86iyCfMTENxgHumSve4` | HarmonicAgave | HarmonicAgave 4.3.2 | not taken | pilot | 5 | 60 |
| `Fd7btgySsrjuo25CJCj7oE7VPMyezDhnx7pZkj2v69Nk` | HarmonicAgave | HarmonicAgave 4.3.2 | not taken | pilot | 4 | 48 |
| `Awes4Tr6TX8JDzEhCZY2QVNimT6iD1zWHzf1vNyGvpLM` | HarmonicFiredancer | HarmonicFiredancer 26.10.4 | not taken | pilot | 5 | 60 |
| `JUPiTERrZqgf1jUyR7dSkhMx4Kn2qJyekWsg3LT1h4b` | HarmonicFiredancer | HarmonicFiredancer 26.10.4 | not taken | pilot | 4 | 36 |
| `BFmqBsaGjeYA7gHpReKmnVkRyhqiMmHoR9ttv1crWmzy` | Firedancer | Firedancer 26.10.4 | not taken | pilot | 4 | 48 |
| `DNVZMSqeRH18Xa4MCTrb1MndNf3Npg4MEwqswo23eWkf` | Firedancer | Firedancer 26.10.4 | not taken | pilot | 4 | 48 |
| `9jxgosAfHgHzwnxsHw4RAZYaLVokMbnYtmiZBreynGFP` | FireBAM | FireBAM 26.10.4 | not taken | pilot | 5 | 60 |
| `SSmBEooM7RkmyuXxuKgAhTvhQZ36Z3G2WsmLGJKoQLY` | FireBAM | FireBAM 26.10.4 | not taken | pilot | 4 | 43 |
| `E3mDbFMr8yZcCAZx5wPUFCRmLX31u8Nnj4jPoPc54h3F` | Rakurai | Rakurai 4.3.2 | not taken | pilot | 4 | 48 |
| `ana2y2YvQ3ZPMwm6qhnN3nJoUSiT3qx5Pvetkq9xcfY` | Rakurai | Rakurai 4.3.2 | not taken | pilot | 4 | 48 |
| `5Us18hLZPXJTS4QVuGSsUw137Dyd2tgBaem24Xsf5nBS` | Agave | Agave 4.3.2 | not taken | pilot | 4 | 48 |
| `7QQGNm3ptwinipDCyaCF7jY5katgmFUu1ieP2f7nwLpE` | Agave | Agave 4.3.2 | not taken | pilot | 4 | 48 |

16 validators, 8 classes by gossip clientId.
<!-- itb:end panel -->

The bounty asks for at least 6 validators on at least 3 client or fork versions. The panel holds 16 validators in 8 classes by gossip `clientId`, two leaders per class, on two code bases. Agave 4.3.2 runs under the classes Agave, JitoLabs, AgaveBam, HarmonicAgave and Rakurai. Firedancer 26.10.4 runs under Firedancer and its two builder forks, FireBAM and HarmonicFiredancer. The label and the version come from `getClusterNodes` at the moment of each burst, and every pilot leader showed its selection class at every burst (section 5.6). The second label from validators.app is missing for the pilot, because the request failed on the measuring machine (section 9).

## 3. Measurements and their dates

<!-- itb:begin runs -->
| Run | Stage | Network | Mode | Started (UTC) | Bursts | Probes | Delivered | Included | In target window | Commit |
|---|---|---|---|---|---|---|---|---|---|---|
| `devnet-devnet-20261027T083150Z` | devnet | devnet | live | 2026-10-27 08:32:32 | 4 | 48 | 48 | 48 | 48 | `8ff9207` |
| `dry-run-devnet-20261026T231756Z` | dry-run | devnet | dry-run | 2026-10-26 23:18:33 | 4 | 48 | 0 | - | - | `0e87340` |
| `dry-run-devnet-20261027T082858Z` | dry-run | devnet | dry-run | 2026-10-27 08:29:35 | 4 | 48 | 0 | - | - | `8ff9207` |
| `dry-run-mainnet-20261026T232506Z` | dry-run | mainnet | dry-run | 2026-10-26 23:25:45 | 4 | 48 | 0 | - | - | `7aaee67` |
| `dry-run-mainnet-20261027T002723Z` | dry-run | mainnet | dry-run | 2026-10-27 00:28:04 | 4 | 48 | 0 | - | - | `2bacfa2` |
| `dry-run-mainnet-20261027T003443Z` | dry-run | mainnet | dry-run | 2026-10-27 00:35:15 | 4 | 48 | 0 | - | - | `d8699aa` |
| `dry-run-mainnet-20261027T010659Z` | dry-run | mainnet | dry-run | 2026-10-27 01:07:38 | 17 | 204 | 0 | - | - | `d4f2cca` |
| `dry-run-mainnet-20261027T130541Z` | dry-run | mainnet | dry-run | 2026-10-27 13:06:16 | 12 | 144 | 0 | - | - | `5ffb53a` |
| `dry-run-mainnet-20261027T233040Z` | dry-run | mainnet | dry-run | 2026-10-27 23:31:14 | 0 | 0 | 0 | - | - | `e3b21e3` |
| `pilot-mainnet-20261027T085253Z` | pilot | mainnet | live | 2026-10-27 08:53:32 | 68 | 816 | 811 | 811 | 799 | `ef77ca3` |
<!-- itb:end runs -->

Every mainnet run is dated after the Alpenglow upgrade of 2026-10-21, so no measurement mixes the two sides of it. The devnet runs test the pipeline and feed no result. The dry-run `dry-run-mainnet-20261027T233040Z` checks the campaign plan of epoch 1071 and stopped after 150 s, about 27 hours before the plan's first round, so it holds the cost check and the slot clock and no burst. Appendix A dates every burst by the `blockTime` of its first included probe.

## 4. Spend

<!-- itb:begin spend -->
| Item | UTC | What | Probe fees (lamports) | Funding and closing fees | Paid | Spend journal growth | Limit of the run (lamports) |
|---|---|---|---|---|---|---|---|
| anchor of pilot | 2026-10-27 08:52:11 | `3jmFZBgsQoXTnKVS`... | - | - | 5000 | - | - |
| `pilot-mainnet-20261027T085253Z` | 2026-10-27 08:53:32 | 811 probes included, 13 funding and closing transactions | 4280230 | 65000 | 4345230 | 4345230 | 4376440 |
| **total** |  |  |  |  | **4350230** (0.004350 SOL) |  | code cap 0.05 SOL |
<!-- itb:end spend -->

Probe fees are `meta.fee` of each included probe. Each transaction that funds or closes the payers carries one signature and pays the 5000-lamport base fee; the run's log names each of them under `fund_send` or `close_send`. The sender keeps a spend journal in a Docker volume and reconciles it with the chain at start. Its growth over the run, read from the log, equals what the table adds up. The limit of each run covers the worst case of every fee in its plan, and the compiled cap of 0.05 SOL stands above any limit.

## 5. Pilot, 2026-10-27, epoch 1069

The pilot sent 68 bursts into the windows of the 16 panel leaders between 08:53 and 10:56 UTC on 2026-10-27, after its analysis plan went on chain at 08:52 UTC. Most cells of a class hold one burst, where a cell is one arm under one moment condition, so a form below is what a single burst gives. The pilot measures inclusion and the spread of tau between bursts, which set the minimum for the campaign (section 5.15). It also tests whether the segments between ticks are rounds in time (section 5.4).

### 5.1 Bursts left out of the order tests

<!-- itb:begin pilot-exclusions -->
68 bursts, 61 kept for the order tests. Reasons a burst stays out: fewer-than-two-in-a-block 1, outside-timing-band 6.
<!-- itb:end pilot-exclusions -->

### 5.2 Order by class and cell

<!-- itb:begin pilot-cells -->
| Class | Arm | Timing | Bursts | Form | Detail | tau (95% CI; p) | Violated pair share (95% CI) |
|---|---|---|---|---|---|---|---|
| Agave | denominator | pre300 | 1 | undetermined | - | limit 0.082 (no interval; p 0.818); send 0.152 (no interval; p 0.545) | 0.444 (no interval); 0 of 1 bursts without a violation |
| Agave | denominator | slot2 | 1 | undetermined | - | limit 0.041 (no interval; p 0.937); send -0.030 (no interval; p 0.947) | 0.472 (no interval); 0 of 1 bursts without a violation |
| Agave | equal_fee | pre300 | 1 | undetermined | - | send -0.182 (no interval; p 0.459) | 0.591 (no interval); 0 of 1 bursts without a violation |
| Agave | independent | pre300 | 1 | undetermined | - | cross 0.000 (no interval; p 1); fee 0.704 (no interval; p 0.00186); ties 0.000 (no interval; p 1) | 0.111 (no interval); 0 of 1 bursts without a violation |
| Agave | shared | pre300 | 1 | fee-rule | ties-unordered | cross -0.333 (no interval; p 0.233); fee 0.905 (no interval; p 5.41e-06); ties -0.333 (no interval; p 0.44) | 0.000 (no interval); 1 of 1 bursts without a violation |
| Agave | shared | slot2 | 1 | arrival-rule | forward | cross 0.815 (no interval; p 0.000141); fee 0.369 (no interval; p 0.138); ties 0.833 (no interval; p 0.0139) | 0.296 (no interval); 0 of 1 bursts without a violation |
| AgaveBam | denominator | pre300 | 1 | undetermined | - | limit 0.739 (no interval; p 0.00216); send -0.091 (no interval; p 0.737) | 0.000 (no interval); 1 of 1 bursts without a violation |
| AgaveBam | denominator | slot2 | 1 | undetermined | - | limit 0.739 (no interval; p 0.00216); send -0.364 (no interval; p 0.116) | 0.000 (no interval); 1 of 1 bursts without a violation |
| AgaveBam | equal_fee | slot2 | 2 | arrival-rule | forward | send 0.712 (0.520 to 0.905; p 9.02e-07) | 0.144 (0.048 to 0.240); 0 of 2 bursts without a violation |
| AgaveBam | independent | pre300 | 1 | fee-rule | ties-unordered | cross -0.037 (no interval; p 0.945); fee 0.905 (no interval; p 5.41e-06); ties -0.167 (no interval; p 0.798) | 0.000 (no interval); 1 of 1 bursts without a violation |
| AgaveBam | independent | slot2 | 1 | fee-rule | ties-unordered | cross 0.333 (no interval; p 0.233); fee 0.905 (no interval; p 5.41e-06); ties -0.333 (no interval; p 0.44) | 0.000 (no interval); 1 of 1 bursts without a violation |
| AgaveBam | shared | pre300 | 1 | fee-rule | ties-unordered | cross 0.074 (no interval; p 0.835); fee 0.905 (no interval; p 5.41e-06); ties -0.500 (no interval; p 0.193) | 0.000 (no interval); 1 of 1 bursts without a violation |
| FireBAM | denominator | pre300 | 1 | undetermined | - | limit 0.739 (no interval; p 0.00216); send 0.152 (no interval; p 0.545) | 0.000 (no interval); 1 of 1 bursts without a violation |
| FireBAM | denominator | slot2 | 1 | undetermined | - | limit 0.739 (no interval; p 0.00216); send 0.121 (no interval; p 0.638) | 0.000 (no interval); 1 of 1 bursts without a violation |
| FireBAM | equal_fee | pre300 | 1 | undetermined | - | send 0.485 (no interval; p 0.0311) | 0.258 (no interval); 0 of 1 bursts without a violation |
| FireBAM | equal_fee | slot2 | 2 | undetermined | - | send -0.045 (-1.778 to 1.687; p 0.81) | 0.523 (-0.344 to 1.389); 0 of 2 bursts without a violation |
| FireBAM | independent | pre300 | 1 | fee-rule | ties-unordered | cross -0.037 (no interval; p 0.945); fee 0.905 (no interval; p 5.41e-06); ties 0.500 (no interval; p 0.193) | 0.000 (no interval); 1 of 1 bursts without a violation |
| FireBAM | shared | pre300 | 1 | fee-rule | ties-reverse-arrival | cross -0.407 (no interval; p 0.138); fee 0.905 (no interval; p 5.41e-06); ties -0.833 (no interval; p 0.0139) | 0.000 (no interval); 1 of 1 bursts without a violation |
| FireBAM | shared | slot2 | 1 | undetermined | - | cross -0.444 (no interval; p 0.289); fee 0.926 (no interval; p 0.00317); ties 0.333 (no interval; p 1) | 0.000 (no interval); 1 of 1 bursts without a violation |
| Firedancer | denominator | pre300 | 1 | undetermined | - | limit 0.739 (no interval; p 0.00216); send -0.394 (no interval; p 0.0863) | 0.000 (no interval); 1 of 1 bursts without a violation |
| Firedancer | denominator | slot2 | 1 | undetermined | - | limit 0.000 (no interval; p 1); send 0.848 (no interval; p 1.63e-05) | 0.500 (no interval); 0 of 1 bursts without a violation |
| Firedancer | equal_fee | pre300 | 1 | arrival-rule | reverse | send -1.000 (no interval; p 4.18e-09) | 1.000 (no interval); 0 of 1 bursts without a violation |
| Firedancer | equal_fee | slot2 | 1 | arrival-rule | forward | send 1.000 (no interval; p 4.18e-09) | 0.000 (no interval); 1 of 1 bursts without a violation |
| Firedancer | independent | pre300 | 1 | fee-rule | ties-reverse-arrival | cross 0.074 (no interval; p 0.835); fee 0.905 (no interval; p 5.41e-06); ties -1.000 (no interval; p 0.00154) | 0.000 (no interval); 1 of 1 bursts without a violation |
| Firedancer | independent | slot2 | 1 | arrival-rule | forward | cross 0.852 (no interval; p 3.99e-05); fee -0.168 (no interval; p 0.532); ties 1.000 (no interval; p 0.00154) | 0.593 (no interval); 0 of 1 bursts without a violation |
| Firedancer | shared | pre300 | 1 | fee-rule | ties-unordered | cross 0.074 (no interval; p 0.835); fee 0.905 (no interval; p 5.41e-06); ties -0.667 (no interval; p 0.0633) | 0.000 (no interval); 1 of 1 bursts without a violation |
| Firedancer | shared | slot2 | 1 | undetermined | - | cross 0.630 (no interval; p 0.0053); fee -0.268 (no interval; p 0.294); ties 0.667 (no interval; p 0.0633) | 0.648 (no interval); 0 of 1 bursts without a violation |
| HarmonicAgave | denominator | pre300 | 1 | undetermined | - | limit 0.451 (no interval; p 0.0931); send 0.212 (no interval; p 0.381) | 0.194 (no interval); 0 of 1 bursts without a violation |
| HarmonicAgave | denominator | slot2 | 1 | undetermined | - | limit 0.164 (no interval; p 0.589); send 0.545 (no interval; p 0.0138) | 0.389 (no interval); 0 of 1 bursts without a violation |
| HarmonicAgave | equal_fee | pre300 | 1 | undetermined | - | send -0.121 (no interval; p 0.638) | 0.561 (no interval); 0 of 1 bursts without a violation |
| HarmonicAgave | equal_fee | slot2 | 2 | undetermined | - | send 0.364 (-0.791 to 1.519; p 0.0214) | 0.318 (-0.259 to 0.896); 0 of 2 bursts without a violation |
| HarmonicAgave | independent | pre300 | 1 | undetermined | - | cross 0.222 (no interval; p 0.404); fee 0.469 (no interval; p 0.0531); ties 0.500 (no interval; p 0.193) | 0.241 (no interval); 0 of 1 bursts without a violation |
| HarmonicAgave | independent | slot2 | 1 | undetermined | - | cross -0.185 (no interval; p 0.462); fee 0.034 (no interval; p 0.945); ties -0.500 (no interval; p 0.193) | 0.481 (no interval); 0 of 1 bursts without a violation |
| HarmonicAgave | shared | pre300 | 1 | fee-rule | ties-unordered | cross 0.111 (no interval; p 0.724); fee 0.804 (no interval; p 0.000189); ties 0.333 (no interval; p 0.44) | 0.056 (no interval); 0 of 1 bursts without a violation |
| HarmonicAgave | shared | slot2 | 1 | undetermined | - | cross -0.074 (no interval; p 0.832); fee 0.670 (no interval; p 0.00342); ties 0.667 (no interval; p 0.0633) | 0.130 (no interval); 0 of 1 bursts without a violation |
| HarmonicFiredancer | denominator | slot2 | 1 | undetermined | - | limit 0.369 (no interval; p 0.18); send -0.030 (no interval; p 0.947) | 0.250 (no interval); 0 of 1 bursts without a violation |
| HarmonicFiredancer | equal_fee | pre300 | 1 | undetermined | - | send 0.576 (no interval; p 0.00876) | 0.212 (no interval); 0 of 1 bursts without a violation |
| HarmonicFiredancer | equal_fee | slot2 | 2 | undetermined | - | send 0.515 (-0.255 to 1.285; p 0.000786) | 0.242 (-0.143 to 0.627); 0 of 2 bursts without a violation |
| HarmonicFiredancer | independent | pre300 | 1 | fee-rule | ties-unordered | cross -0.185 (no interval; p 0.521); fee 0.804 (no interval; p 0.000189); ties 0.333 (no interval; p 0.44) | 0.056 (no interval); 0 of 1 bursts without a violation |
| HarmonicFiredancer | shared | pre300 | 1 | undetermined | - | cross 0.148 (no interval; p 0.621); fee 0.670 (no interval; p 0.00342); ties 0.167 (no interval; p 0.798) | 0.130 (no interval); 0 of 1 bursts without a violation |
| HarmonicFiredancer | shared | slot2 | 1 | fee-rule | ties-unordered | cross -0.481 (no interval; p 0.0686); fee 0.838 (no interval; p 7.03e-05); ties -0.167 (no interval; p 0.798) | 0.037 (no interval); 0 of 1 bursts without a violation |
| JitoLabs | denominator | pre300 | 1 | undetermined | - | limit 0.739 (no interval; p 0.00216); send -0.061 (no interval; p 0.841) | 0.000 (no interval); 1 of 1 bursts without a violation |
| JitoLabs | denominator | slot2 | 1 | undetermined | - | limit 0.287 (no interval; p 0.31); send 0.121 (no interval; p 0.638) | 0.306 (no interval); 0 of 1 bursts without a violation |
| JitoLabs | equal_fee | pre300 | 1 | undetermined | - | send -0.455 (no interval; p 0.0447) | 0.727 (no interval); 0 of 1 bursts without a violation |
| JitoLabs | equal_fee | slot2 | 1 | arrival-rule | forward | send 1.000 (no interval; p 4.18e-09) | 0.000 (no interval); 1 of 1 bursts without a violation |
| JitoLabs | independent | pre300 | 1 | undetermined | - | cross 0.037 (no interval; p 0.933); fee 0.302 (no interval; p 0.233); ties -0.167 (no interval; p 0.798) | 0.333 (no interval); 0 of 1 bursts without a violation |
| JitoLabs | independent | slot2 | 1 | undetermined | - | cross -0.222 (no interval; p 0.389); fee 0.235 (no interval; p 0.365); ties 0.500 (no interval; p 0.193) | 0.370 (no interval); 0 of 1 bursts without a violation |
| JitoLabs | shared | pre300 | 1 | fee-rule | ties-unordered | cross -0.519 (no interval; p 0.0531); fee 0.905 (no interval; p 5.41e-06); ties -0.333 (no interval; p 0.44) | 0.000 (no interval); 1 of 1 bursts without a violation |
| JitoLabs | shared | slot2 | 1 | fee-rule | ties-unordered | cross 0.481 (no interval; p 0.0749); fee 0.905 (no interval; p 5.41e-06); ties -0.333 (no interval; p 0.44) | 0.000 (no interval); 1 of 1 bursts without a violation |
| Rakurai | denominator | pre300 | 1 | undetermined | - | limit 0.739 (no interval; p 0.00216); send -0.182 (no interval; p 0.459) | 0.000 (no interval); 1 of 1 bursts without a violation |
| Rakurai | denominator | slot2 | 1 | undetermined | - | limit 0.410 (no interval; p 0.132); send 0.667 (no interval; p 0.0018) | 0.222 (no interval); 0 of 1 bursts without a violation |
| Rakurai | equal_fee | pre300 | 1 | undetermined | - | send 0.273 (no interval; p 0.25) | 0.364 (no interval); 0 of 1 bursts without a violation |
| Rakurai | equal_fee | slot2 | 1 | arrival-rule | forward | send 0.949 (no interval; p 1.01e-05) | 0.026 (no interval); 0 of 1 bursts without a violation |
| Rakurai | independent | pre300 | 1 | fee-rule | ties-unordered | cross -0.037 (no interval; p 0.943); fee 0.771 (no interval; p 0.000444); ties -0.333 (no interval; p 0.44) | 0.074 (no interval); 0 of 1 bursts without a violation |
| Rakurai | independent | slot2 | 1 | undetermined | - | cross 0.593 (no interval; p 0.00548); fee -0.067 (no interval; p 0.835); ties 0.667 (no interval; p 0.0633) | 0.537 (no interval); 0 of 1 bursts without a violation |
| Rakurai | shared | pre300 | 1 | fee-rule | ties-unordered | cross 0.111 (no interval; p 0.729); fee 0.905 (no interval; p 5.41e-06); ties 0.167 (no interval; p 0.798) | 0.000 (no interval); 1 of 1 bursts without a violation |
| Rakurai | shared | slot2 | 1 | undetermined | - | cross 0.704 (no interval; p 0.00177); fee 0.034 (no interval; p 0.945); ties 0.167 (no interval; p 0.798) | 0.481 (no interval); 0 of 1 bursts without a violation |
<!-- itb:end pilot-cells -->

Tau is Kendall tau-b against block position, pooled over the bursts of the cell, with a jackknife interval over bursts. A cell with one burst has no interval. With two bursts the interval uses one degree of freedom and may run past the range of tau. The violated pair share counts pairs with a different predicted position that landed in the other order.

Before the window, 9 of the 16 different-fee cells had no pair of different fee out of fee order. At the start of slot 2, 3 of 12 had none. The only pre-window equal-fee burst of Firedancer landed in exact reverse send order (tau send -1.000), the order its code predicts (README, hypothesis H3). One burst per cell gives no verdict on either observation.

### 5.3 Builder against its base

<!-- itb:begin pilot-pairs -->
| Pair | Timing | Statistic | Strata | Mean difference | p | TOST p | Form |
|---|---|---|---|---|---|---|---|
| AgaveBam vs JitoLabs | pre300 | fee | 2 | 0.302 | 1 | 0.603 | undetermined |
| AgaveBam vs JitoLabs | pre300 | cross | 2 | 0.259 | 1 | 0.556 | undetermined |
| AgaveBam vs JitoLabs | slot2 | fee | 1 | 0.670 | 1 | 1 | undetermined |
| AgaveBam vs JitoLabs | slot2 | cross | 1 | 0.556 | 1 | 1 | undetermined |
| FireBAM vs Firedancer | pre300 | fee | 2 | 0.000 | 1 | 0 | builder-does-not-change-order |
| FireBAM vs Firedancer | pre300 | cross | 2 | -0.296 | 0.5 | 0.653 | undetermined |
| FireBAM vs Firedancer | slot2 | fee | 1 | 1.194 | 1 | 1 | undetermined |
| FireBAM vs Firedancer | slot2 | cross | 1 | -1.074 | 1 | 1 | undetermined |
| HarmonicAgave vs Agave | pre300 | fee | 2 | -0.168 | 0.5 | 0.356 | undetermined |
| HarmonicAgave vs Agave | pre300 | cross | 2 | 0.333 | 0.5 | 0.779 | undetermined |
| HarmonicAgave vs Agave | slot2 | fee | 1 | 0.302 | 1 | 1 | undetermined |
| HarmonicAgave vs Agave | slot2 | cross | 1 | -0.889 | 1 | 1 | undetermined |
| HarmonicFiredancer vs Firedancer | pre300 | fee | 2 | -0.168 | 0.5 | 0.356 | undetermined |
| HarmonicFiredancer vs Firedancer | pre300 | cross | 2 | -0.093 | 1 | 0.318 | undetermined |
| HarmonicFiredancer vs Firedancer | slot2 | fee | 1 | 1.106 | 1 | 1 | undetermined |
| HarmonicFiredancer vs Firedancer | slot2 | cross | 1 | -1.111 | 1 | 1 | undetermined |
<!-- itb:end pilot-pairs -->

A stratum is one round and arm with a burst of both classes. FireBAM against Firedancer before the window reads "builder-does-not-change-order" on tau fee. Both classes gave tau fee 0.905 in both strata, every pair of different fee in fee order, so the difference is zero with zero spread, and the TOST of the analysis plan returns p 0 when the standard error is zero. Two identical strata carry little weight; the campaign verdict for this pair stands on its own strata.

### 5.4 Segments between ticks

<!-- itb:begin pilot-rounds -->
Arm equal_fee, timing slot2: 11 bursts, 6 with probes in two segments or more, share of bursts with a negative S 0.00. Pooled: tau 0.743, p 4.9e-19. Form: **supported**.

| Class | Bursts | tau send rank against segment | p |
|---|---|---|---|
| AgaveBam | 2 | 0.795 | 7.29e-08 |
| HarmonicAgave | 2 | 0.739 | 2.34e-06 |
| HarmonicFiredancer | 2 | 0.687 | 1.15e-05 |
<!-- itb:end pilot-rounds -->

The analysis plan (section 10) asks whether the segments between ticks in a builder slot are rounds in time. In equal-fee bursts sent at the start of slot 2, a probe sent later should then never stand in an earlier segment. Six of 11 such bursts put probes into two segments or more, and none gave a negative S. The pooled tau of send rank against segment is 0.743. The form is supported: in builder slots a probe's segment follows its send order.

### 5.5 Inclusion

<!-- itb:begin pilot-inclusion -->
| Class | Timing | Path | Priority fee (lamports) | Delivered | In target window | Share |
|---|---|---|---|---|---|---|
| Agave | pre300 | quic | 0 | 6 | 6 | 1.00 |
| Agave | pre300 | quic | 10 | 18 | 18 | 1.00 |
| Agave | pre300 | quic | 100 | 18 | 18 | 1.00 |
| Agave | pre300 | quic | 1000 | 6 | 6 | 1.00 |
| Agave | slot2 | quic | 0 | 6 | 6 | 1.00 |
| Agave | slot2 | quic | 10 | 18 | 18 | 1.00 |
| Agave | slot2 | quic | 100 | 18 | 18 | 1.00 |
| Agave | slot2 | quic | 1000 | 6 | 6 | 1.00 |
| AgaveBam | pre300 | quic | 0 | 18 | 18 | 1.00 |
| AgaveBam | pre300 | quic | 10 | 6 | 6 | 1.00 |
| AgaveBam | pre300 | quic | 100 | 18 | 18 | 1.00 |
| AgaveBam | pre300 | quic | 1000 | 6 | 6 | 1.00 |
| AgaveBam | slot2 | quic | 0 | 18 | 18 | 1.00 |
| AgaveBam | slot2 | quic | 10 | 6 | 6 | 1.00 |
| AgaveBam | slot2 | quic | 100 | 6 | 6 | 1.00 |
| AgaveBam | slot2 | quic | 1000 | 30 | 30 | 1.00 |
| FireBAM | pre300 | quic | 0 | 30 | 30 | 1.00 |
| FireBAM | pre300 | quic | 10 | 6 | 6 | 1.00 |
| FireBAM | pre300 | quic | 100 | 6 | 6 | 1.00 |
| FireBAM | pre300 | quic | 1000 | 6 | 6 | 1.00 |
| FireBAM | slot2 | quic | 0 | 5 | 5 | 1.00 |
| FireBAM | slot2 | quic | 10 | 29 | 29 | 1.00 |
| FireBAM | slot2 | quic | 100 | 4 | 4 | 1.00 |
| FireBAM | slot2 | quic | 1000 | 17 | 17 | 1.00 |
| Firedancer | pre300 | quic | 0 | 6 | 6 | 1.00 |
| Firedancer | pre300 | quic | 10 | 18 | 18 | 1.00 |
| Firedancer | pre300 | quic | 100 | 6 | 6 | 1.00 |
| Firedancer | pre300 | quic | 1000 | 18 | 18 | 1.00 |
| Firedancer | slot2 | quic | 0 | 6 | 6 | 1.00 |
| Firedancer | slot2 | quic | 10 | 18 | 18 | 1.00 |
| Firedancer | slot2 | quic | 100 | 6 | 6 | 1.00 |
| Firedancer | slot2 | quic | 1000 | 18 | 18 | 1.00 |
| HarmonicAgave | pre300 | quic | 0 | 6 | 6 | 1.00 |
| HarmonicAgave | pre300 | quic | 10 | 6 | 6 | 1.00 |
| HarmonicAgave | pre300 | quic | 100 | 6 | 6 | 1.00 |
| HarmonicAgave | pre300 | quic | 1000 | 30 | 30 | 1.00 |
| HarmonicAgave | slot2 | quic | 0 | 18 | 18 | 1.00 |
| HarmonicAgave | slot2 | quic | 10 | 6 | 6 | 1.00 |
| HarmonicAgave | slot2 | quic | 100 | 30 | 30 | 1.00 |
| HarmonicAgave | slot2 | quic | 1000 | 6 | 6 | 1.00 |
| HarmonicFiredancer | pre300 | quic | 0 | 6 | 6 | 1.00 |
| HarmonicFiredancer | pre300 | quic | 10 | 18 | 18 | 1.00 |
| HarmonicFiredancer | pre300 | quic | 100 | 18 | 6 | 0.33 |
| HarmonicFiredancer | pre300 | quic | 1000 | 6 | 6 | 1.00 |
| HarmonicFiredancer | slot2 | quic | 0 | 18 | 18 | 1.00 |
| HarmonicFiredancer | slot2 | quic | 10 | 6 | 6 | 1.00 |
| HarmonicFiredancer | slot2 | quic | 100 | 18 | 18 | 1.00 |
| HarmonicFiredancer | slot2 | quic | 1000 | 18 | 18 | 1.00 |
| JitoLabs | pre300 | quic | 0 | 18 | 18 | 1.00 |
| JitoLabs | pre300 | quic | 10 | 6 | 6 | 1.00 |
| JitoLabs | pre300 | quic | 100 | 18 | 18 | 1.00 |
| JitoLabs | pre300 | quic | 1000 | 6 | 6 | 1.00 |
| JitoLabs | slot2 | quic | 0 | 18 | 18 | 1.00 |
| JitoLabs | slot2 | quic | 10 | 6 | 6 | 1.00 |
| JitoLabs | slot2 | quic | 100 | 18 | 18 | 1.00 |
| JitoLabs | slot2 | quic | 1000 | 6 | 6 | 1.00 |
| Rakurai | pre300 | quic | 0 | 6 | 6 | 1.00 |
| Rakurai | pre300 | quic | 10 | 18 | 18 | 1.00 |
| Rakurai | pre300 | quic | 100 | 6 | 6 | 1.00 |
| Rakurai | pre300 | quic | 1000 | 18 | 18 | 1.00 |
| Rakurai | slot2 | quic | 0 | 18 | 18 | 1.00 |
| Rakurai | slot2 | quic | 10 | 18 | 18 | 1.00 |
| Rakurai | slot2 | quic | 100 | 6 | 6 | 1.00 |
| Rakurai | slot2 | quic | 1000 | 6 | 6 | 1.00 |
<!-- itb:end pilot-inclusion -->

Of 816 probes, 811 were delivered and 799 landed in their target window. Five probes of burst 99 (FireBAM, `SSmBEooM...`, shared arm, slot 2) failed with a closed connection. All 12 probes of burst 52 (HarmonicFiredancer, `JUPiTERr...`, denominator arm, before the window) landed one slot before the window, in the block of another HarmonicFiredancer leader, `nymsGg7Z...`.

### 5.6 Moment condition and client labels

<!-- itb:begin pilot-timing -->
| Condition | Bursts | In the band | Share | Median arrival estimate from the target (ms) | Range (ms) | Slot clock behind |
|---|---|---|---|---|---|---|
| pre300 | 32 | 31 | 0.97 | 3 | -175 to 227 | 0 |
| slot2 | 36 | 31 | 0.86 | -2 | -180 to 304 | 0 |

| Class | In the band, pre300 | In the band, slot2 |
|---|---|---|
| AgaveBam | 3 of 4 | 4 of 5 |
| JitoLabs | 4 of 4 | 4 of 4 |
| HarmonicAgave | 4 of 4 | 5 of 5 |
| HarmonicFiredancer | 4 of 4 | 4 of 5 |
| Firedancer | 4 of 4 | 4 of 4 |
| FireBAM | 4 of 4 | 4 of 5 |
| Rakurai | 4 of 4 | 4 of 4 |
| Agave | 4 of 4 | 2 of 4 |
<!-- itb:end pilot-timing -->

The arrival estimate is the send offset from the first-shred moment of the first slot plus half the round-trip time of the same connection (README, the path from the sender). The pre-window band takes arrivals 500 to 200 ms before the first slot, and the slot-2 band 100 ms either side of the start of slot 2.

<!-- itb:begin pilot-labels -->
| Class at selection | Bursts | Leader showed another clientId | Share | clientId shown |
|---|---|---|---|---|
| AgaveBam | 9 | 0 | 0.00 | - |
| JitoLabs | 8 | 0 | 0.00 | - |
| HarmonicAgave | 9 | 0 | 0.00 | - |
| HarmonicFiredancer | 9 | 0 | 0.00 | - |
| Firedancer | 8 | 0 | 0.00 | - |
| FireBAM | 9 | 0 | 0.00 | - |
| Rakurai | 8 | 0 | 0.00 | - |
| Agave | 8 | 0 | 0.00 | - |
<!-- itb:end pilot-labels -->

### 5.7 Probes outside their window

<!-- itb:begin pilot-elsewhere -->
| Path | Timing | Delivered | In target window | Same leader, outside the window | Another leader's block | Not included | Class of the other leaders |
|---|---|---|---|---|---|---|---|
| quic | pre300 | 384 | 372 | 0 | 12 | 0 | HarmonicFiredancer 12 |
| quic | slot2 | 427 | 427 | 0 | 0 | 0 | - |

| Class of the target | Delivered | In target window | Same leader, outside the window | Another leader's block | Not included |
|---|---|---|---|---|---|
| AgaveBam | 108 | 108 | 0 | 0 | 0 |
| JitoLabs | 96 | 96 | 0 | 0 | 0 |
| HarmonicAgave | 108 | 108 | 0 | 0 | 0 |
| HarmonicFiredancer | 108 | 96 | 0 | 12 | 0 |
| Firedancer | 96 | 96 | 0 | 0 | 0 |
| FireBAM | 103 | 103 | 0 | 0 | 0 |
| Rakurai | 96 | 96 | 0 | 0 | 0 |
| Agave | 96 | 96 | 0 | 0 | 0 |
<!-- itb:end pilot-elsewhere -->

### 5.8 Path latency

<!-- itb:begin pilot-latency -->
| Class | Leader | Bursts | Median one-way estimate (ms) | Class median (ms) |
|---|---|---|---|---|
| AgaveBam | `5Cchr1XGEg7dbBXByV5NY2ad8jfxAM7HA3x8D56rq9Ux` | 4 | 81.3 | 57.3 |
| AgaveBam | `DRpbCBMxVnDK7maPM5tGv6MvB3v1sRMC86PZ8okm21hy` | 5 | 56.4 | 57.3 |
| JitoLabs | `E1r4Psq84tHfQ6aPTvvDka4U3u8zPVD7gEUrH25RdxHL` | 4 | 18.9 | 18.9 |
| JitoLabs | `HEL1USMZKAL2odpNBj2oCjffnFGaYwmbGmyewGv1e2TU` | 4 | 19.1 | 18.9 |
| HarmonicAgave | `CAo1dCGYrB6NhHh5xb1cGjUiu86iyCfMTENxgHumSve4` | 5 | 22.7 | 21.8 |
| HarmonicAgave | `Fd7btgySsrjuo25CJCj7oE7VPMyezDhnx7pZkj2v69Nk` | 4 | 18.1 | 21.8 |
| HarmonicFiredancer | `Awes4Tr6TX8JDzEhCZY2QVNimT6iD1zWHzf1vNyGvpLM` | 5 | 18.1 | 17.5 |
| HarmonicFiredancer | `JUPiTERrZqgf1jUyR7dSkhMx4Kn2qJyekWsg3LT1h4b` | 4 | 16.6 | 17.5 |
| Firedancer | `BFmqBsaGjeYA7gHpReKmnVkRyhqiMmHoR9ttv1crWmzy` | 4 | 23.4 | 22.3 |
| Firedancer | `DNVZMSqeRH18Xa4MCTrb1MndNf3Npg4MEwqswo23eWkf` | 4 | 19.8 | 22.3 |
| FireBAM | `9jxgosAfHgHzwnxsHw4RAZYaLVokMbnYtmiZBreynGFP` | 5 | 16.5 | 18.6 |
| FireBAM | `SSmBEooM7RkmyuXxuKgAhTvhQZ36Z3G2WsmLGJKoQLY` | 4 | 53.6 | 18.6 |
| Rakurai | `E3mDbFMr8yZcCAZx5wPUFCRmLX31u8Nnj4jPoPc54h3F` | 4 | 18.5 | 21.7 |
| Rakurai | `ana2y2YvQ3ZPMwm6qhnN3nJoUSiT3qx5Pvetkq9xcfY` | 4 | 22.3 | 21.7 |
| Agave | `5Us18hLZPXJTS4QVuGSsUw137Dyd2tgBaem24Xsf5nBS` | 4 | 30.2 | 24.9 |
| Agave | `7QQGNm3ptwinipDCyaCF7jY5katgmFUu1ieP2f7nwLpE` | 4 | 22.4 | 24.9 |
<!-- itb:end pilot-latency -->

The one-way estimate is half the round-trip time of the QUIC connection, measured just before the send. For the builder classes it ends at the builder's receiver, and the leg from there to the leader stays unseen (section 8).

### 5.9 Load

<!-- itb:begin pilot-loads -->
| Load by | Quartile | Mean load of the burst's blocks | Bursts | tau fee, independent and shared | tau send, equal fee | tau send, equal fee, Agave |
|---|---|---|---|---|---|---|
| costUnits | Q1 | 4672998 to 9845585 | 16 | 0.503 (-0.143 to 1.148), 4 bursts | 0.227 (-0.190 to 0.644), 6 bursts | - |
| costUnits | Q2 | 10222832 to 13103953 | 15 | 0.610 (-0.011 to 1.230), 5 bursts | 0.561 (-0.327 to 1.449), 4 bursts | - |
| costUnits | Q3 | 13352772 to 20905930 | 15 | 0.307 (-0.083 to 0.698), 6 bursts | 0.242 (-0.515 to 1.000), 6 bursts | -0.182 (no interval), 1 bursts |
| costUnits | Q4 | 21136992 to 49998650 | 15 | 0.775 (0.605 to 0.945), 13 bursts | 0.197 (-4.616 to 5.010), 2 bursts | - |
| transactions | Q1 | 141 to 239 | 16 | 0.413 (-0.695 to 1.521), 3 bursts | 0.309 (-0.115 to 0.734), 8 bursts | - |
| transactions | Q2 | 244 to 296 | 15 | 0.293 (-0.649 to 1.235), 4 bursts | 0.509 (-0.033 to 1.051), 5 bursts | -0.182 (no interval), 1 bursts |
| transactions | Q3 | 299 to 419 | 15 | 0.563 (0.306 to 0.820), 9 bursts | 0.505 (0.348 to 0.662), 3 bursts | - |
| transactions | Q4 | 447 to 816 | 15 | 0.779 (0.601 to 0.957), 12 bursts | -0.591 (-5.789 to 4.607), 2 bursts | - |
<!-- itb:end pilot-loads -->

Quartiles split the kept bursts by the mean load of the blocks that hold their probes. No verdict uses this table.

### 5.10 First slot of the window

<!-- itb:begin pilot-first-slot -->
| Blocks | tau fee | tau cross | tau send, equal fee |
|---|---|---|---|
| first slot of the window | 0.673 (0.529 to 0.817), 21 bursts | 0.030 (-0.110 to 0.170), 21 bursts | 0.016 (-0.481 to 0.513), 8 bursts |
| later slots | 0.365 (-0.143 to 0.874), 7 bursts | 0.310 (-0.193 to 0.813), 7 bursts | 0.508 (0.242 to 0.774), 11 bursts |
<!-- itb:end pilot-first-slot -->

All 30 order blocks of the pre-window bursts lie in the first slot, and 25 of the 32 order blocks of the slot-2 bursts lie in later slots. In the pilot this split therefore repeats the moment condition and adds little of its own.

### 5.11 HarmonicAgave strategy

<!-- itb:begin pilot-strategy -->
| Strategy in the memo | Leaders | tau fee | tau cross | tau send, equal fee |
|---|---|---|---|---|
| FBA | `CAo1dCGY...` | 0.469 (no interval), 1 bursts | 0.222 (no interval), 1 bursts | -0.121 (no interval), 1 bursts |
| MRV | `Fd7btgyS...` | 0.419 (-4.476 to 5.314), 2 bursts | -0.037 (-1.919 to 1.845), 2 bursts | - |
| no memo | `CAo1dCGY...`, `Fd7btgyS...` | 0.670 (no interval), 1 bursts | -0.074 (no interval), 1 bursts | 0.364 (-0.791 to 1.519), 2 bursts |
<!-- itb:end pilot-strategy -->

The strategy comes from the memo of the tip-payment crank transaction, in the blocks that carry one. The panel holds one HarmonicAgave leader with each strategy, so strategy and operator stay confounded and the table only describes.

### 5.12 Epochs and rounds

<!-- itb:begin pilot-epochs -->
| Class | tau fee, epoch 1069 | Round means of tau fee |
|---|---|---|
| AgaveBam | 0.905 (3 cells) | 2 rounds, 0.905 to 0.905 |
| JitoLabs | 0.586 (4 cells) | 2 rounds, 0.268 to 0.905 |
| HarmonicAgave | 0.494 (4 cells) | 2 rounds, 0.251 to 0.737 |
| HarmonicFiredancer | 0.771 (3 cells) | 2 rounds, 0.754 to 0.804 |
| Firedancer | 0.343 (4 cells) | 2 rounds, 0.318 to 0.369 |
| FireBAM | 0.912 (3 cells) | 2 rounds, 0.905 to 0.915 |
| Rakurai | 0.410 (4 cells) | 2 rounds, 0.352 to 0.469 |
| Agave | 0.659 (3 cells) | 2 rounds, 0.637 to 0.704 |
<!-- itb:end pilot-epochs -->

Tau fee of a class is the equal-weight mean over its different-fee cells. The pilot covers one epoch.

### 5.13 Competition inside the block

<!-- itb:begin pilot-competition -->
| Class | Probes | Median position (share of block) | Median rank by requested-limit priority | Median rank by costUnits priority | Jito tip transactions | Transactions without a CU limit |
|---|---|---|---|---|---|---|
| AgaveBam | 84 | 0.12 | 0.08 | 0.02 | 2.2% | 10.0% |
| JitoLabs | 96 | 0.22 | 0.17 | 0.04 | 4.0% | 8.8% |
| HarmonicAgave | 108 | 0.13 | 0.16 | 0.07 | 2.8% | 13.4% |
| HarmonicFiredancer | 84 | 0.22 | 0.15 | 0.06 | 2.4% | 13.7% |
| Firedancer | 96 | 0.15 | 0.12 | 0.03 | 2.4% | 8.9% |
| FireBAM | 91 | 0.24 | 0.14 | 0.04 | 4.8% | 6.6% |
| Rakurai | 96 | 0.11 | 0.19 | 0.03 | 1.3% | 5.0% |
| Agave | 72 | 0.08 | 0.17 | 0.06 | 0.2% | 5.3% |
<!-- itb:end pilot-competition -->

Each probe is ranked among the other transactions of its block by the Agave priority `reward * 1 000 000 / (cost + 1)`, where 0 is the top of the block. Reward is `meta.fee` less the burned half of the signature fees. Cost in the first rank is the Agave v4.3.2 cost from requested limits, with the 64 MiB loaded-data allowance for a transaction that sets no limit; the second rank uses `meta.costUnits`. Transactions that tip a Jito tip account stay out of both ranks. Transactions without a compute-unit limit stay out of the first, because their default limit depends on the programs they call. These choices belong to this table alone: the rank describes where a probe would stand under Agave's rule and tests nothing.

### 5.14 Control path

<!-- itb:begin pilot-control -->
No control-path bursts in this stage.
<!-- itb:end pilot-control -->

The pilot sent no control-path bursts; the campaign sends 64.

### 5.15 Minimum for the campaign

<!-- itb:begin minimum -->
| Arm | tau | Pilot bursts | sigma (residual) | Raw variance by cell | Minimum bursts | Campaign bursts per class and cell | Equivalence reachable |
|---|---|---|---|---|---|---|---|
| independent | fee | 13 | 0.332 | pre300 0.050 (8 bursts); slot2 0.183 (5 bursts) | 72 | 8 | no |
| independent | cross | 13 | 0.375 | pre300 0.013 (8 bursts); slot2 0.224 (5 bursts) | 90 | 8 | no |
| shared | fee | 15 | 0.360 | pre300 0.007 (8 bursts); slot2 0.219 (7 bursts) | 84 | 8 | no |
| shared | cross | 15 | 0.462 | pre300 0.076 (8 bursts); slot2 0.307 (7 bursts) | 134 | 8 | no |
| equal_fee | send | 18 | 0.533 | pre300 0.312 (7 bursts); slot2 0.146 (11 bursts) | 177 | 8 | no |
| denominator | limit | 15 | 0.195 | pre300 0.064 (7 bursts); slot2 0.080 (8 bursts) | 28 | 8 | no |

From 68 pilot bursts, 61 kept; alpha_e 0.000521, power per tau 0.90, delta 0.20.
<!-- itb:end minimum -->

The minimum is the number of bursts per class and cell that an equivalence verdict needs at the spread the pilot showed (analysis plan, section 5). The campaign has 8 per class and cell, and every arm needs at least 28, so no cell can reach a form that rests on a TOST, such as "no rule visible". Forms with a significant tau do not depend on this minimum. The minimum is part of the campaign manifest, which goes on chain before the first campaign probe.

## 6. Campaign

The campaign measures the panel over four epochs from 1071 with 8 bursts per class and cell, plus 64 control-path bursts. Verdicts run through the Holm families of the analysis plan. The [campaign addendum](prereg/CAMPAIGN-ADDENDUM.md) goes on chain with the campaign manifest and states what the plan leaves to the code: the exclusion reasons, the hypotheses H3 and H4, lost epoch indexes, the builder label and the control path.

### 6.1 Bursts left out of the order tests

<!-- itb:begin campaign-exclusions -->
No runs of this stage yet.
<!-- itb:end campaign-exclusions -->

### 6.2 Verdicts by class and cell

<!-- itb:begin campaign-cells -->
No runs of this stage yet.
<!-- itb:end campaign-cells -->

### 6.3 Builder against its base

<!-- itb:begin campaign-pairs -->
No runs of this stage yet.
<!-- itb:end campaign-pairs -->

### 6.4 Segments between ticks

<!-- itb:begin campaign-rounds -->
No runs of this stage yet.
<!-- itb:end campaign-rounds -->

### 6.5 Inclusion

<!-- itb:begin campaign-inclusion -->
No runs of this stage yet.
<!-- itb:end campaign-inclusion -->

### 6.6 Moment condition and client labels

<!-- itb:begin campaign-timing -->
No runs of this stage yet.
<!-- itb:end campaign-timing -->

<!-- itb:begin campaign-labels -->
No runs of this stage yet.
<!-- itb:end campaign-labels -->

### 6.7 Probes outside their window

<!-- itb:begin campaign-elsewhere -->
No runs of this stage yet.
<!-- itb:end campaign-elsewhere -->

### 6.8 Path latency

<!-- itb:begin campaign-latency -->
No runs of this stage yet.
<!-- itb:end campaign-latency -->

### 6.9 Load

<!-- itb:begin campaign-loads -->
No runs of this stage yet.
<!-- itb:end campaign-loads -->

### 6.10 First slot of the window

<!-- itb:begin campaign-first-slot -->
No runs of this stage yet.
<!-- itb:end campaign-first-slot -->

### 6.11 HarmonicAgave strategy

<!-- itb:begin campaign-strategy -->
No runs of this stage yet.
<!-- itb:end campaign-strategy -->

### 6.12 Epochs and rounds

<!-- itb:begin campaign-epochs -->
No runs of this stage yet.
<!-- itb:end campaign-epochs -->

The analysis plan fixes no test of stability over epochs, so this table describes it without a verdict (section 9).

### 6.13 Competition inside the block

<!-- itb:begin campaign-competition -->
No runs of this stage yet.
<!-- itb:end campaign-competition -->

### 6.14 Control path

<!-- itb:begin campaign-control -->
No runs of this stage yet.
<!-- itb:end campaign-control -->

The control path is compared with the direct path only within the same leader and epoch. The p of each measure comes from swapping path labels within those strata, exact while the arrangements stay within the label-test budget of the analysis plan and from seeded draws above it.

## 7. The builder mark

<!-- itb:begin tick-runs -->
| Run | Builder-class slots with their builder's tick | Other slots with a known tick |
|---|---|---|
| `pilot-mainnet-20261027T085253Z` | 36 of 36 | 0 of 33 |
<!-- itb:end tick-runs -->

In every pilot slot of a builder-class leader the block carried a tick from that builder's signer, and no slot of another class carried a tick from either signer.

<!-- itb:begin tick-epoch -->
No epoch sample yet.
<!-- itb:end tick-epoch -->

The epoch table samples one whole epoch through RPC, stratified by the class of the slot's leader in gossip. Its script lies in [research/tick-scale](research/tick-scale/) together with the sample and the raw rows.

## 8. Noise and what the kit does not separate

The README lists what stays out of reach from outside the leader ([What it does NOT separate](README.md#what-it-does-not-separate)). Where that touches the tables above:

- The arrival estimate rests on the first-shred event as the RPC node sees it, so shred propagation from the leader enters the timing tables (sections 5.6 and 6.6) as error of unknown source.
- For the builder classes the round-trip time ends at the builder's receiver (sections 5.8 and 6.8).
- Burst 52 shows that a builder can hand probes to another leader behind it (section 5.5). In the gossip snapshot of the panel, `JUPiTERr...` and `nymsGg7Z...` advertise `tpuQuic` on the same IP with different ports (`198.13.140.105:12349` and `:9007`), and the pilot's rule dropped a window only when the leader before it shared the whole address. The campaign panel drops every window that follows another validator on the same IP ([campaign addendum, section 8](prereg/CAMPAIGN-ADDENDUM.md)). The table below counts the windows the pilot's rule keeps and the campaign's rule turns away, and in epoch 1069 they all fall in the two Harmonic classes. Which builder node handed the probes on stays unknown, because every Harmonic builder shares one tick signer.
- The competition ranks assume Agave's priority rule for every class (sections 5.13 and 6.13).

<!-- itb:begin neighbours -->
| Panel | Class | Windows of its panel leaders passing the whole-address rule | After a leader on the same IP with another port | Share |
|---|---|---|---|---|
| `mainnet-e1069-20261027T005744Z` | AgaveBam | 4499 | 0 | 0.000 |
| `mainnet-e1069-20261027T005744Z` | JitoLabs | 6654 | 0 | 0.000 |
| `mainnet-e1069-20261027T005744Z` | HarmonicAgave | 6687 | 582 | 0.087 |
| `mainnet-e1069-20261027T005744Z` | HarmonicFiredancer | 4033 | 534 | 0.132 |
| `mainnet-e1069-20261027T005744Z` | Firedancer | 687 | 0 | 0.000 |
| `mainnet-e1069-20261027T005744Z` | FireBAM | 1101 | 0 | 0.000 |
| `mainnet-e1069-20261027T005744Z` | Rakurai | 758 | 0 | 0.000 |
| `mainnet-e1069-20261027T005744Z` | Agave | 766 | 0 | 0.000 |
| `mainnet-e1071-20261027T233028Z` | AgaveBam | 4607 | 0 | 0.000 |
| `mainnet-e1071-20261027T233028Z` | JitoLabs | 6765 | 0 | 0.000 |
| `mainnet-e1071-20261027T233028Z` | HarmonicAgave | 6609 | 514 | 0.078 |
| `mainnet-e1071-20261027T233028Z` | HarmonicFiredancer | 4136 | 535 | 0.129 |
| `mainnet-e1071-20261027T233028Z` | Firedancer | 329 | 0 | 0.000 |
| `mainnet-e1071-20261027T233028Z` | FireBAM | 1157 | 0 | 0.000 |
| `mainnet-e1071-20261027T233028Z` | Rakurai | 800 | 0 | 0.000 |
| `mainnet-e1071-20261027T233028Z` | Agave | 770 | 0 | 0.000 |
<!-- itb:end neighbours -->

The table comes from the gossip snapshot and the leader schedule stored with each panel in `data/panels/`. It applies the pilot's whole-address rule and counts, among the windows that pass it, those after another leader on the same IP, which no campaign plan draws.

## 9. What went wrong

<!-- itb:begin what-went-wrong -->
| Run | Windows planned | Bursts written | Skipped before sending | Failed | Left out of the order tests |
|---|---|---|---|---|---|
| `pilot-mainnet-20261027T085253Z` | 68 | 68 | none | 0 | fewer-than-two-in-a-block 1, outside-timing-band 6 |
<!-- itb:end what-went-wrong -->

- **2026-10-26 23:25 UTC, mainnet dry-run `dry-run-mainnet-20261026T232506Z`.** The slot clock ran on WebSocket events of the public node, which queued them 5 to 24 slots behind the cluster. The arrival estimate used the same late events, so the run showed 2 of 4 bursts in the band while all four missed. The clock moved onto the node's own timestamps, with a guard that skips a burst when `getSlot` runs 2 or more slots ahead of it (commit 2bacfa2), and the sender now waits for the first-shred events of the window before it closes a burst (commit d8699aa). No later run skipped a burst for the clock.
- **2026-10-27 01:06 UTC, dry-run of the pilot plan.** Within 100 ms of the target stood 4 of 8 pre-window bursts, and all four misses were early. Before any live probe the pre-window band became 200 ms early and 100 ms late of the target. That change and a neutral rewording of the analysis plan redrew the manifest twice. The anchor went on chain from the third manifest, `9a9c92c2...`; the two earlier ones, `74149b29...` and `cf3c768e...`, were simulated and never sent. The seven pilot anchor logs in `logs/` hold six simulations and the one live send at 08:52 UTC.
- **2026-10-27 08:52 UTC, pilot plan.** The validators.app snapshot failed certificate verification (`CERTIFICATE_VERIFY_FAILED`), because the antivirus web shield of the measuring machine re-signs that host. The plan was drawn without it, so no pilot burst carries the second label. The message reached the console only, since the pilot command keeps no draw notes; campaign plans keep theirs in `draw-notes.json`. The fix adds an extra root for that one request (`ITB_EXTRA_CA_FILE`, commit eebdf2f), and [scripts/campaign.sh](scripts/campaign.sh) passes it on. The campaign plan of epoch 1071, drawn at 23:30 UTC the same day, carries the snapshot with 669 records, and each of its 144 bursts has the same class there as in gossip.
- **2026-10-27, pilot run.** Six bursts arrived outside their band. Burst 52 landed one slot early in another leader's block, and five probes of burst 99 met a closed connection (section 5.5).
- **2026-10-27, minimum.** The spread of tau in the pilot puts every equivalence form out of reach of the campaign (section 5.15).
- **2026-10-27, epoch tick sample.** The public RPC node cut a 0.9 MB `getBlock` body short (`IncompleteRead`). The RPC client retried only OS-level errors, so the read stopped after 321 blocks. It now retries a cut body too, with a selftest check for each kind of failure.
- **2026-10-27 22:35 UTC, first campaign package.** A review of the pre-registration found rules that lived only in code, and the panel rule still kept windows after a leader on the same IP. The [campaign addendum](prereg/CAMPAIGN-ADDENDUM.md) states those rules, and everything drawn from the panel was drawn again at 23:30 UTC under the IP rule. The panel kept its 16 leaders, and the plan of epoch index 0 moved one burst of `Awes4Tr6...`, whose first window followed `shftkxns...` on the same IP (`198.13.140.105`).
- **Stability over epochs.** The README says four epochs show whether a rule holds over time, yet the analysis plan fixed no test for it. The epoch tables (sections 5.12 and 6.12) describe it without a verdict.

## 10. Other measurements of the same question

Four public repositories measured the ordering rule on mainnet after Alpenglow before this campaign. What follows rests on their reports as of 2026-10-27.

- [fomoles/superteam-inside-the-block](https://github.com/fomoles/superteam-inside-the-block), epoch 1066, 2026-10-24. Pairs of probes go straight to the leader's TPU with a controlled gap of 0 to 150 ms, in two runs of 1100 leader windows (6600 and 6438 probes) on panels of 20 and 47 validators, and the checks of the second run were registered in git before it. The report reads the sort key as fee per estimated cost unit, with the 64 MiB loaded-data allowance inside the cost. By its own account the arm of the first run could not tell a total-fee rule from that key; the second run capped the loaded data so that the two rules disagree, and fee per estimated cost won (its check C6, -0.61 with an interval from -0.70 to -0.52). In its runs JitoLabs lets the fee decide less often than the other clients with enough pairs, and Firedancer 26.10.4 gives fee ties to the later arrival (TAU 1.00). Of the 603 direct probes that landed with a leader other than the target, 596 landed with one that advertises the target's IP.
- [eternally-black/alpenglow-validator-ordering](https://github.com/eternally-black/alpenglow-validator-ordering), 2026-10-24 to 2026-10-26. Each of its pre-registered studies froze the hashes of its plan in a mainnet Memo before the first probe, and positive controls on an Agave and a Firedancer validator recovered their known rule. All six core targets order its probes by Agave's priority, `reward / (cost + 1)`, and four exploratory targets agree, Rakurai in part. Firedancer lands the later of two identical probes first in 50 of 54 pairs. Eight leaders of the pilot panel stand among its targets, and five of them (`7QQGNm3p...`, `HEL1USMZ...`, `DRpbCBMx...`, `Fd7btgyS...`, `JUPiTERr...`) are among its six core ones.
- [ukraineopt/inside-the-block](https://github.com/ukraineopt/inside-the-block). 5,296 probes aimed at 27 validators on 8 client builds, without pre-registration. For both Harmonic classes it reads arrival order with a batching window of about 15 to 30 ms, where the fee sorts only inside each small group, and it notes that both classes advertise one IP with different ports.
- [zdfgu113/inside-the-block](https://github.com/zdfgu113/inside-the-block), from 2026-10-23. Bursts of four fee levels in a Latin-square send order gave 135 same-block pairs over eight builds. AgaveBam puts the higher fee first in 25 of 32 pairs, while HarmonicAgave (16 of 30) and HarmonicFiredancer (14 of 27) stay near chance at its price range.

On Harmonic the reports split. fomoles finds a fee sort in both Harmonic classes, and eternally-black counts a HarmonicAgave and a HarmonicFiredancer validator among its core targets that follow Agave's priority. ukraineopt reads arrival order in short batches there, and zdfgu113 sees no fee order. The campaign measures both Harmonic classes with its own design and fixes no expectation for them in advance.

Fee per cost is the reading of two of these reports, so the campaign checks it independently in epochs 1071 and later with another design: bursts of 12 probes in one leader window, an arm that holds the fee equal, an arm that changes only the requested cost, and builder classes set against their base client. The denominator arm separates the same pair of rules as the second fomoles run by another route: all 12 probes of a burst pay one priority fee and half of them request 20 000 CU instead of 1000, so a total-fee rule sees ties where fee per requested cost puts the 1000 CU probes first. Where the leaders shared with eternally-black stay in the campaign panel, the campaign measures the same validators again in later epochs.

Two parts of this kit appear in none of these reports, by a text search of the public repositories on this question on 2026-10-27 with data files left out. The builder mark is checked on chain data: each slot of a builder class is matched to its builder through the builder's tick in the block (section 7), and the analysis plan tests order inside the segments between ticks (sections 5.4 and 6.4). The four epochs of the campaign are a description only: the epoch tables show how each rule holds over time (section 6.12), and the analysis plan fixes no test of stability for them (section 9).

## Appendix A. Every burst

<!-- itb:begin bursts -->
| Run | Burst | UTC (blockTime) | Epoch | Window slots | Leader | Class | clientId at burst | Arm | Timing | Delivered | In window | Other leaders' class | Fee (lamports) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `pilot-mainnet-20261027T085253Z` | 41 | 2026-10-27 08:56:00 | 1069 | 462010628-462010631 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | denominator | pre300 | 12 | 12 | - | 72000 |
| `pilot-mainnet-20261027T085253Z` | 42 | 2026-10-27 08:57:11 | 1069 | 462010960-462010963 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | denominator | slot2 | 12 | 12 | - | 60000 |
| `pilot-mainnet-20261027T085253Z` | 43 | 2026-10-27 08:57:51 | 1069 | 462011144-462011147 | `5Cchr1XG...` | AgaveBam | AgaveBam | denominator | slot2 | 12 | 12 | - | 72000 |
| `pilot-mainnet-20261027T085253Z` | 44 | 2026-10-27 08:58:31 | 1069 | 462011332-462011335 | `E1r4Psq8...` | JitoLabs | JitoLabs | denominator | slot2 | 12 | 12 | - | 61200 |
| `pilot-mainnet-20261027T085253Z` | 45 | 2026-10-27 08:59:13 | 1069 | 462011532-462011535 | `DNVZMSqe...` | Firedancer | Firedancer | denominator | pre300 | 12 | 12 | - | 60120 |
| `pilot-mainnet-20261027T085253Z` | 46 | 2026-10-27 08:59:55 | 1069 | 462011732-462011735 | `E3mDbFMr...` | Rakurai | Rakurai | denominator | slot2 | 12 | 12 | - | 60120 |
| `pilot-mainnet-20261027T085253Z` | 47 | 2026-10-27 09:00:55 | 1069 | 462012016-462012019 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | denominator | slot2 | 12 | 12 | - | 60000 |
| `pilot-mainnet-20261027T085253Z` | 48 | 2026-10-27 09:01:33 | 1069 | 462012200-462012203 | `HEL1USMZ...` | JitoLabs | JitoLabs | denominator | pre300 | 12 | 12 | - | 60000 |
| `pilot-mainnet-20261027T085253Z` | 49 | 2026-10-27 09:02:09 | 1069 | 462012364-462012367 | `DRpbCBMx...` | AgaveBam | AgaveBam | equal_fee | slot2 | 12 | 12 | - | 60000 |
| `pilot-mainnet-20261027T085253Z` | 50 | 2026-10-27 09:02:44 | 1069 | 462012528-462012531 | `5Us18hLZ...` | Agave | Agave | denominator | slot2 | 12 | 12 | - | 61200 |
| `pilot-mainnet-20261027T085253Z` | 51 | 2026-10-27 09:03:51 | 1069 | 462012844-462012847 | `ana2y2Yv...` | Rakurai | Rakurai | denominator | pre300 | 12 | 12 | - | 72000 |
| `pilot-mainnet-20261027T085253Z` | 52 | 2026-10-27 09:04:34 | 1069 | 462013048-462013051 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | denominator | pre300 | 12 | 0 | HarmonicFiredancer | 61200 |
| `pilot-mainnet-20261027T085253Z` | 53 | 2026-10-27 09:05:21 | 1069 | 462013268-462013271 | `DRpbCBMx...` | AgaveBam | AgaveBam | denominator | pre300 | 12 | 12 | - | 61200 |
| `pilot-mainnet-20261027T085253Z` | 54 | 2026-10-27 09:06:48 | 1069 | 462013676-462013679 | `9jxgosAf...` | FireBAM | FireBAM | denominator | pre300 | 12 | 12 | - | 60000 |
| `pilot-mainnet-20261027T085253Z` | 55 | 2026-10-27 09:08:17 | 1069 | 462014096-462014099 | `7QQGNm3p...` | Agave | Agave | denominator | pre300 | 12 | 12 | - | 60120 |
| `pilot-mainnet-20261027T085253Z` | 56 | 2026-10-27 09:12:05 | 1069 | 462015172-462015175 | `BFmqBsaG...` | Firedancer | Firedancer | denominator | slot2 | 12 | 12 | - | 60120 |
| `pilot-mainnet-20261027T085253Z` | 57 | 2026-10-27 09:41:37 | 1069 | 462023512-462023515 | `SSmBEooM...` | FireBAM | FireBAM | denominator | slot2 | 12 | 12 | - | 72000 |
| `pilot-mainnet-20261027T085253Z` | 58 | 2026-10-27 09:42:19 | 1069 | 462023712-462023715 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | equal_fee | slot2 | 12 | 12 | - | 61200 |
| `pilot-mainnet-20261027T085253Z` | 59 | 2026-10-27 09:43:04 | 1069 | 462023924-462023927 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | equal_fee | pre300 | 12 | 12 | - | 60120 |
| `pilot-mainnet-20261027T085253Z` | 60 | 2026-10-27 09:43:42 | 1069 | 462024100-462024103 | `9jxgosAf...` | FireBAM | FireBAM | equal_fee | slot2 | 12 | 12 | - | 60120 |
| `pilot-mainnet-20261027T085253Z` | 61 | 2026-10-27 09:44:32 | 1069 | 462024336-462024339 | `E3mDbFMr...` | Rakurai | Rakurai | equal_fee | pre300 | 12 | 12 | - | 60120 |
| `pilot-mainnet-20261027T085253Z` | 62 | 2026-10-27 09:45:33 | 1069 | 462024616-462024619 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | equal_fee | slot2 | 12 | 12 | - | 61200 |
| `pilot-mainnet-20261027T085253Z` | 63 | 2026-10-27 09:46:37 | 1069 | 462024916-462024919 | `E1r4Psq8...` | JitoLabs | JitoLabs | equal_fee | pre300 | 12 | 12 | - | 61200 |
| `pilot-mainnet-20261027T085253Z` | 64 | 2026-10-27 09:47:12 | 1069 | 462025080-462025083 | `HEL1USMZ...` | JitoLabs | JitoLabs | equal_fee | slot2 | 12 | 12 | - | 60000 |
| `pilot-mainnet-20261027T085253Z` | 65 | 2026-10-27 09:48:12 | 1069 | 462025360-462025363 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | equal_fee | slot2 | 12 | 12 | - | 61200 |
| `pilot-mainnet-20261027T085253Z` | 66 | 2026-10-27 09:48:49 | 1069 | 462025536-462025539 | `DRpbCBMx...` | AgaveBam | AgaveBam | equal_fee | slot2 | 12 | 12 | - | 72000 |
| `pilot-mainnet-20261027T085253Z` | 67 | 2026-10-27 09:49:58 | 1069 | 462025860-462025863 | `ana2y2Yv...` | Rakurai | Rakurai | equal_fee | slot2 | 12 | 12 | - | 60000 |
| `pilot-mainnet-20261027T085253Z` | 68 | 2026-10-27 09:50:35 | 1069 | 462026036-462026039 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | equal_fee | pre300 | 12 | 12 | - | 72000 |
| `pilot-mainnet-20261027T085253Z` | 69 | 2026-10-27 09:51:10 | 1069 | 462026196-462026199 | `DNVZMSqe...` | Firedancer | Firedancer | equal_fee | slot2 | 12 | 12 | - | 72000 |
| `pilot-mainnet-20261027T085253Z` | 70 | 2026-10-27 09:52:23 | 1069 | 462026544-462026547 | `5Us18hLZ...` | Agave | Agave | equal_fee | pre300 | 12 | 12 | - | 61200 |
| `pilot-mainnet-20261027T085253Z` | 71 | 2026-10-27 09:52:59 | 1069 | 462026712-462026715 | `5Cchr1XG...` | AgaveBam | AgaveBam | equal_fee | pre300 | 12 | 12 | - | 60000 |
| `pilot-mainnet-20261027T085253Z` | 72 | 2026-10-27 10:07:26 | 1069 | 462030776-462030779 | `7QQGNm3p...` | Agave | Agave | equal_fee | slot2 | 12 | 12 | - | 60120 |
| `pilot-mainnet-20261027T085253Z` | 73 | 2026-10-27 10:11:00 | 1069 | 462031772-462031775 | `BFmqBsaG...` | Firedancer | Firedancer | equal_fee | pre300 | 12 | 12 | - | 72000 |
| `pilot-mainnet-20261027T085253Z` | 74 | 2026-10-27 10:16:21 | 1069 | 462033280-462033283 | `SSmBEooM...` | FireBAM | FireBAM | equal_fee | pre300 | 12 | 12 | - | 60000 |
| `pilot-mainnet-20261027T085253Z` | 75 | 2026-10-27 10:17:17 | 1069 | 462033544-462033547 | `5Cchr1XG...` | AgaveBam | AgaveBam | independent | pre300 | 12 | 12 | - | 63330 |
| `pilot-mainnet-20261027T085253Z` | 76 | 2026-10-27 10:18:18 | 1069 | 462033832-462033835 | `9jxgosAf...` | FireBAM | FireBAM | independent | slot2 | 12 | 12 | - | 63330 |
| `pilot-mainnet-20261027T085253Z` | 77 | 2026-10-27 10:18:58 | 1069 | 462034020-462034023 | `DNVZMSqe...` | Firedancer | Firedancer | independent | slot2 | 12 | 12 | - | 63330 |
| `pilot-mainnet-20261027T085253Z` | 78 | 2026-10-27 10:19:44 | 1069 | 462034240-462034243 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | independent | slot2 | 12 | 12 | - | 63330 |
| `pilot-mainnet-20261027T085253Z` | 79 | 2026-10-27 10:20:18 | 1069 | 462034400-462034403 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | independent | slot2 | 12 | 12 | - | 63330 |
| `pilot-mainnet-20261027T085253Z` | 80 | 2026-10-27 10:21:06 | 1069 | 462034624-462034627 | `DRpbCBMx...` | AgaveBam | AgaveBam | independent | slot2 | 12 | 12 | - | 63330 |
| `pilot-mainnet-20261027T085253Z` | 81 | 2026-10-27 10:21:41 | 1069 | 462034784-462034787 | `ana2y2Yv...` | Rakurai | Rakurai | independent | slot2 | 12 | 12 | - | 63330 |
| `pilot-mainnet-20261027T085253Z` | 82 | 2026-10-27 10:22:36 | 1069 | 462035044-462035047 | `HEL1USMZ...` | JitoLabs | JitoLabs | independent | slot2 | 12 | 12 | - | 63330 |
| `pilot-mainnet-20261027T085253Z` | 83 | 2026-10-27 10:23:18 | 1069 | 462035244-462035247 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | independent | pre300 | 12 | 12 | - | 63330 |
| `pilot-mainnet-20261027T085253Z` | 84 | 2026-10-27 10:23:54 | 1069 | 462035412-462035415 | `E1r4Psq8...` | JitoLabs | JitoLabs | independent | pre300 | 12 | 12 | - | 63330 |
| `pilot-mainnet-20261027T085253Z` | 85 | 2026-10-27 10:24:38 | 1069 | 462035616-462035619 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | independent | pre300 | 12 | 12 | - | 63330 |
| `pilot-mainnet-20261027T085253Z` | 86 | 2026-10-27 10:25:16 | 1069 | 462035792-462035795 | `E3mDbFMr...` | Rakurai | Rakurai | independent | pre300 | 12 | 12 | - | 63330 |
| `pilot-mainnet-20261027T085253Z` | 87 | 2026-10-27 10:27:12 | 1069 | 462036340-462036343 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | equal_fee | slot2 | 12 | 12 | - | 72000 |
| `pilot-mainnet-20261027T085253Z` | 88 | 2026-10-27 10:28:59 | 1069 | 462036844-462036847 | `7QQGNm3p...` | Agave | Agave | independent | slot2 | 12 | 12 | - | 63330 |
| `pilot-mainnet-20261027T085253Z` | 89 | 2026-10-27 10:32:20 | 1069 | 462037780-462037783 | `BFmqBsaG...` | Firedancer | Firedancer | independent | pre300 | 12 | 12 | - | 63330 |
| `pilot-mainnet-20261027T085253Z` | 90 | 2026-10-27 10:38:16 | 1069 | 462039460-462039463 | `SSmBEooM...` | FireBAM | FireBAM | independent | pre300 | 12 | 12 | - | 63330 |
| `pilot-mainnet-20261027T085253Z` | 91 | 2026-10-27 10:38:53 | 1069 | 462039632-462039635 | `5Us18hLZ...` | Agave | Agave | independent | pre300 | 12 | 12 | - | 63330 |
| `pilot-mainnet-20261027T085253Z` | 92 | 2026-10-27 10:39:42 | 1069 | 462039864-462039867 | `E1r4Psq8...` | JitoLabs | JitoLabs | shared | slot2 | 12 | 12 | - | 63330 |
| `pilot-mainnet-20261027T085253Z` | 93 | 2026-10-27 10:40:45 | 1069 | 462040156-462040159 | `5Cchr1XG...` | AgaveBam | AgaveBam | shared | slot2 | 12 | 12 | - | 63330 |
| `pilot-mainnet-20261027T085253Z` | 94 | 2026-10-27 10:41:42 | 1069 | 462040428-462040431 | `DRpbCBMx...` | AgaveBam | AgaveBam | shared | pre300 | 12 | 12 | - | 63330 |
| `pilot-mainnet-20261027T085253Z` | 95 | 2026-10-27 10:42:21 | 1069 | 462040608-462040611 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | shared | pre300 | 12 | 12 | - | 63330 |
| `pilot-mainnet-20261027T085253Z` | 96 | 2026-10-27 10:43:01 | 1069 | 462040796-462040799 | `HEL1USMZ...` | JitoLabs | JitoLabs | shared | pre300 | 12 | 12 | - | 63330 |
| `pilot-mainnet-20261027T085253Z` | 97 | 2026-10-27 10:43:55 | 1069 | 462041052-462041055 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | shared | slot2 | 12 | 12 | - | 63330 |
| `pilot-mainnet-20261027T085253Z` | 98 | 2026-10-27 10:44:30 | 1069 | 462041216-462041219 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | shared | pre300 | 12 | 12 | - | 63330 |
| `pilot-mainnet-20261027T085253Z` | 99 | 2026-10-27 10:45:09 | 1069 | 462041396-462041399 | `SSmBEooM...` | FireBAM | FireBAM | shared | slot2 | 7 | 7 | - | 37120 |
| `pilot-mainnet-20261027T085253Z` | 100 | 2026-10-27 10:46:11 | 1069 | 462041688-462041691 | `9jxgosAf...` | FireBAM | FireBAM | equal_fee | slot2 | 12 | 12 | - | 60120 |
| `pilot-mainnet-20261027T085253Z` | 101 | 2026-10-27 10:46:52 | 1069 | 462041884-462041887 | `DNVZMSqe...` | Firedancer | Firedancer | shared | pre300 | 12 | 12 | - | 63330 |
| `pilot-mainnet-20261027T085253Z` | 102 | 2026-10-27 10:47:55 | 1069 | 462042176-462042179 | `9jxgosAf...` | FireBAM | FireBAM | shared | pre300 | 12 | 12 | - | 63330 |
| `pilot-mainnet-20261027T085253Z` | 103 | 2026-10-27 10:48:39 | 1069 | 462042384-462042387 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | shared | slot2 | 12 | 12 | - | 63330 |
| `pilot-mainnet-20261027T085253Z` | 104 | 2026-10-27 10:50:26 | 1069 | 462042892-462042895 | `ana2y2Yv...` | Rakurai | Rakurai | shared | pre300 | 12 | 12 | - | 63330 |
| `pilot-mainnet-20261027T085253Z` | 105 | 2026-10-27 10:51:03 | 1069 | 462043068-462043071 | `5Us18hLZ...` | Agave | Agave | shared | slot2 | 12 | 12 | - | 63330 |
| `pilot-mainnet-20261027T085253Z` | 106 | 2026-10-27 10:52:16 | 1069 | 462043412-462043415 | `7QQGNm3p...` | Agave | Agave | shared | pre300 | 12 | 12 | - | 63330 |
| `pilot-mainnet-20261027T085253Z` | 107 | 2026-10-27 10:55:34 | 1069 | 462044336-462044339 | `E3mDbFMr...` | Rakurai | Rakurai | shared | slot2 | 12 | 12 | - | 63330 |
| `pilot-mainnet-20261027T085253Z` | 108 | 2026-10-27 10:56:43 | 1069 | 462044660-462044663 | `BFmqBsaG...` | Firedancer | Firedancer | shared | slot2 | 12 | 12 | - | 63330 |
<!-- itb:end bursts -->
