# Fase 1 — Multi-tenancy e painel base

> Roadmap: Etapas 3–4. Objetivo: usuário cria loja com dados isolados por `store_id`, recebe subdomínio automático, entra no painel `app.loja.club`, seleciona loja ativa e vê um menu controlado por permissões.

Docs de referência: [Fundações & Gargalos](../_foundations-and-bottlenecks.md), [06](../../06_multitenancy_and_domains.md), [08](../../08_modules_and_permissions.md), [09](../../09_merchant_dashboard.md), [05](../../05_frontend_architecture.md), [07](../../07_database_strategy.md), [14](../../14_security_strategy.md), [16](../../16_testing_strategy.md), [20](../../20_api_contracts_todo.md).

> Visão geral / trilha de alto nível: [`../phase-1-tenancy-and-dashboard.md`](../phase-1-tenancy-and-dashboard.md). Este README é o **índice detalhado** das tasks.

## Definition of Done da fase

- Usuário cria loja → `store_stores` + `store_members` (owner) + `domain_hosts` (`{slug}.loja.club`).
- Resolução por `Host` retorna o `store_id` correto; host inexistente/inativo → "loja não encontrada", sem vazar dado interno.
- **Guard central de tenant**: nenhum recurso comercial é buscado só por id (sempre `store_id + id`); autorização sempre no backend.
- **Padrão de API travado** (response/erro/paginação/headers de tenant) e reusado pelos endpoints.
- Login no painel, seletor de loja ativa, menu dinâmico por permissão, tela de configurações e de equipe.
- Testes de isolamento multi-tenant e de permissões passando (fixtures multi-tenant prontas).

## Construído sobre a Fase 0 (não recriar)

- `StoreScopedMixin`/`UUIDMixin`/`TimestampMixin`/`SoftDeleteMixin` (`app/db/base.py`, `P0-MOD-01`).
- Módulo `accounts` + `account_users` (`P0-MOD-04`); `store_members.user_id` referencia `account_users.id`. **`P1-ACCT-01` retrofita `account_users`** com soft delete + `updated_at` (alinha INV-D2) antes do membership.
- Cache Redis (`app/core/cache.py`, `P0-CFG-03`) — usado na resolução por `Host`.
- Fila `arq` (`P0-CFG-04`) e fundação de testes (`tests/unit`+`tests/integration`, rollback; `P0-TEST-01`).
- `Money`/`currency`/`locale` globais (`P0-MOD-05`) — a loja carrega `currency`/`locale` próprios.

## Tasks

| # | ID | Task | Status | Depende de |
|---|---|---|---|---|
| 1 | [P1-API-01](./P1-API-01-api-conventions.md) | Padrão de API (response/erro/paginação/tenant) | done | — |
| 2 | [P1-ACCT-01](./P1-ACCT-01-accounts-soft-delete.md) | Retrofit `account_users` (soft delete + `updated_at`) | done | — |
| 3 | [P1-STORE-01](./P1-STORE-01-store-models.md) | Módulo `stores`: `store_stores` + `store_settings` | done | — |
| 4 | [P1-PERM-01](./P1-PERM-01-members-roles.md) | `store_members` + `store_roles` (tabela + seed) | done | P1-ACCT-01, P1-STORE-01 |
| 5 | [P1-PERM-02](./P1-PERM-02-permission-catalog.md) | `store_permissions` + mapa papel→permissões (tabelas + seed) | done | P1-PERM-01 |
| 6 | [P1-DOM-01](./P1-DOM-01-domains.md) | Módulo `domains`: `domain_hosts` + subdomínio + cache | done | P1-STORE-01 |
| 7 | [P1-TEN-01](./P1-TEN-01-tenancy-guard.md) | Módulo `tenancy`: guard central + resolução por `Host` | todo | P1-STORE-01, P1-PERM-01, P1-DOM-01 |
| 8 | [P1-PERM-03](./P1-PERM-03-require-permission.md) | Autorização: `require_permission` (deps) | todo | P1-PERM-02, P1-TEN-01 |
| 9 | [P1-STORE-02](./P1-STORE-02-store-service-routes.md) | `stores`: serviço/rotas (criar→owner+subdomínio, settings, publish) | todo | P1-API-01, P1-STORE-01, P1-PERM-01, P1-DOM-01, P1-PERM-03 |
| 10 | [P1-TEST-01](./P1-TEST-01-tenant-fixtures-isolation.md) | Fixtures/factories multi-tenant + testes de isolamento | todo | P1-STORE-01, P1-PERM-01 |
| 11 | [P1-DASH-01](./P1-DASH-01-dashboard-infra.md) | Infra do painel (`frontend-dashboard`, Traefik `app.`) | todo | — |
| 12 | [P1-DASH-02](./P1-DASH-02-login-store-selector.md) | Login + seletor de loja ativa + contexto | todo | P1-STORE-02, P1-DASH-01 |
| 13 | [P1-DASH-03](./P1-DASH-03-menu-and-screens.md) | Menu dinâmico por permissão + telas (dashboard, settings, equipe) | todo | P1-DASH-02, P1-PERM-03, P1-STORE-02 |

## Ordem sugerida de execução

```text
P1-API-01 → P1-ACCT-01 → P1-STORE-01 → P1-PERM-01 → P1-PERM-02 → P1-DOM-01
→ P1-TEN-01 → P1-PERM-03 → P1-STORE-02 → P1-TEST-01 → P1-DASH-01 → P1-DASH-02 → P1-DASH-03
```

## Reconciliações da fase (registrar conforme surgirem)

- `account_users.is_superuser` (template) ↔ admin de plataforma (doc [08](../../08_modules_and_permissions.md)): no MVP o superuser cobre o acesso interno; `platform_admin_roles`/`platform.*` entram na Fase 6. (Herdado de `P0-MOD-04`.)
- **DEC-5 (paginação)** estava pendente nas Fundações; é **travada em `P1-API-01`** (a 1ª API real) e reusada — atualizar o status na tabela de decisões e o doc [20](../../20_api_contracts_todo.md).
- **Domínio próprio** (`custom_domain` + verificação DNS) fica **fora do MVP** (doc [18](../../18_open_decisions.md)); a Fase 1 entrega só `platform_subdomain`.
- **Gating por plano** (doc [08](../../08_modules_and_permissions.md) "plano + permissão") entra na Fase 5; aqui deixamos só o **gancho** em `require_permission`.
- **Papéis/permissões em banco (decidido):** `store_roles`, `store_permissions` e o join `store_role_permissions` são **tabelas seedadas** (segue doc [07](../../07_database_strategy.md)), com o catálogo/mapa do doc [08](../../08_modules_and_permissions.md) como fonte de seed em código. São **globais** (não por-loja); aplicam-se no contexto da loja via `store_members`. O join foi **adicionado ao doc [07](../../07_database_strategy.md)**.
- **Retrofit `account_users` (`P1-ACCT-01`):** o template fazia hard delete e não tinha `updated_at`/soft delete — corrigido para honrar INV-D2/doc [07](../../07_database_strategy.md).

## Follow-ups / débitos técnicos

> Itens **adiados** ("fica para depois") ficam aqui como checkboxes — não só em prosa nas notas das tasks. **Convenção:** toda nota de task que diga "fica para depois" também entra nesta lista (ou vira uma task, se for grande); marcar `[x]` quando resolvido, citando a origem.

- [ ] **OpenAPI — tipar o schema de erro por endpoint** (`responses=` com `ErrorResponse`) para o client gerado carregar o tipo do erro. Origem: `P1-API-01`. *Quando:* se/quando o frontend precisar do tipo (hoje lê `err.body` de forma defensiva).
- [ ] **Rotas do painel de domínios** (`GET /stores/{store_id}/domains`, `POST /check`) — dependem de `P1-TEN-01` + `P1-PERM-03`. Origem: `P1-DOM-01`. *Quando:* após essas duas.
- [ ] **Guard de soft-delete em leituras por id de admin** (`read_user_by_id`/`update_user` via `session.get`, que ainda retornam soft-deletados). Origem: `P1-ACCT-01`. *Quando:* se virar problema, ou junto do admin de plataforma (Fase 6).
- [x] **Limpeza do ruído de `alembic autogenerate`** — `_MixinProbe` isolado em `MetaData()` próprio + índice `ix_user_email`→`ix_account_users_email` (migration `c2d3e4f5a6b7`); autogenerate volta a vir vazio. Origem: `P1-STORE-01`. *(feito)*
