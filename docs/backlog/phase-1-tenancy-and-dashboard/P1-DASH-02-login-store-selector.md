---
id: P1-DASH-02
title: Login + seletor de loja ativa + contexto
phase: 1
etapa: "Etapa 7 — Painel do lojista"
area: DASH
status: done
depends_on: [P1-STORE-02, P1-DASH-01]
blocks: [P1-DASH-03]
tests: [unit, e2e]
---

# P1-DASH-02 — Login + seletor de loja ativa + contexto

## Contexto
Um usuário pode ser membro de várias lojas; o painel precisa, após o login, **resolver a loja ativa** e usá-la como contexto de todas as chamadas (`/stores/{store_id}/...`) — doc [09](../../09_merchant_dashboard.md)/[05](../../05_frontend_architecture.md).

## Docs de referência
- [09 — Merchant Dashboard](../../09_merchant_dashboard.md) ("Seleção de loja ativa")
- [05 — Frontend Architecture](../../05_frontend_architecture.md) ("Seleção de loja ativa no dashboard")

## Escopo (o que ENTRA)
- **Login** reaproveitando `routes/login.tsx` + `hooks/useAuth.ts` (já no template).
- Após login: `GET /stores` (minhas lojas, de `P1-STORE-02`). **1 loja → entra direto**; **várias → seletor**.
- **Contexto de loja ativa** (provider/hook) que persiste a escolha e injeta o `store_id` nas chamadas do painel.
- **Store switcher** no header ("Loja atual: … ▼").
- **Regenerar o client OpenAPI** para os endpoints de `stores` (`P1-STORE-02`).

## Fora de escopo (o que NÃO entra)
- Menu dinâmico por permissão e telas (dashboard/settings/equipe) → `P1-DASH-03`.
- Criação de loja por onboarding (checklist) → pode entrar em `P1-DASH-03`/fase posterior.

## Arquivos a criar/alterar
- `frontend-dashboard/src/client/*` (regenerar) — endpoints de stores.
- `frontend-dashboard/src/` — contexto/hook de loja ativa (ex.: `hooks/useActiveStore.ts`), componente de seletor, guarda de rota pós-login.
- `frontend-dashboard/src/routes/_layout.tsx` (alterar) — header com switcher.

## Passos
1. Regenerar o client após `P1-STORE-02`.
2. Buscar `GET /stores` no pós-login; decidir entre entrar direto (1) ou mostrar seletor (várias).
3. Criar o contexto de loja ativa e propagar `store_id` nas chamadas.
4. Switcher no header; persistir seleção.

## Testes
> Fundações §10. Lógica de seleção é pura (unit no front, `vitest`); jornada é E2E.

- **Níveis:** unit (`vitest`, comportamento do seletor) · E2E (Playwright, poucos).
- **Quando escrever:** durante.
- **Cobrir:**
  - unit — 1 loja entra direto; várias mostram seletor; trocar loja troca o contexto.
  - e2e — login → (seletor) → painel carregado no contexto da loja.

## Definition of Done
- [x] Pós-login resolve a loja ativa — `lib/activeStore.ts` (`resolveActiveStore`, pura + unit) + `ActiveStoreProvider`: 1 entra direto, várias → `StoreSelector`, 0 → `NoStores`.
- [x] Contexto fornece `activeStore.id` + `role`/`permissions` (via `GET /stores/{id}/me`) e o `StoreSwitcher` no header troca/persiste a loja.
- [x] Client OpenAPI regenerado (endpoints `stores`); `vitest` (8) / `tsc` / `vite build` / `biome` verdes.
- [x] Itens adiados varridos → Follow-ups + README (E2E ao vivo; onboarding completo).

## Notas / Reconciliações
- **Persistência:** `localStorage["active_store_id"]`. Resolução pura em `lib/activeStore.ts` (testada): 0 → `NoStores` (CTA "Criar loja", dialog mínimo nome → `POST /stores` → ativa a nova); várias sem escolha válida → `StoreSelector`; 1 ou escolha persistida válida → entra. Estado, não URL (URL com `store_id` pode vir depois se preciso).
- **store_id é path param:** o contexto expõe `activeStore.id` + `permissions`/`role` (de `/me`) que a `P1-DASH-03` consome no menu por permissão — é a "injeção" do `store_id` nas chamadas do painel.
- **Client:** regenerado via dump `uv run … app.openapi()` + `openapi-ts`/`biome` pelo `node_modules` da raiz (bun ausente; `frontend-dashboard/openapi.json` é artefato gitignored).
- **E2E (impacto):** a suíte Playwright assertava "Welcome back" (removido) e o pós-login virou **gated por loja** (superuser tem 0 lojas → `NoStores`). Troquei os 4 asserts por `user-menu` (estável no novo fluxo). **Não rodei a suíte ao vivo** (precisa do stack) — ver Follow-ups. Removi `tests/admin.spec.ts` (órfão da página admin removida na `P1-DASH-01`).
- **Correção pós-vistoria (gating de rota):** o gating de loja saiu do `_layout` para um `StoreGate` por rota de loja (Dashboard/Configurações/Equipe). Antes o layout escondia **todas** as rotas — inclusive `/settings` (conta) — no estado "sem loja"; agora rotas não-loja ficam acessíveis sem loja ativa.

## Follow-ups
- [ ] **Rodar/validar a suíte Playwright ao vivo** no fluxo store-aware **+ escrever o E2E da jornada** DASH-02 (login → sem-loja → criar → painel; várias → seletor). *Quando:* com o stack de pé. → [README da fase](./README.md#follow-ups--débitos-técnicos).
- [ ] **Onboarding de loja completo** (checklist) — hoje só o CTA mínimo de criar. *Quando:* `P1-DASH-03` ou fase posterior. → README da fase.
