# Modules and Permissions

## Decisão principal

O painel do lojista será dividido em módulos. Cada módulo terá permissões próprias.

Essa decisão resolve três necessidades:

1. organizar a experiência do lojista;
2. permitir controle de acesso por usuário;
3. permitir bloqueio de funcionalidades por plano.

A V1 também terá personalização 3D de produtos.
Esse módulo deve ser controlado por plano e permissão, porque será um diferencial importante para brindes, gráficas e comunicação visual.

## Tipos de identidade

Existem três grupos diferentes:

| Tipo | Descrição | Acesso |
|---|---|---|
| Admin Loja Club | Equipe interna da plataforma | `frontend-admin` |
| Lojista/equipe | Usuários que operam uma loja | `frontend-dashboard` |
| Cliente final | Comprador da loja | `frontend-storefront` |

Admins e lojistas usam `account_users`.
Clientes finais usam `customer_profiles` e podem comprar sem login.

## Modelo de usuários da loja

Um `account_user` pode gerenciar várias lojas.

Uma loja pode ter vários usuários.

Modelo conceitual:

```text
AccountUser
Store
StoreMember
Role
Permission
```

## AccountUser

Representa a pessoa que acessa a plataforma.

Exemplo:

```text
email: joao@empresa.com
```

## Store

Representa a loja/tenant.

Exemplo:

```text
name: Brindes Fortaleza
slug: brindesfortaleza
```

## StoreMember

Liga um usuário a uma loja.

Exemplo:

```text
user_id: 10
store_id: 123
role: admin
```

Com isso, o mesmo usuário pode ser:

```text
Owner na Loja A
Manager na Loja B
Support na Loja C
```

## Papéis padrão

As regras devem ser positivas: cada papel recebe uma lista explícita de permissões.
Tudo que não estiver na lista do papel é bloqueado.

Papéis iniciais:

- `owner`;
- `admin`;
- `manager`;
- `support`;
- `catalog`;
- `marketing`.

## Módulos do painel

| Módulo | Permissão base |
|---|---|
| Dashboard | `dashboard.view` |
| Produtos | `catalog.view` |
| Pedidos | `orders.view` |
| Personalizações | `customization.view` |
| Clientes | `customers.view` |
| Checkout | `checkout.view` |
| Pagamentos | `payments.view` |
| Frete | `shipping.view` |
| Layout | `layout.view` |
| Cupons | `discounts.view` |
| Relatórios | `reports.view` |
| Domínios | `domains.view` |
| Equipe | `team.view` |
| Configurações | `settings.view` |
| Plano | `billing.view` |

## Permissões granulares

### Dashboard

```text
dashboard.view
```

### Produtos

```text
catalog.product.view
catalog.product.create
catalog.product.update
catalog.product.archive
catalog.inventory.update
catalog.category.manage
catalog.product_customization.update
```

### Personalizações

```text
customization.view
customization.sessions.view
customization.files.download
customization.production_status.update
customization.models.assign
```

### Pedidos

```text
orders.view
orders.update_status
orders.cancel
orders.refund
orders.add_note
orders.export
```

### Clientes

```text
customers.view
customers.update
customers.export
customers.archive
```

### Checkout

```text
checkout.view
checkout.update
checkout.policies.update
```

### Pagamentos

```text
payments.view
payments.connect_account
payments.update_methods
payments.view_transactions
payments.manage_refunds
```

### Layout

```text
layout.view
layout.preview
layout.update
layout.assets.update
```

### Frete

```text
shipping.view
shipping.create
shipping.update
shipping.archive
shipping.private_delivery.update
```

### Cupons

```text
discounts.view
discounts.create
discounts.update
discounts.archive
```

### Relatórios

```text
reports.view
reports.export
reports.financial.view
```

### Domínios

```text
domains.view
domains.create
domains.update
domains.verify
domains.archive
```

### Equipe

```text
team.view
team.invite
team.update_role
team.remove
```

### Billing

```text
billing.view
billing.update_plan
billing.view_invoices
```

### Configurações

```text
settings.view
settings.update
settings.archive_store
```

## Permissões por papel da loja

### Owner

O `owner` tem todas as permissões de loja:

```text
dashboard.view
catalog.view
catalog.product.view
catalog.product.create
catalog.product.update
catalog.product.archive
catalog.inventory.update
catalog.category.manage
catalog.product_customization.update
customization.view
customization.sessions.view
customization.files.download
customization.production_status.update
customization.models.assign
orders.view
orders.update_status
orders.cancel
orders.refund
orders.add_note
orders.export
customers.view
customers.update
customers.export
customers.archive
checkout.view
checkout.update
checkout.policies.update
payments.view
payments.connect_account
payments.update_methods
payments.view_transactions
payments.manage_refunds
layout.view
layout.preview
layout.update
layout.assets.update
shipping.view
shipping.create
shipping.update
shipping.archive
shipping.private_delivery.update
discounts.view
discounts.create
discounts.update
discounts.archive
reports.view
reports.export
reports.financial.view
domains.view
domains.create
domains.update
domains.verify
domains.archive
team.view
team.invite
team.update_role
team.remove
billing.view
billing.update_plan
billing.view_invoices
settings.view
settings.update
settings.archive_store
```

### Admin

```text
dashboard.view
catalog.view
catalog.product.view
catalog.product.create
catalog.product.update
catalog.product.archive
catalog.inventory.update
catalog.category.manage
catalog.product_customization.update
customization.view
customization.sessions.view
customization.files.download
customization.production_status.update
customization.models.assign
orders.view
orders.update_status
orders.cancel
orders.add_note
orders.export
customers.view
customers.update
customers.export
checkout.view
checkout.update
checkout.policies.update
payments.view
payments.update_methods
payments.view_transactions
layout.view
layout.preview
layout.update
layout.assets.update
shipping.view
shipping.create
shipping.update
shipping.archive
shipping.private_delivery.update
discounts.view
discounts.create
discounts.update
discounts.archive
reports.view
reports.export
domains.view
domains.create
domains.update
domains.verify
team.view
team.invite
team.update_role
billing.view
billing.view_invoices
settings.view
settings.update
```

### Manager

```text
dashboard.view
catalog.view
catalog.product.view
catalog.product.create
catalog.product.update
catalog.inventory.update
catalog.category.manage
customization.view
customization.sessions.view
customization.files.download
customization.production_status.update
orders.view
orders.update_status
orders.add_note
orders.export
customers.view
customers.update
customers.export
checkout.view
payments.view
payments.view_transactions
shipping.view
discounts.view
discounts.create
discounts.update
reports.view
reports.export
settings.view
```

### Support

```text
dashboard.view
customization.view
customization.sessions.view
orders.view
orders.update_status
orders.add_note
customers.view
checkout.view
shipping.view
settings.view
```

### Catalog

```text
dashboard.view
catalog.view
catalog.product.view
catalog.product.create
catalog.product.update
catalog.product.archive
catalog.inventory.update
catalog.category.manage
catalog.product_customization.update
customization.view
customization.sessions.view
customization.models.assign
layout.view
layout.preview
settings.view
```

### Marketing

```text
dashboard.view
catalog.view
catalog.product.view
customization.view
layout.view
layout.preview
layout.update
layout.assets.update
discounts.view
discounts.create
discounts.update
discounts.archive
reports.view
settings.view
```

Todas as permissões de loja acima estão contempladas em pelo menos um papel.
Quando uma permissão nova for criada, este mapa precisa ser atualizado junto.

## Permissões globais do admin da plataforma

Admins internos da Loja Club terão permissões globais.

Exemplos:

```text
platform.stores.view
platform.stores.block
platform.stores.unblock
platform.users.view
platform.plans.view
platform.plans.update
platform.webhooks.view
platform.audit.view
platform.support.impersonate
platform.3d_models.view
platform.3d_models.manage
```

Papéis globais iniciais:

| Papel | Permissões |
|---|---|
| `platform_owner` | todas as permissões globais |
| `platform_ops` | `platform.stores.view`, `platform.stores.block`, `platform.stores.unblock`, `platform.users.view`, `platform.plans.view`, `platform.webhooks.view`, `platform.audit.view`, `platform.support.impersonate`, `platform.3d_models.view` |
| `platform_finance` | `platform.stores.view`, `platform.plans.view`, `platform.plans.update`, `platform.audit.view` |
| `platform_support` | `platform.stores.view`, `platform.users.view`, `platform.webhooks.view`, `platform.audit.view`, `platform.support.impersonate`, `platform.3d_models.view` |
| `platform_catalog` | `platform.3d_models.view`, `platform.3d_models.manage` |

Todas as permissões globais estão contempladas em pelo menos um papel global.

## Regra de autorização

Toda rota crítica deve validar:

1. usuário está autenticado;
2. usuário pertence à loja;
3. usuário tem permissão;
4. recurso pertence à loja.

Exemplo:

```text
PUT /stores/{store_id}/products/{product_id}
```

Valida:

```text
user pertence à store_id?
user tem catalog.product.update?
product.store_id == store_id?
```

## Plano + permissão

O acesso final depende de duas camadas:

1. Plano da loja permite o recurso.
2. Usuário tem permissão.

Exemplo:

```text
Plano Pro permite layout.
Usuário Support não tem layout.update.
Resultado: não pode alterar layout.
```

## Interface do painel

O frontend deve esconder módulos sem permissão, mas isso é apenas UX.

A segurança real deve estar no backend.

## Auditoria

Ações sensíveis devem gerar logs:

- alterar plano;
- alterar conta de pagamento;
- alterar domínio;
- convidar usuário;
- remover acesso de usuário;
- alterar permissões;
- cancelar pedido;
- reembolsar pedido;
- bloquear loja;
- acesso de suporte por admin da plataforma.
