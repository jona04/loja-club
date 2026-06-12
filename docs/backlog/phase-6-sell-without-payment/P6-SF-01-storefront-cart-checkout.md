---
id: P6-SF-01
title: Vitrine — carrinho real + checkout/confirmação (3 templates)
phase: 6
etapa: "Etapa 4/5 — Frontend storefront"
area: SF
status: todo
depends_on: [P6-CART-01, P6-CHK-01]
blocks: []
tests: [e2e]
---

# P6-SF-01 — Vitrine: carrinho real + checkout/confirmação

## Contexto
Liga a vitrine ao backend: o carrinho client (localStorage) passa a ler o **carrinho de servidor**; o produto ganha **ação de compra**; e o **checkout single-page + confirmação** (já desenhados) ficam funcionais nos 3 templates.

## Docs de referência
- [10 — Carrinho / Checkout](../../concepts/10_storefront_and_layouts.md)
- [11 — Venda sem gateway](../../concepts/11_checkout_payments_and_split.md)

## Escopo (o que ENTRA)
- **Add-to-cart real** na página de produto (os `*AddToCart` dos 3 templates passam a chamar o backend) + **drawer** lê o carrinho de servidor (mesma fonte do checkout).
- **Checkout single-page** (itens + contato c/ seletor de país + endereço + entrega + políticas + resumo) nos 3 templates (Aurora/Bazar/Studio).
- **Confirmação** com **número do pedido** + **botão de WhatsApp** (mensagem pré-preenchida: pedido + itens, `whatsapp_number`) + políticas.

## Fora de escopo (o que NÃO entra)
- Seleção de variação na vitrine: `P6-SF-02` (fast-follow) — aqui vende produto `image` simples.
- Editor de personalização: **Fase 7**.

## Arquivos a criar/alterar
- `frontend-storefront/lib/cart.tsx` (alterar) — passa a usar o carrinho de servidor.
- `frontend-storefront/components/CartDrawer.tsx`, `templates/*/CheckoutView.tsx`, `templates/*/*AddToCart.tsx` (alterar).
- `frontend-storefront/app/checkout/page.tsx`, `app/order-confirmation/...` (alterar).
- `frontend-storefront/lib/api.ts` (alterar) — endpoints de cart/checkout.

## Passos
1. `lib/cart.tsx` → carrinho de servidor (cookie guest) + drawer.
2. Add-to-cart real nos 3 templates.
3. Checkout single-page + confirmação (nº pedido + WhatsApp + políticas) nos 3.

## Testes
- **Níveis:** e2e (Playwright do storefront — montar infra; ver follow-up `P5-SF-01`).
- **Quando escrever:** depois.
- **Cobrir:** e2e — adicionar ao carrinho → checkout sem login → pedido criado → confirmação com nº + WhatsApp. (Se a infra de e2e do storefront não estiver pronta, cobrir por integração no backend + validação manual; registrar follow-up.)

## Definition of Done
- [ ] Carrinho de servidor nos 3 templates (drawer + checkout = mesma fonte).
- [ ] Checkout single-page + confirmação (nº pedido + WhatsApp + políticas) nos 3.
- [ ] Gates (`tsc`/`biome`) + e2e (ou integração + manual com follow-up de e2e).
- [ ] **Modos de falha mapeados** (API fora; estoque some no checkout; loja sem método de entrega) → tratados/Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Fecha os follow-ups da Fase 3 "ação de compra (carrinho)" + "checkout/confirmação reais".
- **Bloqueio conhecido:** storefront sem infra de Playwright (follow-up `P5-SF-01`) — se persistir, o e2e do marco vira follow-up e a cobertura fica em integração no backend.

## Follow-ups
- [ ] — nenhum (preencher ao implementar).
