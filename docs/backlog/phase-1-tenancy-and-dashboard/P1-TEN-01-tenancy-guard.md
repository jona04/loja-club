---
id: P1-TEN-01
title: Módulo tenancy — guard central + resolução por Host
phase: 1
etapa: "Etapa 3 — Multi-tenancy (backend)"
area: TEN
status: todo
depends_on: [P1-STORE-01, P1-PERM-01, P1-DOM-01]
blocks: [P1-PERM-03, P1-STORE-02]
tests: [integration]
---

# P1-TEN-01 — Módulo `tenancy`: guard central + resolução por `Host`

## Contexto
O isolamento entre lojas é o invariante mais crítico (INV-T1..T4; GARGALO §2). Esta task cria o **guard central de tenant** — uma só porta de entrada para "qual loja é esta e o usuário pode operá-la" — em vez de filtros `store_id` espalhados. Cobre os dois caminhos: **painel** (loja no path) e **storefront** (loja pelo `Host`).

## Docs de referência
- [06 — Multitenancy and Domains](../../06_multitenancy_and_domains.md)
- [14 — Security Strategy](../../14_security_strategy.md)
- [Fundações §2 (INV-T1..T4) + §10 (isolamento)](../_foundations-and-bottlenecks.md)
- [13 — Performance, Cache and CDN](../../13_performance_cache_and_cdn.md)

## Escopo (o que ENTRA)
- `app/modules/tenancy/deps.py`:
  - `get_active_store(store_id)` — resolve a loja do path `/stores/{store_id}` e **valida membership** do usuário autenticado (painel). Loja inexistente/sem acesso → 404/403 sem vazar dado.
  - dependency/contexto que expõe a `store` ativa para as rotas do painel.
- `app/modules/tenancy/services.py`:
  - `resolve_store_by_host(host)` — busca `domain_hosts` ativo → `store_id`; usa cache `domain:{host}` (`P1-DOM-01`); host inexistente/inativo → "loja não encontrada" (INV-T4). (Interface aqui; consumo público na Fase 3.)
- **Helper de scoping** (INV-T2/T3): base de repositório/utilitário que **sempre** recebe/filtra `store_id` (`store_id + id`/`store_id + slug`); nunca buscar recurso comercial só por id.

## Fora de escopo (o que NÃO entra)
- Checagem de **permissão** (papel tem a permissão) → `P1-PERM-03` (usa `get_active_store`).
- Páginas públicas do storefront que consomem `resolve_store_by_host` → Fase 3.

## Arquivos a criar/alterar
- `backend/app/modules/tenancy/deps.py` (criar) — `get_active_store` + dependency de loja ativa.
- `backend/app/modules/tenancy/services.py` (criar) — `resolve_store_by_host` + cache.
- `backend/app/modules/tenancy/__init__.py` — já existe (skeleton do `P0-MOD-02`).

## Passos
1. `get_active_store(store_id)`: busca a loja (não arquivada) + valida `store_members` ativo do usuário; erros sem vazamento.
2. `resolve_store_by_host(host)`: cache-aside em `domain:{host}` → `domain_hosts` ativo → `store_id`.
3. Helper de scoping (`store_id + id`) para os repositórios reusarem.
4. Testes de isolamento no resultado observável.

## Testes
> Fundações §10. Isolamento é **integração** (duas lojas no DB real), no resultado observável (403/404/ausência), nunca no SQL interno.

- **Níveis:** integração.
- **Quando escrever:** durante (caminho feliz + isolamento).
- **Cobrir:**
  - integração — membro da Loja A acessa A; **não-membro → 403**; loja inexistente → 404; `resolve_store_by_host` retorna a loja certa, host desconhecido/inativo → "não encontrada"; cache `domain:{host}` é usado na 2ª chamada.

## Definition of Done
- [ ] `get_active_store` valida loja + membership; nega não-membro sem vazar dado.
- [ ] `resolve_store_by_host` resolve por `Host` com cache; host desconhecido → "loja não encontrada".
- [ ] Helper de scoping documentado e usado pelos repositórios das próximas features.

## Notas / Reconciliações
- Registrar o desenho final do guard (dependency vs base de repositório) e como as próximas fases devem consumi-lo.
