# Fase 4 — Venda sem pagamento online (dev local)

> Roadmap: Etapas 9–14 + 🚀 Marco. Objetivo: a loja recebe **pedidos reais sem gateway**. Checkout cria pedido `pending_payment`, identifica o cliente por e-mail/telefone (sem login), congela preço e personalização, e o pagamento é combinado fora da plataforma. **Tudo rodando 100% local** (Docker Compose); o deploy na AWS é a Fase 6.

Docs de referência: [07](../07_database_strategy.md), [09](../09_merchant_dashboard.md), [10](../10_storefront_and_layouts.md), [11](../11_checkout_payments_and_split.md), [13](../13_performance_cache_and_cdn.md), [15](../15_observability_and_operations.md), [22](../22_product_customization_3d.md), [23](../23_customer_identity_and_guest_checkout.md), [12](../12_aws_infrastructure_and_deployment.md), [16](../16_testing_strategy.md).

> **Nota:** vender sem pagamento + identidade do cliente é desta fase; a **personalização** (`image_3d_customizable`, congelar arte no pedido) é a **[Fase 5 — Produtos 3D](./phase-5-3d-products.md)**; **pagamentos = Fase 6**.

## Definition of Done da fase (= Critério do MVP, dev local)

- Cliente navega, personaliza, aprova, adiciona ao carrinho e finaliza checkout **sem login**.
- Cliente é **identificado por e-mail/telefone normalizados** com deduplicação e primeiro-nome-vence.
- Pedido criado como `pending_payment`; preço e personalização congelados.
- Lojista vê pedido + arte aprovada no painel; cliente e lojista recebem e-mail (Mailcatcher).
- **Tudo rodando 100% local** no Docker Compose; isolamento multi-tenant testado.

---

## Etapa 9 — Módulo `shipping` (frete) — antes do carrinho

### Modelos (com `store_id`)
- [ ] `shipping_methods`: `type` (`fixed_shipping|free_shipping|local_pickup|private_delivery`), `is_active`, nome, descrição exibida no checkout. Doc [07](../07_database_strategy.md)/[11](../11_checkout_payments_and_split.md).
- [ ] `shipping_zones`, `shipping_rates`, `shipping_method_rules` (cidade/região/estado). Doc [07](../07_database_strategy.md).

### Rotas/serviço (doc [20](../20_api_contracts_todo.md))
- [ ] CRUD de métodos; configurar frete fixo, grátis (valor mínimo), retirada local, entrega combinada; definir regiões; mensagem exibida no checkout.
- [ ] `private_delivery` (entrega combinada): sem cálculo automático; deixa claro no checkout/pedido que a entrega será combinada após a compra. Doc [11](../11_checkout_payments_and_split.md)/[10](../10_storefront_and_layouts.md).
- [ ] Índice `shipping_methods.store_id+type+is_active`. Doc [07](../07_database_strategy.md).

---

## Etapa 9 — Módulo `discounts` (cupons) — antes do carrinho

- [ ] `discount_coupons` (`store_id`, `code` único quando ativo, `type` `percentual|fixo`, validade, limite de uso, pedido mínimo, status). `discount_coupon_redemptions`. Doc [07](../07_database_strategy.md)/[09](../09_merchant_dashboard.md).
- [ ] CRUD + serviço de validação/aplicação (consumido pelo carrinho). Doc [20](../20_api_contracts_todo.md).
- [ ] Índice `discount_coupons.store_id+code` único quando ativo. Doc [07](../07_database_strategy.md).

---

## Etapa 11/13 — Módulo `customers` (identidade + dedup, escopo MVP)

> Apenas guest + dedup nesta fase. Login por código/senha/Google e área do cliente são **Fase 6**. Doc [23](../23_customer_identity_and_guest_checkout.md).

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
- [ ] Recuperação no **mesmo navegador** (cookie). (Recuperação por código fica na Fase 6.)

### Frontend (painel) — Etapa 13
- [ ] **Clientes**: listar, detalhe, histórico de pedidos, endereços, busca por nome/e-mail/telefone. Doc [09](../09_merchant_dashboard.md).

---

## Etapa 10 — Módulo `cart` (carrinho)

### Modelos (com `store_id`)
- [ ] `cart_carts`: `guest_session_id`|`customer_id`, `status`; índices `store_id+guest_session_id+status`, `store_id+customer_id+status`. Doc [07](../07_database_strategy.md).
- [ ] `cart_items`; `customization_cart_items` (liga item à sessão de personalização aprovada; único por `cart_item`). Doc [07](../07_database_strategy.md)/[22](../22_product_customization_3d.md).

### Rotas/serviço (doc [20](../20_api_contracts_todo.md))
- [ ] Criar carrinho; recuperar por sessão anônima; recuperar por token seguro; adicionar item; **adicionar item personalizado** (exige sessão `approved`); alterar quantidade; remover; aplicar cupom; resumo (subtotal); validar estoque. Doc [11](../11_checkout_payments_and_split.md)/[10](../10_storefront_and_layouts.md).
- [ ] Regra: item `customizable_3d` só entra com `customization_session.status == approved`. Doc [11](../11_checkout_payments_and_split.md)/[22](../22_product_customization_3d.md).
- [ ] Token seguro para continuar compra (aleatório, expira, escopado à loja). Doc [23](../23_customer_identity_and_guest_checkout.md).

### Frontend (storefront)
- [ ] Página de carrinho: itens, quantidades, subtotal, cupom, frete estimado, método de entrega, **preview da personalização**, botão checkout. Doc [10](../10_storefront_and_layouts.md).

---

## Etapa 11 — Módulo `checkout`

### Modelo
- [ ] `checkout_sessions`: `store_id`, `cart_id`, `status`, `expires_at` (≈24h). Índices `store_id+cart_id+status`, `expires_at+status`. Doc [07](../07_database_strategy.md)/[23](../23_customer_identity_and_guest_checkout.md).

### Fluxo (doc [11](../11_checkout_payments_and_split.md)/[23](../23_customer_identity_and_guest_checkout.md)/[22](../22_product_customization_3d.md))
- [ ] Coletar dados do cliente (nome, e-mail, telefone, **seletor de país** para o telefone) sem senha.
- [ ] `create_or_update_customer` (dedup) + endereço.
- [ ] Selecionar método de entrega (inclui `private_delivery` com aviso).
- [ ] Revisão; validar estoque, valores e personalizações aprovadas.
- [ ] Criar **pedido `pending_payment`**; **congelar preços**; **congelar personalização** em `customization_order_items` (modelo, versão, JSON, arte original, preview, snapshot, data). Doc [11](../11_checkout_payments_and_split.md)/[22](../22_product_customization_3d.md).
- [ ] **Pagamento combinado fora da plataforma**: mensagem pós-compra explicando como será combinado (Pix/transferência/WhatsApp/entrega combinada).
- [ ] **Preparar o ponto de integração do gateway** (interface no `payments`, sem implementar) para a Fase 6. Doc [17](../17_v1_roadmap.md).
- [ ] Não exigir senha/cadastro. Doc [11](../11_checkout_payments_and_split.md).

### Frontend (storefront)
- [ ] Páginas de checkout (dados, endereço, entrega, revisão, confirmação) nos 2 templates. Doc [10](../10_storefront_and_layouts.md).

---

## Etapa 12 — Módulo `orders` (pedidos)

### Modelos (com `store_id`)
- [ ] `order_orders`: status (`draft|pending_payment|paid|payment_failed|processing|shipped|delivered|canceled|refunded|chargeback`), total, frete, desconto, método de entrega, `customer_id`, `guest_session_id`. Doc [07](../07_database_strategy.md)/[11](../11_checkout_payments_and_split.md).
- [ ] `order_items`; `customization_order_items` (congelada); `order_addresses`; `order_status_history`; `order_notes`; `order_fulfillments` (básico); `order_refunds` (stub). Doc [07](../07_database_strategy.md).
- [ ] Índices: `store_id+created_at`, `store_id+status`, `store_id+customer_id`, `order_items.store_id+order_id`, `order_status_history.store_id+order_id+created_at`. Doc [07](../07_database_strategy.md).

### Rotas/serviço + Frontend (painel) — doc [09](../09_merchant_dashboard.md)/[22](../22_product_customization_3d.md)
- [ ] Lista (filtro por status/data), detalhe, cliente, itens, **personalização aprovada por item**, arquivos enviados (download via URL assinada), **status de arte/produção**, notas internas, alterar status operacional.
- [ ] **Marcar pagamento recebido manualmente** (enquanto não há gateway). Doc [17](../17_v1_roadmap.md).
- [ ] Cancelar quando permitido. (Reembolso real fica para a Fase 6.)
- [ ] Lojista não altera arte aprovada sem nova aprovação; pedido preserva o que o cliente confirmou. Doc [09](../09_merchant_dashboard.md)/[22](../22_product_customization_3d.md).

---

## Etapa 14 — Notificações essenciais + finalização local

> Reaproveitar a base de e-mail do template (`app/utils.py` `send_email` + MJML em `app/email-templates/`). No **dev local**, e-mails caem no **Mailcatcher**; SES/SMTP real entra na Fase 6. Doc [21](../21_design_system_todo.md)/[15](../15_observability_and_operations.md).

- [ ] Template + envio: **pedido criado** (cliente).
- [ ] Template + envio: **novo pedido** (lojista).
- [ ] Disparo assíncrono via fila (lib da Fase 0). Doc [13](../13_performance_cache_and_cdn.md).
- [ ] Health checks `/health`, `/health/db`, `/health/redis` no ambiente **local**. Doc [15](../15_observability_and_operations.md).
- [ ] Validar o **fluxo completo de ponta a ponta** no Docker Compose local (E2E do marco).

---

## Deploy → Fase 6

> **O deploy na AWS não é desta fase.** Toda a Fase 4 roda **local**. Subir o sistema na AWS (EC2) é a **Fase 6** — ver [phase-6-customer-account-and-payments.md](./phase-6-customer-account-and-payments.md).

---

## Etapa 9–14 — Testes (doc [16](../16_testing_strategy.md))
- [ ] Compra sem login; carrinho recuperado no mesmo navegador; recuperação por token.
- [ ] **Dedup**: mesmo e-mail/telefone cai no mesmo customer; primeiro-nome-vence; conflito resolve por e-mail.
- [ ] Carrinho cria pedido `pending_payment`; **preço congelado**; **personalização congelada**; alteração posterior da sessão não muda o pedido.
- [ ] Estoque validado; item `customizable_3d` exige sessão aprovada.
- [ ] Pedido não vira pago sozinho (sem gateway: fica `pending_payment` até marcação manual).
- [ ] Isolamento multi-tenant em pedidos/clientes/carrinhos.
- [ ] E2E do fluxo completo do marco (criar conta → loja → produto → 3D → carrinho → checkout → pedido → painel). Doc [16](../16_testing_strategy.md).

---

## Reconciliações (registrar aqui)
- (preencher conforme surgirem)
