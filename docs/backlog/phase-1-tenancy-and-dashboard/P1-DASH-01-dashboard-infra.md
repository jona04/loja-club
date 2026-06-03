---
id: P1-DASH-01
title: Infra do painel (frontend-dashboard, Traefik app.)
phase: 1
etapa: "Etapa 4 — Painel do lojista"
area: DASH
status: todo
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
- **Limpeza** de páginas/exemplos do template fora do escopo do painel: `routes/_layout/admin.tsx` (gestão de `account_users` é do **admin de plataforma**, Fase 6); `items` já removido na Fase 0.
- Smoke: o painel sobe e responde em `app.loja.localhost:8088`.

## Fora de escopo (o que NÃO entra)
- Seletor de loja / contexto → `P1-DASH-02`; menu/telas → `P1-DASH-03`.
- Projetos `frontend-admin` (Fase 6) e `frontend-storefront` (Fase 3).
- **Renomear fisicamente** o diretório `frontend/` → `frontend-dashboard/` (mexe em workspace bun/`bun.lock`/Dockerfiles): **opcional**; pode ficar para quando admin/storefront forem criados. Ver Notas.

## Arquivos a criar/alterar
- `compose.yml` (alterar) — labels Traefik do serviço frontend: host `app.${DOMAIN}`.
- `compose.override.yml` (alterar, se necessário) — args/host do frontend dev.
- `frontend/src/routes/_layout/admin.tsx` (remover/neutralizar) e refs no menu.

## Passos
1. Trocar o host Traefik do painel para `app.${DOMAIN}`.
2. Remover a página `admin.tsx` do template e suas referências de navegação.
3. Confirmar `VITE_API_URL` por env apontando para a API.
4. Subir e validar (smoke manual) o painel em `app.loja.localhost:8088`.

## Testes
> Fundações §10.

- **Níveis:** nenhum automatizado novo (config/infra) — **verificação manual** (painel sobe em `app.`); `vitest` existente segue verde.
- **Quando escrever:** —
- **Cobrir:** —

## Definition of Done
- [ ] Painel responde em `app.${DOMAIN}` (Traefik), com `VITE_API_URL` por env.
- [ ] `admin.tsx` (e refs) removidos; nenhuma rota/menu quebrado.
- [ ] `vitest` e `tsc` do frontend verdes.

## Notas / Reconciliações
- Doc [05](../../05_frontend_architecture.md) pede 3 projetos separados (`frontend-dashboard`/`admin`/`storefront`). No MVP mapeamos o `frontend/` existente ao papel de **dashboard**; o rename físico do diretório (e a criação de admin/storefront) pode ocorrer ao iniciar Fases 3/6 — registrar a decisão tomada aqui.
