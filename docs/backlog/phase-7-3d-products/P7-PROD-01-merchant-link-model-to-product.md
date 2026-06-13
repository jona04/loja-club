---
id: P7-PROD-01
title: Painel lojista — escolher do catálogo + vincular ao produto
phase: 7
etapa: "Etapa 3 — Painel do lojista: escolher do catálogo + vincular ao produto"
area: PROD
status: todo
depends_on: [P7-CAT-01]
blocks: [P7-SESS-01]
tests: [integration]
---

# P7-PROD-01 — Lojista escolhe do catálogo e vincula ao produto

## Contexto
O lojista **navega o catálogo público** (modelos habilitados) e **vincula** um modelo a um produto, marcando-o `image_3d`/`image_3d_customizable` (o campo `type` já existe desde a Fase 6). Sem gerar nada, sem custo.

## Docs de referência
- [30 — §8 `customization_product_settings`](../../concepts/30_3d_customization_technical_design.md)
- [09 — Merchant dashboard (Fase 7)](../../concepts/09_merchant_dashboard.md)

## Escopo (o que ENTRA)
- `customization_product_settings` (por loja): `store_id`, `product_id` → `platform_3d_model_id` + observações de produção. Índice `store_id+product_id` único. Migration.
- Painel (backend + `frontend-dashboard`): listar catálogo habilitado, **escolher** um modelo, **vincular** ao produto e ajustar o `type` do produto. Gated por permissão de produto/personalização.
- Vitrine/editor passam a resolver o modelo do produto a partir daqui.

## Fora de escopo (o que NÃO entra)
- Sessões/editor: `P7-SESS-01`/`P7-EDITOR-*`.
- Edição da área (admin): `P7-ADM-01`.
- **Cor do produto** (recolor): fora da V1.

## Arquivos a criar/alterar
- `backend/app/modules/customization/{models,schemas,services,routes}.py` (alterar) — settings + rotas painel.
- `frontend-dashboard/src/routes/...` (alterar) — seção 3D na tela de produto (escolher/vincular).
- migration alembic.

## Passos
1. `customization_product_settings` + migration.
2. Rotas painel (listar catálogo habilitado, vincular, setar `type`).
3. UI na tela de produto (escolher modelo + observações).

## Testes
- **Níveis:** integração.
- **Quando escrever:** durante.
- **Cobrir:** integração — vincular seta `type` e a settings; isolamento por loja; só modelos **ativos** podem ser vinculados.

## Definition of Done
- [ ] Lojista vincula um modelo do catálogo ao produto (settings + `type`); isolamento por loja.
- [ ] **Modos de falha mapeados** — vincular modelo desabilitado → 422; desvincular volta `type` p/ `image`. → tratados/Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- `allow_color` **não** entra (recolor fora da V1) — settings só tem o vínculo + observações.

## Follow-ups
- [ ] **Preview do modelo na tela de produto** do painel — *Quando:* polir a UX de seleção. → README da fase.
