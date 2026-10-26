#!/usr/bin/env bash
# Mainnet dry-run without a key (plan-implementation, section 11).
#
#   tests/mainnet-dry-run.sh [BURSTS]
#
# Draws a test plan from the live mainnet leader schedule, shows the key mount as the
# probe sees it (secrets/wallet-key.json absent or an empty directory means no key),
# runs the plan in dry-run mode and prints the probe status. The run log records the
# TLS issuer of the RPC node, so a machine whose antivirus intercepts TLS shows it.
# Nothing is signed with a funded key and no QUIC stream is opened. The transcript
# lands in logs/mainnet-dry-run-<stamp>.txt; plans, runs and logs in data/ and logs/.
set -uo pipefail
export MSYS_NO_PATHCONV=1

here=$(cd "$(dirname "$0")" && pwd)
repo=$(cd "$here/.." && pwd)
bursts=${1:-4}
unset ITB_WALLET_KEY_FILE ITB_WALLET_KEY ITB_SIM_PAYER
export ITB_NETWORK=mainnet ITB_RPC_URL=https://api.mainnet-beta.solana.com ITB_WS_URL=wss://api.mainnet-beta.solana.com

# Docker Desktop on Windows takes C:/... paths, and so does Git for Windows under MSYS_NO_PATHCONV.
host_path() { if command -v cygpath >/dev/null 2>&1; then cygpath -m "$1"; else printf '%s\n' "$1"; fi; }
git_repo() { git -C "$(host_path "$repo")" "$@"; }
head=$(git_repo rev-parse HEAD) && [ -n "$head" ] || { echo "mainnet-dry-run.sh: $repo is not a git checkout" >&2; exit 2; }
ITB_GIT_COMMIT=$head$(git_repo diff --quiet HEAD -- . ':!data' ':!logs' || echo -dirty)
export ITB_GIT_COMMIT
compose_file=$(host_path "$repo/compose.yaml")
dc() { docker compose -f "$compose_file" --profile measure "$@"; }
stamp=$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p "$repo/logs"
exec > >(tee "$repo/logs/mainnet-dry-run-$stamp.txt") 2>&1

echo "commit $ITB_GIT_COMMIT, $(date -u +%FT%TZ)"
ls -la "$repo/secrets" 2>&1
echo "== plan"
out=$(dc run --rm --no-deps -T plan plan --network mainnet --stage test --bursts "$bursts" --lead-slots 300) || { echo "$out"; exit 1; }
echo "$out"
plan=$(printf '%s\n' "$out" | sed -n 's|^plan: /repo/data/\(plans/.*plan\.json\)$|\1|p' | tr -d '\r')
[ -n "$plan" ] || { echo "no plan path in the output"; exit 1; }
echo "== the key mount as the probe sees it"
dc run --rm --no-deps -T --entrypoint sh probe -c 'ls -la /run/secrets/ 2>&1; stat -c "wallet_key: %F" /run/secrets/wallet_key 2>&1'
echo "== dry-run"
dc run --rm --no-deps -T probe run --plan "/data/$plan"
code=$?
echo "dry-run exit $code"
echo "== status"
dc run --rm --no-deps -T probe status
exit $code
