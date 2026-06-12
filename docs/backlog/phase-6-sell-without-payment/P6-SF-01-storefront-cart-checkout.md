---
id: P6-SF-01
title: Vitrine — carrinho real + checkout/confirmação (3 templates)
phase: 6
etapa: "Etapa 4/5 — Frontend storefront"
area: SF
status: done
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
- Seleção de variação na vitrine: **Fase 7, Etapa 8** (saiu da Fase 6) — aqui vende produto `image` simples.
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
- [x] Carrinho de servidor nos 3 templates (drawer + checkout = mesma fonte).
- [x] Checkout single-page + confirmação (nº pedido + WhatsApp + políticas) nos 3.
- [x] Gates (`tsc`/`biome` + `next build` verdes); e2e do storefront = follow-up (sem Playwright); backend coberto por integração.
- [x] **Modos de falha mapeados** (API fora / estoque some / portão / loja sem método → `cart.error` exibido; sem método → aviso no checkout) → tratados/Follow-ups.
- [x] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Fecha os follow-ups da Fase 3 "ação de compra (carrinho)" + "checkout/confirmação reais".
- **Arquitetura (Server Actions):** `NEXT_PUBLIC_API_URL=backend:8000` é **SSR-only** (o browser não alcança o host interno) + o cookie guest cruza origem. As mutações vão por **Server Actions** (`lib/cart-actions.ts`, "use server"): o Next encaminha o `Host` da loja + o cookie `guest_session_id` ao backend e **re-emite o `Set-Cookie`** do backend ao browser (mesma origem). Isso resolve o round-trip do cookie do `P6-CUST-01`.
- **Implementação:** `lib/cart.tsx` virou provider de **carrinho de servidor** (expõe `items/count/subtotalMinor` render-ready → os 3 headers/drawers ficaram **intactos**); `*AddToCart` + `AuroraProductCard` chamam `cart.add(productId, qty)`.
- **Checkout por template (fiel ao design):** cada template é dono do seu `CheckoutView` (Aurora/Bazar/Studio), fiel ao `docs/design/templates/<nome>/checkout.html` + `order_confirmation.html` — `Checkout` virou membro do contrato `Template` (`lib/template-types.ts`), os 3 `index.ts` o expõem e `app/checkout/page.tsx` renderiza `Template.Checkout` (não mais um import fixo do Aurora). A **lógica é compartilhada** num hook headless `lib/use-checkout.ts` (estado do form, totais a partir do carrinho + frete selecionado, edição de linha do carrinho, `submitCheckout`, fases `empty`/`form`/`done`); só a apresentação muda. Cada view tem o **mesmo conteúdo dos 3 designs** (o dado/fluxo é igual — o template é só a casca): resumo do pedido **editável** (stepper de quantidade + remover, via `cart.setQty/remove`), contato (com seletor de país), **endereço BR completo** (CEP/Rua/Número/Complemento/Bairro/Cidade/Estado), frete dos métodos ativos, políticas da loja e resumo → `submitCheckout` → **confirmação inline** (#nº + botão **WhatsApp** pré-preenchido). Nuance fiel mantida: o Aurora separa **Nome/Sobrenome** (dois inputs → mesmo `name`). `getShippingMethods` (SSR) passado pela página. `CartDrawer` morto removido; rota placeholder `/order-confirmation` removida.
- **Endereço (backend):** o modelo já tinha `line1/line2/city/state/postal_code/country`; adicionadas as colunas **`number`** e **`neighborhood`** em `customer_addresses` + `order_addresses` (migration `f11beee66d67`) para o endereço do design mapear 1:1 (CEP→`postal_code`, Número→`number`, Complemento→`line2`, Bairro→`neighborhood`, UF→`state`). `AddressInput` + dedup (`_same_address`) + snapshot do pedido cobrem os novos campos.

## Follow-ups
- [ ] **e2e + validação de runtime do storefront** — sem infra de Playwright (bloqueio do `P5-SF-01`); o fluxo carrinho/checkout (round-trip do cookie via Server Actions) está validado por `tsc`/`biome`/`next build` + integração no backend, **mas não no browser**. Montar a infra + validar ao vivo (incluindo os **3 checkouts**: Aurora/Bazar/Studio). Origem: `P6-SF-01`.
- [ ] **Cookie `secure`/`domain` em produção** — as Server Actions setam o cookie guest `httpOnly`+`lax` **sem `secure`** (dev http); produção (https) precisa `secure` + decidir `domain`. (Resolve a parte "Set-Cookie via SSR" do follow-up do `P6-CUST-01`; falta o `secure`/`domain`.) Origem: `P6-SF-01`.
- [ ] **Chrome de checkout simplificado** — os designs de `checkout.html`/`order_confirmation.html` usam um header **enxuto** (logo + "voltar à loja"), mas a página usa o `Template.Shell` completo da loja. Decidir se o checkout ganha um chrome próprio (mais foco) ou mantém o Shell. Origem: `P6-SF-01`.
- [x] **Granularidade do endereço** ✅ — endereço BR completo (CEP/Rua/Número/Complemento/Bairro/Cidade/Estado) nos 3 checkouts, com `number`/`neighborhood` adicionados ao backend (migration `f11beee66d67`). Resta só **CEP→autofill** (consulta de CEP) como melhoria futura — cruza com o frete por zona (Fase 8, Etapa 5). Origem: `P6-SF-01`.
- [ ] **Cupom de desconto no checkout** — os 3 designs têm um campo de cupom; deixado de fora aqui (cupom é a `P6-DISC-01`, ainda não construída) para não renderizar input não-funcional. Ligar nos 3 (cada estilo) quando os cupons existirem. Origem: `P6-SF-01` → `P6-DISC-01`.
- [ ] **Recap completo na confirmação** — a confirmação dos designs traz, além de itens + total, um **breakdown** (subtotal/frete) e um **recap de cliente/endereço/entrega** (varia por template, ex.: "Dados do Cliente" no Studio). Hoje a confirmação mostra itens + total + handoff WhatsApp. Completar o recap por template. Origem: `P6-SF-01`.
