---
id: P3-FE-01
title: Renomear painel + scaffold do storefront (Next.js)
phase: 3
etapa: "Etapa 7 — Projeto frontend-storefront (Next.js)"
area: FE
status: todo
depends_on: []
blocks: [P3-SF-02]
tests: none
---

# P3-FE-01 — Renomear painel + scaffold do storefront

## Contexto
A V1 tem **dois** frontends: o painel (`frontend-dashboard`, Vite) e a vitrine pública (`frontend-storefront`, Next.js). Esta task **renomeia** o painel (`frontend/` → `frontend-dashboard/`, nome que os docs [05](../../05_frontend_architecture.md)/[12](../../12_aws_infrastructure_and_deployment.md) usam) e **cria** o `frontend-storefront/`. É **só setup**; as telas da vitrine são a `P3-SF-02`.

## Docs de referência
- [05 — Frontend Architecture](../../05_frontend_architecture.md)
- [12 — AWS Infra & Deployment](../../12_aws_infrastructure_and_deployment.md)
- [03 — System Architecture](../../03_system_architecture.md)

## Escopo (o que ENTRA)
- **Renomear** `frontend/` → `frontend-dashboard/`; ajustar `compose*.yml`, Traefik (`app.${DOMAIN}`), workspace `bun` (lockfile único na raiz) e CI.
- **Criar** `frontend-storefront/` (Next.js + TypeScript + Tailwind), no workspace `bun`; pode reusar o cliente OpenAPI e padrões visuais do dashboard.
- **Compose:** serviço `frontend-storefront`; **Traefik wildcard** `*.${DOMAIN}` → storefront (o painel fica em `app.`).
- Página placeholder no storefront só pra subir verde.

## Fora de escopo (o que NÃO entra)
- Resolução por host, "loja não encontrada", templates → `P3-SF-02`.
- API pública → `P3-SF-01`.

## Arquivos a criar/alterar
- `frontend/` → `frontend-dashboard/` (renomear) — dir + refs em `compose*.yml`, `.github/`, labels do Traefik, `package.json`/workspace.
- `frontend-storefront/` (criar) — projeto Next.js.
- `compose.yml`/`compose.override.yml` (alterar) — serviço + roteamento.

## Passos
1. Renomear o diretório + atualizar **todas** as referências (compose, Traefik, CI, workspace `bun`).
2. Regenerar `bun.lock` na raiz; confirmar painel sobe em `app.${DOMAIN}` e gate do dashboard verde.
3. `create-next-app` em `frontend-storefront/` (TS, Tailwind, App Router); placeholder.
4. Compose + Traefik wildcard; confirmar storefront responde num host de loja.

## Testes
> Regra em [`_foundations-and-bottlenecks.md`](../_foundations-and-bottlenecks.md) §10.

- **Níveis:** `nenhum automatizado` (setup/infra) — smoke manual: painel em `app.`, storefront placeholder em `*.${DOMAIN}`.
- **Cobrir:** o gate do dashboard (`tsc`/`biome`/`vitest`) continua verde após o rename.

## Definition of Done
- [ ] `frontend-dashboard/` sobe em `app.${DOMAIN}`; gate do dashboard verde após o rename.
- [ ] `frontend-storefront/` (Next.js) sobe via Traefik wildcard `*.${DOMAIN}` com placeholder.
- [ ] `compose*.yml`, Traefik, CI e workspace `bun` consistentes (lockfile na raiz regenerado).
- [ ] **Modos de falha mapeados** (rename quebrando CI/Traefik/imports) → tratados ou Follow-up.
- [ ] Itens adiados varridos → Follow-ups + README, ou "nenhum".

## Notas / Reconciliações
- O painel ficou como `frontend/` nas Fases 0–2 (sem segundo frontend, sem motivo pra churn). Os docs já o chamam de `frontend-dashboard` — o rename fecha a divergência.

## Follow-ups
- (preencher ao executar)
