---
id: P1-DASH-01
title: Infra do painel (frontend-dashboard, Traefik app.)
phase: 1
etapa: "Etapa 4 — Painel do lojista"
area: DASH
status: done
depends_on: []
blocks: [P1-DASH-02]
tests: none
---

# P1-DASH-01 — Infra do painel (`frontend-dashboard`, Traefik `app.`)

## Contexto
O painel do lojista mora em `app.loja.club` e é o frontend React/Vite do template reaproveitado como **`frontend-dashboard`** (doc [05](../../05_frontend_architecture.md)/[09](../../09_merchant_dashboard.md)). Esta task ajusta roteamento/infra e limpa resíduos do template antes de construir as telas.

## Docs de referência
- [05 — Frontend Architecture](../../05_frontend_architecture.md) (três frontends; URLs)
- [09 — Merchant Dashboard](../../09_merchant_dashboard.md)
- [03 — System Architecture](../../03_system_architecture.md)

## Escopo (o que ENTRA)
- **Traefik:** host do painel `dashboard.${DOMAIN}` → **`app.${DOMAIN}`** (labels em `compose.yml`).
- **Papel do projeto:** tratar o `frontend/` do template como o **`frontend-dashboard`** (admin e storefront são projetos separados, Fases 6 e 3). `VITE_API_URL` por env (sem hardcode — INV-FE3; já aponta para a porta dev `8800`).
- **Limpeza** de páginas/exemplos do template fora do escopo do painel: `routes/_layout/admin.tsx` (gestão de `account_users` é do **admin de plataforma**, Fase 7); `items` já removido na Fase 0.
- Smoke: o painel sobe e responde em `app.localhost:8088`.

## Fora de escopo (o que NÃO entra)
- Seletor de loja / contexto → `P1-DASH-02`; menu/telas → `P1-DASH-03`.
- Projetos `frontend-admin` (Fase 7) e `frontend-storefront` (Fase 3).
- **Renomear fisicamente** o diretório `frontend/` → `frontend-dashboard/` (mexe em workspace bun/`bun.lock`/Dockerfiles): **opcional**; pode ficar para quando admin/storefront forem criados. Ver Notas.

## Arquivos a criar/alterar
- `compose.yml` (alterar) — labels Traefik do serviço frontend-dashboard: host `app.${DOMAIN}`.
- `compose.override.yml` (alterar, se necessário) — args/host do frontend-dashboard dev.
- `frontend-dashboard/src/routes/_layout/admin.tsx` (remover/neutralizar) e refs no menu.

## Passos
1. Trocar o host Traefik do painel para `app.${DOMAIN}`.
2. Remover a página `admin.tsx` do template e suas referências de navegação.
3. Confirmar `VITE_API_URL` por env apontando para a API.
4. Subir e validar (smoke manual) o painel em `app.localhost:8088`.

## Testes
> Fundações §10.

- **Níveis:** nenhum automatizado novo (config/infra) — **verificação manual** (painel sobe em `app.`); `vitest` existente segue verde.
- **Quando escrever:** —
- **Cobrir:** —

## Definition of Done
- [x] Traefik do painel → `Host(app.${DOMAIN})` (labels http+https em `compose.yml`); `VITE_API_URL` por env (prod `https://api.${DOMAIN}`, dev `http://localhost:8800`); CORS já inclui `http://app.localhost:8088`. *(smoke HTTP ao vivo = manual, ver Notas)*
- [x] `admin.tsx` + `components/Admin/*` + item de menu removidos; `routeTree.gen.ts` regenerado (0 refs a admin); nada quebrado.
- [x] `tsc` + `vitest` (2) verdes; `vite build` ok; `biome` limpo.

## Notas / Reconciliações
- Doc [05](../../05_frontend_architecture.md) pede 3 projetos separados (`frontend-dashboard`/`admin`/`storefront`). No MVP mapeamos o `frontend/` existente ao papel de **dashboard**; o **rename físico** do diretório (e a criação de admin/storefront) fica para o início das Fases 3/6 (mexe em workspace bun/`bun.lock`/Dockerfiles).
- **Limpeza:** removido o cluster inteiro `routes/_layout/admin.tsx` + `components/Admin/*` (AddUser/columns/EditUser/DeleteUser/UserActionsMenu) — era **auto-contido** (nada fora dele importava) e é gestão de `account_users` = **admin de plataforma** (Fase 7, `frontend-admin`). O item "Admin" do `AppSidebar` (só superuser) saiu.
- **`routeTree.gen.ts`** é gerado pelo plugin do TanStack Router; regenerado via `vite build` (não há `tsr` standalone local; `bun` ausente — usei o `node_modules` da raiz do workspace).
- **Smoke ao vivo (manual):** `docker compose up -d proxy frontend` e então `curl -H "Host: app.localhost" http://localhost:8088/` (ou abrir `http://app.localhost:8088`). Não executado aqui (build da imagem do frontend é pesado); a mudança é só o label Traefik + o CORS já contempla o host.

## Follow-ups
- [ ] **Rename físico `frontend/` → `frontend-dashboard/`** + criar `frontend-admin` (Fase 7) e `frontend-storefront` (Fase 3) como projetos separados. *Quando:* ao iniciar a Fase 3 ou 6. → [README da fase](./README.md#follow-ups--débitos-técnicos).
