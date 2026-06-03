---
id: P0-CI-01
title: CI, lint, testes e client OpenAPI
phase: 0
etapa: "Etapa 2 — Refatoração modular"
area: CI
status: done
depends_on: [P0-MOD-03, P0-MOD-04]
blocks: []
tests: none
---

# P0-CI-01 — CI, lint, testes e client OpenAPI

## Contexto
Depois do refactor modular (módulos, remoção de `items`, `account_users`), o CI, os scripts e o client OpenAPI do frontend precisam refletir a nova estrutura e continuar verdes.

## Docs de referência
- [16 — Testing Strategy](../../16_testing_strategy.md)

## Escopo (o que ENTRA)
- Ajustar GitHub Actions (`.github/workflows/`) e `.pre-commit-config.yaml` para os novos paths de `app/modules/*`.
- Garantir `backend/scripts/lint.sh`, `format.sh`, `test.sh` rodando na estrutura nova.
- Habilitar **Ruff pydocstyle** (`D` + `convention = "google"`) no `pyproject.toml` para exigir docstrings (ver `CLAUDE.md`/DEC-13); garantir que o código da Fase 0 passa.
- Ajustar/limpar testes do template que referenciam `items`/`user` antigos.
- Regenerar o client OpenAPI do frontend (`npm run generate-client`) após mudanças de rota.

## Fora de escopo (o que NÃO entra)
- Build de imagens + deploy automatizado (CD) → Fase 6 (`P6-CICD-*`).
- Novos testes de domínio (multi-tenant, catálogo, etc.) → fases respectivas.

## Arquivos a criar/alterar
- `.github/workflows/*` (alterar) — paths/jobs.
- `.pre-commit-config.yaml` (alterar).
- `backend/pyproject.toml` (alterar) — `[tool.ruff.lint]` adicionar `D` + `convention = "google"`.
- `backend/tests/*` (alterar) — remover/ajustar testes de item/user antigos.
- `frontend/src/client/*` (regenerar).

## Passos
1. Rodar lint/format/test localmente e corrigir o que o refactor quebrou.
2. Atualizar workflows e pre-commit.
3. Regenerar o client OpenAPI e ajustar imports no frontend.
4. Conferir o CI no push.

## Testes
> Fundações §10. Task meta — não tem teste próprio; **garante** que os testes rodam.

- **Níveis:** meta — assegura unit + integração (backend) e `vitest` (front) rodando no CI, com `coverage`/`mypy`.
- **Quando:** —

## Definition of Done
- [x] `lint` + type check + testes do backend passam localmente *(mypy/ty/ruff/format verdes; 69 testes; cobertura 90%, gate `--fail-under=90`)*.
- [x] Client OpenAPI regenerado, sem referências a endpoints removidos *(sem `Item*`; `items.spec.ts`/`PendingItems.tsx` removidos)*.
- [~] CI verde no GitHub Actions — workflows ajustados para a estrutura/portas novas; **não executado ao vivo** (o usuário gerencia o git; sem push nesta sessão).

## Notas / Reconciliações
- Esta é a parte de **CI** (Etapa 1 do roadmap). O **CD** (deploy automatizado) é a Etapa 21, na Fase 6.
- **Docstrings (DEC-13):** habilitado Ruff `D` + `convention = "google"` no `backend/pyproject.toml`; `tests/**` isento via `per-file-ignores` (testes documentam intenção pelos nomes/asserts). Docstrings Google adicionadas em todos os módulos/pacotes/funções/métodos do template em `app/` (deps, config, security, db, utils, routes/auth dos accounts, entry scripts). Gate `ruff check app` verde.
- **Client OpenAPI:** regenerado com `@hey-api/openapi-ts` (via `npm run generate-client`; `generate-client.sh` usa `bun`, ausente local — saída idêntica, mesmo gerador). `frontend/openapi.json` é gitignored (artefato). Removidos o componente órfão `PendingItems.tsx` e o E2E morto `tests/items.spec.ts` + helpers `randomItem*`.
- **Cobertura:** o teste de integração da fila exigido pela `P0-CFG-04` (enqueue de `dummy_task` + worker `--burst` processa) estava faltando → criado `tests/integration/test_queue_sample.py`, o que cobre `queue.py` e leva o total a 90% (gate do CI).
- **Portas no CI (consequência da `P0-CFG-02`):** o `compose.override.yml` publica em portas não-padrão (db 5442, redis 6399, backend 8800, frontend 5180) e o `docker compose` mescla o override no CI. Ajustes: `test-backend.yml` sobe `db redis mailcatcher` e roda os passos de host com `POSTGRES_PORT=5442`/`REDIS_PORT=6399` (env de job; só backend/worker usam `${POSTGRES_PORT}` e não são iniciados aqui); `test-docker-compose.yml` faz `curl` em `8800`/`5180`. Os containers seguem usando portas internas padrão (5432/6379).
- **Lockfile do frontend (1ª execução do CI):** o repo é um **workspace bun** com `bun.lock` único na **raiz**. A `P0-TEST-01` adicionou deps de teste (`vitest`, `@testing-library/*`, `jsdom`) ao `frontend/package.json` sem regenerar o lockfile → `bun ci` (`--frozen-lockfile`, usado em `playwright` e `pre-commit`) falhava com *"lockfile had changes, but lockfile is frozen"*. Resolvido regenerando `bun.lock` (`bun install` na raiz, bun 1.3.14 = versão do CI). **Regra:** ao mexer em `frontend/package.json`, sempre regenerar e commitar o `bun.lock` da raiz.
- **Branch dos workflows:** gatilho de **push** em `development` (branch de integração) nos workflows de CI/teste (`test-backend`, `test-docker-compose`, `playwright`); os `pull_request` seguem disparando em qualquer PR. `main` (produção) fica **sem gatilho** por ora. Os de deploy (CD) ficam para a Fase 6.
- **Limpeza de automação do template:** removidos os workflows voltados ao fluxo open-source do upstream, que falhavam ou não se aplicam (dependiam de secrets do `fastapi org`): `add-to-project`, `labeler` (+ config `.github/labeler.yml`), `smokeshow`, `issue-manager`, `latest-changes` e `detect-conflicts`. Sobram em `.github/workflows/`: os 4 de CI + `deploy-production`/`deploy-staging` (placeholders dormentes da Fase 6).
