---
id: P1-DASH-03
title: Menu dinâmico por permissão + telas (dashboard, configurações, equipe)
phase: 1
etapa: "Etapa 7 — Painel do lojista"
area: DASH
status: done
depends_on: [P1-DASH-02, P1-PERM-03, P1-STORE-02]
blocks: []
tests: [unit, e2e]
---

# P1-DASH-03 — Menu dinâmico por permissão + telas base

## Contexto
O painel mostra um **menu modular** em que cada módulo só aparece se o papel do usuário permite (e, na Fase 8, se o plano permite) — doc [05](../../05_frontend_architecture.md)/[09](../../09_merchant_dashboard.md)/[08](../../08_modules_and_permissions.md). Esta task entrega o menu dinâmico e as **telas base** da Fase 1 (dashboard, configurações, equipe). A segurança real está no backend (`P1-PERM-03`); o front esconder módulo é só UX.

## Docs de referência
- [09 — Merchant Dashboard](../../09_merchant_dashboard.md) (menu, configurações, equipe, estados da loja)
- [05 — Frontend Architecture](../../05_frontend_architecture.md) ("Roteamento por permissão")
- [08 — Modules and Permissions](../../08_modules_and_permissions.md) (módulo ↔ permissão base)

## Escopo (o que ENTRA)
- **Menu modular dinâmico:** módulo aparece só se o papel do membro tem a permissão base (`*.view`). Gancho para gating de plano (Fase 8). Consome as **permissões do membro na loja ativa** expostas pela API.
- **Dashboard inicial** (esqueleto; métricas reais conforme dados existirem em fases seguintes) — doc [09](../../09_merchant_dashboard.md).
- **Configurações da loja** (nome, descrição, logo, contato, redes, WhatsApp, status publicada) → `PATCH /stores/{store_id}/settings`.
- **Equipe** (listar membros, convidar, alterar papel, remover) → endpoints de equipe de `P1-STORE-02`.
- Esconder módulo/ações sem permissão (UX); ações de salvar exigem a permissão (ex.: sem `layout.update` vê, mas não salva).

## Fora de escopo (o que NÃO entra)
- Telas dos demais módulos (Produtos/Pedidos/etc.) → fases respectivas (só o item de menu, desabilitado/placeholder).
- **Gating por plano** → Fase 8 (só o gancho).
- Admin de plataforma → Fase 4.

## Arquivos a criar/alterar
- `frontend-dashboard/src/` — componente de menu/sidebar dinâmico; rotas/telas de Dashboard, Configurações e Equipe; hook de permissões do membro ativo.
- Regenerar client OpenAPI se a API expuser novo campo de permissões/membro.

## Passos
1. Garantir que a API expõe **papel/permissões do membro na loja ativa** (campo no `GET /stores` ou `/stores/{id}/me`); se faltar, adicionar (pequeno, no módulo `stores`).
2. Menu dinâmico a partir dessas permissões.
3. Telas de Configurações (form → PATCH settings) e Equipe (CRUD de membros).
4. Dashboard inicial (esqueleto com atalhos).

## Testes
> Fundações §10.

- **Níveis:** unit (`vitest`, visibilidade do menu por permissão) · E2E (poucos: settings/equipe).
- **Quando escrever:** durante.
- **Cobrir:**
  - unit — menu esconde módulo sem permissão; ação de salvar desabilitada sem a permissão.
  - e2e — salvar configurações reflete; convidar/alterar papel/remover membro na tela de Equipe.

## Definition of Done
- [x] Menu modular dinâmico — `lib/menu.ts` (`buildMenu`, pura + unit) + `AppSidebar` consome `permissions`; gancho de plano `planAllowsModule` (Fase 8).
- [x] Telas: Dashboard (esqueleto + atalhos), Configurações (load `GET` + save `PATCH` gated por `settings.update` + publish/pause) e Equipe (listar/convidar/alterar papel/remover, ações gated por `team.*`) contra a API.
- [x] `tsc`/`vitest` (14) verdes; build/biome ok. **E2E base deferido** (precisa do stack — ver Follow-ups).
- [x] Itens adiados varridos → Follow-ups + README.

## Notas / Reconciliações
- **API:** as permissões do membro ativo já vêm de `GET /stores/{id}/me` (exposto na `P1-DASH-02`/`useActiveStore`). Adicionei **`GET /stores/{id}/settings`** (gated `settings.view`) — o form precisa carregar os valores e só havia `PATCH`; consistente com o contrato (doc [20](../../20_api_contracts_todo.md) não enumera endpoints, só a convenção de URL). Client regenerado.
- **Menu:** `buildMenu(permissions)` — módulo aparece se permissão base (ou `null`) + `planAllowsModule` (stub Fase 8). 3 módulos reais (Dashboard/Configurações/Equipe); itens placeholder de outros módulos ficam para suas fases (evitei links 404).
- **Gating é UX:** segurança real é o backend (`P1-PERM-03`). Save desabilitado sem `settings.update` (com unit); ações de equipe escondidas sem `team.*`.

## Follow-ups
- [ ] **E2E do painel** (settings salvar; equipe convidar/alterar papel/remover) — rodar ao vivo. *Quando:* com o stack de pé (junto do Playwright da `P1-DASH-02`). → [README da fase](./README.md#follow-ups--débitos-técnicos).
- [ ] **Campo de redes sociais (`social_links`)** no form de Configurações (é dict; não entrou no MVP). *Quando:* quando o storefront precisar exibir redes. → README da fase.
