---
id: P4-ADMIN-01
title: Projeto frontend-admin — scaffold + Traefik admin. + login
phase: 4
etapa: "Etapa 1 — frontend-admin + platform_admin + papéis globais"
area: ADMIN
status: todo
depends_on: [P4-PLAT-01]
blocks: [P4-ADMIN-02, P4-ADMIN-03]
tests: [e2e]
---

# P4-ADMIN-01 — `frontend-admin` (scaffold + Traefik + login)

## Contexto
A equipe Loja Club precisa de um painel **separado** do painel do lojista, em `admin.${DOMAIN}`, autenticado pelos papéis `platform.*` (`P4-PLAT-01`).

## Docs de referência
- [05 — Frontend Architecture](../../05_frontend_architecture.md)
- [25 — Platform Admin](../../25_platform_admin.md)
- [06 — Multitenancy and Domains](../../06_multitenancy_and_domains.md)
- [12 — AWS Infra & Deployment](../../12_aws_infrastructure_and_deployment.md)

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
- [ ] `frontend-admin` sobe em `admin.localhost` (Traefik), login `platform.*`, shell com aviso interno.
- [ ] Gates (`tsc`/`biome`) verdes + smoke do host.
- [ ] **Modos de falha / edge cases mapeados** → tratados ou Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Reusa o cliente OpenAPI/padrões do `frontend-dashboard` (não recriar) — decisão de frontends separados (doc [05](../../05_frontend_architecture.md)).

## Follow-ups
- [ ] — (preencher ao implementar) → README da fase.
