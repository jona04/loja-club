# Fase 6 — Venda sem pagamento online (dev local)

> Objetivo: a loja recebe **pedidos reais sem gateway** — checkout **sem login**, cliente identificado por e-mail/telefone (dedup), pedido `pending_payment` com **preço congelado + estoque decrementado + número do pedido**, e **pagamento combinado fora da plataforma** (handoff por **WhatsApp**). **Tudo 100% local**; deploy + gateway = **Fase 8**.

Docs de referência: [Fundações & Gargalos](../_foundations-and-bottlenecks.md), [11](../../concepts/11_checkout_payments_and_split.md), [23](../../concepts/23_customer_identity_and_guest_checkout.md), [07](../../concepts/07_database_strategy.md), [10](../../concepts/10_storefront_and_layouts.md), [09](../../concepts/09_merchant_dashboard.md), [22](../../concepts/22_product_customization_3d.md), [16](../../concepts/16_testing_strategy.md), [20](../../concepts/20_api_contracts_todo.md).

> Visão geral / trilha: [`../phase-6-sell-without-payment.md`](../phase-6-sell-without-payment.md). Este README é o **índice detalhado** das tasks.

## Definition of Done da fase
- Cliente compra **sem login**; identificado por e-mail/telefone normalizados (dedup + primeiro-nome-vence).
- Pedido `pending_payment`: **preço congelado** (+ `variant_id`), **estoque decrementado**, **número sequencial por loja**.
- Pagamento **combinado fora da plataforma** (confirmação com **handoff WhatsApp** + msg pré-preenchida); lojista **marca pago manualmente** (nenhum pedido vira pago sozinho).
- Lojista vê o pedido no painel; cliente + lojista recebem e-mail (**Mailcatcher**).
- **100% local** no Docker Compose; **isolamento multi-tenant** testado.

## Sequência (MVP fino primeiro)
> **Núcleo vendável primeiro:** `CAT-01`/`CUST-01`/`SHIP-01` → `CART-01` → `ORD-01` → `CHK-01` → vitrine/painel/e-mails. **Fast-follow:** cupons, frete avançado e seleção de variação. Detalhe na [trilha](../phase-6-sell-without-payment.md#sequência-mvp-fino-primeiro).

## Construído sobre as Fases 0–5 (não recriar)
- **Catálogo + estoque** (`catalog_inventory_items`) — Fase 2; **storefront** (vitrine por Host) + **carrinho client placeholder** (localStorage) — Fase 3.
- **`media`/`storage`** + **`whatsapp_number`** em `store_settings` (Fase 1) + **botão flutuante de WhatsApp** (Fase 3).
- **Worker `arq`** + `app.core.queue.enqueue` (Fase 0) + **`mailcatcher`** no compose (dev) + base `send_email`/MJML do template.
- **Módulos stub** (`orders`/`customers`/`cart`/`checkout`/`shipping`/`discounts`/`notifications`) — só `enums`/`schemas` vazios, prontos para receber models/services/routes.
- **Telas de checkout/confirmação dos 3 templates já desenhadas** (`docs/design/templates/<nome>/`, `P3-TPL-*`) — esta fase as **liga** ao carrinho/pedido.

## Tasks

| # | ID | Task | Status | Depende de |
|---|----|------|--------|-----------|
| 1 | [P6-CAT-01](./P6-CAT-01-product-type-and-cart-gate.md) | Tipo de produto (`type`) + portão do add-to-cart | ✅ done | — |
| 2 | [P6-CUST-01](./P6-CUST-01-customer-identity-dedup.md) | Identidade do cliente + dedup (guest) | ✅ done | — |
| 3 | [P6-SHIP-01](./P6-SHIP-01-shipping-methods.md) | Frete: métodos MVP (retirada/combinada/fixo) | ✅ done | — |
| 4 | [P6-CART-01](./P6-CART-01-server-cart.md) | Carrinho de servidor (`cart_carts`/`cart_items`) | ✅ done | P6-CAT-01 |
| 5 | [P6-ORD-01](./P6-ORD-01-orders-create.md) | Pedidos: módulo + criação (congela/estoque/nº) | ✅ done | P6-CART-01 |
| 6 | [P6-CHK-01](./P6-CHK-01-checkout-flow.md) | Checkout: sessão + fluxo (sem gateway) | ✅ done | P6-CUST-01, P6-CART-01, P6-SHIP-01, P6-ORD-01 |
| 7 | [P6-SF-01](./P6-SF-01-storefront-cart-checkout.md) | Vitrine: carrinho real + checkout/confirmação (3 templates) | ✅ done | P6-CART-01, P6-CHK-01 |
| 8 | [P6-ORD-02](./P6-ORD-02-orders-panel.md) | Painel de pedidos | ✅ done | P6-ORD-01 |
| 9 | [P6-CUST-02](./P6-CUST-02-customers-panel.md) | Painel de clientes | todo | P6-CUST-01 |
| 10 | [P6-NOTIF-01](./P6-NOTIF-01-order-emails.md) | E-mails de pedido (worker) + health + E2E do marco | todo | P6-ORD-01, P6-CHK-01 |
| 11 | [P6-DISC-01](./P6-DISC-01-coupons.md) | Cupons (**fast-follow**) | todo | P6-CART-01 |
| 12 | [P6-SHIP-02](./P6-SHIP-02-shipping-zones.md) | Frete completo: zonas/tarifas/regras (**fast-follow**) | todo | P6-SHIP-01 |
| 13 | [P6-SF-02](./P6-SF-02-storefront-variants.md) | Seleção de variação na vitrine (**fast-follow**) | todo | P6-CART-01 |

## Ordem sugerida de execução

```text
P6-CAT-01 · P6-CUST-01 · P6-SHIP-01            (núcleo, independentes)
   └→ P6-CART-01 → P6-ORD-01 → P6-CHK-01
         ├→ P6-SF-01    (vitrine: carrinho real + checkout/confirmação)
         ├→ P6-ORD-02   (painel de pedidos) · P6-CUST-02 (painel de clientes)
         └→ P6-NOTIF-01 (e-mails no worker + health + E2E do marco)

Fast-follow: P6-DISC-01 (cupons) · P6-SHIP-02 (zonas/tarifas) · P6-SF-02 (variação na vitrine)
```

## Follow-ups / débitos técnicos

> Item adiado vira checkbox aqui (origem + quando), e também na seção Follow-ups da task.

**Esta fase fecha/adianta follow-ups de fases anteriores** (marcar `[x]` na **origem** ao concluir a task):
- [x] **Índice único de estoque** `(store_id, product_id, variant_id)` (Fase 2, `P2-CAT-02`) → `P6-ORD-01` ✅ (único, `nulls_not_distinct` p/ a linha product-level; baixa de estoque confiável).
- [ ] **Vitrine expõe variações + disponibilidade** (Fase 3, `P3-SF-01`/`P3-SF-02`) → `P6-SF-02`.
- [x] **Políticas da loja (troca/devolução/privacidade)** (Fase 1, `checkout.policies.*`) → `P6-CHK-01` ✅ (campos em `store_settings` + rota painel gated `checkout.policies.update` + exposição na vitrine).
- [x] **Carrinho/checkout reais + ação de compra na vitrine** (Fase 3, `P3-TPL-01`/`P3-SF-02`) → `P6-CART-01` (carrinho de servidor) + `P6-SF-01` ✅ (add-to-cart + drawer + checkout single-page + confirmação WhatsApp nos 3 templates).
- [ ] **Editar categorias de um produto** (Fase 3) — não é desta fase; segue aberto.

**Da própria fase:**
- [ ] **`customer_consents` (LGPD)** — não incluído no `P6-CUST-01`; quando precisar registrar consentimento. Origem: `P6-CUST-01`.
- [ ] **Limpeza de guest sessions expiradas** — `expires_at` existe, falta worker que marque/limpe (doc 23 pede `expired`). Origem: `P6-CUST-01`.
- [x] **Set-Cookie via SSR do storefront** — `P6-SF-01` ✅ (Server Actions encaminham host+cookie e re-emitem o `Set-Cookie` ao browser). Falta **`secure`/`domain` em produção** (https) → continua aberto abaixo. Origem: `P6-CUST-01`.
- [ ] **Cookie `secure`/`domain` em produção** — as Server Actions setam o cookie guest `httponly`+`lax` sem `secure` (dev http); prod precisa `secure` + decidir `domain`. Origem: `P6-CUST-01`/`P6-SF-01`.
- [ ] **e2e + validação de runtime do storefront** — sem Playwright (bloqueio do `P5-SF-01`); o fluxo carrinho/checkout (os **3 checkouts** Aurora/Bazar/Studio) está validado por `tsc`/`biome`/`next build` + integração no backend, não no browser. Origem: `P6-SF-01`.
- [x] **Rota `/order-confirmation` placeholder removida** — a confirmação virou inline no `CheckoutView` (de cada template). Origem: `P6-SF-01`.
- [ ] **Chrome de checkout simplificado** — os designs de checkout/confirmação usam um header enxuto (logo + "voltar à loja"); a página usa o `Template.Shell` completo. Decidir se o checkout ganha um chrome próprio. Origem: `P6-SF-01`.
- [x] **Granularidade do endereço** ✅ `P6-SF-01` — endereço BR completo (CEP/Rua/Número/Complemento/Bairro/Cidade/Estado) nos 3 checkouts + colunas `number`/`neighborhood` no backend (migration `f11beee66d67`); resta só CEP→autofill (futuro, cruza com `P6-SHIP-02`).
- [ ] **Cupom de desconto no checkout** — os 3 designs têm campo de cupom; fora de escopo aqui (cupom = `P6-DISC-01`). Ligar nos 3 quando os cupons existirem. Origem: `P6-SF-01` → `P6-DISC-01`.
- [ ] **Recap completo na confirmação** — designs trazem breakdown (subtotal/frete) + recap de cliente/endereço (varia por template); hoje a confirmação mostra itens + total + handoff. Completar por template. Origem: `P6-SF-01`.
- [ ] **e2e Playwright do painel de pedidos** — fluxo "vê pedido → marca pago" coberto por integração + vitest, não por Playwright (falta seedar pedido no e2e). Origem: `P6-ORD-02`.
- [ ] **Exportar pedidos (`orders.export`)** — permissão existe no catálogo, sem rota/botão. Origem: `P6-ORD-02`.
- [x] **Steppers de quantidade + remover no checkout** ✅ `P6-SF-01` — resumo do pedido editável (via `cart.setQty/remove`) nos 3 templates, fiel aos designs.
- [ ] **`shipping.private_delivery.update` órfã** — o CRUD de frete usa `shipping.create/update/delete`; a permissão `shipping.private_delivery.update` não é lida por rota. Virar ação própria (`P6-SHIP-02`) ou remover do catálogo. Origem: `P6-SHIP-01`.
- [ ] **Token seguro p/ continuar a compra (cross-device)** — adiado; recuperação no mesmo navegador já funciona pelo cookie; cross-device cruza com o fluxo de código da Fase 8. Origem: `P6-CART-01`.
- [ ] **N+1 no payload do carrinho** + **snapshot de preço stale** — `to_public` busca produto/imagens por item; preço congelado no add (o pedido re-congela). Origem: `P6-CART-01`.
- [ ] **Corrida de `order_number`** — `max+1` + índice único não duplica, mas concorrência gera `IntegrityError` sem retry. Adicionar retry/lock por loja. Origem: `P6-ORD-01`.
- [ ] **`order_fulfillments` + `order_refunds` adiados** — stub tables não criadas (status do pedido cobre envio; reembolso = Fase 8). Criar quando consumidas. Origem: `P6-ORD-01`.
- [ ] **Limpeza de `checkout_sessions` abandonadas** — sessões `active` que não viram `completed` ficam até `expires_at` sem worker (mesma família do follow-up de guest sessions). Origem: `P6-CHK-01`.
