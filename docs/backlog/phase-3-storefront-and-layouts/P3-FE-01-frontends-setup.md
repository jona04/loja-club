---
id: P3-FE-01
title: Renomear painel + scaffold do storefront (Next.js)
phase: 3
etapa: "Etapa 1 — Projeto frontend-storefront"
area: FE
status: done
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
- [x] Gate do dashboard verde após o rename (**biome + tsc + vitest 18**); imagem Docker do painel builda. *(roteamento Traefik `app.` = smoke pendente — ver Follow-ups)*
- [x] `frontend-storefront/` (Next.js) com placeholder: **`next build` verde** + imagem Docker builda. *(wildcard Traefik = smoke pendente)*
- [x] `compose*.yml`, Traefik, CI e workspace `bun` consistentes; **`bun.lock` regenerado** (2 membros, bun 1.3.14) — **`compose config` válido**.
- [x] **e2e Playwright 41/41** após o rename (corrigido teste de tema flaky do template).
- [x] **Modos de falha mapeados** → Follow-ups.
- [x] Itens adiados varridos → Follow-ups + README.

## Notas / Reconciliações
- O painel ficou como `frontend/` nas Fases 0–2 (sem segundo frontend, sem motivo pra churn). Os docs já o chamam de `frontend-dashboard` — o rename fecha a divergência.
- **Serviço compose também renomeado:** `frontend` → `frontend-dashboard` (+ routers Traefik `-frontend-dashboard-*`), pra casar com `frontend-storefront`.
- **Caminho interno dos Dockerfiles → `/app/frontend-dashboard`** (o `bun install` resolve o workspace pelo root `package.json`, tem que casar). Os Dockerfiles do dashboard (build + playwright) copiam **os dois** manifestos (`frontend-dashboard/` **e** `frontend-storefront/package.json`) antes do `bun install` — workspace de 2 membros.
- **Scaffold do storefront feito à mão** (não `create-next-app`, que pede bun/rede): Next 15 + React 19 (casando versões do dashboard) + Tailwind 4 via `@tailwindcss/postcss`.
- **Traefik:** storefront usa `HostRegexp(^.+\.${DOMAIN}$)` com `priority=1` (baixa) pra os routers `Host()` específicos (`app.`/`api.`/`adminer.`) ganharem.
- **Vite dev/e2e em `:5180`** (= painel, casa com `FRONTEND_HOST`+CORS); `bun.lock` regenerado via `docker run oven/bun:1` (bun **1.3.14 = CI**).
- **Teste de tema flaky do template corrigido:** `user-settings.spec.ts "Selected mode is preserved"` usava `page.evaluate(classList)` sem auto-wait → reescrito p/ `toHaveClass` (sem isso o CI quebra por `--fail-on-flaky-tests`).

## Follow-ups
- [ ] **Smoke do Traefik** (com o proxy rodando): `app.${DOMAIN}`→painel, `api.`→backend, `{loja}.${DOMAIN}`→storefront. O wildcard só foi validado por `compose config`, **não** no roteamento real. *Modo de falha:* prioridade/regex errada faz o catch-all do storefront engolir `app.`/`api.`/`adminer.`.
- [ ] **Lint/test do storefront nos gates:** o hook biome do `.pre-commit` é só `^frontend-dashboard/`; o storefront não tem lint/test no pre-commit nem job de CI — plugar quando tiver código real (`P3-SF-02`).
- [ ] **Pipeline da imagem do storefront:** `DOCKER_IMAGE_STOREFRONT` + serviço no `compose.yml` existem, mas o build/push da imagem (doc [12](../../12_aws_infrastructure_and_deployment.md)) não está montado — Fase 8/9.
- [ ] **Dockerfile do storefront é single-stage** (não-standalone) — otimizar p/ Next standalone depois.
- [x] **Refs `frontend/` em docs de tasks concluídas (P0/P1/P2)** varridas p/ `frontend-dashboard/` — mantido `frontend/` só onde o texto descreve o próprio mapeamento/rename (`P1-DASH-01` linhas 25/58 e esta task).
- [ ] **`bun.lock`:** confirmar/regerar com o `bun` do usuário antes de commitar (foi via `oven/bun:1` 1.3.14, deve bater).
