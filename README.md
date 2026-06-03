# Loja Club

Plataforma SaaS multi-tenant de ecommerce, com foco inicial em **brindes, gráficas e comunicação visual** — incluindo **personalização 3D** de produtos.

## Documentação

- **Visão, arquitetura e regras de negócio:** [`docs/`](./docs/) (documentos `01`–`24`).
- **Backlog de implementação (por fase e task):** [`docs/backlog/`](./docs/backlog/README.md).
- **Invariantes e decisões técnicas:** [`docs/backlog/_foundations-and-bottlenecks.md`](./docs/backlog/_foundations-and-bottlenecks.md).
- **Convenções de código (para devs e IA):** [`CLAUDE.md`](./CLAUDE.md).

## Stack

FastAPI · SQLModel · PostgreSQL · Redis · React + Vite (painel) · Next.js (storefront, planejado) · Docker Compose · Traefik.

## Desenvolvimento

- Backend: [`backend/README.md`](./backend/README.md)
- Frontend: [`frontend/README.md`](./frontend/README.md)
- Ambiente local / Docker Compose: [`development.md`](./development.md)
- Deploy: [`deployment.md`](./deployment.md)

A V1 roda em ambiente de **dev** (local; depois AWS/EC2 — ver doc 12). Ajuste o `.env` antes de subir (troque ao menos `SECRET_KEY`, `FIRST_SUPERUSER_PASSWORD`, `POSTGRES_PASSWORD`).

## Licença

MIT — ver [`LICENSE`](./LICENSE).
