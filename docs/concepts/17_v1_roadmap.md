# V1 Roadmap

## Objetivo

Construir uma primeira versão da Kriar capaz de operar lojas reais.

A V1 deve ser completa, mas sem complexidade desnecessária.

> **Ambientes.** As Fases **0–8** rodam **local** (na máquina do dev); a **Fase 9** sobe o sistema **no ar na AWS, em EC2** (ainda **dev**); a **Fase 10** consolida (follow-ups + segurança); a **Fase 11** é a **produção robusta** (ECS/Fargate + ALB). A **Fase 12** dá ao lojista a geração do próprio 3D. Ver [AWS Infrastructure and Deployment](./12_aws_infrastructure_and_deployment.md).

A prioridade é ter o **sistema funcionando local o quanto antes** (fim da Fase 6), deixando a **integração de pagamento/split para o final** (Fase 8) e o **deploy** logo depois (Fase 9).

Enquanto o gateway não entra, o pagamento é **combinado diretamente entre loja e cliente** (Pix manual, transferência, link, WhatsApp ou entrega combinada). O checkout já cria o pedido como `pending_payment`; só a confirmação automática por gateway é que fica para depois.

## Como ler este roadmap

- As etapas estão agrupadas em **fases**.
- **Ambientes:** Fases 0–8 **local**; Fase 9 **dev online na AWS (EC2)**; Fase 10 consolidação; **Fase 11 produção** (ECS/Fargate).
- Os arquivos (imagens, modelos 3D, artes) usam **AWS S3 + CloudFront reais desde o dev local** (sem MinIO).
- O **marco do MVP (dev local)** acontece ao fim da Fase 6, **antes** de pagamentos e do deploy.
- **Frete e cupons** foram movidos para **antes do carrinho**, porque carrinho e checkout dependem deles.
- **Conta do cliente, pagamento e billing** = Fase 8 (local); **deploy dev na AWS** = Fase 9; **produção** = Fase 11.
- Há dois critérios de conclusão no fim do documento: o do **MVP (dev local)** e o da **V1 completa (dev online na AWS, com pagamento/split)**.
- **Etapas — canônico vs trilha:** a decomposição **canônica** (com tarefas) é a do **[backlog](../backlog/README.md)** (`phase-N-*.md`, etapas **locais 1..N** por fase). Aqui o roadmap é a **trilha de alto nível** e pode **agrupar** etapas mais grosso (e em ordem **narrativa**, não de dependência) — a contagem por fase pode diferir do backlog.

---

## Fase 0 — Fundação (dev local)

### Etapa 1 — Fundação do projeto

Entregas:

- criar projeto a partir do Full Stack FastAPI Template;
- configurar nome/branding Kriar (`PROJECT_NAME`, e-mails, frontend);
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
Projeto base rodando localmente com backend, frontend, banco e proxy, já com a cara da Kriar.
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

### Etapa 1 — Multi-tenancy e lojas

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

### Etapa 2 — Painel do lojista base

Entregas:

- painel em `app.kriar.shop` (local: `app.localhost`);
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

### Etapa 1 — Catálogo e mídia

> Mídia já usa **AWS S3 + CloudFront reais** a partir do dev local (bucket/distribuição de dev). Sem MinIO.

Entregas:

- CRUD de produtos;
- categorias;
- variações simples;
- estoque;
- status publicado/rascunho;
- upload de imagens;
- produto com imagem; 3D / 3D-personalizável → Fase 7;
- S3 (AWS real, ambiente dev);
- worker para thumbnails;
- CloudFront para imagens;
- testes de catálogo.

Resultado:

```text
Lojista consegue cadastrar produtos reais com imagens (servidas por S3/CloudFront).
```

> A personalização 3D é a **Fase 7 — Produtos 3D** (ver abaixo): os modelos vêm do **catálogo da plataforma** (populado por seed; o lojista **escolhe**). A **geração pelo próprio lojista** (GLB via API + mapear área) é a **Fase 12**.

---

## Fase 3 — Loja pública (dev local)

### Etapa 1 — Storefront público (Next.js)

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
Loja pública abre em nomedaloja.kriar.shop (local: *.localhost).
```

### Etapa 2 — Layouts/templates

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

## Fase 4 — Admin do SaaS (dev local)

> Objetivo: a equipe Kriar ganha o **admin** (`frontend-admin` em `admin.${DOMAIN}` + módulo `platform_admin`) pra operar lojas/planos/usuários **e cadastrar templates** (registro + thumbnail no CDN + schema). **Antes do lançamento** — alimenta a configuração da loja (Fase 5). Detalhe em [`backlog/phase-4-platform-admin.md`](../backlog/phase-4-platform-admin.md); decisões em [25](./25_platform_admin.md).

Entregas:

- `frontend-admin` em `admin.${DOMAIN}` (Traefik) + papéis globais `platform.*` (substitui `is_superuser`);
- operar lojas (listar/detalhe/bloquear), planos, usuários; suporte com impersonation + auditoria mínima;
- **registro de templates:** metadados + **thumbnail no CDN** + **settings schema** (do código). *(import de imagens, loja-demo e preview navegável = Fase 5)*

Resultado:

```text
Equipe opera a plataforma e registra templates (thumbnail + schema); a vitrine sai do hardcoded.
```

---

## Fase 5 — Configuração da loja pelo lojista (dev local)

> Objetivo: com os templates **registrados** (Fase 4), esta fase entrega a **loja-demo** por template (import das imagens pro CDN) + o lojista **personaliza** o template — **schema-driven** (`P3-TPL-04`) + **preview navegável completo**. Detalhe em [`backlog/phase-5-store-configuration.md`](../backlog/phase-5-store-configuration.md); decisões em [26](./26_template_system.md) e o passo-a-passo em [27](./27_template_authoring_guide.md).

Entregas:

- **loja-demo por template** (do `demo.json`) + **import das imagens** (uxpilot → CDN);
- form gerado do `settings_schema` do template ativo (campos `text/textarea/image/boolean/select`);
- valores por **loja × template** (não perde ao trocar; resetar = excluir); imagens com **default no CDN**;
- vitrine lê `theme.settings[key] ?? default`; botão "ver preview completo" (outra aba) abre a loja-demo.

Resultado:

```text
Lojista personaliza o template pelo painel; a vitrine reflete.
```

---

## Fase 6 — Venda sem pagamento online (dev local)

> Objetivo da fase: a loja roda **100% local** e já **recebe pedidos sem o gateway**.
> O checkout cria o pedido como `pending_payment` e o pagamento é combinado fora da plataforma
> (Pix/transferência/WhatsApp/entrega combinada) até o gateway entrar na Fase 8.

### Etapa 1 — Frete e cupons (base)

> Movido para antes do carrinho: carrinho (Etapa 2) e checkout (Etapa 3) dependem destas regras.

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

### Etapa 2 — Carrinho

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

### Etapa 3 — Checkout sem pagamento online

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
- **ponto de integração do gateway preparado, mas ainda não conectado** (entra na Fase 8).

Resultado:

```text
Carrinho vira pedido pending_payment, com o cliente identificado por e-mail/telefone; o pagamento é combinado entre loja e cliente.
```

### Etapa 4 — Pedidos

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

### Etapa 5 — Clientes

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

### Etapa 6 — Notificações essenciais + finalização local

> Fecha o MVP rodando de ponta a ponta no Docker Compose local. E-mails locais via Mailcatcher; SES/SMTP real entra na Fase 8.

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

## Fase 7 — Produtos 3D — catálogo da plataforma (dev local)

> Os modelos 3D personalizáveis vêm de um **catálogo público da plataforma** (caneca, camiseta…), **populado por seed** pelo dev (igual ao registro de templates — rápido/barato; o lojista não gera GLB de item comum); o **admin só habilita/desabilita**, e o lojista **escolhe** do catálogo. A **geração pelo próprio lojista** (GLB via API + mapear área) é a **Fase 12**. Detalhe em [`backlog/phase-7-3d-products.md`](../backlog/phase-7-3d-products.md).

### Etapa 1 — Produtos 3D e personalização

Entregas:

- **catálogo público de modelos 3D** (plataforma, via **seed**) + **admin habilita/desabilita**;
- módulo `product_customization`;
- o lojista **escolhe um modelo do catálogo** e vincula ao produto;
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
Cliente personaliza, em 3D, um produto cujo modelo veio do catálogo da plataforma, aprova a arte, e o lojista recebe exatamente o que foi aprovado — sem gerar nenhum GLB.
```

---

## Fase 8 — Conta do cliente, pagamentos e billing (dev local)

> Conta do cliente, gateway com **split**, **billing** e **pagamento em 2 etapas** — **construído e testado local** (webhooks **mockados**). O **deploy dev na AWS** (que destrava os webhooks reais) é a **Fase 9**. Detalhe em [`backlog/phase-8-customer-account-and-payments.md`](../backlog/phase-8-customer-account-and-payments.md).

### Etapa 1 — Conta e login do cliente

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

### Etapa 2 — Pagamentos e split

Entregas:

- escolha e integração com o gateway (decisão pendente: Pagar.me / Mercado Pago / Asaas — ver `18_open_decisions.md`);
- criação de recebedor/subconta;
- payment account por loja;
- criação de transação;
- split automático;
- webhook assinado + idempotência (**contra mock** local; real na Fase 9);
- status de pagamento;
- atualização de pedido por webhook;
- substituir o "pagamento combinado" pelo gateway no checkout;
- testes de webhook (mock).

Resultado:

```text
Cliente paga, gateway divide valores e pedido é atualizado por webhook (validado contra mock; real na Fase 9).
```

### Etapa 3 — Pagamento em 2 etapas (sinal + saldo na entrega)

Entregas:

- ativar/desativar a modalidade por loja + **percentual do sinal** (default 50%) — config no painel;
- **opção no checkout**: "pagar tudo agora" ou "sinal de X% agora + saldo na entrega" (mostra os valores);
- modelo: `order.payment_plan` (`full|deposit_balance`) + `deposit_amount`/`balance_amount`; o **sinal** vira transação no gateway (com split), o **saldo** é marcado recebido na entrega;
- **status próprio** `payment_status` `pending→deposit_paid→paid`, visível pra **cliente** (confirmação/área), **lojista** (painel + "marcar saldo recebido") e **admin** (operação).

Resultado:

```text
O cliente paga 50% agora e 50% na entrega; lojista, cliente e admin acompanham o sinal e o saldo pelo status.
```

### Etapa 4 — Billing da Kriar

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
Kriar começa a monetizar por mensalidade e/ou comissão.
```

---

## Fase 9 — Deploy dev na AWS + ops mínimo (dev online)

> Sobe o sistema **para o ar** (ainda **dev**, em **EC2**) — o que destrava os **webhooks reais** de pagamento (Fase 8) — com o **mínimo** de CI/CD e ops/segurança pra operar. O **admin** já está no ar desde a **Fase 4**. Revisão geral = **Fase 10**; produção = **Fase 11**; beta = **Fase 11**. Detalhe em [`backlog/phase-9-platform-ops-and-dev-deploy.md`](../backlog/phase-9-platform-ops-and-dev-deploy.md).

### Etapa 1 — Deploy do ambiente dev na AWS (EC2)

Entregas:

- provisionar **EC2 + Docker Compose + Traefik** (mesmo stack do dev local);
- **RDS PostgreSQL**; **Redis** (container ou ElastiCache);
- **S3 + CloudFront** do ambiente; **Route 53** (`*.kriar.shop` + `api.`/`app.`/`admin.`);
- **SSL** via Traefik/Let's Encrypt (ACM é a Fase 11);
- **SES/SMTP real** (substitui o Mailcatcher); **não expor** Adminer/Mailcatcher/Traefik;
- segredos em SSM; health checks acessíveis (já existem).

### Etapa 2 — Go-live dos pagamentos (webhook real)

Entregas:

- apontar o gateway pra URL pública; **validar webhook real** (assinatura + idempotência); confirmar transação/pedido/split de ponta a ponta;
- conferir o **pagamento em 2 etapas** online.

### Etapa 3 — CI/CD

Entregas:

- GitHub Actions: lint + type check + testes + build Docker;
- **gate de e2e** (Playwright de todos os frontends → só sobe o que passa);
- deploy automatizado pro **EC2 (dev online)** a cada merge; disciplina de migrations; rollback básico.

### Etapa 4 — Ops/segurança mínimo

Entregas:

- Sentry (DSN por ambiente); logs estruturados + alertas básicos;
- **rate limit** nos endpoints sensíveis; HTTPS + headers + CORS restrito; backups do RDS ligados.

Resultado:

```text
Sistema no ar (dev) na AWS, pagamentos rodando de verdade, deploy automatizado.
```

---

## Fase 10 — Follow-ups, débito técnico e segurança geral (dev online)

> Consolidação antes da produção: **zera os follow-ups/débito técnico** das fases 0–9 e faz a **revisão geral de segurança**. Detalhe em [`backlog/phase-10-followups-and-hardening.md`](../backlog/phase-10-followups-and-hardening.md).

Entregas:

- varredura e fechamento de **todos os follow-ups** (campo de cupom na vitrine + tela de cupons, corridas/idempotência, limpeza de sessões, N+1, LGPD `customer_consents`/export, MJML no pipeline, etc.);
- módulo **`audit`** (auditoria de negócio) + **hardening completo** (restore testado, CSP, retenção de logs, revisão de permissões);
- revisão de performance/cache/índices e edge cases.

Resultado:

```text
Sistema sólido, sem follow-ups soltos, revisado de segurança — pronto pra produção.
```

---

## Fase 11 — Produção na AWS + beta com lojas reais

> Troca a orquestração por **serviços gerenciados** (mantendo backend/banco/storage) e valida com um **beta** real. Detalhe em [`backlog/phase-11-production.md`](../backlog/phase-11-production.md).

### Etapa 1 — Infra de produção

- **ECS/Fargate + ECR**; **ALB** + **ACM**; **RDS Multi-AZ**/read replicas; **ElastiCache**; **autoescala**; **CD** apontando pra ECS + rollback testado.

### Etapa 2 — Domínios próprios dos lojistas

- estratégia de **certificado** para `custom_domain` (emissão/renovação + roteamento).

### Etapa 3 — Beta com lojas reais

- onboarding das primeiras lojas; vendas reais; personalização 3D; **pagamento e split**; **pagamento em 2 etapas**; **jurídico/compliance mínimo**; feedback + correções.

Resultado:

```text
Kriar em produção na AWS, validada por lojistas reais.
```

---

## Fase 12 — 3D gerado pelo lojista (traga seu próprio modelo)

> Além do **catálogo da plataforma** (Fase 7), o lojista **gera o próprio GLB via API externa** (Meshy/Tripo3D/Hyper3D — decisão no doc [18](./18_open_decisions.md)) e **mapeia a área personalizável pelo painel**. Recurso **premium** (plano). Detalhe em [`backlog/phase-12-merchant-3d-generation.md`](../backlog/phase-12-merchant-3d-generation.md).

Entregas:

- abstração do provedor de geração 3D (assíncrono via worker); GLB **por loja** no S3/CDN;
- editor no painel pra **mapear a área imprimível** + limites do modelo gerado;
- vincular o modelo gerado ao produto (entra no fluxo da Fase 7); **gating de plano**.

Resultado:

```text
O lojista cria o próprio modelo 3D e define a área personalizável, sem depender do catálogo da plataforma.
```

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
- comissão da Kriar é registrada;
- billing/assinatura está ativo (se definido na V1);
- admin Kriar consegue monitorar;
- segurança e observabilidade mínimas estão no ar;
- CI/CD faz deploy automatizado para o EC2;
- beta validado com lojistas reais.
