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
| 1 | [P5-TEST-01](./P5-TEST-01-e2e-disposable-db.md) | Banco descartável pro e2e (`db-test` + `backend-e2e`) | todo | — |
| 2 | [P5-DOC-01](./P5-DOC-01-database-doc-audit.md) | Auditoria do doc de banco (tabelas + índices vs código) | todo | — |
| 3 | [P5-CFG-01](./P5-CFG-01-template-settings-storage.md) | `content_store_template_settings` + API (storage dos settings) | todo | P4-TPL-01 |
| 4 | [P5-CFG-02](./P5-CFG-02-template-settings-form.md) | Form genérico no painel (1 componente, N schemas) | todo | P5-CFG-01 |
| 5 | [P5-DEMO-01](./P5-DEMO-01-import-assets.md) | `demo.json` + `import_assets` (uxpilot → CDN) | todo | P4-TPL-01, P4-TPL-02 |
| 6 | [P5-DEMO-02](./P5-DEMO-02-template-demo-stores.md) | Loja-demo por template (`<id>-demo`) | todo | P5-DEMO-01 |
| 7 | [P5-TPL-01](./P5-TPL-01-template-screens-refinements.md) | Refinos das telas de template (admin + dashboard, thumb CDN) | todo | P5-DEMO-01 |
| 8 | [P5-SF-01](./P5-SF-01-storefront-reads-settings.md) | Vitrine lê `theme.settings` (defaults ⊕ overrides) | todo | P5-CFG-01 |
| 9 | [P5-PREV-01](./P5-PREV-01-navigable-preview.md) | Preview navegável (painel abre a loja-demo) | todo | P5-DEMO-02, P5-SF-01 |
| 10 | [P5-PAGE-01](./P5-PAGE-01-content-pages.md) | Conteúdo das páginas (`content_pages`/menus/banners no painel + vitrine) | todo | — |

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
- [ ] **e2e polui o db de dev** (Fase 4) → `P5-TEST-01`.
- [ ] **Imagens-default no CDN** + **thumb relativo do seed** + **remover PNGs de `public/`** (Fase 4, `P4-TPL-02`) → `P5-DEMO-01`.
- [ ] **Telas de templates: thumb relativo (admin)** + **dashboard thumbnail do CDN** (Fase 4, `P4-ADMIN-03`) → `P5-TPL-01`.
- [ ] **`previewLayout` sem uso** + **preview ao vivo / botão abrir preview** (Fases 3/4) → `P5-PREV-01`.
- [ ] **Conteúdo estático/lorem → dinâmico** (Fase 3, `P3-TPL-03`) → `P5-SF-01`.
- [ ] **Permissão do upload do banner / layout** (Fase 3) → `P5-CFG-02` (`layout.assets.update`).
- [ ] **CRUD de páginas/menus/banners** + **páginas institucionais via `content_pages`** (Fase 3, `P3-TPL-03`) → `P5-PAGE-01`.

**Da própria fase:**
- (preencher conforme as tasks forem implementadas.)
