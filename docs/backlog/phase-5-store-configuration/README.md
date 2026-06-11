# Fase 5 — Configuração da loja

> Objetivo: com os templates **registrados** (Fase 4: thumbnail + schema), o lojista bota a loja no ar de verdade — **loja-demo por template** (imagens uxpilot → CDN), **personalização schema-driven** (1 form genérico), **vitrine lendo `theme.settings`** e **preview navegável**. **Antes do lançamento.**

Docs de referência: [Fundações & Gargalos](../_foundations-and-bottlenecks.md), [26](../../concepts/26_template_system.md), [27](../../concepts/27_template_authoring_guide.md), [25](../../concepts/25_platform_admin.md), [09](../../concepts/09_merchant_dashboard.md), [10](../../concepts/10_storefront_and_layouts.md), [07](../../concepts/07_database_strategy.md), [08](../../concepts/08_modules_and_permissions.md), [13](../../concepts/13_performance_cache_and_cdn.md), [16](../../concepts/16_testing_strategy.md).

> Visão geral / trilha: [`../phase-5-store-configuration.md`](../phase-5-store-configuration.md). Este README é o **índice detalhado** das tasks.

## Definition of Done da fase
- e2e roda contra **banco descartável** (não polui o db de dev); doc de banco (07) **auditado**.
- Lojista **personaliza** o template (form schema-driven, por loja × template) + a **vitrine reflete** (`theme.settings`).
- Cada template tem sua **loja-demo** (imagens no CDN via `import_assets`) e o painel abre o **preview navegável**.
- Thumbnails de template no **CDN** (admin + picker do lojista).

> **Fora desta fase:** carrinho/checkout/pedidos = **[Fase 6](../phase-6-sell-without-payment.md)**; 3D = **[Fase 7](../phase-7-3d-products.md)**; pagamentos/planos = **[Fase 8](../phase-8-customer-account-and-payments.md)**; cor do tema (campo `color`) = follow-up.

## Construído sobre as Fases 0–4 (não recriar)
- **`content_theme_templates` + `settings_schema`** (`P3-CONTENT-01`/`P4-TPL-01`): o schema vem do **código**, seedado no deploy.
- **Registro de templates + thumbnail no CDN** (`P4-TPL-01/02`): o admin registra; a Fase 5 importa as imagens + monta o demo.
- **`content_store_theme_settings`** (settings universais: banner/headline/cor) — Fase 3; o schema cobre só o **chrome específico** do template.
- **`media`/`storage`** (S3/CloudFront) + **`app.core.cache`** (invalidação) + **`storefront`** (vitrine por Host).

## Tasks

| # | ID | Task | Status | Depende de |
|---|---|---|---|---|
| 1 | [P5-TEST-01](./P5-TEST-01-e2e-disposable-db.md) | Banco descartável pro e2e (`db-test` + `backend-e2e`) | ✅ done | — |
| 2 | [P5-DOC-01](./P5-DOC-01-database-doc-audit.md) | Auditoria do doc de banco (tabelas + índices vs código) | ✅ done | — |
| 3 | [P5-CFG-01](./P5-CFG-01-template-settings-storage.md) | `content_store_template_settings` + API (storage dos settings) | ✅ done | P4-TPL-01 |
| 4 | [P5-CFG-02](./P5-CFG-02-template-settings-form.md) | Form genérico no painel (1 componente, N schemas) | ✅ done | P5-CFG-01 |
| 5 | [P5-DEMO-01](./P5-DEMO-01-import-assets.md) | `demo.json` + `import_assets` (uxpilot → CDN) | ✅ done | P4-TPL-01, P4-TPL-02 |
| 6 | [P5-DEMO-02](./P5-DEMO-02-template-demo-stores.md) | Loja-demo por template (`<id>-demo`) | ✅ done | P5-DEMO-01 |
| 7 | [P5-TPL-01](./P5-TPL-01-template-screens-refinements.md) | Refinos das telas de template (admin + dashboard, thumb CDN) | ✅ done | P5-DEMO-01 |
| 8 | [P5-SF-01](./P5-SF-01-storefront-reads-settings.md) | Vitrine lê `theme.settings` (defaults ⊕ overrides) | ✅ done | P5-CFG-01 |
| 9 | [P5-PREV-01](./P5-PREV-01-navigable-preview.md) | Preview navegável (painel abre a loja-demo) | ✅ done | P5-DEMO-02, P5-SF-01 |
| 10 | [P5-PAGE-01](./P5-PAGE-01-content-pages.md) | Conteúdo das páginas (`content_pages`/menus/banners no painel + vitrine) | ✅ done | — |

## Ordem sugerida de execução

```text
P5-TEST-01 · P5-DOC-01 · P5-PAGE-01    (independentes)
P5-CFG-01 → P5-CFG-02                  (settings: storage/API → form)
         └→ P5-SF-01 ┐
P5-DEMO-01 → P5-DEMO-02 ─┼→ P5-PREV-01
          └→ P5-TPL-01  ┘
```

## Follow-ups / débitos técnicos

> Item adiado vira checkbox aqui (origem + quando), e também na seção Follow-ups da task.

**Esta fase fecha follow-ups de fases anteriores** (marcar `[x]` na **origem** ao concluir a task):
- [x] **e2e polui o db de dev** (Fase 4) → `P5-TEST-01` ✅ (db-test tmpfs + backend-e2e; db de dev provado intacto).

**Da própria fase:**
- [ ] **e2e compartilha o `redis` do dev** (jobs do `backend-e2e` podem ser pegos pelo `worker` de dev e falhar — ruído, não polui). Isolar com `redis-test`/`worker-e2e`. Origem: `P5-TEST-01`.
- [x] **`settings_schema` na imagem do backend** ✅ resolvido (`backend/Dockerfile` copia `frontend-storefront/templates/`; seed no docker grava o schema real; doc 27 §Passo 4 atualizada). Origem: `P5-CFG-01`.
- [x] **Imagens-default (demo) no CDN** (Fase 4) → `P5-DEMO-01` ✅ (import_assets baixa→S3→CDN). **Thumb do seed absoluto (CDN)** + **PNGs de `public/` removidos** → `P5-TPL-01` ✅.
- [ ] **`import_assets`: erro por-imagem** (URL 4xx/5xx ou S3 falho aborta o template — decidir continuar+reportar) + **download em memória sem limite** (streaming p/ imagens grandes). Origem: `P5-DEMO-01`.
- [x] **Telas de templates: thumb relativo (admin)** + **dashboard thumbnail do CDN** (Fase 4, `P4-ADMIN-03`) → `P5-TPL-01` ✅ (admin lista/detalhe/editar + picker do dashboard usam o thumb absoluto do CDN; placeholder quando falta thumb).
- [x] **`previewLayout` sem uso** + **preview ao vivo / botão abrir preview** (Fases 3/4) → `P5-PREV-01` ✅ (painel abre `<id>-demo` no storefront; previewLayout removido). Sobra: permissão `layout.preview` órfã → follow-up.
- [x] **Conteúdo estático/lorem → dinâmico** (Fase 3) → `P5-SF-01` ✅ (chrome editável vem de settings nos 3 templates).
- [ ] **e2e/smoke do storefront** (vitrine reflete `theme.settings`) — storefront sem infra de e2e/Playwright; a API é coberta por integração (backend) + render type-validado (`tsc`/`next build`). Montar infra + e2e real. Origem: `P5-SF-01`.
- [ ] **Upload de imagem de layout gated na permissão errada** — o upload do banner (universal **e** dos `content_banners`) passa por `MediaService.uploadMedia`, que ainda exige **`catalog.product.update`**, não `layout.update`: um membro só-`layout` vê o botão (gated client por `layout.update`) mas o upload retorna **403**. Religar a rota de upload a `layout.update`/`layout.assets.update` (que hoje não está ligada a rota). Some o caso de campos `image` (nenhum template V1 tem). Mesmo débito que o follow-up aberto da Fase 3 (`P3-TPL-03`). Origem: Fase 3 + `P5-CFG-02`/`P5-PAGE-01`.
- [x] **CRUD de páginas/menus/banners** + **páginas institucionais via `content_pages`** (Fase 3, `P3-TPL-03`) → `P5-PAGE-01` ✅ (CRUD gated `layout.*` no painel; vitrine `/pages/[slug]` lê `content_pages` com fallback). Sobra: vitrine ainda não renderiza banners/menus → follow-up abaixo.

**Da própria fase:**
- [ ] **Detalhe do admin sem conteúdo-demo + defaults** — o escopo do `P5-TPL-01` pedia mostrar "conteúdo demo + defaults" no detalhe, mas `ThemeTemplateAdminPublic` expõe só id/nome/descrição/ativo/thumb/`settings_schema`; falta o backend expor o `demo.json` resolvido e os defaults do schema. Origem: `P5-TPL-01`.
- [ ] **Vitrine não renderiza banners nem menus** — o painel autora `content_banners`/`content_menus` (`P5-PAGE-01`), mas o hero usa `theme.banner_image_url` (único) e a nav dos Shells é fixa. Expor no `/storefront/home` + renderizar nos 3 templates. Origem: `P5-PAGE-01`.
- [ ] **e2e da vitrine para `content_pages`** — bloqueado pela falta de infra de Playwright no storefront (mesmo bloqueio do `P5-SF-01`); por ora coberto por integração no backend. Origem: `P5-PAGE-01`.
- [ ] **Edição de item de menu não exposta na UI** — `update_menu_item` existe/testada, mas o painel só add/remove item (+ renomeia menu). Expor edição inline. Origem: `P5-PAGE-01`.
- [ ] **Permissão `layout.preview` órfã** — `P5-PREV-01` removeu a rota de preview, mas a permissão segue no catálogo + mapa de papéis (`app/modules/stores/permissions.py`, 4 ocorrências) sem nenhum `require_permission` lendo. Permissão que ninguém lê = lixo (regra de ouro) → remover do catálogo/seed/mapa (e ajustar o teste "toda permissão em ≥1 papel"). Origem: `P5-PREV-01`.
