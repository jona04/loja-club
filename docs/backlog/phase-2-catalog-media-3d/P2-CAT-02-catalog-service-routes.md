---
id: P2-CAT-02
title: catalog — serviço/rotas (CRUD/publicar/categorias/variações/estoque/imagens)
phase: 2
etapa: "Etapa 5 — Módulo catalog"
area: CAT
status: todo
depends_on: [P2-CAT-01, P2-MEDIA-02]
blocks: [P2-CUST-02, P2-FE-01]
tests: [integration]
---

# P2-CAT-02 — `catalog`: serviço e rotas

## Contexto
Endpoints do painel para o catálogo, sob `/api/v1/stores/{store_id}/...`, com gating por `catalog.*` e padrão de API (`P1-API-01`). Reusa `require_permission`, `get_active_store`, `get_store_scoped` (INV-T2) e o `Page`.

## Docs de referência
- [09 — Merchant Dashboard](../../09_merchant_dashboard.md) (produtos)
- [20 — API Contracts](../../20_api_contracts_todo.md)
- [08 — Modules and Permissions](../../08_modules_and_permissions.md) (`catalog.*`)
- [07 — Database Strategy](../../07_database_strategy.md) (regras de query)

## Escopo (o que ENTRA)
- **Produtos:** listar (paginado), criar, atualizar, **arquivar** (soft delete → `archived`), **publicar/despublicar**. Geração de `slug` a partir do nome + único por loja quando ativo. `currency` default herdada da loja.
- **Categorias:** CRUD; **variações**; **estoque** (atualizar quantidade); **imagens** (vincular `media_file_id`, reordenar `position`).
- Gating: `catalog.product.*`, `catalog.category.*`, `catalog.inventory.*`, `catalog.product.update` p/ publicar — conforme doc [08](../../08_modules_and_permissions.md).
- Acesso a recurso por `store_id + id` (`get_store_scoped`). Incluir router no `api/router.py`. Regenerar client OpenAPI.

## Fora de escopo (o que NÃO entra)
- Vincular produto a modelo 3D / marcar personalizável → `P2-CUST-02`/`P2-CUST-03`. Telas → `P2-FE-01`.

## Arquivos a criar/alterar
- `backend/app/modules/catalog/services.py`/`repositories.py`/`routes.py`/`schemas.py` (preencher).
- `backend/app/api/router.py` (incluir). Regenerar client.

## Passos
1. Schemas (create/update/public) + repositories scoped + serviço (slug, publish/archive).
2. Rotas com `require_permission` + paginação.
3. Tests de fluxo, isolamento e gating.

## Testes
> Fundações §10. Fronteira real (constraint/permissão/query) → integração.

- **Cobrir:** criar/publicar/despublicar/arquivar produto; estoque; `slug` único por loja; mesmo slug em lojas diferentes; `support` sem `catalog.*` → 403; loja A não vê produto de B.

## Definition of Done
- [ ] CRUD/publish + categorias/variações/estoque/imagens no padrão `P1-API-01`, com gating.
- [ ] `slug` único por loja; isolamento garantido pelo guard.
- [ ] Client OpenAPI regenerado; lint/tests/cobertura verdes.
- [ ] Itens adiados varridos → Follow-ups + README (ou "nenhum").

## Notas / Reconciliações
- (preencher)

## Follow-ups
- (preencher)
