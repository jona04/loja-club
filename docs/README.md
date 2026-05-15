# Loja Club — Documentação do Projeto

Este diretório contém a documentação inicial da **Loja Club V1**, baseada nas decisões arquiteturais, de produto e de negócio definidas até agora.

A documentação está em português por enquanto. A estrutura de pastas e nomes de arquivos está em inglês para facilitar uso posterior no Codex, GitHub e ferramentas de desenvolvimento.

## Sumário

1. [Product Vision](./01_product_vision.md)
2. [Business Model and Rules](./02_business_model_and_rules.md)
3. [System Architecture](./03_system_architecture.md)
4. [FastAPI Template Adaptation](./04_fastapi_template_adaptation.md)
5. [Frontend Architecture](./05_frontend_architecture.md)
6. [Multitenancy and Domains](./06_multitenancy_and_domains.md)
7. [Database Strategy](./07_database_strategy.md)
8. [Modules and Permissions](./08_modules_and_permissions.md)
9. [Merchant Dashboard](./09_merchant_dashboard.md)
10. [Storefront and Layouts](./10_storefront_and_layouts.md)
11. [Checkout, Payments and Split](./11_checkout_payments_and_split.md)
12. [AWS Infrastructure and Deployment](./12_aws_infrastructure_and_deployment.md)
13. [Performance, Cache and CDN](./13_performance_cache_and_cdn.md)
14. [Security Strategy](./14_security_strategy.md)
15. [Observability and Operations](./15_observability_and_operations.md)
16. [Testing Strategy](./16_testing_strategy.md)
17. [V1 Roadmap](./17_v1_roadmap.md)
18. [Open Decisions](./18_open_decisions.md)
19. [Legal and Compliance TODO](./19_legal_and_compliance_todo.md)
20. [API Contracts TODO](./20_api_contracts_todo.md)
21. [Design System TODO](./21_design_system_todo.md)
22. [Product Customization 3D](./22_product_customization_3d.md)

## Decisões canônicas até agora

- A Loja Club será uma plataforma **SaaS multi-tenant de ecommerce**.
- A V1 terá foco comercial inicial em **brindes, gráficas e comunicação visual**.
- A V1 será construída usando o **Full Stack FastAPI Template** como base.
- O backend será um **monólito modular em FastAPI**.
- O banco principal será **PostgreSQL**.
- A estratégia de multi-tenancy será **banco compartilhado com `store_id` nas tabelas comerciais**.
- A plataforma terá **frontend público das lojas**, **painel do lojista** e **admin da plataforma**.
- A V1 terá `frontend-storefront`, `frontend-dashboard` e `frontend-admin` como projetos separados.
- O painel do lojista e o admin da plataforma não devem morar no mesmo frontend.
- O storefront público deve ser separado do painel do lojista.
- O sistema de subdomínios será feito com **wildcard DNS** e resolução da loja pelo `Host` da requisição.
- O gateway de pagamento fará o split. A Loja Club **não vai reter dinheiro dos lojistas**.
- A primeira versão terá **2 templates/layouts prontos** para as lojas públicas.
- A V1 terá **personalização 3D de produtos** usando modelos criados pela Loja Club.
- O lojista poderá alterar o template ativo no painel, salvar e refletir imediatamente na loja pública.
- Produtos comuns continuarão funcionando com fotos, variações e carrinho tradicional.
- O painel do lojista será dividido por módulos, permitindo bloqueio por permissão e por plano.
- Um usuário poderá gerenciar várias lojas, e uma loja poderá ter vários usuários.
- A V1 deve ser completa e funcional, mas sem microserviços e sem Kubernetes no primeiro momento.
- Para desenvolvimento e staging barato, Traefik + Docker Compose fazem sentido.
- Para produção V1 mais robusta na AWS, a sugestão é ECS/Fargate + ALB + RDS + S3 + CloudFront.
