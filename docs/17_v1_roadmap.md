# V1 Roadmap

## Objetivo

Construir uma primeira versão da Loja Club capaz de operar lojas reais.

A V1 deve ser completa, mas sem complexidade desnecessária.

> **Toda a V1 é um ambiente de desenvolvimento (dev).** As Fases 0–4 rodam **local** (na máquina do desenvolvedor) e as Fases 6–7 sobem o sistema **no ar na AWS, em EC2**. A **produção robusta** (ECS/Fargate + ALB) fica para **depois da V1**. Ver [AWS Infrastructure and Deployment](./12_aws_infrastructure_and_deployment.md).

A prioridade é ter o **sistema funcionando local o quanto antes** (fim da Fase 4), deixando a **integração de pagamento/split para o final** (Fase 6).

Enquanto o gateway não entra, o pagamento é **combinado diretamente entre loja e cliente** (Pix manual, transferência, link, WhatsApp ou entrega combinada). O checkout já cria o pedido como `pending_payment`; só a confirmação automática por gateway é que fica para depois.

## Situação atual (2026-06-01)

> Até aqui, os commits do projeto foram **somente de documentação**. O código ainda é o **Full Stack FastAPI Template** praticamente sem alterações:
>
> - `backend/app/models.py` só tem `User` e `Item`;
> - `PROJECT_NAME` ainda é `"Full Stack FastAPI Project"` (branding Loja Club pendente);
> - o frontend ainda é o painel padrão do template (login/signup/items);
> - não existe `Store`, `store_id`, módulos, storefront Next.js nem admin.
>
> Ou seja: a **Etapa 1 está apenas parcialmente feita** (projeto gerado pelo template) e as demais ainda não começaram.

## Como ler este roadmap

- As etapas estão agrupadas em **fases**.
- **Toda a V1 é dev:** Fases 0–4 **local**; Fases 6–7 **online na AWS (EC2)**. Produção robusta (ECS/Fargate) é **pós-V1**.
- Os arquivos (imagens, modelos 3D, artes) usam **AWS S3 + CloudFront reais desde o dev local** (sem MinIO).
- O **marco do MVP (dev local)** acontece ao fim da Fase 4, **antes** de subir para a AWS e de pagamentos.
- **Frete e cupons** foram movidos para **antes do carrinho**, porque carrinho e checkout dependem deles.
- **Deploy na AWS, conta do cliente, pagamento e billing** ficam nas Fases 6–7.
- Há dois critérios de conclusão no fim do documento: o do **MVP (dev local)** e o da **V1 completa (dev online na AWS, com pagamento/split)**.

---

## Fase 0 — Fundação (dev local)

### Etapa 1 — Fundação do projeto

> Parcialmente feito: o projeto já foi gerado a partir do template. Faltam o branding e a configuração descritos abaixo.

Entregas:

- criar projeto a partir do Full Stack FastAPI Template; *(feito)*
- configurar nome/branding Loja Club (`PROJECT_NAME`, e-mails, frontend); *(pendente)*
- configurar variáveis de ambiente;
- rodar Docker Compose local;
- validar backend;
- validar frontend;
- validar banco;
- configurar Redis;
- configurar estrutura base de módulos;
- configurar CI inicial (lint/testes);
- configurar lint/testes básicos.

Resultado:

```text
Projeto base rodando localmente com backend, frontend, banco e proxy, já com a cara da Loja Club.
```

### Etapa 2 — Refatoração modular

Entregas:

- separar backend em módulos;
- remover exemplos genéricos do template (`items`);
- criar base de services/repositories/routes/schemas por módulo;
- definir padrões internos;
- preparar base para multi-tenancy.

Resultado:

```text
Template transformado em monólito modular.
```

---

## Fase 1 — Núcleo multi-tenant e painel (dev local)

### Etapa 3 — Multi-tenancy e lojas

Entregas:

- entidade Store;
- entidade StoreMember;
- roles/permissões iniciais;
- criação de loja;
- seleção de loja ativa;
- subdomínio automático;
- tabela `domain_hosts`;
- resolução por host;
- isolamento por store_id;
- testes de isolamento.

Resultado:

```text
Usuário cria loja e os dados ficam isolados por store_id.
```

### Etapa 4 — Painel do lojista base

Entregas:

- painel em `app.loja.club` (local: `app.localhost`);
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

---

## Fase 2 — Catálogo e mídia (dev local)

### Etapa 5 — Catálogo e mídia

> Mídia já usa **AWS S3 + CloudFront reais** a partir do dev local (bucket/distribuição de dev). Sem MinIO.

Entregas:

- CRUD de produtos;
- categorias;
- variações simples;
- estoque;
- status publicado/rascunho;
- upload de imagens;
- produto com imagem; 3D / 3D-personalizável → Fase 5;
- S3 (AWS real, ambiente dev);
- worker para thumbnails;
- CloudFront para imagens;
- testes de catálogo.

Resultado:

```text
Lojista consegue cadastrar produtos reais com imagens (servidas por S3/CloudFront).
```

> A personalização 3D é a **Fase 5 — Produtos 3D** (ver abaixo): o lojista **gera o modelo via API de terceiros**; não há biblioteca da plataforma.

---

## Fase 3 — Loja pública (dev local)

### Etapa 7 — Storefront público (Next.js)

> Decisão fechada (docs 05/10/18): o storefront usa **Next.js** desde a V1, com **Three.js** para o editor 3D.

Entregas:

- projeto `frontend-storefront` em Next.js;
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
Loja pública abre em nomedaloja.loja.club (local: *.localhost).
```

### Etapa 8 — Layouts/templates

Entregas:

- template `classic`;
- template `modern`;
- tabela `content_theme_templates`;
- tabela `content_store_theme_settings`;
- tela Layout da Loja;
- preview;
- aplicar template;
- invalidar cache;
- refletir alteração na loja pública.

Resultado:

```text
Lojista escolhe entre 2 layouts e a loja pública muda ao salvar.
```

---

## Fase 4 — Venda sem pagamento online (dev local)

> Objetivo da fase: a loja roda **100% local** e já **recebe pedidos sem o gateway**.
> O checkout cria o pedido como `pending_payment` e o pagamento é combinado fora da plataforma
> (Pix/transferência/WhatsApp/entrega combinada) até o gateway entrar na Fase 6.

### Etapa 9 — Frete e cupons (base)

> Movido para antes do carrinho: carrinho (Etapa 10) e checkout (Etapa 11) dependem destas regras.

Entregas:

- frete fixo;
- frete grátis por valor mínimo;
- retirada local;
- entrega combinada (`private_delivery`);
- regiões atendidas (cidade/região/estado), sem cálculo automático;
- cupom percentual;
- cupom valor fixo;
- validade;
- limite de uso;
- pedido mínimo.

Resultado:

```text
Loja tem regras básicas de entrega e desconto disponíveis para o carrinho e o checkout.
```

### Etapa 10 — Carrinho

Entregas:

- criar carrinho;
- sessão anônima de carrinho;
- recuperação de carrinho no mesmo navegador;
- token seguro para continuar compra;
- adicionar item;
- adicionar item personalizado;
- remover item do carrinho;
- alterar quantidade;
- aplicar cupom básico;
- calcular subtotal;
- validar estoque;
- persistência temporária;
- vínculo com sessão de personalização aprovada.

Resultado:

```text
Cliente final consegue montar carrinho.
```

### Etapa 11 — Checkout sem pagamento online

Entregas:

- dados do cliente;
- **identificação e deduplicação do customer sem login**, por e-mail e telefone normalizados (E.164), match priorizando o e-mail (ver `23_customer_identity_and_guest_checkout.md`);
- normalização de e-mail (trim + minúsculas) e telefone (país pelo seletor → E.164);
- criação/atualização de customer com regra de **primeiro-nome-vence**;
- endereço, permitindo **vários endereços por customer**;
- frete simples;
- entrega combinada;
- revisão do pedido;
- criação de pedido `pending_payment`;
- congelamento de preços;
- congelamento da personalização aprovada;
- sessão de checkout;
- **pagamento combinado fora da plataforma** (Pix manual/transferência/WhatsApp), com mensagem pós-compra explicando como o pagamento será combinado;
- **ponto de integração do gateway preparado, mas ainda não conectado** (entra na Fase 6).

Resultado:

```text
Carrinho vira pedido pending_payment, com o cliente identificado por e-mail/telefone; o pagamento é combinado entre loja e cliente.
```

### Etapa 12 — Pedidos

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
- marcação manual de pagamento recebido (enquanto não há gateway);
- cancelamento, se permitido.

Resultado:

```text
Lojista consegue operar vendas recebidas.
```

### Etapa 13 — Clientes

Entregas:

- lista de clientes;
- detalhe do cliente;
- **cliente identificado por e-mail/telefone normalizados, sem cadastro** (um customer por loja);
- histórico de pedidos do customer;
- endereços (vários por customer);
- busca por nome/e-mail/telefone;
- permissões.

Resultado:

```text
Lojista visualiza clientes da própria loja e sabe quem é quem pelo contato, mesmo sem cadastro.
```

### Etapa 14 — Notificações essenciais + finalização local

> Fecha o MVP rodando de ponta a ponta no Docker Compose local. E-mails locais via Mailcatcher; SES/SMTP real entra na Fase 6.

Entregas:

- e-mail de **pedido criado** para o cliente (Mailcatcher no dev local);
- e-mail de **novo pedido** para o lojista (Mailcatcher no dev local);
- health checks básicos (`/health`, `/health/db`, `/health/redis`) no ambiente de desenvolvimento;
- fluxo completo validado de ponta a ponta no Docker Compose local.

Resultado:

```text
MVP rodando 100% local, recebendo pedidos, com pagamento combinado fora da plataforma.
```

---

## 🚀 Marco — MVP funcionando local

Este é o ponto que você pediu para alcançar o quanto antes: o sistema **rodando local** de ponta a ponta, **sem pagamento online**. Atingido quando:

- lojista cria conta;
- lojista cria loja;
- subdomínio funciona (local);
- lojista cadastra produto (simples e personalizável);
- lojista vincula modelo 3D a produto personalizável;
- lojista escolhe layout;
- loja pública abre no subdomínio local;
- cliente navega, personaliza produto em 3D e aprova a arte;
- cliente adiciona ao carrinho;
- cliente finaliza checkout sem login;
- **cliente é identificado por e-mail/telefone normalizados (sem cadastro), com deduplicação**;
- pedido é criado como `pending_payment`;
- pagamento é combinado fora da plataforma;
- lojista vê o pedido e a arte aprovada no painel;
- cliente e lojista recebem e-mail do pedido (Mailcatcher);
- isolamento multi-tenant está testado.

---

## Fase 5 — Produtos 3D (dev local)

> O **lojista gera o próprio modelo 3D (GLB) via API de terceiros** (Meshy/Tripo3D/Hyper3D — decisão no doc [18](./18_open_decisions.md)); **não há catálogo 3D da plataforma**. Modelos **por loja**. Detalhe em [`backlog/phase-5-3d-products.md`](./backlog/phase-5-3d-products.md).

### Etapa 6 — Produtos 3D e personalização

Entregas:

- módulo `product_customization`;
- **geração de modelo 3D via API** (lojista, a partir de imagem/descrição) → GLB por loja no S3;
- campo `type` do produto (`image`/`image_3d`/`image_3d_customizable`);
- configuração de produto personalizável;
- sessão de personalização salva;
- upload de arte pelo cliente;
- preview/snapshot aprovado;
- editor 3D no storefront (Three.js);
- vínculo da personalização com carrinho;
- cópia congelada da personalização no pedido;
- visualização da personalização no painel do lojista.

Resultado:

```text
Cliente personaliza, em 3D, um produto cujo modelo o próprio lojista gerou via API, aprova a arte, e o lojista recebe exatamente o que foi aprovado.
```

---

## Fase 6 — Dev online na AWS (EC2)

> Aqui o sistema vai **para o ar** (ainda como ambiente **dev**), em **EC2**. Subir antes de pagamentos é necessário porque o gateway envia **webhooks** para uma URL pública.

### Etapa 15 — Deploy do ambiente dev na AWS (EC2)

Entregas:

- provisionar **EC2 + Docker Compose + Traefik**;
- **RDS PostgreSQL**;
- **Redis** (container no EC2 ou ElastiCache);
- **S3 + CloudFront** do ambiente online (a implementação já existe desde o dev local);
- **Route 53** com wildcard `*.loja.club` + `api.`/`app.`;
- **SSL** via Traefik/Let's Encrypt (ACM depois);
- **SES/SMTP real** para os e-mails;
- **não expor** Adminer/Mailcatcher/Traefik dashboard;
- health checks acessíveis.

Resultado:

```text
Sistema no ar (dev), em EC2, pronto para receber webhooks de pagamento.
```

### Etapa 16 — Conta e login do cliente

> Detalhes em `23_customer_identity_and_guest_checkout.md`. No MVP o cliente já é identificado por e-mail/telefone; aqui ele ganha login e área própria, sincronizando com o que comprou como convidado.

Entregas:

- recuperação de carrinho/pedido por **código de uso único** (e-mail/SMS/WhatsApp);
- **login por código** (sem senha);
- **login por e-mail + senha**;
- **login com Google (OAuth)**;
- tabelas `customer_auth_identities` e `customer_verification_codes`;
- **sincronização guest ↔ conta** (mesmo customer por e-mail/telefone, sem duplicar);
- **área do cliente**: histórico de pedidos, endereços, personalizações e edição de perfil (inclui o nome);
- edição de perfil exige autenticação;
- rate limit/anti brute force nos códigos.

Resultado:

```text
Cliente entra por código, senha ou Google, vê o histórico e edita o perfil, sem perder o que comprou como convidado.
```

### Etapa 17 — Pagamentos e split

Entregas:

- escolha e integração com o gateway (decisão pendente: Pagar.me / Mercado Pago / Asaas — ver `18_open_decisions.md`);
- criação de recebedor/subconta;
- payment account por loja;
- criação de transação;
- split automático;
- webhook assinado;
- idempotência;
- status de pagamento;
- atualização de pedido por webhook;
- substituir o "pagamento combinado" pelo gateway no checkout;
- testes de webhook.

Resultado:

```text
Cliente paga, gateway divide valores e pedido é atualizado por webhook.
```

### Etapa 18 — Billing da Loja Club

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

---

## Fase 7 — Operação da plataforma, CI/CD e beta

### Etapa 19 — Admin da plataforma

Entregas:

- projeto `frontend-admin`;
- `admin.loja.club`;
- listar lojas;
- ver detalhes de loja;
- bloquear/desbloquear loja;
- ver usuários;
- ver pedidos por loja;
- ver webhooks com erro;
- configurar a integração da API de geração 3D (Fase 5);
- gerenciar planos;
- ver comissões;
- auditoria.

Resultado:

```text
Equipe Loja Club consegue operar a plataforma.
```

### Etapa 20 — Segurança e observabilidade

Entregas:

- auditoria;
- Sentry;
- CloudWatch;
- health checks completos;
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
Ambiente dev online pronto para uso controlado.
```

### Etapa 21 — CI/CD

Entregas:

- GitHub Actions: lint + type check + testes;
- build das imagens Docker;
- push para registry (ECR/registry escolhido);
- deploy automatizado para o **EC2 (dev online)**;
- disciplina de migrations (rodar em dev antes);
- rollback básico.

Resultado:

```text
Deploy automatizado do ambiente dev na AWS a cada merge.
```

### Etapa 22 — Beta com lojas reais

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
V1 validada com lojistas reais (no ambiente dev online da AWS).
```

---

## Pós-V1 — Produção robusta (fora do escopo da V1)

> Não entra na V1. Quando a V1 (dev) estiver validada, migrar para produção trocando a orquestração por serviços gerenciados, **mantendo backend, banco e storage**:

- ECS/Fargate + ECR;
- ALB;
- ACM;
- RDS Multi-AZ / read replicas conforme necessidade;
- ElastiCache;
- autoescala;
- estratégia de certificado para domínios próprios dos lojistas.

Ver [AWS Infrastructure and Deployment](./12_aws_infrastructure_and_deployment.md).

---

## Critério do MVP (dev local, sem pagamento)

O MVP está pronto (rodando local) quando:

- lojista cria conta e loja;
- subdomínio funciona (local);
- lojista cadastra produto simples e personalizável;
- lojista vincula modelo 3D ao produto personalizável;
- lojista escolhe layout;
- loja pública abre;
- cliente personaliza produto em 3D e aprova a arte;
- cliente adiciona ao carrinho;
- cliente finaliza checkout sem login;
- cliente é identificado por e-mail/telefone normalizados, com deduplicação e primeiro-nome-vence;
- pedido é criado como `pending_payment`;
- pagamento é combinado fora da plataforma;
- lojista vê pedido e arte aprovada no painel;
- cliente e lojista recebem e-mail do pedido;
- isolamento multi-tenant está testado.

## Critério de V1 completa (dev online na AWS, com pagamento/split)

A V1 está completa quando, além de tudo acima:

- sistema está **no ar na AWS (EC2)**, em ambiente dev;
- cliente pode entrar na área do cliente (código, senha ou Google) e editar o perfil, com sincronização guest ↔ conta;
- pagamento é processado pelo gateway;
- webhook confirma pedido;
- split é aplicado;
- comissão da Loja Club é registrada;
- billing/assinatura está ativo (se definido na V1);
- admin Loja Club consegue monitorar;
- segurança e observabilidade mínimas estão no ar;
- CI/CD faz deploy automatizado para o EC2;
- beta validado com lojistas reais.
