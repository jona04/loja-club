---
id: P1-TEST-01
title: Fixtures/factories multi-tenant + testes de isolamento
phase: 1
etapa: "Etapa 3 — Multi-tenancy (backend)"
area: TEST
status: todo
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
- `backend/tests/integration/conftest.py` (alterar) — fixtures multi-tenant.
- `backend/tests/factories.py` (criar) — factories de store/member (ou em `tests/utils/`).
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
- [ ] Factories/fixtures multi-tenant disponíveis para as próximas fases.
- [ ] `test_tenant_isolation.py` verde, cobrindo "A não vê B" no resultado observável.
- [ ] Smoke de permissão por papel verde.

## Notas / Reconciliações
- Estas factories viram a base para os testes de catálogo/pedidos/etc. nas fases seguintes.
