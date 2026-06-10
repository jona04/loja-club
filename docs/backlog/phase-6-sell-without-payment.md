# Fase 6 — Venda sem pagamento online (dev local)

> Objetivo: a loja recebe **pedidos reais sem gateway**. Checkout cria pedido `pending_payment`, identifica o cliente por e-mail/telefone (sem login), congela o preço, e o pagamento é combinado fora da plataforma. **Tudo rodando 100% local** (Docker Compose); o deploy na AWS é a Fase 8.

Docs de referência: [07](../07_database_strategy.md), [09](../09_merchant_dashboard.md), [10](../10_storefront_and_layouts.md), [11](../11_checkout_payments_and_split.md), [13](../13_performance_cache_and_cdn.md), [15](../15_observability_and_operations.md), [22](../22_product_customization_3d.md), [23](../23_customer_identity_and_guest_checkout.md), [12](../12_aws_infrastructure_and_deployment.md), [16](../16_testing_strategy.md).

> **Nota:** vender sem pagamento + identidade do cliente é desta fase, com **produtos de imagem**. Toda a **personalização** (`image_3d_customizable`: sessões, editor 3D e **congelar a arte no carrinho/pedido**) é a **[Fase 7 — Produtos 3D](./phase-7-3d-products.md)**, que **estende** o carrinho/checkout/pedido daqui; **pagamentos = Fase 8**.

## Definition of Done da fase (= Critério do MVP, dev local)

- Cliente navega, adiciona ao carrinho e finaliza checkout **sem login**.
- Cliente é **identificado por e-mail/telefone normalizados** com deduplicação e primeiro-nome-vence.
- Pedido criado como `pending_payment`; preço congelado.
- Lojista vê o pedido no painel; cliente e lojista recebem e-mail (Mailcatcher).
- **Tudo rodando 100% local** no Docker Compose; isolamento multi-tenant testado.

---

## Etapa 1 — Módulo `shipping` (frete) — antes do carrinho

### Modelos (com `store_id`)
- [ ] `shipping_methods`: `type` (`fixed_shipping|free_shipping|local_pickup|private_delivery`), `is_active`, nome, descrição exibida no checkout. Doc [07](../07_database_strategy.md)/[11](../11_checkout_payments_and_split.md).
- [ ] `shipping_zones`, `shipping_rates`, `shipping_method_rules` (cidade/região/estado). Doc [07](../07_database_strategy.md).

### Rotas/serviço (doc [20](../20_api_contracts_todo.md))
- [ ] CRUD de métodos; configurar frete fixo, grátis (valor mínimo), retirada local, entrega combinada; definir regiões; mensagem exibida no checkout.
- [ ] `private_delivery` (entrega combinada): sem cálculo automático; deixa claro no checkout/pedido que a entrega será combinada após a compra. Doc [11](../11_checkout_payments_and_split.md)/[10](../10_storefront_and_layouts.md).
- [ ] Índice `shipping_methods.store_id+type+is_active`. Doc [07](../07_database_strategy.md).

---

## Etapa 2 — Módulo `discounts` (cupons) — antes do carrinho

- [ ] `discount_coupons` (`store_id`, `code` único quando ativo, `type` `percentual|fixo`, validade, limite de uso, pedido mínimo, status). `discount_coupon_redemptions`. Doc [07](../07_database_strategy.md)/[09](../09_merchant_dashboard.md).
- [ ] CRUD + serviço de validação/aplicação (consumido pelo carrinho). Doc [20](../20_api_contracts_todo.md).
- [ ] Índice `discount_coupons.store_id+code` único quando ativo. Doc [07](../07_database_strategy.md).

---

## Etapa 3 — Módulo `customers` (identidade + dedup, escopo MVP)

> Apenas guest + dedup nesta fase. Login por código/senha/Google e área do cliente são **Fase 8**. Doc [23](../23_customer_identity_and_guest_checkout.md).

### Modelos (com `store_id`)
- [ ] `customer_profiles`: `store_id`, `name`, `email` (normalizado), `phone_e164`, timestamps, soft delete. Índices únicos `store_id+email` e `store_id+phone_e164` quando existirem. Doc [23](../23_customer_identity_and_guest_checkout.md)/[07](../07_database_strategy.md).
- [ ] `customer_addresses` (vários por customer), `customer_consents` (LGPD), `customer_guest_sessions` (`guest_session_id` único, `store_id+expires_at`). Doc [07](../07_database_strategy.md)/[23](../23_customer_identity_and_guest_checkout.md).

### Normalização e dedup (doc [23](../23_customer_identity_and_guest_checkout.md))
- [ ] Util de **e-mail**: trim + minúsculas (não remover pontos nem `+tag`).
- [ ] Util de **telefone → E.164** via lib `phonenumbers` (libphonenumber): país vem do seletor (região ISO 3166); a lib valida e devolve E.164 para **qualquer país** (sem `+55`/DDD hard-coded). Ver doc [23](../23_customer_identity_and_guest_checkout.md). Ex. ilustrativos: `BR (86) 99999-0000 → +5586999990000`, `US (415) 555-0132 → +14155550132`.
- [ ] `create_or_update_customer(store_id, name, email, phone, address)`: match por **e-mail** → senão **phone_e164** → senão cria. **Primeiro-nome-vence** (não sobrescreve `name`). Preencher e-mail/telefone faltante só se não pertencer a outro customer. **Conflito** (e-mail de um, telefone de outro): vence o e-mail, não rouba contato alheio. Doc [23](../23_customer_identity_and_guest_checkout.md).
- [ ] Endereço novo → novo `customer_addresses` (não duplicar idêntico). Doc [23](../23_customer_identity_and_guest_checkout.md).

### Guest sessions
- [ ] Cookie HTTP-only `guest_session_id`; criar/recuperar/renovar; vincular ao customer no checkout; validade 30 dias. Doc [23](../23_customer_identity_and_guest_checkout.md).
- [ ] Recuperação no **mesmo navegador** (cookie). (Recuperação por código fica na Fase 8.)

### Frontend (painel) — Etapa 3
- [ ] **Clientes**: listar, detalhe, histórico de pedidos, endereços, busca por nome/e-mail/telefone. Doc [09](../09_merchant_dashboard.md).

---

## Etapa 4 — Módulo `cart` (carrinho)

### Modelos (com `store_id`)
- [ ] `cart_carts`: `guest_session_id`|`customer_id`, `status`; índices `store_id+guest_session_id+status`, `store_id+customer_id+status`. Doc [07](../07_database_strategy.md).
- [ ] `cart_items`. (O `customization_cart_items` — liga o item à sessão de personalização aprovada — é da **[Fase 7](./phase-7-3d-products.md)**.) Doc [07](../07_database_strategy.md).

### Rotas/serviço (doc [20](../20_api_contracts_todo.md))
- [ ] Criar carrinho; recuperar por sessão anônima; recuperar por token seguro; adicionar item; alterar quantidade; remover; aplicar cupom; resumo (subtotal); validar estoque. Doc [11](../11_checkout_payments_and_split.md)/[10](../10_storefront_and_layouts.md).

> Itens **personalizáveis** (`image_3d_customizable`, exigem sessão `approved`) estendem o carrinho na **[Fase 7](./phase-7-3d-products.md)** — não entram aqui.
- [ ] Token seguro para continuar compra (aleatório, expira, escopado à loja). Doc [23](../23_customer_identity_and_guest_checkout.md).

### Frontend (storefront)
- [ ] **Mini-carrinho (drawer)**: itens, quantidades, subtotal, botão "finalizar compra" → checkout. (Não há página de carrinho separada — os itens também aparecem no topo do checkout single-page.) Doc [10](../10_storefront_and_layouts.md).

---

## Etapa 5 — Módulo `checkout`

### Modelo
- [ ] `checkout_sessions`: `store_id`, `cart_id`, `status`, `expires_at` (≈24h). Índices `store_id+cart_id+status`, `expires_at+status`. Doc [07](../07_database_strategy.md)/[23](../23_customer_identity_and_guest_checkout.md).

### Fluxo (doc [11](../11_checkout_payments_and_split.md)/[23](../23_customer_identity_and_guest_checkout.md)/[22](../22_product_customization_3d.md))
- [ ] Coletar dados do cliente (nome, e-mail, telefone, **seletor de país** para o telefone) sem senha.
- [ ] `create_or_update_customer` (dedup) + endereço.
- [ ] Selecionar método de entrega (inclui `private_delivery` com aviso).
- [ ] Revisão; validar estoque e valores.
- [ ] Criar **pedido `pending_payment`**; **congelar preços**. (O **congelamento de personalização** em `customization_order_items` é da **[Fase 7](./phase-7-3d-products.md)**.) Doc [11](../11_checkout_payments_and_split.md).
- [ ] **Pagamento combinado fora da plataforma**: mensagem pós-compra explicando como será combinado (Pix/transferência/WhatsApp/entrega combinada).
- [ ] **Preparar o ponto de integração do gateway** (interface no `payments`, sem implementar) para a Fase 8. Doc [17](../17_v1_roadmap.md).
- [ ] Não exigir senha/cadastro. Doc [11](../11_checkout_payments_and_split.md).

### Frontend (storefront)
- [ ] Checkout **single-page** (itens + contato c/ seletor de país + endereço + entrega + resumo) + **confirmação**, **nos 3 templates** (Aurora/Bazar/Studio) — designs prontos em `docs/design/templates/<nome>/` (`P3-TPL-*`); o **drawer** de mini-carrinho vem dos templates. Doc [10](../10_storefront_and_layouts.md)/[11](../11_checkout_payments_and_split.md).

---

## Etapa 6 — Módulo `orders` (pedidos)

### Modelos (com `store_id`)
- [ ] `order_orders`: status (`draft|pending_payment|paid|payment_failed|processing|shipped|delivered|canceled|refunded|chargeback`), total, frete, desconto, método de entrega, `customer_id`, `guest_session_id`. Doc [07](../07_database_strategy.md)/[11](../11_checkout_payments_and_split.md).
- [ ] `order_items`; `order_addresses`; `order_status_history`; `order_notes`; `order_fulfillments` (básico); `order_refunds` (stub). (O `customization_order_items` — personalização congelada — é da **[Fase 7](./phase-7-3d-products.md)**.) Doc [07](../07_database_strategy.md).
- [ ] Índices: `store_id+created_at`, `store_id+status`, `store_id+customer_id`, `order_items.store_id+order_id`, `order_status_history.store_id+order_id+created_at`. Doc [07](../07_database_strategy.md).

### Rotas/serviço + Frontend (painel) — doc [09](../09_merchant_dashboard.md)/[22](../22_product_customization_3d.md)
- [ ] Lista (filtro por status/data), detalhe, cliente, itens, notas internas, alterar status operacional.
- [ ] **Marcar pagamento recebido manualmente** (enquanto não há gateway). Doc [17](../17_v1_roadmap.md).
- [ ] Cancelar quando permitido. (Reembolso real fica para a Fase 8.)

---

## Etapa 7 — Notificações essenciais + finalização local

> Reaproveitar a base de e-mail do template (`app/utils.py` `send_email` + MJML em `app/email-templates/`), **mas o envio roda no worker** (task `send_email` enfileirada via `enqueue()`, INV-F5) — nunca inline. No **dev local**, e-mails caem no **Mailcatcher**; SES/SMTP real entra na Fase 8. Doc [21](../21_design_system_todo.md)/[15](../15_observability_and_operations.md).

- [ ] Template + envio: **pedido criado** (cliente).
- [ ] Template + envio: **novo pedido** (lojista).
- [ ] Envio **no worker** (task `send_email` enfileirada, INV-F5), com retry. Doc [13](../13_performance_cache_and_cdn.md).
- [ ] Health checks `/health`, `/health/db`, `/health/redis` no ambiente **local**. Doc [15](../15_observability_and_operations.md).
- [ ] Validar o **fluxo completo de ponta a ponta** no Docker Compose local (E2E do marco).

---

## Deploy → Fase 8

> **O deploy na AWS não é desta fase.** Toda a Fase 6 roda **local**. Subir o sistema na AWS (EC2) é a **Fase 8** — ver [phase-8-customer-account-and-payments.md](./phase-8-customer-account-and-payments.md).

---

## Testes (doc [16](../16_testing_strategy.md))
- [ ] Compra sem login; carrinho recuperado no mesmo navegador; recuperação por token.
- [ ] **Dedup**: mesmo e-mail/telefone cai no mesmo customer; primeiro-nome-vence; conflito resolve por e-mail.
- [ ] Carrinho cria pedido `pending_payment`; **preço congelado**.
- [ ] Estoque validado.
- [ ] Pedido não vira pago sozinho (sem gateway: fica `pending_payment` até marcação manual).
- [ ] Isolamento multi-tenant em pedidos/clientes/carrinhos.
- [ ] E2E do fluxo completo do marco (criar conta → loja → produto → carrinho → checkout → pedido → painel). Doc [16](../16_testing_strategy.md).

---

## Reconciliações (registrar aqui)
- **Telas dos templates (checkout/confirmação) já desenhadas (Fase 3):** os 3 templates (Aurora/Bazar/Studio) têm **checkout single-page + confirmação** em `docs/design/templates/<nome>/` (`P3-TPL-*`). A Fase 3 porta a **navegação** (home/categoria/produto); esta fase **liga** checkout/confirmação ao carrinho/pedido. **Carrinho = drawer** (mini-carrinho), não página separada.
- **Personalização movida para a Fase 7:** sessões, editor 3D e o **congelamento da arte no carrinho/pedido** (`customization_cart_items`/`customization_order_items`, a regra "item `image_3d_customizable` só entra com sessão `approved`", preview/arte/status de produção no painel) eram leftover de antes do pivô. A Fase 6 vende **produtos de imagem**; a [Fase 7](./phase-7-3d-products.md) **estende** carrinho/checkout/pedido com a personalização.
