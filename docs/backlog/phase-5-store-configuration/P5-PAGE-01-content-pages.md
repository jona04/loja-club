---
id: P5-PAGE-01
title: Conteúdo das páginas (content_pages/menus/banners no painel + vitrine)
phase: 5
etapa: "Etapa 6 — Conteúdo das páginas"
area: PAGE
status: done
depends_on: []
blocks: []
tests: [integration, e2e]
---

# P5-PAGE-01 — Conteúdo das páginas

## Contexto
Os modelos (`content_pages`/`content_menus`/`content_menu_items`/`content_banners`) já existem (`P3-CONTENT-01`); faltam **rotas + UI** no painel e o **wiring** na vitrine. Hoje `/pages/[slug]` mostra defaults apresentáveis (`P3-TPL-03`).

## Docs de referência
- [09 — Merchant Dashboard](../../concepts/09_merchant_dashboard.md)
- [10 — Storefront and Layouts](../../concepts/10_storefront_and_layouts.md)
- [08 — Modules and Permissions](../../concepts/08_modules_and_permissions.md) (`layout.*`)

## Escopo (o que ENTRA)
- **CRUD de páginas** (institucionais: sobre/privacidade/termos/trocas + avulsas), **menus** e **banners** no painel — o lojista escreve o conteúdo real (gating `layout.*`).
- **Vitrine:** `/pages/[slug]` passa a ler de **`content_pages`**; **fallback** pro default quando a página não existir.

## Fora de escopo (o que NÃO entra)
- Os settings de chrome (schema): `P5-CFG-*`.
- Editor visual drag-drop / reordenar blocos livres → fora da V1.

## Arquivos a criar/alterar
- `backend/app/modules/content/{services,routes}.py` (alterar) — CRUD de pages/menus/banners (gated `layout.update`); invalida cache ao salvar.
- `frontend-dashboard/src/routes/_layout/...` (criar/alterar) — UI de conteúdo.
- `frontend-storefront/app/pages/[slug]/...` (alterar) — ler `content_pages`.

## Passos
1. Rotas CRUD de pages/menus/banners (gated `layout.update`) + invalidação de cache.
2. UI no painel.
3. Vitrine `/pages/[slug]` lê `content_pages` (fallback default).

## Testes
- **Níveis:** integração (CRUD) + e2e (vitrine).
- **Quando escrever:** durante.
- **Cobrir:** integração — CRUD gated `layout.update`, único por slug ativo; e2e — página criada aparece na vitrine; inexistente → fallback.

## Definition of Done
- [x] CRUD de pages/menus/banners no painel (gated `layout.*`); cache invalidado.
- [x] Vitrine `/pages/[slug]` lê `content_pages` (fallback quando não existir).
- [x] Gates + testes (integração: CRUD gated + slug único + 404s + cascade; e2e painel `store-content.spec`).
- [x] **Modos de falha mapeados** (slug duplicado, página inexistente, menu órfão) → tratados ou Follow-ups.
- [x] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Funde os follow-ups "CRUD de páginas/menus/banners" + "páginas institucionais via `content_pages`" da Fase 3.
- **Backend:** `content/{schemas,repositories,services,routes}.py` ganharam CRUD de `pages`/`banners`/`menus`(+`items`) sob `/stores/{id}/layout/...`, gated `layout.view`/`layout.update`; toda escrita chama `invalidate_layout_cache`. Modos de falha tratados: slug duplicado → **409** `duplicate_slug` (create e rename); not-found → **404**; item em menu inexistente → **404** `menu_not_found` (sem órfão); excluir menu **cascateia soft-delete** nos itens.
- **Vitrine:** `getPage(slug)` (storefront `/storefront/pages/{slug}`, já existente) — 404 vira `null` → `/pages/[slug]` cai no copy default. Body em texto, parágrafos separados por linha em branco.
- **Painel:** rota `/_layout/store-content` (menu "Conteúdo", gated `layout.view`) com abas Páginas/Banners/Menus; banner reusa `MediaService.uploadMedia(owner_type="banner")`.

## Follow-ups
- [ ] **Vitrine não renderiza banners nem menus** — o painel **autora** `content_banners`/`content_menus`, mas o hero da vitrine ainda usa `theme.banner_image_url` (único) e a nav dos Shells é fixa (`sobre`/`privacidade`/`termos`). Expor banners/menus no `/storefront/home` + renderizar nos 3 templates (carrossel de banners; nav por menu header/footer).
- [ ] **e2e da vitrine (página de `content_pages`)** — "página criada aparece na vitrine" não roda: o storefront não tem infra de Playwright (mesmo bloqueio do follow-up de `P5-SF-01`). Coberto por integração no backend (`test_published_page_is_served` + 404). Montar infra e fazer o e2e real.
- [ ] **Edição de item de menu não exposta na UI** — `update_menu_item` existe (e é testada), mas o painel só faz add/remove de item (+ renomear o menu). Expor edição inline de `label`/`url`/`position`.
