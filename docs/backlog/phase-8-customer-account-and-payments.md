# Fase 8 — Conta do cliente, pagamentos e monetização (dev local)

> Objetivo: o sistema ganha **conta do cliente**, **gateway com split**, **billing** e a modalidade de **pagamento em 2 etapas** (sinal + saldo na entrega). **Construído e testado local** (webhooks **mockados**); o **go-live na AWS (EC2)** é a **[Fase 9](./phase-9-platform-ops-and-dev-deploy.md)** — onde os webhooks reais passam a ser alcançáveis.

Docs de referência: [23](../concepts/23_customer_identity_and_guest_checkout.md), [11](../concepts/11_checkout_payments_and_split.md), [02](../concepts/02_business_model_and_rules.md), [08](../concepts/08_modules_and_permissions.md), [07](../concepts/07_database_strategy.md), [14](../concepts/14_security_strategy.md), [09](../concepts/09_merchant_dashboard.md), [18](../concepts/18_open_decisions.md), [16](../concepts/16_testing_strategy.md).

## Definition of Done da fase
- Cliente entra por **código (e-mail/SMS/WhatsApp), senha ou Google**, com **sincronização guest ↔ conta**.
- Área do cliente: histórico, endereços, personalizações, editar perfil (inclui nome).
- Gateway com **split** processa pagamento; **webhook assinado e idempotente** confirma o pedido (validado contra **mock** local; real na Fase 9).
- **Pagamento em 2 etapas** (sinal 50% + saldo na entrega): **configurável no painel**, **opção no checkout** e **status próprio** acompanhável por lojista/cliente/admin.
- Planos com **comissão por plano** e gating de recurso por **plano + permissão**.

## Decisões pendentes a fechar nesta fase (registrar em [18](../concepts/18_open_decisions.md))
- **Gateway principal:** Pagar.me / Mercado Pago / Asaas (doc [11](../concepts/11_checkout_payments_and_split.md)/[18](../concepts/18_open_decisions.md)).
- **Provedor de SMS/WhatsApp** para os códigos (ex.: Twilio, Zenvia, API oficial do WhatsApp).
- **Google OAuth** (client id/secret, domínios autorizados).
- **Cobrança da mensalidade:** manual ou via gateway recorrente (doc [18](../concepts/18_open_decisions.md)).
- **Comissão no pagamento em 2 etapas:** sobre o **total** do pedido ou só sobre o que passou no gateway (o **sinal**)? O saldo recebido na entrega não passa pelo split automático.

---

## Etapa 1 — Conta e login do cliente (extensão do módulo `customers`)

> No MVP o cliente já é identificado por e-mail/telefone (Fase 6). Aqui ele ganha **autenticação** e **área do cliente**. Doc [23](../concepts/23_customer_identity_and_guest_checkout.md).

### Modelos (com `store_id`)
- [ ] `customer_auth_identities`: `store_id`, `customer_id`, `provider` (`password|google|code`), `provider_subject` (e-mail/`sub` do Google), `secret_hash?`. Índices `store_id+provider+provider_subject` único e `store_id+customer_id`. Doc [07](../concepts/07_database_strategy.md)/[23](../concepts/23_customer_identity_and_guest_checkout.md).
- [ ] `customer_verification_codes`: `store_id`, `customer_id`, `channel` (`email|sms|whatsapp`), `code_hash`, `expires_at` (~10 min), `used_at`, `attempts`. Índice `store_id+customer_id+expires_at`. Doc [07](../concepts/07_database_strategy.md)/[23](../concepts/23_customer_identity_and_guest_checkout.md).

### Autenticação do cliente (separada do `account_users`)
- [ ] Token/sessão de **cliente por loja** (não confundir com o JWT do painel). Reaproveitar hashing de `app/core/security.py`, mas escopo e emissão próprios.
- [ ] **Código (sem senha):** solicitar código por e-mail/telefone → enviar via e-mail/SMS/WhatsApp → verificar → emitir token. Anti brute force + rate limit. Doc [23](../concepts/23_customer_identity_and_guest_checkout.md)/[14](../concepts/14_security_strategy.md).
- [ ] **Senha:** definir senha opcional; login e-mail + senha.
- [ ] **Google (OAuth):** start + callback; vincular `sub` ao customer.
- [ ] **Sincronização guest ↔ conta:** resolver por e-mail/telefone normalizados (Fase 6); nunca duplicar; ligar identidades ao mesmo `customer_profiles`. Doc [23](../concepts/23_customer_identity_and_guest_checkout.md).

### Rotas/serviço (doc [20](../concepts/20_api_contracts_todo.md))
- [ ] solicitar código; verificar código; login senha; Google start/callback; logout; `me`.
- [ ] recuperar carrinho/pedido por código (cross-device) — completa o que ficou na Fase 6. Doc [23](../concepts/23_customer_identity_and_guest_checkout.md).
- [ ] área do cliente: histórico de pedidos, endereços (CRUD), personalizações, **editar perfil (inclui nome)**. Editar exige autenticação. Doc [23](../concepts/23_customer_identity_and_guest_checkout.md).
- [ ] **Ver/aprovar personalização criada pelo lojista (na conta):** além do **link público + confirmação de contato** já entregue na Fase 7 (doc [30 §9](../concepts/30_3d_customization_technical_design.md)), o cliente **logado** vê/aprova suas personalizações na **área do cliente**; aprovar segue o fluxo normal (carrinho/checkout). Doc [22](../concepts/22_product_customization_3d.md)/[23](../concepts/23_customer_identity_and_guest_checkout.md).

### Frontend (storefront, Next.js)
- [ ] Modal/área de login (código, senha, Google); área do cliente (histórico, endereços, perfil). Doc [05](../concepts/05_frontend_architecture.md)/[21](../concepts/21_design_system_todo.md).

### Testes (doc [16](../concepts/16_testing_strategy.md))
- [ ] sync guest→conta e conta→guest sem duplicar; código expira/limite de tentativas; vínculo Google; editar nome exige login.

**Reconciliação:** a auth do template é só para `account_users`. A auth do cliente é um sistema **novo e separado**, por loja (doc [23](../concepts/23_customer_identity_and_guest_checkout.md)/[03](../concepts/03_system_architecture.md)). Google OAuth e SMS/WhatsApp exigem libs/serviços não presentes no template.

---

## Etapa 2 — Pagamentos e split (módulo `payments` — NOVO)

Doc [11](../concepts/11_checkout_payments_and_split.md), [14](../concepts/14_security_strategy.md), [07](../concepts/07_database_strategy.md), [02](../concepts/02_business_model_and_rules.md).

### Modelos (com `store_id`, salvo webhooks)
- [ ] `payment_accounts`: `store_id`, `gateway`, `gateway_recipient_id`, `status` (`pending|active|blocked|rejected`), `kyc_status`, `metadata`. Doc [11](../concepts/11_checkout_payments_and_split.md).
- [ ] `payment_transactions`: `store_id`, `order_id`, `gateway_transaction_id`, `status` (`created|pending|authorized|paid|refused|canceled|refunded|chargeback`), `amount`, `method`, `kind` (`full|deposit|balance` — ver Etapa 3), `metadata`. Índice `store_id+gateway_transaction_id`. Doc [07](../concepts/07_database_strategy.md).
- [ ] `payment_webhooks`: `gateway_event_id` único, `gateway`, `event_type`, `payload`, `processed_at`, `status` (`received|processed|failed`). Doc [11](../concepts/11_checkout_payments_and_split.md).
- [ ] `payment_split_rules` (comissão vinda do plano), `payment_chargebacks`. Doc [07](../concepts/07_database_strategy.md).

### Fluxo (doc [11](../concepts/11_checkout_payments_and_split.md))
- [ ] Conectar recebedor/subconta da loja no gateway (KYC).
- [ ] No checkout, **substituir o "pagamento combinado" pela criação de transação no gateway** (consumir o ponto de integração preparado na Fase 6 — `payments.get_gateway`). Manter combinado como opção/fallback se a loja quiser.
- [ ] **Split automático** com a comissão do plano (vem do `billing`).
- [ ] **Webhook:** validar assinatura/origem, **idempotência** (`gateway_event_id`), pertencimento à loja, status válido → atualizar transação + pedido. **Construído contra mock local**; o webhook real exige o sistema no ar (**Fase 9**). Doc [11](../concepts/11_checkout_payments_and_split.md)/[14](../concepts/14_security_strategy.md).
- [ ] Métodos: Pix, cartão, boleto (parcelado com cuidado). Doc [11](../concepts/11_checkout_payments_and_split.md).
- [ ] Reembolso: exige permissão, auditoria, chamada ao gateway, atualizar transação/pedido. Doc [11](../concepts/11_checkout_payments_and_split.md).
- [ ] Chargeback: registrar, alertar, bloquear loja com excesso. Doc [11](../concepts/11_checkout_payments_and_split.md)/[02](../concepts/02_business_model_and_rules.md).

### Frontend (painel — Pagamentos)
- [ ] Conectar conta; status da conta/métodos; transações; problemas; chargebacks; info de repasse (somente exibição — Kriar não retém dinheiro). Doc [09](../concepts/09_merchant_dashboard.md)/[11](../concepts/11_checkout_payments_and_split.md).

### Testes (doc [16](../concepts/16_testing_strategy.md))
- [ ] split com comissão correta do plano; loja sem conta ativa não vende; assinatura inválida rejeitada (mock); evento duplicado não reprocessa; evento pago atualiza transação e pedido; evento de outra loja não contamina; reembolso exige permissão; chargeback registrado.

**Reconciliação:** **nunca** armazenar cartão; dados sensíveis ficam no gateway (doc [14](../concepts/14_security_strategy.md)). A lib do gateway não existe no template. O **webhook real** só roda na Fase 9 (precisa de URL pública).

---

## Etapa 3 — Pagamento em 2 etapas (sinal + saldo na entrega — NOVO)

> Modalidade comum no varejo: o cliente paga um **sinal** (ex.: **50%**) agora e o **saldo na entrega**. Tem que ser **configurável pelo lojista**, **aparecer no checkout** e ter **status próprio** pra ficar claro pra **lojista, cliente e admin**.

### Config (painel do lojista)
- [ ] Ativar/desativar a modalidade por loja + **percentual do sinal** (default 50%, configurável). (`store_settings` ou `payment_settings`.) Doc [09](../concepts/09_merchant_dashboard.md).

### Checkout (cliente)
- [ ] Quando ativa, o checkout oferece **"Pagar tudo agora"** ou **"Sinal de X% agora + saldo na entrega"**, mostrando os valores (**sinal R$ A agora**, **saldo R$ B na entrega**). O `order` grava o **plano de pagamento** escolhido.

### Modelo / status (pra todo mundo acompanhar)
- [ ] `order.payment_plan` (`full` | `deposit_balance`) + `deposit_amount_minor` / `balance_amount_minor`. O **sinal** vira uma `payment_transaction` (`kind=deposit`) no gateway (com split); o **saldo** é cobrado/recebido na entrega (`kind=balance`, fora do gateway por padrão → o lojista **marca recebido**, como o mark-paid manual da Fase 6).
- [ ] `order.payment_status` distinto do status operacional: `pending → deposit_paid → paid` (quitado). `deposit_paid` = sinal recebido, **saldo pendente na entrega**.
- [ ] **Visibilidade:**
  - **Cliente** (confirmação + área): "Você pagou o sinal de R$ A; **R$ B na entrega**".
  - **Lojista** (painel/pedido): "Sinal pago R$ A · **saldo R$ B a receber na entrega**" + botão **"Marcar saldo recebido"** → `paid`.
  - **Admin** (`platform_admin`): vê o `payment_plan` + `payment_status` na operação/relatórios.

### Testes (doc [16](../concepts/16_testing_strategy.md))
- [ ] modalidade desativada não aparece no checkout; sinal cobrado no gateway + split correto; `payment_status` evolui `pending→deposit_paid→paid`; "marcar saldo recebido" exige permissão; valores sinal/saldo conferem com o total; isolamento por loja.

**Reconciliação:** a **comissão sobre o saldo** (recebido fora do gateway) é **decisão pendente** (total vs só o sinal) — ver Decisões pendentes.

---

## Etapa 4 — Billing da Kriar (módulo `billing` — NOVO)

Doc [02](../concepts/02_business_model_and_rules.md), [07](../concepts/07_database_strategy.md), [08](../concepts/08_modules_and_permissions.md), [18](../concepts/18_open_decisions.md).

### Modelos
- [ ] `billing_plans` (Free/Starter/Pro/Business — valores a validar, doc [02](../concepts/02_business_model_and_rules.md)/[18](../concepts/18_open_decisions.md)).
- [ ] `billing_plan_features` (recursos/limites por plano), `billing_store_subscriptions` (`store_id`, `plan`, `status` `active|suspended|canceled`), `billing_subscription_invoices` (mensalidade), `billing_platform_commissions` (`store_id`, `order_id`, valor). Índices `store_id+status`, `store_id+order_id`. Doc [07](../concepts/07_database_strategy.md).

### Regras
- [ ] **Gating plano + permissão:** completar o "gancho de plano" deixado na Fase 1 em `require_permission` — recurso disponível exige *plano permite* **e** *usuário tem permissão*. Doc [08](../concepts/08_modules_and_permissions.md)/[02](../concepts/02_business_model_and_rules.md).
- [ ] **Comissão por plano** alimenta o split do `payments` (Etapa 2). Lojista não configura comissão. Doc [11](../concepts/11_checkout_payments_and_split.md).
- [ ] Status de assinatura: ativo/suspenso/cancelado; **bloqueio por inadimplência**. Doc [02](../concepts/02_business_model_and_rules.md).
- [ ] Cobrança da mensalidade conforme decisão pendente (manual ou gateway recorrente). Doc [18](../concepts/18_open_decisions.md).
- [ ] **Personalização 3D restrita a plano pago** (gancho do doc [22](../concepts/22_product_customization_3d.md)): o gating de plano governa quem oferece produtos 3D personalizáveis.

### Frontend (painel — Plano)
- [ ] Plano atual, comissão, mensalidade, status, faturas, trocar plano, alerta de inadimplência. Doc [09](../concepts/09_merchant_dashboard.md).
- [ ] (Gestão de planos pela Kriar é no `frontend-admin` — **Fase 4** `platform_admin`.)

### Testes (doc [16](../concepts/16_testing_strategy.md))
- [ ] gating por plano; comissão aplicada no split; inadimplência bloqueia recursos/loja.

---

## Etapa 5 — Frete por região (completa o `shipping` da Fase 6)
> **Veio da Fase 6** (era o fast-follow `P6-SHIP-02`): além dos métodos MVP da Fase 6 (retirada/combinada/fixo), o frete por **região** (cidade/estado). Entra aqui, quando a loja vende "de verdade" (pagamento + entrega real).

Doc [11 — Entrega combinada](../concepts/11_checkout_payments_and_split.md), [09 — Frete](../concepts/09_merchant_dashboard.md), [07](../concepts/07_database_strategy.md).

### Modelos (com `store_id`)
- [ ] `shipping_zones` (regiões de entrega), `shipping_rates` (tarifa por zona/método — índice `store_id+shipping_method_id`), `shipping_method_rules` (cidade/região/estado + tipo de entrega). Doc [07](../concepts/07_database_strategy.md).

### Regras
- [ ] CRUD no painel (gated `shipping.*`) + **cálculo do frete por região no checkout** (substitui o frete fixo plano quando houver zona/tarifa).
- [ ] **Limitar `private_delivery` por cidade/região/estado** (resolve a permissão `shipping.private_delivery.update`, hoje órfã desde `P6-SHIP-01`).

### Testes (doc [16](../concepts/16_testing_strategy.md))
- [ ] tarifa por região aplicada no checkout; `private_delivery` limitada por região; isolamento por loja; região sem tarifa / endereço fora de cobertura tratados.

---

## Reconciliações (registrar aqui)
- **Deploy/online saiu desta fase** → o go-live na AWS (EC2, dev) é a **[Fase 9](./phase-9-platform-ops-and-dev-deploy.md)**. A Fase 8 é construída **local** (gateway/webhook contra **mock**); por isso a Etapa 2 testa o webhook contra mock e a validação real fica pra Fase 9.
- **Pagamento em 2 etapas** introduz `payment_plan`/`payment_status` no pedido (distintos do status operacional da Fase 6) — registrar o modelo no doc [11](../concepts/11_checkout_payments_and_split.md).
