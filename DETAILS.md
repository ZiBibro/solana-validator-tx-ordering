# Details of the report

[REPORT.md](REPORT.md) gives the answer, the spend, the campaign results and the conditions of the measurement. This file holds every other table, the pilot, the method notes and the full log, and keeps the section numbers the report had before it was split, so a reference such as section 5.6 still points here. The old sections 1 and 4 moved to REPORT.md, and so did section 10 on other measurements. Each table sits between `<!-- itb:begin NAME -->` and `<!-- itb:end NAME -->` and comes from `python -m itb report`, which fills this file and REPORT.md; `python -m itb report --check` fails when a table differs from the raw data or a table is missing from both files.

## 2. Validators and clients

<!-- itb:begin panel -->
| Leader identity | Class at selection | gossip clientId and version at the bursts | validators.app label | Stages | Bursts | Probes in window |
|---|---|---|---|---|---|---|
| `5Cchr1XGEg7dbBXByV5NY2ad8jfxAM7HA3x8D56rq9Ux` | AgaveBam | AgaveBam 4.3.2 | AgaveBam 4.3.2, not taken | pilot, campaign | 39 | 432 |
| `DRpbCBMxVnDK7maPM5tGv6MvB3v1sRMC86PZ8okm21hy` | AgaveBam | AgaveBam 4.3.2, AgaveBam 4.4.0, AgaveBam 4.4.0-rc.1 | AgaveBam 4.3.2, AgaveBam 4.4.0, not taken | pilot, campaign | 40 | 445 |
| `E1r4Psq84tHfQ6aPTvvDka4U3u8zPVD7gEUrH25RdxHL` | JitoLabs | JitoLabs 4.3.2, JitoLabs 4.4.0 | JitoLabs 4.3.2, JitoLabs 4.4.0, not taken | pilot, campaign | 39 | 452 |
| `HEL1USMZKAL2odpNBj2oCjffnFGaYwmbGmyewGv1e2TU` | JitoLabs | JitoLabs 4.3.2, JitoLabs 4.4.0 | JitoLabs 4.3.2, JitoLabs 4.4.0, not taken | pilot, campaign | 39 | 445 |
| `CAo1dCGYrB6NhHh5xb1cGjUiu86iyCfMTENxgHumSve4` | HarmonicAgave | HarmonicAgave 4.3.2 | HarmonicAgave 4.3.2, not taken | pilot, campaign | 40 | 472 |
| `Fd7btgySsrjuo25CJCj7oE7VPMyezDhnx7pZkj2v69Nk` | HarmonicAgave | HarmonicAgave 4.3.2, HarmonicAgave 4.4.0, HarmonicAgave 4.4.0-rc.1 | HarmonicAgave 4.3.2, HarmonicAgave 4.4.0, not taken | pilot, campaign | 39 | 445 |
| `Awes4Tr6TX8JDzEhCZY2QVNimT6iD1zWHzf1vNyGvpLM` | HarmonicFiredancer | HarmonicFiredancer 26.10.4, HarmonicFiredancer 26.10.5 | HarmonicFiredancer 26.10.4, HarmonicFiredancer 26.10.5, not taken | pilot, campaign | 40 | 470 |
| `JUPiTERrZqgf1jUyR7dSkhMx4Kn2qJyekWsg3LT1h4b` | HarmonicFiredancer | HarmonicFiredancer 26.10.4, HarmonicFiredancer 26.10.5 | HarmonicFiredancer 26.10.4, HarmonicFiredancer 26.10.5, not taken | pilot, campaign | 39 | 448 |
| `4VRs6A9zBRXz6MLcmQGsBiSoWE2JjHrmw7LintC3T4Nv` | Firedancer | Firedancer 26.10.4, Firedancer 26.10.5 | Firedancer 26.10.4, Firedancer 26.10.5 | campaign | 35 | 412 |
| `BFmqBsaGjeYA7gHpReKmnVkRyhqiMmHoR9ttv1crWmzy` | Firedancer | Firedancer 26.10.4, Firedancer 26.10.5 | Firedancer 26.10.4, Firedancer 26.10.5, JitoLabs 4.3.2, not taken | pilot, campaign | 39 | 461 |
| `DNVZMSqeRH18Xa4MCTrb1MndNf3Npg4MEwqswo23eWkf` | Firedancer | Firedancer 26.10.4 | not taken | pilot | 4 | 48 |
| `9jxgosAfHgHzwnxsHw4RAZYaLVokMbnYtmiZBreynGFP` | FireBAM | FireBAM 26.10.4, FireBAM 26.10.5 | FireBAM 26.10.5, not taken | pilot, campaign | 40 | 474 |
| `LA1NEzryoih6CQW3gwQqJQffK2mKgnXcjSQZSRpM3wc` | FireBAM | FireBAM 26.10.5 | FireBAM 26.10.5 | campaign | 35 | 410 |
| `SSmBEooM7RkmyuXxuKgAhTvhQZ36Z3G2WsmLGJKoQLY` | FireBAM | FireBAM 26.10.4 | not taken | pilot | 4 | 43 |
| `E3mDbFMr8yZcCAZx5wPUFCRmLX31u8Nnj4jPoPc54h3F` | Rakurai | Rakurai 4.3.2, Rakurai 4.4.0 | Rakurai 4.3.2, not taken | pilot, campaign | 39 | 456 |
| `ana2y2YvQ3ZPMwm6qhnN3nJoUSiT3qx5Pvetkq9xcfY` | Rakurai | Rakurai 4.3.2, Rakurai 4.4.0 | Rakurai 4.3.2, Rakurai 4.4.0, not taken | pilot, campaign | 39 | 449 |
| `5Us18hLZPXJTS4QVuGSsUw137Dyd2tgBaem24Xsf5nBS` | Agave | Agave 4.3.2 | Agave 4.3.2, not taken | pilot, campaign | 39 | 456 |
| `7QQGNm3ptwinipDCyaCF7jY5katgmFUu1ieP2f7nwLpE` | Agave | Agave 4.3.2 | Agave 4.3.2, not taken | pilot, campaign | 39 | 450 |

18 validators, 8 classes by gossip clientId.
<!-- itb:end panel -->

The panel of each stage holds 16 validators in 8 classes by gossip `clientId`, two leaders per class, on two code bases. Over both stages 18 validators appear: `DNVZMSqe...` (Firedancer) and `SSmBEooM...` (FireBAM) stand in the pilot alone, and `4VRs6A9z...` (Firedancer) and `LA1NEzry...` (FireBAM) in the campaign alone. Agave-based builds 4.3.2 and 4.4.0 run under the classes Agave, JitoLabs, AgaveBam, HarmonicAgave and Rakurai. Firedancer 26.10.4 and 26.10.5 run under Firedancer and its two builder forks, FireBAM and HarmonicFiredancer. The label and the version come from `getClusterNodes` at the moment of each burst, and each leader showed its selection class at each of its bursts in both stages (sections 5.6 and 6.6). At some bursts validators.app labelled `BFmqBsaG...` JitoLabs 4.3.2, while gossip showed Firedancer at each of them. The second label from validators.app is missing for the pilot, because the request failed on the measuring machine (section 9).

## 3. Measurements and their dates

<!-- itb:begin runs -->
| Run | Stage | Network | Mode | Started (UTC) | First burst (UTC) | Last burst (UTC) | Bursts | Probes | Delivered | Included | In target window | Commit |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `campaign-mainnet-20261028T034521Z` | campaign | mainnet | live | 2026-10-28 03:46:01 | - | - | 0 | 0 | 0 | - | - | `6df1ef9` |
| `campaign-mainnet-20261028T055501Z` | campaign | mainnet | live | 2026-10-28 05:55:36 | 2026-10-29 03:00:13 | 2026-10-29 09:41:31 | 56 | 672 | 660 | 652 | 629 | `5501e6e` |
| `campaign-mainnet-20261029T120927Z` | campaign | mainnet | live | 2026-10-29 12:15:03 | 2026-10-29 13:20:06 | 2026-10-30 01:36:46 | 72 | 864 | 852 | 852 | 835 | `18a543c` |
| `campaign-mainnet-20261030T015219Z` | campaign | mainnet | live | 2026-10-30 01:52:56 | 2026-10-30 04:32:21 | 2026-10-31 01:24:15 | 144 | 1728 | 1728 | 1728 | 1683 | `18a543c` |
| `campaign-mainnet-20261031T014357Z` | campaign | mainnet | live | 2026-10-31 01:46:50 | 2026-10-31 03:53:13 | 2026-11-01 03:57:58 | 144 | 1728 | 1704 | 1704 | 1660 | `18a543c` |
| `campaign-mainnet-20261101T041655Z` | campaign | mainnet | live | 2026-11-01 04:17:34 | 2026-11-01 06:55:08 | 2026-11-02 05:24:44 | 144 | 1728 | 1716 | 1716 | 1662 | `18a543c` |
| `devnet-devnet-20261027T083150Z` | devnet | devnet | live | 2026-10-27 08:32:32 | 2026-10-27 08:32:58 | 2026-10-27 08:34:52 | 4 | 48 | 48 | 48 | 48 | `8ff9207` |
| `dry-run-devnet-20261026T231756Z` | dry-run | devnet | dry-run | 2026-10-26 23:18:33 | 2026-10-26 23:18:46 | 2026-10-26 23:20:41 | 4 | 48 | 0 | - | - | `0e87340` |
| `dry-run-devnet-20261027T082858Z` | dry-run | devnet | dry-run | 2026-10-27 08:29:35 | 2026-10-27 08:29:45 | 2026-10-27 08:31:40 | 4 | 48 | 0 | - | - | `8ff9207` |
| `dry-run-mainnet-20261026T232506Z` | dry-run | mainnet | dry-run | 2026-10-26 23:25:45 | 2026-10-26 23:26:07 | 2026-10-26 23:27:50 | 4 | 48 | 0 | - | - | `7aaee67` |
| `dry-run-mainnet-20261027T002723Z` | dry-run | mainnet | dry-run | 2026-10-27 00:28:04 | 2026-10-27 00:28:20 | 2026-10-27 00:30:02 | 4 | 48 | 0 | - | - | `2bacfa2` |
| `dry-run-mainnet-20261027T003443Z` | dry-run | mainnet | dry-run | 2026-10-27 00:35:15 | 2026-10-27 00:35:41 | 2026-10-27 00:37:22 | 4 | 48 | 0 | - | - | `d8699aa` |
| `dry-run-mainnet-20261027T010659Z` | dry-run | mainnet | dry-run | 2026-10-27 01:07:38 | 2026-10-27 01:09:06 | 2026-10-27 01:48:43 | 17 | 204 | 0 | - | - | `d4f2cca-dirty` |
| `dry-run-mainnet-20261027T130541Z` | dry-run | mainnet | dry-run | 2026-10-27 13:06:16 | 2026-10-27 13:06:41 | 2026-10-27 13:13:28 | 12 | 144 | 0 | - | - | `5ffb53a` |
| `dry-run-mainnet-20261028T005747Z` | dry-run | mainnet | dry-run | 2026-10-28 00:58:24 | - | - | 0 | 0 | 0 | - | - | `2293eb4` |
| `dry-run-mainnet-20261028T011115Z` | dry-run | mainnet | dry-run | 2026-10-28 01:11:48 | 2026-10-28 01:12:21 | 2026-10-28 01:19:07 | 12 | 144 | 0 | - | - | `321b11d` |
| `dry-run-mainnet-20261028T014101Z` | dry-run | mainnet | dry-run | 2026-10-28 01:41:35 | 2026-10-28 01:42:01 | 2026-10-28 01:49:28 | 12 | 144 | 0 | - | - | `73f3d20` |
| `dry-run-mainnet-20261028T020206Z` | dry-run | mainnet | dry-run | 2026-10-28 02:02:40 | 2026-10-28 02:03:11 | 2026-10-28 02:10:16 | 12 | 144 | 0 | - | - | `732f502` |
| `dry-run-mainnet-20261028T021746Z` | dry-run | mainnet | dry-run | 2026-10-28 02:18:18 | 2026-10-28 02:53:10 | 2026-10-28 03:00:00 | 12 | 144 | 0 | - | - | `cf7c56a` |
| `dry-run-mainnet-20261028T043400Z` | dry-run | mainnet | dry-run | 2026-10-28 04:34:32 | 2026-10-28 04:39:41 | 2026-10-28 04:50:02 | 12 | 144 | 0 | - | - | `6fdceca` |
| `pilot-mainnet-20261027T085253Z` | pilot | mainnet | live | 2026-10-27 08:53:32 | 2026-10-27 08:55:58 | 2026-10-27 10:56:41 | 68 | 816 | 811 | 811 | 799 | `ef77ca3` |
<!-- itb:end runs -->

Every mainnet run is dated after the Alpenglow upgrade of 2026-10-21, so no measurement mixes the two sides of it. The devnet runs test the pipeline and feed no result. The dry-run `dry-run-mainnet-20261028T005747Z` checks the campaign plan of epoch 1071 and stopped after 150 s, about 26 hours before the plan's first round, so it holds the cost check and the slot clock and no burst. The campaign run `campaign-mainnet-20261028T034521Z` funded the payers and was stopped before its first window, so that the campaign could start on the leader correction of commit `6fdceca`; it holds no burst. Appendix A dates every burst by the `blockTime` of its first included probe.

## 5. Pilot, 2026-10-27, epoch 1069

The pilot sent 68 bursts into the windows of the 16 panel leaders between 08:53 and 10:56 UTC on 2026-10-27, after its analysis plan went on chain at 08:52 UTC. Most cells of a class hold one burst, where a cell is one arm under one moment condition, so a form below is what a single burst gives. The pilot measures inclusion and the spread of tau between bursts, which set the minimum for the campaign (section 5.15). It also tests whether the segments between ticks are rounds in time (section 5.4).

### 5.1 Bursts left out of the order tests

<!-- itb:begin pilot-exclusions -->
68 bursts: 61 kept for the order tests, 7 left out, 0 of them for more than one reason. Reasons: fewer-than-two-in-a-block 1, outside-timing-band 6.
<!-- itb:end pilot-exclusions -->

### 5.2 Order by class and cell

<!-- itb:begin pilot-cells -->
| Class | Arm | Timing | Bursts | Form | Detail | tau (95% CI; p) | Violated pair share (95% CI) |
|---|---|---|---|---|---|---|---|
| Agave | denominator | pre300 | 1 | undetermined | - | limit 0.082 (no interval; p 0.818; mean of burst taus 0.082); send 0.152 (no interval; p 0.545; mean of burst taus 0.152) | 0.444 (no interval); 0 of 1 bursts without a violation |
| Agave | denominator | slot2 | 1 | undetermined | - | limit 0.041 (no interval; p 0.937; mean of burst taus 0.041); send -0.030 (no interval; p 0.947; mean of burst taus -0.030) | 0.472 (no interval); 0 of 1 bursts without a violation |
| Agave | equal_fee | pre300 | 1 | undetermined | - | send -0.182 (no interval; p 0.459; mean of burst taus -0.182) | 0.591 (no interval); 0 of 1 bursts without a violation |
| Agave | independent | pre300 | 1 | undetermined | - | cross 0.000 (no interval; p 1; mean of burst taus 0.000); fee 0.704 (no interval; p 0.00186; mean of burst taus 0.704); ties 0.000 (no interval; p 1; mean of burst taus 0.000) | 0.111 (no interval); 0 of 1 bursts without a violation |
| Agave | shared | pre300 | 1 | fee-rule | ties-unordered | cross -0.333 (no interval; p 0.233; mean of burst taus -0.333); fee 0.905 (no interval; p 5.41e-06; mean of burst taus 0.905); ties -0.333 (no interval; p 0.44; mean of burst taus -0.333) | 0.000 (no interval); 1 of 1 bursts without a violation |
| Agave | shared | slot2 | 1 | arrival-rule | forward | cross 0.815 (no interval; p 0.000141; mean of burst taus 0.815); fee 0.369 (no interval; p 0.138; mean of burst taus 0.369); ties 0.833 (no interval; p 0.0139; mean of burst taus 0.833) | 0.296 (no interval); 0 of 1 bursts without a violation |
| AgaveBam | denominator | pre300 | 1 | undetermined | - | limit 0.739 (no interval; p 0.00216; mean of burst taus 0.739); send -0.091 (no interval; p 0.737; mean of burst taus -0.091) | 0.000 (no interval); 1 of 1 bursts without a violation |
| AgaveBam | denominator | slot2 | 1 | undetermined | - | limit 0.739 (no interval; p 0.00216; mean of burst taus 0.739); send -0.364 (no interval; p 0.116; mean of burst taus -0.364) | 0.000 (no interval); 1 of 1 bursts without a violation |
| AgaveBam | equal_fee | slot2 | 2 | arrival-rule | forward | send 0.712 (0.520 to 0.905; p 9.02e-07; mean of burst taus 0.712) | 0.144 (0.048 to 0.240); 0 of 2 bursts without a violation |
| AgaveBam | independent | pre300 | 1 | fee-rule | ties-unordered | cross -0.037 (no interval; p 0.945; mean of burst taus -0.037); fee 0.905 (no interval; p 5.41e-06; mean of burst taus 0.905); ties -0.167 (no interval; p 0.798; mean of burst taus -0.167) | 0.000 (no interval); 1 of 1 bursts without a violation |
| AgaveBam | independent | slot2 | 1 | fee-rule | ties-unordered | cross 0.333 (no interval; p 0.233; mean of burst taus 0.333); fee 0.905 (no interval; p 5.41e-06; mean of burst taus 0.905); ties -0.333 (no interval; p 0.44; mean of burst taus -0.333) | 0.000 (no interval); 1 of 1 bursts without a violation |
| AgaveBam | shared | pre300 | 1 | fee-rule | ties-unordered | cross 0.074 (no interval; p 0.835; mean of burst taus 0.074); fee 0.905 (no interval; p 5.41e-06; mean of burst taus 0.905); ties -0.500 (no interval; p 0.193; mean of burst taus -0.500) | 0.000 (no interval); 1 of 1 bursts without a violation |
| FireBAM | denominator | pre300 | 1 | undetermined | - | limit 0.739 (no interval; p 0.00216; mean of burst taus 0.739); send 0.152 (no interval; p 0.545; mean of burst taus 0.152) | 0.000 (no interval); 1 of 1 bursts without a violation |
| FireBAM | denominator | slot2 | 1 | undetermined | - | limit 0.739 (no interval; p 0.00216; mean of burst taus 0.739); send 0.121 (no interval; p 0.638; mean of burst taus 0.121) | 0.000 (no interval); 1 of 1 bursts without a violation |
| FireBAM | equal_fee | pre300 | 1 | undetermined | - | send 0.485 (no interval; p 0.0311; mean of burst taus 0.485) | 0.258 (no interval); 0 of 1 bursts without a violation |
| FireBAM | equal_fee | slot2 | 2 | undetermined | - | send -0.045 (-1.778 to 1.687; p 0.81; mean of burst taus -0.045) | 0.523 (-0.344 to 1.389); 0 of 2 bursts without a violation |
| FireBAM | independent | pre300 | 1 | fee-rule | ties-unordered | cross -0.037 (no interval; p 0.945; mean of burst taus -0.037); fee 0.905 (no interval; p 5.41e-06; mean of burst taus 0.905); ties 0.500 (no interval; p 0.193; mean of burst taus 0.500) | 0.000 (no interval); 1 of 1 bursts without a violation |
| FireBAM | shared | pre300 | 1 | fee-rule | ties-reverse-arrival | cross -0.407 (no interval; p 0.138; mean of burst taus -0.407); fee 0.905 (no interval; p 5.41e-06; mean of burst taus 0.905); ties -0.833 (no interval; p 0.0139; mean of burst taus -0.833) | 0.000 (no interval); 1 of 1 bursts without a violation |
| FireBAM | shared | slot2 | 1 | undetermined | - | cross -0.444 (no interval; p 0.289; mean of burst taus -0.444); fee 0.926 (no interval; p 0.00317; mean of burst taus 0.926); ties 0.333 (no interval; p 1; mean of burst taus 0.333) | 0.000 (no interval); 1 of 1 bursts without a violation |
| Firedancer | denominator | pre300 | 1 | undetermined | - | limit 0.739 (no interval; p 0.00216; mean of burst taus 0.739); send -0.394 (no interval; p 0.0863; mean of burst taus -0.394) | 0.000 (no interval); 1 of 1 bursts without a violation |
| Firedancer | denominator | slot2 | 1 | undetermined | - | limit 0.000 (no interval; p 1; mean of burst taus 0.000); send 0.848 (no interval; p 1.63e-05; mean of burst taus 0.848) | 0.500 (no interval); 0 of 1 bursts without a violation |
| Firedancer | equal_fee | pre300 | 1 | arrival-rule | reverse | send -1.000 (no interval; p 4.18e-09; mean of burst taus -1.000) | 1.000 (no interval); 0 of 1 bursts without a violation |
| Firedancer | equal_fee | slot2 | 1 | arrival-rule | forward | send 1.000 (no interval; p 4.18e-09; mean of burst taus 1.000) | 0.000 (no interval); 1 of 1 bursts without a violation |
| Firedancer | independent | pre300 | 1 | fee-rule | ties-reverse-arrival | cross 0.074 (no interval; p 0.835; mean of burst taus 0.074); fee 0.905 (no interval; p 5.41e-06; mean of burst taus 0.905); ties -1.000 (no interval; p 0.00154; mean of burst taus -1.000) | 0.000 (no interval); 1 of 1 bursts without a violation |
| Firedancer | independent | slot2 | 1 | arrival-rule | forward | cross 0.852 (no interval; p 3.99e-05; mean of burst taus 0.852); fee -0.168 (no interval; p 0.532; mean of burst taus -0.168); ties 1.000 (no interval; p 0.00154; mean of burst taus 1.000) | 0.593 (no interval); 0 of 1 bursts without a violation |
| Firedancer | shared | pre300 | 1 | fee-rule | ties-unordered | cross 0.074 (no interval; p 0.835; mean of burst taus 0.074); fee 0.905 (no interval; p 5.41e-06; mean of burst taus 0.905); ties -0.667 (no interval; p 0.0633; mean of burst taus -0.667) | 0.000 (no interval); 1 of 1 bursts without a violation |
| Firedancer | shared | slot2 | 1 | undetermined | - | cross 0.630 (no interval; p 0.0053; mean of burst taus 0.630); fee -0.268 (no interval; p 0.294; mean of burst taus -0.268); ties 0.667 (no interval; p 0.0633; mean of burst taus 0.667) | 0.648 (no interval); 0 of 1 bursts without a violation |
| HarmonicAgave | denominator | pre300 | 1 | undetermined | - | limit 0.451 (no interval; p 0.0931; mean of burst taus 0.451); send 0.212 (no interval; p 0.381; mean of burst taus 0.212) | 0.194 (no interval); 0 of 1 bursts without a violation |
| HarmonicAgave | denominator | slot2 | 1 | undetermined | - | limit 0.164 (no interval; p 0.589; mean of burst taus 0.164); send 0.545 (no interval; p 0.0138; mean of burst taus 0.545) | 0.389 (no interval); 0 of 1 bursts without a violation |
| HarmonicAgave | equal_fee | pre300 | 1 | undetermined | - | send -0.121 (no interval; p 0.638; mean of burst taus -0.121) | 0.561 (no interval); 0 of 1 bursts without a violation |
| HarmonicAgave | equal_fee | slot2 | 2 | undetermined | - | send 0.364 (-0.791 to 1.519; p 0.0214; mean of burst taus 0.364) | 0.318 (-0.259 to 0.896); 0 of 2 bursts without a violation |
| HarmonicAgave | independent | pre300 | 1 | undetermined | - | cross 0.222 (no interval; p 0.404; mean of burst taus 0.222); fee 0.469 (no interval; p 0.0531; mean of burst taus 0.469); ties 0.500 (no interval; p 0.193; mean of burst taus 0.500) | 0.241 (no interval); 0 of 1 bursts without a violation |
| HarmonicAgave | independent | slot2 | 1 | undetermined | - | cross -0.185 (no interval; p 0.462; mean of burst taus -0.185); fee 0.034 (no interval; p 0.945; mean of burst taus 0.034); ties -0.500 (no interval; p 0.193; mean of burst taus -0.500) | 0.481 (no interval); 0 of 1 bursts without a violation |
| HarmonicAgave | shared | pre300 | 1 | fee-rule | ties-unordered | cross 0.111 (no interval; p 0.724; mean of burst taus 0.111); fee 0.804 (no interval; p 0.000189; mean of burst taus 0.804); ties 0.333 (no interval; p 0.44; mean of burst taus 0.333) | 0.056 (no interval); 0 of 1 bursts without a violation |
| HarmonicAgave | shared | slot2 | 1 | undetermined | - | cross -0.074 (no interval; p 0.832; mean of burst taus -0.074); fee 0.670 (no interval; p 0.00342; mean of burst taus 0.670); ties 0.667 (no interval; p 0.0633; mean of burst taus 0.667) | 0.130 (no interval); 0 of 1 bursts without a violation |
| HarmonicFiredancer | denominator | slot2 | 1 | undetermined | - | limit 0.369 (no interval; p 0.18; mean of burst taus 0.369); send -0.030 (no interval; p 0.947; mean of burst taus -0.030) | 0.250 (no interval); 0 of 1 bursts without a violation |
| HarmonicFiredancer | equal_fee | pre300 | 1 | undetermined | - | send 0.576 (no interval; p 0.00876; mean of burst taus 0.576) | 0.212 (no interval); 0 of 1 bursts without a violation |
| HarmonicFiredancer | equal_fee | slot2 | 2 | undetermined | - | send 0.515 (-0.255 to 1.285; p 0.000786; mean of burst taus 0.515) | 0.242 (-0.143 to 0.627); 0 of 2 bursts without a violation |
| HarmonicFiredancer | independent | pre300 | 1 | fee-rule | ties-unordered | cross -0.185 (no interval; p 0.521; mean of burst taus -0.185); fee 0.804 (no interval; p 0.000189; mean of burst taus 0.804); ties 0.333 (no interval; p 0.44; mean of burst taus 0.333) | 0.056 (no interval); 0 of 1 bursts without a violation |
| HarmonicFiredancer | shared | pre300 | 1 | undetermined | - | cross 0.148 (no interval; p 0.621; mean of burst taus 0.148); fee 0.670 (no interval; p 0.00342; mean of burst taus 0.670); ties 0.167 (no interval; p 0.798; mean of burst taus 0.167) | 0.130 (no interval); 0 of 1 bursts without a violation |
| HarmonicFiredancer | shared | slot2 | 1 | fee-rule | ties-unordered | cross -0.481 (no interval; p 0.0686; mean of burst taus -0.481); fee 0.838 (no interval; p 7.03e-05; mean of burst taus 0.838); ties -0.167 (no interval; p 0.798; mean of burst taus -0.167) | 0.037 (no interval); 0 of 1 bursts without a violation |
| JitoLabs | denominator | pre300 | 1 | undetermined | - | limit 0.739 (no interval; p 0.00216; mean of burst taus 0.739); send -0.061 (no interval; p 0.841; mean of burst taus -0.061) | 0.000 (no interval); 1 of 1 bursts without a violation |
| JitoLabs | denominator | slot2 | 1 | undetermined | - | limit 0.287 (no interval; p 0.31; mean of burst taus 0.287); send 0.121 (no interval; p 0.638; mean of burst taus 0.121) | 0.306 (no interval); 0 of 1 bursts without a violation |
| JitoLabs | equal_fee | pre300 | 1 | undetermined | - | send -0.455 (no interval; p 0.0447; mean of burst taus -0.455) | 0.727 (no interval); 0 of 1 bursts without a violation |
| JitoLabs | equal_fee | slot2 | 1 | arrival-rule | forward | send 1.000 (no interval; p 4.18e-09; mean of burst taus 1.000) | 0.000 (no interval); 1 of 1 bursts without a violation |
| JitoLabs | independent | pre300 | 1 | undetermined | - | cross 0.037 (no interval; p 0.933; mean of burst taus 0.037); fee 0.302 (no interval; p 0.233; mean of burst taus 0.302); ties -0.167 (no interval; p 0.798; mean of burst taus -0.167) | 0.333 (no interval); 0 of 1 bursts without a violation |
| JitoLabs | independent | slot2 | 1 | undetermined | - | cross -0.222 (no interval; p 0.389; mean of burst taus -0.222); fee 0.235 (no interval; p 0.365; mean of burst taus 0.235); ties 0.500 (no interval; p 0.193; mean of burst taus 0.500) | 0.370 (no interval); 0 of 1 bursts without a violation |
| JitoLabs | shared | pre300 | 1 | fee-rule | ties-unordered | cross -0.519 (no interval; p 0.0531; mean of burst taus -0.519); fee 0.905 (no interval; p 5.41e-06; mean of burst taus 0.905); ties -0.333 (no interval; p 0.44; mean of burst taus -0.333) | 0.000 (no interval); 1 of 1 bursts without a violation |
| JitoLabs | shared | slot2 | 1 | fee-rule | ties-unordered | cross 0.481 (no interval; p 0.0749; mean of burst taus 0.481); fee 0.905 (no interval; p 5.41e-06; mean of burst taus 0.905); ties -0.333 (no interval; p 0.44; mean of burst taus -0.333) | 0.000 (no interval); 1 of 1 bursts without a violation |
| Rakurai | denominator | pre300 | 1 | undetermined | - | limit 0.739 (no interval; p 0.00216; mean of burst taus 0.739); send -0.182 (no interval; p 0.459; mean of burst taus -0.182) | 0.000 (no interval); 1 of 1 bursts without a violation |
| Rakurai | denominator | slot2 | 1 | undetermined | - | limit 0.410 (no interval; p 0.132; mean of burst taus 0.410); send 0.667 (no interval; p 0.0018; mean of burst taus 0.667) | 0.222 (no interval); 0 of 1 bursts without a violation |
| Rakurai | equal_fee | pre300 | 1 | undetermined | - | send 0.273 (no interval; p 0.25; mean of burst taus 0.273) | 0.364 (no interval); 0 of 1 bursts without a violation |
| Rakurai | equal_fee | slot2 | 1 | arrival-rule | forward | send 0.949 (no interval; p 1.01e-05; mean of burst taus 0.949) | 0.026 (no interval); 0 of 1 bursts without a violation |
| Rakurai | independent | pre300 | 1 | fee-rule | ties-unordered | cross -0.037 (no interval; p 0.943; mean of burst taus -0.037); fee 0.771 (no interval; p 0.000444; mean of burst taus 0.771); ties -0.333 (no interval; p 0.44; mean of burst taus -0.333) | 0.074 (no interval); 0 of 1 bursts without a violation |
| Rakurai | independent | slot2 | 1 | undetermined | - | cross 0.593 (no interval; p 0.00548; mean of burst taus 0.593); fee -0.067 (no interval; p 0.835; mean of burst taus -0.067); ties 0.667 (no interval; p 0.0633; mean of burst taus 0.667) | 0.537 (no interval); 0 of 1 bursts without a violation |
| Rakurai | shared | pre300 | 1 | fee-rule | ties-unordered | cross 0.111 (no interval; p 0.729; mean of burst taus 0.111); fee 0.905 (no interval; p 5.41e-06; mean of burst taus 0.905); ties 0.167 (no interval; p 0.798; mean of burst taus 0.167) | 0.000 (no interval); 1 of 1 bursts without a violation |
| Rakurai | shared | slot2 | 1 | undetermined | - | cross 0.704 (no interval; p 0.00177; mean of burst taus 0.704); fee 0.034 (no interval; p 0.945; mean of burst taus 0.034); ties 0.167 (no interval; p 0.798; mean of burst taus 0.167) | 0.481 (no interval); 0 of 1 bursts without a violation |
<!-- itb:end pilot-cells -->

Tau is Kendall tau-b against block position, pooled over the bursts of the cell, with a jackknife interval over bursts. A cell with one burst has no interval. With two bursts the interval uses one degree of freedom and may run past the range of tau. The violated pair share counts pairs with a different predicted position that landed in the other order.

Before the window, 9 of the 16 different-fee cells had no pair of different fee out of fee order. At the start of slot 2, 3 of 12 had none. The only pre-window equal-fee burst of Firedancer landed in exact reverse send order (tau send -1.000), the order its code predicts ([README.md](README.md#two-hypotheses-from-the-code), hypothesis H3). One burst per cell gives no verdict on either observation.

### 5.3 Builder against its base

<!-- itb:begin pilot-pairs -->
| Pair | Timing | Statistic | Strata | Mean difference | p | TOST p | Label test | Form |
|---|---|---|---|---|---|---|---|---|
| AgaveBam vs JitoLabs | pre300 | fee | 2 | 0.302 | 1 | 0.603 | exact over 4 | undetermined |
| AgaveBam vs JitoLabs | pre300 | cross | 2 | 0.259 | 1 | 0.556 | exact over 4 | undetermined |
| AgaveBam vs JitoLabs | slot2 | fee | 1 | 0.670 | 1 | 1 | exact over 2 | undetermined |
| AgaveBam vs JitoLabs | slot2 | cross | 1 | 0.556 | 1 | 1 | exact over 2 | undetermined |
| FireBAM vs Firedancer | pre300 | fee | 2 | 0.000 | 1 | 0 | exact over 4 | builder-does-not-change-order |
| FireBAM vs Firedancer | pre300 | cross | 2 | -0.296 | 0.5 | 0.653 | exact over 4 | undetermined |
| FireBAM vs Firedancer | slot2 | fee | 1 | 1.194 | 1 | 1 | exact over 2 | undetermined |
| FireBAM vs Firedancer | slot2 | cross | 1 | -1.074 | 1 | 1 | exact over 2 | undetermined |
| HarmonicAgave vs Agave | pre300 | fee | 2 | -0.168 | 0.5 | 0.356 | exact over 4 | undetermined |
| HarmonicAgave vs Agave | pre300 | cross | 2 | 0.333 | 0.5 | 0.779 | exact over 4 | undetermined |
| HarmonicAgave vs Agave | slot2 | fee | 1 | 0.302 | 1 | 1 | exact over 2 | undetermined |
| HarmonicAgave vs Agave | slot2 | cross | 1 | -0.889 | 1 | 1 | exact over 2 | undetermined |
| HarmonicFiredancer vs Firedancer | pre300 | fee | 2 | -0.168 | 0.5 | 0.356 | exact over 4 | undetermined |
| HarmonicFiredancer vs Firedancer | pre300 | cross | 2 | -0.093 | 1 | 0.318 | exact over 4 | undetermined |
| HarmonicFiredancer vs Firedancer | slot2 | fee | 1 | 1.106 | 1 | 1 | exact over 2 | undetermined |
| HarmonicFiredancer vs Firedancer | slot2 | cross | 1 | -1.111 | 1 | 1 | exact over 2 | undetermined |
<!-- itb:end pilot-pairs -->

A stratum is one round and arm with a burst of both classes. FireBAM against Firedancer before the window reads "builder-does-not-change-order" on tau fee. Both classes gave tau fee 0.905 in both strata, every pair of different fee in fee order, so the difference is zero with zero spread. With a standard error of zero the TOST of the code (`stats.tost_p`) returns p 0 when the difference lies inside plus or minus delta; the analysis plan does not state that rule, and the [campaign addendum, sections 2 and 6](prereg/CAMPAIGN-ADDENDUM.md) states it for the campaign with this pair as its example. Two identical strata carry little weight; the campaign verdict for this pair stands on its own strata.

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

The arrival estimate is the send offset from the first-shred moment of the first slot plus half the round-trip time of the same connection ([DESIGN.md](DESIGN.md#the-path-from-the-sender-to-the-executing-node)). The pre-window band takes arrivals 500 to 200 ms before the first slot, and the slot-2 band 100 ms either side of the start of slot 2.

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
| Load by | Quartile | Mean load of the burst's blocks | Bursts | tau fee, independent and shared | tau send, equal fee | tau send, equal fee, Agave, pre300 |
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
| Arm | tau | Pilot bursts | sigma (residual) | Raw variance by cell | Minimum bursts | Campaign bursts per class and cell | Equivalence reachable at the pilot's spread |
|---|---|---|---|---|---|---|---|
| independent | fee | 13 | 0.332 | pre300 0.050 (8 bursts); slot2 0.183 (5 bursts) | 72 | 8 | no |
| independent | cross | 13 | 0.375 | pre300 0.013 (8 bursts); slot2 0.224 (5 bursts) | 90 | 8 | no |
| shared | fee | 15 | 0.360 | pre300 0.007 (8 bursts); slot2 0.219 (7 bursts) | 84 | 8 | no |
| shared | cross | 15 | 0.462 | pre300 0.076 (8 bursts); slot2 0.307 (7 bursts) | 134 | 8 | no |
| equal_fee | send | 18 | 0.533 | pre300 0.312 (7 bursts); slot2 0.146 (11 bursts) | 177 | 8 | no |
| denominator | limit | 15 | 0.195 | pre300 0.064 (7 bursts); slot2 0.080 (8 bursts) | 28 | 8 | no |

From 68 pilot bursts, 61 kept; alpha_e 0.000521, power per tau 0.90, delta 0.20.
<!-- itb:end minimum -->

The minimum is the number of bursts per class and cell that an equivalence verdict needs at the spread the pilot showed (analysis plan, section 5). The campaign has 8 per class and cell, and every arm needs at least 28, so at the pilot's spread no cell is expected to reach a form that rests on a TOST, such as "no rule visible". A spread near zero is the exception, since the TOST of the code passes on a standard error of zero ([campaign addendum, section 2](prereg/CAMPAIGN-ADDENDUM.md)). Forms with a significant tau do not depend on this minimum. The minimum is part of the campaign manifest, which goes on chain before the first campaign probe.

## 6. Campaign

The campaign measures the panel over four epochs from 1071 with 8 bursts per class and cell, plus 64 control-path bursts. Verdicts run through the Holm families of the analysis plan. The [campaign addendum](prereg/CAMPAIGN-ADDENDUM.md) goes on chain with the campaign manifest and states what the plan leaves to the code: the exclusion reasons, the hypotheses H3 and H4, lost epoch indexes and repeated bursts, the builder label and the control path.

The campaign manifest `8e7d834a...` went on chain at 01:21:59 UTC on 2026-10-28, in slot 462288545 (`data/prereg-anchors.json`). These code changes came after it:

- `73f3d20` makes the sender sleep to a window in steps and skip a burst it wakes for too late.
- `cf7c56a` fixes how the campaign runner reads the spend journal (section 9), which `tests/test_campaign_sh.py` replays on the lines of that start.
- `6fdceca` adds a leader correction to the aim and keeps the first shreds from the aim's anchor to slot 2 in `burst_end` (raw format version 3).
- `c062eb8` settles stale bookings of an earlier run from a listing of the payers' history on chain. `c3ae1f6` retries error -32019 and stops the listing at a short page, and `18a543c` lists the chain once per start ([REPORT.md, section 6](REPORT.md#6-what-went-wrong-in-the-campaign)). The campaign runs from 12:15 UTC on 2026-10-29 onward ran on `18a543c`.
- `3f012d5` makes collection take the slot of each probe from the payer listing and ask `getBlock` again when it answers null.
- `cd50678` changes the balance check of the payers at a run's start. It applies from the end of the campaign, the close of 2026-11-02, and no campaign run ran on it.
- `9f36bf2` names the rounds of an epoch lost once the epoch passes and keeps its epoch index, and `1275cf5` tests that hand-over after a failed run.
- `662b7db` adds the campaign data and makes the spend table count the closing transactions that `probe close` sends outside a run.
- The commit that splits the report into REPORT.md and this file adds the table of forms and a check that each generated table stands in exactly one of the two files. It also moves the design and running sections of the README into DESIGN.md and RUNNING.md, and code comments that named the old places now name the new files.

The other five commits after the anchor touch no code outside `tests/`. None of these commits touches a file the manifest pins (`git diff 4cb1012 HEAD` over the six pinned files lists none), so the pinned text keeps the bytes it was hashed from, and the bands and targets of the addendum stay as they were.

The pilot and the four test runs of 2026-10-28 put 98 of 116 bursts in their timing band, and [logs/aim-diagnosis-20261028.txt](logs/aim-diagnosis-20261028.txt) splits the deviation of each burst into its parts. Eight of the 18 misses aimed from an anchor tens of slots old while the slot stream lagged. Two came from a distant leader: the first shreds of `5Cchr1...` (QUIC RTT 162-165 ms) reached the RPC node about 110 ms after the prediction, since the slot steps are medians over all leaders. The leader correction is the median, over that leader's earlier handoff windows in the stream the probe already holds, of the first slot's node time minus its prediction from the window before. Its two numbers come from a firstShredReceived stream of the public node ([logs/shreds-mainnet-20261028T040857Z.jsonl](logs/shreds-mainnet-20261028T040857Z.jsonl)), 75 minutes from 04:09 UTC on 2026-10-28, with 5089 handoff windows of 534 leaders; [logs/leader-correction-20261028.txt](logs/leader-correction-20261028.txt) gives the method, the tables, the replay below and the mutants of the tests. The median of 3 earlier windows cut the mean error of the next window from 36.9 to 18.6 ms, and 10 windows cut it from 35.2 to 15.8 ms. One or two windows pushed a window that was within 150 ms of its prediction past that mark in 0.18% and 0.22% of cases, three windows in 0.05%, so the correction waits for 3. Leader medians over at least 3 windows ran from -46 to 205 ms (`5Cchr1...` 109 ms over 62 windows). Single windows reached -551 and 530 ms, and the bound of 250 ms lies between the two.

Replayed on the 116 bursts with the correction taken from the same leader's other bursts at an anchor up to 4 slots old, 101 of 116 fall in the band, and 100 when only earlier bursts count. Misses 93 and 150 move to 0.5 and 5.0 ms from the band centre, while 129 stays out at -102.6 ms. Two other misses come into the band and one burst leaves it. The dry run `dry-run-mainnet-20261028T043400Z` on commit `6fdceca` took 12 windows of `5Cchr1...` and `DRpbCB...` and put all 12 in the band. Its corrections at signing were 102 to 112 ms for `5Cchr1...` over 5 to 14 windows and 49 to 61 ms for `DRpbCB...` over 3 to 18, and the six bursts of `5Cchr1...` landed between -20 and 19.5 ms from the band centre. The stale anchor, behind 8 of the misses, is left as it was (option C of the diagnosis).

### 6.1 Bursts left out of the order tests

<!-- itb:in-report campaign-exclusions -->
This table stands in [REPORT.md, section 4](REPORT.md#4-campaign-results).

### 6.2 Verdicts by class and cell

Hypotheses H3 and H4 take tau send of the equal-fee arm before the window under the rules of [campaign addendum, section 3](prereg/CAMPAIGN-ADDENDUM.md). The other classes stand beside them for comparison, without a judgement on either hypothesis.

<!-- itb:in-report campaign-hypotheses -->
The table of H3 and H4 stands in [REPORT.md, section 4.1](REPORT.md#41-hypotheses-h3-and-h4), and the table below gives every class and cell.

<!-- itb:begin campaign-cells -->
| Class | Arm | Timing | Bursts | Form | Detail | tau (95% CI; p) | Violated pair share (95% CI) |
|---|---|---|---|---|---|---|---|
| Agave | denominator | pre300 | 6 | divides | - | limit 0.636 (0.429 to 0.843; p 1.85e-11; mean of burst taus 0.636); send 0.056 (-0.154 to 0.265; p 0.558; mean of burst taus 0.056) | 0.069 (-0.071 to 0.210); 4 of 6 bursts without a violation |
| Agave | denominator | slot2 | 8 | undetermined | - | limit 0.185 (0.052 to 0.317; p 0.0441; mean of burst taus 0.185); send 0.477 (0.287 to 0.667; p 2.9e-10; mean of burst taus 0.477) | 0.375 (0.285 to 0.465); 0 of 8 bursts without a violation |
| Agave | equal_fee | pre300 | 7 | undetermined | - | send 0.095 (-0.085 to 0.275; p 0.266; mean of burst taus 0.095) | 0.452 (0.362 to 0.542); 0 of 7 bursts without a violation |
| Agave | equal_fee | slot2 | 6 | arrival-rule | forward | send 1.000 (1.000 to 1.000; p 1.66e-52; mean of burst taus 1.000) | 0.000 (0.000 to 0.000); 6 of 6 bursts without a violation |
| Agave | independent | pre300 | 8 | fee-rule | ties-unordered | cross -0.051 (-0.320 to 0.218; p 0.549; mean of burst taus -0.051); fee 0.440 (0.334 to 0.545; p 6.44e-08; mean of burst taus 0.440); ties -0.062 (-0.341 to 0.216; p 0.645; mean of burst taus -0.062) | 0.257 (0.199 to 0.315); 0 of 8 bursts without a violation |
| Agave | independent | slot2 | 7 | arrival-rule | forward | cross 0.317 (0.151 to 0.484; p 0.000302; mean of burst taus 0.317); fee 0.029 (-0.309 to 0.366; p 0.768; mean of burst taus 0.029); ties 0.286 (-0.044 to 0.615; p 0.0226; mean of burst taus 0.286) | 0.484 (0.298 to 0.671); 0 of 7 bursts without a violation |
| Agave | shared | pre300 | 6 | fee-rule | ties-unordered | cross 0.031 (-0.307 to 0.369; p 0.795; mean of burst taus 0.031); fee 0.905 (0.905 to 0.905; p 7.85e-34; mean of burst taus 0.905); ties -0.056 (-0.319 to 0.208; p 0.75; mean of burst taus -0.056) | 0.000 (0.000 to 0.000); 6 of 6 bursts without a violation |
| Agave | shared | slot2 | 5 | mixed-rule | - | cross 0.600 (0.166 to 1.034; p 1.85e-09; mean of burst taus 0.600); fee 0.422 (-0.041 to 0.885; p 4.7e-05; mean of burst taus 0.422); ties 0.700 (0.430 to 0.970; p 4.82e-07; mean of burst taus 0.700) | 0.267 (0.011 to 0.523); 1 of 5 bursts without a violation |
| AgaveBam | denominator | pre300 | 6 | divides | - | limit 0.739 (0.739 to 0.739; p 3.21e-18; mean of burst taus 0.739); send -0.131 (-0.506 to 0.243; p 0.154; mean of burst taus -0.131) | 0.000 (0.000 to 0.000); 6 of 6 bursts without a violation |
| AgaveBam | denominator | slot2 | 5 | divides | - | limit 0.739 (0.739 to 0.739; p 2.97e-15; mean of burst taus 0.739); send -0.158 (-0.363 to 0.047; p 0.118; mean of burst taus -0.158) | 0.000 (0.000 to 0.000); 5 of 5 bursts without a violation |
| AgaveBam | equal_fee | pre300 | 8 | undetermined | - | send -0.011 (-0.289 to 0.266; p 0.904; mean of burst taus -0.011) | 0.506 (0.367 to 0.644); 0 of 8 bursts without a violation |
| AgaveBam | equal_fee | slot2 | 6 | arrival-rule | forward | send 0.773 (0.688 to 0.857; p 6.95e-22; mean of burst taus 0.773) | 0.114 (0.071 to 0.156); 0 of 6 bursts without a violation |
| AgaveBam | independent | pre300 | 7 | fee-rule | ties-unordered | cross 0.058 (-0.188 to 0.304; p 0.572; mean of burst taus 0.058); fee 0.895 (0.880 to 0.910; p 5.82e-37; mean of burst taus 0.895); ties 0.119 (-0.128 to 0.366; p 0.375; mean of burst taus 0.119) | 0.005 (-0.003 to 0.014); 5 of 7 bursts without a violation |
| AgaveBam | independent | slot2 | 4 | fee-rule | ties-unordered | cross 0.222 (0.049 to 0.396; p 0.086; mean of burst taus 0.222); fee 0.796 (0.620 to 0.972; p 1.37e-14; mean of burst taus 0.796); ties 0.125 (-0.209 to 0.459; p 0.515; mean of burst taus 0.125) | 0.060 (-0.037 to 0.158); 0 of 4 bursts without a violation |
| AgaveBam | shared | pre300 | 5 | fee-rule | ties-unordered | cross -0.089 (-0.334 to 0.156; p 0.467; mean of burst taus -0.089); fee 0.905 (0.905 to 0.905; p 2.9e-28; mean of burst taus 0.905); ties -0.167 (-0.313 to -0.020; p 0.294; mean of burst taus -0.167) | 0.000 (0.000 to 0.000); 5 of 5 bursts without a violation |
| AgaveBam | shared | slot2 | 2 | fee-rule | ties-reverse-arrival | cross -0.426 (-5.367 to 4.515; p 0.0223; mean of burst taus -0.426); fee 0.905 (0.905 to 0.905; p 1.46e-11; mean of burst taus 0.905); ties -0.583 (-3.760 to 2.593; p 0.0142; mean of burst taus -0.583) | 0.000 (0.000 to 0.000); 2 of 2 bursts without a violation |
| FireBAM | denominator | pre300 | 5 | divides | - | limit 0.739 (0.739 to 0.739; p 2.97e-15; mean of burst taus 0.739); send 0.024 (-0.234 to 0.283; p 0.831; mean of burst taus 0.024) | 0.000 (0.000 to 0.000); 5 of 5 bursts without a violation |
| FireBAM | denominator | slot2 | 6 | divides | - | limit 0.656 (0.446 to 0.867; p 2.18e-12; mean of burst taus 0.656); send 0.030 (-0.271 to 0.331; p 0.759; mean of burst taus 0.030) | 0.056 (-0.087 to 0.198); 5 of 6 bursts without a violation |
| FireBAM | equal_fee | pre300 | 6 | undetermined | - | send -0.061 (-0.482 to 0.361; p 0.521; mean of burst taus -0.061) | 0.530 (0.319 to 0.741); 0 of 6 bursts without a violation |
| FireBAM | equal_fee | slot2 | 6 | undetermined | - | send 0.035 (-0.425 to 0.495; p 0.717; mean of burst taus 0.035) | 0.482 (0.252 to 0.712); 0 of 6 bursts without a violation |
| FireBAM | independent | pre300 | 6 | fee-rule | ties-unordered | cross 0.056 (-0.209 to 0.320; p 0.619; mean of burst taus 0.056); fee 0.860 (0.817 to 0.902; p 5.11e-27; mean of burst taus 0.860); ties -0.028 (-0.367 to 0.312; p 0.915; mean of burst taus -0.028) | 0.025 (0.001 to 0.048); 2 of 6 bursts without a violation |
| FireBAM | independent | slot2 | 8 | fee-rule | ties-unordered | cross -0.093 (-0.263 to 0.078; p 0.316; mean of burst taus -0.093); fee 0.800 (0.671 to 0.929; p 2e-28; mean of burst taus 0.800); ties -0.167 (-0.516 to 0.183; p 0.166; mean of burst taus -0.167) | 0.058 (-0.014 to 0.129); 2 of 8 bursts without a violation |
| FireBAM | shared | pre300 | 4 | fee-rule | ties-unordered | cross 0.083 (-0.005 to 0.172; p 0.548; mean of burst taus 0.083); fee 0.905 (0.905 to 0.905; p 1.07e-22; mean of burst taus 0.905); ties -0.208 (-1.341 to 0.925; p 0.241; mean of burst taus -0.208) | 0.000 (0.000 to 0.000); 4 of 4 bursts without a violation |
| FireBAM | shared | slot2 | 6 | fee-rule | ties-unordered | cross 0.025 (-0.348 to 0.397; p 0.84; mean of burst taus 0.025); fee 0.905 (0.905 to 0.905; p 7.85e-34; mean of burst taus 0.905); ties 0.139 (-0.440 to 0.718; p 0.338; mean of burst taus 0.139) | 0.000 (0.000 to 0.000); 6 of 6 bursts without a violation |
| Firedancer | denominator | pre300 | 8 | divides | - | limit 0.739 (0.739 to 0.739; p 3.76e-24; mean of burst taus 0.739); send -0.352 (-0.486 to -0.219; p 5.07e-06; mean of burst taus -0.352) | 0.000 (0.000 to 0.000); 8 of 8 bursts without a violation |
| Firedancer | denominator | slot2 | 6 | divides | - | limit 0.636 (0.372 to 0.900; p 1.85e-11; mean of burst taus 0.636); send -0.202 (-0.743 to 0.339; p 0.0266; mean of burst taus -0.202) | 0.069 (-0.109 to 0.248); 5 of 6 bursts without a violation |
| Firedancer | equal_fee | pre300 | 8 | arrival-rule | reverse | send -1.000 (-1.000 to -1.000; p 7.22e-70; mean of burst taus -1.000) | 1.000 (1.000 to 1.000); 0 of 8 bursts without a violation |
| Firedancer | equal_fee | slot2 | 5 | undetermined | - | send 0.193 (-0.646 to 1.033; p 0.0808; mean of burst taus 0.096) | 0.403 (-0.016 to 0.823); 1 of 5 bursts without a violation |
| Firedancer | independent | pre300 | 8 | fee-rule | ties-reverse-arrival | cross -0.032 (-0.358 to 0.293; p 0.745; mean of burst taus -0.032); fee 0.905 (0.905 to 0.905; p 5.74e-45; mean of burst taus 0.905); ties -0.729 (-0.911 to -0.548; p 1.43e-11; mean of burst taus -0.729) | 0.000 (0.000 to 0.000); 8 of 8 bursts without a violation |
| Firedancer | independent | slot2 | 8 | fee-rule | ties-reverse-arrival | cross 0.065 (-0.216 to 0.346; p 0.499; mean of burst taus 0.065); fee 0.905 (0.905 to 0.905; p 5.74e-45; mean of burst taus 0.905); ties -0.729 (-0.952 to -0.507; p 1.43e-11; mean of burst taus -0.729) | 0.000 (0.000 to 0.000); 8 of 8 bursts without a violation |
| Firedancer | shared | pre300 | 7 | fee-rule | ties-reverse-arrival | cross -0.085 (-0.333 to 0.164; p 0.406; mean of burst taus -0.085); fee 0.905 (0.905 to 0.905; p 2.12e-39; mean of burst taus 0.905); ties -0.905 (-1.026 to -0.783; p 1.43e-16; mean of burst taus -0.905) | 0.000 (0.000 to 0.000); 7 of 7 bursts without a violation |
| Firedancer | shared | slot2 | 6 | fee-rule | ties-reverse-arrival | cross 0.080 (-0.190 to 0.350; p 0.47; mean of burst taus 0.080); fee 0.905 (0.905 to 0.905; p 7.85e-34; mean of burst taus 0.905); ties -0.917 (-1.063 to -0.770; p 8.28e-15; mean of burst taus -0.917) | 0.000 (0.000 to 0.000); 6 of 6 bursts without a violation |
| HarmonicAgave | denominator | pre300 | 6 | undetermined | - | limit 0.150 (-0.021 to 0.322; p 0.161; mean of burst taus 0.150); send 0.081 (-0.178 to 0.340; p 0.387; mean of burst taus 0.081) | 0.398 (0.282 to 0.514); 0 of 6 bursts without a violation |
| HarmonicAgave | denominator | slot2 | 7 | divides | - | limit 0.463 (0.217 to 0.709; p 7.17e-07; mean of burst taus 0.463); send 0.108 (-0.148 to 0.365; p 0.205; mean of burst taus 0.108) | 0.187 (0.020 to 0.353); 2 of 7 bursts without a violation |
| HarmonicAgave | equal_fee | pre300 | 7 | undetermined | - | send -0.047 (-0.164 to 0.071; p 0.606; mean of burst taus -0.023) | 0.523 (0.464 to 0.582); 0 of 7 bursts without a violation |
| HarmonicAgave | equal_fee | slot2 | 6 | arrival-rule | forward | send 0.682 (0.555 to 0.809; p 2.6e-16; mean of burst taus 0.682) | 0.159 (0.096 to 0.222); 0 of 6 bursts without a violation |
| HarmonicAgave | independent | pre300 | 8 | undetermined | - | cross -0.060 (-0.222 to 0.102; p 0.471; mean of burst taus -0.060); fee 0.214 (0.105 to 0.322; p 0.0108; mean of burst taus 0.214); ties 0.167 (-0.057 to 0.390; p 0.166; mean of burst taus 0.167) | 0.382 (0.322 to 0.442); 0 of 8 bursts without a violation |
| HarmonicAgave | independent | slot2 | 6 | undetermined | - | cross 0.080 (-0.233 to 0.394; p 0.421; mean of burst taus 0.080); fee 0.173 (-0.195 to 0.541; p 0.0767; mean of burst taus 0.173); ties 0.028 (-0.273 to 0.329; p 0.915; mean of burst taus 0.028) | 0.404 (0.201 to 0.608); 0 of 6 bursts without a violation |
| HarmonicAgave | shared | pre300 | 4 | fee-rule | ties-unordered | cross -0.046 (-0.384 to 0.292; p 0.747; mean of burst taus -0.046); fee 0.779 (0.626 to 0.932; p 8.37e-14; mean of burst taus 0.779); ties -0.042 (-0.705 to 0.621; p 0.897; mean of burst taus -0.042) | 0.069 (-0.015 to 0.154); 1 of 4 bursts without a violation |
| HarmonicAgave | shared | slot2 | 7 | fee-rule | ties-unordered | cross 0.180 (-0.033 to 0.393; p 0.0668; mean of burst taus 0.180); fee 0.766 (0.674 to 0.858; p 2.99e-22; mean of burst taus 0.766); ties -0.048 (-0.325 to 0.230; p 0.768; mean of burst taus -0.048) | 0.077 (0.026 to 0.128); 1 of 7 bursts without a violation |
| HarmonicFiredancer | denominator | pre300 | 8 | divides | - | limit 0.667 (0.497 to 0.837; p 8.06e-17; mean of burst taus 0.667); send 0.045 (-0.114 to 0.205; p 0.578; mean of burst taus 0.045) | 0.049 (-0.066 to 0.164); 7 of 8 bursts without a violation |
| HarmonicFiredancer | denominator | slot2 | 7 | undetermined | - | limit 0.123 (-0.163 to 0.409; p 0.216; mean of burst taus 0.123); send -0.121 (-0.290 to 0.048; p 0.154; mean of burst taus -0.121) | 0.417 (0.223 to 0.610); 0 of 7 bursts without a violation |
| HarmonicFiredancer | equal_fee | pre300 | 6 | undetermined | - | send 0.187 (-0.225 to 0.599; p 0.0407; mean of burst taus 0.187) | 0.407 (0.201 to 0.613); 0 of 6 bursts without a violation |
| HarmonicFiredancer | equal_fee | slot2 | 7 | arrival-rule | forward | send 0.647 (0.538 to 0.756; p 4.19e-16; mean of burst taus 0.644) | 0.176 (0.122 to 0.231); 0 of 7 bursts without a violation |
| HarmonicFiredancer | independent | pre300 | 8 | fee-rule | ties-unordered | cross -0.032 (-0.365 to 0.300; p 0.742; mean of burst taus -0.032); fee 0.737 (0.637 to 0.837; p 6.67e-23; mean of burst taus 0.737); ties 0.167 (0.000 to 0.333; p 0.166; mean of burst taus 0.167) | 0.093 (0.037 to 0.148); 1 of 8 bursts without a violation |
| HarmonicFiredancer | independent | slot2 | 7 | undetermined | - | cross -0.217 (-0.363 to -0.071; p 0.013; mean of burst taus -0.217); fee 0.168 (-0.062 to 0.397; p 0.0636; mean of burst taus 0.168); ties -0.119 (-0.424 to 0.186; p 0.375; mean of burst taus -0.119) | 0.407 (0.280 to 0.534); 0 of 7 bursts without a violation |
| HarmonicFiredancer | shared | pre300 | 7 | fee-rule | ties-unordered | cross 0.217 (-0.072 to 0.506; p 0.0261; mean of burst taus 0.217); fee 0.727 (0.646 to 0.809; p 1.45e-19; mean of burst taus 0.727); ties 0.024 (-0.388 to 0.436; p 0.922; mean of burst taus 0.024) | 0.098 (0.053 to 0.143); 0 of 7 bursts without a violation |
| HarmonicFiredancer | shared | slot2 | 4 | fee-rule | ties-unordered | cross 0.000 (-0.357 to 0.357; p 1; mean of burst taus 0.000); fee 0.771 (0.673 to 0.868; p 1.97e-13; mean of burst taus 0.771); ties -0.167 (-0.473 to 0.140; p 0.362; mean of burst taus -0.167) | 0.074 (0.020 to 0.128); 0 of 4 bursts without a violation |
| JitoLabs | denominator | pre300 | 8 | divides | - | limit 0.385 (0.112 to 0.657; p 1.48e-05; mean of burst taus 0.385); send 0.042 (-0.172 to 0.255; p 0.612; mean of burst taus 0.042) | 0.240 (0.055 to 0.424); 3 of 8 bursts without a violation |
| JitoLabs | denominator | slot2 | 6 | undetermined | - | limit 0.157 (0.023 to 0.292; p 0.142; mean of burst taus 0.157); send 0.207 (-0.074 to 0.488; p 0.023; mean of burst taus 0.207) | 0.394 (0.302 to 0.485); 0 of 6 bursts without a violation |
| JitoLabs | equal_fee | pre300 | 7 | undetermined | - | send 0.160 (-0.119 to 0.439; p 0.0583; mean of burst taus 0.160) | 0.420 (0.280 to 0.560); 0 of 7 bursts without a violation |
| JitoLabs | equal_fee | slot2 | 8 | arrival-rule | forward | send 1.000 (1.000 to 1.000; p 7.22e-70; mean of burst taus 1.000) | 0.000 (0.000 to 0.000); 8 of 8 bursts without a violation |
| JitoLabs | independent | pre300 | 8 | fee-rule | ties-unordered | cross -0.014 (-0.224 to 0.196; p 0.886; mean of burst taus -0.014); fee 0.419 (0.289 to 0.548; p 2.89e-07; mean of burst taus 0.419); ties -0.083 (-0.399 to 0.233; p 0.519; mean of burst taus -0.083) | 0.269 (0.197 to 0.340); 0 of 8 bursts without a violation |
| JitoLabs | independent | slot2 | 7 | undetermined | - | cross 0.196 (0.079 to 0.312; p 0.0236; mean of burst taus 0.196); fee -0.067 (-0.366 to 0.232; p 0.47; mean of burst taus -0.067); ties 0.381 (0.104 to 0.658; p 0.00198; mean of burst taus 0.381) | 0.537 (0.372 to 0.702); 0 of 7 bursts without a violation |
| JitoLabs | shared | pre300 | 5 | fee-rule | ties-arrival | cross 0.148 (-0.137 to 0.433; p 0.216; mean of burst taus 0.148); fee 0.905 (0.905 to 0.905; p 2.9e-28; mean of burst taus 0.905); ties 0.500 (0.061 to 0.939; p 0.000546; mean of burst taus 0.500) | 0.000 (0.000 to 0.000); 5 of 5 bursts without a violation |
| JitoLabs | shared | slot2 | 6 | arrival-rule | forward | cross 0.654 (0.499 to 0.809; p 9.3e-14; mean of burst taus 0.654); fee 0.179 (-0.113 to 0.470; p 0.0674; mean of burst taus 0.179); ties 0.722 (0.483 to 0.961; p 9.03e-09; mean of burst taus 0.722) | 0.401 (0.240 to 0.562); 0 of 6 bursts without a violation |
| Rakurai | denominator | pre300 | 7 | divides | - | limit 0.510 (0.185 to 0.835; p 3.17e-08; mean of burst taus 0.510); send 0.069 (-0.205 to 0.344; p 0.423; mean of burst taus 0.069) | 0.155 (-0.065 to 0.375); 4 of 7 bursts without a violation |
| Rakurai | denominator | slot2 | 5 | undetermined | - | limit 0.164 (0.062 to 0.266; p 0.164; mean of burst taus 0.164); send 0.188 (-0.317 to 0.692; p 0.0612; mean of burst taus 0.188) | 0.389 (0.320 to 0.458); 0 of 5 bursts without a violation |
| Rakurai | equal_fee | pre300 | 8 | undetermined | - | send -0.057 (-0.230 to 0.116; p 0.483; mean of burst taus -0.057) | 0.528 (0.442 to 0.615); 0 of 8 bursts without a violation |
| Rakurai | equal_fee | slot2 | 6 | arrival-rule | forward | send 1.000 (1.000 to 1.000; p 5.41e-48; mean of burst taus 1.000) | 0.000 (0.000 to 0.000); 6 of 6 bursts without a violation |
| Rakurai | independent | pre300 | 8 | fee-rule | ties-unordered | cross 0.051 (-0.196 to 0.298; p 0.578; mean of burst taus 0.051); fee 0.360 (0.066 to 0.654; p 1.22e-05; mean of burst taus 0.360); ties -0.125 (-0.391 to 0.141; p 0.31; mean of burst taus -0.125) | 0.301 (0.138 to 0.463); 1 of 8 bursts without a violation |
| Rakurai | independent | slot2 | 6 | arrival-rule | forward | cross 0.426 (0.211 to 0.641; p 3.09e-06; mean of burst taus 0.426); fee 0.067 (-0.139 to 0.273; p 0.506; mean of burst taus 0.067); ties 0.389 (0.103 to 0.675; p 0.00361; mean of burst taus 0.389) | 0.463 (0.349 to 0.577); 0 of 6 bursts without a violation |
| Rakurai | shared | pre300 | 7 | fee-rule | ties-unordered | cross -0.069 (-0.380 to 0.242; p 0.503; mean of burst taus -0.069); fee 0.905 (0.905 to 0.905; p 2.12e-39; mean of burst taus 0.905); ties 0.024 (-0.314 to 0.362; p 0.922; mean of burst taus 0.024) | 0.000 (0.000 to 0.000); 7 of 7 bursts without a violation |
| Rakurai | shared | slot2 | 5 | arrival-rule | forward | cross 0.733 (0.433 to 1.034; p 1.56e-14; mean of burst taus 0.733); fee 0.087 (-0.582 to 0.756; p 0.429; mean of burst taus 0.087); ties 0.600 (0.041 to 1.159; p 2.38e-05; mean of burst taus 0.600) | 0.452 (0.082 to 0.822); 1 of 5 bursts without a violation |
<!-- itb:end campaign-cells -->

### 6.3 Builder against its base

<!-- itb:in-report campaign-pairs -->
This table stands in [REPORT.md, section 4.2](REPORT.md#42-builder-against-its-base).

### 6.4 Segments between ticks

<!-- itb:in-report campaign-rounds -->
This table stands in [REPORT.md, section 4.3](REPORT.md#43-segments-between-ticks).

### 6.5 Inclusion

<!-- itb:begin campaign-inclusion -->
| Class | Timing | Path | Priority fee (lamports) | Delivered | In target window | Share |
|---|---|---|---|---|---|---|
| Agave | pre300 | quic | 0 | 93 | 93 | 1.00 |
| Agave | pre300 | quic | 10 | 93 | 93 | 1.00 |
| Agave | pre300 | quic | 100 | 93 | 93 | 1.00 |
| Agave | pre300 | quic | 1000 | 93 | 93 | 1.00 |
| Agave | pre300 | rpc | 0 | 12 | 7 | 0.58 |
| Agave | pre300 | rpc | 10 | 12 | 5 | 0.42 |
| Agave | pre300 | rpc | 100 | 12 | 7 | 0.58 |
| Agave | pre300 | rpc | 1000 | 12 | 7 | 0.58 |
| Agave | slot2 | quic | 0 | 93 | 93 | 1.00 |
| Agave | slot2 | quic | 10 | 93 | 93 | 1.00 |
| Agave | slot2 | quic | 100 | 93 | 93 | 1.00 |
| Agave | slot2 | quic | 1000 | 93 | 93 | 1.00 |
| Agave | slot2 | rpc | 0 | 12 | 11 | 0.92 |
| Agave | slot2 | rpc | 10 | 12 | 12 | 1.00 |
| Agave | slot2 | rpc | 100 | 12 | 10 | 0.83 |
| Agave | slot2 | rpc | 1000 | 12 | 7 | 0.58 |
| AgaveBam | pre300 | quic | 0 | 93 | 93 | 1.00 |
| AgaveBam | pre300 | quic | 10 | 93 | 93 | 1.00 |
| AgaveBam | pre300 | quic | 100 | 93 | 93 | 1.00 |
| AgaveBam | pre300 | quic | 1000 | 93 | 93 | 1.00 |
| AgaveBam | pre300 | rpc | 0 | 12 | 8 | 0.67 |
| AgaveBam | pre300 | rpc | 10 | 12 | 11 | 0.92 |
| AgaveBam | pre300 | rpc | 100 | 12 | 12 | 1.00 |
| AgaveBam | pre300 | rpc | 1000 | 12 | 11 | 0.92 |
| AgaveBam | slot2 | quic | 0 | 87 | 87 | 1.00 |
| AgaveBam | slot2 | quic | 10 | 87 | 87 | 1.00 |
| AgaveBam | slot2 | quic | 100 | 75 | 75 | 1.00 |
| AgaveBam | slot2 | quic | 1000 | 75 | 75 | 1.00 |
| AgaveBam | slot2 | rpc | 0 | 12 | 9 | 0.75 |
| AgaveBam | slot2 | rpc | 10 | 12 | 6 | 0.50 |
| AgaveBam | slot2 | rpc | 100 | 12 | 9 | 0.75 |
| AgaveBam | slot2 | rpc | 1000 | 12 | 7 | 0.58 |
| FireBAM | pre300 | quic | 0 | 93 | 90 | 0.97 |
| FireBAM | pre300 | quic | 10 | 93 | 93 | 1.00 |
| FireBAM | pre300 | quic | 100 | 93 | 93 | 1.00 |
| FireBAM | pre300 | quic | 1000 | 93 | 93 | 1.00 |
| FireBAM | pre300 | rpc | 0 | 12 | 10 | 0.83 |
| FireBAM | pre300 | rpc | 10 | 12 | 10 | 0.83 |
| FireBAM | pre300 | rpc | 100 | 12 | 12 | 1.00 |
| FireBAM | pre300 | rpc | 1000 | 12 | 10 | 0.83 |
| FireBAM | slot2 | quic | 0 | 93 | 93 | 1.00 |
| FireBAM | slot2 | quic | 10 | 93 | 93 | 1.00 |
| FireBAM | slot2 | quic | 100 | 93 | 93 | 1.00 |
| FireBAM | slot2 | quic | 1000 | 93 | 93 | 1.00 |
| FireBAM | slot2 | rpc | 0 | 12 | 11 | 0.92 |
| FireBAM | slot2 | rpc | 10 | 12 | 10 | 0.83 |
| FireBAM | slot2 | rpc | 100 | 12 | 9 | 0.75 |
| FireBAM | slot2 | rpc | 1000 | 12 | 11 | 0.92 |
| Firedancer | pre300 | quic | 0 | 93 | 93 | 1.00 |
| Firedancer | pre300 | quic | 10 | 93 | 93 | 1.00 |
| Firedancer | pre300 | quic | 100 | 93 | 93 | 1.00 |
| Firedancer | pre300 | quic | 1000 | 93 | 93 | 1.00 |
| Firedancer | pre300 | rpc | 0 | 12 | 11 | 0.92 |
| Firedancer | pre300 | rpc | 10 | 12 | 9 | 0.75 |
| Firedancer | pre300 | rpc | 100 | 12 | 11 | 0.92 |
| Firedancer | pre300 | rpc | 1000 | 12 | 7 | 0.58 |
| Firedancer | slot2 | quic | 0 | 93 | 93 | 1.00 |
| Firedancer | slot2 | quic | 10 | 93 | 93 | 1.00 |
| Firedancer | slot2 | quic | 100 | 93 | 93 | 1.00 |
| Firedancer | slot2 | quic | 1000 | 93 | 93 | 1.00 |
| Firedancer | slot2 | rpc | 0 | 12 | 10 | 0.83 |
| Firedancer | slot2 | rpc | 10 | 12 | 12 | 1.00 |
| Firedancer | slot2 | rpc | 100 | 12 | 12 | 1.00 |
| Firedancer | slot2 | rpc | 1000 | 12 | 9 | 0.75 |
| HarmonicAgave | pre300 | quic | 0 | 93 | 93 | 1.00 |
| HarmonicAgave | pre300 | quic | 10 | 93 | 81 | 0.87 |
| HarmonicAgave | pre300 | quic | 100 | 93 | 93 | 1.00 |
| HarmonicAgave | pre300 | quic | 1000 | 93 | 93 | 1.00 |
| HarmonicAgave | pre300 | rpc | 0 | 12 | 9 | 0.75 |
| HarmonicAgave | pre300 | rpc | 10 | 12 | 11 | 0.92 |
| HarmonicAgave | pre300 | rpc | 100 | 12 | 7 | 0.58 |
| HarmonicAgave | pre300 | rpc | 1000 | 12 | 10 | 0.83 |
| HarmonicAgave | slot2 | quic | 0 | 93 | 93 | 1.00 |
| HarmonicAgave | slot2 | quic | 10 | 93 | 93 | 1.00 |
| HarmonicAgave | slot2 | quic | 100 | 93 | 93 | 1.00 |
| HarmonicAgave | slot2 | quic | 1000 | 93 | 93 | 1.00 |
| HarmonicAgave | slot2 | rpc | 0 | 12 | 9 | 0.75 |
| HarmonicAgave | slot2 | rpc | 10 | 12 | 10 | 0.83 |
| HarmonicAgave | slot2 | rpc | 100 | 12 | 11 | 0.92 |
| HarmonicAgave | slot2 | rpc | 1000 | 12 | 10 | 0.83 |
| HarmonicFiredancer | pre300 | quic | 0 | 93 | 93 | 1.00 |
| HarmonicFiredancer | pre300 | quic | 10 | 93 | 93 | 1.00 |
| HarmonicFiredancer | pre300 | quic | 100 | 93 | 93 | 1.00 |
| HarmonicFiredancer | pre300 | quic | 1000 | 93 | 93 | 1.00 |
| HarmonicFiredancer | pre300 | rpc | 0 | 12 | 9 | 0.75 |
| HarmonicFiredancer | pre300 | rpc | 10 | 12 | 12 | 1.00 |
| HarmonicFiredancer | pre300 | rpc | 100 | 12 | 10 | 0.83 |
| HarmonicFiredancer | pre300 | rpc | 1000 | 12 | 11 | 0.92 |
| HarmonicFiredancer | slot2 | quic | 0 | 93 | 93 | 1.00 |
| HarmonicFiredancer | slot2 | quic | 10 | 93 | 93 | 1.00 |
| HarmonicFiredancer | slot2 | quic | 100 | 93 | 93 | 1.00 |
| HarmonicFiredancer | slot2 | quic | 1000 | 93 | 93 | 1.00 |
| HarmonicFiredancer | slot2 | rpc | 0 | 12 | 9 | 0.75 |
| HarmonicFiredancer | slot2 | rpc | 10 | 12 | 8 | 0.67 |
| HarmonicFiredancer | slot2 | rpc | 100 | 12 | 8 | 0.67 |
| HarmonicFiredancer | slot2 | rpc | 1000 | 12 | 11 | 0.92 |
| JitoLabs | pre300 | quic | 0 | 93 | 93 | 1.00 |
| JitoLabs | pre300 | quic | 10 | 93 | 93 | 1.00 |
| JitoLabs | pre300 | quic | 100 | 93 | 93 | 1.00 |
| JitoLabs | pre300 | quic | 1000 | 93 | 93 | 1.00 |
| JitoLabs | pre300 | rpc | 0 | 12 | 8 | 0.67 |
| JitoLabs | pre300 | rpc | 10 | 12 | 9 | 0.75 |
| JitoLabs | pre300 | rpc | 100 | 12 | 11 | 0.92 |
| JitoLabs | pre300 | rpc | 1000 | 12 | 8 | 0.67 |
| JitoLabs | slot2 | quic | 0 | 93 | 93 | 1.00 |
| JitoLabs | slot2 | quic | 10 | 93 | 93 | 1.00 |
| JitoLabs | slot2 | quic | 100 | 93 | 93 | 1.00 |
| JitoLabs | slot2 | quic | 1000 | 81 | 81 | 1.00 |
| JitoLabs | slot2 | rpc | 0 | 12 | 9 | 0.75 |
| JitoLabs | slot2 | rpc | 10 | 12 | 5 | 0.42 |
| JitoLabs | slot2 | rpc | 100 | 12 | 9 | 0.75 |
| JitoLabs | slot2 | rpc | 1000 | 12 | 10 | 0.83 |
| Rakurai | pre300 | quic | 0 | 93 | 93 | 1.00 |
| Rakurai | pre300 | quic | 10 | 93 | 93 | 1.00 |
| Rakurai | pre300 | quic | 100 | 93 | 93 | 1.00 |
| Rakurai | pre300 | quic | 1000 | 93 | 93 | 1.00 |
| Rakurai | pre300 | rpc | 0 | 12 | 9 | 0.75 |
| Rakurai | pre300 | rpc | 10 | 12 | 11 | 0.92 |
| Rakurai | pre300 | rpc | 100 | 12 | 8 | 0.67 |
| Rakurai | pre300 | rpc | 1000 | 12 | 8 | 0.67 |
| Rakurai | slot2 | quic | 0 | 93 | 93 | 1.00 |
| Rakurai | slot2 | quic | 10 | 93 | 85 | 0.91 |
| Rakurai | slot2 | quic | 100 | 93 | 93 | 1.00 |
| Rakurai | slot2 | quic | 1000 | 93 | 93 | 1.00 |
| Rakurai | slot2 | rpc | 0 | 12 | 9 | 0.75 |
| Rakurai | slot2 | rpc | 10 | 12 | 9 | 0.75 |
| Rakurai | slot2 | rpc | 100 | 12 | 10 | 0.83 |
| Rakurai | slot2 | rpc | 1000 | 12 | 9 | 0.75 |
<!-- itb:end campaign-inclusion -->

### 6.6 Moment condition and client labels

<!-- itb:begin campaign-timing -->
| Condition | Bursts | In the band | Share | Median arrival estimate from the target (ms) | Range (ms) | Slot clock behind |
|---|---|---|---|---|---|---|
| pre300 | 248 | 218 | 0.88 | -0 | -507 to 764 | 0 |
| slot2 | 248 | 197 | 0.79 | -1 | -571 to 334 | 0 |

| Class | In the band, pre300 | In the band, slot2 |
|---|---|---|
| AgaveBam | 26 of 31 | 19 of 31 |
| JitoLabs | 28 of 31 | 28 of 31 |
| HarmonicAgave | 26 of 31 | 26 of 31 |
| HarmonicFiredancer | 29 of 31 | 25 of 31 |
| Firedancer | 31 of 31 | 25 of 31 |
| FireBAM | 21 of 31 | 26 of 31 |
| Rakurai | 30 of 31 | 22 of 31 |
| Agave | 27 of 31 | 26 of 31 |
<!-- itb:end campaign-timing -->

<!-- itb:begin campaign-labels -->
| Class at selection | Bursts | Leader showed another clientId | Share | clientId shown |
|---|---|---|---|---|
| AgaveBam | 62 | 0 | 0.00 | - |
| JitoLabs | 62 | 0 | 0.00 | - |
| HarmonicAgave | 62 | 0 | 0.00 | - |
| HarmonicFiredancer | 62 | 0 | 0.00 | - |
| Firedancer | 62 | 0 | 0.00 | - |
| FireBAM | 62 | 0 | 0.00 | - |
| Rakurai | 62 | 0 | 0.00 | - |
| Agave | 62 | 0 | 0.00 | - |
<!-- itb:end campaign-labels -->

### 6.7 Probes outside their window

<!-- itb:begin campaign-elsewhere -->
| Path | Timing | Delivered | In target window | Same leader, outside the window | Another leader's block | Not included | Class of the other leaders |
|---|---|---|---|---|---|---|---|
| quic | pre300 | 2976 | 2961 | 12 | 3 | 0 | AgaveBam 3 |
| quic | slot2 | 2916 | 2908 | 0 | 0 | 8 | - |
| rpc | pre300 | 384 | 299 | 0 | 85 | 0 | AgaveBam 15, Firedancer 4, HarmonicAgave 14, HarmonicFiredancer 18, JitoLabs 22, unknown 12 |
| rpc | slot2 | 384 | 301 | 2 | 81 | 0 | AgaveBam 28, Firedancer 9, HarmonicAgave 24, JitoLabs 16, unknown 4 |

| Class of the target | Delivered | In target window | Same leader, outside the window | Another leader's block | Not included |
|---|---|---|---|---|---|
| AgaveBam | 792 | 769 | 0 | 23 | 0 |
| JitoLabs | 828 | 801 | 0 | 27 | 0 |
| HarmonicAgave | 840 | 809 | 12 | 19 | 0 |
| HarmonicFiredancer | 840 | 822 | 2 | 16 | 0 |
| Firedancer | 840 | 825 | 0 | 15 | 0 |
| FireBAM | 840 | 824 | 0 | 16 | 0 |
| Rakurai | 840 | 809 | 0 | 23 | 8 |
| Agave | 840 | 810 | 0 | 30 | 0 |
<!-- itb:end campaign-elsewhere -->

### 6.8 Path latency

<!-- itb:begin campaign-latency -->
| Class | Leader | Bursts | Median one-way estimate (ms) | Class median (ms) |
|---|---|---|---|---|
| AgaveBam | `5Cchr1XGEg7dbBXByV5NY2ad8jfxAM7HA3x8D56rq9Ux` | 31 | 81.6 | 71.3 |
| AgaveBam | `DRpbCBMxVnDK7maPM5tGv6MvB3v1sRMC86PZ8okm21hy` | 31 | 57.1 | 71.3 |
| JitoLabs | `E1r4Psq84tHfQ6aPTvvDka4U3u8zPVD7gEUrH25RdxHL` | 31 | 19.1 | 19.3 |
| JitoLabs | `HEL1USMZKAL2odpNBj2oCjffnFGaYwmbGmyewGv1e2TU` | 31 | 19.5 | 19.3 |
| HarmonicAgave | `CAo1dCGYrB6NhHh5xb1cGjUiu86iyCfMTENxgHumSve4` | 31 | 24.0 | 21.3 |
| HarmonicAgave | `Fd7btgySsrjuo25CJCj7oE7VPMyezDhnx7pZkj2v69Nk` | 31 | 18.0 | 21.3 |
| HarmonicFiredancer | `Awes4Tr6TX8JDzEhCZY2QVNimT6iD1zWHzf1vNyGvpLM` | 31 | 17.3 | 17.3 |
| HarmonicFiredancer | `JUPiTERrZqgf1jUyR7dSkhMx4Kn2qJyekWsg3LT1h4b` | 31 | 17.3 | 17.3 |
| Firedancer | `4VRs6A9zBRXz6MLcmQGsBiSoWE2JjHrmw7LintC3T4Nv` | 31 | 24.1 | 24.3 |
| Firedancer | `BFmqBsaGjeYA7gHpReKmnVkRyhqiMmHoR9ttv1crWmzy` | 31 | 24.3 | 24.3 |
| FireBAM | `9jxgosAfHgHzwnxsHw4RAZYaLVokMbnYtmiZBreynGFP` | 31 | 16.0 | 18.6 |
| FireBAM | `LA1NEzryoih6CQW3gwQqJQffK2mKgnXcjSQZSRpM3wc` | 31 | 19.1 | 18.6 |
| Rakurai | `E3mDbFMr8yZcCAZx5wPUFCRmLX31u8Nnj4jPoPc54h3F` | 31 | 18.3 | 17.7 |
| Rakurai | `ana2y2YvQ3ZPMwm6qhnN3nJoUSiT3qx5Pvetkq9xcfY` | 31 | 16.0 | 17.7 |
| Agave | `5Us18hLZPXJTS4QVuGSsUw137Dyd2tgBaem24Xsf5nBS` | 31 | 29.7 | 26.4 |
| Agave | `7QQGNm3ptwinipDCyaCF7jY5katgmFUu1ieP2f7nwLpE` | 31 | 22.7 | 26.4 |
<!-- itb:end campaign-latency -->

### 6.9 Load

<!-- itb:begin campaign-loads -->
| Load by | Quartile | Mean load of the burst's blocks | Bursts | tau fee, independent and shared | tau send, equal fee | tau send, equal fee, Agave, pre300 |
|---|---|---|---|---|---|---|
| costUnits | Q1 | 983322 to 9681380 | 103 | 0.444 (0.319 to 0.570), 42 bursts | 0.414 (0.219 to 0.609), 30 bursts | 0.172 (-0.330 to 0.673), 3 bursts |
| costUnits | Q2 | 9693014 to 12989788 | 103 | 0.553 (0.433 to 0.673), 48 bursts | 0.218 (-0.029 to 0.465), 28 bursts | 0.091 (0.091 to 0.091), 2 bursts |
| costUnits | Q3 | 12992911 to 18667855 | 103 | 0.620 (0.521 to 0.719), 51 bursts | 0.209 (-0.011 to 0.429), 30 bursts | -0.242 (no interval), 1 bursts |
| costUnits | Q4 | 18670736 to 49978378 | 102 | 0.713 (0.629 to 0.796), 59 bursts | 0.139 (-0.171 to 0.449), 19 bursts | 0.212 (no interval), 1 bursts |
| transactions | Q1 | 114 to 239 | 103 | 0.422 (0.287 to 0.557), 39 bursts | 0.492 (0.263 to 0.721), 28 bursts | 0.303 (no interval), 1 bursts |
| transactions | Q2 | 239 to 316 | 103 | 0.542 (0.436 to 0.647), 53 bursts | 0.295 (0.097 to 0.494), 28 bursts | 0.101 (-0.314 to 0.516), 3 bursts |
| transactions | Q3 | 318 to 430 | 103 | 0.642 (0.544 to 0.740), 47 bursts | 0.183 (-0.040 to 0.407), 29 bursts | 0.152 (-0.619 to 0.922), 2 bursts |
| transactions | Q4 | 431 to 1713 | 102 | 0.713 (0.625 to 0.802), 61 bursts | 0.000 (-0.273 to 0.273), 22 bursts | -0.242 (no interval), 1 bursts |
<!-- itb:end campaign-loads -->

### 6.10 First slot of the window

<!-- itb:begin campaign-first-slot -->
| Blocks | tau fee | tau cross | tau send, equal fee |
|---|---|---|---|
| first slot of the window | 0.696 (0.645 to 0.746), 131 bursts | 0.040 (-0.013 to 0.092), 131 bursts | -0.083 (-0.201 to 0.036), 65 bursts |
| later slots | 0.402 (0.295 to 0.509), 69 bursts | 0.187 (0.100 to 0.274), 69 bursts | 0.733 (0.623 to 0.843), 49 bursts |
<!-- itb:end campaign-first-slot -->

### 6.11 HarmonicAgave strategy

<!-- itb:begin campaign-strategy -->
| Strategy in the memo | Leaders | tau fee | tau cross | tau send, equal fee |
|---|---|---|---|---|
| FBA | `CAo1dCGY...` | 0.455 (0.133 to 0.776), 7 bursts | -0.048 (-0.233 to 0.138), 7 bursts | -0.023 (-0.137 to 0.091), 4 bursts |
| MRV | `Fd7btgyS...` | 0.369 (0.158 to 0.579), 7 bursts | 0.063 (-0.191 to 0.318), 7 bursts | -0.182 (-0.567 to 0.203), 2 bursts |
| no memo | `CAo1dCGY...`, `Fd7btgyS...` | 0.496 (0.215 to 0.778), 11 bursts | 0.088 (-0.083 to 0.258), 11 bursts | 0.651 (0.517 to 0.786), 7 bursts |
<!-- itb:end campaign-strategy -->

### 6.12 Epochs and rounds

<!-- itb:begin campaign-epochs -->
| Class | tau fee, epoch 1071 | tau fee, epoch 1072 | tau fee, epoch 1073 | tau fee, epoch 1074 | Round means of tau fee |
|---|---|---|---|---|---|
| AgaveBam | 0.888 (2 cells) | 0.879 (4 cells) | 0.804 (3 cells) | 0.893 (3 cells) | 13 rounds, 0.754 to 0.905 |
| JitoLabs | 0.507 (4 cells) | 0.255 (4 cells) | 0.331 (4 cells) | 0.377 (4 cells) | 14 rounds, -0.067 to 0.670 |
| HarmonicAgave | 0.441 (3 cells) | 0.473 (4 cells) | 0.507 (4 cells) | 0.398 (4 cells) | 15 rounds, 0.000 to 0.871 |
| HarmonicFiredancer | 0.497 (3 cells) | 0.645 (4 cells) | 0.578 (4 cells) | 0.586 (3 cells) | 15 rounds, 0.335 to 0.871 |
| Firedancer | 0.905 (4 cells) | 0.905 (4 cells) | 0.905 (4 cells) | 0.905 (4 cells) | 15 rounds, 0.905 to 0.905 |
| FireBAM | 0.879 (4 cells) | 0.838 (4 cells) | 0.882 (3 cells) | 0.875 (4 cells) | 14 rounds, 0.670 to 0.905 |
| Rakurai | 0.645 (4 cells) | 0.272 (4 cells) | 0.264 (4 cells) | 0.264 (4 cells) | 15 rounds, -0.134 to 0.905 |
| Agave | 0.448 (4 cells) | 0.427 (4 cells) | 0.494 (4 cells) | 0.394 (4 cells) | 15 rounds, 0.000 to 0.905 |
<!-- itb:end campaign-epochs -->

The analysis plan fixes no test of stability over epochs, so this table describes it without a verdict (section 9).

### 6.13 Competition inside the block

<!-- itb:begin campaign-competition -->
| Class | Probes | Median position (share of block) | Median rank by requested-limit priority | Median rank by costUnits priority | Jito tip transactions | Transactions without a CU limit |
|---|---|---|---|---|---|---|
| AgaveBam | 516 | 0.16 | 0.13 | 0.03 | 2.7% | 8.9% |
| JitoLabs | 660 | 0.22 | 0.17 | 0.05 | 4.0% | 7.4% |
| HarmonicAgave | 612 | 0.09 | 0.19 | 0.07 | 3.8% | 9.9% |
| HarmonicFiredancer | 647 | 0.05 | 0.19 | 0.07 | 2.9% | 9.1% |
| Firedancer | 671 | 0.06 | 0.15 | 0.05 | 5.2% | 9.8% |
| FireBAM | 564 | 0.21 | 0.15 | 0.04 | 3.7% | 6.9% |
| Rakurai | 624 | 0.13 | 0.19 | 0.06 | 1.2% | 8.9% |
| Agave | 636 | 0.14 | 0.18 | 0.06 | 0.2% | 8.4% |
<!-- itb:end campaign-competition -->

### 6.14 Control path

<!-- itb:in-report campaign-control -->
This table stands in [REPORT.md, section 4.4](REPORT.md#44-control-path).

The control path is compared with the direct path only within the same leader and epoch. The p of each measure comes from swapping path labels within those strata, exact while the arrangements stay within the label-test budget of the analysis plan and from seeded draws above it.

### 6.15 Each leader on its own

The question is asked of each validator, while the verdicts stand on the client class: the analysis plan tests classes and allows values per leader only as a description (ANALYSIS-PLAN.md, line 33). Each leader holds a share of its class cell's bursts, too few for a test of its own, so this table shows whether the two leaders of a class point the same way.

<!-- itb:begin campaign-leaders -->
Descriptive, no verdict: each leader holds a share of its class cell's bursts before the window. A cell gives the pooled taus of the arm as the cells block names them, the violated pair share and the bursts behind them.

| Leader | Class | Version | independent | shared | equal_fee | denominator |
|---|---|---|---|---|---|---|
| `5Cchr1XG...` | AgaveBam | 4.3.2 | fee 0.90; cross 0.01; violated 0.00; 4 bursts | fee 0.90; cross -0.12; violated 0.00; 3 bursts | send 0.09; violated 0.45; 4 bursts | limit 0.74; send -0.17; violated 0.00; 4 bursts |
| `DRpbCBMx...` | AgaveBam | 4.4.0, 4.4.0-rc.1 | fee 0.88; cross 0.12; violated 0.01; 3 bursts | fee 0.90; cross -0.04; violated 0.00; 2 bursts | send -0.11; violated 0.56; 4 bursts | limit 0.74; send -0.06; violated 0.00; 2 bursts |
| `E1r4Psq8...` | JitoLabs | 4.3.2, 4.4.0 | fee 0.46; cross -0.01; violated 0.25; 4 bursts | fee 0.90; cross 0.26; violated 0.00; 2 bursts | send 0.18; violated 0.41; 4 bursts | limit 0.42; send -0.09; violated 0.22; 4 bursts |
| `HEL1USMZ...` | JitoLabs | 4.3.2, 4.4.0 | fee 0.38; cross -0.02; violated 0.29; 4 bursts | fee 0.90; cross 0.07; violated 0.00; 3 bursts | send 0.13; violated 0.43; 3 bursts | limit 0.35; send 0.17; violated 0.26; 4 bursts |
| `CAo1dCGY...` | HarmonicAgave | 4.3.2 | fee 0.19; cross -0.05; violated 0.39; 4 bursts | fee 0.80; cross -0.05; violated 0.06; 3 bursts | send -0.02; violated 0.51; 4 bursts | limit 0.21; send -0.15; violated 0.36; 2 bursts |
| `Fd7btgyS...` | HarmonicAgave | 4.3.2, 4.4.0 | fee 0.23; cross -0.07; violated 0.37; 4 bursts | fee 0.70; cross -0.04; violated 0.11; 1 burst | send -0.08; violated 0.54; 3 bursts | limit 0.12; send 0.20; violated 0.42; 4 bursts |
| `Awes4Tr6...` | HarmonicFiredancer | 26.10.4, 26.10.5 | fee 0.78; cross -0.06; violated 0.07; 4 bursts | fee 0.72; cross 0.23; violated 0.10; 4 bursts | send 0.35; violated 0.32; 3 bursts | limit 0.74; send 0.02; violated 0.00; 4 bursts |
| `JUPiTERr...` | HarmonicFiredancer | 26.10.4, 26.10.5 | fee 0.70; cross -0.01; violated 0.12; 4 bursts | fee 0.74; cross 0.20; violated 0.09; 3 bursts | send 0.02; violated 0.49; 3 bursts | limit 0.59; send 0.07; violated 0.10; 4 bursts |
| `4VRs6A9z...` | Firedancer | 26.10.4, 26.10.5 | fee 0.90; cross -0.10; violated 0.00; 4 bursts | fee 0.90; cross 0.07; violated 0.00; 4 bursts | send -1.00; violated 1.00; 4 bursts | limit 0.74; send -0.23; violated 0.00; 4 bursts |
| `BFmqBsaG...` | Firedancer | 26.10.4, 26.10.5 | fee 0.90; cross 0.04; violated 0.00; 4 bursts | fee 0.90; cross -0.30; violated 0.00; 3 bursts | send -1.00; violated 1.00; 4 bursts | limit 0.74; send -0.47; violated 0.00; 4 bursts |
| `9jxgosAf...` | FireBAM | 26.10.5 | fee 0.82; cross 0.02; violated 0.05; 2 bursts | fee 0.90; cross 0.07; violated 0.00; 2 bursts | send -0.16; violated 0.58; 3 bursts | limit 0.74; send 0.09; violated 0.00; 2 bursts |
| `LA1NEzry...` | FireBAM | 26.10.5 | fee 0.88; cross 0.07; violated 0.01; 4 bursts | fee 0.90; cross 0.09; violated 0.00; 2 bursts | send 0.04; violated 0.48; 3 bursts | limit 0.74; send -0.02; violated 0.00; 3 bursts |
| `E3mDbFMr...` | Rakurai | 4.3.2 | fee 0.49; cross 0.05; violated 0.23; 4 bursts | fee 0.90; cross 0.04; violated 0.00; 4 bursts | send -0.08; violated 0.54; 4 bursts | limit 0.55; send 0.08; violated 0.12; 4 bursts |
| `ana2y2Yv...` | Rakurai | 4.3.2, 4.4.0 | fee 0.23; cross 0.06; violated 0.37; 4 bursts | fee 0.90; cross -0.21; violated 0.00; 3 bursts | send -0.03; violated 0.52; 4 bursts | limit 0.45; send 0.06; violated 0.19; 3 bursts |
| `5Us18hLZ...` | Agave | 4.3.2 | fee 0.46; cross 0.06; violated 0.25; 4 bursts | fee 0.90; cross 0.11; violated 0.00; 4 bursts | send -0.07; violated 0.54; 3 bursts | limit 0.74; send 0.17; violated 0.00; 3 bursts |
| `7QQGNm3p...` | Agave | 4.3.2 | fee 0.42; cross -0.16; violated 0.27; 4 bursts | fee 0.90; cross -0.13; violated 0.00; 2 bursts | send 0.22; violated 0.39; 4 bursts | limit 0.53; send -0.06; violated 0.14; 3 bursts |
<!-- itb:end campaign-leaders -->

## 7. The builder mark

<!-- itb:begin tick-runs -->
| Run | Class of the slot's leader | Its builder | Slots | With a BAM tick | With a Harmonic tick |
|---|---|---|---|---|---|
| `campaign-mainnet-20261028T055501Z` | AgaveBam | BAM | 13 | 13 (100.0%) | 0 (0.0%) |
| `campaign-mainnet-20261028T055501Z` | JitoLabs | none | 14 | 0 (0.0%) | 0 (0.0%) |
| `campaign-mainnet-20261028T055501Z` | HarmonicAgave | Harmonic | 14 | 0 (0.0%) | 14 (100.0%) |
| `campaign-mainnet-20261028T055501Z` | HarmonicFiredancer | Harmonic | 13 | 0 (0.0%) | 13 (100.0%) |
| `campaign-mainnet-20261028T055501Z` | Firedancer | none | 12 | 0 (0.0%) | 0 (0.0%) |
| `campaign-mainnet-20261028T055501Z` | FireBAM | BAM | 12 | 12 (100.0%) | 0 (0.0%) |
| `campaign-mainnet-20261028T055501Z` | Rakurai | none | 11 | 0 (0.0%) | 0 (0.0%) |
| `campaign-mainnet-20261028T055501Z` | Agave | none | 13 | 0 (0.0%) | 0 (0.0%) |
| `campaign-mainnet-20261029T120927Z` | AgaveBam | BAM | 15 | 15 (100.0%) | 0 (0.0%) |
| `campaign-mainnet-20261029T120927Z` | JitoLabs | none | 14 | 0 (0.0%) | 0 (0.0%) |
| `campaign-mainnet-20261029T120927Z` | HarmonicAgave | Harmonic | 15 | 0 (0.0%) | 15 (100.0%) |
| `campaign-mainnet-20261029T120927Z` | HarmonicFiredancer | Harmonic | 15 | 0 (0.0%) | 15 (100.0%) |
| `campaign-mainnet-20261029T120927Z` | Firedancer | none | 14 | 0 (0.0%) | 0 (0.0%) |
| `campaign-mainnet-20261029T120927Z` | FireBAM | BAM | 16 | 16 (100.0%) | 0 (0.0%) |
| `campaign-mainnet-20261029T120927Z` | Rakurai | none | 12 | 0 (0.0%) | 0 (0.0%) |
| `campaign-mainnet-20261029T120927Z` | Agave | none | 13 | 0 (0.0%) | 0 (0.0%) |
| `campaign-mainnet-20261030T015219Z` | AgaveBam | BAM | 31 | 31 (100.0%) | 0 (0.0%) |
| `campaign-mainnet-20261030T015219Z` | JitoLabs | none | 31 | 0 (0.0%) | 0 (0.0%) |
| `campaign-mainnet-20261030T015219Z` | HarmonicAgave | Harmonic | 32 | 0 (0.0%) | 32 (100.0%) |
| `campaign-mainnet-20261030T015219Z` | HarmonicFiredancer | Harmonic | 34 | 0 (0.0%) | 34 (100.0%) |
| `campaign-mainnet-20261030T015219Z` | Firedancer | none | 23 | 0 (0.0%) | 0 (0.0%) |
| `campaign-mainnet-20261030T015219Z` | FireBAM | BAM | 30 | 30 (100.0%) | 0 (0.0%) |
| `campaign-mainnet-20261030T015219Z` | Rakurai | none | 28 | 0 (0.0%) | 0 (0.0%) |
| `campaign-mainnet-20261030T015219Z` | Agave | none | 31 | 0 (0.0%) | 0 (0.0%) |
| `campaign-mainnet-20261031T014357Z` | AgaveBam | BAM | 29 | 29 (100.0%) | 0 (0.0%) |
| `campaign-mainnet-20261031T014357Z` | JitoLabs | none | 30 | 0 (0.0%) | 0 (0.0%) |
| `campaign-mainnet-20261031T014357Z` | HarmonicAgave | Harmonic | 30 | 0 (0.0%) | 30 (100.0%) |
| `campaign-mainnet-20261031T014357Z` | HarmonicFiredancer | Harmonic | 31 | 0 (0.0%) | 31 (100.0%) |
| `campaign-mainnet-20261031T014357Z` | Firedancer | none | 25 | 0 (0.0%) | 0 (0.0%) |
| `campaign-mainnet-20261031T014357Z` | FireBAM | BAM | 28 | 28 (100.0%) | 0 (0.0%) |
| `campaign-mainnet-20261031T014357Z` | Rakurai | none | 26 | 0 (0.0%) | 0 (0.0%) |
| `campaign-mainnet-20261031T014357Z` | Agave | none | 31 | 0 (0.0%) | 0 (0.0%) |
| `campaign-mainnet-20261101T041655Z` | AgaveBam | BAM | 29 | 29 (100.0%) | 0 (0.0%) |
| `campaign-mainnet-20261101T041655Z` | JitoLabs | none | 31 | 0 (0.0%) | 0 (0.0%) |
| `campaign-mainnet-20261101T041655Z` | HarmonicAgave | Harmonic | 28 | 0 (0.0%) | 28 (100.0%) |
| `campaign-mainnet-20261101T041655Z` | HarmonicFiredancer | Harmonic | 27 | 0 (0.0%) | 27 (100.0%) |
| `campaign-mainnet-20261101T041655Z` | Firedancer | none | 22 | 0 (0.0%) | 0 (0.0%) |
| `campaign-mainnet-20261101T041655Z` | FireBAM | BAM | 28 | 28 (100.0%) | 0 (0.0%) |
| `campaign-mainnet-20261101T041655Z` | Rakurai | none | 24 | 0 (0.0%) | 0 (0.0%) |
| `campaign-mainnet-20261101T041655Z` | Agave | none | 27 | 0 (0.0%) | 0 (0.0%) |
| `pilot-mainnet-20261027T085253Z` | AgaveBam | BAM | 12 | 12 (100.0%) | 0 (0.0%) |
| `pilot-mainnet-20261027T085253Z` | JitoLabs | none | 11 | 0 (0.0%) | 0 (0.0%) |
| `pilot-mainnet-20261027T085253Z` | HarmonicAgave | Harmonic | 13 | 0 (0.0%) | 13 (100.0%) |
| `pilot-mainnet-20261027T085253Z` | HarmonicFiredancer | Harmonic | 13 | 0 (0.0%) | 13 (100.0%) |
| `pilot-mainnet-20261027T085253Z` | Firedancer | none | 11 | 0 (0.0%) | 0 (0.0%) |
| `pilot-mainnet-20261027T085253Z` | FireBAM | BAM | 14 | 14 (100.0%) | 0 (0.0%) |
| `pilot-mainnet-20261027T085253Z` | Rakurai | none | 11 | 0 (0.0%) | 0 (0.0%) |
| `pilot-mainnet-20261027T085253Z` | Agave | none | 10 | 0 (0.0%) | 0 (0.0%) |

Slots left out because no burst row names their leader, so neither this table nor the label check classes them: `campaign-mainnet-20261028T034521Z` 0 of 0, `campaign-mainnet-20261028T055501Z` 4 of 106, `campaign-mainnet-20261029T120927Z` 7 of 121, `campaign-mainnet-20261030T015219Z` 15 of 255, `campaign-mainnet-20261031T014357Z` 17 of 247, `campaign-mainnet-20261101T041655Z` 24 of 240, `pilot-mainnet-20261027T085253Z` 1 of 96.
<!-- itb:end tick-runs -->

In every pilot slot of a builder-class leader the block carried a tick from that builder's signer, and no slot of another class carried a tick from either signer.

<!-- itb:begin tick-epoch -->
Epoch 1069, 400 slots per class drawn with seed 1069, classes by gossip at 2026-10-27 00:56:38 (`research/tick-scale/summary-e1069.json`):

| Class | Slots in epoch | Blocks read | Leaders read | Skipped or empty | BAM tick (95% CI) | Harmonic tick (95% CI) | No tick (95% CI) |
|---|---|---|---|---|---|---|---|
| Agave | 4796 | 394 | 20 | 6 | 1 (0.2%; 0.0 to 1.4) | 0 (0.0%; 0.0 to 1.0) | 393 (99.8%; 98.6 to 100.0) |
| AgaveBam | 152256 | 389 | 140 | 11 | 332 (85.3%; 81.5 to 88.5) | 1 (0.3%; 0.1 to 1.4) | 56 (14.4%; 11.3 to 18.2) |
| FireBAM | 7528 | 400 | 17 | 0 | 364 (91.0%; 87.8 to 93.4) | 0 (0.0%; 0.0 to 0.9) | 36 (9.0%; 6.6 to 12.2) |
| Firedancer | 22968 | 400 | 20 | 0 | 0 (0.0%; 0.0 to 0.9) | 0 (0.0%; 0.0 to 0.9) | 400 (100.0%; 99.0 to 100.0) |
| HarmonicAgave | 93832 | 400 | 38 | 0 | 0 (0.0%; 0.0 to 0.9) | 395 (98.8%; 97.1 to 99.5) | 5 (1.2%; 0.5 to 2.9) |
| HarmonicFiredancer | 37124 | 400 | 34 | 0 | 0 (0.0%; 0.0 to 0.9) | 400 (100.0%; 99.0 to 100.0) | 0 (0.0%; 0.0 to 0.9) |
| JitoLabs | 107540 | 397 | 78 | 3 | 0 (0.0%; 0.0 to 1.0) | 0 (0.0%; 0.0 to 1.0) | 394 (99.2%; 97.8 to 99.7) |
| Rakurai | 4984 | 397 | 9 | 3 | 0 (0.0%; 0.0 to 1.0) | 0 (0.0%; 0.0 to 1.0) | 397 (100.0%; 99.0 to 100.0) |
<!-- itb:end tick-epoch -->

The epoch table samples one whole epoch through RPC, stratified by the class of the slot's leader in gossip. Its script lies in [research/tick-scale](research/tick-scale/) together with the sample and the raw rows. Across the whole of epoch 1069 the builder's tick marks 85.3% of the AgaveBam blocks read and 91.0% of the FireBAM blocks, while the two Harmonic classes reach 98.8% and 100.0%. The campaign's pair tests take only blocks that carry their builder's tick ([campaign addendum, section 7](prereg/CAMPAIGN-ADDENDUM.md)), so the BAM classes are the ones that can lose blocks to the row without the tick.

## 8. Noise and what the kit does not separate

DESIGN.md lists what stays out of reach from outside the leader ([What it does NOT separate](DESIGN.md#what-it-does-not-separate)). Where that touches the tables above:

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
| Run | Windows planned | Bursts written | Skipped before sending | Failed | Not reached | Left out of the order tests |
|---|---|---|---|---|---|---|
| `campaign-mainnet-20261028T034521Z` | 16 | 0 | none | 0 | 16 | none |
| `campaign-mainnet-20261028T055501Z` | 72 | 56 | none | 0 | 16 | control-path 8, fewer-than-two-in-a-block 2, outside-timing-band 5 |
| `campaign-mainnet-20261029T120927Z` | 72 | 72 | none | 0 | 0 | control-path 8, fewer-than-two-in-a-block 1, outside-timing-band 12 |
| `campaign-mainnet-20261030T015219Z` | 144 | 144 | none | 0 | 0 | control-path 16, outside-timing-band 16 |
| `campaign-mainnet-20261031T014357Z` | 144 | 144 | none | 0 | 0 | control-path 16, fewer-than-two-in-a-block 2, outside-timing-band 24 |
| `campaign-mainnet-20261101T041655Z` | 144 | 144 | none | 0 | 0 | control-path 16, fewer-than-two-in-a-block 1, outside-timing-band 33 |
| `pilot-mainnet-20261027T085253Z` | 68 | 68 | none | 0 | 0 | fewer-than-two-in-a-block 1, outside-timing-band 6 |
<!-- itb:end what-went-wrong -->

- **2026-10-26 23:25 UTC, mainnet dry-run `dry-run-mainnet-20261026T232506Z`.** The slot clock ran on WebSocket events of the public node, which queued them 5 to 24 slots behind the cluster. The arrival estimate used the same late events, so the run showed 2 of 4 bursts in the band while all four missed. The clock moved onto the node's own timestamps, with a guard that skips a burst when `getSlot` runs 2 or more slots ahead of it (commit 2bacfa2), and the sender now waits for the first-shred events of the window before it closes a burst (commit d8699aa). No later run skipped a burst for the clock.
- **2026-10-27 01:06 UTC, dry-run of the pilot plan.** Within 100 ms of the target stood 4 of 8 pre-window bursts, and all four misses were early. Before any live probe the pre-window band became 200 ms early and 100 ms late of the target. That change and a neutral rewording of the analysis plan redrew the manifest twice. The anchor went on chain from the third manifest, `9a9c92c2...`; the two earlier ones, `74149b29...` and `cf3c768e...`, were simulated and never sent. The seven pilot anchor logs in `logs/` hold six simulations and the one live send at 08:52 UTC.
- **2026-10-27 08:52 UTC, pilot plan.** The validators.app snapshot failed certificate verification (`CERTIFICATE_VERIFY_FAILED`), because the antivirus web shield of the measuring machine re-signs that host. The plan was drawn without it, so no pilot burst carries the second label. The message reached the console only, since the pilot command keeps no draw notes; campaign plans keep theirs in `draw-notes.json`. The fix adds an extra root for that one request (`ITB_EXTRA_CA_FILE`, commit eebdf2f), and [scripts/campaign.sh](scripts/campaign.sh) passes it on. The campaign plan of epoch 1071, drawn at 00:57 UTC on 2026-10-28, carries the snapshot with 669 records, and each of its 144 bursts has the same class there as in gossip.
- **2026-10-27, pilot run.** Six bursts arrived outside their band. Burst 52 landed one slot early in another leader's block, and five probes of burst 99 met a closed connection (section 5.5).
- **2026-10-27, minimum.** At the spread of tau in the pilot every equivalence form is expected out of reach of the campaign, short of a spread near zero (section 5.15).
- **2026-10-27, epoch tick sample.** The public RPC node cut a 0.9 MB `getBlock` body short (`IncompleteRead`). The RPC client retried only OS-level errors, so the read stopped after 321 blocks. It now retries a cut body too, with a selftest check for each kind of failure.
- **2026-10-27 22:35 UTC, first campaign package.** A review of the pre-registration found rules that lived only in code, and the panel rule still kept windows after a leader on the same IP. The [campaign addendum](prereg/CAMPAIGN-ADDENDUM.md) states those rules, and everything drawn from the panel was drawn again at 23:30 UTC under the IP rule. The panel kept its 16 leaders, and the plan of epoch index 0 moved one burst of `Awes4Tr6...`, whose first window followed `shftkxns...` on the same IP (`198.13.140.105`).
- **2026-10-28 00:18 UTC, second review of the campaign package.** A second review read the addendum against the code. The addendum called a pair TOST out of reach, while the code's TOST passes at zero spread, as the pilot pair FireBAM against Firedancer shows (section 5.3). It also read the step-down Holm of the pair family as a fixed bar of 10 strata, and the code refused data with a repeated table burst, which a resumed run must be able to read. The addendum now states the zero-spread rule and the step-down thresholds. It also adds the reason `repeated-burst` and sets what follows from a failed builder label, and the analysis code follows these rules. The plan of epoch index 0 was drawn again under the new manifest and kept all 144 bursts of the previous plan.
- **2026-10-28 00:57 UTC, third check of the campaign package.** A third check found that the builder label was tested only in slots that held an included probe, while analysis plan line 89 covers every slot of a class without a builder. The label check and the tick table of section 7 now class every slot row by its leader and the class gossip showed for it at the burst, which takes 95 of the pilot's 96 slot rows where 69 counted before; no slot of another class carries a builder tick. The draw of epoch index 0 now refuses when the package's plan of that index is missing. The plan of epoch index 0 was drawn again under the new manifest. It keeps 143 of the 144 bursts of the previous plan; the burst of leader `LA1NEzry` in round 5 moved 7000 slots earlier, because the leader before that window had left the IP address the two shared.
- **2026-10-28 01:40 UTC, slot clock over long gaps.** Before the campaign start a check of the sender found that it slept to each window in one stretch, on the slope of the slot clock at the moment it fell asleep, and woke 30 slots (about 6 s) before the window. The rounds of the campaign plan stand 13 660 to 88 532 slots apart. Over such gaps the pilot's slopes erred by up to 37 s at 40 000 slots ahead, and a slope from 20 000 slots of block times erred by up to 100 s at 80 000 slots ahead. The pilot itself never slept longer than 8336 slots. A late wake would have sent a burst into a later leader's slots, since the clock guard compares the fresh clock with `getSlot` and both agree after the wake. The sender now sleeps in steps of at most 30 s and reads the clock again at each step, and it skips a burst it wakes for less than 4 slots before the window (`woke after the window`).
- **2026-10-28 02:12 UTC, campaign start.** The campaign runner read the spend journal from `probe status` with the pattern of the line that `probe run` and `probe close` print. The status line has another form, so the runner found no number and ended its first attempt before the live run. Nothing was sent, and the plan drawn for that attempt stays in `data/plans/campaign-mainnet-e1071-20261028T021233Z`. The runner now reads the status line, which gives the journal's 4 355 230 lamports.
- **2026-10-29, round 3 of epoch 1071.** Run `campaign-mainnet-20261028T055501Z` sent rounds 0 to 2 and never reached round 3, so its 16 windows stand under "Not reached" above; [REPORT.md, section 6](REPORT.md#6-what-went-wrong-in-the-campaign) tells why the round is lost. A start at 12:04:56 UTC ran on `c3ae1f6` with uncommitted changes and was stopped after its TLS check, before the first burst, so it left no run folder ([logs/campaign-20261029T120456Z.txt](logs/campaign-20261029T120456Z.txt)). The campaign went on at 12:09 UTC from the clean commit `18a543c` ([logs/campaign-20261029T120918Z.txt](logs/campaign-20261029T120918Z.txt)).
- **Stability over epochs.** [DESIGN.md](DESIGN.md#noise-versus-rule) says four epochs show whether a rule holds over time, yet the analysis plan fixed no test for it. The epoch tables (sections 5.12 and 6.12) describe it without a verdict.

## Appendix A. Every burst

<!-- itb:begin bursts -->
| Run | Burst | UTC (blockTime) | Epoch | Window slots | Leader | Class | clientId at burst | Arm | Timing | Delivered | In window | Other leaders' class | Fee (lamports) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `campaign-mainnet-20261028T055501Z` | 181 | 2026-10-29 03:00:16 | 1071 | 462721436-462721439 | `4VRs6A9z...` | Firedancer | Firedancer | denominator | pre300 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261028T055501Z` | 182 | 2026-10-29 03:04:07 | 1071 | 462722516-462722519 | `E3mDbFMr...` | Rakurai | Rakurai | denominator | pre300 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261028T055501Z` | 183 | 2026-10-29 03:05:42 | 1071 | 462722960-462722963 | `7QQGNm3p...` | Agave | Agave | denominator | slot2 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261028T055501Z` | 184 | 2026-10-29 03:06:40 | 1071 | 462723232-462723235 | `LA1NEzry...` | FireBAM | FireBAM | denominator | pre300 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261028T055501Z` | 185 | 2026-10-29 03:07:14 | 1071 | 462723392-462723395 | `ana2y2Yv...` | Rakurai | Rakurai | denominator | slot2 | 12 | 4 | - | 20040 |
| `campaign-mainnet-20261028T055501Z` | 186 | 2026-10-29 03:08:01 | 1071 | 462723608-462723611 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | denominator | pre300 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261028T055501Z` | 187 | 2026-10-29 03:08:36 | 1071 | 462723776-462723779 | `5Us18hLZ...` | Agave | Agave | denominator | pre300 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261028T055501Z` | 188 | 2026-10-29 03:09:11 | 1071 | 462723936-462723939 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | denominator | slot2 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261028T055501Z` | 189 | 2026-10-29 03:09:45 | 1071 | 462724096-462724099 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | denominator | slot2 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261028T055501Z` | 190 | 2026-10-29 03:10:21 | 1071 | 462724260-462724263 | `DRpbCBMx...` | AgaveBam | AgaveBam | denominator | slot2 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261028T055501Z` | 191 | 2026-10-29 03:11:22 | 1071 | 462724548-462724551 | `E1r4Psq8...` | JitoLabs | JitoLabs | denominator | pre300 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261028T055501Z` | 192 | 2026-10-29 03:12:10 | 1071 | 462724776-462724779 | `5Cchr1XG...` | AgaveBam | AgaveBam | denominator | pre300 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261028T055501Z` | 193 | 2026-10-29 03:13:03 | 1071 | 462725020-462725023 | `9jxgosAf...` | FireBAM | FireBAM | denominator | slot2 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261028T055501Z` | 194 | 2026-10-29 03:13:56 (tool clock) | 1071 | 462725268-462725271 | `HEL1USMZ...` | JitoLabs | JitoLabs | denominator | slot2 | 0 | 0 | - | 0 |
| `campaign-mainnet-20261028T055501Z` | 195 | 2026-10-29 03:15:01 | 1071 | 462725564-462725567 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | denominator | pre300 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261028T055501Z` | 196 | 2026-10-29 03:16:33 | 1071 | 462725996-462725999 | `BFmqBsaG...` | Firedancer | Firedancer | denominator | slot2 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261028T055501Z` | 197 | 2026-10-29 05:52:07 | 1071 | 462769692-462769695 | `LA1NEzry...` | FireBAM | FireBAM | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261028T055501Z` | 198 | 2026-10-29 06:19:08 | 1071 | 462777292-462777295 | `5Cchr1XG...` | AgaveBam | AgaveBam | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261028T055501Z` | 199 | 2026-10-29 06:19:49 | 1071 | 462777480-462777483 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | independent | pre300 | 12 | 11 | Firedancer | 63330 |
| `campaign-mainnet-20261028T055501Z` | 200 | 2026-10-29 06:21:24 | 1071 | 462777924-462777927 | `DRpbCBMx...` | AgaveBam | AgaveBam | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261028T055501Z` | 201 | 2026-10-29 06:21:58 | 1071 | 462778084-462778087 | `4VRs6A9z...` | Firedancer | Firedancer | independent | pre300 | 12 | 10 | HarmonicAgave | 63330 |
| `campaign-mainnet-20261028T055501Z` | 202 | 2026-10-29 06:22:34 | 1071 | 462778252-462778255 | `HEL1USMZ...` | JitoLabs | JitoLabs | independent | slot2 | 12 | 9 | HarmonicAgave | 63330 |
| `campaign-mainnet-20261028T055501Z` | 203 | 2026-10-29 06:23:19 | 1071 | 462778460-462778463 | `7QQGNm3p...` | Agave | Agave | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261028T055501Z` | 204 | 2026-10-29 06:24:25 | 1071 | 462778772-462778775 | `BFmqBsaG...` | Firedancer | Firedancer | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261028T055501Z` | 205 | 2026-10-29 06:25:38 | 1071 | 462779112-462779115 | `ana2y2Yv...` | Rakurai | Rakurai | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261028T055501Z` | 206 | 2026-10-29 06:26:18 | 1071 | 462779296-462779299 | `7QQGNm3p...` | Agave | Agave | independent | slot2 | 12 | 10 | JitoLabs | 63330 |
| `campaign-mainnet-20261028T055501Z` | 207 | 2026-10-29 06:26:55 | 1071 | 462779468-462779471 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | independent | slot2 | 12 | 11 | AgaveBam | 63330 |
| `campaign-mainnet-20261028T055501Z` | 208 | 2026-10-29 06:27:29 | 1071 | 462779628-462779631 | `9jxgosAf...` | FireBAM | FireBAM | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261028T055501Z` | 209 | 2026-10-29 06:28:08 | 1071 | 462779812-462779815 | `ana2y2Yv...` | Rakurai | Rakurai | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261028T055501Z` | 210 | 2026-10-29 06:29:11 | 1071 | 462780108-462780111 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261028T055501Z` | 211 | 2026-10-29 06:30:05 | 1071 | 462780364-462780367 | `E1r4Psq8...` | JitoLabs | JitoLabs | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261028T055501Z` | 212 | 2026-10-29 06:30:50 | 1071 | 462780572-462780575 | `HEL1USMZ...` | JitoLabs | JitoLabs | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261028T055501Z` | 213 | 2026-10-29 06:31:50 | 1071 | 462780856-462780859 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261028T055501Z` | 214 | 2026-10-29 06:32:29 | 1071 | 462781040-462781043 | `DRpbCBMx...` | AgaveBam | AgaveBam | independent | slot2 | 12 | 10 | JitoLabs | 63330 |
| `campaign-mainnet-20261028T055501Z` | 215 | 2026-10-29 06:33:25 | 1071 | 462781300-462781303 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261028T055501Z` | 216 | 2026-10-29 06:34:16 | 1071 | 462781540-462781543 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261028T055501Z` | 217 | 2026-10-29 06:35:27 | 1071 | 462781868-462781871 | `E3mDbFMr...` | Rakurai | Rakurai | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261028T055501Z` | 218 | 2026-10-29 06:36:15 | 1071 | 462782092-462782095 | `5Us18hLZ...` | Agave | Agave | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261028T055501Z` | 219 | 2026-10-29 06:39:15 | 1071 | 462782940-462782943 | `LA1NEzry...` | FireBAM | FireBAM | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261028T055501Z` | 220 | 2026-10-29 06:47:31 | 1071 | 462785280-462785283 | `4VRs6A9z...` | Firedancer | Firedancer | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261028T055501Z` | 221 | 2026-10-29 09:26:53 | 1071 | 462830128-462830131 | `E3mDbFMr...` | Rakurai | Rakurai | equal_fee | slot2 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261028T055501Z` | 222 | 2026-10-29 09:28:01 | 1071 | 462830448-462830451 | `4VRs6A9z...` | Firedancer | Firedancer | equal_fee | slot2 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261028T055501Z` | 223 | 2026-10-29 09:28:46 | 1071 | 462830660-462830663 | `9jxgosAf...` | FireBAM | FireBAM | equal_fee | pre300 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261028T055501Z` | 224 | 2026-10-29 09:29:25 | 1071 | 462830844-462830847 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | equal_fee | slot2 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261028T055501Z` | 225 | 2026-10-29 09:30:40 | 1071 | 462831192-462831195 | `5Us18hLZ...` | Agave | Agave | equal_fee | slot2 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261028T055501Z` | 226 | 2026-10-29 09:31:20 | 1071 | 462831380-462831383 | `ana2y2Yv...` | Rakurai | Rakurai | equal_fee | pre300 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261028T055501Z` | 227 | 2026-10-29 09:32:18 | 1071 | 462831652-462831655 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | equal_fee | pre300 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261028T055501Z` | 228 | 2026-10-29 09:33:27 | 1071 | 462831976-462831979 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | equal_fee | pre300 | 12 | 0 | HarmonicAgave | 60120 |
| `campaign-mainnet-20261028T055501Z` | 229 | 2026-10-29 09:34:02 | 1071 | 462832140-462832143 | `HEL1USMZ...` | JitoLabs | JitoLabs | equal_fee | pre300 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261028T055501Z` | 230 | 2026-10-29 09:34:37 | 1071 | 462832304-462832307 | `E1r4Psq8...` | JitoLabs | JitoLabs | equal_fee | slot2 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261028T055501Z` | 231 | 2026-10-29 09:35:15 | 1071 | 462832484-462832487 | `DRpbCBMx...` | AgaveBam | AgaveBam | equal_fee | pre300 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261028T055501Z` | 232 | 2026-10-29 09:35:58 | 1071 | 462832684-462832687 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | equal_fee | slot2 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261028T055501Z` | 233 | 2026-10-29 09:36:43 | 1071 | 462832896-462832899 | `BFmqBsaG...` | Firedancer | Firedancer | equal_fee | pre300 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261028T055501Z` | 234 | 2026-10-29 09:37:43 | 1071 | 462833172-462833175 | `5Cchr1XG...` | AgaveBam | AgaveBam | equal_fee | slot2 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261028T055501Z` | 235 | 2026-10-29 09:40:04 | 1071 | 462833824-462833827 | `7QQGNm3p...` | Agave | Agave | equal_fee | pre300 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261028T055501Z` | 236 | 2026-10-29 09:41:33 | 1071 | 462834240-462834243 | `LA1NEzry...` | FireBAM | FireBAM | equal_fee | slot2 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261029T120927Z` | 237 | 2026-10-29 13:20:08 | 1071 | 462895568-462895571 | `4VRs6A9z...` | Firedancer | Firedancer | equal_fee | slot2 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261029T120927Z` | 238 | 2026-10-29 13:23:20 | 1071 | 462896460-462896463 | `LA1NEzry...` | FireBAM | FireBAM | equal_fee | slot2 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261029T120927Z` | 239 | 2026-10-29 13:24:48 | 1071 | 462896880-462896883 | `ana2y2Yv...` | Rakurai | Rakurai | equal_fee | pre300 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261029T120927Z` | 240 | 2026-10-29 13:26:19 | 1071 | 462897308-462897311 | `7QQGNm3p...` | Agave | Agave | equal_fee | pre300 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261029T120927Z` | 241 | 2026-10-29 13:27:15 | 1071 | 462897568-462897571 | `5Cchr1XG...` | AgaveBam | AgaveBam | equal_fee | slot2 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261029T120927Z` | 242 | 2026-10-29 13:28:06 | 1071 | 462897804-462897807 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | equal_fee | pre300 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261029T120927Z` | 243 | 2026-10-29 13:28:40 | 1071 | 462897964-462897967 | `9jxgosAf...` | FireBAM | FireBAM | equal_fee | pre300 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261029T120927Z` | 244 | 2026-10-29 13:29:32 | 1071 | 462898200-462898203 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | equal_fee | pre300 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261029T120927Z` | 245 | 2026-10-29 13:30:11 | 1071 | 462898380-462898383 | `HEL1USMZ...` | JitoLabs | JitoLabs | equal_fee | pre300 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261029T120927Z` | 246 | 2026-10-29 13:31:21 | 1071 | 462898704-462898707 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | equal_fee | slot2 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261029T120927Z` | 247 | 2026-10-29 13:32:03 | 1071 | 462898900-462898903 | `5Us18hLZ...` | Agave | Agave | equal_fee | slot2 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261029T120927Z` | 248 | 2026-10-29 13:32:41 | 1071 | 462899076-462899079 | `DRpbCBMx...` | AgaveBam | AgaveBam | equal_fee | pre300 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261029T120927Z` | 249 | 2026-10-29 13:33:20 | 1071 | 462899260-462899263 | `E3mDbFMr...` | Rakurai | Rakurai | equal_fee | slot2 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261029T120927Z` | 250 | 2026-10-29 13:34:38 | 1071 | 462899620-462899623 | `E1r4Psq8...` | JitoLabs | JitoLabs | equal_fee | slot2 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261029T120927Z` | 251 | 2026-10-29 13:35:30 | 1071 | 462899868-462899871 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | equal_fee | slot2 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261029T120927Z` | 252 | 2026-10-29 13:39:57 | 1071 | 462901120-462901123 | `BFmqBsaG...` | Firedancer | Firedancer | equal_fee | pre300 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261029T120927Z` | 253 | 2026-10-29 18:55:47 | 1071 | 462989656-462989659 | `LA1NEzry...` | FireBAM | FireBAM | denominator | pre300 | 12 | 9 | AgaveBam | 60000 |
| `campaign-mainnet-20261029T120927Z` | 254 | 2026-10-29 18:57:57 | 1071 | 462990264-462990267 | `4VRs6A9z...` | Firedancer | Firedancer | denominator | pre300 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261029T120927Z` | 255 | 2026-10-29 19:02:27 | 1071 | 462991520-462991523 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | denominator | slot2 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261029T120927Z` | 256 | 2026-10-29 19:03:12 | 1071 | 462991728-462991731 | `E1r4Psq8...` | JitoLabs | JitoLabs | denominator | pre300 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261029T120927Z` | 257 | 2026-10-29 19:04:13 | 1071 | 462992016-462992019 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | denominator | pre300 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261029T120927Z` | 258 | 2026-10-29 19:05:15 | 1071 | 462992308-462992311 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | denominator | pre300 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261029T120927Z` | 259 | 2026-10-29 19:06:21 | 1071 | 462992616-462992619 | `HEL1USMZ...` | JitoLabs | JitoLabs | denominator | slot2 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261029T120927Z` | 260 | 2026-10-29 19:07:09 | 1071 | 462992848-462992851 | `ana2y2Yv...` | Rakurai | Rakurai | denominator | slot2 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261029T120927Z` | 261 | 2026-10-29 19:07:55 | 1071 | 462993068-462993071 | `9jxgosAf...` | FireBAM | FireBAM | denominator | slot2 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261029T120927Z` | 262 | 2026-10-29 19:08:30 | 1071 | 462993232-462993235 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | denominator | slot2 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261029T120927Z` | 263 | 2026-10-29 19:09:05 | 1071 | 462993392-462993395 | `5Cchr1XG...` | AgaveBam | AgaveBam | denominator | pre300 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261029T120927Z` | 264 | 2026-10-29 19:09:42 | 1071 | 462993564-462993567 | `DRpbCBMx...` | AgaveBam | AgaveBam | denominator | slot2 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261029T120927Z` | 265 | 2026-10-29 19:11:01 | 1071 | 462993936-462993939 | `5Us18hLZ...` | Agave | Agave | denominator | pre300 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261029T120927Z` | 266 | 2026-10-29 19:12:28 | 1071 | 462994340-462994343 | `7QQGNm3p...` | Agave | Agave | denominator | slot2 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261029T120927Z` | 267 | 2026-10-29 19:14:08 | 1071 | 462994804-462994807 | `E3mDbFMr...` | Rakurai | Rakurai | denominator | pre300 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261029T120927Z` | 268 | 2026-10-29 19:15:25 | 1071 | 462995168-462995171 | `BFmqBsaG...` | Firedancer | Firedancer | denominator | slot2 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261029T120927Z` | 269 | 2026-10-29 20:04:16 | 1071 | 463008832-463008835 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261029T120927Z` | 270 | 2026-10-29 20:04:57 | 1071 | 463009028-463009031 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261029T120927Z` | 271 | 2026-10-29 20:06:13 | 1071 | 463009380-463009383 | `9jxgosAf...` | FireBAM | FireBAM | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261029T120927Z` | 272 | 2026-10-29 20:06:48 | 1071 | 463009544-463009547 | `LA1NEzry...` | FireBAM | FireBAM | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261029T120927Z` | 273 | 2026-10-29 20:07:29 | 1071 | 463009736-463009739 | `E3mDbFMr...` | Rakurai | Rakurai | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261029T120927Z` | 274 | 2026-10-29 20:08:19 | 1071 | 463009972-463009975 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261029T120927Z` | 275 | 2026-10-29 20:09:01 | 1071 | 463010164-463010167 | `HEL1USMZ...` | JitoLabs | JitoLabs | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261029T120927Z` | 276 | 2026-10-29 20:09:41 | 1071 | 463010352-463010355 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261029T120927Z` | 277 | 2026-10-29 20:10:39 (tool clock) | 1071 | 463010612-463010615 | `5Cchr1XG...` | AgaveBam | AgaveBam | shared | slot2 | 0 | 0 | - | 0 |
| `campaign-mainnet-20261029T120927Z` | 278 | 2026-10-29 20:11:14 | 1071 | 463010788-463010791 | `DRpbCBMx...` | AgaveBam | AgaveBam | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261029T120927Z` | 279 | 2026-10-29 20:12:12 | 1071 | 463011060-463011063 | `4VRs6A9z...` | Firedancer | Firedancer | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261029T120927Z` | 280 | 2026-10-29 20:12:57 | 1071 | 463011264-463011267 | `BFmqBsaG...` | Firedancer | Firedancer | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261029T120927Z` | 281 | 2026-10-29 20:14:12 | 1071 | 463011620-463011623 | `7QQGNm3p...` | Agave | Agave | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261029T120927Z` | 282 | 2026-10-29 20:15:07 | 1071 | 463011876-463011879 | `E1r4Psq8...` | JitoLabs | JitoLabs | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261029T120927Z` | 283 | 2026-10-29 20:15:53 | 1071 | 463012092-463012095 | `ana2y2Yv...` | Rakurai | Rakurai | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261029T120927Z` | 284 | 2026-10-29 20:18:39 | 1071 | 463012868-463012871 | `5Us18hLZ...` | Agave | Agave | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261029T120927Z` | 285 | 2026-10-30 01:02:46 | 1071 | 463092440-463092443 | `BFmqBsaG...` | Firedancer | Firedancer | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261029T120927Z` | 286 | 2026-10-30 01:05:13 | 1071 | 463093128-463093131 | `4VRs6A9z...` | Firedancer | Firedancer | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261029T120927Z` | 287 | 2026-10-30 01:06:51 | 1071 | 463093596-463093599 | `5Cchr1XG...` | AgaveBam | AgaveBam | independent | pre300 | 12 | 11 | AgaveBam | 63330 |
| `campaign-mainnet-20261029T120927Z` | 288 | 2026-10-30 01:07:33 | 1071 | 463093792-463093795 | `5Us18hLZ...` | Agave | Agave | independent | pre300 | 12 | 7 | JitoLabs | 63330 |
| `campaign-mainnet-20261029T120927Z` | 289 | 2026-10-30 01:08:15 | 1071 | 463093992-463093995 | `ana2y2Yv...` | Rakurai | Rakurai | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261029T120927Z` | 290 | 2026-10-30 01:08:49 | 1071 | 463094152-463094155 | `5Us18hLZ...` | Agave | Agave | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261029T120927Z` | 291 | 2026-10-30 01:10:27 | 1071 | 463094608-463094611 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261029T120927Z` | 292 | 2026-10-30 01:11:05 | 1071 | 463094792-463094795 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261029T120927Z` | 293 | 2026-10-30 01:11:40 | 1071 | 463094956-463094959 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | independent | slot2 | 12 | 10 | HarmonicAgave | 63330 |
| `campaign-mainnet-20261029T120927Z` | 294 | 2026-10-30 01:12:39 | 1071 | 463095236-463095239 | `HEL1USMZ...` | JitoLabs | JitoLabs | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261029T120927Z` | 295 | 2026-10-30 01:13:50 | 1071 | 463095568-463095571 | `E1r4Psq8...` | JitoLabs | JitoLabs | independent | pre300 | 12 | 9 | JitoLabs | 63330 |
| `campaign-mainnet-20261029T120927Z` | 296 | 2026-10-30 01:14:31 | 1071 | 463095760-463095763 | `E1r4Psq8...` | JitoLabs | JitoLabs | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261029T120927Z` | 297 | 2026-10-30 01:15:36 | 1071 | 463096060-463096063 | `DRpbCBMx...` | AgaveBam | AgaveBam | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261029T120927Z` | 298 | 2026-10-30 01:16:33 | 1071 | 463096328-463096331 | `9jxgosAf...` | FireBAM | FireBAM | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261029T120927Z` | 299 | 2026-10-30 01:17:39 | 1071 | 463096640-463096643 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261029T120927Z` | 300 | 2026-10-30 01:19:02 | 1071 | 463097020-463097023 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261029T120927Z` | 301 | 2026-10-30 01:19:40 | 1071 | 463097196-463097199 | `9jxgosAf...` | FireBAM | FireBAM | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261029T120927Z` | 302 | 2026-10-30 01:20:17 | 1071 | 463097368-463097371 | `5Cchr1XG...` | AgaveBam | AgaveBam | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261029T120927Z` | 303 | 2026-10-30 01:21:20 | 1071 | 463097660-463097663 | `E3mDbFMr...` | Rakurai | Rakurai | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261029T120927Z` | 304 | 2026-10-30 01:22:01 | 1071 | 463097856-463097859 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | independent | pre300 | 12 | 11 | AgaveBam | 63330 |
| `campaign-mainnet-20261029T120927Z` | 305 | 2026-10-30 01:23:40 | 1071 | 463098312-463098315 | `LA1NEzry...` | FireBAM | FireBAM | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261029T120927Z` | 306 | 2026-10-30 01:25:01 | 1071 | 463098696-463098699 | `E3mDbFMr...` | Rakurai | Rakurai | independent | pre300 | 12 | 10 | AgaveBam | 63330 |
| `campaign-mainnet-20261029T120927Z` | 307 | 2026-10-30 01:27:30 | 1071 | 463099392-463099395 | `7QQGNm3p...` | Agave | Agave | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261029T120927Z` | 308 | 2026-10-30 01:36:49 | 1071 | 463102024-463102027 | `BFmqBsaG...` | Firedancer | Firedancer | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 309 | 2026-10-30 04:32:23 | 1072 | 463151364-463151367 | `LA1NEzry...` | FireBAM | FireBAM | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 310 | 2026-10-30 04:32:58 | 1072 | 463151528-463151531 | `5Us18hLZ...` | Agave | Agave | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 311 | 2026-10-30 04:36:11 | 1072 | 463152432-463152435 | `4VRs6A9z...` | Firedancer | Firedancer | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 312 | 2026-10-30 04:44:02 | 1072 | 463154640-463154643 | `DRpbCBMx...` | AgaveBam | AgaveBam | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 313 | 2026-10-30 04:45:03 | 1072 | 463154928-463154931 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 314 | 2026-10-30 04:45:47 | 1072 | 463155140-463155143 | `5Cchr1XG...` | AgaveBam | AgaveBam | independent | pre300 | 12 | 11 | AgaveBam | 63330 |
| `campaign-mainnet-20261030T015219Z` | 315 | 2026-10-30 04:46:26 | 1072 | 463155320-463155323 | `HEL1USMZ...` | JitoLabs | JitoLabs | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 316 | 2026-10-30 04:47:00 | 1072 | 463155480-463155483 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 317 | 2026-10-30 04:47:35 | 1072 | 463155648-463155651 | `E1r4Psq8...` | JitoLabs | JitoLabs | independent | pre300 | 12 | 8 | HarmonicFiredancer | 63330 |
| `campaign-mainnet-20261030T015219Z` | 318 | 2026-10-30 04:48:09 | 1072 | 463155808-463155811 | `E1r4Psq8...` | JitoLabs | JitoLabs | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 319 | 2026-10-30 04:49:08 | 1072 | 463156080-463156083 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 320 | 2026-10-30 04:50:11 | 1072 | 463156372-463156375 | `9jxgosAf...` | FireBAM | FireBAM | independent | slot2 | 12 | 10 | AgaveBam | 63330 |
| `campaign-mainnet-20261030T015219Z` | 321 | 2026-10-30 04:50:57 | 1072 | 463156592-463156595 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | independent | slot2 | 12 | 10 | Firedancer | 63330 |
| `campaign-mainnet-20261030T015219Z` | 322 | 2026-10-30 04:51:35 | 1072 | 463156768-463156771 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 323 | 2026-10-30 04:52:13 | 1072 | 463156948-463156951 | `5Cchr1XG...` | AgaveBam | AgaveBam | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 324 | 2026-10-30 04:53:03 | 1072 | 463157172-463157175 | `ana2y2Yv...` | Rakurai | Rakurai | independent | slot2 | 12 | 8 | HarmonicAgave | 63330 |
| `campaign-mainnet-20261030T015219Z` | 325 | 2026-10-30 04:53:36 | 1072 | 463157332-463157335 | `ana2y2Yv...` | Rakurai | Rakurai | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 326 | 2026-10-30 04:54:19 | 1072 | 463157528-463157531 | `7QQGNm3p...` | Agave | Agave | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 327 | 2026-10-30 04:54:53 | 1072 | 463157692-463157695 | `BFmqBsaG...` | Firedancer | Firedancer | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 328 | 2026-10-30 04:55:38 | 1072 | 463157900-463157903 | `9jxgosAf...` | FireBAM | FireBAM | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 329 | 2026-10-30 04:56:43 | 1072 | 463158208-463158211 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | independent | slot2 | 12 | 10 | HarmonicFiredancer | 63330 |
| `campaign-mainnet-20261030T015219Z` | 330 | 2026-10-30 05:02:16 | 1072 | 463159772-463159775 | `E3mDbFMr...` | Rakurai | Rakurai | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 331 | 2026-10-30 05:07:47 | 1072 | 463161324-463161327 | `5Us18hLZ...` | Agave | Agave | independent | pre300 | 12 | 8 | HarmonicFiredancer | 63330 |
| `campaign-mainnet-20261030T015219Z` | 332 | 2026-10-30 05:10:42 | 1072 | 463162152-463162155 | `4VRs6A9z...` | Firedancer | Firedancer | independent | pre300 | 12 | 8 | HarmonicAgave | 63330 |
| `campaign-mainnet-20261030T015219Z` | 333 | 2026-10-30 06:07:11 | 1072 | 463178020-463178023 | `LA1NEzry...` | FireBAM | FireBAM | denominator | slot2 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261030T015219Z` | 334 | 2026-10-30 06:17:20 | 1072 | 463180864-463180867 | `7QQGNm3p...` | Agave | Agave | denominator | pre300 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261030T015219Z` | 335 | 2026-10-30 06:19:46 | 1072 | 463181544-463181547 | `E3mDbFMr...` | Rakurai | Rakurai | denominator | slot2 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261030T015219Z` | 336 | 2026-10-30 06:20:22 | 1072 | 463181712-463181715 | `BFmqBsaG...` | Firedancer | Firedancer | denominator | pre300 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261030T015219Z` | 337 | 2026-10-30 06:21:21 | 1072 | 463181988-463181991 | `ana2y2Yv...` | Rakurai | Rakurai | denominator | pre300 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261030T015219Z` | 338 | 2026-10-30 06:22:01 | 1072 | 463182172-463182175 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | denominator | slot2 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261030T015219Z` | 339 | 2026-10-30 06:22:43 | 1072 | 463182372-463182375 | `9jxgosAf...` | FireBAM | FireBAM | denominator | pre300 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261030T015219Z` | 340 | 2026-10-30 06:23:37 | 1072 | 463182624-463182627 | `E1r4Psq8...` | JitoLabs | JitoLabs | denominator | slot2 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261030T015219Z` | 341 | 2026-10-30 06:24:10 | 1072 | 463182784-463182787 | `DRpbCBMx...` | AgaveBam | AgaveBam | denominator | pre300 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261030T015219Z` | 342 | 2026-10-30 06:24:48 | 1072 | 463182964-463182967 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | denominator | pre300 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261030T015219Z` | 343 | 2026-10-30 06:25:48 | 1072 | 463183244-463183247 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | denominator | slot2 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261030T015219Z` | 344 | 2026-10-30 06:26:30 | 1072 | 463183444-463183447 | `5Cchr1XG...` | AgaveBam | AgaveBam | denominator | slot2 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261030T015219Z` | 345 | 2026-10-30 06:27:44 | 1072 | 463183792-463183795 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | denominator | pre300 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261030T015219Z` | 346 | 2026-10-30 06:28:27 | 1072 | 463183996-463183999 | `HEL1USMZ...` | JitoLabs | JitoLabs | denominator | pre300 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261030T015219Z` | 347 | 2026-10-30 06:29:22 | 1072 | 463184252-463184255 | `5Us18hLZ...` | Agave | Agave | denominator | slot2 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261030T015219Z` | 348 | 2026-10-30 06:44:22 | 1072 | 463188484-463188487 | `4VRs6A9z...` | Firedancer | Firedancer | denominator | slot2 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261030T015219Z` | 349 | 2026-10-30 07:57:52 | 1072 | 463209112-463209115 | `4VRs6A9z...` | Firedancer | Firedancer | equal_fee | pre300 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261030T015219Z` | 350 | 2026-10-30 08:04:12 | 1072 | 463210888-463210891 | `5Cchr1XG...` | AgaveBam | AgaveBam | equal_fee | pre300 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261030T015219Z` | 351 | 2026-10-30 08:05:13 | 1072 | 463211172-463211175 | `LA1NEzry...` | FireBAM | FireBAM | equal_fee | pre300 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261030T015219Z` | 352 | 2026-10-30 08:06:22 | 1072 | 463211496-463211499 | `ana2y2Yv...` | Rakurai | Rakurai | equal_fee | slot2 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261030T015219Z` | 353 | 2026-10-30 08:07:41 | 1072 | 463211868-463211871 | `9jxgosAf...` | FireBAM | FireBAM | equal_fee | slot2 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261030T015219Z` | 354 | 2026-10-30 08:08:17 | 1072 | 463212036-463212039 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | equal_fee | slot2 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261030T015219Z` | 355 | 2026-10-30 08:08:52 | 1072 | 463212196-463212199 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | equal_fee | pre300 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261030T015219Z` | 356 | 2026-10-30 08:09:38 | 1072 | 463212412-463212415 | `DRpbCBMx...` | AgaveBam | AgaveBam | equal_fee | slot2 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261030T015219Z` | 357 | 2026-10-30 08:10:20 | 1072 | 463212608-463212611 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | equal_fee | pre300 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261030T015219Z` | 358 | 2026-10-30 08:10:54 | 1072 | 463212768-463212771 | `HEL1USMZ...` | JitoLabs | JitoLabs | equal_fee | slot2 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261030T015219Z` | 359 | 2026-10-30 08:11:56 | 1072 | 463213060-463213063 | `E1r4Psq8...` | JitoLabs | JitoLabs | equal_fee | pre300 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261030T015219Z` | 360 | 2026-10-30 08:13:19 | 1072 | 463213448-463213451 | `5Us18hLZ...` | Agave | Agave | equal_fee | pre300 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261030T015219Z` | 361 | 2026-10-30 08:13:54 | 1072 | 463213612-463213615 | `7QQGNm3p...` | Agave | Agave | equal_fee | slot2 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261030T015219Z` | 362 | 2026-10-30 08:14:46 | 1072 | 463213856-463213859 | `E3mDbFMr...` | Rakurai | Rakurai | equal_fee | pre300 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261030T015219Z` | 363 | 2026-10-30 08:15:27 | 1072 | 463214052-463214055 | `BFmqBsaG...` | Firedancer | Firedancer | equal_fee | slot2 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261030T015219Z` | 364 | 2026-10-30 08:16:44 | 1072 | 463214408-463214411 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | equal_fee | slot2 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261030T015219Z` | 365 | 2026-10-30 12:48:24 | 1072 | 463290796-463290799 | `7QQGNm3p...` | Agave | Agave | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 366 | 2026-10-30 12:49:05 | 1072 | 463290984-463290987 | `9jxgosAf...` | FireBAM | FireBAM | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 367 | 2026-10-30 12:50:47 | 1072 | 463291468-463291471 | `4VRs6A9z...` | Firedancer | Firedancer | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 368 | 2026-10-30 12:52:07 | 1072 | 463291836-463291839 | `E3mDbFMr...` | Rakurai | Rakurai | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 369 | 2026-10-30 12:52:42 | 1072 | 463291996-463291999 | `E1r4Psq8...` | JitoLabs | JitoLabs | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 370 | 2026-10-30 12:53:28 | 1072 | 463292212-463292215 | `BFmqBsaG...` | Firedancer | Firedancer | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 371 | 2026-10-30 12:54:43 | 1072 | 463292564-463292567 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 372 | 2026-10-30 12:55:27 | 1072 | 463292772-463292775 | `HEL1USMZ...` | JitoLabs | JitoLabs | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 373 | 2026-10-30 12:56:01 | 1072 | 463292932-463292935 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 374 | 2026-10-30 12:56:36 | 1072 | 463293096-463293099 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 375 | 2026-10-30 12:57:15 | 1072 | 463293276-463293279 | `DRpbCBMx...` | AgaveBam | AgaveBam | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 376 | 2026-10-30 12:58:24 | 1072 | 463293600-463293603 | `ana2y2Yv...` | Rakurai | Rakurai | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 377 | 2026-10-30 12:59:01 | 1072 | 463293764-463293767 | `5Us18hLZ...` | Agave | Agave | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 378 | 2026-10-30 12:59:37 | 1072 | 463293936-463293939 | `5Cchr1XG...` | AgaveBam | AgaveBam | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 379 | 2026-10-30 13:00:15 | 1072 | 463294116-463294119 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 380 | 2026-10-30 13:11:24 | 1072 | 463297260-463297263 | `LA1NEzry...` | FireBAM | FireBAM | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 381 | 2026-10-30 15:29:34 | 1072 | 463336068-463336071 | `LA1NEzry...` | FireBAM | FireBAM | equal_fee | pre300 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261030T015219Z` | 382 | 2026-10-30 15:44:14 | 1072 | 463340180-463340183 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | equal_fee | pre300 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261030T015219Z` | 383 | 2026-10-30 15:45:15 | 1072 | 463340464-463340467 | `E3mDbFMr...` | Rakurai | Rakurai | equal_fee | pre300 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261030T015219Z` | 384 | 2026-10-30 15:46:26 | 1072 | 463340796-463340799 | `9jxgosAf...` | FireBAM | FireBAM | equal_fee | slot2 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261030T015219Z` | 385 | 2026-10-30 15:47:19 | 1072 | 463341040-463341043 | `HEL1USMZ...` | JitoLabs | JitoLabs | equal_fee | slot2 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261030T015219Z` | 386 | 2026-10-30 15:48:07 | 1072 | 463341268-463341271 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | equal_fee | slot2 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261030T015219Z` | 387 | 2026-10-30 15:48:46 | 1072 | 463341452-463341455 | `5Us18hLZ...` | Agave | Agave | equal_fee | pre300 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261030T015219Z` | 388 | 2026-10-30 15:49:51 | 1072 | 463341756-463341759 | `5Cchr1XG...` | AgaveBam | AgaveBam | equal_fee | pre300 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261030T015219Z` | 389 | 2026-10-30 15:50:36 | 1072 | 463341964-463341967 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | equal_fee | pre300 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261030T015219Z` | 390 | 2026-10-30 15:51:24 | 1072 | 463342188-463342191 | `7QQGNm3p...` | Agave | Agave | equal_fee | slot2 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261030T015219Z` | 391 | 2026-10-30 15:52:02 | 1072 | 463342376-463342379 | `E1r4Psq8...` | JitoLabs | JitoLabs | equal_fee | pre300 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261030T015219Z` | 392 | 2026-10-30 15:52:44 | 1072 | 463342568-463342571 | `DRpbCBMx...` | AgaveBam | AgaveBam | equal_fee | slot2 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261030T015219Z` | 393 | 2026-10-30 15:53:39 | 1072 | 463342828-463342831 | `ana2y2Yv...` | Rakurai | Rakurai | equal_fee | slot2 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261030T015219Z` | 394 | 2026-10-30 15:54:22 | 1072 | 463343032-463343035 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | equal_fee | slot2 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261030T015219Z` | 395 | 2026-10-30 15:56:41 | 1072 | 463343688-463343691 | `4VRs6A9z...` | Firedancer | Firedancer | equal_fee | pre300 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261030T015219Z` | 396 | 2026-10-30 16:00:05 | 1072 | 463344632-463344635 | `BFmqBsaG...` | Firedancer | Firedancer | equal_fee | slot2 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261030T015219Z` | 397 | 2026-10-30 19:08:40 | 1072 | 463397412-463397415 | `BFmqBsaG...` | Firedancer | Firedancer | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 398 | 2026-10-30 19:09:33 | 1072 | 463397656-463397659 | `E3mDbFMr...` | Rakurai | Rakurai | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 399 | 2026-10-30 19:10:22 | 1072 | 463397884-463397887 | `ana2y2Yv...` | Rakurai | Rakurai | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 400 | 2026-10-30 19:11:16 | 1072 | 463398140-463398143 | `5Cchr1XG...` | AgaveBam | AgaveBam | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 401 | 2026-10-30 19:12:07 | 1072 | 463398376-463398379 | `DRpbCBMx...` | AgaveBam | AgaveBam | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 402 | 2026-10-30 19:12:48 | 1072 | 463398564-463398567 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 403 | 2026-10-30 19:13:27 | 1072 | 463398744-463398747 | `5Us18hLZ...` | Agave | Agave | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 404 | 2026-10-30 19:14:03 | 1072 | 463398908-463398911 | `HEL1USMZ...` | JitoLabs | JitoLabs | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 405 | 2026-10-30 19:14:39 | 1072 | 463399072-463399075 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 406 | 2026-10-30 19:15:32 | 1072 | 463399316-463399319 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 407 | 2026-10-30 19:16:06 | 1072 | 463399480-463399483 | `E1r4Psq8...` | JitoLabs | JitoLabs | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 408 | 2026-10-30 19:16:40 | 1072 | 463399640-463399643 | `9jxgosAf...` | FireBAM | FireBAM | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 409 | 2026-10-30 19:18:00 | 1072 | 463400016-463400019 | `7QQGNm3p...` | Agave | Agave | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 410 | 2026-10-30 19:19:02 | 1072 | 463400308-463400311 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 411 | 2026-10-30 19:27:29 | 1072 | 463402696-463402699 | `4VRs6A9z...` | Firedancer | Firedancer | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 412 | 2026-10-30 19:33:36 | 1072 | 463404400-463404403 | `LA1NEzry...` | FireBAM | FireBAM | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 413 | 2026-10-30 23:36:25 | 1072 | 463472300-463472303 | `5Us18hLZ...` | Agave | Agave | denominator | slot2 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261030T015219Z` | 414 | 2026-10-30 23:37:38 | 1072 | 463472644-463472647 | `BFmqBsaG...` | Firedancer | Firedancer | denominator | pre300 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261030T015219Z` | 415 | 2026-10-30 23:38:24 | 1072 | 463472856-463472859 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | denominator | slot2 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261030T015219Z` | 416 | 2026-10-30 23:39:20 | 1072 | 463473120-463473123 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | denominator | pre300 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261030T015219Z` | 417 | 2026-10-30 23:39:56 | 1072 | 463473284-463473287 | `5Cchr1XG...` | AgaveBam | AgaveBam | denominator | slot2 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261030T015219Z` | 418 | 2026-10-30 23:40:48 | 1072 | 463473532-463473535 | `E3mDbFMr...` | Rakurai | Rakurai | denominator | slot2 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261030T015219Z` | 419 | 2026-10-30 23:41:30 | 1072 | 463473728-463473731 | `E1r4Psq8...` | JitoLabs | JitoLabs | denominator | slot2 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261030T015219Z` | 420 | 2026-10-30 23:42:07 | 1072 | 463473900-463473903 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | denominator | pre300 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261030T015219Z` | 421 | 2026-10-30 23:43:13 | 1072 | 463474212-463474215 | `ana2y2Yv...` | Rakurai | Rakurai | denominator | pre300 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261030T015219Z` | 422 | 2026-10-30 23:44:09 | 1072 | 463474472-463474475 | `9jxgosAf...` | FireBAM | FireBAM | denominator | pre300 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261030T015219Z` | 423 | 2026-10-30 23:44:51 | 1072 | 463474668-463474671 | `HEL1USMZ...` | JitoLabs | JitoLabs | denominator | pre300 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261030T015219Z` | 424 | 2026-10-30 23:45:44 | 1072 | 463474920-463474923 | `DRpbCBMx...` | AgaveBam | AgaveBam | denominator | pre300 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261030T015219Z` | 425 | 2026-10-30 23:46:24 | 1072 | 463475108-463475111 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | denominator | slot2 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261030T015219Z` | 426 | 2026-10-30 23:47:46 | 1072 | 463475492-463475495 | `7QQGNm3p...` | Agave | Agave | denominator | pre300 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261030T015219Z` | 427 | 2026-10-30 23:50:33 | 1072 | 463476256-463476259 | `4VRs6A9z...` | Firedancer | Firedancer | denominator | slot2 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261030T015219Z` | 428 | 2026-10-30 23:56:59 | 1072 | 463478072-463478075 | `LA1NEzry...` | FireBAM | FireBAM | denominator | slot2 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261030T015219Z` | 429 | 2026-10-31 00:40:44 | 1072 | 463490296-463490299 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 430 | 2026-10-31 00:41:23 | 1072 | 463490480-463490483 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 431 | 2026-10-31 00:42:00 | 1072 | 463490652-463490655 | `ana2y2Yv...` | Rakurai | Rakurai | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 432 | 2026-10-31 00:42:47 | 1072 | 463490872-463490875 | `BFmqBsaG...` | Firedancer | Firedancer | independent | slot2 | 12 | 9 | HarmonicAgave | 63330 |
| `campaign-mainnet-20261030T015219Z` | 433 | 2026-10-31 00:43:23 | 1072 | 463491044-463491047 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | independent | pre300 | 12 | 11 | ? | 63330 |
| `campaign-mainnet-20261030T015219Z` | 434 | 2026-10-31 00:44:19 | 1072 | 463491304-463491307 | `LA1NEzry...` | FireBAM | FireBAM | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 435 | 2026-10-31 00:45:01 | 1072 | 463491496-463491499 | `DRpbCBMx...` | AgaveBam | AgaveBam | independent | slot2 | 12 | 7 | JitoLabs | 63330 |
| `campaign-mainnet-20261030T015219Z` | 436 | 2026-10-31 00:46:05 | 1072 | 463491796-463491799 | `HEL1USMZ...` | JitoLabs | JitoLabs | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 437 | 2026-10-31 00:46:54 | 1072 | 463492024-463492027 | `E3mDbFMr...` | Rakurai | Rakurai | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 438 | 2026-10-31 00:47:46 | 1072 | 463492268-463492271 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 439 | 2026-10-31 00:48:44 | 1072 | 463492540-463492543 | `5Cchr1XG...` | AgaveBam | AgaveBam | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 440 | 2026-10-31 00:49:29 | 1072 | 463492752-463492755 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | independent | pre300 | 12 | 10 | ? | 63330 |
| `campaign-mainnet-20261030T015219Z` | 441 | 2026-10-31 00:50:06 | 1072 | 463492920-463492923 | `7QQGNm3p...` | Agave | Agave | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 442 | 2026-10-31 00:50:40 | 1072 | 463493084-463493087 | `9jxgosAf...` | FireBAM | FireBAM | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 443 | 2026-10-31 00:51:26 | 1072 | 463493300-463493303 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 444 | 2026-10-31 00:52:05 | 1072 | 463493476-463493479 | `E1r4Psq8...` | JitoLabs | JitoLabs | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 445 | 2026-10-31 00:52:45 | 1072 | 463493660-463493663 | `E3mDbFMr...` | Rakurai | Rakurai | independent | pre300 | 12 | 9 | HarmonicAgave | 63330 |
| `campaign-mainnet-20261030T015219Z` | 446 | 2026-10-31 00:53:23 | 1072 | 463493836-463493839 | `5Us18hLZ...` | Agave | Agave | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 447 | 2026-10-31 00:54:23 | 1072 | 463494120-463494123 | `HEL1USMZ...` | JitoLabs | JitoLabs | independent | slot2 | 12 | 9 | Firedancer | 63330 |
| `campaign-mainnet-20261030T015219Z` | 448 | 2026-10-31 00:54:58 | 1072 | 463494284-463494287 | `DRpbCBMx...` | AgaveBam | AgaveBam | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 449 | 2026-10-31 00:55:56 | 1072 | 463494556-463494559 | `BFmqBsaG...` | Firedancer | Firedancer | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 450 | 2026-10-31 00:58:06 | 1072 | 463495168-463495171 | `7QQGNm3p...` | Agave | Agave | independent | slot2 | 12 | 9 | AgaveBam | 63330 |
| `campaign-mainnet-20261030T015219Z` | 451 | 2026-10-31 01:10:38 | 1072 | 463498684-463498687 | `4VRs6A9z...` | Firedancer | Firedancer | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261030T015219Z` | 452 | 2026-10-31 01:24:18 | 1072 | 463502508-463502511 | `LA1NEzry...` | FireBAM | FireBAM | independent | pre300 | 12 | 10 | AgaveBam | 63330 |
| `campaign-mainnet-20261031T014357Z` | 453 | 2026-10-31 03:53:16 | 1073 | 463544140-463544143 | `BFmqBsaG...` | Firedancer | Firedancer | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 454 | 2026-10-31 03:56:33 | 1073 | 463545060-463545063 | `LA1NEzry...` | FireBAM | FireBAM | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 455 | 2026-10-31 03:58:42 | 1073 | 463545660-463545663 | `BFmqBsaG...` | Firedancer | Firedancer | independent | pre300 | 12 | 10 | HarmonicAgave | 63330 |
| `campaign-mainnet-20261031T014357Z` | 456 | 2026-10-31 04:07:27 | 1073 | 463548120-463548123 | `7QQGNm3p...` | Agave | Agave | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 457 | 2026-10-31 04:08:02 | 1073 | 463548280-463548283 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | independent | pre300 | 12 | 8 | ? | 63330 |
| `campaign-mainnet-20261031T014357Z` | 458 | 2026-10-31 04:08:49 | 1073 | 463548496-463548499 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 459 | 2026-10-31 04:09:37 | 1073 | 463548720-463548723 | `5Us18hLZ...` | Agave | Agave | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 460 | 2026-10-31 04:10:44 | 1073 | 463549036-463549039 | `ana2y2Yv...` | Rakurai | Rakurai | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 461 | 2026-10-31 04:11:20 | 1073 | 463549204-463549207 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 462 | 2026-10-31 04:11:54 | 1073 | 463549364-463549367 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 463 | 2026-10-31 04:12:55 | 1073 | 463549652-463549655 | `5Cchr1XG...` | AgaveBam | AgaveBam | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 464 | 2026-10-31 04:13:35 | 1073 | 463549836-463549839 | `DRpbCBMx...` | AgaveBam | AgaveBam | independent | pre300 | 12 | 10 | AgaveBam | 63330 |
| `campaign-mainnet-20261031T014357Z` | 465 | 2026-10-31 04:14:12 | 1073 | 463550004-463550007 | `9jxgosAf...` | FireBAM | FireBAM | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 466 | 2026-10-31 04:14:46 | 1073 | 463550164-463550167 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | independent | pre300 | 12 | 9 | JitoLabs | 63330 |
| `campaign-mainnet-20261031T014357Z` | 467 | 2026-10-31 04:15:24 | 1073 | 463550340-463550343 | `5Us18hLZ...` | Agave | Agave | independent | slot2 | 12 | 11 | AgaveBam | 63330 |
| `campaign-mainnet-20261031T014357Z` | 468 | 2026-10-31 04:16:08 | 1073 | 463550544-463550547 | `HEL1USMZ...` | JitoLabs | JitoLabs | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 469 | 2026-10-31 04:17:01 | 1073 | 463550788-463550791 | `E1r4Psq8...` | JitoLabs | JitoLabs | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 470 | 2026-10-31 04:17:46 | 1073 | 463551000-463551003 | `HEL1USMZ...` | JitoLabs | JitoLabs | independent | pre300 | 12 | 9 | JitoLabs | 63330 |
| `campaign-mainnet-20261031T014357Z` | 471 | 2026-10-31 04:18:42 | 1073 | 463551260-463551263 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 472 | 2026-10-31 04:19:35 | 1073 | 463551516-463551519 | `ana2y2Yv...` | Rakurai | Rakurai | independent | pre300 | 12 | 8 | JitoLabs | 63330 |
| `campaign-mainnet-20261031T014357Z` | 473 | 2026-10-31 04:20:20 | 1073 | 463551720-463551723 | `DRpbCBMx...` | AgaveBam | AgaveBam | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 474 | 2026-10-31 04:21:41 | 1073 | 463552096-463552099 | `4VRs6A9z...` | Firedancer | Firedancer | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 475 | 2026-10-31 04:24:50 | 1073 | 463552976-463552979 | `E3mDbFMr...` | Rakurai | Rakurai | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 476 | 2026-10-31 04:38:49 | 1073 | 463556908-463556911 | `LA1NEzry...` | FireBAM | FireBAM | independent | slot2 | 12 | 8 | Firedancer | 63330 |
| `campaign-mainnet-20261031T014357Z` | 477 | 2026-10-31 09:08:24 | 1073 | 463632444-463632447 | `5Us18hLZ...` | Agave | Agave | denominator | slot2 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261031T014357Z` | 478 | 2026-10-31 09:14:16 | 1073 | 463634104-463634107 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | denominator | pre300 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261031T014357Z` | 479 | 2026-10-31 09:14:58 | 1073 | 463634300-463634303 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | denominator | slot2 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261031T014357Z` | 480 | 2026-10-31 09:15:38 | 1073 | 463634488-463634491 | `E3mDbFMr...` | Rakurai | Rakurai | denominator | slot2 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261031T014357Z` | 481 | 2026-10-31 09:16:52 | 1073 | 463634836-463634839 | `LA1NEzry...` | FireBAM | FireBAM | denominator | slot2 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261031T014357Z` | 482 | 2026-10-31 09:17:34 | 1073 | 463635032-463635035 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | denominator | slot2 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261031T014357Z` | 483 | 2026-10-31 09:18:08 | 1073 | 463635192-463635195 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | denominator | pre300 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261031T014357Z` | 484 | 2026-10-31 09:19:15 | 1073 | 463635504-463635507 | `DRpbCBMx...` | AgaveBam | AgaveBam | denominator | pre300 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261031T014357Z` | 485 | 2026-10-31 09:19:51 | 1073 | 463635668-463635671 | `HEL1USMZ...` | JitoLabs | JitoLabs | denominator | pre300 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261031T014357Z` | 486 | 2026-10-31 09:20:42 | 1073 | 463635904-463635907 | `5Cchr1XG...` | AgaveBam | AgaveBam | denominator | slot2 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261031T014357Z` | 487 | 2026-10-31 09:21:18 | 1073 | 463636072-463636075 | `E1r4Psq8...` | JitoLabs | JitoLabs | denominator | slot2 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261031T014357Z` | 488 | 2026-10-31 09:22:00 | 1073 | 463636268-463636271 | `7QQGNm3p...` | Agave | Agave | denominator | pre300 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261031T014357Z` | 489 | 2026-10-31 09:23:21 | 1073 | 463636652-463636655 | `ana2y2Yv...` | Rakurai | Rakurai | denominator | pre300 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261031T014357Z` | 490 | 2026-10-31 09:25:52 | 1073 | 463637356-463637359 | `9jxgosAf...` | FireBAM | FireBAM | denominator | pre300 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261031T014357Z` | 491 | 2026-10-31 09:30:58 | 1073 | 463638788-463638791 | `BFmqBsaG...` | Firedancer | Firedancer | denominator | pre300 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261031T014357Z` | 492 | 2026-10-31 09:34:51 | 1073 | 463639876-463639879 | `4VRs6A9z...` | Firedancer | Firedancer | denominator | slot2 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261031T014357Z` | 493 | 2026-10-31 09:43:13 | 1073 | 463642220-463642223 | `5Us18hLZ...` | Agave | Agave | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 494 | 2026-10-31 09:46:21 | 1073 | 463643088-463643091 | `4VRs6A9z...` | Firedancer | Firedancer | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 495 | 2026-10-31 09:47:18 | 1073 | 463643352-463643355 | `BFmqBsaG...` | Firedancer | Firedancer | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 496 | 2026-10-31 09:49:21 | 1073 | 463643924-463643927 | `E3mDbFMr...` | Rakurai | Rakurai | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 497 | 2026-10-31 09:50:07 | 1073 | 463644136-463644139 | `LA1NEzry...` | FireBAM | FireBAM | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 498 | 2026-10-31 09:51:22 | 1073 | 463644492-463644495 | `7QQGNm3p...` | Agave | Agave | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 499 | 2026-10-31 09:51:59 | 1073 | 463644664-463644667 | `HEL1USMZ...` | JitoLabs | JitoLabs | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 500 | 2026-10-31 09:52:34 | 1073 | 463644824-463644827 | `9jxgosAf...` | FireBAM | FireBAM | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 501 | 2026-10-31 09:53:08 | 1073 | 463644988-463644991 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 502 | 2026-10-31 09:53:46 | 1073 | 463645164-463645167 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 503 | 2026-10-31 09:54:46 | 1073 | 463645444-463645447 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 504 | 2026-10-31 09:55:36 | 1073 | 463645680-463645683 | `DRpbCBMx...` | AgaveBam | AgaveBam | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 505 | 2026-10-31 09:56:23 | 1073 | 463645900-463645903 | `E1r4Psq8...` | JitoLabs | JitoLabs | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 506 | 2026-10-31 09:57:05 | 1073 | 463646100-463646103 | `ana2y2Yv...` | Rakurai | Rakurai | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 507 | 2026-10-31 09:57:41 | 1073 | 463646264-463646267 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 508 | 2026-10-31 09:58:17 | 1073 | 463646432-463646435 | `5Cchr1XG...` | AgaveBam | AgaveBam | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 509 | 2026-10-31 13:57:12 | 1073 | 463713440-463713443 | `BFmqBsaG...` | Firedancer | Firedancer | equal_fee | pre300 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261031T014357Z` | 510 | 2026-10-31 13:59:16 | 1073 | 463714024-463714027 | `7QQGNm3p...` | Agave | Agave | equal_fee | pre300 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261031T014357Z` | 511 | 2026-10-31 14:00:04 | 1073 | 463714248-463714251 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | equal_fee | slot2 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261031T014357Z` | 512 | 2026-10-31 14:00:53 | 1073 | 463714472-463714475 | `4VRs6A9z...` | Firedancer | Firedancer | equal_fee | slot2 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261031T014357Z` | 513 | 2026-10-31 14:01:45 | 1073 | 463714712-463714715 | `LA1NEzry...` | FireBAM | FireBAM | equal_fee | slot2 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261031T014357Z` | 514 | 2026-10-31 14:02:37 | 1073 | 463714956-463714959 | `E1r4Psq8...` | JitoLabs | JitoLabs | equal_fee | slot2 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261031T014357Z` | 515 | 2026-10-31 14:03:15 | 1073 | 463715132-463715135 | `DRpbCBMx...` | AgaveBam | AgaveBam | equal_fee | pre300 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261031T014357Z` | 516 | 2026-10-31 14:04:05 | 1073 | 463715368-463715371 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | equal_fee | pre300 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261031T014357Z` | 517 | 2026-10-31 14:05:13 | 1073 | 463715688-463715691 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | equal_fee | slot2 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261031T014357Z` | 518 | 2026-10-31 14:05:49 | 1073 | 463715856-463715859 | `HEL1USMZ...` | JitoLabs | JitoLabs | equal_fee | pre300 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261031T014357Z` | 519 | 2026-10-31 14:06:53 | 1073 | 463716152-463716155 | `ana2y2Yv...` | Rakurai | Rakurai | equal_fee | pre300 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261031T014357Z` | 520 | 2026-10-31 14:07:38 | 1073 | 463716368-463716371 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | equal_fee | pre300 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261031T014357Z` | 521 | 2026-10-31 14:08:13 | 1073 | 463716532-463716535 | `9jxgosAf...` | FireBAM | FireBAM | equal_fee | pre300 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261031T014357Z` | 522 | 2026-10-31 14:09:16 | 1073 | 463716824-463716827 | `5Us18hLZ...` | Agave | Agave | equal_fee | slot2 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261031T014357Z` | 523 | 2026-10-31 14:10:09 | 1073 | 463717072-463717075 | `E3mDbFMr...` | Rakurai | Rakurai | equal_fee | slot2 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261031T014357Z` | 524 | 2026-10-31 14:13:28 | 1073 | 463717996-463717999 | `5Cchr1XG...` | AgaveBam | AgaveBam | equal_fee | slot2 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261031T014357Z` | 525 | 2026-10-31 18:52:32 | 1073 | 463796148-463796151 | `4VRs6A9z...` | Firedancer | Firedancer | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 526 | 2026-10-31 19:00:41 | 1073 | 463798428-463798431 | `LA1NEzry...` | FireBAM | FireBAM | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 527 | 2026-10-31 19:03:18 | 1073 | 463799164-463799167 | `E3mDbFMr...` | Rakurai | Rakurai | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 528 | 2026-10-31 19:06:30 | 1073 | 463800056-463800059 | `HEL1USMZ...` | JitoLabs | JitoLabs | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 529 | 2026-10-31 19:07:40 | 1073 | 463800380-463800383 | `5Cchr1XG...` | AgaveBam | AgaveBam | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 530 | 2026-10-31 19:08:29 | 1073 | 463800612-463800615 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 531 | 2026-10-31 19:09:29 | 1073 | 463800896-463800899 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 532 | 2026-10-31 19:10:14 | 1073 | 463801104-463801107 | `5Us18hLZ...` | Agave | Agave | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 533 | 2026-10-31 19:11:13 | 1073 | 463801380-463801383 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 534 | 2026-10-31 19:12:14 | 1073 | 463801664-463801667 | `ana2y2Yv...` | Rakurai | Rakurai | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 535 | 2026-10-31 19:12:49 (tool clock) | 1073 | 463801828-463801831 | `DRpbCBMx...` | AgaveBam | AgaveBam | shared | slot2 | 0 | 0 | - | 0 |
| `campaign-mainnet-20261031T014357Z` | 536 | 2026-10-31 19:13:25 | 1073 | 463801992-463801995 | `E1r4Psq8...` | JitoLabs | JitoLabs | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 537 | 2026-10-31 19:14:05 | 1073 | 463802180-463802183 | `7QQGNm3p...` | Agave | Agave | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 538 | 2026-10-31 19:14:48 | 1073 | 463802380-463802383 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 539 | 2026-10-31 19:15:45 | 1073 | 463802644-463802647 | `9jxgosAf...` | FireBAM | FireBAM | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 540 | 2026-10-31 19:16:22 | 1073 | 463802816-463802819 | `BFmqBsaG...` | Firedancer | Firedancer | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 541 | 2026-10-31 21:00:19 | 1073 | 463831952-463831955 | `LA1NEzry...` | FireBAM | FireBAM | denominator | slot2 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261031T014357Z` | 542 | 2026-10-31 21:02:25 | 1073 | 463832544-463832547 | `7QQGNm3p...` | Agave | Agave | denominator | pre300 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261031T014357Z` | 543 | 2026-10-31 21:03:18 | 1073 | 463832788-463832791 | `BFmqBsaG...` | Firedancer | Firedancer | denominator | pre300 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261031T014357Z` | 544 | 2026-10-31 21:04:37 | 1073 | 463833160-463833163 | `HEL1USMZ...` | JitoLabs | JitoLabs | denominator | pre300 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261031T014357Z` | 545 | 2026-10-31 21:05:11 | 1073 | 463833320-463833323 | `DRpbCBMx...` | AgaveBam | AgaveBam | denominator | pre300 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261031T014357Z` | 546 | 2026-10-31 21:05:45 | 1073 | 463833480-463833483 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | denominator | pre300 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261031T014357Z` | 547 | 2026-10-31 21:06:27 | 1073 | 463833680-463833683 | `ana2y2Yv...` | Rakurai | Rakurai | denominator | pre300 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261031T014357Z` | 548 | 2026-10-31 21:07:10 | 1073 | 463833884-463833887 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | denominator | pre300 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261031T014357Z` | 549 | 2026-10-31 21:08:12 | 1073 | 463834172-463834175 | `5Us18hLZ...` | Agave | Agave | denominator | slot2 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261031T014357Z` | 550 | 2026-10-31 21:08:58 | 1073 | 463834380-463834383 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | denominator | slot2 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261031T014357Z` | 551 | 2026-10-31 21:09:57 | 1073 | 463834660-463834663 | `E3mDbFMr...` | Rakurai | Rakurai | denominator | slot2 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261031T014357Z` | 552 | 2026-10-31 21:10:46 | 1073 | 463834884-463834887 | `9jxgosAf...` | FireBAM | FireBAM | denominator | pre300 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261031T014357Z` | 553 | 2026-10-31 21:11:39 | 1073 | 463835132-463835135 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | denominator | slot2 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261031T014357Z` | 554 | 2026-10-31 21:12:23 | 1073 | 463835336-463835339 | `E1r4Psq8...` | JitoLabs | JitoLabs | denominator | slot2 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261031T014357Z` | 555 | 2026-10-31 21:15:46 (tool clock) | 1073 | 463836232-463836235 | `5Cchr1XG...` | AgaveBam | AgaveBam | denominator | slot2 | 0 | 0 | - | 0 |
| `campaign-mainnet-20261031T014357Z` | 556 | 2026-10-31 21:19:54 | 1073 | 463837440-463837443 | `4VRs6A9z...` | Firedancer | Firedancer | denominator | slot2 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261031T014357Z` | 557 | 2026-11-01 00:35:44 | 1073 | 463892364-463892367 | `5Us18hLZ...` | Agave | Agave | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 558 | 2026-11-01 00:37:23 | 1073 | 463892828-463892831 | `5Cchr1XG...` | AgaveBam | AgaveBam | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 559 | 2026-11-01 00:38:03 | 1073 | 463893016-463893019 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | independent | slot2 | 12 | 8 | HarmonicAgave | 63330 |
| `campaign-mainnet-20261031T014357Z` | 560 | 2026-11-01 00:39:20 | 1073 | 463893376-463893379 | `9jxgosAf...` | FireBAM | FireBAM | independent | pre300 | 12 | 9 | AgaveBam | 63330 |
| `campaign-mainnet-20261031T014357Z` | 561 | 2026-11-01 00:40:16 | 1073 | 463893632-463893635 | `E1r4Psq8...` | JitoLabs | JitoLabs | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 562 | 2026-11-01 00:40:51 | 1073 | 463893796-463893799 | `BFmqBsaG...` | Firedancer | Firedancer | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 563 | 2026-11-01 00:41:28 | 1073 | 463893964-463893967 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 564 | 2026-11-01 00:42:19 | 1073 | 463894200-463894203 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 565 | 2026-11-01 00:43:08 | 1073 | 463894432-463894435 | `ana2y2Yv...` | Rakurai | Rakurai | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 566 | 2026-11-01 00:43:47 | 1073 | 463894612-463894615 | `HEL1USMZ...` | JitoLabs | JitoLabs | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 567 | 2026-11-01 00:44:25 | 1073 | 463894788-463894791 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 568 | 2026-11-01 00:45:09 | 1073 | 463894996-463894999 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | independent | slot2 | 12 | 11 | AgaveBam | 63330 |
| `campaign-mainnet-20261031T014357Z` | 569 | 2026-11-01 00:45:57 | 1073 | 463895220-463895223 | `5Cchr1XG...` | AgaveBam | AgaveBam | independent | slot2 | 12 | 8 | HarmonicAgave | 63330 |
| `campaign-mainnet-20261031T014357Z` | 570 | 2026-11-01 00:46:38 | 1073 | 463895408-463895411 | `4VRs6A9z...` | Firedancer | Firedancer | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 571 | 2026-11-01 00:47:31 | 1073 | 463895652-463895655 | `DRpbCBMx...` | AgaveBam | AgaveBam | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 572 | 2026-11-01 00:48:08 | 1073 | 463895828-463895831 | `7QQGNm3p...` | Agave | Agave | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 573 | 2026-11-01 00:48:45 | 1073 | 463896000-463896003 | `E1r4Psq8...` | JitoLabs | JitoLabs | independent | slot2 | 12 | 9 | HarmonicAgave | 63330 |
| `campaign-mainnet-20261031T014357Z` | 574 | 2026-11-01 00:49:34 | 1073 | 463896228-463896231 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 575 | 2026-11-01 00:50:36 | 1073 | 463896520-463896523 | `E3mDbFMr...` | Rakurai | Rakurai | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 576 | 2026-11-01 00:51:12 | 1073 | 463896688-463896691 | `9jxgosAf...` | FireBAM | FireBAM | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 577 | 2026-11-01 00:51:59 | 1073 | 463896904-463896907 | `LA1NEzry...` | FireBAM | FireBAM | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 578 | 2026-11-01 00:54:17 | 1073 | 463897552-463897555 | `7QQGNm3p...` | Agave | Agave | independent | pre300 | 12 | 9 | Firedancer | 63330 |
| `campaign-mainnet-20261031T014357Z` | 579 | 2026-11-01 00:58:47 | 1073 | 463898792-463898795 | `E3mDbFMr...` | Rakurai | Rakurai | independent | slot2 | 12 | 9 | AgaveBam | 63330 |
| `campaign-mainnet-20261031T014357Z` | 580 | 2026-11-01 01:04:08 | 1073 | 463900304-463900307 | `4VRs6A9z...` | Firedancer | Firedancer | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261031T014357Z` | 581 | 2026-11-01 03:30:05 | 1073 | 463941232-463941235 | `E3mDbFMr...` | Rakurai | Rakurai | equal_fee | slot2 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261031T014357Z` | 582 | 2026-11-01 03:44:15 | 1073 | 463945200-463945203 | `5Us18hLZ...` | Agave | Agave | equal_fee | slot2 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261031T014357Z` | 583 | 2026-11-01 03:46:36 | 1073 | 463945860-463945863 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | equal_fee | slot2 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261031T014357Z` | 584 | 2026-11-01 03:47:14 | 1073 | 463946036-463946039 | `4VRs6A9z...` | Firedancer | Firedancer | equal_fee | slot2 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261031T014357Z` | 585 | 2026-11-01 03:48:07 | 1073 | 463946284-463946287 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | equal_fee | pre300 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261031T014357Z` | 586 | 2026-11-01 03:49:09 | 1073 | 463946572-463946575 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | equal_fee | pre300 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261031T014357Z` | 587 | 2026-11-01 03:49:48 | 1073 | 463946752-463946755 | `HEL1USMZ...` | JitoLabs | JitoLabs | equal_fee | pre300 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261031T014357Z` | 588 | 2026-11-01 03:50:31 | 1073 | 463946952-463946955 | `9jxgosAf...` | FireBAM | FireBAM | equal_fee | pre300 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261031T014357Z` | 589 | 2026-11-01 03:51:09 | 1073 | 463947132-463947135 | `DRpbCBMx...` | AgaveBam | AgaveBam | equal_fee | pre300 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261031T014357Z` | 590 | 2026-11-01 03:51:45 | 1073 | 463947300-463947303 | `E1r4Psq8...` | JitoLabs | JitoLabs | equal_fee | slot2 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261031T014357Z` | 591 | 2026-11-01 03:52:23 | 1073 | 463947476-463947479 | `5Cchr1XG...` | AgaveBam | AgaveBam | equal_fee | slot2 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261031T014357Z` | 592 | 2026-11-01 03:53:14 | 1073 | 463947712-463947715 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | equal_fee | slot2 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261031T014357Z` | 593 | 2026-11-01 03:54:41 | 1073 | 463948124-463948127 | `7QQGNm3p...` | Agave | Agave | equal_fee | pre300 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261031T014357Z` | 594 | 2026-11-01 03:55:15 | 1073 | 463948284-463948287 | `ana2y2Yv...` | Rakurai | Rakurai | equal_fee | pre300 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261031T014357Z` | 595 | 2026-11-01 03:56:30 | 1073 | 463948628-463948631 | `LA1NEzry...` | FireBAM | FireBAM | equal_fee | slot2 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261031T014357Z` | 596 | 2026-11-01 03:58:01 | 1073 | 463949052-463949055 | `BFmqBsaG...` | Firedancer | Firedancer | equal_fee | pre300 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261101T041655Z` | 597 | 2026-11-01 06:55:11 | 1074 | 463998656-463998659 | `E3mDbFMr...` | Rakurai | Rakurai | equal_fee | pre300 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261101T041655Z` | 598 | 2026-11-01 07:00:01 | 1074 | 464000004-464000007 | `BFmqBsaG...` | Firedancer | Firedancer | equal_fee | slot2 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261101T041655Z` | 599 | 2026-11-01 07:01:19 (tool clock) | 1074 | 464000368-464000371 | `DRpbCBMx...` | AgaveBam | AgaveBam | equal_fee | slot2 | 0 | 0 | - | 0 |
| `campaign-mainnet-20261101T041655Z` | 600 | 2026-11-01 07:02:07 | 1074 | 464000596-464000599 | `HEL1USMZ...` | JitoLabs | JitoLabs | equal_fee | slot2 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261101T041655Z` | 601 | 2026-11-01 07:02:46 | 1074 | 464000780-464000783 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | equal_fee | slot2 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261101T041655Z` | 602 | 2026-11-01 07:03:44 | 1074 | 464001052-464001055 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | equal_fee | slot2 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261101T041655Z` | 603 | 2026-11-01 07:04:30 | 1074 | 464001268-464001271 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | equal_fee | pre300 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261101T041655Z` | 604 | 2026-11-01 07:05:24 | 1074 | 464001516-464001519 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | equal_fee | pre300 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261101T041655Z` | 605 | 2026-11-01 07:06:03 | 1074 | 464001692-464001695 | `5Cchr1XG...` | AgaveBam | AgaveBam | equal_fee | pre300 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261101T041655Z` | 606 | 2026-11-01 07:06:56 | 1074 | 464001936-464001939 | `ana2y2Yv...` | Rakurai | Rakurai | equal_fee | slot2 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261101T041655Z` | 607 | 2026-11-01 07:07:58 | 1074 | 464002228-464002231 | `E1r4Psq8...` | JitoLabs | JitoLabs | equal_fee | pre300 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261101T041655Z` | 608 | 2026-11-01 07:08:43 | 1074 | 464002432-464002435 | `9jxgosAf...` | FireBAM | FireBAM | equal_fee | slot2 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261101T041655Z` | 609 | 2026-11-01 07:09:26 | 1074 | 464002632-464002635 | `5Us18hLZ...` | Agave | Agave | equal_fee | pre300 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261101T041655Z` | 610 | 2026-11-01 07:10:46 | 1074 | 464003004-464003007 | `4VRs6A9z...` | Firedancer | Firedancer | equal_fee | pre300 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261101T041655Z` | 611 | 2026-11-01 07:12:18 | 1074 | 464003432-464003435 | `7QQGNm3p...` | Agave | Agave | equal_fee | slot2 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261101T041655Z` | 612 | 2026-11-01 07:14:56 | 1074 | 464004168-464004171 | `LA1NEzry...` | FireBAM | FireBAM | equal_fee | pre300 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261101T041655Z` | 613 | 2026-11-01 09:01:49 | 1074 | 464034168-464034171 | `LA1NEzry...` | FireBAM | FireBAM | denominator | pre300 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261101T041655Z` | 614 | 2026-11-01 09:08:53 | 1074 | 464036156-464036159 | `BFmqBsaG...` | Firedancer | Firedancer | denominator | slot2 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261101T041655Z` | 615 | 2026-11-01 09:11:39 | 1074 | 464036920-464036923 | `5Cchr1XG...` | AgaveBam | AgaveBam | denominator | pre300 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261101T041655Z` | 616 | 2026-11-01 09:12:53 | 1074 | 464037264-464037267 | `E1r4Psq8...` | JitoLabs | JitoLabs | denominator | pre300 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261101T041655Z` | 617 | 2026-11-01 09:13:37 | 1074 | 464037472-464037475 | `5Us18hLZ...` | Agave | Agave | denominator | pre300 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261101T041655Z` | 618 | 2026-11-01 09:14:24 | 1074 | 464037684-464037687 | `DRpbCBMx...` | AgaveBam | AgaveBam | denominator | slot2 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261101T041655Z` | 619 | 2026-11-01 09:15:00 | 1074 | 464037856-464037859 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | denominator | slot2 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261101T041655Z` | 620 | 2026-11-01 09:15:38 | 1074 | 464038036-464038039 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | denominator | slot2 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261101T041655Z` | 621 | 2026-11-01 09:16:18 | 1074 | 464038224-464038227 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | denominator | pre300 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261101T041655Z` | 622 | 2026-11-01 09:16:53 | 1074 | 464038388-464038391 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | denominator | pre300 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261101T041655Z` | 623 | 2026-11-01 09:18:06 | 1074 | 464038728-464038731 | `4VRs6A9z...` | Firedancer | Firedancer | denominator | pre300 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261101T041655Z` | 624 | 2026-11-01 09:18:56 | 1074 | 464038956-464038959 | `7QQGNm3p...` | Agave | Agave | denominator | slot2 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261101T041655Z` | 625 | 2026-11-01 09:19:31 | 1074 | 464039124-464039127 | `E3mDbFMr...` | Rakurai | Rakurai | denominator | pre300 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261101T041655Z` | 626 | 2026-11-01 09:20:37 | 1074 | 464039424-464039427 | `HEL1USMZ...` | JitoLabs | JitoLabs | denominator | slot2 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261101T041655Z` | 627 | 2026-11-01 09:21:44 | 1074 | 464039736-464039739 | `9jxgosAf...` | FireBAM | FireBAM | denominator | slot2 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261101T041655Z` | 628 | 2026-11-01 09:22:57 | 1074 | 464040080-464040083 | `ana2y2Yv...` | Rakurai | Rakurai | denominator | slot2 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261101T041655Z` | 629 | 2026-11-01 12:13:17 | 1074 | 464087892-464087895 | `LA1NEzry...` | FireBAM | FireBAM | independent | slot2 | 12 | 11 | HarmonicAgave | 63330 |
| `campaign-mainnet-20261101T041655Z` | 630 | 2026-11-01 12:27:49 | 1074 | 464091976-464091979 | `LA1NEzry...` | FireBAM | FireBAM | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 631 | 2026-11-01 12:38:45 | 1074 | 464095024-464095027 | `BFmqBsaG...` | Firedancer | Firedancer | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 632 | 2026-11-01 12:39:58 | 1074 | 464095364-464095367 | `5Us18hLZ...` | Agave | Agave | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 633 | 2026-11-01 12:41:30 | 1074 | 464095792-464095795 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | independent | slot2 | 12 | 5 | AgaveBam | 63330 |
| `campaign-mainnet-20261101T041655Z` | 634 | 2026-11-01 12:42:19 | 1074 | 464096020-464096023 | `DRpbCBMx...` | AgaveBam | AgaveBam | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 635 | 2026-11-01 12:43:12 | 1074 | 464096264-464096267 | `5Cchr1XG...` | AgaveBam | AgaveBam | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 636 | 2026-11-01 12:43:50 | 1074 | 464096448-464096451 | `E1r4Psq8...` | JitoLabs | JitoLabs | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 637 | 2026-11-01 12:44:25 | 1074 | 464096612-464096615 | `7QQGNm3p...` | Agave | Agave | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 638 | 2026-11-01 12:45:12 | 1074 | 464096828-464096831 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | independent | slot2 | 12 | 11 | JitoLabs | 63330 |
| `campaign-mainnet-20261101T041655Z` | 639 | 2026-11-01 12:46:01 | 1074 | 464097060-464097063 | `E1r4Psq8...` | JitoLabs | JitoLabs | independent | slot2 | 12 | 6 | AgaveBam | 63330 |
| `campaign-mainnet-20261101T041655Z` | 640 | 2026-11-01 12:46:50 | 1074 | 464097288-464097291 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 641 | 2026-11-01 12:47:49 | 1074 | 464097572-464097575 | `9jxgosAf...` | FireBAM | FireBAM | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 642 | 2026-11-01 12:48:30 | 1074 | 464097764-464097767 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 643 | 2026-11-01 12:49:22 | 1074 | 464098008-464098011 | `HEL1USMZ...` | JitoLabs | JitoLabs | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 644 | 2026-11-01 12:50:09 | 1074 | 464098224-464098227 | `DRpbCBMx...` | AgaveBam | AgaveBam | independent | pre300 | 12 | 10 | HarmonicAgave | 63330 |
| `campaign-mainnet-20261101T041655Z` | 645 | 2026-11-01 12:50:50 | 1074 | 464098416-464098419 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 646 | 2026-11-01 12:51:38 | 1074 | 464098640-464098643 | `4VRs6A9z...` | Firedancer | Firedancer | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 647 | 2026-11-01 12:52:17 | 1074 | 464098820-464098823 | `E3mDbFMr...` | Rakurai | Rakurai | independent | slot2 | 12 | 8 | ? | 63330 |
| `campaign-mainnet-20261101T041655Z` | 648 | 2026-11-01 12:53:36 | 1074 | 464099184-464099187 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 649 | 2026-11-01 12:55:18 | 1074 | 464099664-464099667 | `4VRs6A9z...` | Firedancer | Firedancer | independent | slot2 | 12 | 10 | AgaveBam | 63330 |
| `campaign-mainnet-20261101T041655Z` | 650 | 2026-11-01 12:56:34 | 1074 | 464100024-464100027 | `5Us18hLZ...` | Agave | Agave | independent | slot2 | 12 | 10 | AgaveBam | 63330 |
| `campaign-mainnet-20261101T041655Z` | 651 | 2026-11-01 12:57:39 | 1074 | 464100328-464100331 | `ana2y2Yv...` | Rakurai | Rakurai | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 652 | 2026-11-01 12:59:05 | 1074 | 464100728-464100731 | `E3mDbFMr...` | Rakurai | Rakurai | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 653 | 2026-11-01 15:27:46 | 1074 | 464142308-464142311 | `LA1NEzry...` | FireBAM | FireBAM | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 654 | 2026-11-01 15:28:24 | 1074 | 464142484-464142487 | `ana2y2Yv...` | Rakurai | Rakurai | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 655 | 2026-11-01 15:30:10 | 1074 | 464142984-464142987 | `E1r4Psq8...` | JitoLabs | JitoLabs | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 656 | 2026-11-01 15:30:54 | 1074 | 464143184-464143187 | `DRpbCBMx...` | AgaveBam | AgaveBam | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 657 | 2026-11-01 15:31:47 | 1074 | 464143436-464143439 | `4VRs6A9z...` | Firedancer | Firedancer | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 658 | 2026-11-01 15:32:22 | 1074 | 464143596-464143599 | `9jxgosAf...` | FireBAM | FireBAM | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 659 | 2026-11-01 15:33:28 | 1074 | 464143900-464143903 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 660 | 2026-11-01 15:34:09 | 1074 | 464144092-464144095 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 661 | 2026-11-01 15:34:50 | 1074 | 464144288-464144291 | `HEL1USMZ...` | JitoLabs | JitoLabs | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 662 | 2026-11-01 15:35:29 | 1074 | 464144468-464144471 | `5Cchr1XG...` | AgaveBam | AgaveBam | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 663 | 2026-11-01 15:36:36 | 1074 | 464144780-464144783 | `7QQGNm3p...` | Agave | Agave | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 664 | 2026-11-01 15:37:33 | 1074 | 464145048-464145051 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 665 | 2026-11-01 15:38:36 | 1074 | 464145348-464145351 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 666 | 2026-11-01 15:39:53 | 1074 | 464145708-464145711 | `E3mDbFMr...` | Rakurai | Rakurai | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 667 | 2026-11-01 15:40:52 | 1074 | 464145980-464145983 | `5Us18hLZ...` | Agave | Agave | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 668 | 2026-11-01 15:42:29 | 1074 | 464146440-464146443 | `BFmqBsaG...` | Firedancer | Firedancer | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 669 | 2026-11-01 20:53:38 | 1074 | 464233548-464233551 | `E3mDbFMr...` | Rakurai | Rakurai | denominator | pre300 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261101T041655Z` | 670 | 2026-11-01 20:59:21 | 1074 | 464235144-464235147 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | denominator | slot2 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261101T041655Z` | 671 | 2026-11-01 21:00:08 | 1074 | 464235364-464235367 | `5Us18hLZ...` | Agave | Agave | denominator | pre300 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261101T041655Z` | 672 | 2026-11-01 21:00:48 | 1074 | 464235548-464235551 | `9jxgosAf...` | FireBAM | FireBAM | denominator | slot2 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261101T041655Z` | 673 | 2026-11-01 21:01:35 | 1074 | 464235768-464235771 | `5Cchr1XG...` | AgaveBam | AgaveBam | denominator | pre300 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261101T041655Z` | 674 | 2026-11-01 21:02:22 | 1074 | 464235988-464235991 | `4VRs6A9z...` | Firedancer | Firedancer | denominator | pre300 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261101T041655Z` | 675 | 2026-11-01 21:03:15 | 1074 | 464236236-464236239 | `HEL1USMZ...` | JitoLabs | JitoLabs | denominator | slot2 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261101T041655Z` | 676 | 2026-11-01 21:03:49 | 1074 | 464236396-464236399 | `DRpbCBMx...` | AgaveBam | AgaveBam | denominator | slot2 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261101T041655Z` | 677 | 2026-11-01 21:04:23 | 1074 | 464236556-464236559 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | denominator | slot2 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261101T041655Z` | 678 | 2026-11-01 21:05:09 | 1074 | 464236768-464236771 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | denominator | pre300 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261101T041655Z` | 679 | 2026-11-01 21:06:12 | 1074 | 464237064-464237067 | `LA1NEzry...` | FireBAM | FireBAM | denominator | pre300 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261101T041655Z` | 680 | 2026-11-01 21:06:59 | 1074 | 464237280-464237283 | `E1r4Psq8...` | JitoLabs | JitoLabs | denominator | pre300 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261101T041655Z` | 681 | 2026-11-01 21:07:41 | 1074 | 464237472-464237475 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | denominator | pre300 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261101T041655Z` | 682 | 2026-11-01 21:08:21 | 1074 | 464237660-464237663 | `ana2y2Yv...` | Rakurai | Rakurai | denominator | slot2 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261101T041655Z` | 683 | 2026-11-01 21:09:13 | 1074 | 464237900-464237903 | `BFmqBsaG...` | Firedancer | Firedancer | denominator | slot2 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261101T041655Z` | 684 | 2026-11-01 21:13:44 | 1074 | 464239156-464239159 | `7QQGNm3p...` | Agave | Agave | denominator | slot2 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261101T041655Z` | 685 | 2026-11-02 00:17:11 | 1074 | 464290552-464290555 | `DRpbCBMx...` | AgaveBam | AgaveBam | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 686 | 2026-11-02 00:18:11 | 1074 | 464290832-464290835 | `ana2y2Yv...` | Rakurai | Rakurai | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 687 | 2026-11-02 00:18:53 | 1074 | 464291028-464291031 | `BFmqBsaG...` | Firedancer | Firedancer | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 688 | 2026-11-02 00:19:41 | 1074 | 464291252-464291255 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 689 | 2026-11-02 00:20:25 | 1074 | 464291452-464291455 | `9jxgosAf...` | FireBAM | FireBAM | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 690 | 2026-11-02 00:21:07 | 1074 | 464291640-464291643 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 691 | 2026-11-02 00:21:47 | 1074 | 464291828-464291831 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 692 | 2026-11-02 00:22:30 | 1074 | 464292028-464292031 | `5Cchr1XG...` | AgaveBam | AgaveBam | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 693 | 2026-11-02 00:23:10 | 1074 | 464292208-464292211 | `E3mDbFMr...` | Rakurai | Rakurai | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 694 | 2026-11-02 00:23:47 | 1074 | 464292380-464292383 | `5Us18hLZ...` | Agave | Agave | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 695 | 2026-11-02 00:24:34 | 1074 | 464292604-464292607 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 696 | 2026-11-02 00:25:25 | 1074 | 464292836-464292839 | `E1r4Psq8...` | JitoLabs | JitoLabs | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 697 | 2026-11-02 00:26:47 | 1074 | 464293212-464293215 | `HEL1USMZ...` | JitoLabs | JitoLabs | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 698 | 2026-11-02 00:27:28 | 1074 | 464293408-464293411 | `LA1NEzry...` | FireBAM | FireBAM | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 699 | 2026-11-02 00:28:13 | 1074 | 464293608-464293611 | `7QQGNm3p...` | Agave | Agave | shared | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 700 | 2026-11-02 00:29:22 | 1074 | 464293932-464293935 | `4VRs6A9z...` | Firedancer | Firedancer | shared | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 701 | 2026-11-02 01:44:14 | 1074 | 464314904-464314907 | `DRpbCBMx...` | AgaveBam | AgaveBam | equal_fee | slot2 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261101T041655Z` | 702 | 2026-11-02 01:44:50 | 1074 | 464315080-464315083 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | equal_fee | pre300 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261101T041655Z` | 703 | 2026-11-02 01:46:04 | 1074 | 464315424-464315427 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | equal_fee | slot2 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261101T041655Z` | 704 | 2026-11-02 01:46:52 | 1074 | 464315644-464315647 | `E3mDbFMr...` | Rakurai | Rakurai | equal_fee | pre300 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261101T041655Z` | 705 | 2026-11-02 01:47:38 | 1074 | 464315856-464315859 | `7QQGNm3p...` | Agave | Agave | equal_fee | slot2 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261101T041655Z` | 706 | 2026-11-02 01:48:44 | 1074 | 464316168-464316171 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | equal_fee | pre300 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261101T041655Z` | 707 | 2026-11-02 01:49:22 | 1074 | 464316344-464316347 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | equal_fee | slot2 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261101T041655Z` | 708 | 2026-11-02 01:50:14 | 1074 | 464316584-464316587 | `5Cchr1XG...` | AgaveBam | AgaveBam | equal_fee | pre300 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261101T041655Z` | 709 | 2026-11-02 01:51:08 | 1074 | 464316840-464316843 | `9jxgosAf...` | FireBAM | FireBAM | equal_fee | slot2 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261101T041655Z` | 710 | 2026-11-02 01:52:08 | 1074 | 464317120-464317123 | `ana2y2Yv...` | Rakurai | Rakurai | equal_fee | slot2 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261101T041655Z` | 711 | 2026-11-02 01:52:43 | 1074 | 464317280-464317283 | `5Us18hLZ...` | Agave | Agave | equal_fee | pre300 | 12 | 12 | - | 61200 |
| `campaign-mainnet-20261101T041655Z` | 712 | 2026-11-02 01:54:01 | 1074 | 464317640-464317643 | `HEL1USMZ...` | JitoLabs | JitoLabs | equal_fee | slot2 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261101T041655Z` | 713 | 2026-11-02 01:55:31 | 1074 | 464318060-464318063 | `BFmqBsaG...` | Firedancer | Firedancer | equal_fee | slot2 | 12 | 12 | - | 60120 |
| `campaign-mainnet-20261101T041655Z` | 714 | 2026-11-02 01:56:06 | 1074 | 464318224-464318227 | `E1r4Psq8...` | JitoLabs | JitoLabs | equal_fee | pre300 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261101T041655Z` | 715 | 2026-11-02 01:56:48 | 1074 | 464318428-464318431 | `LA1NEzry...` | FireBAM | FireBAM | equal_fee | pre300 | 12 | 12 | - | 72000 |
| `campaign-mainnet-20261101T041655Z` | 716 | 2026-11-02 02:15:00 | 1074 | 464323532-464323535 | `4VRs6A9z...` | Firedancer | Firedancer | equal_fee | pre300 | 12 | 12 | - | 60000 |
| `campaign-mainnet-20261101T041655Z` | 717 | 2026-11-02 04:51:44 | 1074 | 464367400-464367403 | `4VRs6A9z...` | Firedancer | Firedancer | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 718 | 2026-11-02 05:00:38 | 1074 | 464369892-464369895 | `LA1NEzry...` | FireBAM | FireBAM | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 719 | 2026-11-02 05:02:11 | 1074 | 464370316-464370319 | `CAo1dCGY...` | HarmonicAgave | HarmonicAgave | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 720 | 2026-11-02 05:04:18 | 1074 | 464370900-464370903 | `HEL1USMZ...` | JitoLabs | JitoLabs | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 721 | 2026-11-02 05:04:59 | 1074 | 464371092-464371095 | `9jxgosAf...` | FireBAM | FireBAM | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 722 | 2026-11-02 05:05:48 | 1074 | 464371324-464371327 | `DRpbCBMx...` | AgaveBam | AgaveBam | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 723 | 2026-11-02 05:06:23 | 1074 | 464371492-464371495 | `7QQGNm3p...` | Agave | Agave | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 724 | 2026-11-02 05:07:01 | 1074 | 464371668-464371671 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | independent | pre300 | 12 | 8 | ? | 63330 |
| `campaign-mainnet-20261101T041655Z` | 725 | 2026-11-02 05:08:07 | 1074 | 464371972-464371975 | `E1r4Psq8...` | JitoLabs | JitoLabs | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 726 | 2026-11-02 05:09:02 | 1074 | 464372228-464372231 | `Awes4Tr6...` | HarmonicFiredancer | HarmonicFiredancer | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 727 | 2026-11-02 05:09:49 | 1074 | 464372444-464372447 | `E3mDbFMr...` | Rakurai | Rakurai | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 728 | 2026-11-02 05:10:44 | 1074 | 464372700-464372703 | `7QQGNm3p...` | Agave | Agave | independent | pre300 | 12 | 2 | HarmonicFiredancer | 63330 |
| `campaign-mainnet-20261101T041655Z` | 729 | 2026-11-02 05:11:25 | 1074 | 464372888-464372891 | `HEL1USMZ...` | JitoLabs | JitoLabs | independent | pre300 | 12 | 10 | JitoLabs | 63330 |
| `campaign-mainnet-20261101T041655Z` | 730 | 2026-11-02 05:11:59 | 1074 | 464373048-464373051 | `5Us18hLZ...` | Agave | Agave | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 731 | 2026-11-02 05:12:55 | 1074 | 464373312-464373315 | `9jxgosAf...` | FireBAM | FireBAM | independent | pre300 | 12 | 11 | HarmonicAgave | 63330 |
| `campaign-mainnet-20261101T041655Z` | 732 | 2026-11-02 05:13:55 | 1074 | 464373588-464373591 | `5Cchr1XG...` | AgaveBam | AgaveBam | independent | slot2 | 12 | 6 | JitoLabs | 63330 |
| `campaign-mainnet-20261101T041655Z` | 733 | 2026-11-02 05:14:34 | 1074 | 464373772-464373775 | `Fd7btgyS...` | HarmonicAgave | HarmonicAgave | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 734 | 2026-11-02 05:15:11 | 1074 | 464373948-464373951 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | independent | pre300 | 12 | 11 | ? | 63330 |
| `campaign-mainnet-20261101T041655Z` | 735 | 2026-11-02 05:15:47 | 1074 | 464374112-464374115 | `5Cchr1XG...` | AgaveBam | AgaveBam | independent | slot2 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 736 | 2026-11-02 05:16:47 | 1074 | 464374396-464374399 | `BFmqBsaG...` | Firedancer | Firedancer | independent | pre300 | 12 | 10 | JitoLabs | 63330 |
| `campaign-mainnet-20261101T041655Z` | 737 | 2026-11-02 05:17:48 | 1074 | 464374680-464374683 | `ana2y2Yv...` | Rakurai | Rakurai | independent | pre300 | 12 | 9 | AgaveBam | 63330 |
| `campaign-mainnet-20261101T041655Z` | 738 | 2026-11-02 05:18:43 | 1074 | 464374936-464374939 | `JUPiTERr...` | HarmonicFiredancer | HarmonicFiredancer | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 739 | 2026-11-02 05:21:09 | 1074 | 464375620-464375623 | `ana2y2Yv...` | Rakurai | Rakurai | independent | pre300 | 12 | 12 | - | 63330 |
| `campaign-mainnet-20261101T041655Z` | 740 | 2026-11-02 05:24:46 | 1074 | 464376632-464376635 | `BFmqBsaG...` | Firedancer | Firedancer | independent | pre300 | 12 | 12 | - | 63330 |
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
