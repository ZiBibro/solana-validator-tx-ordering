#!/usr/bin/env bash
# Live mainnet campaign, one table epoch after another (plan-implementation, sections 10 and 11).
#
#   scripts/campaign.sh PANEL FIRST_EPOCH [FROM_INDEX [TO_INDEX]]
#
# PANEL is the panel file relative to the repository (data/panels/<id>/panel.json).
# Epoch index e of prereg/campaign-table.json runs in chain epoch FIRST_EPOCH+e, for e
# from FROM_INDEX (default 0) to TO_INDEX (default 3). For each index the script draws
# the plan from the live leader schedule, runs it live under a limit of the journal's
# committed lamports plus the plan's worst-case fees plus the funding and closing
# overhead, closes the payers and collects the run.
#
# Epochs run one after another because they share the payers and the spend journal.
# The plan of index e+1 is drawn once run e has ended; a round whose windows have
# passed by then is left out and noted in draw-notes.json (the missed-round rule).
# A failed run is collected and its index drawn again after a pause: the new plan
# keeps the windows of the rounds still ahead and leaves out the round in progress,
# so no burst runs twice. An index with no round ahead hands over to the next one;
# three failed attempts on one index stop the campaign. Running the script again with
# FROM_INDEX resumes a stopped campaign the same way.
#
# It needs the campaign anchor on chain (probe anchor --stage campaign --live) and the
# wallet key file in ITB_WALLET_KEY_FILE, which only the probe container reads.
# ITB_EXTRA_CA_PEM, when set, reaches the plan service (README, TLS-inspecting proxy);
# ITB_EXTRA_CA_FILE names the same root as a file, and the script passes on its text.
# The transcript lands in logs/campaign-<stamp>.txt.
set -uo pipefail
export MSYS_NO_PATHCONV=1

here=$(cd "$(dirname "$0")" && pwd)
repo=$(cd "$here/.." && pwd)
[ $# -ge 2 ] || { sed -n 4p "$0" >&2; exit 2; }
panel=$1 first_epoch=$2 from=${3:-0} to=${4:-3}
attempts=3 pause=600
# Probe overhead for a run with --close-after: one close fee for funding plus one per
# payer closed, CLOSE_FEE * (1 + keys::PAYERS) in probe/src/session.rs.
overhead=65000

[ -f "$repo/$panel" ] || { echo "campaign.sh: no panel $repo/$panel" >&2; exit 2; }
[ -f "$repo/prereg/manifest-campaign.json" ] || { echo "campaign.sh: no prereg/manifest-campaign.json" >&2; exit 2; }
[ -n "${ITB_WALLET_KEY_FILE:-}" ] && [ -f "$ITB_WALLET_KEY_FILE" ] \
    || { echo "campaign.sh: ITB_WALLET_KEY_FILE names no file" >&2; exit 2; }
unset ITB_WALLET_KEY ITB_SIM_PAYER
if [ -z "${ITB_EXTRA_CA_PEM:-}" ] && [ -n "${ITB_EXTRA_CA_FILE:-}" ]; then
    ITB_EXTRA_CA_PEM=$(cat "$ITB_EXTRA_CA_FILE") \
        || { echo "campaign.sh: ITB_EXTRA_CA_FILE names no readable file" >&2; exit 2; }
    export ITB_EXTRA_CA_PEM
fi
export ITB_NETWORK=mainnet ITB_RPC_URL=https://api.mainnet-beta.solana.com ITB_WS_URL=wss://api.mainnet-beta.solana.com

# Docker Desktop on Windows takes C:/... paths, and so does Git for Windows under MSYS_NO_PATHCONV.
host_path() { if command -v cygpath >/dev/null 2>&1; then cygpath -m "$1"; else printf '%s\n' "$1"; fi; }
git_repo() { git -C "$(host_path "$repo")" "$@"; }
head=$(git_repo rev-parse HEAD) && [ -n "$head" ] || { echo "campaign.sh: $repo is not a git checkout" >&2; exit 2; }
ITB_GIT_COMMIT=$head$(git_repo diff --quiet HEAD -- . ':!data' ':!logs' || echo -dirty)
export ITB_GIT_COMMIT
compose_file=$(host_path "$repo/compose.yaml")
dc() { docker compose -f "$compose_file" --profile measure "$@"; }
stamp=$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p "$repo/logs"
exec > >(tee "$repo/logs/campaign-$stamp.txt") 2>&1
scratch=$(mktemp)
trap 'rm -f "$scratch"' EXIT

committed() {
    dc run --rm --no-deps -T probe status | sed -n 's|^spend journal: \([0-9][0-9]*\) of .*|\1|p' | tr -d '\r' | head -n 1
}

echo "commit $ITB_GIT_COMMIT, $(date -u +%FT%TZ), panel $panel, epoch indexes $from to $to from chain epoch $first_epoch"
for e in $(seq "$from" "$to"); do
    epoch=$((first_epoch + e))
    attempt=1
    while :; do
        echo "== epoch index $e in chain epoch $epoch, attempt $attempt, $(date -u +%FT%TZ)"
        out=$(dc run --rm --no-deps -T plan campaign --panel "$panel" --epoch-index "$e" --epoch "$epoch" 2>&1)
        code=$?
        echo "$out"
        if [ $code -ne 0 ]; then
            case $out in *"found a window from slot"*) echo "no round of epoch index $e lies ahead"; break ;; esac
            echo "plan exit $code"
        else
            plan=$(printf '%s\n' "$out" | sed -n 's|^campaign: /repo/data/\(plans/.*plan\.json\)$|\1|p' | tr -d '\r')
            fees=$(printf '%s\n' "$out" | sed -n 's|^campaign: epoch index .*, fees \([0-9][0-9]*\) lamports .*|\1|p' | tr -d '\r')
            spent=$(committed)
            if [ -z "$plan" ] || [ -z "$fees" ] || [ -z "$spent" ]; then
                echo "plan path, fee total or committed lamports missing: '$plan' '$fees' '$spent'"
                code=1
            else
                limit=$((spent + fees + overhead))
                echo "== live run: limit $limit lamports = committed $spent + plan fees $fees + overhead $overhead"
                dc run --rm --no-deps -T probe run --plan "/data/$plan" --live --max-spend-lamports "$limit" --close-after 2>&1 \
                    | tee "$scratch"
                code=${PIPESTATUS[0]}
                echo "probe run exit $code"
                run_id=$(sed -n 's|^itb-probe LIVE run \([^:]*\):.*|\1|p' "$scratch" | tr -d '\r' | head -n 1)
                if [ -n "$run_id" ]; then
                    dc run --rm --no-deps -T collect collect "$run_id" --network mainnet
                    ccode=$?
                    echo "collect $run_id exit $ccode"
                    [ $ccode -eq 0 ] || code=$ccode
                fi
                dc run --rm --no-deps -T probe status
            fi
        fi
        [ $code -eq 0 ] && break
        if [ $attempt -ge $attempts ]; then
            echo "campaign stopped at epoch index $e after $attempt attempts, $(date -u +%FT%TZ)"
            exit 1
        fi
        attempt=$((attempt + 1))
        sleep "$pause"
    done
done
echo "campaign done, $(date -u +%FT%TZ)"
