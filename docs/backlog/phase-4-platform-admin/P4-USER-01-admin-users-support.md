---
id: P4-USER-01
title: Usuários + suporte no admin — listar/ver + impersonation auditada
phase: 4
etapa: "Etapa 2 — Operação: lojas, usuários, planos, suporte"
area: USER
status: todo
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
- [ ] Listar/ver usuários + impersonation **auditada**; guard de soft-delete em leitura por id corrigido.
- [ ] **Modos de falha / edge cases mapeados** → tratados ou Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Fecha o follow-up `P1-ACCT-01` ("Guard de soft-delete em leituras por id de admin") — marcar `[x]` na origem (README da Fase 1) ao concluir.

## Follow-ups
- [ ] — (preencher ao implementar) → README da fase.
