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

Auth é para `account_users`: admin Loja Club, lojista e equipe.
Cliente final não precisa usar login na V1.

### Guest Session

- criar sessão anônima;
- recuperar sessão anônima;
- renovar expiração;
- vincular sessão a customer no checkout;
- gerar token seguro para continuar compra;
- validar token seguro.

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
- arquivar domínio.

### Catalog

- listar produtos;
- criar produto;
- atualizar produto;
- publicar produto;
- arquivar produto (offline reversível);
- deletar produto (soft-delete);
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
- recuperar carrinho por sessão anônima;
- recuperar carrinho por token seguro;
- adicionar item;
- adicionar item personalizado;
- atualizar quantidade;
- remover item do carrinho;
- aplicar cupom;
- obter resumo.

### Checkout

- iniciar checkout;
- validar carrinho;
- validar personalizações aprovadas;
- identificar ou criar customer no checkout;
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
- arquivar cliente;
- gerar link seguro para continuar compra;
- gerar link seguro para acompanhar pedido.

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

## Padrão da API (V1 — travado em `P1-API-01`)

- **URL/versão:** `/api/v1`. Painel sob `/api/v1/stores/{store_id}/...`; storefront público resolve a loja pelo header `Host`.
- **Response:** recurso único = objeto direto; **lista = `{ "data": [...], "count": <total> }`**.
- **Paginação:** offset por query — `skip` (≥ 0) e `limit` (1..100, default 100).
- **Erro:** envelope estruturado `{ "error": { "code": "<slug>", "message": "<texto>", "details": <lista|null> } }`. `code` estável por status (`bad_request`, `unauthorized`, `forbidden`, `not_found`, `conflict`, `validation_error`, `rate_limited`) ou explícito via `AppError`.
- **Autenticação:** Bearer JWT (`/api/v1/login/access-token`).
- **Headers de tenant:** painel → `store_id` no path (não header); storefront → `Host`.
- **Idempotency-Key:** reservado para operações sensíveis (criar pedido/pagamento) — implementação Fase 6/7.

## TODO (restante)

- [x] URL · response · erro · paginação · headers de tenant · autenticação — **definidos** (`P1-API-01`).
- [ ] Filtros (por endpoint, conforme a feature).
- [ ] Schemas por módulo (cada fase).
- [ ] Contratos públicos do storefront (Fase 3).
- [ ] Contratos de webhook (Fase 8).
