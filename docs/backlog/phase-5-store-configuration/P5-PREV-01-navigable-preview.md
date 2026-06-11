---
id: P5-PREV-01
title: Preview navegável (painel abre a loja-demo do template)
phase: 5
etapa: "Etapa 5 — Vitrine lê settings + preview navegável"
area: PREV
status: done
depends_on: [P5-DEMO-02, P5-SF-01]
blocks: []
tests: [e2e]
---

# P5-PREV-01 — Preview navegável

## Contexto
O preview navegável = o storefront servindo a **loja-demo** do template (cada clique navega de verdade: home → categoria → produto → carrinho). O painel abre esse preview em vez de só uma imagem.

## Docs de referência
- [26 — Sistema de templates](../../concepts/26_template_system.md) (§"A loja-demo", §"Ciclo de vida")
- [27 — Guia de autoria](../../concepts/27_template_authoring_guide.md) (Passo 8)
- [10 — Storefront and Layouts](../../concepts/10_storefront_and_layouts.md) (§"Preview")

## Escopo (o que ENTRA)
- O painel abre o **preview navegável completo** do template (outra aba) — a **loja-demo** (`<id>-demo`) servida pelo storefront.
- **Remover o `previewLayout`** (backend) — sem uso desde o `P3-TPL-03` (o preview navegável o substitui).

## Fora de escopo (o que NÃO entra)
- Montar a loja-demo: `P5-DEMO-02`.
- A vitrine ler settings: `P5-SF-01`.

## Arquivos a criar/alterar
- `frontend-dashboard/src/routes/_layout/store-layout.tsx` (alterar) — botão "abrir preview navegável".
- `backend/app/modules/content/{services,routes}.py` (alterar) — remover `previewLayout`.

## Passos
1. Painel: botão abre a loja-demo do template (URL do storefront).
2. Remover o `previewLayout` do backend (e do painel).

## Testes
- **Níveis:** e2e (Playwright).
- **Cobrir:** e2e — abrir o preview navega na loja-demo (home → categoria → produto).

## Definition of Done
- [x] Painel abre o **preview navegável** — cada template linka pra `{id}-demo.{storefront}` (imagem do card + botão "Ver preview", nova aba). URL via `VITE_STOREFRONT_URL` (.env + compose).
- [x] `previewLayout` removido (rota `/preview/{id}` + `preview_theme_settings` + Dialog do painel + regen do client).
- [x] Gates (tsc/biome/vitest) + **e2e** (`store-layout.spec`: o link "Ver preview" aponta pra `*-demo.*`).
- [x] **Modos de falha mapeados** (loja-demo ausente / template sem demo → o storefront responde 404 "loja não encontrada"; abre em nova aba, não bloqueia o painel).
- [x] **Itens adiados varridos** → Follow-ups + README.

> **Entregue:** painel: `demoStoreUrl(templateId)` + links pro `<id>-demo` (removido o preview-Dialog/`previewId`); backend: removidos a rota `/preview/{id}` + `preview_theme_settings` + o teste; client regenerado (`previewLayout` sumiu); `VITE_STOREFRONT_URL` no `.env`+compose. tsc/biome/vitest + e2e verdes.

## Notas / Reconciliações
- **Fecha** os follow-ups "previewLayout sem uso" (P3-TPL-03) e "preview ao vivo / botão abrir preview" (Fases 3/4).

## Follow-ups
- [ ] **Permissão `layout.preview` órfã** — sem rota desde a remoção do `previewLayout`; remover do catálogo + seed de permissões (CLAUDE.md: permissão sem leitor = lixo). Origem: `P5-PREV-01`.
