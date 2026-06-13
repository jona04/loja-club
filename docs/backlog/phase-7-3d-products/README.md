# Fase 7 — Produtos 3D (catálogo da plataforma)

> Objetivo: a loja vende **produtos 3D / 3D personalizáveis** **escolhendo do catálogo público da plataforma** (modelos GLB prontos, populados por seed). O cliente personaliza no **editor 3D do storefront** (imagem + texto), aprova, e a personalização é **congelada no pedido**. Sobre as Fases 2 (catálogo), 3 (storefront) e 6 (checkout).

Docs de referência: **[30 — Design técnico](../../concepts/30_3d_customization_technical_design.md)** (contrato), [22 — Experiência](../../concepts/22_product_customization_3d.md), [07](../../concepts/07_database_strategy.md), [13](../../concepts/13_performance_cache_and_cdn.md), [14](../../concepts/14_security_strategy.md), [10](../../concepts/10_storefront_and_layouts.md), [09](../../concepts/09_merchant_dashboard.md), [25](../../concepts/25_platform_admin.md), [16](../../concepts/16_testing_strategy.md).

> Visão geral / trilha: [`../phase-7-3d-products.md`](../phase-7-3d-products.md). Este README é o **índice detalhado** das tasks.

## Decisões de entrada (doc 30 — não redecidir)
- **1º modelo = caneca branca de cerâmica** (`glb-models/ceramic-mug-3d-model.glb`, source 4K ~56 MB → pré-processar).
- Editor = **imagem + transform + texto**. **Sem troca de cor do produto na V1** (recolor = follow-up). Arte = **só raster (PNG/JPG)**.
- Lib = **react-three-fiber + drei**; **2 painéis** (2D edita / 3D gira-zoom-move); área imprimível = **decal projetado**, **editável no admin**.
- Assistida = **link público (`public_token`) + confirmação de contato** (sem conta; logado é Fase 8).
- **Snapshot client-side** (canvas→PNG) na aprovação; pedido **congela** `state_json` + `version_id` + snapshot.

## Definition of Done da fase
- Catálogo público (seed) com a **caneca**; **admin habilita/desabilita + edita a área imprimível**.
- Lojista **escolhe do catálogo** e vincula ao produto (sem gerar nada).
- Cliente personaliza no editor (2 painéis), **autosave** + **aprovação**; personalização **congelada no pedido**.
- Assistida: lojista monta pelo cliente → **link público** → cliente vê/aprova confirmando contato.
- Lojista opera as personalizações (ver arte, baixar, status de produção).
- Testes: isolamento, arte privada (URL assinada), congelamento, gate `image_3d_customizable` só com `approved`.

## Tasks

| # | ID | Task | Status | Depende de |
|---|----|------|--------|-----------|
| 1 | [P7-ASSET-01](./P7-ASSET-01-glb-preprocessing-pipeline.md) | Pipeline de pré-processamento do GLB (4K→web, Draco) + CDN | todo | — |
| 2 | [P7-CAT-01](./P7-CAT-01-platform-3d-catalog.md) | Catálogo 3D da plataforma: tabelas + seed da caneca | todo | P7-ASSET-01 |
| 3 | [P7-ADM-01](./P7-ADM-01-admin-catalog-and-area-editor.md) | Admin: habilitar/desabilitar + editor visual da área | todo | P7-CAT-01 |
| 4 | [P7-PROD-01](./P7-PROD-01-merchant-link-model-to-product.md) | Painel lojista: escolher do catálogo + vincular ao produto | todo | P7-CAT-01 |
| 5 | [P7-SESS-01](./P7-SESS-01-customization-sessions-backend.md) | Sessões de personalização (backend) + assistida | todo | P7-PROD-01 |
| 6 | [P7-EDITOR-01](./P7-EDITOR-01-storefront-editor-shell.md) | Editor storefront: 2 painéis + GLB + orbit/zoom + autosave | todo | P7-SESS-01, P7-CAT-01 |
| 7 | [P7-EDITOR-02](./P7-EDITOR-02-layers-approval-snapshot.md) | Editor: camadas (imagem+texto) + aprovação + snapshot + link público | todo | P7-EDITOR-01 |
| 8 | [P7-ORD-01](./P7-ORD-01-freeze-customization-in-order.md) | Carrinho/pedido: congelar a personalização | todo | P7-SESS-01, P7-EDITOR-02 |
| 9 | [P7-OPS-01](./P7-OPS-01-merchant-operate-and-assisted.md) | Painel lojista: operar personalizações + montar assistida | todo | P7-SESS-01 |
| 10 | [P7-SF-02](./P7-SF-02-storefront-variant-selection.md) | Vitrine: seleção de variação (não-3D, da Fase 6) | todo | — |

## Ordem sugerida de execução

```text
P7-ASSET-01 → P7-CAT-01
                 ├→ P7-ADM-01            (admin: catálogo + editor de área)
                 └→ P7-PROD-01 → P7-SESS-01
                                    ├→ P7-EDITOR-01 → P7-EDITOR-02
                                    │                     └→ P7-ORD-01 (congelar)
                                    └→ P7-OPS-01         (operar + assistida)

P7-SF-02 (variação na vitrine) — independente do 3D, pode ir a qualquer momento
```

## Follow-ups / débitos técnicos

> Item adiado vira checkbox aqui (origem + quando), e também na seção Follow-ups da task.

**Esta fase fecha follow-ups de fases anteriores** (marcar `[x]` na origem ao concluir):
- [ ] **Vitrine expõe variações + disponibilidade** (Fase 3, `P3-SF-01`/`P3-SF-02`; movido da Fase 6) → **`P7-SF-02`**.

**Da própria fase** (preencher conforme as tasks fecham):
- [ ] **Recolor do produto** (paleta + material nomeado + seletor) — fora da V1 (doc [30 §12](../../concepts/30_3d_customization_technical_design.md)). Origem: `P7-EDITOR-02`.
- [ ] **Arte vetorial (SVG/PDF)** — V1 é só raster. Origem: `P7-EDITOR-02`.
- [ ] **Múltiplas faces/áreas** (ex.: camiseta frente/verso) — a caneca usa 1 área. Origem: `P7-CAT-01`.
- [ ] **e2e Playwright do fluxo de personalização** (browser) → depende da infra `P3-SF-03`. Origem: `P7-EDITOR-02`.
