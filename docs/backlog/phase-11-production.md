# Fase 11 — Produção na AWS + beta com lojas reais

> Objetivo: levar o sistema (já validado em **dev online** + consolidado na Fase 10) para **produção robusta** na AWS — trocando a orquestração por **serviços gerenciados**, **mantendo backend, banco e storage** — e validar com um **beta** de lojas reais. Aqui o sistema deixa de ser "dev online" e vira **produção**.

Docs de referência: [12](../concepts/12_aws_infrastructure_and_deployment.md), [06](../concepts/06_multitenancy_and_domains.md), [14](../concepts/14_security_strategy.md), [15](../concepts/15_observability_and_operations.md), [02](../concepts/02_business_model_and_rules.md), [19](../concepts/19_legal_and_compliance_todo.md), [16](../concepts/16_testing_strategy.md), [17](../concepts/17_v1_roadmap.md).

## Definition of Done da fase
- Produção rodando em **ECS/Fargate + ALB + ACM** (substitui EC2 + Docker Compose + Traefik), **mantendo** o mesmo backend/banco/storage.
- **CD** apontando para produção; rollback testado.
- **Beta** com lojas reais validado: vendas reais, pagamento/split, personalização 3D, suporte e feedback — com **jurídico/compliance mínimo** no ar.

---

## Etapa 1 — Infra de produção (AWS gerenciada)

Doc [12](../concepts/12_aws_infrastructure_and_deployment.md).
- [ ] **ECS/Fargate + ECR** (substitui EC2 + Docker Compose).
- [ ] **ALB** (substitui Traefik) + **ACM** (substitui Let's Encrypt).
- [ ] **RDS Multi-AZ** / read replicas conforme necessidade.
- [ ] **ElastiCache** dedicado (Redis gerenciado).
- [ ] **Autoescala** de containers.
- [ ] **Pipeline de CD** apontando para ECS (a partir do CI/CD da Fase 9) + **rollback** testado.

## Etapa 2 — Domínios próprios dos lojistas

Doc [06](../concepts/06_multitenancy_and_domains.md).
- [ ] Estratégia de **certificado para domínios próprios** dos lojistas (`custom_domain`): emissão/renovação automática + roteamento.

## Etapa 3 — Beta com lojas reais

Doc [17](../concepts/17_v1_roadmap.md), [02](../concepts/02_business_model_and_rules.md), [19](../concepts/19_legal_and_compliance_todo.md), [16](../concepts/16_testing_strategy.md).
- [ ] **Onboarding** das primeiras lojas (brindes, gráficas, comunicação visual), seguindo o checklist do doc [09](../concepts/09_merchant_dashboard.md).
- [ ] Testar **vendas reais**; **personalização 3D** real; **validar pagamento e split**; **pagamento em 2 etapas**; suporte; coletar feedback; corrigir bugs críticos.
- [ ] **Jurídico/compliance mínimo** antes de clientes reais: termos de uso, termos do lojista, política de privacidade/LGPD, produtos proibidos, chargeback (doc [19](../concepts/19_legal_and_compliance_todo.md)).

## Etapa 4 — Melhorias internas

- [ ] Endereçar o que o beta + a carga real revelarem (performance, custos, ergonomia de operação).

---

## Testes (doc [16](../concepts/16_testing_strategy.md))
- [ ] **Deploy produção:** CD sobe pra ECS sem passos manuais; rollback funciona.
- [ ] **Carga** (beta): listagem de produtos, home, página de produto, editor 3D, criação de carrinho/pedido, webhook.
- [ ] **Domínio próprio** de um lojista resolve com HTTPS.

---

## Reconciliações
- Esta fase materializa o que era **"Pós-V1 — Produção robusta"** no roadmap antigo (estava no fim da antiga Fase 9). O **beta** veio da antiga Fase 9 (Etapa 3) — precisa de chão de produção.
