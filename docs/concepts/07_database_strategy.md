# Database Strategy

## Banco principal

O banco principal será PostgreSQL.

A estratégia da V1 será:

```text
PostgreSQL compartilhado + store_id nas tabelas comerciais
```

Não haverá banco separado por loja na V1.

## Por que banco compartilhado

Vantagens:

- mais simples;
- mais barato;
- mais fácil de migrar;
- mais fácil de operar;
- bom para MVP/V1;
- permite crescimento inicial sem complexidade excessiva.

Desvantagens:

- exige disciplina absoluta no filtro por `store_id`;
- exige bons índices;
- exige cuidado com queries globais;
- pode exigir particionamento no futuro.

## Tabelas globais

Tabelas globais não pertencem a uma loja específica.

## Padrão de nomes

Toda tabela deve ter prefixo do domínio.

Exemplos:

```text
account_users
store_members
catalog_products
shipping_methods
customization_sessions
order_orders
```

Evitar nomes soltos como `users`, `products`, `orders` ou `domains`.
O nome da tabela deve indicar o contexto antes de abrir relacionamentos.

Exemplos:

| Tabela | Função |
|---|---|
| `account_users` | Usuários da plataforma |
| `billing_plans` | Planos da Kriar |
| `platform_settings` | Configurações globais |
| `content_theme_templates` | Templates globais disponíveis |
| `feature_flags` | Flags de recursos |
| `platform_admin_roles` | Papéis globais internos |

## Tabelas por loja

Tabelas comerciais devem ter `store_id`.

Exemplos:

| Tabela | Tem `store_id`? |
|---|---|
| `store_members` | Sim |
| `domain_hosts` | Sim |
| `store_settings` | Sim |
| `catalog_products` | Sim |
| `catalog_product_variants` | Sim |
| `catalog_categories` | Sim |
| `catalog_product_images` | Sim |
| `customization_product_settings` | Sim |
| `customization_sessions` | Sim |
| `customization_uploads` | Sim |
| `catalog_inventory_items` | Sim |
| `customer_profiles` | Sim |
| `customer_addresses` | Sim |
| `customer_guest_sessions` | Sim |
| `cart_carts` | Sim |
| `cart_items` | Sim |
| `customization_cart_items` | Sim |
| `order_orders` | Sim |
| `order_items` | Sim |
| `customization_order_items` | Sim |
| `payment_accounts` | Sim |
| `payment_transactions` | Sim |
| `shipping_zones` | Sim |
| `shipping_methods` | Sim |
| `shipping_rates` | Sim |
| `shipping_method_rules` | Sim |
| `discount_coupons` | Sim |
| `content_pages` | Sim |
| `content_menus` | Sim |
| `content_menu_items` | Sim |
| `content_store_theme_settings` | Sim |
| `content_store_template_settings` | Sim |
| `content_banners` | Sim |
| `media_files` | Sim |

## Tabelas principais

### Identidade e lojas

| Tabela | Função |
|---|---|
| `account_users` | Usuários que acessam dashboard/admin |
| `store_stores` | Lojas/tenants |
| `store_members` | Ligação usuário-loja |
| `store_roles` | Papéis por loja |
| `store_permissions` | Permissões disponíveis |
| `store_role_permissions` | Mapa papel→permissões (positivo) |
| `store_member_permissions` | Permissões customizadas, se necessário |
| `domain_hosts` | Domínios/subdomínios da loja |
| `store_settings` | Configurações da loja |

### Catálogo

| Tabela | Função |
|---|---|
| `catalog_products` | Produto principal |
| `catalog_product_variants` | Variações |
| `catalog_product_images` | Imagens do produto |
| `catalog_categories` | Categorias |
| `catalog_product_categories` | Produto/categoria |
| `catalog_inventory_items` | Estoque |
| `catalog_collections` | Vitrines/coleções |

`catalog_products` tem um **`type`** (`image|image_3d|image_3d_customizable`, default `image`) — nasce na **Fase 6** (todo produto é `image`) e gateia o add-to-cart (`image_3d_customizable` exige sessão `approved`); o modelo 3D + editor são a **Fase 7**. Ver [22 — Tipo de produto](./22_product_customization_3d.md).

### Personalização 3D

> **Fase 7 (Produtos 3D).** Há **dois tipos de modelo**: o **catálogo da plataforma** (`platform_3d_models`/`_versions`, **sem `store_id`**, populado por **seed**; o lojista **escolhe** — Fase 7) e os **modelos gerados pelo lojista** (`customization_3d_models`/`_versions`, **por loja** `store_id`, gerados via API — **[Fase 12](../backlog/phase-12-merchant-3d-generation.md)**). Ver [Fase 7](../backlog/phase-7-3d-products.md).

| Tabela | Função |
|---|---|
| `platform_3d_models` | Catálogo público de modelos 3D da plataforma (sem `store_id`; via seed; **Fase 7**) |
| `platform_3d_model_versions` | Versões (GLB) + áreas/limites dos modelos do catálogo |
| `customization_3d_models` | Modelos 3D **do lojista** (por loja; gerados via API; **Fase 12**) |
| `customization_3d_model_versions` | Versões dos arquivos (GLB) e parâmetros do modelo da loja |
| `customization_product_settings` | Vínculo produto → modelo (do catálogo ou da loja) + config de personalização |
| `customization_sessions` | Sessões salvas de personalização do cliente |
| `customization_uploads` | Arquivos enviados pelo cliente |
| `customization_cart_items` | Personalização aprovada no carrinho |
| `customization_order_items` | Cópia congelada da personalização no pedido |

Campos do **catálogo da plataforma** (Fase 7, **sem `store_id`**) — detalhe e JSONs no doc [30](./30_3d_customization_technical_design.md):

- `platform_3d_models`: `name`, `category`, `slug`, `is_active` (+ soft delete).
- `platform_3d_model_versions`: `model_id` (FK), `version` (int), `glb_url` (CDN), `printable_areas` (JSON — **região de UV** + limites por área; a arte é mapeada pela UV do modelo, colando na superfície real), `text_config` (JSON — fontes/limites de texto), `art_limits` (JSON — mimes/tamanho/dimensão mín), `is_active`. **GLB imutável** (novo GLB = nova versão); **área/limites editáveis no admin** dentro da versão.

Campos importantes em `customization_sessions`:

```text
store_id
product_id
guest_session_id
customer_id
platform_3d_model_version_id   # versão fixada do catálogo (Fase 12 acrescenta o modelo da loja)
status
state_json
snapshot_key                   # mockup 3D, privado (URL assinada); copiado pro pedido; é a imagem do carrinho
composite_key                  # arte de produção (retângulo achatado, alta-res), privado; copiado pro pedido
created_by_user_id             # usuário da loja na personalização assistida (senão nulo)
public_token                   # link público read-only da assistida (token opaco; ver doc 30 §9)
expires_at
approved_at
```

O `state_json` guarda as **camadas** (imagem e texto), posição/escala/rotação e a área usada — schema canônico no doc [30 §4](./30_3d_customization_technical_design.md) (a **cor do produto** fica fora da V1).
O vínculo com carrinho/pedido **não** fica na sessão: a personalização aprovada é copiada para `customization_cart_items` e, no pedido, para `customization_order_items` (congelamento — **P7-ORD-01**), pra o pedido não depender da sessão viva. O `customization_order_items` carrega ainda o **`production_status`** (`CustomizationProductionStatus`, [31 §7](./31_configuration_and_constants.md)): o **eixo operacional de produção** (começa em `received`), avançado pelo lojista no painel (**P7-OPS-01**) — separado do `status` da sessão.

Sessões de personalização expiram em 30 dias quando não viram pedido (TTL + agendamento da varredura em [31 §4](./31_configuration_and_constants.md)).
Ao expirar, marcar `status = expired` e `deleted_at`, sem hard delete do registro de negócio. A expiração é aplicada **também no acesso** (uma sessão vencida responde **410** em autosave/upload/aprovar/link público); o worker só faz a **faxina** (tira das listagens), então a regra não depende da hora em que ele roda.

### Cliente final

| Tabela | Função |
|---|---|
| `customer_profiles` | Clientes finais da loja (chaves: `email` normalizado e `phone_e164`) |
| `customer_addresses` | Endereços (vários por customer) |
| `customer_auth_identities` | Credenciais de login do cliente: senha e Google/OAuth |
| `customer_verification_codes` | Códigos de uso único (e-mail/SMS/WhatsApp) para recuperação e login |
| `customer_consents` | Consentimentos LGPD |
| `customer_guest_sessions` | Sessões anônimas de carrinho/personalização |

O `customer_profiles` guarda o e-mail normalizado e o `phone_e164` como chaves de identidade/deduplicação por loja.
O nome segue a regra de primeiro-nome-vence (ver [Customer Identity and Guest Checkout](./23_customer_identity_and_guest_checkout.md)).
Login por código, senha ou Google sincroniza no mesmo customer via `customer_auth_identities`.

### Carrinho e checkout

| Tabela | Função |
|---|---|
| `cart_carts` | Carrinho |
| `cart_items` | Itens do carrinho |
| `checkout_sessions` | Sessões de checkout |

`cart_items` guarda o **`variant_id`** quando o produto comprado tiver variação (a vitrine seleciona a variação na página de produto). `cart_carts` guarda o **`coupon_code`** aplicado (validado contra `discount_coupons` no carrinho/checkout; o desconto é recalculado a cada render).

### Pedidos

| Tabela | Função |
|---|---|
| `order_orders` | Pedido principal |
| `order_items` | Itens comprados |
| `customization_order_items` | Personalização congelada no item |
| `order_addresses` | Endereço de entrega/cobrança |
| `order_status_history` | Histórico do pedido |
| `order_notes` | Notas internas |
| `order_fulfillments` | Entrega/envio |
| `order_refunds` | Reembolsos |

`order_orders` tem um **`order_number` sequencial por loja** (`store_id + order_number` único) — referência que cliente e lojista usam (confirmação/e-mail/painel). `order_items` congela preço **e** `variant_id` na compra. Criar o pedido **decrementa** `catalog_inventory_items`; **cancelar** devolve o estoque (ver [11 — Venda sem gateway](./11_checkout_payments_and_split.md)).

### Pagamentos

| Tabela | Função |
|---|---|
| `payment_accounts` | Conta/recebedor do lojista no provider ativo |
| `payment_transactions` | Transações |
| `payment_webhooks` | Eventos recebidos do provider |
| `payment_split_rules` | Regras de comissão |
| `payment_chargebacks` | Contestação/chargeback |

`payment_accounts` deve nascer multi-provider, mesmo que a Fase 8 implemente só `asaas_baas`.

Campos importantes:

```text
store_id
provider                 # asaas_baas | mercado_pago | ...
mode                     # native | connected
provider_account_id
provider_wallet_id       # quando o provider tiver carteira/wallet
status                   # pending | active | blocked | rejected
kyc_status
capabilities             # JSON cacheado para a UX do painel
external_dashboard_url
provider_credentials_ref # referência segura para API key/token, não o segredo em texto puro
metadata
```

O histórico de transações preserva o provider usado no momento da venda. Trocar o provider ativo da loja não reescreve pedidos antigos.

### Layout e conteúdo

| Tabela | Função |
|---|---|
| `content_theme_templates` | Templates globais (+ `settings_schema` do template, vindo do código) |
| `content_store_theme_settings` | Template ativo + configurações universais (banner/headline/cor) |
| `content_store_template_settings` | Valores do `settings_schema` **por loja × template** (jsonb, soft delete) |
| `content_pages` | Páginas da loja |
| `content_menus` | Menus |
| `content_menu_items` | Itens do menu |
| `content_banners` | Banners |

### Frete e cupons

| Tabela | Função |
|---|---|
| `shipping_zones` | Regiões de entrega |
| `shipping_methods` | Métodos de entrega |
| `shipping_rates` | Taxas de frete |
| `shipping_method_rules` | Regras por cidade/região e tipo de entrega |
| `discount_coupons` | Cupons |
| `discount_coupon_redemptions` | Uso dos cupons |

Tipos iniciais de método de entrega:

```text
fixed_shipping
free_shipping
local_pickup
private_delivery
```

O tipo `private_delivery` representa entrega combinada entre cliente e loja.
Ele deve permitir regras por cidade, região ou estado, mas não precisa calcular automaticamente preço ou prazo na V1.

### Billing da Kriar

| Tabela | Função |
|---|---|
| `billing_plans` | Planos |
| `billing_plan_features` | Recursos por plano |
| `billing_store_subscriptions` | Assinatura da loja |
| `billing_subscription_invoices` | Cobranças da mensalidade |
| `billing_platform_commissions` | Comissões por venda |

### Auditoria

| Tabela | Função |
|---|---|
| `audit_logs` | Ações críticas |
| `account_login_events` | Logins |
| `audit_security_events` | Eventos de segurança |

## Soft delete

Não deve existir hard delete em registros de negócio.

Regra:

```text
deleted_at
deleted_by_user_id
delete_reason
```

Quando uma ação for **exclusão**, é **soft delete** (`deleted_at`) — nunca hard delete, **nunca via status**. Status (`archived`/`paused`/`inactive`/`expired`) são **operacionais** (recurso fora do ar, reversível, expirado), **não** exclusão.

Exemplos:

- produto **deletado** = soft-delete (`deleted_at`); `archived` é um **status offline reversível**, não delete;
- loja **deletada** = soft delete (`deleted_at`); offline reversível = `paused`;
- cupom **deletado** = soft delete (`deleted_at`);
- membro removido recebe `removed_at`;
- sessão expirada vira `expired`;
- domínio **deletado** = soft delete (`deleted_at`); `inactive` = desativado (não é exclusão).

Arquivos binários temporários sem valor de auditoria podem ser removidos do storage conforme política de retenção, mantendo o registro de histórico no banco.

## Índices completos iniciais

A performance depende muito dos índices compostos com `store_id`.

| Tabela | Índice recomendado |
|---|---|
| `account_users` | `email` único |
| `store_stores` | `slug` único quando ativo |
| `store_members` | `store_id + user_id` único quando ativo |
| `store_members` | `store_id + status` |
| `store_roles` | `key` único |
| `store_permissions` | `key` único |
| `store_role_permissions` | `role + permission` único |
| `store_settings` | `store_id` único |
| `platform_admin_roles` | `user_id + role` único |
| `domain_hosts` | `host` único quando ativo |
| `domain_hosts` | `store_id + status` |
| `catalog_products` | `store_id + slug` único quando ativo |
| `catalog_products` | `store_id + status` |
| `catalog_products` | `store_id + created_at` |
| `catalog_product_variants` | `store_id + product_id + status` |
| `catalog_product_images` | `store_id + product_id + position` |
| `catalog_categories` | `store_id + slug` único quando ativo |
| `catalog_product_categories` | `product_id + category_id` único |
| `catalog_inventory_items` | `store_id + product_id + variant_id` **único** |
| `catalog_collections` | `store_id + slug` único quando ativo |
| `platform_3d_models` | `slug` único quando ativo |
| `platform_3d_models` | `category` |
| `platform_3d_model_versions` | `model_id + version` único |
| `customization_product_settings` | `store_id + product_id` único |
| `customization_sessions` | `store_id + product_id + status` |
| `customization_sessions` | `store_id + guest_session_id + status` |
| `customization_sessions` | `store_id + customer_id + status` |
| `customization_sessions` | `expires_at + status` |
| `customization_sessions` | `public_token` único quando existir |
| `customization_uploads` | `store_id + customization_session_id` |
| `customization_cart_items` | `store_id + cart_item_id` único |
| `customization_order_items` | `store_id + order_id` |
| `customization_order_items` | `store_id + order_item_id` único |
| `customer_profiles` | `store_id + email` único quando email existir |
| `customer_profiles` | `store_id + phone_e164` único quando phone existir |
| `customer_auth_identities` | `store_id + provider + provider_subject` único |
| `customer_auth_identities` | `store_id + customer_id` |
| `customer_verification_codes` | `store_id + customer_id + expires_at` |
| `customer_guest_sessions` | `guest_session_id` único |
| `customer_guest_sessions` | `store_id + expires_at` |
| `cart_carts` | `store_id + guest_session_id + status` |
| `cart_carts` | `store_id + customer_id + status` |
| `cart_items` | `store_id + cart_id` |
| `checkout_sessions` | `store_id + cart_id + status` |
| `checkout_sessions` | `expires_at + status` |
| `order_orders` | `store_id + created_at` |
| `order_orders` | `store_id + status` |
| `order_orders` | `store_id + customer_id` |
| `order_orders` | `store_id + order_number` único |
| `order_items` | `store_id + order_id` |
| `order_status_history` | `store_id + order_id + created_at` |
| `payment_transactions` | `store_id + provider + gateway_transaction_id` |
| `payment_webhooks` | `provider + gateway_event_id` único |
| `shipping_methods` | `store_id + type + is_active` |
| `shipping_rates` | `store_id + shipping_method_id` |
| `discount_coupons` | `store_id + code` único quando ativo |
| `content_pages` | `store_id + slug` único quando ativo |
| `content_menus` | `store_id + location` |
| `content_menu_items` | `store_id + menu_id + position` |
| `content_banners` | `store_id + position` |
| `content_store_theme_settings` | `store_id` único |
| `content_store_template_settings` | `store_id + template_id` único quando ativo |
| `billing_plans` | `key` único quando ativo |
| `billing_store_subscriptions` | `store_id + status` |
| `billing_platform_commissions` | `store_id + order_id` |
| `audit_logs` | `store_id + created_at` |
| `audit_logs` | `user_id + created_at` |
| `account_login_events` | `user_id + created_at` |
| `media_files` | `store_id + id` |
| `media_files` | `store_id + owner_type + owner_id` |

## Regras de query

1. Nunca buscar recurso comercial só por ID.
2. Sempre usar `store_id` junto.
3. Paginar listas.
4. Não fazer filtros em memória quando o banco pode filtrar.
5. Não carregar relações pesadas sem necessidade.
6. Separar consultas de leitura pública das consultas administrativas.
7. Evitar joins desnecessários na loja pública.
8. Usar cache para dados pouco mutáveis.
9. Congelar personalização aprovada no item do pedido.
10. Não depender de sessão editável para reproduzir pedido já criado.

## Status de pedido

Status sugeridos:

| Status | Significado |
|---|---|
| `draft` | Pedido em construção |
| `pending_payment` | Aguardando pagamento |
| `paid` | Pago |
| `payment_failed` | Pagamento recusado |
| `processing` | Em preparação |
| `shipped` | Enviado |
| `delivered` | Entregue |
| `canceled` | Cancelado |
| `refunded` | Reembolsado |
| `chargeback` | Contestação |

## Status de pagamento

| Status | Significado |
|---|---|
| `created` | Transação criada |
| `pending` | Aguardando confirmação |
| `authorized` | Autorizado |
| `paid` | Pago |
| `refused` | Recusado |
| `canceled` | Cancelado |
| `refunded` | Reembolsado |
| `chargeback` | Contestação |

## Migrações

Alembic será usado para migrações.

Regras:

- toda alteração de schema deve gerar migration;
- migrations precisam rodar em dev antes de produção;
- não fazer alterações manuais em produção;
- criar índices junto com a feature;
- evitar migrations destrutivas sem plano de rollback.

## Futuro

Quando crescer, considerar:

- read replicas;
- particionamento por `store_id` ou data em tabelas grandes;
- arquivamento de logs antigos;
- banco analítico separado;
- isolamento especial para lojas grandes;
- filas dedicadas para webhooks/pagamentos.
