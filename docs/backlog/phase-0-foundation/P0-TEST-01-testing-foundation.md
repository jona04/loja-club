---
id: P0-TEST-01
title: Fundação de testes (layout, isolamento, mocks, vitest)
phase: 0
etapa: "Etapa 2 — Refatoração modular"
area: TEST
status: todo
depends_on: []
blocks: []
tests: meta
---

# P0-TEST-01 — Fundação de testes

## Contexto
O template é integração-pesado (Pytest contra Postgres real, limpeza por `delete` no fim da sessão) e o frontend só tem Playwright (E2E). Para seguir a regra de testes das Fundações (§10) — unit para lógica pura, integração no seam, E2E para jornadas — precisamos do **chão de testes** antes de escrever os testes das fases: layout, isolamento por teste, mock de externos e runner de unit no frontend.

## Docs de referência
- [16 — Testing Strategy](../../16_testing_strategy.md)
- [Fundações & Gargalos §10](../_foundations-and-bottlenecks.md) (INV-TEST-1/2, DEC-9/10/11)

## Escopo (o que ENTRA)
- **Backend layout:** `backend/tests/unit/` e `backend/tests/integration/`; mover os testes de rota/crud atuais para `integration/`.
- **Isolamento por teste (DEC-10):** fixture que roda cada teste numa **transação com rollback** (savepoint), substituindo o `delete(User/Item)` de fim de sessão do `conftest.py`. Cada teste começa limpo, sem depender de ordem.
- **Mock de externos (DEC-11):** convenção/fixtures para **S3 via `moto`** (ou botocore stubber), e-mail (já via `patch`), relógio e aleatoriedade — para não bater na AWS nem em rede em teste.
- **Frontend unit (DEC-9):** adicionar **`vitest` + `@testing-library/react`** ao `frontend/`; script `test:unit`; setup; manter Playwright para E2E.
- **Samples provando o chão:** 1 teste unit backend, 1 integração backend (round-trip no DB com rollback), 1 unit frontend (ex.: formatação de moeda/locale).
- Ajustar `backend/scripts/test.sh` para rodar `unit` + `integration` com `coverage` (mantendo `mypy strict`/`ruff`).

## Fora de escopo (o que NÃO entra)
- **Fixtures/factories multi-tenant** (criar loja/membro/cliente) e **testes de isolamento A≠B** → **Fase 1** (precisam de `Store`/`StoreMember`).
- Testes de domínio reais (catálogo, 3D, checkout…) → cada fase.
- Integração do CI com esses comandos → `P0-CI-01`.

## Passos
1. Criar `tests/unit/` e `tests/integration/`; mover os testes existentes para `integration/`.
2. Reescrever o `conftest.py`: engine de teste + fixture de **sessão transacional com rollback por teste**; fixtures `client`, tokens.
3. Adicionar fixtures de mock (S3 `moto`, e-mail, clock/random).
4. Frontend: instalar `vitest`+RTL, `vitest.config`, setup e script `test:unit`.
5. Escrever os 3 samples e validar que rodam isolados.

## Testes
> Esta task **é** a fundação de testes; seus "testes" são os samples que provam o chão.

- **Níveis:** meta — habilita unit + integração (backend) e unit (frontend).
- **Quando escrever:** durante.
- **Cobrir:**
  - sample unit backend (função pura) + sample integração backend (DB com rollback) + sample unit frontend (componente/formatação).

## Definition of Done
- [ ] `pytest tests/unit` e `pytest tests/integration` rodam separados e no conjunto.
- [ ] Cada teste roda **isolado** (rollback por teste; sem vazar estado; independente de ordem).
- [ ] Um teste de integração que usa S3 passa com **S3 mockado** (sem AWS real).
- [ ] `npm run test:unit` (vitest) roda no frontend com um teste de exemplo verde.
- [ ] `coverage` e `mypy strict` seguem no gate.

## Notas / Reconciliações
- **Vem cedo** (logo após `P0-CFG-01`), **antes de qualquer task que escreve teste** (CFG-02/03/04, MOD-*), para que esses testes já nasçam no layout/isolamento novos. Usa a stack do template, que **já roda** — não depende do refactor. As tasks de refactor (`MOD-03`/`MOD-04`) ajustam seus próprios testes dentro do que é estabelecido aqui.
- Lib de teste backend = **`pytest`** (DEC-12, já no template); front = **`vitest`** (DEC-9).
- **Smoke** (app sobe / `/health` / OpenAPI) entra como teste de **integração raso** (§10), **não** é teste manual. O template já tem readiness no `backend_pre_start.py` (`select 1`) e o healthcheck do compose — reaproveitar.
- O `conftest.py` atual limpa por `delete` no fim da sessão; será substituído pelo **rollback por teste** (DEC-10).
