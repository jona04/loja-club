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
| `billing_plans` | Planos da Loja Club |
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

### Personalização 3D

> **Fase 7 (Produtos 3D).** Os modelos 3D são **gerados pelo lojista via API de terceiros** e ficam **por loja** (`store_id`) — não há biblioteca global da plataforma; `customization_3d_models`/`_versions` têm `store_id`. Ver [Fase 7](backlog/phase-7-3d-products.md).

| Tabela | Função |
|---|---|
| `customization_3d_models` | Modelos 3D do lojista (por loja; gerados via API) |
| `customization_3d_model_versions` | Versões dos arquivos (GLB) e parâmetros do modelo |
| `customization_product_settings` | Configuração de personalização por produto/loja |
| `customization_sessions` | Sessões salvas de personalização do cliente |
| `customization_uploads` | Arquivos enviados pelo cliente |
| `customization_cart_items` | Personalização aprovada no carrinho |
| `customization_order_items` | Cópia congelada da personalização no pedido |

Campos importantes em `customization_sessions`:

```text
store_id
product_id
guest_session_id
customer_id
cart_id
model_id
model_version_id
status
state_json
preview_url
approved_snapshot_url
expires_at
approved_at
```

O `state_json` guarda parâmetros como cor, posição, escala, rotação, imagem aplicada, textos e área utilizada.
O pedido não deve depender da sessão viva: ao criar pedido, copiar a personalização para `customization_order_items`.

Sessões de personalização expiram em 30 dias quando não viram pedido.
Ao expirar, marcar `status = expired` e `deleted_at`, sem hard delete do registro de negócio.

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

### Pagamentos

| Tabela | Função |
|---|---|
| `payment_accounts` | Conta/recebedor do lojista |
| `payment_transactions` | Transações |
| `payment_webhooks` | Eventos recebidos do gateway |
| `payment_split_rules` | Regras de comissão |
| `payment_chargebacks` | Contestação/chargeback |

### Layout e conteúdo

| Tabela | Função |
|---|---|
| `content_theme_templates` | Templates globais |
| `content_store_theme_settings` | Template ativo e configurações |
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

### Billing da Loja Club

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
| `store_role_permissions` | `role + permission` único |
| `domain_hosts` | `host` único quando ativo |
| `domain_hosts` | `store_id + status` |
| `catalog_products` | `store_id + slug` único quando ativo |
| `catalog_products` | `store_id + status` |
| `catalog_products` | `store_id + created_at` |
| `catalog_product_variants` | `store_id + product_id + status` |
| `catalog_product_images` | `store_id + product_id + position` |
| `catalog_categories` | `store_id + slug` único quando ativo |
| `catalog_inventory_items` | `store_id + product_id + variant_id` |
| `customization_product_settings` | `store_id + product_id` único |
| `customization_sessions` | `store_id + product_id + status` |
| `customization_sessions` | `store_id + guest_session_id + status` |
| `customization_sessions` | `store_id + customer_id + status` |
| `customization_sessions` | `expires_at + status` |
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
| `order_items` | `store_id + order_id` |
| `order_status_history` | `store_id + order_id + created_at` |
| `payment_transactions` | `store_id + gateway_transaction_id` |
| `payment_webhooks` | `gateway_event_id` único |
| `shipping_methods` | `store_id + type + is_active` |
| `shipping_rates` | `store_id + shipping_method_id` |
| `discount_coupons` | `store_id + code` único quando ativo |
| `content_pages` | `store_id + slug` único quando ativo |
| `content_menus` | `store_id + location` |
| `content_store_theme_settings` | `store_id` único |
| `billing_store_subscriptions` | `store_id + status` |
| `billing_platform_commissions` | `store_id + order_id` |
| `audit_logs` | `store_id + created_at` |
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
