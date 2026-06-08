---
id: P3-SF-01
title: Módulo storefront — API pública de leitura
phase: 3
etapa: "Etapa 7 — Módulo storefront (API pública)"
area: SF
status: todo
depends_on: [P3-CONTENT-01]
blocks: [P3-SF-02]
tests: [integration]
---

# P3-SF-01 — API pública do storefront

## Contexto
Endpoints **públicos, sem login**, com a loja resolvida pelo `Host` — leitura otimizada e cacheada para a vitrine. Só serve loja **publicada/`active`**.

## Docs de referência
- [10 — Storefront & Layouts](../../10_storefront_and_layouts.md)
- [13 — Performance, Cache & CDN](../../13_performance_cache_and_cdn.md)
- [06 — Multitenancy & Domains](../../06_multitenancy_and_domains.md)
- [20 — API Contracts](../../20_api_contracts_todo.md)

## Escopo (o que ENTRA)
- **Resolução + publicação:** reusar `resolve_store_by_host` (`P1-TEN-01`); servir **apenas loja com `status == active`** (qualquer outro status → "loja não encontrada", sem vazar).
- **Endpoints públicos:** `GET` home (config + destaques + tema ativo), categorias, produtos públicos (**paginado**), produto por `slug`, página pública. **Só produtos `published`** (draft/archived/deletados ficam fora — novo ciclo de vida do produto).
- **Cache de leitura** (doc 13): `store:{id}:settings|theme|home|categories|product:{slug}|menu`.
- Consultas públicas separadas das administrativas; evitar joins pesados na vitrine.

## Fora de escopo (o que NÃO entra)
- Render no Next.js → `P3-SF-02`.
- Rotas do **painel** (aplicar template) → `P3-CONTENT-02`.
- Carrinho/checkout → Fase 4.

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
- [ ] Loja não publicada/host inexistente → "loja não encontrada" (sem vazar dado interno).
- [ ] Home/categorias/produtos(paginado)/produto-por-slug retornam para loja `active`, cacheados.
- [ ] **Modos de falha mapeados** (cache stale após edição, slug inexistente, loja pausada com cache quente) → tratados ou Follow-up.
- [ ] Itens adiados varridos → Follow-ups + README, ou "nenhum".

## Notas / Reconciliações
- `resolve_store_by_host` **já existe** (`P1-TEN-01`, cache `domain:{host}`); esta task só adiciona o **filtro de publicação** + as chaves de leitura.

## Follow-ups
- (preencher ao executar)
