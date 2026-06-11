---
id: P1-TEST-01
title: Fixtures/factories multi-tenant + testes de isolamento
phase: 1
etapa: "Testes"
area: TEST
status: done
depends_on: [P1-STORE-01, P1-PERM-01]
blocks: []
tests: meta
---

# P1-TEST-01 — Fixtures/factories multi-tenant + testes de isolamento

## Contexto
As Fundações §10 atribuem à **Fase 1** as **fixtures/factories multi-tenant** e a **suíte de isolamento** (precisam de `Store`). Esta task cria o ferramental de teste reutilizável (duas lojas, membros com papéis) e a suíte que prova "Loja A não vê Loja B", consumida por todas as features comerciais seguintes.

## Docs de referência
- [16 — Testing Strategy](../../16_testing_strategy.md) (isolamento é o item nº1)
- [Fundações §10 + GARGALO §2](../_foundations-and-bottlenecks.md)
- [06 — Multitenancy and Domains](../../06_multitenancy_and_domains.md)

## Escopo (o que ENTRA)
- **Factories/fixtures** em `tests/integration` (estende `P0-TEST-01`): `create_store`, `create_member(store, user, role)`, `two_stores` (A/B com owners distintos), headers de auth por membro.
- **Suíte de isolamento** (`test_tenant_isolation.py`): membro da Loja A **não** lê/edita recursos da Loja B; recurso só é encontrado com `store_id` correto (resultado observável: 403/404/ausência).
- Smoke de **permissões por papel** usando as factories (owner permitido / support negado) para validar o guard de `P1-PERM-03`.

## Fora de escopo (o que NÃO entra)
- Testes específicos de cada módulo (ficam nas tasks dos módulos; aqui só o **ferramental compartilhado** + o isolamento cross-tenant).
- E2E do painel → `P1-DASH-*`.

## Arquivos a criar/alterar
- `backend/tests/integration/conftest.py` (alterar) — fixture `two_stores`.
- `backend/tests/utils/store.py` (criar) — factories `create_user/create_store/create_member/member_headers` + `TenantContext` (em `tests/utils/`, junto de `user.py`/`utils.py`, em vez de `tests/factories.py`).
- `backend/tests/integration/test_tenant_isolation.py` (criar) — suíte de isolamento.

## Passos
1. Criar as factories de loja/membro e a fixture `two_stores`.
2. Escrever a suíte de isolamento contra endpoints reais (`/stores/...` de `P1-STORE-02`).
3. Garantir que o isolamento checa **resultado observável**, não SQL interno.

## Testes
> Fundações §10. Task meta — **fornece** fixtures e **é** a suíte de isolamento.

- **Níveis:** integração (a própria suíte) + ferramental reutilizável.
- **Quando escrever:** durante/depois de `P1-STORE-02`.
- **Cobrir:**
  - integração — A não acessa B (403/404); listagem só traz dados da própria loja; papel sem permissão é negado.

## Definition of Done
- [x] Factories/fixtures multi-tenant disponíveis (`tests/utils/store.py` + fixture `two_stores`) para as próximas fases.
- [x] `test_tenant_isolation.py` verde — A não lê/edita/publica/lista B (403), `GET /stores` só traz a própria, loja inexistente → 404 *(132 testes; cobertura 91%)*.
- [x] Smoke de permissão por papel verde (owner/admin permitidos em settings/team; `support` negado).

## Notas / Reconciliações
- **Local das factories:** `tests/utils/store.py` (junto de `user.py`/`utils.py`), não `tests/factories.py` — consistência com a estrutura de test-utils existente. Doc acima atualizado.
- **Isolamento por resultado observável:** a suíte usa os endpoints reais (`/stores/...`) e checa 403/404/ausência, nunca SQL interno (Fundações §10).
- Estas factories viram a base para os testes de catálogo/pedidos/etc. nas fases seguintes.
- **Gate estendido (resolvido nesta task):** o `scripts/lint.sh` só cobria `app` (um `F401` em teste passou batido). Passou a rodar `mypy app tests` + `ruff check/format app tests` (o `ty` segue em `app`). Limpei os 5 problemas de tipo em testes: `col()` no `join`, `cast(Any, ...)` para acesso dinâmico, type-args em `dict`, e `# type: ignore[import-untyped]` no `boto3` (sem stubs). Ver [P0-CI-01](../phase-0-foundation/P0-CI-01-ci-lint-tests.md).
