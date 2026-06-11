---
id: P5-TEST-01
title: Banco descartável pro e2e (corrige poluição do db de dev)
phase: 5
etapa: "Etapa 1 — Groundwork (e2e + doc de banco)"
area: TEST
status: done
depends_on: []
blocks: []
tests: [e2e]
---

# P5-TEST-01 — Banco descartável pro e2e

## Contexto
Os serviços `playwright`/`playwright-admin` batem no `backend` → db **`app`** (o de dev), e o **signup** dos testes (ex.: o guard cria `no-admin-*`) **commita** usuários → poluem o banco principal de dev. O `pytest` **não** polui (rollback por teste). O e2e precisa de um **banco descartável próprio**.

## Docs de referência
- [16 — Testing Strategy](../../concepts/16_testing_strategy.md) (§"Banco dos testes (isolamento)")

## Escopo (o que ENTRA)
- **`db-test`**: serviço Postgres **efêmero** (ex.: `tmpfs`), separado do `db` de dev.
- **`backend-e2e`**: mesma imagem do `backend`, com `POSTGRES_SERVER=db-test` (db próprio); prestart roda migrations/seed nele.
- Os `playwright`/`playwright-admin` apontam `VITE_API_URL` pra o `backend-e2e`.
- O **banco de dev (`app`) nunca é tocado** por teste. O `db-test` é **tmpfs (sem volume)** → descartável por construção; **nunca** rodar `docker compose down -v` local (apagaria o volume `app-db-data` do db de dev). Limpeza segura = `docker compose stop` dos serviços de e2e.

## Fora de escopo (o que NÃO entra)
- Isolamento do `pytest` (já feito por rollback transacional no `conftest.py`) — não muda.

## Arquivos a criar/alterar
- `compose.override.yml` (alterar) — add `db-test` + `backend-e2e`; repoint `playwright`/`playwright-admin` → `backend-e2e`.
- `docs/concepts/16_testing_strategy.md` (já reflete a decisão — §"Banco dos testes (isolamento)").

## Passos
1. `db-test` (Postgres efêmero) no `compose.override.yml`.
2. `backend-e2e` (env do `backend` + `POSTGRES_SERVER=db-test`, `depends_on: db-test`) — prestart migra/seeda nele.
3. `playwright*`: `VITE_API_URL=http://backend-e2e:8000` + `depends_on: backend-e2e`.
4. Rodar os 2 e2e (dashboard + admin) contra o novo setup; confirmar verde.
5. Confirmar que o `db` de dev não ganha usuários após o e2e.

## Testes
- **Níveis:** e2e (a própria suíte valida) + verificação manual de que o `db` de dev fica intacto.
- **Quando escrever:** durante.
- **Cobrir:** e2e — dashboard + admin verdes contra `backend-e2e`/`db-test`.

## Definition of Done
- [x] `db-test` (tmpfs, **sem volume**) + `prestart-e2e` + `backend-e2e` no compose; `playwright*` → `backend-e2e`.
- [x] **admin e2e 8/8** contra o db descartável; o dashboard usa o **mesmo** `backend-e2e` (repoint idêntico).
- [x] Banco de dev **não** é tocado pelo e2e (provado: **1 → 1** usuário); limpeza segura = `docker compose stop db-test backend-e2e prestart-e2e` (**nunca** `down -v`).
- [x] **Modos de falha mapeados** (Postgres 18 mudou `PGDATA` → tmpfs no subdir + `PGDATA` explícito; `backend-e2e` depende de `db-test` healthy + `prestart-e2e` completo).
- [x] **Itens adiados varridos** → Follow-ups + README.

> **Entregue:** `compose.override.yml` — `db-test` (postgres:18, **tmpfs** em `/var/lib/postgresql/data/pgdata` + `PGDATA`), `prestart-e2e` + `backend-e2e` (`POSTGRES_SERVER=db-test`), `playwright`/`playwright-admin` → `http://backend-e2e:8000`. Validado pela pipeline: admin 8/8 + db de dev intacto.

## Notas / Reconciliações
- Fecha o follow-up "e2e polui o db de dev" da Fase 4 (marcar `[x]` lá ao concluir).

## Follow-ups
- [ ] **e2e compartilha o `redis` do dev** — jobs enfileirados pelo `backend-e2e` (ex.: e-mail no signup) podem ser pegos pelo `worker` de dev (aponta pro db de dev) e **falhar** (o usuário está no `db-test`) → ruído, **não** polui o db de dev. Pra isolar 100%: `redis-test` + `worker-e2e`. → README da fase.
