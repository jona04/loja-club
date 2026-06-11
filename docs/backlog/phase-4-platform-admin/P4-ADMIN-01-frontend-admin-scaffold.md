---
id: P4-ADMIN-01
title: Projeto frontend-admin — scaffold + Traefik admin. + login
phase: 4
etapa: "Etapa 1 — frontend-admin + platform_admin + papéis globais"
area: ADMIN
status: done
depends_on: [P4-PLAT-01]
blocks: [P4-ADMIN-02, P4-ADMIN-03]
tests: [e2e]
---

# P4-ADMIN-01 — `frontend-admin` (scaffold + Traefik + login)

## Contexto
A equipe Loja Club precisa de um painel **separado** do painel do lojista, em `admin.${DOMAIN}`, autenticado pelos papéis `platform.*` (`P4-PLAT-01`).

## Docs de referência
- [05 — Frontend Architecture](../../concepts/05_frontend_architecture.md)
- [25 — Platform Admin](../../concepts/25_platform_admin.md)
- [06 — Multitenancy and Domains](../../concepts/06_multitenancy_and_domains.md)
- [12 — AWS Infra & Deployment](../../concepts/12_aws_infrastructure_and_deployment.md)

## Escopo (o que ENTRA)
- Projeto `frontend-admin/` (React/Vite, no workspace bun) — **reusa** o cliente OpenAPI + componentes/padrões do `frontend-dashboard`.
- Roteamento Traefik do host `admin.${DOMAIN}` (dev: `admin.localhost`) → `frontend-admin`; service no `compose.yml`.
- Login (sessão `platform.*`) + shell/layout com **indicação visual clara de ambiente interno**.
- Origem do admin no `BACKEND_CORS_ORIGINS`.

## Fora de escopo (o que NÃO entra)
- Telas de operação (lojas/usuários/planos) → `P4-ADMIN-02`.
- Telas de templates → `P4-ADMIN-03`.
- Backend de autorização global → `P4-PLAT-01`.

## Arquivos a criar/alterar
- `frontend-admin/` (criar) — scaffold Vite + cliente OpenAPI + login/shell.
- `compose.yml` + labels Traefik (alterar) — host `admin.`.
- `backend/.env.example` / CORS (alterar) — origem do admin.
- `package.json` raiz / `bun.lock` (alterar) — workspace.

## Passos
1. Scaffold `frontend-admin` espelhando `frontend-dashboard` (sem recriar o cliente).
2. Service + Traefik `admin.` no compose; adicionar a origem ao CORS.
3. Login com `platform.*`; shell com aviso de ambiente interno.
4. Subir via Traefik (`admin.localhost`) e validar o roteamento real.

## Testes
> Regra em [`_foundations-and-bottlenecks.md`](../_foundations-and-bottlenecks.md) §10.
- **Níveis:** e2e (smoke) + `tsc`/`biome`.
- **Cobrir:** `admin.` roteia pro admin; login `platform.*` entra; usuário sem papel não acessa.

## Definition of Done
- [x] `frontend-admin` (Vite/React) com **login** `platform.*` + **shell** com banner de **ambiente interno** + guard via `GET /platform/me` (sem papel → "acesso negado").
- [x] Gates verdes: `vite build` + `tsc` + `biome` + **e2e Playwright 3/3** (não-logado→login; admin→shell; sem papel→negado); backend `/platform/me` testado (3/3 + lint).
- [x] **Smoke do host** validado (`docker compose up --build frontend-admin` → `admin.localhost` via Traefik + login OK) e **`bun.lock`** regenerado com o membro novo.
- [x] **Modos de falha mapeados** → guard de não-admin; 401/403 → `/login`.
- [x] **Itens adiados varridos** → Follow-ups + README.

> **Entregue:** projeto `frontend-admin/` espelhando o `frontend-dashboard` (cliente OpenAPI **regenerado** c/ `/platform/*`, UI Radix/shadcn, TanStack Router/Query); rotas `__root`/`login`/`_layout` (shell+guard+banner)/`index` + `useAuth`; backend **`GET /platform/me`** (+ teste); wiring `compose.yml`+`override` (`admin.${DOMAIN}` / porta **5181**), workspace na raiz, `DOCKER_IMAGE_ADMIN`, CORS (`localhost:5181` + `admin.localhost`). **Validado:** smoke real (docker, login OK) + **e2e Playwright 3/3** (`playwright-admin`); `bun.lock` regenerado com o membro novo.

## Notas / Reconciliações
- Reusa o cliente OpenAPI/padrões do `frontend-dashboard` (não recriar) — decisão de frontends separados (doc [05](../../concepts/05_frontend_architecture.md)).

## Follow-ups
- [x] **Smoke real do host** (docker) — validado (login via `admin.localhost`).
- [x] **`bun.lock`** regenerado com o membro `frontend-admin` (`npx bun@1.3.14 install`).
- [x] **e2e (Playwright) do admin** — `playwright.config` + `Dockerfile.playwright` + service `playwright-admin` + specs (login + guard) → **3/3 verde**.
- [ ] **Gate de CI** (e2e de **todos** os frontends bloqueia o deploy) → **Fase 9** (regra registrada na `P3-SF-03`). → README da fase.
