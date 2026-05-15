# V1 Roadmap

## Objetivo

Construir uma primeira versão completa, funcional e capaz de operar lojas reais na Loja Club.

A V1 deve ser completa, mas sem complexidade desnecessária.

## Etapa 1 — Fundação do projeto

Entregas:

- criar projeto a partir do Full Stack FastAPI Template;
- configurar nome Loja Club;
- configurar variáveis de ambiente;
- rodar Docker Compose local;
- validar backend;
- validar frontend;
- validar banco;
- configurar Redis;
- configurar estrutura base de módulos;
- configurar CI inicial;
- configurar lint/testes básicos.

Resultado:

```text
Projeto base rodando localmente com backend, frontend, banco e proxy.
```

## Etapa 2 — Refatoração modular

Entregas:

- separar backend em módulos;
- remover exemplos genéricos do template;
- criar base de services/repositories/routes/schemas por módulo;
- definir padrões internos;
- preparar base para multi-tenancy.

Resultado:

```text
Template transformado em monólito modular.
```

## Etapa 3 — Multi-tenancy e lojas

Entregas:

- entidade Store;
- entidade StoreMember;
- roles/permissões iniciais;
- criação de loja;
- seleção de loja ativa;
- subdomínio automático;
- tabela domains;
- resolução por host;
- isolamento por store_id;
- testes de isolamento.

Resultado:

```text
Usuário cria loja e os dados ficam isolados por store_id.
```

## Etapa 4 — Painel do lojista base

Entregas:

- painel em `app.loja.club`;
- login;
- seleção de loja ativa;
- menu modular;
- permissões no menu;
- dashboard inicial;
- tela de configurações da loja;
- tela de equipe.

Resultado:

```text
Lojista consegue acessar e gerenciar sua loja básica.
```

## Etapa 5 — Catálogo e mídia

Entregas:

- CRUD de produtos;
- categorias;
- variações simples;
- estoque;
- status publicado/rascunho;
- upload de imagens;
- produto `simple` e `customizable_3d`;
- S3;
- worker para thumbnails;
- CloudFront para imagens;
- testes de catálogo.

Resultado:

```text
Lojista consegue cadastrar produtos reais com imagens.
```

## Etapa 6 — Personalização 3D de produtos

Entregas:

- módulo `product_customization`;
- biblioteca inicial de modelos 3D;
- modelos de caneca, squeeze e camisa;
- configuração de produto personalizável;
- sessão de personalização salva;
- upload de arte pelo cliente;
- preview/snapshot aprovado;
- vínculo da personalização com carrinho;
- cópia congelada da personalização no pedido;
- visualização da personalização no painel do lojista.

Resultado:

```text
Cliente personaliza produto em 3D, aprova a arte e o lojista recebe exatamente o que foi aprovado.
```

## Etapa 7 — Storefront público

Entregas:

- projeto `frontend-storefront`;
- roteamento por domínio/subdomínio;
- home pública;
- página de produto;
- editor 3D com Three.js;
- página de categoria;
- menu;
- rodapé;
- botão flutuante de WhatsApp;
- busca simples, se couber;
- cache público básico.

Resultado:

```text
Loja pública abre em nomedaloja.loja.club.
```

## Etapa 8 — Layouts/templates

Entregas:

- template `classic`;
- template `modern`;
- tabela `theme_templates`;
- tabela `store_theme_settings`;
- tela Layout da Loja;
- preview;
- aplicar template;
- invalidar cache;
- refletir alteração na loja pública.

Resultado:

```text
Lojista escolhe entre 2 layouts e a loja pública muda ao salvar.
```

## Etapa 9 — Carrinho

Entregas:

- criar carrinho;
- adicionar item;
- adicionar item personalizado;
- remover item;
- alterar quantidade;
- aplicar cupom básico;
- calcular subtotal;
- validar estoque;
- persistência temporária.
- vínculo com sessão de personalização aprovada.

Resultado:

```text
Cliente final consegue montar carrinho.
```

## Etapa 10 — Checkout

Entregas:

- dados do cliente;
- endereço;
- frete simples;
- entrega combinada;
- revisão do pedido;
- criação de pedido pendente;
- congelamento de preços;
- congelamento da personalização aprovada;
- sessão de checkout;
- preparação para gateway.

Resultado:

```text
Carrinho vira pedido pending_payment.
```

## Etapa 11 — Pagamentos e split

Entregas:

- integração com gateway escolhido;
- criação de recebedor/subconta;
- payment account por loja;
- criação de transação;
- split automático;
- webhook assinado;
- idempotência;
- status de pagamento;
- atualização de pedido;
- testes de webhook.

Resultado:

```text
Cliente paga, gateway divide valores e pedido é atualizado por webhook.
```

## Etapa 12 — Pedidos

Entregas:

- lista de pedidos no painel;
- detalhe do pedido;
- status;
- histórico;
- dados do cliente;
- itens;
- personalização aprovada por item;
- arquivos enviados pelo cliente;
- status de arte/produção;
- notas internas;
- alteração de status operacional;
- cancelamento, se permitido.

Resultado:

```text
Lojista consegue operar vendas recebidas.
```

## Etapa 13 — Clientes

Entregas:

- lista de clientes;
- detalhe do cliente;
- histórico de pedidos;
- endereços;
- busca;
- permissões.

Resultado:

```text
Lojista visualiza clientes da própria loja.
```

## Etapa 14 — Frete e cupons

Entregas:

- frete fixo;
- frete grátis por valor mínimo;
- retirada local;
- entrega combinada;
- cupom percentual;
- cupom valor fixo;
- validade;
- limite de uso.

Resultado:

```text
Loja consegue vender com regras básicas de entrega e desconto.
```

## Etapa 15 — Billing da Loja Club

Entregas:

- planos;
- recursos por plano;
- comissão por plano;
- status de assinatura;
- faturas;
- bloqueio por inadimplência;
- tela de plano no painel;
- integração de cobrança da mensalidade, se definida na V1.

Resultado:

```text
Loja Club começa a monetizar por mensalidade e/ou comissão.
```

## Etapa 16 — Admin da plataforma

Entregas:

- projeto `frontend-admin`;
- `admin.loja.club`;
- listar lojas;
- ver detalhes de loja;
- bloquear/desbloquear loja;
- ver usuários;
- ver pedidos por loja;
- ver webhooks com erro;
- gerenciar modelos 3D globais;
- gerenciar planos;
- ver comissões;
- auditoria.

Resultado:

```text
Equipe Loja Club consegue operar a plataforma.
```

## Etapa 17 — Segurança e observabilidade

Entregas:

- auditoria;
- Sentry;
- CloudWatch;
- health checks;
- rate limit;
- validação de webhooks;
- política de segredos;
- segurança de uploads de arte;
- URLs assinadas para arquivos privados;
- backups;
- logs estruturados;
- alertas mínimos.

Resultado:

```text
Sistema pronto para produção controlada.
```

## Etapa 18 — Infra AWS

Entregas:

- S3;
- CloudFront;
- storage para modelos 3D e artes de clientes;
- RDS;
- Redis/ElastiCache;
- ECS/Fargate ou EC2 staging;
- Route 53;
- SSL;
- GitHub Actions;
- deploy staging;
- deploy production.

Resultado:

```text
Loja Club publicada com infraestrutura real.
```

## Etapa 19 — Beta com lojas reais

Entregas:

- cadastrar primeiras lojas;
- priorizar brindes, gráficas e comunicação visual;
- testar vendas reais;
- testar personalização 3D real;
- validar fluxo de pagamento;
- validar split;
- validar suporte;
- coletar feedback;
- corrigir bugs críticos.

Resultado:

```text
V1 validada com lojistas reais.
```

## Critério de V1 pronta

A V1 está pronta quando:

- lojista cria conta;
- lojista cria loja;
- subdomínio funciona;
- lojista cadastra produto;
- lojista vincula modelo 3D a produto personalizável;
- lojista escolhe layout;
- loja pública abre;
- cliente personaliza produto em 3D;
- cliente aprova arte;
- cliente adiciona ao carrinho;
- cliente finaliza checkout;
- pagamento é processado;
- webhook confirma pedido;
- split é aplicado;
- lojista vê pedido no painel;
- lojista vê arte personalizada aprovada;
- cliente recebe confirmação;
- admin Loja Club consegue monitorar;
- isolamento multi-tenant está testado.
