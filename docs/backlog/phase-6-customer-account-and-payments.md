# Fase 6 — Dev online na AWS: conta do cliente, pagamentos e monetização

> Roadmap: Etapas 15–18. O sistema **vai para o ar** (ambiente **dev**) em **EC2** e ganha conta do cliente, gateway com split e billing.

Docs de referência: [12](../12_aws_infrastructure_and_deployment.md), [23](../23_customer_identity_and_guest_checkout.md), [11](../11_checkout_payments_and_split.md), [02](../02_business_model_and_rules.md), [08](../08_modules_and_permissions.md), [07](../07_database_strategy.md), [14](../14_security_strategy.md), [18](../18_open_decisions.md), [16](../16_testing_strategy.md).

## Definition of Done da fase

- Sistema **no ar na AWS (EC2)**, em ambiente dev, com domínios/TLS e recebendo webhooks.
- Cliente entra por **código (e-mail/SMS/WhatsApp), senha ou Google**, com **sincronização guest ↔ conta**.
- Área do cliente: histórico, endereços, personalizações, editar perfil (inclui nome).
- Gateway com **split** processa pagamento; **webhook assinado e idempotente** confirma o pedido.
- Planos com **comissão por plano** e gating de recurso por **plano + permissão**.

## Decisões pendentes a fechar nesta fase (registrar em [18](../18_open_decisions.md))

- **Gateway principal:** Pagar.me / Mercado Pago / Asaas (doc [11](../11_checkout_payments_and_split.md)/[18](../18_open_decisions.md)).
- **Provedor de SMS/WhatsApp** para os códigos (ex.: Twilio, Zenvia, API oficial do WhatsApp).
- **Google OAuth** (client id/secret, domínios autorizados).
- **Cobrança da mensalidade:** desde já, manual ou via gateway recorrente (doc [18](../18_open_decisions.md)).

---

## Etapa 15 — Deploy do ambiente dev na AWS (EC2)

> Subir **antes** dos pagamentos: o gateway envia webhooks para uma URL pública. Ambiente **dev online** (não é produção; produção ECS é pós-V1). Doc [12](../12_aws_infrastructure_and_deployment.md).

### Infra
- [ ] Provisionar **EC2** + **Docker Compose** + **Traefik** (mesmo stack do dev local).
- [ ] **RDS PostgreSQL** (single-AZ, backups automáticos). Doc [12](../12_aws_infrastructure_and_deployment.md).
- [ ] **Redis**: container no EC2 ou **ElastiCache**.
- [ ] **S3 + CloudFront** do ambiente online (implementação já existe desde o dev local; apontar para bucket/distribuição do ambiente). Doc [12](../12_aws_infrastructure_and_deployment.md)/[13](../13_performance_cache_and_cdn.md).
- [ ] **Route 53**: `*.loja.club`, `api.`, `app.` (e `admin.` quando a Fase 7 entrar). Doc [06](../06_multitenancy_and_domains.md)/[12](../12_aws_infrastructure_and_deployment.md).
- [ ] **SSL** via Traefik/Let's Encrypt (ACM fica para produção). Doc [12](../12_aws_infrastructure_and_deployment.md).
- [ ] **SES/SMTP real** para os e-mails (substitui o Mailcatcher do dev local). Doc [12](../12_aws_infrastructure_and_deployment.md)/[21](../21_design_system_todo.md).
- [ ] **Não expor** Adminer/Mailcatcher/Traefik dashboard. Doc [04](../04_fastapi_template_adaptation.md)/[14](../14_security_strategy.md).
- [ ] **Segredos** fora do código (env seguro/SSM). Doc [14](../14_security_strategy.md).
- [ ] Compose dedicado do ambiente online (ex.: `compose.aws.yml`) + script de deploy manual (o pipeline automatizado vem na Fase 7/Etapa 21).
- [ ] Health checks acessíveis (`/health`, `/health/db`, `/health/redis`). Doc [15](../15_observability_and_operations.md).

### DoD da etapa
- [ ] Loja pública, painel e API acessíveis por domínio público com HTTPS; webhooks alcançáveis.

**Reconciliação:** ambiente dev online usa **EC2 + Docker Compose + Traefik** (doc [12](../12_aws_infrastructure_and_deployment.md)). ECS/Fargate é **pós-V1**.

---

## Etapa 16 — Conta e login do cliente (extensão do módulo `customers`)

> No MVP o cliente já é identificado por e-mail/telefone (Fase 4). Aqui ele ganha **autenticação** e **área do cliente**. Doc [23](../23_customer_identity_and_guest_checkout.md).

### Modelos (com `store_id`)
- [ ] `customer_auth_identities`: `store_id`, `customer_id`, `provider` (`password|google|code`), `provider_subject` (e-mail/`sub` do Google), `secret_hash?`. Índices `store_id+provider+provider_subject` único e `store_id+customer_id`. Doc [07](../07_database_strategy.md)/[23](../23_customer_identity_and_guest_checkout.md).
- [ ] `customer_verification_codes`: `store_id`, `customer_id`, `channel` (`email|sms|whatsapp`), `code_hash`, `expires_at` (~10 min), `used_at`, `attempts`. Índice `store_id+customer_id+expires_at`. Doc [07](../07_database_strategy.md)/[23](../23_customer_identity_and_guest_checkout.md).

### Autenticação do cliente (separada do `account_users`)
- [ ] Token/sessão de **cliente por loja** (não confundir com o JWT do painel). Reaproveitar hashing de `app/core/security.py`, mas escopo e emissão próprios.
- [ ] **Código (sem senha):** solicitar código por e-mail/telefone → enviar via e-mail/SMS/WhatsApp → verificar → emitir token. Anti brute force + rate limit. Doc [23](../23_customer_identity_and_guest_checkout.md)/[14](../14_security_strategy.md).
- [ ] **Senha:** definir senha opcional; login e-mail + senha.
- [ ] **Google (OAuth):** start + callback; vincular `sub` ao customer.
- [ ] **Sincronização guest ↔ conta:** resolver por e-mail/telefone normalizados (Fase 4); nunca duplicar; ligar identidades ao mesmo `customer_profiles`. Doc [23](../23_customer_identity_and_guest_checkout.md).

### Rotas/serviço (doc [20](../20_api_contracts_todo.md))
- [ ] solicitar código; verificar código; login senha; Google start/callback; logout; `me`.
- [ ] recuperar carrinho/pedido por código (cross-device) — completa o que ficou na Fase 4. Doc [23](../23_customer_identity_and_guest_checkout.md).
- [ ] área do cliente: histórico de pedidos, endereços (CRUD), personalizações, **editar perfil (inclui nome)**. Editar exige autenticação. Doc [23](../23_customer_identity_and_guest_checkout.md).
- [ ] **Ver/aprovar personalização criada pelo lojista:** o cliente loga com o e-mail/telefone pré-cadastrado e **vê/aprova** a personalização que o lojista montou por ele (doc [22](../22_product_customization_3d.md)); aprovar segue o fluxo normal (carrinho/checkout). **Acesso (login vs link público) = decisão em aberto** ([18](../18_open_decisions.md)).

### Frontend (storefront, Next.js)
- [ ] Modal/área de login (código, senha, Google); área do cliente (histórico, endereços, perfil). Doc [05](../05_frontend_architecture.md)/[21](../21_design_system_todo.md).

### Testes (doc [16](../16_testing_strategy.md))
- [ ] sync guest→conta e conta→guest sem duplicar; código expira/limite de tentativas; vínculo Google; editar nome exige login.

**Reconciliação:** a auth do template é só para `account_users`. A auth do cliente é um sistema **novo e separado**, por loja (doc [23](../23_customer_identity_and_guest_checkout.md)/[03](../03_system_architecture.md)). Google OAuth e SMS/WhatsApp exigem libs/serviços não presentes no template.

---

## Etapa 17 — Pagamentos e split (módulo `payments` — NOVO)

Doc [11](../11_checkout_payments_and_split.md), [14](../14_security_strategy.md), [07](../07_database_strategy.md), [02](../02_business_model_and_rules.md).

### Modelos (com `store_id`, salvo webhooks)
- [ ] `payment_accounts`: `store_id`, `gateway`, `gateway_recipient_id`, `status` (`pending|active|blocked|rejected`), `kyc_status`, `metadata`. Doc [11](../11_checkout_payments_and_split.md).
- [ ] `payment_transactions`: `store_id`, `order_id`, `gateway_transaction_id`, `status` (`created|pending|authorized|paid|refused|canceled|refunded|chargeback`), `amount`, `method`, `metadata`. Índice `store_id+gateway_transaction_id`. Doc [07](../07_database_strategy.md).
- [ ] `payment_webhooks`: `gateway_event_id` único, `gateway`, `event_type`, `payload`, `processed_at`, `status` (`received|processed|failed`). Doc [11](../11_checkout_payments_and_split.md).
- [ ] `payment_split_rules` (comissão vinda do plano), `payment_chargebacks`. Doc [07](../07_database_strategy.md).

### Fluxo (doc [11](../11_checkout_payments_and_split.md))
- [ ] Conectar recebedor/subconta da loja no gateway (KYC).
- [ ] No checkout, **substituir o "pagamento combinado" pela criação de transação no gateway** (consumir o ponto de integração preparado na Fase 4). Manter combinado como opção/fallback se a loja quiser.
- [ ] **Split automático** com a comissão do plano (vem do `billing`).
- [ ] **Webhook:** validar assinatura/origem, **idempotência** (`gateway_event_id`), pertencimento à loja, status válido → atualizar transação + pedido. **Requer o sistema no ar (Etapa 15).** Doc [11](../11_checkout_payments_and_split.md)/[14](../14_security_strategy.md).
- [ ] Métodos: Pix, cartão, boleto (parcelado com cuidado). Doc [11](../11_checkout_payments_and_split.md).
- [ ] Reembolso: exige permissão, auditoria, chamada ao gateway, atualizar transação/pedido. Doc [11](../11_checkout_payments_and_split.md).
- [ ] Chargeback: registrar, alertar, bloquear loja com excesso. Doc [11](../11_checkout_payments_and_split.md)/[02](../02_business_model_and_rules.md).

### Frontend (painel — Pagamentos)
- [ ] Conectar conta; status da conta/métodos; transações; problemas; chargebacks; info de repasse (somente exibição — Loja Club não retém dinheiro). Doc [09](../09_merchant_dashboard.md)/[11](../11_checkout_payments_and_split.md).

### Testes (doc [16](../16_testing_strategy.md))
- [ ] split com comissão correta do plano; loja sem conta ativa não vende; assinatura inválida rejeitada; evento duplicado não reprocessa; evento pago atualiza transação e pedido; evento de outra loja não contamina; reembolso exige permissão; chargeback registrado.

**Reconciliação:** **nunca** armazenar cartão; dados sensíveis ficam no gateway (doc [14](../14_security_strategy.md)). A lib do gateway não existe no template.

---

## Etapa 18 — Billing da Loja Club (módulo `billing` — NOVO)

Doc [02](../02_business_model_and_rules.md), [07](../07_database_strategy.md), [08](../08_modules_and_permissions.md), [18](../18_open_decisions.md).

### Modelos
- [ ] `billing_plans` (Free/Starter/Pro/Business — valores a validar, doc [02](../02_business_model_and_rules.md)/[18](../18_open_decisions.md)).
- [ ] `billing_plan_features` (recursos/limites por plano), `billing_store_subscriptions` (`store_id`, `plan`, `status` `active|suspended|canceled`), `billing_subscription_invoices` (mensalidade), `billing_platform_commissions` (`store_id`, `order_id`, valor). Índices `store_id+status`, `store_id+order_id`. Doc [07](../07_database_strategy.md).

### Regras
- [ ] **Gating plano + permissão:** completar o "gancho de plano" deixado na Fase 1 em `require_permission` — recurso disponível exige *plano permite* **e** *usuário tem permissão*. Doc [08](../08_modules_and_permissions.md)/[02](../02_business_model_and_rules.md).
- [ ] **Comissão por plano** alimenta o split do `payments` (Etapa 17). Lojista não configura comissão. Doc [11](../11_checkout_payments_and_split.md).
- [ ] Status de assinatura: ativo/suspenso/cancelado; **bloqueio por inadimplência**. Doc [02](../02_business_model_and_rules.md).
- [ ] Cobrança da mensalidade conforme decisão pendente (manual ou gateway recorrente). Doc [18](../18_open_decisions.md).

### Frontend (painel — Plano)
- [ ] Plano atual, comissão, mensalidade, status, faturas, trocar plano, alerta de inadimplência. Doc [09](../09_merchant_dashboard.md).
- [ ] (Gestão de planos pela Loja Club é no `frontend-admin` — Fase 7.)

### Testes (doc [16](../16_testing_strategy.md))
- [ ] gating por plano; comissão aplicada no split; inadimplência bloqueia recursos/loja.

---

## Reconciliações (registrar aqui)
- (preencher conforme surgirem)
