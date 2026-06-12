---
id: P6-CUST-02
title: Painel de clientes (lista/detalhe/histórico/busca)
phase: 6
etapa: "Etapa 3 — customers (painel)"
area: CUST
status: done
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
- [x] Rotas gated `customers.*` (lista/busca/detalhe/histórico).
- [x] Tela + menu (gated `customers.view`).
- [x] **Modos de falha mapeados** (busca vazia → lista normal; cliente de outra loja → 404; cliente sem pedidos → `orders: []`) → tratados/Follow-ups.
- [x] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- **Backend:** rotas `/stores/{id}/customers` (`customers/routes.py`, novo) — `GET` lista `Page[CustomerSummary]` (busca `?search=` case-insensitive em nome/e-mail/telefone via `or_`+`ilike`, newest-first) + `GET /{id}` `CustomerDetail` (perfil + endereços salvos + **histórico de pedidos**); ambas gated `customers.view`. Serviços `list_customers`/`get_customer` em `customers/services.py`; schemas novos (`CustomerSummary`/`CustomerAddressPublic`/`CustomerOrderRow`/`CustomerDetail`).
- **Direção de dependência preservada:** o histórico de pedidos fica em `orders.services.list_orders_by_customer` (orders já depende de customers); a **rota** de customers compõe perfil+endereços (customers) + histórico (orders) — `customers.services` **não** importa orders.
- **Frontend:** `routes/_layout/customers.tsx` (lista + campo de busca + diálogo de detalhe: perfil/WhatsApp + endereços + tabela de histórico) + entrada "Clientes" no `menu.ts` (gated `customers.view`). Client regenerado (`CustomersService`). Teste de componente `customers.test.tsx` (lista + detalhe com endereço/histórico).
- **Read-only nesta fase:** editar perfil / área do cliente = Fase 8 (doc 09/23).

## Follow-ups
- [ ] **e2e Playwright do painel de clientes** — fluxo (achar cliente → ver histórico) coberto por integração (backend) + componente (vitest), **não** por Playwright. Origem: `P6-CUST-02`.
- [ ] **Busca por telefone formatado** — o telefone é guardado em E.164 (`+5586…`); a busca faz `ilike` no valor cru, então "(86)" ou espaços **não** casam. Normalizar o termo de busca (só dígitos → casar `phone_e164`) quando precisar. Origem: `P6-CUST-02`.
- [ ] **`customers.export` / `customers.delete` (LGPD)** — permissões existem no catálogo, sem rota/UI; exportar/anonimizar cliente = follow-up (cruza com `customer_consents` do `P6-CUST-01`). Origem: `P6-CUST-02`.
- [ ] **Contagem de pedidos na lista** — a lista não mostra nº de pedidos por cliente (evita acoplar `customers`→`orders` no list); a contagem aparece só no detalhe (tamanho do histórico). Adicionar à lista se o lojista pedir. Origem: `P6-CUST-02`.
