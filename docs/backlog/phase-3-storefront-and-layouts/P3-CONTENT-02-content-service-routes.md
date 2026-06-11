---
id: P3-CONTENT-02
title: content — serviço/rotas do painel (tema/layout)
phase: 3
etapa: "Etapa 3 — Módulo de conteúdo/layout"
area: CONTENT
status: done
depends_on: [P3-CONTENT-01]
blocks: [P3-FE-02]
tests: [integration]
---

# P3-CONTENT-02 — Serviço/rotas do `content`

## Contexto
Endpoints do **painel** para o lojista escolher o template e editar a aparência; aplicar template **invalida o cache de leitura** que a vitrine (`P3-SF-01`) consome.

## Docs de referência
- [10 — Storefront & Layouts](../../concepts/10_storefront_and_layouts.md)
- [13 — Performance, Cache & CDN](../../concepts/13_performance_cache_and_cdn.md)
- [20 — API Contracts](../../concepts/20_api_contracts_todo.md)

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
- [x] Aplicar/editar persiste + **invalida** `store:{id}:theme|home|settings` (teste com `cache_set`/`cache_get`).
- [x] Gating (`layout.*`) + isolamento por loja testados; **cliente OpenAPI regenerado** (`ContentService`).
- [x] **Modos de falha mapeados** (template inexistente → 400; invalidação stale; race de aplicar) → Follow-ups.
- [x] Itens adiados varridos → Follow-ups + README.

## Notas / Reconciliações
- As chaves de cache são definidas junto com a `P3-SF-01` (quem as lê); manter os nomes em sincronia.
- **Aplicar + editar unificados** em `PATCH /stores/{id}/layout` (um write, `exclude_unset`; `active_template_id` valida template ativo). Leitura: `GET /layout`, `/layout/templates`, `/layout/preview/{template_id}`.
- **`get_or_create`:** loja sem row → cria default (`classic`) no 1º acesso (lazy init em GET/preview/PATCH) — atende ao "loja sem theme settings → default".
- **Gating** por `layout.view`/`preview`/`update` (já no catálogo de permissões da Fase 1); **sem `permissions.py`** no módulo, usando as strings (= padrão do `catalog`).
- **Preview não persiste** (só o response carrega o template previsto).

## Follow-ups
- [ ] **Invalidação de cache falha → stale** (`P3-CONTENT-02`): `cache_delete` roda **após o commit**; se o Redis cair, a escrita persiste mas o cache fica stale (e a request pode 500). Tratar (best-effort/log) quando o cache de leitura da vitrine entrar (`P3-SF-01`).
- [ ] **Race de aplicar** (`P3-CONTENT-02`): PATCH concorrente = last-write-wins (sem lock). Aceitável no V1.
- [ ] **CRUD de páginas/menus/banners no painel** (`P3-CONTENT-02`): modelos existem (CONTENT-01), mas sem rotas/UI — adicionar quando a UI precisar.
