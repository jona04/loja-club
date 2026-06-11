---
id: P4-USER-01
title: Usuários + suporte no admin — listar/ver + impersonation auditada
phase: 4
etapa: "Etapa 2 — Operação: lojas, usuários, planos, suporte"
area: USER
status: done
depends_on: [P4-PLAT-01]
blocks: [P4-ADMIN-02]
tests: [integration]
---

# P4-USER-01 — Usuários + suporte (backend)

## Contexto
A gestão de `account_users` é do **admin**, não do painel do lojista. Inclui o **suporte com impersonation** (auditado) e fecha o follow-up da Fase 1 (guard de soft-delete em leitura por id).

## Docs de referência
- [25 — Platform Admin](../../25_platform_admin.md)
- [08 — Modules and Permissions](../../08_modules_and_permissions.md)
- [14 — Security Strategy](../../14_security_strategy.md)

## Escopo (o que ENTRA)
- Rotas `platform_admin` (gated `platform.users.view`): listar/ver `account_users` (paginado, busca por e-mail).
- **Guard de soft-delete em leitura por id** — `read_user_by_id`/`update_user` (via `session.get`) **não** retornam soft-deletados. *(fecha follow-up `P1-ACCT-01`)*
- **Impersonation** (suporte): gerar sessão **em nome** do usuário, **auditada obrigatoriamente** (`record_platform_action`), com escopo/limite explícito.

## Fora de escopo (o que NÃO entra)
- Telas → `P4-ADMIN-02`.
- Operação de lojas → `P4-STORE-01`. Planos → `P4-PLAN-01`.
- Auditoria completa/retenção → **Fase 9**.

## Arquivos a criar/alterar
- `app/modules/platform_admin/{services,routes,schemas}.py` (alterar) — usuários + impersonation.
- `app/modules/accounts/services.py` (alterar) — guard de soft-delete em `read_user_by_id`/`update_user`.

## Passos
1. Listar/ver usuários (cross-account, gated `platform.users.view`).
2. Corrigir `read_user_by_id`/`update_user` para excluir `deleted_at`.
3. Impersonation: emitir token/sessão em nome do usuário + `record_platform_action` (obrigatório).

## Testes
> Regra em [`_foundations-and-bottlenecks.md`](../_foundations-and-bottlenecks.md) §10.
- **Níveis:** integração.
- **Cobrir:** `read_user_by_id`/`update_user` não retornam soft-deletado; impersonation gera auditoria; gating `platform.*`.

## Definition of Done
- [x] Listar/ver usuários (gated `platform.users.view`) + **impersonation** (gated `platform.support.impersonate`) auditada em `audit_logs`; **guard de soft-delete** em leitura por id corrigido (`read_user_by_id`/`update_user`/`delete_user`).
- [x] **Modos de falha / edge cases mapeados** → Follow-ups.
- [x] **Itens adiados varridos** → Follow-ups + README.

> **Entregue:** `get_active_user()` em `accounts/repositories` (usado nas 3 rotas que faziam `session.get`) + rotas `/platform/users*` (listar/detalhe/impersonate) no `platform_admin`. Gate: **219 testes** (8 novos), cobertura **94%**, lint verde.

## Notas / Reconciliações
- **Fecha o follow-up da Fase 1** ("Guard de soft-delete em leituras por id de admin") — corrigido em `read_user_by_id`/`update_user`/`delete_user` via `get_active_user()`; marcado `[x]` na origem (`P1-ACCT-01` + README da Fase 1).
- **Layering:** os checks inline de `is_superuser` (`read_user_by_id`/`delete_user_me`) **não** foram migrados para papel aqui — `accounts` é módulo mais baixo e não deve importar `platform_admin`. Ficam até o campo `is_superuser` ser removido (follow-up da `P4-PLAT-01`).

## Follow-ups
- [ ] **Hardening da impersonation** (→ Fase 9): o token emitido é **igual a um login normal do alvo** — não marca que é impersonation do admin. Só o **evento de acesso** é registrado em `audit_logs`; as **ações feitas durante a impersonation NÃO são auditadas** (aparecem como do próprio usuário). Faltam: **marca de impersonation no token** + **auditoria das ações** da sessão + **expiração curta** / "parar de impersonar". → README da fase.
- A migração dos checks inline de `is_superuser` é follow-up da `P4-PLAT-01` (layering).
