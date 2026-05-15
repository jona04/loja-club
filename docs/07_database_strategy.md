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

Exemplos:

| Tabela | Função |
|---|---|
| `users` | Usuários da plataforma |
| `plans` | Planos da Loja Club |
| `platform_settings` | Configurações globais |
| `theme_templates` | Templates globais disponíveis |
| `product_3d_models` | Modelos 3D globais criados pela Loja Club |
| `product_3d_model_versions` | Versões dos modelos 3D |
| `feature_flags` | Flags de recursos |
| `platform_admin_roles` | Papéis globais internos |

## Tabelas por loja

Tabelas comerciais devem ter `store_id`.

Exemplos:

| Tabela | Tem `store_id`? |
|---|---|
| `store_members` | Sim |
| `domains` | Sim |
| `store_settings` | Sim |
| `products` | Sim |
| `product_variants` | Sim |
| `categories` | Sim |
| `product_images` | Sim |
| `product_customization_settings` | Sim |
| `product_customization_sessions` | Sim |
| `product_customization_uploads` | Sim |
| `inventory_items` | Sim |
| `customers` | Sim |
| `customer_addresses` | Sim |
| `carts` | Sim |
| `cart_items` | Sim |
| `cart_item_customizations` | Sim |
| `orders` | Sim |
| `order_items` | Sim |
| `order_item_customizations` | Sim |
| `payment_accounts` | Sim |
| `payment_transactions` | Sim |
| `shipping_zones` | Sim |
| `shipping_methods` | Sim |
| `shipping_rates` | Sim |
| `shipping_method_rules` | Sim |
| `coupons` | Sim |
| `pages` | Sim |
| `menus` | Sim |
| `store_theme_settings` | Sim |
| `media_files` | Sim |

## Tabelas principais

### Identidade e lojas

| Tabela | Função |
|---|---|
| `users` | Usuários que acessam a plataforma |
| `stores` | Lojas/tenants |
| `store_members` | Ligação usuário-loja |
| `store_roles` | Papéis por loja |
| `store_permissions` | Permissões disponíveis |
| `store_member_permissions` | Permissões customizadas, se necessário |
| `domains` | Domínios/subdomínios |
| `store_settings` | Configurações da loja |

### Catálogo

| Tabela | Função |
|---|---|
| `products` | Produto principal |
| `product_variants` | Variações |
| `product_images` | Imagens do produto |
| `categories` | Categorias |
| `product_categories` | Produto/categoria |
| `inventory_items` | Estoque |
| `collections` | Vitrines/coleções |

### Personalização 3D

| Tabela | Função |
|---|---|
| `product_3d_models` | Biblioteca global de modelos 3D da Loja Club |
| `product_3d_model_versions` | Versões dos arquivos e parâmetros do modelo |
| `product_customization_settings` | Configuração de personalização por produto/loja |
| `product_customization_sessions` | Sessões salvas de personalização do cliente |
| `product_customization_uploads` | Arquivos enviados pelo cliente |
| `cart_item_customizations` | Personalização aprovada no carrinho |
| `order_item_customizations` | Cópia congelada da personalização no pedido |

Campos importantes em `product_customization_sessions`:

```text
store_id
product_id
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

O `state_json` guarda parâmetros como cor, posição, escala, rotação, imagem aplicada e área utilizada.
O pedido não deve depender da sessão viva: ao criar pedido, copiar a personalização para `order_item_customizations`.

### Cliente final

| Tabela | Função |
|---|---|
| `customers` | Clientes da loja |
| `customer_addresses` | Endereços |
| `customer_consents` | Consentimentos LGPD |

### Carrinho e checkout

| Tabela | Função |
|---|---|
| `carts` | Carrinho |
| `cart_items` | Itens do carrinho |
| `checkout_sessions` | Sessões de checkout |

### Pedidos

| Tabela | Função |
|---|---|
| `orders` | Pedido principal |
| `order_items` | Itens comprados |
| `order_item_customizations` | Personalização congelada no item |
| `order_addresses` | Endereço de entrega/cobrança |
| `order_status_history` | Histórico do pedido |
| `order_notes` | Notas internas |
| `fulfillments` | Entrega/envio |
| `refunds` | Reembolsos |

### Pagamentos

| Tabela | Função |
|---|---|
| `payment_accounts` | Conta/recebedor do lojista |
| `payment_transactions` | Transações |
| `payment_webhooks` | Eventos recebidos do gateway |
| `split_rules` | Regras de comissão |
| `chargebacks` | Contestação/chargeback |

### Layout e conteúdo

| Tabela | Função |
|---|---|
| `theme_templates` | Templates globais |
| `store_theme_settings` | Template ativo e configurações |
| `pages` | Páginas da loja |
| `menus` | Menus |
| `menu_items` | Itens do menu |
| `banners` | Banners |

### Frete e cupons

| Tabela | Função |
|---|---|
| `shipping_zones` | Regiões de entrega |
| `shipping_methods` | Métodos de entrega |
| `shipping_rates` | Taxas de frete |
| `shipping_method_rules` | Regras por cidade/região e tipo de entrega |
| `coupons` | Cupons |
| `coupon_redemptions` | Uso dos cupons |

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
| `plans` | Planos |
| `plan_features` | Recursos por plano |
| `store_subscriptions` | Assinatura da loja |
| `subscription_invoices` | Cobranças da mensalidade |
| `platform_commissions` | Comissões por venda |

### Auditoria

| Tabela | Função |
|---|---|
| `audit_logs` | Ações críticas |
| `login_events` | Logins |
| `security_events` | Eventos de segurança |

## Índices essenciais

A performance depende muito dos índices compostos com `store_id`.

| Tabela | Índice recomendado |
|---|---|
| `domains` | `host` único |
| `products` | `store_id + slug` |
| `products` | `store_id + status` |
| `products` | `store_id + created_at` |
| `product_customization_settings` | `store_id + product_id` |
| `product_customization_sessions` | `store_id + product_id + status` |
| `product_customization_sessions` | `store_id + customer_id + status` |
| `order_item_customizations` | `store_id + order_id` |
| `categories` | `store_id + slug` |
| `customers` | `store_id + email` |
| `orders` | `store_id + created_at` |
| `orders` | `store_id + status` |
| `orders` | `store_id + customer_id` |
| `carts` | `store_id + customer_id` |
| `payment_transactions` | `store_id + gateway_transaction_id` |
| `payment_webhooks` | `gateway_event_id` único |
| `shipping_methods` | `store_id + type + is_active` |
| `store_members` | `store_id + user_id` único |
| `media_files` | `store_id + id` |

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
- migrations precisam rodar em staging antes de produção;
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
