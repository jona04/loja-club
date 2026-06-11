#!/usr/bin/env bash
#
# ci-local.sh — roda LOCALMENTE tudo que o CI roda e imprime um resumo no fim.
#
# Espelha os 4 jobs do CI (.github/workflows/):
#   test-backend ........ lint (mypy/ty/ruff/format) + pytest + coverage >= 90%
#   pre-commit .......... hooks de higiene (eof/trailing-ws/yaml/toml) via `prek`
#   playwright .......... e2e no docker (dashboard + admin)
#   test-docker-compose . smoke: sobe o stack e bate health-check
# ...e os lint/testes de frontend que não têm job próprio no CI:
#   biome (lint) + vitest (unit) de cada frontend. (O build dos frontends é
#   feito no docker — não é repetido aqui.)
#
# Uso:
#   bash scripts/ci-local.sh             # tudo (lento: ~10-15 min com docker)
#   bash scripts/ci-local.sh --quick     # pula e2e + smoke (sem docker pesado)
#   bash scripts/ci-local.sh --no-e2e    # pula só o e2e
#   bash scripts/ci-local.sh --no-smoke  # pula só o smoke do stack
#   bash scripts/ci-local.sh -h
#
# Não para no primeiro erro: roda tudo e mostra um resumo PASS/FAIL no final
# (exit != 0 se algo falhar). Logs completos de cada passo ficam em /tmp.
#
# Pré-requisitos: docker, uv, e os binários do bun-workspace em node_modules/.bin
# (frontends). `prek` e a 1ª execução de hooks são baixados sob demanda (uvx).
# Limitação: o hook `generate-frontend-sdk` (regenera o cliente) precisa de bun e
# é pulado aqui — rode-o no docker se quiser checar staleness do SDK.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export POSTGRES_PORT="${POSTGRES_PORT:-5442}"
export REDIS_PORT="${REDIS_PORT:-6399}"

RUN_E2E=1
RUN_SMOKE=1
for arg in "$@"; do
  case "$arg" in
    --quick) RUN_E2E=0; RUN_SMOKE=0 ;;
    --no-e2e) RUN_E2E=0 ;;
    --no-smoke) RUN_SMOKE=0 ;;
    -h|--help) sed -n '2,/^set -/p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//; s/^set -.*//'; exit 0 ;;
    *) echo "argumento desconhecido: $arg (use -h)"; exit 2 ;;
  esac
done

LOGDIR="$(mktemp -d -t ci-local.XXXXXX)"
declare -a S_NAME S_RES S_TIME

# step "Rótulo" comando args... — roda o comando, registra PASS/FAIL + duração.
step() {
  local name="$1"; shift
  local log="$LOGDIR/$(printf '%s' "$name" | tr -c 'A-Za-z0-9' '_').log"
  printf '\n\033[1;36m── %s\033[0m\n' "$name"
  local t0=$SECONDS
  if "$@" >"$log" 2>&1; then
    S_RES+=("PASS")
    printf '   \033[32m✔ PASS\033[0m (%ss)\n' "$((SECONDS - t0))"
  else
    S_RES+=("FAIL")
    printf '   \033[31m✗ FAIL\033[0m (%ss) — fim do log:\n' "$((SECONDS - t0))"
    tail -n 20 "$log" | sed 's/^/     │ /'
  fi
  S_NAME+=("$name")
  S_TIME+=("$((SECONDS - t0))")
}

# ───────────────────────── Backend (job: test-backend) ─────────────────────────
step "backend · lint (mypy/ty/ruff/format)" bash -c 'cd backend && uv run bash scripts/lint.sh'
step "infra · sobe db/redis/mailcatcher"    docker compose up -d --wait db redis mailcatcher
step "backend · migrations (prestart)"      bash -c 'cd backend && uv run bash scripts/prestart.sh'
step "backend · pytest + coverage ≥90%"     bash -c 'cd backend && uv run coverage run -m pytest tests/ && uv run coverage report --fail-under=90'

# ──────────────────── Pre-commit / higiene (job: pre-commit) ────────────────────
# `prek` é o tool que o CI usa. Pulamos os hooks locais que precisam de uv/bun
# (cobertos pelos passos de lint acima); sobram os de higiene de arquivo — que
# foram o que escapou (eof/trailing-whitespace).
step "hooks · pre-commit (prek: eof/trailing-ws/yaml/toml)" \
  env SKIP=local-biome-check,local-ruff-check,local-ruff-format,local-mypy,local-ty,generate-frontend-sdk,add-release-date \
  uvx prek run --all-files

# ───────────────── Frontends: lint (biome) + testes (vitest) ─────────────────
# Build (tsc + vite/next build) NÃO entra aqui — é feito quando você sobe o docker.
for fe in frontend-dashboard frontend-admin; do
  step "$fe · biome (lint)"  bash -c "cd '$fe' && ../node_modules/.bin/biome check --no-errors-on-unmatched --files-ignore-unknown=true ./src"
  step "$fe · vitest (unit)" bash -c "cd '$fe' && ../node_modules/.bin/vitest run --passWithNoTests"
done
step "frontend-storefront · biome (lint)" bash -c "cd frontend-storefront && ../node_modules/.bin/biome check app"

# ──────────────────────── E2E docker (job: playwright) ──────────────────────────
if [ "$RUN_E2E" = 1 ]; then
  step "e2e · dashboard (playwright)"   bash -c 'CI=1 docker compose run --build --rm playwright bunx playwright test'
  step "e2e · admin (playwright-admin)" bash -c 'CI=1 docker compose run --build --rm playwright-admin bunx playwright test'
fi

# ─────────────────── Smoke do stack (job: test-docker-compose) ──────────────────
if [ "$RUN_SMOKE" = 1 ]; then
  step "docker · smoke do stack" bash -c '
    docker compose up -d --wait backend frontend-dashboard adminer &&
    curl -fsS http://localhost:8800/api/v1/utils/health-check >/dev/null &&
    curl -fsS http://localhost:5180 >/dev/null'
fi

# ──────────────────────────────── Resumo ────────────────────────────────
printf '\n\033[1m═══════════════════ RESUMO ═══════════════════\033[0m\n'
fails=0
for i in "${!S_NAME[@]}"; do
  if [ "${S_RES[$i]}" = PASS ]; then
    printf '  \033[32m✔\033[0m %-46s %3ss\n' "${S_NAME[$i]}" "${S_TIME[$i]}"
  else
    printf '  \033[31m✗ %-46s %3ss\033[0m\n' "${S_NAME[$i]}" "${S_TIME[$i]}"
    fails=$((fails + 1))
  fi
done
printf '\033[1m═══════════════════════════════════════════════\033[0m\n'
echo "  logs completos: $LOGDIR"
if [ "$fails" -gt 0 ]; then
  printf '\n\033[31m✗ CI local FALHOU em %s passo(s).\033[0m\n' "$fails"
  exit 1
fi
printf '\n\033[32m✔ CI local: tudo verde.\033[0m\n'
