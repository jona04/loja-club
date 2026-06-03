---
id: P1-DASH-02
title: Login + seletor de loja ativa + contexto
phase: 1
etapa: "Etapa 4 — Painel do lojista"
area: DASH
status: todo
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
- `frontend/src/client/*` (regenerar) — endpoints de stores.
- `frontend/src/` — contexto/hook de loja ativa (ex.: `hooks/useActiveStore.ts`), componente de seletor, guarda de rota pós-login.
- `frontend/src/routes/_layout.tsx` (alterar) — header com switcher.

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
- [ ] Pós-login resolve loja ativa (1 direto / várias com seletor).
- [ ] Contexto injeta `store_id` nas chamadas do painel; switcher funciona.
- [ ] Client OpenAPI regenerado; `vitest`/`tsc` verdes.

## Notas / Reconciliações
- Registrar como a loja ativa é persistida (estado/URL) e o comportamento ao não haver nenhuma loja (CTA de criar loja).
