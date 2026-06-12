---
id: P6-CUST-02
title: Painel de clientes (lista/detalhe/histórico/busca)
phase: 6
etapa: "Etapa 3 — customers (painel)"
area: CUST
status: todo
depends_on: [P6-CUST-01]
blocks: []
tests: [integration, e2e]
---

# P6-CUST-02 — Painel de clientes

## Contexto
O lojista vê quem comprou: lista, detalhe, **histórico de pedidos**, endereços, busca por nome/e-mail/telefone.

## Docs de referência
- [09 — Clientes](../../concepts/09_merchant_dashboard.md)
- [23 — Customer Identity](../../concepts/23_customer_identity_and_guest_checkout.md)

## Escopo (o que ENTRA)
- Rotas/serviço (painel, gated `customers.*`): listar (busca nome/e-mail/telefone), detalhe (perfil + endereços), **histórico de pedidos** do cliente.
- Tela no `frontend-dashboard` (`/_layout/customers`) + menu (gated `customers.view`).

## Fora de escopo (o que NÃO entra)
- Editar perfil do cliente / área do cliente: **Fase 8**.
- Exportar/deletar cliente (LGPD): follow-up se não couber.

## Arquivos a criar/alterar
- `backend/app/modules/customers/routes.py` (alterar) — rotas do painel.
- `frontend-dashboard/src/routes/_layout/customers.tsx` (criar) + `src/lib/menu.ts` (alterar).
- client OpenAPI regenerado.

## Passos
1. Rotas do painel (gated) — lista/busca/detalhe/histórico.
2. Tela + menu.

## Testes
- **Níveis:** integração (gated/busca/isolamento) + e2e (painel).
- **Cobrir:** integração — gating `customers.view`; busca por e-mail/telefone; **isolamento por loja**. e2e — lojista acha o cliente e vê o histórico.

## Definition of Done
- [ ] Rotas gated `customers.*` (lista/busca/detalhe/histórico).
- [ ] Tela + menu (gated `customers.view`).
- [ ] **Modos de falha mapeados** (busca vazia; cliente de outra loja; cliente sem pedidos) → tratados/Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- (preencher ao implementar.)

## Follow-ups
- [ ] — nenhum (preencher ao implementar).
