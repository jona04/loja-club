---
id: P0-MOD-04
title: Mover User para o módulo accounts (account_users)
phase: 0
etapa: "Etapa 2 — Refatoração modular"
area: MOD
status: todo
depends_on: [P0-MOD-01, P0-MOD-02]
blocks: [P0-CI-01, P1-STORE-01]
---

# P0-MOD-04 — Mover `User` para o módulo `accounts` (`account_users`)

## Contexto
O template guarda `User` em `app/models.py` (tabela `user`) e a lógica em `app/crud.py`. Os docs chamam essa entidade de `account_users` (usuários que acessam painel/admin). Esta task move o usuário para o módulo `accounts`, mantendo a autenticação funcionando.

## Docs de referência
- [04 — FastAPI Template Adaptation](../../04_fastapi_template_adaptation.md)
- [07 — Database Strategy](../../07_database_strategy.md)
- [08 — Modules and Permissions](../../08_modules_and_permissions.md)

## Escopo (o que ENTRA)
- Mover os modelos de usuário para `app/modules/accounts/models.py`, com `__tablename__ = "account_users"`, usando os mixins de `P0-MOD-01` onde fizer sentido (UUID/timestamps).
- Mover `create_user`/`update_user`/`get_user_by_email`/`authenticate` (de `app/crud.py`) para `accounts/repositories.py` + `accounts/services.py`.
- Mover as rotas de `login.py` e `users.py` para `accounts/routes.py` (manter os paths atuais por enquanto).
- Atualizar `app/api/deps.py` (`get_current_user`) e `app/core/db.py` (`init_db`) para os novos imports.
- Migration Alembic renomeando `user` → `account_users` (ou recriando a tabela).

## Fora de escopo (o que NÃO entra)
- Papéis/permissões por loja, `store_members`, `store_roles` → Fase 1 (`P1-PERM-*`/`P1-STORE-*`).
- Conceito de admin de plataforma e `platform_admin_roles` → Fase 6.
- Autenticação do cliente final (customer) → Fase 5.

## Arquivos a criar/alterar
- `backend/app/modules/accounts/models.py` (criar) — `AccountUser` (`__tablename__="account_users"`) + schemas de usuário.
- `backend/app/modules/accounts/repositories.py` + `services.py` (criar) — lógica vinda de `crud.py`.
- `backend/app/modules/accounts/routes.py` (criar) — login + users.
- `backend/app/api/deps.py` (alterar) — `get_current_user` usa `AccountUser`.
- `backend/app/core/db.py` (alterar) — `init_db` cria o superuser via accounts.
- `backend/app/crud.py` / `app/models.py` (alterar) — remover o que migrou (manter genéricos como `Message`, `Token`, etc., ou mover p/ `app/core`/`accounts`).
- `backend/app/alembic/versions/xxxx_rename_user_account_users.py` (criar).

## Passos
1. Criar `accounts/models.py` com `AccountUser` e schemas.
2. Migrar a lógica de `crud.py` para `repositories.py`/`services.py`.
3. Migrar rotas de login/users para `accounts/routes.py` e incluir no `api/main.py`.
4. Atualizar `deps.py` e `db.py`.
5. Gerar e aplicar a migration de rename para `account_users`.
6. Rodar o fluxo de login e recuperação de senha.

## Definition of Done
- [ ] Tabela criada/renomeada como `account_users` (migration aplica limpa).
- [ ] Login (`/login/access-token`), `test-token`, recuperação e reset de senha funcionam.
- [ ] `init_db` cria o `FIRST_SUPERUSER` na nova estrutura.
- [ ] Testes de usuário/login do template ajustados passam.

## Notas / Reconciliações
- Doc [07](../../07_database_strategy.md) usa `account_users`; o template usa `user`. Resolvido via `__tablename__`.
- `is_superuser` (template) **permanece** e, no MVP, cobre o acesso interno. O mapeamento para papéis globais de plataforma (`platform.*`) entra na Fase 6 — registrado aqui para não esquecer.
