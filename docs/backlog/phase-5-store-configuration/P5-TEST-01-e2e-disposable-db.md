---
id: P5-TEST-01
title: Banco descartável pro e2e (corrige poluição do db de dev)
phase: 5
etapa: "Etapa 1 — Groundwork (e2e + doc de banco)"
area: TEST
status: todo
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
- O **banco de dev (`app`) nunca é tocado** por teste; `docker compose down -v` reseta só o `db-test`.

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
- [ ] `db-test` + `backend-e2e` no compose; `playwright*` apontando pra ele.
- [ ] e2e (dashboard + admin) **verde** contra o db descartável.
- [ ] Banco de dev **não** ganha usuários após rodar o e2e; `down -v` reseta só o `db-test`.
- [ ] **Modos de falha mapeados** (backend-e2e não sobe / db-test não migra) → tratados ou Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Fecha o follow-up "e2e polui o db de dev" da Fase 4 (marcar `[x]` lá ao concluir).

## Follow-ups
- [ ] — nenhum (preencher ao implementar).
