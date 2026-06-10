# Fase 9 — Operação da plataforma, CI/CD e beta

> Roadmap: Etapas 20–22. Objetivo: o ambiente **dev online na AWS** fica seguro e observável, o deploy vira **CI/CD automatizado** e a V1 é validada em **beta** com lojas reais. (O **admin da plataforma** é a **[Fase 4](./phase-4-platform-admin.md)**; produção robusta com ECS/Fargate é **pós-V1** — ver o fim deste arquivo.)

Docs de referência: [05](../05_frontend_architecture.md), [08](../08_modules_and_permissions.md), [09](../09_merchant_dashboard.md), [22](../22_product_customization_3d.md), [14](../14_security_strategy.md), [15](../15_observability_and_operations.md), [12](../12_aws_infrastructure_and_deployment.md), [13](../13_performance_cache_and_cdn.md), [19](../19_legal_and_compliance_todo.md), [16](../16_testing_strategy.md), [17](../17_v1_roadmap.md).

## Definition of Done da fase (= Critério de V1 completa)

- O **admin da plataforma** ([Fase 4](./phase-4-platform-admin.md)) está no ar em `admin.loja.club` operando lojas/planos/webhooks/auditoria.
- Segurança e observabilidade mínimas no ar (auditoria, Sentry, rate limit, URLs assinadas, backups, alertas).
- **CI/CD** faz deploy automatizado para o **EC2 (dev online)**.
- Beta validado com lojistas reais, incluindo pagamento e split.

---

## Etapa 20 — Segurança e observabilidade (módulo `audit` + hardening)

Doc [14](../14_security_strategy.md), [15](../15_observability_and_operations.md).

### Módulo `audit`
- [ ] `audit_logs` (ações críticas), `account_login_events` (logins/falhas), `audit_security_events`. Índices `store_id+created_at`, `user_id+created_at`. Doc [07](../07_database_strategy.md)/[15](../15_observability_and_operations.md).
- [ ] Registrar ações sensíveis do doc [08](../08_modules_and_permissions.md)/[14](../14_security_strategy.md)/[15](../15_observability_and_operations.md): alterar plano/conta de pagamento/domínio/permissão, convidar/remover usuário, cancelar/reembolsar pedido, bloquear loja, acesso de suporte, acesso a arte do cliente, alteração de preço/modelo 3D.

### Observabilidade
- [ ] **Sentry** (template já integra — configurar DSN por ambiente). Doc [04](../04_fastapi_template_adaptation.md)/[15](../15_observability_and_operations.md).
- [ ] **CloudWatch** logs/métricas/alarmes; **logs estruturados** (request id, user id, store id, endpoint, status, latência, order id, payment tx id, customization session id). Doc [15](../15_observability_and_operations.md).
- [ ] **Health checks** completos `/health`, `/health/db`, `/health/redis`. Doc [15](../15_observability_and_operations.md).
- [ ] **Alertas** iniciais (5xx, latência de checkout, fila acumulando, webhooks falhando, RDS CPU/storage, worker indisponível, cert perto de expirar, falhas de upload/3D). Doc [15](../15_observability_and_operations.md).

### Hardening
- [ ] **Rate limit** em login, recuperação de senha, checkout, criação de conta, códigos de cliente, APIs públicas sensíveis. Doc [14](../14_security_strategy.md).
- [ ] **Validação de webhooks** (assinatura/origem/idempotência) endurecida (consolida Fase 8). Doc [14](../14_security_strategy.md).
- [ ] **Segredos** em SSM/env seguro; nada no código. Doc [14](../14_security_strategy.md).
- [ ] **Uploads/arte privada**: validação + **URLs assinadas** para arquivos privados; separar por `store_id`. Doc [14](../14_security_strategy.md)/[22](../22_product_customization_3d.md).
- [ ] **Backups** automáticos do RDS + **plano de restauração testado**. Doc [14](../14_security_strategy.md).
- [ ] **HTTPS + headers** (HSTS, X-Content-Type-Options, CSP/X-Frame-Options) + **CORS restrito** a `app.`, `admin.`, `*.`, `loja.club`. Doc [14](../14_security_strategy.md).
- [ ] Política de **retenção de logs** (app 14–30 dias; auditoria por mais tempo). Doc [15](../15_observability_and_operations.md).

### Testes (doc [16](../16_testing_strategy.md))
- [ ] permissão validada no backend (não só no front); assinatura de webhook; rate limit; URL assinada para arquivo privado; entradas de auditoria geradas.

---

## Etapa 21 — CI/CD

Doc [12](../12_aws_infrastructure_and_deployment.md), [16](../16_testing_strategy.md).

- [ ] **CI** (consolida o CI básico da Fase 0): GitHub Actions roda **lint + type check + testes** (backend e frontend) + build Docker.
- [ ] **CD**: push das imagens para registry (ECR ou registry escolhido) e **deploy automatizado para o EC2 (dev online)** a cada merge na branch alvo.
- [ ] **Migrations** com disciplina: rodar em dev antes; não alterar prod manualmente. Doc [07](../07_database_strategy.md)/[12](../12_aws_infrastructure_and_deployment.md).
- [ ] **Rollback** básico (versão anterior das imagens).
- [ ] Secrets do pipeline fora do código (GitHub Secrets/SSM). Doc [14](../14_security_strategy.md).

### Testes/validação
- [ ] Um merge dispara o pipeline e atualiza o ambiente dev online sem passos manuais.

---

## Etapa 22 — Beta com lojas reais

Doc [17](../17_v1_roadmap.md), [02](../02_business_model_and_rules.md), [16](../16_testing_strategy.md), [19](../19_legal_and_compliance_todo.md).

- [ ] Onboarding das primeiras lojas (brindes, gráficas, comunicação visual), seguindo o checklist do doc [09](../09_merchant_dashboard.md).
- [ ] Testar vendas reais; personalização 3D real; **validar pagamento e split**; suporte; coletar feedback; corrigir bugs críticos. Doc [17](../17_v1_roadmap.md).
- [ ] **Testes de carga** (doc [16](../16_testing_strategy.md)): listagem de produtos, home, página de produto, editor 3D, criação de carrinho/pedido, webhook.
- [ ] **Jurídico/compliance mínimo** antes de clientes reais: termos de uso, termos do lojista, política de privacidade/LGPD, produtos proibidos, chargeback (doc [19](../19_legal_and_compliance_todo.md)).

### Critério de V1 completa
- [ ] Sistema **no ar na AWS (EC2)**, em ambiente dev.
- [ ] Cliente entra na área do cliente (código/senha/Google) e edita perfil, com sync guest↔conta.
- [ ] Pagamento processado pelo gateway; webhook confirma pedido; split aplicado; comissão registrada.
- [ ] Billing/assinatura ativo (se definido na V1); admin monitora; segurança/observabilidade no ar; **CI/CD** ativo; beta validado. Doc [17](../17_v1_roadmap.md).

---

## Pós-V1 — Produção robusta (fora do escopo da V1)

> **Não entra na V1.** Quando a V1 (dev) estiver validada, migrar para produção trocando a orquestração por serviços gerenciados, **mantendo backend, banco e storage**. Doc [12](../12_aws_infrastructure_and_deployment.md).

- [ ] ECS/Fargate + ECR (substitui EC2 + Docker Compose).
- [ ] ALB (substitui Traefik) + ACM (substitui Let's Encrypt).
- [ ] RDS Multi-AZ / read replicas conforme necessidade.
- [ ] ElastiCache dedicado.
- [ ] Autoescala de containers.
- [ ] Estratégia de **certificado para domínios próprios** dos lojistas (custom_domain). Doc [06](../06_multitenancy_and_domains.md).
- [ ] Pipeline de CD apontando para ECS.

---

## Reconciliações (registrar aqui)
- (preencher conforme surgirem)
