---
id: P1-PERM-02
title: store_permissions + mapa papel→permissões (tabelas + seed)
phase: 1
etapa: "Etapa 3 — Multi-tenancy (backend)"
area: PERM
status: done
depends_on: [P1-PERM-01]
blocks: [P1-PERM-03, P1-DASH-03]
tests: [integration, unit]
---

# P1-PERM-02 — `store_permissions` + mapa papel→permissões (tabelas + seed)

## Contexto
O painel é dividido em módulos com **permissões granulares**; as regras são **positivas** (o que não está no papel é negado). O doc [08](../../08_modules_and_permissions.md) traz o catálogo e o mapa; o doc [07](../../07_database_strategy.md) lista `store_permissions` como **tabela**. Esta task cria o catálogo e o mapa **no banco** (seedados), sem inventar permissões.

## Docs de referência
- [08 — Modules and Permissions](../../08_modules_and_permissions.md) (catálogo + mapa por papel — **espelhar exatamente**)
- [07 — Database Strategy](../../07_database_strategy.md) (`store_permissions` como tabela)
- [09 — Merchant Dashboard](../../09_merchant_dashboard.md) (módulo ↔ permissão base)

## Escopo (o que ENTRA)
- `store_permissions` (`__tablename__="store_permissions"`): tabela **seedada** com o **catálogo completo** do doc [08](../../08_modules_and_permissions.md) (`key`, `module`, `description`): `dashboard.*`, `catalog.*`, `customization.*`, `orders.*`, `customers.*`, `checkout.*`, `payments.*`, `layout.*`, `shipping.*`, `discounts.*`, `reports.*`, `domains.*`, `team.*`, `billing.*`, `settings.*`.
- `store_role_permissions` (`__tablename__="store_role_permissions"`): join **seedado** (`role` → `permission`) que materializa o **mapa positivo** do doc [08](../../08_modules_and_permissions.md) para `owner|admin|manager|support|catalog|marketing`.
- **Fonte de seed em código** (`app/modules/stores/permissions.py`): o catálogo e o mapa do doc [08](../../08_modules_and_permissions.md) ficam como **constantes canônicas** que o `init_db` usa para popular as tabelas (single source do seed, idempotente — ver Notas) + helper `role_permissions(role)`.

## Fora de escopo (o que NÃO entra)
- Enforcement na rota (`require_permission`) → `P1-PERM-03`.
- Permissões globais da plataforma (`platform.*`) e papéis globais → Fase 6.
- Camada de **plano** (plano permite o recurso) → Fase 5 (gancho em `P1-PERM-03`).
- Overrides por membro (`store_member_permissions`, opcional no doc [07](../../07_database_strategy.md)) → fora do MVP.

## Arquivos a criar/alterar
- `backend/app/modules/stores/models.py` (alterar) — `StorePermission`, `StoreRolePermission`.
- `backend/app/modules/stores/permissions.py` (criar) — constantes canônicas (catálogo + mapa) e `role_permissions()`.
- `backend/app/modules/stores/repositories.py` (alterar) — `seed_store_permissions` (idempotente).
- `backend/app/core/db.py` (alterar) — `init_db` chama `seed_store_permissions`.
- `backend/app/alembic/versions/8d0ba011eeec_create_store_permissions.py` (criar) — só as tabelas.
- `docs/07_database_strategy.md` (alterar) — adicionar `store_role_permissions` à lista de tabelas/índices (join não estava explícito).

## Passos
1. Transcrever o catálogo e o mapa do doc [08](../../08_modules_and_permissions.md) para `permissions.py` (sem adicionar/remover).
2. Modelar `store_permissions` + `store_role_permissions`.
3. Migration cria as tabelas; o **seed** (catálogo + mapa) roda no `init_db` a partir das constantes canônicas.
4. Helper `role_permissions(role)` para consultar o mapa.
5. Atualizar o doc 07 com o join; escrever testes.

## Testes
> Fundações §10. Lógica do mapa = unit; integridade do seed no banco = integração.

- **Níveis:** unit (constantes do mapa) + integração (seed no DB).
- **Quando escrever:** antes (o doc define o contrato exato).
- **Cobrir:**
  - unit — **toda permissão do catálogo aparece em ≥1 papel**; `owner` contém todas; conjuntos de `admin/manager/support/catalog/marketing` batem com o doc [08](../../08_modules_and_permissions.md).
  - integração — após a migration, `store_permissions` tem o catálogo completo e `store_role_permissions` reflete o mapa; `role_permissions("support")` retorna exatamente o conjunto do doc.

## Definition of Done
- [x] `store_permissions` (63) e `store_role_permissions` criadas via migration `8d0ba011eeec` e **seedadas** por `init_db` (idênticas ao doc [08](../../08_modules_and_permissions.md)).
- [x] Unit (catálogo/mapa, com counts por papel) + integração (integridade do seed) verdes *(96 testes; cobertura 91%)*.
- [x] Doc [07](../../07_database_strategy.md) atualizado com `store_role_permissions`; regra registrada: **permissão nova → atualizar catálogo + mapa + doc**.

## Notas / Reconciliações
- **Seed via `init_db`, não na migration:** mesma reconciliação da `P1-PERM-01` — os testes usam `create_all` (sem migrations), então o seed roda no `init_db` (idempotente) a partir das constantes de `permissions.py`. A migration só cria as tabelas. `module` é derivado do prefixo da `key`; `description` fica nulo (o doc 08 não dá descrições).
- Unit usa os **counts por papel** do doc 08 (owner 63 / admin 54 / manager 28 / support 10 / catalog 15 / marketing 14) como guarda contra erro de transcrição.
- `store_permissions`/`store_role_permissions` são **globais/seed** (catálogo do produto, igual para toda loja), aplicados no contexto da loja via `store_members.role`. Mesma interpretação de `store_roles` (`P1-PERM-01`).
- O **join `store_role_permissions`** não estava explícito no doc [07](../../07_database_strategy.md) (que listava só `store_roles` e `store_permissions`); adicionado por ser a forma normalizada do "papel recebe uma lista explícita de permissões" (doc [08](../../08_modules_and_permissions.md)).
