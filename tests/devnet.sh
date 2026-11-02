#!/usr/bin/env bash
# Devnet pipeline test (build plan, sections 11, 12 and 13).
#
#   tests/devnet.sh KEY_FILE [BURSTS]
#
# KEY_FILE is a one-time solana-keygen file outside the repository, funded on devnet
# through faucet.solana.com (the RPC faucet answers 410, closed). Steps:
#   a plan drawn from the live devnet leader schedule;
#   the rights of the key as the probe container sees them;
#   a live run of that plan under a limit set below its cost, which must refuse
#   before anything is sent (the log shows limit_refusal);
#   a dry-run of the same plan, which must open zero QUIC streams;
#   a second plan, run live with funding and closing, then collect and verify;
#   a search of everything the runs wrote for the bytes of the key.
# Plans, runs and logs land in data/ and logs/ of the repository; nothing else in
# it may change. The live steps need about 0.012 SOL on the wallet, most of it payer
# rent that the closing returns. Without it they are skipped and the exit code is 3.
# Exit 0: every step passed. Exit 1: a step failed. Exit 2: bad arguments.
set -uo pipefail
export MSYS_NO_PATHCONV=1

here=$(cd "$(dirname "$0")" && pwd)
repo=$(cd "$here/.." && pwd)
key=${1:?usage: tests/devnet.sh KEY_FILE [BURSTS]}
bursts=${2:-4}
[ -f "$key" ] || { echo "devnet.sh: no key file at $key" >&2; exit 2; }
key=$(cd "$(dirname "$key")" && pwd)/$(basename "$key")
case "$key" in "$repo"/*) echo "devnet.sh: the key file must lie outside the repository" >&2; exit 2 ;; esac

# Docker Desktop on Windows takes C:/... paths; elsewhere the path stays as it is.
host_path() { if command -v cygpath >/dev/null 2>&1; then cygpath -m "$1"; else printf '%s\n' "$1"; fi; }
ITB_WALLET_KEY_FILE=$(host_path "$key")
export ITB_WALLET_KEY_FILE
export ITB_NETWORK=devnet ITB_RPC_URL=https://api.devnet.solana.com ITB_WS_URL=wss://api.devnet.solana.com
# Git for Windows gets no path conversion under MSYS_NO_PATHCONV, so it takes the host path too.
git_repo() { git -C "$(host_path "$repo")" "$@"; }
repo_state() { git_repo status --porcelain -- . ':!data' ':!logs'; }
head=$(git_repo rev-parse HEAD) && [ -n "$head" ] || { echo "devnet.sh: $repo is not a git checkout" >&2; exit 2; }
ITB_GIT_COMMIT=$head$(git_repo diff --quiet HEAD -- . ':!data' ':!logs' || echo -dirty)
export ITB_GIT_COMMIT
repo_before=$(repo_state) || exit 2
compose_file=$(host_path "$repo/compose.yaml")
dc() { docker compose -f "$compose_file" --profile measure "$@"; }
stamp=$(date -u +%Y%m%dT%H%M%SZ)
transcript="$repo/logs/devnet-pipeline-$stamp.txt"
mkdir -p "$repo/logs"
exec > >(tee "$transcript") 2>&1

step() { printf '\n== %s (%s)\n' "$1" "$(date -u +%H:%M:%SZ)"; }
failed=()
skipped=()
check() { local name=$1; shift; if "$@"; then echo "-- $name: ok"; else echo "-- $name: FAILED"; failed+=("$name"); fi; }
# rpc METHOD PARAMS FIELD: one JSON-RPC call from the plan image (the host needs no
# Python); FIELD is "value" or "top_identity", the identity of the most-staked validator.
rpc() {
    dc run --rm --no-deps -T --entrypoint python plan -c 'import json, os, sys, urllib.request as u
q = u.Request(os.environ["ITB_RPC_URL"], json.dumps(dict(jsonrpc="2.0", id=1, method=sys.argv[1], params=json.loads(sys.argv[2]))).encode(), {"Content-Type": "application/json"})
r = json.load(u.urlopen(q, timeout=30))["result"]
pick = {"value": lambda r: r["value"],
        "top_identity": lambda r: max(r["current"], key=lambda a: a["activatedStake"])["nodePubkey"]}
print(pick[sys.argv[3]](r))' "$1" "$2" "$3" | tr -d '\r'
}
draw_plan() {
    local out
    out=$(dc run --rm --no-deps -T plan plan --network devnet --bursts "$bursts" --lead-slots 300) || { echo "$out"; return 1; }
    echo "$out" >&2
    printf '%s\n' "$out" | sed -n 's|^plan: /repo/data/\(plans/.*plan\.json\)$|\1|p' | tr -d '\r'
}
run_id_of() { sed -n 's/^itb-probe [A-Za-z-]* run \([^:]*\):.*/\1/p' "$1" | head -1; }
echo "commit $ITB_GIT_COMMIT, transcript logs/devnet-pipeline-$stamp.txt"

step "probe image (built as RUNNING.md says)"
docker image inspect inside-the-block-probe:local >/dev/null 2>&1 || { echo "build the probe image first (RUNNING.md)"; exit 1; }

step "funded public address the dry-run simulates from"
# The identity of the validator with the most stake pays its vote fees, so it holds SOL.
ITB_SIM_PAYER=$(rpc getVoteAccounts '[{"commitment":"confirmed"}]' top_identity) && [ -n "$ITB_SIM_PAYER" ] || exit 1
export ITB_SIM_PAYER
echo "simulation payer $ITB_SIM_PAYER, $(rpc getBalance "[\"$ITB_SIM_PAYER\"]" value) lamports"

step "plan"
plan_a=$(draw_plan) && [ -n "$plan_a" ] || { echo "no plan path in the output"; exit 1; }

step "the key as the probe container sees it"
dc run --rm --no-deps -T --entrypoint sh probe -c \
    'stat -c "key mode %a, owner %u:%g, type %F" /run/secrets/wallet_key; echo "process uid $(id -u), gid $(id -g)"'

step "live run under a limit below the plan cost: must refuse before sending"
out=$(mktemp)
dc run --rm --no-deps -T probe run --plan "/data/$plan_a" --live --max-spend-lamports 1000 > "$out" 2>&1
code=$?
cat "$out"
refusal_id=$(run_id_of "$out")
rm -f "$out"
check "refusal exits non-zero" test "$code" -ne 0
check "log shows limit_refusal" grep -q '"event":"limit_refusal"' "$repo/logs/$refusal_id.jsonl"
check "refusal wrote no raw data" test ! -e "$repo/data/runs/$refusal_id"

step "dry-run of the same plan: zero streams, every probe simulated"
out=$(mktemp)
dc run --rm --no-deps -T probe run --plan "/data/$plan_a" > "$out" 2>&1
code=$?
cat "$out"
dry_id=$(run_id_of "$out")
rm -f "$out"
check "dry-run" test "$code" -eq 0
rows="$repo/data/runs/$dry_id/probes.jsonl"
sends=$(grep -c '"kind":"send"' "$rows")
clean=$(grep '"kind":"send"' "$rows" | grep '"result":"simulated"' | grep -c '"simulate":{"err":null')
echo "dry-run: $sends send rows, $clean simulated without error"
check "dry-run rows simulated without error" test "${sends:-0}" -gt 0 -a "$clean" = "$sends"

step "wallet balance"
status=$(dc run --rm --no-deps -T probe status | tr -d '\r')
echo "$status"
wallet=$(printf '%s\n' "$status" | sed -n 's/^wallet \([1-9A-HJ-NP-Za-km-z]*\).*/\1/p')
[ -n "$wallet" ] || { echo "no wallet address in the probe status"; exit 1; }
balance=$(rpc getBalance "[\"$wallet\"]" value)
echo "wallet $wallet holds $balance lamports"

if [ "${balance:-0}" -lt 12000000 ]; then
    echo "-- live run, collect, verify: SKIPPED (fund $wallet at faucet.solana.com, about 0.012 SOL)"
    skipped+=("live run" "collect" "verify")
else
    step "second plan, live, with funding and closing"
    plan_b=$(draw_plan) && [ -n "$plan_b" ] || { echo "no plan path in the output"; exit 1; }
    out=$(mktemp)
    dc run --rm --no-deps -T probe run --plan "/data/$plan_b" --live --max-spend-lamports 2000000 --close-after > "$out" 2>&1
    code=$?
    cat "$out"
    live_id=$(run_id_of "$out")
    rm -f "$out"
    check "live run" test "$code" -eq 0
    dc run --rm --no-deps -T probe status

    step "collect, after the run's slots finalize"
    sleep 40
    check "collect" dc run --rm --no-deps -T collect collect "$live_id" --network devnet

    step "verify (reads the v1 probes with maxSupportedTransactionVersion 1)"
    check "verify" dc run --rm --no-deps -T reproduce verify --network devnet
fi

step "search everything the runs wrote for the bytes of the key"
check "keyscan" dc run --rm --no-deps -T -v "$ITB_WALLET_KEY_FILE:/keys/wallet-key.json:ro" \
    -v inside-the-block_itb-state:/scan/state:ro --entrypoint python reproduce \
    tests/keyscan.py /keys/wallet-key.json /repo/data /repo/logs /scan/state

step "nothing outside data/ and logs/ changed"
check "repository untouched" test "$(repo_state || echo git-failed)" = "$repo_before"

if [ ${#failed[@]} -gt 0 ]; then
    printf '\ndevnet pipeline test FAILED: %s\n' "${failed[*]}"
    exit 1
fi
if [ ${#skipped[@]} -gt 0 ]; then
    printf '\ndevnet pipeline test incomplete, skipped: %s\n' "${skipped[*]}"
    exit 3
fi
printf '\ndevnet pipeline test passed\n'
