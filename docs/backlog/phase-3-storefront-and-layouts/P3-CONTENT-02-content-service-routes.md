---
id: P3-CONTENT-02
title: content — serviço/rotas do painel (tema/layout)
phase: 3
etapa: "Etapa 8 — Módulo de conteúdo/layout"
area: CONTENT
status: todo
depends_on: [P3-CONTENT-01]
blocks: [P3-FE-02]
tests: [integration]
---

# P3-CONTENT-02 — Serviço/rotas do `content`

## Contexto
Endpoints do **painel** para o lojista escolher o template e editar a aparência; aplicar template **invalida o cache de leitura** que a vitrine (`P3-SF-01`) consome.

## Docs de referência
- [10 — Storefront & Layouts](../../10_storefront_and_layouts.md)
- [13 — Performance, Cache & CDN](../../13_performance_cache_and_cdn.md)
- [20 — API Contracts](../../20_api_contracts_todo.md)

## Escopo (o que ENTRA)
- Sob `/api/v1/stores/{store_id}/...`, gated por **`layout.*`** (ver=`layout.view`, preview=`layout.preview`, aplicar/editar=`layout.update`, assets=`layout.assets.update`): listar templates; obter template ativo; **preview**; **aplicar template** (salva `active_template_id`); editar `banner`/`headline`/`featured_collection`.
- **Invalidação:** ao aplicar/editar, invalidar `store:{id}:theme|home|settings` (chaves de leitura da `P3-SF-01`).

## Fora de escopo (o que NÃO entra)
- Endpoints **públicos** (vitrine) → `P3-SF-01`.
- CRUD de páginas/menus/banners no painel → Follow-up (modelos existem; UI/rotas depois).
- Tela do painel → `P3-FE-02`.

## Arquivos a criar/alterar
- `app/modules/content/{services,repositories,routes,permissions}.py` (criar).
- `app/api/router.py` (alterar) — incluir as rotas.

## Passos
1. Serviço store-scoped (`get_store_scoped`); aplicar template valida `template_id` ∈ templates ativos.
2. Rotas + `require_permission`; após escrita, invalidar as chaves de cache.
3. Regenerar o cliente OpenAPI.

## Testes
> Regra em [`_foundations-and-bottlenecks.md`](../_foundations-and-bottlenecks.md) §10.

- **Níveis:** integração.
- **Cobrir:** aplicar template muda `active_template_id` **e invalida** as chaves; template inválido → 4xx; gating; isolamento por loja.

## Definition of Done
- [ ] Aplicar/editar persiste + **invalida** `store:{id}:theme|home|settings`.
- [ ] Gating + isolamento por loja testados; cliente OpenAPI regenerado.
- [ ] **Modos de falha mapeados** (template inexistente, invalidação parcial, race de aplicar) → tratados ou Follow-up.
- [ ] Itens adiados varridos → Follow-ups + README, ou "nenhum".

## Notas / Reconciliações
- As chaves de cache são definidas junto com a `P3-SF-01` (quem as lê); manter os nomes em sincronia.

## Follow-ups
- (preencher ao executar)
