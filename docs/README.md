# Loja Club — Documentação do Projeto

Documentação da **Loja Club V1** — SaaS multi-tenant de ecommerce. Organizada em três partes:

- **[`concepts/`](./concepts/README.md)** — os **docs conceituais** (produto, arquitetura, negócio, banco, etc., 01–27). **Fonte de verdade** das decisões; o código imita a lógica daqui.
- **[`backlog/`](./backlog/README.md)** — o **backlog acionável** (todo list por fase, em nível de task). Foco atual: Fases 0–6 (o MVP utilizável para teste).
- **[`design/`](./design/)** — os **designs** dos templates (HTML do uxpilot — referência de port).

Português por enquanto; nomes de pasta/arquivo em inglês.

## Decisões canônicas até agora

- A Loja Club será uma plataforma **SaaS multi-tenant de ecommerce**, com foco comercial inicial em **brindes, gráficas e comunicação visual**.
- Construída sobre o **Full Stack FastAPI Template**; backend = **monólito modular em FastAPI**; banco = **PostgreSQL** (compartilhado, com `store_id` nas tabelas comerciais).
- Três frontends separados: **`frontend-storefront`** (loja pública), **`frontend-dashboard`** (painel do lojista) e **`frontend-admin`** (admin da plataforma).
- Subdomínios via **wildcard DNS** + resolução da loja pelo `Host`.
- O gateway de pagamento faz o **split**; a Loja Club **não retém dinheiro** dos lojistas.
- **Templates prontos** (Aurora/Bazar/Studio) para as lojas públicas — o lojista **escolhe e personaliza**, sem montar layout livre; trocar de template não quebra o fluxo de compra.
- **Personalização 3D** = **Fase 7**: o lojista gera os modelos via **API de terceiros** (não há catálogo 3D da plataforma).
- O cliente final compra e personaliza **sem login obrigatório**; carrinhos/sessões anônimas têm validade.
- **Soft delete / status arquivado** em vez de delete físico para registros de negócio.
- Um usuário pode gerenciar várias lojas; uma loja pode ter vários usuários (papéis/permissões por loja).
- Toda a V1 é ambiente de **dev**: Fases 0–7 rodam **local** (com S3/CloudFront reais); Fases 8–9 sobem na AWS com **EC2** + Docker Compose + Traefik. **Produção robusta** (ECS/Fargate) fica para **depois da V1**.
