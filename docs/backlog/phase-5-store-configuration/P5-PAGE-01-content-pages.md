---
id: P5-PAGE-01
title: Conteúdo das páginas (content_pages/menus/banners no painel + vitrine)
phase: 5
etapa: "Etapa 6 — Conteúdo das páginas"
area: PAGE
status: todo
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
- [ ] CRUD de pages/menus/banners no painel (gated `layout.*`); cache invalidado.
- [ ] Vitrine `/pages/[slug]` lê `content_pages` (fallback quando não existir).
- [ ] Gates + testes.
- [ ] **Modos de falha mapeados** (slug duplicado, página inexistente, menu órfão) → tratados ou Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Funde os follow-ups "CRUD de páginas/menus/banners" + "páginas institucionais via `content_pages`" da Fase 3.

## Follow-ups
- [ ] — nenhum (preencher ao implementar).
