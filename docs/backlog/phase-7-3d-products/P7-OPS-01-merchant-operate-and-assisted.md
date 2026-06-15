---
id: P7-OPS-01
title: Painel lojista — operar personalizações + montar assistida
phase: 7
etapa: "Etapa 7 — Painel do lojista: operar as personalizações"
area: OPS
status: done
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
- [x] Lojista vê/baixa/atualiza status das personalizações da loja; cria assistida e obtém o link público.
- [x] **Modos de falha mapeados** — acesso a sessão de outra loja → **404** (`get_session` é store-scoped); atualizar status de sessão **não-pedida** → **422 `not_ordered`**; link assistido sem contato pré-cadastrado → **403** no `/p/{token}/approve` (`P7-SESS-01`). → tratados/Follow-ups.
- [x] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- **Status de produção** = enum `CustomizationProductionStatus` (received…production_done, doc [22](../../concepts/22_product_customization_3d.md)) no **item do pedido** (`customization_order_items.production_status`, começa em `received` no congelamento) — **eixo separado** do `status` da sessão. O lojista avança no painel; uma sessão ainda **não-pedida** dá `not_ordered`.
- **Rotas do painel** (`/stores/{store_id}/customizations`): listar (paginado, polling — `customization.sessions.view`), detalhe com URLs assinadas de snapshot/composite/uploads (`customization.files.download`), atualizar status (`customization.production_status.update`). Assistida (`create_assisted_session`) já existia (`P7-SESS-01`).
- **Visualização quase em tempo real** = **polling** a cada **10 s** ([31 §4](../../concepts/31_configuration_and_constants.md)); WebSocket fica pra depois.
- **Composite é a "arte de produção"** que a gráfica usa (o download principal); o snapshot é a prévia/mockup. Ambos privados (URL assinada).
- **Link da assistida** = `VITE_STOREFRONT_URL` + `/p/{token}` (o token é global, não-scoped); usar o **domínio próprio da loja** é follow-up.

## Follow-ups
- [ ] **Atualização ao vivo via WebSocket** (em vez de polling) — *Quando:* se a UX exigir. → README da fase.
- [ ] **e2e Playwright** do painel de personalizações — → `P3-SF-03`/infra de e2e do painel. → README da fase.
- [ ] **Link da assistida no domínio da loja** (hoje usa `VITE_STOREFRONT_URL` único) — usar o host primário da loja. → README da fase.
- [ ] **Auditoria de acesso do lojista** aos arquivos da personalização (doc [22](../../concepts/22_product_customization_3d.md) §Segurança) — registrar quem baixou/visualizou. → README da fase.
