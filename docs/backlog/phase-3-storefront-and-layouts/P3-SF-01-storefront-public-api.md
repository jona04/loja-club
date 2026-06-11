---
id: P3-SF-01
title: Módulo storefront — API pública de leitura
phase: 3
etapa: "Etapa 2 — Módulo storefront (API pública)"
area: SF
status: done
depends_on: [P3-CONTENT-01]
blocks: [P3-SF-02]
tests: [integration]
---

# P3-SF-01 — API pública do storefront

## Contexto
Endpoints **públicos, sem login**, com a loja resolvida pelo `Host` — leitura otimizada e cacheada para a vitrine. Só serve loja **publicada/`active`**.

## Docs de referência
- [10 — Storefront & Layouts](../../concepts/10_storefront_and_layouts.md)
- [13 — Performance, Cache & CDN](../../concepts/13_performance_cache_and_cdn.md)
- [06 — Multitenancy & Domains](../../concepts/06_multitenancy_and_domains.md)
- [20 — API Contracts](../../concepts/20_api_contracts_todo.md)

## Escopo (o que ENTRA)
- **Resolução + publicação:** reusar `resolve_store_by_host` (`P1-TEN-01`); servir **apenas loja com `status == active`** (qualquer outro status → "loja não encontrada", sem vazar).
- **Endpoints públicos:** `GET` home (config + destaques + tema ativo), categorias, produtos públicos (**paginado**), produto por `slug`, página pública. **Só produtos `published`** (draft/archived/deletados não aparecem na vitrine).
- **Cache de leitura** (doc 13): `store:{id}:settings|theme|home|categories|product:{slug}|menu`.
- Consultas públicas separadas das administrativas; evitar joins pesados na vitrine.

## Fora de escopo (o que NÃO entra)
- Render no Next.js → `P3-SF-02`.
- Rotas do **painel** (aplicar template) → `P3-CONTENT-02`.
- Carrinho/checkout → Fase 6.

## Arquivos a criar/alterar
- `app/modules/storefront/{routes,services,schemas}.py` (criar).
- `app/api/router.py` (alterar) — rotas públicas (sem auth de painel).

## Passos
1. Dependency pública: resolve a loja pelo `Host` **e** exige publicada; senão 404 "não encontrada".
2. Endpoints de leitura consumindo `catalog` (Fase 2) + `content` (tema); DTOs públicos enxutos.
3. Cache-aside nas chaves do doc 13 (TTL + invalidação combinada com `P3-CONTENT-02`).

## Testes
> Regra em [`_foundations-and-bottlenecks.md`](../_foundations-and-bottlenecks.md) §10.

- **Níveis:** integração.
- **Cobrir:** host inexistente → 404; loja `draft` → 404 (sem vazar); home/produto/categoria de loja `active` retornam; isolamento por loja; cache hit/miss.

## Definition of Done
- [x] Loja não publicada/host inexistente → **404 `store_not_found`** (mesma resposta, sem vazar; testado).
- [x] Home/categorias/produtos(paginado)/produto-por-slug retornam para loja `active`, com **cache-aside**.
- [x] **Modos de falha mapeados** (slug inexistente → 404; loja pausada → status checado **live**, não cacheado; cache stale → Follow-up) → tratados/Follow-up.
- [x] Itens adiados varridos → Follow-ups + README.

## Notas / Reconciliações
- `resolve_store_by_host` **já existe** (`P1-TEN-01`, cache `domain:{host}`); esta task adiciona o **filtro de publicação** (`status == active`, checado **live** por request — pausar a loja reflete na hora) + as chaves de leitura. Host lido do header (porta removida).
- **Endpoints** (`/storefront`, sem auth, resolvidos por Host): `home`, `categories`, `products` (paginado), `products/{slug}`, `pages/{slug}`.
- **Cache-aside** (TTL 5 min): `store:{id}:home|categories|product:{slug}`. O `home` agrega store+theme+destaques (dobra `settings`+`theme`); produtos paginados e páginas **não** são cacheados.
- **Theme read-only:** loja sem row → default `classic` (sem criar) — atende ao fallback da `P3-CONTENT-01`.
- **Destaques** = produtos `is_featured` published (não há link produto↔coleção no `catalog`, então o `featured_collection_id` do theme ainda não é usado).
- Queries públicas **separadas** das admin (published + não-deletado + `store_id`). Stub `enums.py` removido (storefront é só leitura).

## Follow-ups
- [ ] **Cache stale após edição de catálogo** (`P3-SF-01`): escritas do `catalog` (produto/categoria) **não** invalidam `store:{id}:categories|product:{slug}|home` — só o TTL (5 min) resolve. Adicionar invalidação no `catalog` (hook/sinal) quando a vitrine for pra produção.
- [ ] **N+1 de imagens** (`P3-SF-01`): `list_products`/home chamam `list_images` por produto. Otimizar com query em lote para listas grandes.
- [ ] **Destaque por coleção** (`P3-SF-01`): ligar `featured_collection_id` quando existir o link produto↔coleção no `catalog` (hoje destaque = `is_featured`).
- [ ] **Menu + caches `settings`/`theme` separados** (`P3-SF-01`): a home dobra settings+theme; o menu não é servido (sem CRUD) e as chaves `store:{id}:settings|theme|menu` ficam reservadas — servir o menu quando o CRUD existir.
