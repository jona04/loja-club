---
id: P2-CAT-02
title: catalog — serviço/rotas (CRUD/publicar/categorias/variações/estoque/imagens)
phase: 2
etapa: "Etapa 5 — Módulo catalog"
area: CAT
status: done
depends_on: [P2-CAT-01, P2-MEDIA-02]
blocks: [P2-FE-01]
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
- Vincular produto a modelo 3D / marcar personalizável → **[Fase 5 — Produtos 3D](../phase-5-3d-products.md)**. Telas → `P2-FE-01`.

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
- [x] CRUD/publish + categorias/variações/estoque/imagens no padrão `P1-API-01`, com gating (19 rotas).
- [x] `slug` único por loja; isolamento garantido pelo `get_store_scoped`.
- [x] Client OpenAPI regenerado (catalog **+** `uploadMedia`); `tsc` verde; lint/tests/cobertura verdes (166 passed, 93%).
- [x] Itens adiados varridos → Follow-ups + README.

## Progresso
- ✅ **Schemas/Repos/Service/Routes** (`catalog/*`): products (list/get/create/update/publish/unpublish/archive), categories (CRUD), variants (CRUD), images (attach/list/remove), inventory (set). Gating `catalog.*`; tudo scoped por `get_store_scoped` (INV-T2); listas com `Page`. Slug derivado + único-quando-ativo (**auto-sufixo** `-2/-3…` em nome repetido; slug explícito tomado → 409); `currency` herdada da loja.
- ✅ **Wire** no `api/router.py`; **client OpenAPI** regenerado (`scripts/generate-client.sh` → openapi-ts), `tsc -p tsconfig.build.json` verde.
- ✅ **Testes** `tests/integration/api/routes/test_catalog.py`: CRUD/publish/archive, slug por loja, cross-store, isolamento, **gating (support→403)**, inventory upsert, categorias, variantes, imagens (+ isolamento de mídia).

## Notas / Reconciliações
- **Arquivar = soft delete** (status `archived` + `deleted_at`): some das listas/get ativos; slug volta a ficar livre.
- **Slug:** derivado do nome **auto-desambigua** (`camiseta`, `camiseta-2`…); enquanto `draft`, renomear faz o slug **acompanhar**; ao **publicar**, trava (URL pública estável). Slug explícito tomado → 409. (Race concorrente segue como follow-up.)
- **Imagem só de mídia da própria loja:** `attach_image` valida a `media_file` via `get_store_scoped` (404 se for de outra loja).
- **`currency` do produto** herdada da loja na criação (override opcional no payload).
- **Permissões de categoria:** view via `catalog.view`; escrita via `catalog.category.manage` (doc 08).
- **`GET .../products/{id}/inventory`** (gated `catalog.product.view`) — devolve o estoque do produto (ou `null` se não houver), pra o painel **pré-preencher** o campo de quantidade no editar.

## Follow-ups
- [ ] **Race no slug:** o pré-check (`active_slug_exists`) tem janela de corrida → dois creates simultâneos com o mesmo slug → o 2º estoura `IntegrityError` (índice parcial) como **500**, não 409. Tratar `IntegrityError` no service → 409. Origem: P2-CAT-02.
- [ ] **Estoque sem unique:** índice `(store_id, product_id, variant_id)` é **não-único** (doc 07) → upsert de `set_inventory` tem corrida que pode criar **linhas duplicadas** de estoque. Avaliar índice parcial único + tratamento. Origem: P2-CAT-02.
- [ ] **Archive não cascateia:** arquivar produto **não** arquiva variações/imagens/estoque (ficam órfãos ativos). Decidir cascata (soft-delete filhos) ou ignorar conscientemente. Origem: P2-CAT-02.
