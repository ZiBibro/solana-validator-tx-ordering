# Running the kit

How to measure, how to test the kit without spending, and where each part of the repository lies. [README.md](README.md#reproduce-every-number-with-one-command) gives the one command that reproduces every table, and [DESIGN.md](DESIGN.md) gives the reasons behind each step.

## Measuring

The sender is dry-run by default: it opens the connections, simulates every probe and sends nothing. A live run needs both `--live` and `--max-spend-lamports N`, and a compiled cap of 0.05 SOL (50 000 000 lamports) stands above any limit given on the command line. Before the first send the sender prices the whole plan at its worst-case fee and refuses when the limit does not cover it.

```bash
docker compose --profile measure run --rm plan panel
docker compose --profile measure run --rm plan pilot --panel data/panels/<id>/panel.json
docker compose --profile measure run --rm probe anchor --stage pilot
docker compose --profile measure run --rm probe run --plan /data/plans/<id>/plan.json
```

The commands draw the panel, place the seeded pilot table into its windows, simulate the anchor memo, and dry-run the plan. The live form of the last two adds `--live --max-spend-lamports N`.

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

Keys are never part of the repository. The sender reads the wallet key from a Compose secret whose file is given by `ITB_WALLET_KEY_FILE` (by default the git-ignored `secrets/wallet-key.json`), or from an environment variable through `compose.key-from-env.yaml`. Logs and raw rows never carry key bytes, and `tests/keyscan.py` searches everything a run wrote for them in every encoding.

## Development without spending

A local test validator is not part of the kit. The Linux release of `solana-test-validator` 4.3.2 needs `io_uring`, which Docker's default seccomp profile blocks, and the kit does not loosen that profile. The kit tests itself in two other ways. The selftest runs collect, verify and analyze over a fake chain with a known answer, including the exact zero of tau cross. The pipeline test [tests/devnet.sh](tests/devnet.sh) runs on devnet: it draws a plan from the devnet leader schedule, starts a live run under a limit below the plan's cost and expects a refusal before the first send, dry-runs the same plan, and with test SOL on a throwaway key runs a second plan live with collect and verify, then scans everything for key bytes. The refusal is on record in [logs/devnet-devnet-20261026T231740Z.jsonl](logs/devnet-devnet-20261026T231740Z.jsonl).

The probe image runs `cargo test` while it builds, and a failing test fails the build.

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
| `RUNNING.md` | measuring and development without spending |
| `prereg/` | everything fixed before live data: the analysis plan, the seeded pilot and campaign tables, the minimum from the pilot, and the manifests whose hashes go on chain |
| `schema/raw-format.json` | the format of every raw row, shared by both languages |
| `data/` | inputs and raw data of every run, failed ones included |
| `logs/` | operational logs, kept apart from raw data |
| `scripts/` | the live campaign runner, one epoch after another, and the line check before it |
| `tests/` | the devnet pipeline test, the mainnet dry-run, the key scanner, and unit tests for the scanner, the raw format, the campaign runner, the campaign data and the report over two files |
