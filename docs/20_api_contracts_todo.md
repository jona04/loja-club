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
- configurar produto personalizável;
- vincular modelo 3D ao produto.

### Product Customization

- listar modelos 3D disponíveis;
- obter configuração de personalização do produto;
- iniciar sessão de personalização;
- obter sessão de personalização;
- atualizar estado da sessão;
- enviar imagem/arte do cliente;
- gerar/registrar preview;
- aprovar personalização;
- listar sessões da loja;
- expirar sessão abandonada.

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
- adicionar item personalizado;
- atualizar quantidade;
- remover item;
- aplicar cupom;
- obter resumo.

### Checkout

- iniciar checkout;
- validar carrinho;
- validar personalizações aprovadas;
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
- obter personalização do item;
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
- gerenciar biblioteca de modelos 3D;
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
