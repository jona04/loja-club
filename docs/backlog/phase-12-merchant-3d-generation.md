# Fase 12 — 3D gerado pelo lojista (traga seu próprio modelo)

> Objetivo: além do **catálogo da plataforma** (Fase 7), o lojista passa a **gerar o próprio modelo 3D (GLB)** via **API de terceiros** (image/text → GLB) e **mapear a área personalizável pelo painel** — o caminho **avançado/DIY**, para produtos que não estão no catálogo público. Reaproveita toda a experiência de personalização da Fase 7 (editor, sessões, congelar no pedido); só muda a **origem do modelo** (gerado pela loja, não do catálogo).

Docs de referência: [30](../concepts/30_3d_customization_technical_design.md), [22](../concepts/22_product_customization_3d.md), [18](../concepts/18_open_decisions.md), [07](../concepts/07_database_strategy.md), [13](../concepts/13_performance_cache_and_cdn.md), [14](../concepts/14_security_strategy.md), [09](../concepts/09_merchant_dashboard.md), [16](../concepts/16_testing_strategy.md).

> **Decisão a fechar:** o **provedor de geração 3D** (Meshy / Tripo3D / Hyper3D) — registrar no doc [18](../concepts/18_open_decisions.md). A **geração** é um recurso de **plano pago** (gancho de plano da Fase 8).

## Definition of Done da fase
- O lojista **gera um modelo 3D via API** a partir de uma imagem/descrição; o GLB fica no storage **da loja** (S3/CloudFront) e é vinculado ao produto.
- O lojista **mapeia a área personalizável** (e limites) do modelo gerado **pelo painel** (sem depender do dev/seed) — **reaproveitando a ferramenta de mapeamento criada no admin da Fase 7** (doc [30](../concepts/30_3d_customization_technical_design.md)).
- O modelo gerado entra no mesmo fluxo de personalização da Fase 7 (editor → aprovação → congela no pedido).
- Geração restrita a **plano pago** (billing da Fase 8).

---

## Etapa 1 — Geração de modelo 3D via API (integração)

Doc [18](../concepts/18_open_decisions.md), [22](../concepts/22_product_customization_3d.md).
- [ ] Abstração fina do provedor de geração 3D (módulo `product_customization` ou `app/core/...`): submeter imagem/descrição → obter GLB; tratar **assíncrono** (geração demora) via **worker**.
- [ ] Persistir o GLB **por loja** (S3) e servir por CDN — seguindo a convenção de chaves do doc [30 §6](../concepts/30_3d_customization_technical_design.md) (o GLB é público pro storefront; a arte do cliente continua privada). Reaproveita `app/core/storage.py` (Fase 2).
- [ ] Decisão do provedor (Meshy/Tripo3D/Hyper3D) registrada no doc [18](../concepts/18_open_decisions.md).

## Etapa 2 — Modelos por loja + versões

Doc [07](../concepts/07_database_strategy.md).
- [ ] Tabelas **por loja** (`store_id`) para os modelos gerados + versões (GLB, parâmetros, áreas, limites) — espelham o catálogo da plataforma (Fase 7), mas são da loja.

## Etapa 3 — Mapear a área personalizável pelo painel

Doc [09](../concepts/09_merchant_dashboard.md), [22](../concepts/22_product_customization_3d.md).
- [ ] **Reaproveitar a ferramenta de mapeamento da área** (criada no admin da Fase 7, doc [30 §3](../concepts/30_3d_customization_technical_design.md)) pra o lojista **definir a área imprimível** + limites (texto/escala; **cor é follow-up**, doc [30 §12](../concepts/30_3d_customization_technical_design.md)) sobre o GLB gerado — a config que, no catálogo da plataforma, vinha do seed.

## Etapa 4 — Vincular ao produto + restrição por plano

- [ ] Vincular o modelo gerado ao produto (marca `image_3d`/`image_3d_customizable`) e entrar no fluxo da Fase 7 (editor/sessões/congelar).
- [ ] **Gating de plano:** a geração é recurso **premium** (billing da Fase 8 + `require_permission`).

---

## Testes (doc [16](../concepts/16_testing_strategy.md))
- [ ] geração assíncrona (worker) com sucesso/erro; GLB no storage da loja por CDN; área mapeada pelo painel aplicada no editor; isolamento por loja; gating de plano (loja sem plano não gera).

---

## Reconciliações
- Esta fase é a **outra metade** do 3D que saiu da Fase 7: o **catálogo público da plataforma** é a Fase 7 (caminho fácil/barato, via seed); a **geração pelo lojista** é esta fase (avançado). Doc [22](../concepts/22_product_customization_3d.md) descreve os dois caminhos.
