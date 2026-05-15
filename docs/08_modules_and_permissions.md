# Modules and Permissions

## Decisão principal

O painel do lojista será dividido em módulos. Cada módulo terá permissões próprias.

Essa decisão resolve três necessidades:

1. organizar a experiência do lojista;
2. permitir controle de acesso por usuário;
3. permitir bloqueio de funcionalidades por plano.

A V1 também terá personalização 3D de produtos.
Esse módulo deve ser controlado por plano e permissão, porque será um diferencial importante para brindes, gráficas e comunicação visual.

## Modelo de usuários

Um usuário pode gerenciar várias lojas.

Uma loja pode ter vários usuários.

Modelo conceitual:

```text
User
Store
StoreMember
Role
Permission
```

## User

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

### Owner

Dono da loja.

Tem acesso total.

Pode:

- gerenciar tudo;
- alterar plano;
- convidar/remover admins;
- transferir propriedade;
- excluir ou solicitar exclusão da loja;
- alterar dados críticos.

### Admin

Administrador da loja.

Pode:

- gerenciar produtos;
- gerenciar pedidos;
- gerenciar personalizações;
- gerenciar clientes;
- alterar layout;
- configurar checkout;
- configurar frete;
- convidar equipe;
- ver relatórios.

Não deve poder, por padrão:

- transferir propriedade;
- excluir loja;
- alterar dados críticos de cobrança sem permissão explícita.

### Manager

Gerente operacional.

Pode:

- produtos;
- pedidos;
- clientes;
- estoque;
- cupons;
- relatórios básicos.

Não pode:

- alterar plano;
- alterar gateway;
- alterar domínio;
- gerenciar equipe.

### Support

Atendimento.

Pode:

- ver pedidos;
- ver clientes;
- adicionar notas;
- atualizar status operacional permitido.

Não pode:

- alterar preço;
- excluir produto;
- configurar pagamento;
- alterar layout;
- reembolsar sem permissão extra.

### Catalog

Responsável pelo catálogo.

Pode:

- criar produto;
- editar produto;
- alterar imagens;
- alterar estoque;
- alterar categorias.

Não pode:

- ver relatórios financeiros;
- configurar pagamento;
- reembolsar pedido;
- alterar equipe.

### Marketing

Responsável por aparência e promoções.

Pode:

- alterar banners;
- alterar páginas;
- alterar layout;
- criar cupons;
- ver relatórios simples.

Não pode:

- configurar gateway;
- reembolsar pedido;
- alterar equipe.

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

### Produtos

```text
catalog.product.view
catalog.product.create
catalog.product.update
catalog.product.delete
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
customers.delete
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
shipping.delete
shipping.private_delivery.update
```

### Cupons

```text
discounts.view
discounts.create
discounts.update
discounts.delete
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
domains.delete
domains.verify
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
- remover usuário;
- alterar permissões;
- cancelar pedido;
- reembolsar pedido;
- bloquear loja;
- acesso de suporte por admin da plataforma.
