# Testing Strategy

## Objetivo

A Loja Club precisa de testes focados em comportamento crítico.

O foco da V1 deve ser testar:

- isolamento multi-tenant;
- permissões;
- catálogo;
- personalização 3D;
- guest checkout;
- checkout;
- pagamentos/webhooks;
- pedidos;
- domínio/subdomínio;
- layout/template;
- segurança.

## Ferramentas

O template já traz base para:

- Pytest no backend;
- Playwright para E2E;
- testes de frontend;
- CI via GitHub Actions.

## Testes backend

Prioridades:

### Multi-tenant

Testar que:

- usuário da loja A não acessa dados da loja B;
- produto só é encontrado com `store_id` correto;
- pedido de uma loja não aparece em outra;
- domínio resolve para a loja correta;
- domínio inexistente retorna loja não encontrada.

### Permissões

Testar que:

- Owner acessa tudo;
- Admin acessa quase tudo;
- Support não altera layout;
- Catalog não vê pagamento;
- usuário sem permissão recebe bloqueio;
- permissão no frontend não substitui validação no backend.

### Catálogo

Testar:

- criar produto;
- publicar produto;
- despublicar produto;
- alterar estoque;
- slug único por loja;
- mesmo slug pode existir em lojas diferentes, se permitido;
- upload de imagem valida tipo/tamanho.

### Personalização 3D

Testar:

- produto simples não exige personalização;
- produto `customizable_3d` exige sessão aprovada para ir ao checkout;
- cliente consegue iniciar sessão;
- estado da sessão é salvo;
- upload de arte valida tipo/tamanho;
- preview/snapshot é registrado;
- sessão aprovada é vinculada ao carrinho;
- pedido congela a personalização;
- alteração posterior da sessão não altera pedido criado;
- lojista só vê personalizações da própria loja.

### Layout

Testar:

- loja inicia com template padrão;
- lojista aplica template `classic`;
- lojista aplica template `modern`;
- cache é invalidado;
- storefront retorna template ativo correto.

### Checkout

Testar:

- cliente compra sem login;
- carrinho anônimo é recuperado no mesmo navegador;
- carrinho pode ser recuperado por token seguro depois de contato informado;
- carrinho cria pedido pendente;
- preço do pedido fica congelado no momento da compra;
- personalização aprovada fica congelada no pedido;
- estoque é validado;
- pedido não vira pago sem webhook;
- pagamento recusado atualiza pedido;
- pagamento aprovado atualiza pedido.

### Webhooks

Testar:

- assinatura inválida é rejeitada;
- evento duplicado não processa duas vezes;
- evento desconhecido é registrado;
- evento pago atualiza transação;
- evento pago atualiza pedido;
- evento de outra loja não contamina dados.

### Pagamentos

Testar:

- split é criado com comissão correta do plano;
- loja sem payment account ativa não pode vender;
- reembolso exige permissão;
- chargeback é registrado.

## Testes frontend

### Dashboard

Testar:

- login;
- seleção de loja;
- menu muda por permissão;
- usuário sem permissão não vê módulo;
- alteração de layout salva;
- criação de produto;
- visualização de pedidos.
- visualização de personalizações.

### Storefront

Testar:

- domínio resolve loja;
- home carrega;
- produto carrega;
- editor 3D carrega em produto personalizável;
- sessão de personalização é retomada;
- categoria carrega;
- carrinho funciona;
- checkout inicia.

## Testes E2E críticos

Fluxos principais:

1. Criar conta.
2. Criar loja.
3. Escolher subdomínio.
4. Cadastrar produto.
5. Vincular modelo 3D, se produto for personalizável.
6. Escolher layout.
7. Abrir loja pública.
8. Personalizar produto.
9. Aprovar arte.
10. Adicionar produto ao carrinho.
11. Criar pedido.
12. Simular webhook de pagamento aprovado.
13. Ver pedido e personalização no painel.

## Mocks

Mockar integrações externas em testes:

- gateway de pagamento;
- S3;
- e-mail;
- DNS;
- CloudFront;
- webhooks externos.

## CI

GitHub Actions deve rodar:

- lint;
- type check, se configurado;
- testes backend;
- testes frontend;
- testes E2E essenciais, quando viável;
- build Docker.

## Testes de carga simples

Antes de produção, testar:

- listagem de produtos;
- home pública;
- página de produto;
- editor de personalização 3D;
- criação de carrinho;
- criação de pedido;
- webhook.

## Decisão canônica

A estratégia de testes deve priorizar multi-tenancy, permissões, personalização 3D, checkout, webhooks e isolamento de dados. Esses são os pontos mais críticos para evitar falhas graves na Loja Club.
