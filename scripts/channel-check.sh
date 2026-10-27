#!/usr/bin/env bash
# Line check before the live campaign (plan-implementation, section 11).
#
#   scripts/channel-check.sh PANEL [BURSTS [SECONDS]]
#
# Times getSlot round trips to the RPC node for SECONDS (default 180) from the plan
# container, then draws a test plan of BURSTS windows (default 12, at most 2 per leader)
# of the PANEL leaders from the live schedule and runs it in dry-run mode: QUIC
# handshakes to the leaders, the slot clock guard and the timing band, with nothing
# signed by a funded key. Both parts are compared with THRESHOLDS in itb/channel.py.
# Exit 0 when both pass, 3 when one misses a threshold, 1 on a failure. The transcript
# lands in logs/channel-check-<stamp>.txt.
set -uo pipefail
export MSYS_NO_PATHCONV=1

here=$(cd "$(dirname "$0")" && pwd)
repo=$(cd "$here/.." && pwd)
[ $# -ge 1 ] || { sed -n 4p "$0" >&2; exit 2; }
panel=$1 bursts=${2:-12} seconds=${3:-180}
[ -f "$repo/$panel" ] || { echo "channel-check.sh: no panel $repo/$panel" >&2; exit 2; }
unset ITB_WALLET_KEY_FILE ITB_WALLET_KEY ITB_SIM_PAYER
export ITB_NETWORK=mainnet ITB_RPC_URL=https://api.mainnet-beta.solana.com ITB_WS_URL=wss://api.mainnet-beta.solana.com

# Docker Desktop on Windows takes C:/... paths, and so does Git for Windows under MSYS_NO_PATHCONV.
host_path() { if command -v cygpath >/dev/null 2>&1; then cygpath -m "$1"; else printf '%s\n' "$1"; fi; }
git_repo() { git -C "$(host_path "$repo")" "$@"; }
head=$(git_repo rev-parse HEAD) && [ -n "$head" ] || { echo "channel-check.sh: $repo is not a git checkout" >&2; exit 2; }
ITB_GIT_COMMIT=$head$(git_repo diff --quiet HEAD -- . ':!data' ':!logs' || echo -dirty)
export ITB_GIT_COMMIT
compose_file=$(host_path "$repo/compose.yaml")
dc() { docker compose -f "$compose_file" --profile measure "$@"; }
stamp=$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p "$repo/logs"
exec > >(tee "$repo/logs/channel-check-$stamp.txt") 2>&1
scratch=$(mktemp)
trap 'rm -f "$scratch"' EXIT

echo "commit $ITB_GIT_COMMIT, $(date -u +%FT%TZ), panel $panel"
echo "== getSlot round trips for $seconds s"
dc run --rm --no-deps -T plan channel rpc --seconds "$seconds" --gate
rpc_code=$?
echo "rpc exit $rpc_code"
[ $rpc_code -eq 0 ] || [ $rpc_code -eq 3 ] || exit 1

echo "== plan"
out=$(dc run --rm --no-deps -T plan plan --network mainnet --stage test --bursts "$bursts" --lead-slots 300 \
    --panel "$panel" --per-leader 2) || { echo "$out"; exit 1; }
echo "$out"
plan=$(printf '%s\n' "$out" | sed -n 's|^plan: /repo/data/\(plans/.*plan\.json\)$|\1|p' | tr -d '\r')
[ -n "$plan" ] || { echo "no plan path in the output"; exit 1; }
echo "== dry-run"
dc run --rm --no-deps -T probe run --plan "/data/$plan" 2>&1 | tee "$scratch"
code=${PIPESTATUS[0]}
echo "dry-run exit $code"
run_id=$(sed -n 's|^itb-probe dry-run run \([^:]*\):.*|\1|p' "$scratch" | tr -d '\r' | head -n 1)
[ $code -eq 0 ] && [ -n "$run_id" ] || exit 1
echo "== rounds of $run_id"
dc run --rm --no-deps -T plan channel rounds "$run_id" --all --gate
rounds_code=$?
echo "rounds exit $rounds_code"
[ $rounds_code -eq 0 ] || [ $rounds_code -eq 3 ] || exit 1
if [ $rpc_code -eq 3 ] || [ $rounds_code -eq 3 ]; then
    echo "line check: below a threshold, $(date -u +%FT%TZ)"
    exit 3
fi
echo "line check: passed, $(date -u +%FT%TZ)"
