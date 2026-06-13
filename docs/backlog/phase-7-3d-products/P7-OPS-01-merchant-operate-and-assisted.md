---
id: P7-OPS-01
title: Painel lojista — operar personalizações + montar assistida
phase: 7
etapa: "Etapa 7 — Painel do lojista: operar as personalizações"
area: OPS
status: todo
depends_on: [P7-SESS-01]
blocks: []
tests: [integration]
---

# P7-OPS-01 — Operar personalizações + personalização assistida

## Contexto
O lado **lojista**: ver as sessões/arte da própria loja, **baixar** os arquivos e atualizar o **status de produção** — e **montar a personalização em nome do cliente** (assistida), gerando o **link público** pra ele ver/aprovar.

## Docs de referência
- [30 — §9 Assistida + link público](../../concepts/30_3d_customization_technical_design.md)
- [22 — Personalização assistida / Painel do lojista](../../concepts/22_product_customization_3d.md)
- [09 — Merchant dashboard](../../concepts/09_merchant_dashboard.md)

## Escopo (o que ENTRA)
- `frontend-dashboard`: tela das personalizações da loja — listar (polling), abrir preview, **baixar** arte (URL assinada), atualizar **status de arte/produção** (`received…production_done`). Gated por permissão.
- **Montar assistida:** abrir o editor **em nome do cliente** (reusa o editor), pré-cadastrar por contato (`create_or_update_customer`), salvar a sessão (`created_by`) e **gerar o link público** (`public_token`) pra o cliente ver/aprovar (`P7-EDITOR-02`/`P7-SESS-01`).

## Fora de escopo (o que NÃO entra)
- Backend das sessões/`public_token`: `P7-SESS-01`. Editor em si: `P7-EDITOR-*`.
- Congelar no pedido: `P7-ORD-01`.

## Arquivos a criar/alterar
- `backend/app/modules/customization/routes.py` (alterar) — listagem/operacional da loja + criar assistida.
- `frontend-dashboard/src/routes/...` (criar) — tela de personalizações + fluxo assistido + menu.
- regen do client OpenAPI do dashboard.

## Passos
1. Rotas painel (listar/baixar/atualizar status) + tela + menu.
2. Fluxo assistido: criar sessão pela loja + gerar/copiar o **link público**.

## Testes
- **Níveis:** integração.
- **Quando escrever:** durante.
- **Cobrir:** integração — lojista vê só as sessões da própria loja; download por URL assinada; mudar status persiste; criar assistida gera `public_token` válido.

## Definition of Done
- [ ] Lojista vê/baixa/atualiza status das personalizações da loja; cria assistida e obtém o link público.
- [ ] **Modos de falha mapeados** — acesso a sessão de outra loja → 404/403; link assistido sem contato pré-cadastrado → erro. → tratados/Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Visualização **quase em tempo real** = **polling** na V1 (doc [22](../../concepts/22_product_customization_3d.md)); WebSocket fica pra depois.

## Follow-ups
- [ ] **Atualização ao vivo via WebSocket** (em vez de polling) — *Quando:* se a UX exigir. → README da fase.
- [ ] **e2e Playwright** do painel de personalizações — → `P3-SF-03`/infra de e2e do painel. → README da fase.
