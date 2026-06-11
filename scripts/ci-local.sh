#!/usr/bin/env bash
#
# ci-local.sh -- run LOCALLY everything CI runs and print a summary at the end.
#
# Mirrors the 4 CI jobs (.github/workflows/):
#   test-backend ........ lint (mypy/ty/ruff/format) + pytest + coverage >= 90%
#   pre-commit .......... file-hygiene hooks (eof/trailing-ws/yaml/toml) via `prek`
#   playwright .......... e2e in docker (dashboard + admin)
#   test-docker-compose . smoke: bring the stack up and hit the health-check
# ...plus the frontend lint/tests that have no dedicated CI job:
#   biome (lint) + vitest (unit) for each frontend. (Frontend builds happen when
#   you bring docker up -- not repeated here.)
#
# The e2e runs against a DISPOSABLE database (`db-test`, tmpfs) through
# `backend-e2e`, never the dev db. That routing lives in compose.override.yml
# (the playwright services depend_on backend-e2e), so the very same
# `docker compose run --rm playwright*` command used here already hits db-test.
#
# Usage:
#   bash scripts/ci-local.sh             # EVERYTHING, incl. full e2e (dashboard+admin) (~10-15 min)
#   bash scripts/ci-local.sh --quick     # skip e2e + smoke (fast lint/tests, no docker)
#   bash scripts/ci-local.sh --no-e2e    # run everything except the e2e
#   bash scripts/ci-local.sh --no-smoke  # run everything except the stack smoke
#   bash scripts/ci-local.sh -h
# Skipped steps show up as SKIPPED in the summary -- they never vanish.
#
# Does not stop at the first error: runs everything and prints a PASS/FAIL
# summary at the end (exit != 0 if anything failed). Per-step logs go to /tmp.
#
# Prereqs: docker, uv, and the bun-workspace binaries in node_modules/.bin
# (frontends). `prek` and the first hook run are fetched on demand (uvx).
# SAFETY: never `docker compose down -v` locally (it would wipe the dev db
# volume `app-db-data`). This script only uses `up` / `run --rm` / targeted
# `stop` -- the e2e db is tmpfs and disposable on its own.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# The dev db/redis are exposed on the HOST at 5442/6399. Those ports are passed
# INLINE only to the host steps (pytest/prestart) below -- they are NOT exported,
# so they never leak into `docker compose` (inside the network containers must use
# the internal 5432/6379 from .env, reached via the `db`/`redis` hostnames).

RUN_E2E=1
RUN_SMOKE=1
for arg in "$@"; do
  case "$arg" in
    --quick) RUN_E2E=0; RUN_SMOKE=0 ;;
    --no-e2e) RUN_E2E=0 ;;
    --no-smoke) RUN_SMOKE=0 ;;
    -h|--help) sed -n '2,/^set -/p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//; s/^set -.*//'; exit 0 ;;
    *) echo "unknown argument: $arg (use -h)"; exit 2 ;;
  esac
done

LOGDIR="$(mktemp -d -t ci-local.XXXXXX)"
declare -a S_NAME S_RES S_TIME

# step "Label" command args... -- run the command, record PASS/FAIL + duration.
step() {
  local name="$1"; shift
  local log="$LOGDIR/$(printf '%s' "$name" | tr -c 'A-Za-z0-9' '_').log"
  printf '\n\033[1;36m-- %s\033[0m\n' "$name"
  local t0=$SECONDS
  if "$@" >"$log" 2>&1; then
    S_RES+=("PASS")
    printf '   \033[32mPASS\033[0m (%ss)\n' "$((SECONDS - t0))"
  else
    S_RES+=("FAIL")
    printf '   \033[31mFAIL\033[0m (%ss) -- log tail:\n' "$((SECONDS - t0))"
    tail -n 20 "$log" | sed 's/^/     | /'
  fi
  S_NAME+=("$name")
  S_TIME+=("$((SECONDS - t0))")
}

# skip "Label" "reason" -- record a SKIPPED step (shown in the summary, not hidden).
skip() {
  printf '\n\033[1;36m-- %s\033[0m\n   \033[33mSKIPPED\033[0m %s\n' "$1" "${2:-}"
  S_NAME+=("$1")
  S_RES+=("SKIP")
  S_TIME+=("0")
}

# --- Backend (job: test-backend) ---
step "backend - lint (mypy/ty/ruff/format)" bash -c 'cd backend && uv run bash scripts/lint.sh'
step "infra - bring up db/redis/mailcatcher" docker compose up -d --wait db redis mailcatcher
step "backend - migrations (prestart)"       bash -c 'cd backend && POSTGRES_PORT=5442 REDIS_PORT=6399 uv run bash scripts/prestart.sh'
step "backend - pytest + coverage >=90%"     bash -c 'cd backend && POSTGRES_PORT=5442 REDIS_PORT=6399 uv run coverage run -m pytest tests/ && POSTGRES_PORT=5442 REDIS_PORT=6399 uv run coverage report --fail-under=90'

# --- Pre-commit / file hygiene (job: pre-commit) ---
# `prek` is the tool CI uses. We skip the local hooks that need uv/bun (covered
# by the lint steps above); the file-hygiene hooks remain -- those are what
# escaped before (eof/trailing-whitespace).
step "hooks - pre-commit (prek: eof/trailing-ws/yaml/toml)" \
  env SKIP=local-biome-check,local-ruff-check,local-ruff-format,local-mypy,local-ty,generate-frontend-sdk,add-release-date \
  uvx prek run --all-files

# --- Frontends: lint (biome) + tests (vitest) ---
# Build (tsc + vite/next build) is NOT here -- it happens when you bring docker up.
for fe in frontend-dashboard frontend-admin; do
  step "$fe - biome (lint)"  bash -c "cd '$fe' && ../node_modules/.bin/biome check --no-errors-on-unmatched --files-ignore-unknown=true ./src"
  step "$fe - vitest (unit)" bash -c "cd '$fe' && ../node_modules/.bin/vitest run --passWithNoTests"
done
step "frontend-storefront - biome (lint)" bash -c "cd frontend-storefront && ../node_modules/.bin/biome check app"

# --- E2E in docker (job: playwright) ---
# Routed to the disposable `db-test` through `backend-e2e` (depends_on in
# compose.override.yml) -- the dev db is never touched.
if [ "$RUN_E2E" = 1 ]; then
  step "e2e - dashboard (playwright)"   bash -c 'CI=1 docker compose run --build --rm playwright bunx playwright test'
  step "e2e - admin (playwright-admin)" bash -c 'CI=1 docker compose run --build --rm playwright-admin bunx playwright test'
  # Safe cleanup: stop ONLY the e2e services (db-test is tmpfs). Never `down -v`.
  docker compose stop db-test backend-e2e prestart-e2e >/dev/null 2>&1 || true
else
  skip "e2e - dashboard (playwright)"   "(run without --quick/--no-e2e to enable)"
  skip "e2e - admin (playwright-admin)" "(run without --quick/--no-e2e to enable)"
fi

# --- Stack smoke (job: test-docker-compose) ---
if [ "$RUN_SMOKE" = 1 ]; then
  step "docker - stack smoke" bash -c '
    docker compose up -d --build --wait backend frontend-dashboard adminer &&
    curl -fsS http://localhost:8800/api/v1/utils/health-check >/dev/null &&
    curl -fsS http://localhost:5180 >/dev/null'
else
  skip "docker - stack smoke" "(run without --quick/--no-smoke to enable)"
fi

# --- Summary ---
printf '\n\033[1m=================== SUMMARY ===================\033[0m\n'
fails=0
for i in "${!S_NAME[@]}"; do
  case "${S_RES[$i]}" in
    PASS) printf '  \033[32mok  \033[0m %-46s %3ss\n' "${S_NAME[$i]}" "${S_TIME[$i]}" ;;
    SKIP) printf '  \033[33mskip\033[0m %-46s (skipped)\n' "${S_NAME[$i]}" ;;
    *)    printf '  \033[31mFAIL %-46s %3ss\033[0m\n' "${S_NAME[$i]}" "${S_TIME[$i]}"
          fails=$((fails + 1)) ;;
  esac
done
printf '\033[1m==============================================\033[0m\n'
echo "  full logs: $LOGDIR"
if [ "$fails" -gt 0 ]; then
  printf '\n\033[31mci-local FAILED in %s step(s).\033[0m\n' "$fails"
  exit 1
fi
printf '\n\033[32mci-local: all green.\033[0m\n'
