# Inside the Block

A measurement kit for one question about Solana mainnet: by what rule does each leader order transactions inside its block, how strictly does the rule hold, and is there a rule at all. The kit sends small bursts of its own probe transactions into chosen leader windows, reads the blocks back, and tests the ordering against rules fixed before any live data.

Status: under construction. The full README (design, the six Considerations, and what the design does NOT separate) and the REPORT come with the measurement.

## One command for judges

```bash
docker compose run --rm reproduce
```

It needs no key and no Rust build. It runs the known-answer selftest, re-reads every recorded signature from the chain (verify), and recomputes every REPORT number from the raw data (analyze), failing on the first mismatch. Steps can be run alone with `docker compose run --rm reproduce verify` or `analyze`.

## Layout

| Path | What it holds |
|---|---|
| `compose.yaml` | services: `reproduce` (always on), `plan`, `probe` and `collect` (profile `measure`) |
| `probe/` | the sender, Rust on Agave's QUIC stack; dry-run by default, live sending only with `--live --max-spend-lamports N` under a compiled 0.05 SOL cap |
| `itb/` | collect, verify, analyze and selftest, Python standard library only |
| `schema/raw-format.json` | the format of every raw row, shared by both languages |
| `data/` | raw data of every run, including failed ones |
| `logs/` | operational logs, kept apart from raw data |

Keys are never part of the repository: the probe reads one from a Compose secret (a file outside the checkout, or an environment variable via `compose.key-from-env.yaml`).

## Building the probe behind a TLS-inspecting proxy

The probe image fetches crates from crates.io while it builds. An antivirus web shield or a corporate proxy that re-signs HTTPS makes that fetch fail with a certificate error. Export the proxy's root certificate as PEM and pass it as a build secret; only the dependency fetch sees it, it is added to the system roots, and the built image does not contain it:

```bash
docker build --secret id=extra_ca,src=proxy-root.pem -f probe/Dockerfile -t inside-the-block-probe:local .
```

The probe itself refuses to measure through such a proxy: before a run it checks who issued the certificates of the RPC and WebSocket endpoints and stops with the issuer's name when the chain does not verify against the public roots.

## License

MIT
