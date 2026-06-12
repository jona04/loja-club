# Fase 1 — Multi-tenancy e painel base

> Objetivo: usuário cria loja com dados isolados por `store_id`, recebe subdomínio automático, entra no painel `app.kriar.shop`, seleciona loja ativa e vê um menu controlado por permissões.

Docs de referência: [06](../concepts/06_multitenancy_and_domains.md), [08](../concepts/08_modules_and_permissions.md), [09](../concepts/09_merchant_dashboard.md), [05](../concepts/05_frontend_architecture.md), [14](../concepts/14_security_strategy.md), [16](../concepts/16_testing_strategy.md).

> **Esta fase já está decomposta em tasks** — ver [`phase-1-tenancy-and-dashboard/`](./phase-1-tenancy-and-dashboard/README.md) (13 tasks, com escopo, dependências e DoD). Este arquivo é a **visão geral (consulta)**: a trilha de alto nível.
>
> **Adaptado à realidade pós-Fase 0:** as tasks **constroem sobre** `StoreScopedMixin`/mixins (`P0-MOD-01`), módulo `accounts`/`account_users` (`P0-MOD-04`), cache Redis (`P0-CFG-03`), fila (`P0-CFG-04`) e a fundação de testes (`P0-TEST-01`) — sem recriar. Tasks **acrescentadas**: `P1-API-01` (travar o padrão de API — DEC-5), `P1-TEST-01` (fixtures multi-tenant + isolamento) e `P1-ACCT-01` (retrofit do `account_users` com soft delete + `updated_at`, alinhando INV-D2). **Decisão:** papéis/permissões ficam em **tabelas no banco** (`store_roles`/`store_permissions`/`store_role_permissions` seedados, seguindo doc [07](../concepts/07_database_strategy.md)). O esboço abaixo é mantido como referência; o detalhe e o status oficial estão no README da pasta.

## Definition of Done da fase

- Usuário cria loja → `store_stores` + `store_members` (owner) + `domain_hosts` (`{slug}.kriar.shop`).
- Resolução por `Host` retorna o `store_id` correto; host inexistente → "loja não encontrada".
- **Guard central de tenant** + **padrão de API travado** (response/erro/paginação) reusado pelos endpoints.
- Login no painel, seletor de loja ativa, menu dinâmico por permissão, tela de configurações e de equipe.
- Testes de isolamento multi-tenant e de permissões passando (fixtures multi-tenant prontas).

---

## Etapa 1 — Padrão de API (`P1-API-01`)

- [ ] Travar o padrão da **primeira API real** (Fundações §5; resolve **DEC-5**): URL/versão (`/api/v1`; painel `/stores/{store_id}/...`; storefront por `Host`), **paginação** (decidir offset vs cursor), envelope de response, formato de erro e headers de tenant. Reusar em todos os endpoints. Doc [20](../concepts/20_api_contracts_todo.md).

---

## Etapa 2 — Retrofit `account_users` (`P1-ACCT-01`)

- [ ] `account_users` (Fase 0) passa a usar `TimestampMixin` (+`updated_at`) e `SoftDeleteMixin`; remoção vira **soft delete** (template fazia hard delete). Alinha INV-D2/doc [07](../concepts/07_database_strategy.md). Leituras/auth ignoram soft-deletados.

---

## Etapa 3 — Módulo `stores`

### Modelos (`P1-STORE-01`)
- [ ] `store_stores`: `id` (UUID), `name`, `slug` (único quando ativo), `status` (`draft|active|paused|suspended|blocked|archived`), **`currency` (ISO 4217)** e **`locale`** próprios da loja (INV-G3), timestamps, soft delete. Doc [09](../concepts/09_merchant_dashboard.md) (estados da loja), [07](../concepts/07_database_strategy.md).
- [ ] `store_settings`: `store_id` (único), nome público, descrição, `logo_url`, e-mail/telefone de contato, endereço, redes sociais, `whatsapp_number`, flag publicada. Doc [09](../concepts/09_merchant_dashboard.md)/[10](../concepts/10_storefront_and_layouts.md).

### Serviço/rotas (`P1-STORE-02`)
- [ ] `slug` gerado a partir do nome + verificação de disponibilidade.
- [ ] Endpoints (`/api/v1/stores`): `POST /` criar loja, `GET /` minhas lojas, `GET /{store_id}` obter, `PATCH /{store_id}/settings`, `POST /{store_id}/publish`, `POST /{store_id}/pause`. Doc [20](../concepts/20_api_contracts_todo.md).
- [ ] Ao criar loja: criar `store_members` (role `owner`) + subdomínio em `domain_hosts` (ver módulo `domains`).
- [ ] Índices: `store_stores.slug` único; `store_settings.store_id` único. Doc [07](../concepts/07_database_strategy.md).

---

## Etapa 4 — Módulos `accounts` ↔ `stores` (membros, papéis, permissões)

### Modelos — membros/papéis (`P1-PERM-01`)
- [ ] `store_members` (`app/modules/stores/models.py`): `store_id`, `user_id` (→ `account_users`), `role` (→ `store_roles`), `status`, `invited_at`, `removed_at`, timestamps, soft delete. Índice único `store_id + user_id` quando ativo + `store_id + status`. Doc [08](../concepts/08_modules_and_permissions.md)/[07](../concepts/07_database_strategy.md).
- [ ] `store_roles`: **tabela seedada** com os papéis `owner|admin|manager|support|catalog|marketing` (global; aplicada no contexto da loja). Doc [07](../concepts/07_database_strategy.md)/[08](../concepts/08_modules_and_permissions.md).

### Permissões — catálogo + mapa em DB (`P1-PERM-02`)
- [ ] `store_permissions`: **tabela seedada** com o **catálogo completo** do doc [08](../concepts/08_modules_and_permissions.md) (dashboard, catalog.*, customization.*, orders.*, customers.*, checkout.*, payments.*, layout.*, shipping.*, discounts.*, reports.*, domains.*, team.*, billing.*, settings.*).
- [ ] `store_role_permissions`: **join seedado** que materializa o mapa **positivo** papel→permissões do doc [08](../concepts/08_modules_and_permissions.md) (adicionado ao doc [07](../concepts/07_database_strategy.md)).
- [ ] Catálogo + mapa como **constantes canônicas** em `app/modules/stores/permissions.py` (fonte do seed) + helper `role_permissions(role)`; teste "toda permissão em ≥1 papel". Permissão nova → atualizar catálogo/mapa/doc.

### Autorização (`P1-PERM-03`)
- [ ] Dependency `require_permission("catalog.product.update")` que valida: autenticado → membro da loja → papel tem a permissão → (gancho de plano para a Fase 8). Doc [08](../concepts/08_modules_and_permissions.md)/[14](../concepts/14_security_strategy.md).
- [ ] Conceito de **admin de plataforma**: mapear `account_users.is_superuser` (template) para acesso de plataforma; permissões globais (`platform.*`) ficam para a Fase 4 (admin). Anotar reconciliação.

---

## Etapa 5 — Módulo `tenancy` (`P1-TEN-01`)

- [ ] `app/modules/tenancy/deps.py`: `get_active_store(store_id)` resolve a loja do path `/stores/{store_id}` e valida membership (painel). Doc [08](../concepts/08_modules_and_permissions.md).
- [ ] `resolve_store_by_host(host)` para storefront: busca em `domain_hosts`, retorna `store_id`; usa cache `domain:{host}` no Redis. (Interface aqui; consumo público na Fase 3.) Doc [06](../concepts/06_multitenancy_and_domains.md)/[13](../concepts/13_performance_cache_and_cdn.md).
- [ ] Helper de scoping: toda query comercial recebe/filtra `store_id`. Doc [14](../concepts/14_security_strategy.md).

---

## Etapa 6 — Módulo `domains` (`P1-DOM-01`)

### Modelo (`app/modules/domains/models.py`)
- [ ] `domain_hosts`: `id`, `store_id`, `host` (único), `type` (`platform_subdomain|custom_domain`), `status` (`pending|active|failed|blocked`), `ssl_status` (`pending|issued|failed`), `verified_at`, timestamps, `deleted_at`. Doc [06](../concepts/06_multitenancy_and_domains.md)/[07](../concepts/07_database_strategy.md).

### Serviço/rotas
- [ ] Ao criar loja → inserir `host = {slug}.{DOMAIN}`, `type=platform_subdomain`, `status=active`.
- [ ] Endpoints: `GET /stores/{store_id}/domains`, `POST /stores/{store_id}/domains/check` (disponibilidade), `POST` subdomínio. Domínio próprio (`custom_domain` + verificação DNS) **fora do MVP** (doc [18](../concepts/18_open_decisions.md)).
- [ ] Cache `domain:{host}` + invalidação ao alterar domínio. Doc [06](../concepts/06_multitenancy_and_domains.md)/[13](../concepts/13_performance_cache_and_cdn.md).
- [ ] Índices: `domain_hosts.host` único; `store_id + status`. Doc [07](../concepts/07_database_strategy.md).

---

## Etapa 7 — Painel do lojista (frontend-dashboard)

> Reaproveitar o frontend do template como `frontend-dashboard`. Doc [05](../concepts/05_frontend_architecture.md)/[09](../concepts/09_merchant_dashboard.md).

### Roteamento e infra (`P1-DASH-01`)
- [ ] Traefik: renomear host `dashboard.${DOMAIN}` → `app.${DOMAIN}` (`compose.yml`). Doc [03](../concepts/03_system_architecture.md)/[05](../concepts/05_frontend_architecture.md).
- [ ] Limpar páginas/example do template não usadas: `routes/_layout/admin.tsx` (admin é projeto à parte na Fase 4); `items` já removido na Fase 0.

### Telas — login + seletor de loja (`P1-DASH-02`)
- [ ] **Login** (reaproveitar `routes/login.tsx`, `hooks/useAuth.ts`).
- [ ] **Seletor de loja ativa**: após login, listar lojas do membro; 1 loja → entra direto; várias → seletor. Loja ativa define o contexto das chamadas (`/stores/{store_id}/...`). Doc [05](../concepts/05_frontend_architecture.md)/[09](../concepts/09_merchant_dashboard.md).

### Telas — menu + telas base (`P1-DASH-03`)
- [ ] **Menu modular dinâmico por permissão**: módulo só aparece se o papel permite (e, na Fase 8, se o plano permite). Doc [05](../concepts/05_frontend_architecture.md)/[08](../concepts/08_modules_and_permissions.md).
- [ ] **Dashboard inicial** (esqueleto; métricas reais conforme dados existirem). Doc [09](../concepts/09_merchant_dashboard.md).
- [ ] **Configurações da loja** (nome, descrição, logo, contato, redes, WhatsApp, status publicada). Doc [09](../concepts/09_merchant_dashboard.md).
- [ ] **Equipe**: listar membros, convidar, alterar papel, remover. Doc [09](../concepts/09_merchant_dashboard.md)/[08](../concepts/08_modules_and_permissions.md).
- [ ] Regenerar cliente OpenAPI após novos endpoints.

---

## Testes (`P1-TEST-01`, doc [16](../concepts/16_testing_strategy.md))

- [ ] **Fixtures/factories multi-tenant**: duas lojas (A/B) com membros/papéis + headers de auth, reutilizáveis pelas próximas fases (Fundações §10).
- [ ] **Isolamento multi-tenant**: usuário da Loja A não acessa dados da Loja B; recurso só é achado com `store_id` correto.
- [ ] **Resolução de host**: host correto → loja certa; host inexistente/inativo → "loja não encontrada", sem vazar dado interno.
- [ ] **Permissões**: owner acessa tudo; support não altera layout; catalog não vê pagamento; sem permissão → bloqueio no backend (não só no front).
- [ ] **Criação de loja**: gera membership owner + subdomínio.

---

## Reconciliações (registrar aqui)

- `account_users.is_superuser` (template) ↔ admin de plataforma (doc [08](../concepts/08_modules_and_permissions.md)): no MVP o superuser cobre o acesso interno; o modelo de `platform_admin_roles`/`platform.*` entra na Fase 4. Anotado.
- (demais divergências conforme surgirem)
