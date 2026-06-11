---
id: P1-DOM-01
title: Módulo domains — domain_hosts + subdomínio automático + cache
phase: 1
etapa: "Etapa 6 — Módulo domains"
area: DOM
status: done
depends_on: [P1-STORE-01]
blocks: [P1-TEN-01, P1-STORE-02]
tests: [integration]
---

# P1-DOM-01 — Módulo `domains`: `domain_hosts` + subdomínio automático + cache

## Contexto
Toda loja recebe um **subdomínio automático** (`{slug}.loja.club`) e é resolvida pelo `Host` (doc [06](../../06_multitenancy_and_domains.md)). Esta task cria o módulo `domains` (modelo + serviço + rotas + cache). A resolução por `Host` em si fica no `tenancy` (`P1-TEN-01`), que consome este módulo.

## Docs de referência
- [06 — Multitenancy and Domains](../../06_multitenancy_and_domains.md) (tabela `domain_hosts`, subdomínio, cache, wildcard)
- [07 — Database Strategy](../../07_database_strategy.md)
- [13 — Performance, Cache and CDN](../../13_performance_cache_and_cdn.md) (chave `domain:{host}`)
- [18 — Open Decisions](../../18_open_decisions.md) (domínio próprio fora do MVP)

## Escopo (o que ENTRA)
- `domain_hosts` (`__tablename__="domain_hosts"`): `id`, `store_id`, `host` (**único**), `type` (`platform_subdomain|custom_domain`), `status` (`pending|active|failed|blocked`), `ssl_status` (`pending|issued|failed`), `verified_at`, timestamps, soft delete. Doc [06](../../06_multitenancy_and_domains.md).
- Serviço: `create_platform_subdomain(store_id, slug)` → insere `host={slug}.{DOMAIN}`, `type=platform_subdomain`, `status=active` (chamado por `P1-STORE-02`); `check_availability(slug/host)`.
- Rotas (painel, `/api/v1/stores/{store_id}/domains`): `GET` listar; `POST /check` disponibilidade. (Domínio próprio: só placeholder.)
- **Cache** `domain:{host}` (chave canônica) com **invalidação** ao alterar/arquivar domínio. Reusa `app/core/cache.py` (`P0-CFG-03`).
- Índices: `domain_hosts.host` único; `store_id + status`.

## Fora de escopo (o que NÃO entra)
- `resolve_store_by_host(host)` (a leitura por `Host`) → `P1-TEN-01`.
- **Domínio próprio** (`custom_domain` + verificação DNS + SSL) → fora do MVP (doc [18](../../18_open_decisions.md)); deixar só o campo/placeholder.
- Consumo público no storefront → Fase 3.

## Arquivos a criar/alterar
- `backend/app/modules/domains/models.py` (criar) — `DomainHost` + schemas.
- `backend/app/modules/domains/services.py` (criar) — `create_platform_subdomain`, `check_availability`, invalidação de cache.
- `backend/app/modules/domains/routes.py` (criar) — listar/checar.
- `backend/app/alembic/versions/xxxx_create_domain_hosts.py` (criar); `models_registry` (alterar).

## Passos
1. Modelar `DomainHost` com os enums de `type`/`status`/`ssl_status`.
2. Serviço de criação de subdomínio (usa `settings.DOMAIN`) + disponibilidade.
3. Cache `domain:{host}` + invalidação ao alterar.
4. Rotas de listagem/checagem (gated por `domains.view` quando `P1-PERM-03` existir).
5. Migration + índices; aplicar em db do zero.

## Testes
> Fundações §10.

- **Níveis:** integração (unicidade de host, criação de subdomínio, cache são fronteiras reais).
- **Quando escrever:** durante.
- **Cobrir:**
  - integração — `create_platform_subdomain` gera `{slug}.{DOMAIN}` ativo; `host` é único; `check_availability` retorna falso p/ slug em uso; invalidação remove `domain:{host}` do Redis.

## Definition of Done
- [x] `domain_hosts` criada via migration `c505b47136b7` (db do zero); `host` **único quando ativo** (índice parcial).
- [x] `create_platform_subdomain` insere subdomínio ativo (`{slug}.{DOMAIN}`, `status=active`, `ssl_status=issued`) — teste.
- [x] Cache `domain:{host}` invalidado ao criar/alterar (teste) *(100 testes; cobertura 92%)*.

## Notas / Reconciliações
- **Rotas deferidas (ver Follow-ups):** as rotas do painel (`GET /stores/{store_id}/domains`, `POST /check`) precisam de `get_active_store` (`P1-TEN-01`) + `require_permission("domains.view")` (`P1-PERM-03`), ainda não implementados. O DoD (model + serviço + cache) não as inclui. Entregue agora: `enums.py` (`DomainType`/`DomainStatus`/`SslStatus`), `models.py` (`DomainHost`), `services.py` (`create_platform_subdomain`/`is_subdomain_available`/`invalidate_domain_cache`).
- **`host` único quando ativo (parcial):** mudei de "único cheio" (doc 07/escopo) para parcial `WHERE deleted_at IS NULL`, espelhando o `slug` de `store_stores` (loja arquivada libera o subdomínio). Doc 07 atualizado.
- **Cache:** DOM-01 entrega a **invalidação** (`cache_delete` em `app/core/cache.py`); a **população** (cache-aside na resolução por `Host`) é da `P1-TEN-01`.
- **`ssl_status=issued`** para `platform_subdomain` (coberto pelo wildcard `*.{DOMAIN}`); `verified_at` fica nulo. Doc [06](../../06_multitenancy_and_domains.md): V1 **sem domínio principal** — qualquer host ativo renderiza a mesma loja.

## Follow-ups
- [ ] **Rotas do painel de domínios** (`GET /stores/{store_id}/domains` listar; `POST /check` disponibilidade) — dependem de `P1-TEN-01` (`get_active_store`) + `P1-PERM-03` (`require_permission`). *Quando:* depois dessas duas. → README da fase.
