# Running the kit

How to measure, how to test the kit without spending, where each part of the repository lies, and what the section numbers in code comments refer to. [README.md](README.md#reproduce-every-number-with-one-command) gives the one command that reproduces every table, and [DESIGN.md](DESIGN.md) gives the reasons behind each step.

## Measuring

The sender is dry-run by default: it opens the connections, simulates every probe and sends nothing. A live run needs both `--live` and `--max-spend-lamports N`, and a compiled cap of 0.05 SOL (50 000 000 lamports) stands above any limit given on the command line. Before the first send the sender prices the whole plan at its worst-case fee and refuses when the limit does not cover it.

```bash
docker compose --profile measure run --rm plan panel
docker compose --profile measure run --rm plan pilot --panel data/panels/<id>/panel.json
docker compose --profile measure run --rm probe anchor --stage pilot
docker compose --profile measure run --rm probe run --plan /data/plans/<id>/plan.json
```

The commands draw the panel, place the seeded pilot table into its windows, simulate the anchor memo, and dry-run the plan. The live form of the last two adds `--live --max-spend-lamports N`.

A dry-run waits for the real windows of its plan: on 2026-11-02 the dry-run of a 68-burst pilot plan took 2 h 36 min. A short check draws a test plan of 8 bursts with `docker compose --profile measure run --rm plan plan --stage test --bursts 8` and dry-runs that plan.

Measure in a separate clone. `docker compose run --rm reproduce` and `python -m itb report --check` compare the published tables with every run under `data/`, so a new run in this folder fails the check, and the check names that run. Give the run its commit with `ITB_GIT_COMMIT=$(git rev-parse HEAD)` in the environment of `docker compose`; without it the first row records no commit and the run table shows `-`.

In the published folder some steps are history and refuse by design, since both stages are anchored and the campaign has ended: `probe anchor`, `python -m itb manifest` for either stage, `python -m itb minimum`, `python -m itb campaign-table` and `plan campaign`. `minimum` and `campaign-table` still run with `--out` naming a new file, and on 2026-11-02 both outputs matched the committed files byte for byte. `plan pilot` draws on the committed panel `data/panels/mainnet-e1069-20261027T005744Z/panel.json`. `plan panel` writes the panel of the coming epoch and exits with code 1 when a class has fewer leaders than the rule needs, as HarmonicAgave did at epoch 1075 on 2026-11-02; `plan pilot` refuses such a panel.

The campaign follows the same steps. On the host, `python -m itb minimum` reads the collected pilot runs and `python -m itb manifest --stage campaign --panel data/panels/<id>/panel.json` hashes the campaign files together with the panel the campaign runs on; containers mount `prereg/` read-only. Each epoch gets its own plan, drawn once the leader schedule of that epoch is known:

```bash
docker compose --profile measure run --rm plan campaign --panel data/panels/<id>/panel.json --epoch-index 0 --epoch <epoch>
```

A round whose first window has already passed when the plan is drawn is left out and noted in `draw-notes.json` beside the plan; its cells are not moved to another hour, because that would break the blocking by round. Placement depends on the seed and the leader schedule only, so a plan drawn again after a stopped run keeps the windows of the rounds still ahead.

[scripts/campaign.sh](scripts/campaign.sh) runs the four epochs live one after another, since they share the payers and the spend journal. For each epoch it draws the plan, sets the limit to the committed lamports plus the plan's worst-case fees plus the funding and closing overhead, closes the payers at the end and collects the run. A failed run is collected and its epoch drawn again after ten minutes, up to three attempts:

```bash
scripts/campaign.sh data/panels/<id>/panel.json <first epoch>
```

A campaign runs for days on one network line, and other traffic on that line spoils timing before it shows anywhere else. Half the RTT sets the send moment and also enters the arrival estimate, so delay that grows in one direction only moves the real arrival while the estimate stays in the band. [itb/channel.py](itb/channel.py) therefore watches the RTT next to the band. Per round it reports the share of bursts in the timing band, bursts skipped because the slot clock fell behind, the largest clock lag, failed handshakes, and the median QUIC handshake and getSlot round trips. Each check has a threshold derived from the pilot, and the reasoning sits in a comment beside it. [scripts/channel-check.sh](scripts/channel-check.sh) checks the line before the start with three minutes of getSlot round trips and a dry-run on the nearest windows of the panel leaders. During the campaign the watch journals every finished round and exits with code 3 at the first one below a threshold:

```bash
scripts/channel-check.sh data/panels/<id>/panel.json
python -m itb channel watch --journal logs/channel-<stamp>.jsonl --transcript logs/campaign-<stamp>.txt
```

The comments at the top of [compose.yaml](compose.yaml) list every command.

Keys are never part of the repository. The sender reads the wallet key from a Compose secret whose file is given by `ITB_WALLET_KEY_FILE` (by default the git-ignored `secrets/wallet-key.json`), or from an environment variable through `compose.key-from-env.yaml`. Where that file is missing, Docker Desktop creates an empty directory `secrets/wallet-key.json/` at the first start of the probe service; remove the directory before putting the key in its place. Logs and raw rows never carry key bytes, and `tests/keyscan.py` searches everything a run wrote for them in every encoding.

## Development without spending

A local test validator is not part of the kit. The Linux release of `solana-test-validator` 4.3.2 needs `io_uring`, which Docker's default seccomp profile blocks, and the kit does not loosen that profile. The kit tests itself in two other ways. The selftest runs collect, verify and analyze over a fake chain with a known answer, including the exact zero of tau cross. The pipeline test [tests/devnet.sh](tests/devnet.sh) runs on devnet: it draws a plan from the devnet leader schedule, starts a live run under a limit below the plan's cost and expects a refusal before the first send, dry-runs the same plan, and with test SOL on a throwaway key runs a second plan live with collect and verify, then scans everything for key bytes. The refusal is on record in [logs/devnet-devnet-20261026T231740Z.jsonl](logs/devnet-devnet-20261026T231740Z.jsonl).

The probe image runs `cargo test` while it builds, and a failing test fails the build. `node research/probe-layout/vector.mjs` rebuilds the expected bytes of the probe message tests from the JavaScript builder whose messages a mainnet node priced and simulated.

On the host the unit tests run with `python -m unittest discover -s tests` and the known-answer checks with `python -m itb selftest`. Both need the Python standard library alone and are tested on Python 3.12, the version of the image.

## Building the probe behind a TLS-inspecting proxy

The probe image fetches crates from crates.io while it builds. An antivirus web shield or a corporate proxy that re-signs HTTPS makes that fetch fail with a certificate error. Export the proxy's root certificate as PEM and pass it as a build secret. Only the dependency fetch sees it, through the system roots of the build stage, and the built image does not contain it:

```bash
docker build --secret id=extra_ca,src=proxy-root.pem -f probe/Dockerfile -t inside-the-block-probe:local .
```

The probe itself refuses to measure through such a proxy ([DESIGN.md](DESIGN.md#the-path-from-the-sender-to-the-executing-node)).

The plan step reads the second client label from validators.app, and a web shield may re-sign that host too. `ITB_EXTRA_CA_PEM`, set to the PEM text of the same root, adds it next to the system roots for that one request (`ITB_EXTRA_CA_FILE` names the root as a file instead, for runs on the host and for `scripts/campaign.sh`); RPC calls never use it, and the snapshot records the root's SHA-256. Without it the plan still draws and notes that its bursts carry no second label.

## Layout

| Path | What it holds |
|---|---|
| `compose.yaml` | four services: `reproduce`, `plan`, `collect`, `probe`; all but the first need the profile `measure` |
| `probe/` | the sender, Rust on Agave's QUIC stack; dry-run by default, live sending only with `--live --max-spend-lamports N` under a compiled 0.05 SOL cap |
| `itb/` | panel, plan, collect, verify, analyze, report and selftest, Python standard library only |
| `REPORT.md` | the answer, the conditions of the measurement and the plan that lifts them |
| `DETAILS.md` | the pilot and every other table, with the log of what went wrong; `python -m itb report` writes the tables of both files from `data/` and `logs/` |
| `DESIGN.md` | the reasons behind the design and what it does not separate |
| `RUNNING.md` | measuring, development without spending, and the section numbers of code comments |
| `prereg/` | everything fixed before live data: the analysis plan, the seeded pilot and campaign tables, the minimum from the pilot, and the manifests whose hashes go on chain |
| `schema/raw-format.json` | the format of every raw row, shared by both languages |
| `data/` | inputs and raw data of every run, failed ones included |
| `logs/` | operational logs, kept apart from raw data |
| `research/` | two measurements the code rests on, each with its script and raw output: the builder's tick over one whole epoch (`tick-scale`) and hand-built probe messages a mainnet node priced and simulated (`probe-layout`) |
| `scripts/` | the live campaign runner, one epoch after another, and the line check before it |
| `tests/` | the devnet pipeline test, the mainnet dry-run, the key scanner, and unit tests for the scanner, the raw format, the campaign runner, the campaign data and the report over two files |

## Section numbers in code comments

Comments in the code cite sections of the build plan the kit was written from. The build plan is not part of the repository, and the table below gives a public place for each number the comments cite. A bare "section N", "plan, section N" and "build plan, section N" all mean the build plan. So do the numbers in the comments of `itb/prereg.py` and the "plan section 5.2" of the analysis plan: the hashes of both files are anchored on chain, so they stay as written. "Analysis plan, section N" and "addendum, section N" use the own numbers of [prereg/ANALYSIS-PLAN.md](prereg/ANALYSIS-PLAN.md) and [prereg/CAMPAIGN-ADDENDUM.md](prereg/CAMPAIGN-ADDENDUM.md).

| Section | Subject and where to read it |
|---|---|
| 1 | builder classes marked by the market tick, each fork with a builder set against its code base: [DESIGN.md](DESIGN.md#leader-schedule-and-leader-types), [analysis plan, section 8](prereg/ANALYSIS-PLAN.md#8-class-pairs) |
| 3 | the leader panel: [DESIGN.md](DESIGN.md#how-a-measurement-works), [addendum, section 8](prereg/CAMPAIGN-ADDENDUM.md#8-the-panel) |
| 4 | the probe transaction and its limits: [DESIGN.md](DESIGN.md#how-a-measurement-works), [research/probe-layout](research/probe-layout/) |
| 5.1 | direct QUIC to the leader's tpuQuic with the slot clock that aims it: [DESIGN.md](DESIGN.md#the-path-from-the-sender-to-the-executing-node) |
| 5.2 | the control path through public RPC: [addendum, section 9](prereg/CAMPAIGN-ADDENDUM.md#9-control-path), [REPORT.md, section 4.4](REPORT.md#44-control-path) |
| 5.3 | leaders with a builder: [DESIGN.md](DESIGN.md#leader-schedule-and-leader-types), [addendum, section 7](prereg/CAMPAIGN-ADDENDUM.md#7-the-builder-label) |
| 6 | the burst with its arms and moment conditions: [DESIGN.md](DESIGN.md#how-a-measurement-works), [the interaction of the probes](DESIGN.md#interaction-of-the-probes-with-each-other) |
| 7 | campaign rounds and the spend budget: [Measuring](#measuring), [the gap between windows](DESIGN.md#interaction-of-the-probes-with-each-other) |
| 8 | raw data: [schema/raw-format.json](schema/raw-format.json) |
| 9 | the check of every number with one command: [README.md](README.md#reproduce-every-number-with-one-command), [REPORT.md, section 9](REPORT.md#9-how-the-tables-are-made) |
| 10 | the analysis plan fixed before live data and its anchor on chain: [prereg/](prereg/), [data/prereg-anchors.json](data/prereg-anchors.json) |
| 11 | safety of money and key: [Measuring](#measuring) |
| 12 | the repository and its Compose file: [Layout](#layout), [compose.yaml](compose.yaml) |
| 13 | development without spending: [Development without spending](#development-without-spending) |
