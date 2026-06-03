---
id: P1-DASH-03
title: Menu dinâmico por permissão + telas (dashboard, configurações, equipe)
phase: 1
etapa: "Etapa 4 — Painel do lojista"
area: DASH
status: todo
depends_on: [P1-DASH-02, P1-PERM-03, P1-STORE-02]
blocks: []
tests: [unit, e2e]
---

# P1-DASH-03 — Menu dinâmico por permissão + telas base

## Contexto
O painel mostra um **menu modular** em que cada módulo só aparece se o papel do usuário permite (e, na Fase 5, se o plano permite) — doc [05](../../05_frontend_architecture.md)/[09](../../09_merchant_dashboard.md)/[08](../../08_modules_and_permissions.md). Esta task entrega o menu dinâmico e as **telas base** da Fase 1 (dashboard, configurações, equipe). A segurança real está no backend (`P1-PERM-03`); o front esconder módulo é só UX.

## Docs de referência
- [09 — Merchant Dashboard](../../09_merchant_dashboard.md) (menu, configurações, equipe, estados da loja)
- [05 — Frontend Architecture](../../05_frontend_architecture.md) ("Roteamento por permissão")
- [08 — Modules and Permissions](../../08_modules_and_permissions.md) (módulo ↔ permissão base)

## Escopo (o que ENTRA)
- **Menu modular dinâmico:** módulo aparece só se o papel do membro tem a permissão base (`*.view`). Gancho para gating de plano (Fase 5). Consome as **permissões do membro na loja ativa** expostas pela API.
- **Dashboard inicial** (esqueleto; métricas reais conforme dados existirem em fases seguintes) — doc [09](../../09_merchant_dashboard.md).
- **Configurações da loja** (nome, descrição, logo, contato, redes, WhatsApp, status publicada) → `PATCH /stores/{store_id}/settings`.
- **Equipe** (listar membros, convidar, alterar papel, remover) → endpoints de equipe de `P1-STORE-02`.
- Esconder módulo/ações sem permissão (UX); ações de salvar exigem a permissão (ex.: sem `layout.update` vê, mas não salva).

## Fora de escopo (o que NÃO entra)
- Telas dos demais módulos (Produtos/Pedidos/etc.) → fases respectivas (só o item de menu, desabilitado/placeholder).
- **Gating por plano** → Fase 5 (só o gancho).
- Admin de plataforma → Fase 6.

## Arquivos a criar/alterar
- `frontend/src/` — componente de menu/sidebar dinâmico; rotas/telas de Dashboard, Configurações e Equipe; hook de permissões do membro ativo.
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
- [ ] Menu modular dinâmico por permissão (com gancho de plano para a Fase 5).
- [ ] Telas de Dashboard (esqueleto), Configurações e Equipe funcionando contra a API.
- [ ] `vitest`/`tsc` verdes; E2E base do painel passa.

## Notas / Reconciliações
- A visibilidade no front é **UX**; a autorização real é a de `P1-PERM-03`. Se a API precisar de um endpoint de "permissões do membro ativo", registrar aqui e manter o doc [08](../../08_modules_and_permissions.md)/[20](../../20_api_contracts_todo.md) coerentes.
