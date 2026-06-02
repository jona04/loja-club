# Fase 1 — Multi-tenancy e painel base

> Roadmap: Etapas 3–4. Objetivo: usuário cria loja com dados isolados por `store_id`, recebe subdomínio automático, entra no painel `app.loja.club`, seleciona loja ativa e vê um menu controlado por permissões.

Docs de referência: [06](../06_multitenancy_and_domains.md), [08](../08_modules_and_permissions.md), [09](../09_merchant_dashboard.md), [05](../05_frontend_architecture.md), [14](../14_security_strategy.md), [16](../16_testing_strategy.md).

## Definition of Done da fase

- Usuário cria loja → `store_stores` + `store_members` (owner) + `domain_hosts` (`{slug}.loja.club`).
- Resolução por `Host` retorna o `store_id` correto; host inexistente → "loja não encontrada".
- Login no painel, seletor de loja ativa, menu dinâmico por permissão, tela de configurações e de equipe.
- Testes de isolamento multi-tenant e de permissões passando.

---

## Etapa 3 — Módulo `stores`

### Modelos (`app/modules/stores/models.py`)
- [ ] `store_stores`: `id` (UUID), `name`, `slug` (único quando ativo), `status` (`draft|active|paused|suspended|blocked|archived`), timestamps, soft delete. Doc [09](../09_merchant_dashboard.md) (estados da loja), [07](../07_database_strategy.md).
- [ ] `store_settings`: `store_id` (único), nome público, descrição, `logo_url`, e-mail/telefone de contato, endereço, redes sociais, `whatsapp_number`, flag publicada. Doc [09](../09_merchant_dashboard.md)/[10](../10_storefront_and_layouts.md).

### Serviço/rotas
- [ ] `slug` gerado a partir do nome + verificação de disponibilidade.
- [ ] Endpoints (`/api/v1/stores`): `POST /` criar loja, `GET /` minhas lojas, `GET /{store_id}` obter, `PATCH /{store_id}/settings`, `POST /{store_id}/publish`, `POST /{store_id}/pause`. Doc [20](../20_api_contracts_todo.md).
- [ ] Ao criar loja: criar `store_members` (role `owner`) + subdomínio em `domain_hosts` (ver módulo `domains`).
- [ ] Índices: `store_stores.slug` único; `store_settings.store_id` único. Doc [07](../07_database_strategy.md).

---

## Etapa 3 — Módulos `accounts` ↔ `stores` (membros, papéis, permissões)

### Modelos
- [ ] `store_members` (`app/modules/stores/models.py`): `store_id`, `user_id`, `role`, `status`, `invited_at`, `removed_at`. Índice único `store_id + user_id` quando ativo. Doc [08](../08_modules_and_permissions.md)/[07](../07_database_strategy.md).
- [ ] `store_roles`: papéis `owner|admin|manager|support|catalog|marketing`. Doc [08](../08_modules_and_permissions.md).
- [ ] `store_permissions`: catálogo de permissões. `store_member_permissions` (override por membro) — opcional, criar só se necessário.

### Permissões (`app/modules/<mod>/permissions.py` + mapa central)
- [ ] Implementar o **catálogo completo de permissões** do doc [08](../08_modules_and_permissions.md) (dashboard, catalog.*, customization.*, orders.*, customers.*, checkout.*, payments.*, layout.*, shipping.*, discounts.*, reports.*, domains.*, team.*, billing.*, settings.*).
- [ ] Mapa **papel → permissões** (positivo: o que não está listado é negado) conforme doc [08](../08_modules_and_permissions.md). Quando criar permissão nova, atualizar o mapa.
- [ ] Manter o mapa em um único lugar (ex.: `app/modules/stores/permissions.py`) com teste que garante "toda permissão existe em ≥1 papel".

### Autorização (`app/api/deps.py` + tenancy)
- [ ] Dependency `require_permission("catalog.product.update")` que valida: autenticado → membro da loja → papel tem a permissão → (gancho de plano para a Fase 5). Doc [08](../08_modules_and_permissions.md)/[14](../14_security_strategy.md).
- [ ] Conceito de **admin de plataforma**: mapear `account_users.is_superuser` (template) para acesso de plataforma; permissões globais (`platform.*`) ficam para a Fase 6 (admin). Anotar reconciliação.

---

## Etapa 3 — Módulo `tenancy`

- [ ] `app/modules/tenancy/deps.py`: `get_active_store(store_id)` resolve a loja do path `/stores/{store_id}` e valida membership (painel). Doc [08](../08_modules_and_permissions.md).
- [ ] `resolve_store_by_host(host)` para storefront: busca em `domain_hosts`, retorna `store_id`; usa cache `domain:{host}` no Redis. (Interface aqui; consumo público na Fase 3.) Doc [06](../06_multitenancy_and_domains.md)/[13](../13_performance_cache_and_cdn.md).
- [ ] Helper de scoping: toda query comercial recebe/filtra `store_id`. Doc [14](../14_security_strategy.md).

---

## Etapa 3 — Módulo `domains`

### Modelo (`app/modules/domains/models.py`)
- [ ] `domain_hosts`: `id`, `store_id`, `host` (único), `type` (`platform_subdomain|custom_domain`), `status` (`pending|active|failed|blocked`), `ssl_status` (`pending|issued|failed`), `verified_at`, timestamps, `deleted_at`. Doc [06](../06_multitenancy_and_domains.md)/[07](../07_database_strategy.md).

### Serviço/rotas
- [ ] Ao criar loja → inserir `host = {slug}.{DOMAIN}`, `type=platform_subdomain`, `status=active`.
- [ ] Endpoints: `GET /stores/{store_id}/domains`, `POST /stores/{store_id}/domains/check` (disponibilidade), `POST` subdomínio. Domínio próprio (`custom_domain` + verificação DNS) **fora do MVP** (doc [18](../18_open_decisions.md)).
- [ ] Cache `domain:{host}` + invalidação ao alterar domínio. Doc [06](../06_multitenancy_and_domains.md)/[13](../13_performance_cache_and_cdn.md).
- [ ] Índices: `domain_hosts.host` único; `store_id + status`. Doc [07](../07_database_strategy.md).

---

## Etapa 4 — Painel do lojista (frontend-dashboard)

> Reaproveitar o frontend do template como `frontend-dashboard`. Doc [05](../05_frontend_architecture.md)/[09](../09_merchant_dashboard.md).

### Roteamento e infra
- [ ] Traefik: renomear host `dashboard.${DOMAIN}` → `app.${DOMAIN}` (`compose.yml`). Doc [03](../03_system_architecture.md)/[05](../05_frontend_architecture.md).
- [ ] Limpar páginas/example do template não usadas: `routes/_layout/admin.tsx` (admin é projeto à parte na Fase 6), `routes/_layout/items.tsx` (removido na Fase 0).

### Telas
- [ ] **Login** (reaproveitar `routes/login.tsx`, `hooks/useAuth.ts`).
- [ ] **Seletor de loja ativa**: após login, listar lojas do membro; 1 loja → entra direto; várias → seletor. Loja ativa define o contexto das chamadas (`/stores/{store_id}/...`). Doc [05](../05_frontend_architecture.md)/[09](../09_merchant_dashboard.md).
- [ ] **Menu modular dinâmico por permissão**: módulo só aparece se o papel permite (e, na Fase 5, se o plano permite). Doc [05](../05_frontend_architecture.md)/[08](../08_modules_and_permissions.md).
- [ ] **Dashboard inicial** (esqueleto; métricas reais conforme dados existirem). Doc [09](../09_merchant_dashboard.md).
- [ ] **Configurações da loja** (nome, descrição, logo, contato, redes, WhatsApp, status publicada). Doc [09](../09_merchant_dashboard.md).
- [ ] **Equipe**: listar membros, convidar, alterar papel, remover. Doc [09](../09_merchant_dashboard.md)/[08](../08_modules_and_permissions.md).
- [ ] Regenerar cliente OpenAPI após novos endpoints.

---

## Etapa 3/4 — Testes (doc [16](../16_testing_strategy.md))

- [ ] **Isolamento multi-tenant**: usuário da Loja A não acessa dados da Loja B; recurso só é achado com `store_id` correto.
- [ ] **Resolução de host**: host correto → loja certa; host inexistente/inativo → "loja não encontrada", sem vazar dado interno.
- [ ] **Permissões**: owner acessa tudo; support não altera layout; catalog não vê pagamento; sem permissão → bloqueio no backend (não só no front).
- [ ] **Criação de loja**: gera membership owner + subdomínio.

---

## Reconciliações (registrar aqui)

- `account_users.is_superuser` (template) ↔ admin de plataforma (doc [08](../08_modules_and_permissions.md)): no MVP o superuser cobre o acesso interno; o modelo de `platform_admin_roles`/`platform.*` entra na Fase 6. Anotado.
- (demais divergências conforme surgirem)
