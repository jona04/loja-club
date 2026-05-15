# API Contracts TODO

<!--
Este documento será usado depois para detalhar contratos de API.
Por enquanto, ele lista os grupos de endpoints necessários para a V1.
-->

## Grupos de endpoints previstos

### Auth

- login;
- logout;
- me;
- recuperação de senha;
- refresh token, se aplicável.

### Stores

- criar loja;
- listar minhas lojas;
- obter loja ativa;
- atualizar configurações;
- publicar/pausar loja.

### Store Members

- listar membros;
- convidar membro;
- alterar papel;
- remover membro;
- listar permissões.

### Domains

- listar domínios;
- criar subdomínio;
- verificar disponibilidade;
- adicionar domínio próprio;
- verificar DNS;
- definir domínio principal.

### Catalog

- listar produtos;
- criar produto;
- atualizar produto;
- excluir/desativar produto;
- publicar/despublicar;
- categorias;
- variações;
- estoque;
- imagens.

### Storefront Public

- resolver loja por host;
- obter home;
- obter tema ativo;
- listar categorias;
- listar produtos públicos;
- obter produto por slug;
- obter página pública.

### Cart

- criar carrinho;
- adicionar item;
- atualizar quantidade;
- remover item;
- aplicar cupom;
- obter resumo.

### Checkout

- iniciar checkout;
- validar carrinho;
- calcular frete;
- listar métodos de entrega disponíveis;
- selecionar método de entrega;
- criar pedido pendente;
- criar pagamento.

### Shipping

- listar métodos de entrega da loja;
- criar método de entrega;
- atualizar método de entrega;
- ativar/desativar método de entrega;
- configurar frete fixo;
- configurar frete grátis;
- configurar retirada local;
- configurar entrega combinada;
- definir regiões atendidas;
- definir mensagem exibida no checkout.

### Payments

- conectar conta;
- obter status da conta;
- listar transações;
- webhook do gateway;
- reprocessar webhook interno;
- reembolso.

### Orders

- listar pedidos;
- obter detalhe;
- atualizar status;
- cancelar;
- adicionar nota;
- histórico.

### Customers

- listar clientes;
- obter cliente;
- histórico de pedidos;
- endereços.

### Layout

- listar templates;
- obter template ativo;
- preview;
- aplicar template;
- atualizar logo/banner/textos.

### Billing

- listar planos;
- obter plano atual;
- trocar plano;
- listar faturas;
- ver comissão aplicada.

### Platform Admin

- listar lojas;
- ver loja;
- bloquear/desbloquear;
- listar usuários;
- listar webhooks;
- gerenciar planos;
- ver auditoria.

## TODO

- [ ] Definir padrão de URL.
- [ ] Definir padrão de response.
- [ ] Definir padrão de erro.
- [ ] Definir paginação.
- [ ] Definir filtros.
- [ ] Definir autenticação.
- [ ] Definir headers de tenant/store.
- [ ] Definir schemas por módulo.
- [ ] Definir contratos públicos do storefront.
- [ ] Definir contratos de webhook.
