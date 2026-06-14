# Fase 7 — Produtos 3D (catálogo da plataforma)

> Objetivo: a loja vende **produtos 3D / 3D personalizáveis** **escolhendo do catálogo público da plataforma** (modelos GLB prontos, populados por seed). O cliente personaliza no **editor 3D do storefront** (imagem + texto), aprova, e a personalização é **congelada no pedido**. Sobre as Fases 2 (catálogo), 3 (storefront) e 6 (checkout).

Docs de referência: **[30 — Design técnico](../../concepts/30_3d_customization_technical_design.md)** (contrato), [22 — Experiência](../../concepts/22_product_customization_3d.md), [07](../../concepts/07_database_strategy.md), [13](../../concepts/13_performance_cache_and_cdn.md), [14](../../concepts/14_security_strategy.md), [10](../../concepts/10_storefront_and_layouts.md), [09](../../concepts/09_merchant_dashboard.md), [25](../../concepts/25_platform_admin.md), [16](../../concepts/16_testing_strategy.md).

> Visão geral / trilha: [`../phase-7-3d-products.md`](../phase-7-3d-products.md). Este README é o **índice detalhado** das tasks.

## Decisões de entrada (doc 30 — não redecidir)
- **1º modelo = caneca branca de cerâmica** (`glb-models/ceramic-mug-3d-model.glb`, source 4K ~56 MB → pré-processar).
- Editor = **imagem + transform + texto**. **Sem troca de cor do produto na V1** (recolor = follow-up). Arte = **só raster (PNG/JPG)**.
- Lib = **react-three-fiber + drei**; **2 painéis** (2D = região de UV / 3D mostra na superfície); área imprimível = **região de UV** (a arte é mapeada pela UV do GLB → cola na superfície real), **editável no admin** (picker 2D + preview 3D).
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
| 1 | [P7-ASSET-01](./P7-ASSET-01-glb-preprocessing-pipeline.md) | Pipeline de pré-processamento do GLB (4K→web, Draco) + CDN | ✅ done | — |
| 2 | [P7-CAT-01](./P7-CAT-01-platform-3d-catalog.md) | Catálogo 3D da plataforma: tabelas + seed da caneca | ✅ done | P7-ASSET-01 |
| 3 | [P7-ADM-01](./P7-ADM-01-admin-catalog-and-area-editor.md) | Admin: habilitar/desabilitar + **editor visual 3D** da área imprimível | ✅ done | P7-CAT-01 |
| 4 | [P7-PROD-01](./P7-PROD-01-merchant-link-model-to-product.md) | Painel lojista: escolher do catálogo + vincular ao produto | ✅ done | P7-CAT-01 |
| 5 | [P7-SESS-01](./P7-SESS-01-customization-sessions-backend.md) | Sessões de personalização (backend) + assistida | ✅ done | P7-PROD-01 |
| 6 | [P7-EDITOR-01](./P7-EDITOR-01-storefront-editor-shell.md) | Editor storefront: 2 painéis + GLB + orbit/zoom + autosave | ✅ done | P7-SESS-01, P7-CAT-01 |
| 7 | [P7-EDITOR-02](./P7-EDITOR-02-layers-approval-snapshot.md) | Editor: camadas (imagem+texto) + aprovação + snapshot + link público | ✅ done | P7-EDITOR-01 |
| 8 | [P7-ORD-01](./P7-ORD-01-freeze-customization-in-order.md) | Carrinho/pedido: congelar a personalização | ✅ done | P7-SESS-01, P7-EDITOR-02 |
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
- [ ] **QA visual da caneca v1** (`simplify 0.25`, 491k tris, 2.05 MB) — **conferir quando o `P7-EDITOR-01` renderizar na vitrine** (alça/bordas no zoom do cliente). Se distorcer, regenerar com ratio maior (ou sem simplify) → **v2** + reseed. Origem: `P7-ASSET-01`.
- [ ] **Validar existência do GLB na chave do slug** (seed/upload) — slug com typo → `glb_url` 404 silencioso; o acoplamento slug↔caminho é garantido, a existência não. Origem: `P7-CAT-01`.
- [ ] **QA visual no browser do editor 3D** (`P7-ADM-01`) — a caneca carrega? o retângulo projeta certo? arrastar/girar/redimensionar fluido? Não inspecionável fora do browser. Origem: `P7-ADM-01`.
- [ ] **e2e Playwright do admin 3D** (lista/toggle/editar área). Origem: `P7-ADM-01`.
- [ ] **Costura da UV cilíndrica** (`--cylindrical-uv`): a emenda em `u=0/1` (atrás) não é dividida → uma faixa que cruza as costas mostra uma listra. OK pra faixa frontal; pra volta 360° precisa **split de vértices na costura**. Origem: `P7-ASSET-01`.
- [ ] **UV cilíndrica assume eixo Y + cilindro**: distorce um pouco onde a peça foge do cilindro (lábio/cônico) e fica torta se o modelo não estiver em pé. Pra produtos não-cilíndricos, unwrap limpo (Blender). Origem: `P7-ASSET-01`.
- [ ] **CORS do CDN reproduzível em produção** — o GLB carrega cross-origin no `three.js`; o CloudFront precisa devolver `Access-Control-Allow-Origin` (response-headers-policy `SimpleCORS`). Ligado **manualmente no dev** (console); falta no provisionamento de prod/IaC. Vale pro admin **e pra vitrine** (`P7-EDITOR-01`). Origem: `P7-ADM-01` (doc [30 §6](../../concepts/30_3d_customization_technical_design.md)).
- [ ] **Calibrar a região de UV imprimível da caneca** (o seed traz um retângulo placeholder) — fazer **visualmente** no admin (picker 2D de UV + preview 3D na superfície + Salvar). Origem: `P7-CAT-01`/`P7-ADM-01`.
- [x] **Aspecto da arte do cliente no editor da vitrine** — **resolvido em `P7-EDITOR-02`** (`regionAspect` enquadra o painel 2D no aspecto físico da `uv_rect`; faixa ~2:1). Origem: `P7-ADM-01`.
- [ ] **Múltiplas áreas imprimíveis** (camiseta frente/verso) — caneca usa 1; schema suporta N. Origem: `P7-CAT-01`.
- [ ] **Modelo vinculado desativado depois** — desativar um modelo/versão no admin não desfaz os vínculos existentes (`customization_product_settings`); o editor da vitrine não resolve o GLB. Avisar/bloquear/fallback. Origem: `P7-PROD-01`.
- [ ] **Excluir produto não desvincula** — soft delete do produto deixa a settings órfã (inofensiva; recriar não conflita). Limpar no delete por consistência. Origem: `P7-PROD-01`.
- [ ] **Preview do modelo na tela de produto** do painel (polir a UX de seleção). Origem: `P7-PROD-01`.
- [ ] **e2e Playwright do vínculo** (escolher → vincular → tipo muda → desvincular) → depende da infra de e2e do painel. Origem: `P7-PROD-01`.
- [ ] **Recolor do produto** (paleta + material nomeado + seletor) — fora da V1 (doc [30 §12](../../concepts/30_3d_customization_technical_design.md)). Origem: `P7-EDITOR-02`.
- [ ] **Arte vetorial (SVG/PDF)** — V1 é só raster. Origem: `P7-EDITOR-02`.
- [ ] **Múltiplas faces/áreas** (ex.: camiseta frente/verso) — a caneca usa 1 área. Origem: `P7-CAT-01`.
- [ ] **e2e Playwright do fluxo de personalização** (browser) → depende da infra `P3-SF-03`. Origem: `P7-EDITOR-02`.
- [ ] **Fontes web no editor** (Inter/Roboto/Montserrat carregadas) + aviso de glifo ausente — hoje o canvas cai no `sans-serif` do SO. Origem: `P7-EDITOR-02`.
- [ ] **Handles 2D ricos** (escala/rotação por alça, além de sliders + arrastar). Origem: `P7-EDITOR-02`.
- [ ] **Limpeza de uploads órfãos** de sessões que não viraram pedido (mantendo o que é do pedido). Origem: `P7-ORD-01`/`P7-SESS-01`.
- [ ] **Cópia do snapshot via S3 copy-object** (em vez de download+upload) ao congelar — perf/escala. Origem: `P7-ORD-01`.
- [ ] **Re-render server-side do composite** (fila/headless, fidelidade máxima) — hoje o cliente gera o retângulo de produção em alta-res no approve. Origem: `P7-EDITOR-02` (melhorias).
- [ ] **Upload direto ao S3 (presigned PUT)** — a barra de progresso cobre só navegador→Next (a etapa Next→backend→S3 é opaca, mostra "Processando…"); presigned PUT dá progresso real até o CDN e tira a imagem grande do Next. Origem: `P7-EDITOR-02` (melhorias).
- [ ] **Limpeza de arquivos (S3) de sessões expiradas** mantendo histórico de negócio — política de retenção. Origem: `P7-SESS-01`.
- [ ] **Anti-abuso no endpoint público** (rate limit do `public_token`) — hardening (Fase 10). Origem: `P7-SESS-01`.
- [x] **Strip de metadados/re-encode da imagem** no upload — **resolvido em `P7-EDITOR-02`** (`_sanitize_image` re-encoda via PIL → remove EXIF; snapshot idem). Origem: `P7-SESS-01`.
- [ ] **Status de arte/produção** (`received…production_done`) no **item do pedido** — criar onde é lido. Origem: `P7-SESS-01` → `P7-ORD-01`/`P7-OPS-01`.
- [ ] **`dispose` de texturas/geometrias** no editor ao fechar/trocar (perf mobile). Origem: `P7-EDITOR-01`.
- [ ] **Chrome do template no editor** — `/personalizar` é standalone; aplicar o `Shell` do template ativo. Origem: `P7-EDITOR-01`.
- [x] **Painel 2D proporcional à superfície** no storefront (`computeUnwrapAspect`/`regionAspect`) — **resolvido em `P7-EDITOR-02`**. Origem: `P7-EDITOR-01`.
- [ ] **Sessão expirada no autosave → oferecer clonar** (hoje só mostra o 410). Origem: `P7-EDITOR-01`.
