# Fase 9 — Operação da plataforma e deploy dev na AWS (EC2)

> Objetivo: **subir o sistema para o ar** num ambiente **dev** na **AWS (EC2)** + o **mínimo** de ops/CI-CD/segurança pra rodar online (o que destrava os **webhooks reais** de pagamento da Fase 8). **Só dev** — produção robusta é a **[Fase 11](./phase-11-production.md)**. A **revisão geral** de segurança/débito técnico é a **[Fase 10](./phase-10-followups-and-hardening.md)**; o **beta** com lojas reais vai com a produção (**Fase 11**). O **admin da plataforma** já está no ar desde a **[Fase 4](./phase-4-platform-admin.md)**.

Docs de referência: [12](../concepts/12_aws_infrastructure_and_deployment.md), [13](../concepts/13_performance_cache_and_cdn.md), [14](../concepts/14_security_strategy.md), [15](../concepts/15_observability_and_operations.md), [11](../concepts/11_checkout_payments_and_split.md), [16](../concepts/16_testing_strategy.md), [17](../concepts/17_v1_roadmap.md).

## Definition of Done da fase
- Loja pública, painel, **admin** e API no ar por domínio público com **HTTPS** (ambiente **dev**, EC2).
- **Webhooks reais** alcançáveis → os pagamentos da Fase 8 (gateway/split) passam a rodar de verdade.
- **CI/CD** faz deploy automatizado para o EC2 (dev online) a cada merge.
- **Mínimo** de segurança/observabilidade no ar pra operar (Sentry, health, alertas básicos, segredos em SSM, HTTPS/headers/CORS, rate limit nos endpoints sensíveis).

---

## Etapa 1 — Deploy do ambiente dev na AWS (EC2)

> Mesmo stack do dev local (**EC2 + Docker Compose + Traefik**); **não** é produção (ECS/Fargate é a Fase 11). Doc [12](../concepts/12_aws_infrastructure_and_deployment.md).

### Infra
- [ ] Provisionar **EC2** + **Docker Compose** + **Traefik** (mesmo stack do dev local).
- [ ] **RDS PostgreSQL** (single-AZ, backups automáticos). Doc [12](../concepts/12_aws_infrastructure_and_deployment.md).
- [ ] **Redis**: container no EC2 ou **ElastiCache**.
- [ ] **S3 + CloudFront** do ambiente online (implementação já existe desde o dev local; apontar para bucket/distribuição do ambiente). Doc [12](../concepts/12_aws_infrastructure_and_deployment.md)/[13](../concepts/13_performance_cache_and_cdn.md).
- [ ] **Route 53**: `*.kriar.shop`, `api.`, `app.`, `admin.`. Doc [06](../concepts/06_multitenancy_and_domains.md)/[12](../concepts/12_aws_infrastructure_and_deployment.md).
- [ ] **SSL** via Traefik/Let's Encrypt (ACM fica para produção — Fase 11). Doc [12](../concepts/12_aws_infrastructure_and_deployment.md).
- [ ] **SES/SMTP real** para os e-mails (substitui o Mailcatcher do dev local). Doc [12](../concepts/12_aws_infrastructure_and_deployment.md)/[21](../concepts/21_design_system_todo.md).
- [ ] **Não expor** Adminer/Mailcatcher/Traefik dashboard. Doc [04](../concepts/04_fastapi_template_adaptation.md)/[14](../concepts/14_security_strategy.md).
- [ ] **Segredos** fora do código (env seguro/SSM). Doc [14](../concepts/14_security_strategy.md).
- [ ] Compose dedicado do ambiente online (ex.: `compose.aws.yml`) + script de deploy manual (o pipeline automatizado é a Etapa 3).
- [ ] Health checks acessíveis (`/health`, `/health/db`, `/health/redis` — **já existem** desde `P6-NOTIF-01`). Doc [15](../concepts/15_observability_and_operations.md).

### DoD da etapa
- [ ] Loja pública, painel, admin e API acessíveis por domínio público com HTTPS; **webhooks alcançáveis**.

**Reconciliação:** ambiente dev online usa **EC2 + Docker Compose + Traefik** (doc [12](../concepts/12_aws_infrastructure_and_deployment.md)). ECS/Fargate + ALB + ACM é a **Fase 11**.

---

## Etapa 2 — Go-live dos pagamentos (webhook real)

> A Fase 8 construiu o `payments` contra **mock**. Com o sistema no ar, os webhooks reais passam a chegar. Doc [11](../concepts/11_checkout_payments_and_split.md)/[14](../concepts/14_security_strategy.md).
- [ ] Apontar o gateway para a URL pública; **validar assinatura/origem + idempotência** dos webhooks reais; confirmar transação + pedido + split de ponta a ponta.
- [ ] Conferir o **pagamento em 2 etapas** (sinal no gateway + saldo marcado na entrega) no ambiente online.

---

## Etapa 3 — CI/CD (deploy automatizado pro EC2 dev)

Doc [12](../concepts/12_aws_infrastructure_and_deployment.md), [16](../concepts/16_testing_strategy.md).
- [ ] **CI** (consolida o CI básico da Fase 0): GitHub Actions roda **lint + type check + testes** (backend e frontend) + build Docker.
- [ ] **Gate de e2e (release):** o CI roda o **e2e (Playwright) de TODOS os frontends** (dashboard + admin + storefront) e **só faz deploy do que passa** — nenhum frontend sobe com e2e vermelho. (Storefront ganha e2e na [`P3-SF-03`](./phase-3-storefront-and-layouts/P3-SF-03-storefront-e2e.md); admin já tem na `P4-ADMIN-01`.)
- [ ] **CD**: push das imagens para registry (ECR ou registry escolhido) e **deploy automatizado para o EC2 (dev online)** a cada merge na branch alvo.
- [ ] **Migrations** com disciplina: rodar em dev antes; não alterar o ambiente online manualmente. Doc [07](../concepts/07_database_strategy.md)/[12](../concepts/12_aws_infrastructure_and_deployment.md).
- [ ] **Rollback** básico (versão anterior das imagens).
- [ ] Secrets do pipeline fora do código (GitHub Secrets/SSM). Doc [14](../concepts/14_security_strategy.md).

---

## Etapa 4 — Mínimo de segurança/observabilidade pra rodar online

> Só o **necessário pra operar o dev-online com segurança**. A **revisão geral** (módulo `audit`, hardening completo, retenção, restore testado) é a **[Fase 10](./phase-10-followups-and-hardening.md)**. Doc [14](../concepts/14_security_strategy.md)/[15](../concepts/15_observability_and_operations.md).
- [ ] **Sentry** com DSN por ambiente (template já integra). Doc [04](../concepts/04_fastapi_template_adaptation.md)/[15](../concepts/15_observability_and_operations.md).
- [ ] **Logs estruturados** + **alertas básicos** (5xx, latência de checkout, fila acumulando, webhooks falhando, RDS CPU/storage, worker indisponível, cert perto de expirar). Doc [15](../concepts/15_observability_and_operations.md).
- [ ] **Rate limit** nos endpoints sensíveis (login, recuperação de senha, checkout, criação de conta, códigos de cliente). Doc [14](../concepts/14_security_strategy.md).
- [ ] **HTTPS + headers** (HSTS, X-Content-Type-Options, CSP/X-Frame-Options) + **CORS restrito** a `app.`, `admin.`, `*.`, `kriar.shop`. Doc [14](../concepts/14_security_strategy.md).
- [ ] **Segredos** em SSM/env seguro; nada no código. Doc [14](../concepts/14_security_strategy.md).
- [ ] **Backups** automáticos do RDS ligados (o **plano de restauração testado** fica pra Fase 10). Doc [14](../concepts/14_security_strategy.md).

---

## Testes (doc [16](../concepts/16_testing_strategy.md))
- [ ] **CI/CD:** um merge dispara o pipeline e atualiza o ambiente dev online sem passos manuais.
- [ ] **Webhook real:** assinatura validada; evento duplicado não reprocessa; evento pago atualiza transação + pedido.
- [ ] **Smoke online:** loja pública, painel, admin e API respondem por HTTPS; health checks OK.

---

## Reconciliações (registrar aqui)
- **Produção robusta** (ECS/Fargate + ALB + ACM + Multi-AZ + autoescala) = **[Fase 11](./phase-11-production.md)** (não entra aqui).
- **Revisão geral** de segurança + módulo `audit` + hardening completo + retenção de logs + restore testado = **[Fase 10](./phase-10-followups-and-hardening.md)**.
- **Beta com lojas reais** + jurídico/compliance + teste de carga = **[Fase 11](./phase-11-production.md)** (precisa de chão sólido/produção).
