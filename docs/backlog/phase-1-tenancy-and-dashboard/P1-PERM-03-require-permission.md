---
id: P1-PERM-03
title: Autorização — require_permission (deps)
phase: 1
etapa: "Etapa 4 — Módulos accounts ↔ stores"
area: PERM
status: done
depends_on: [P1-PERM-02, P1-TEN-01]
blocks: [P1-STORE-02, P1-DASH-03]
tests: [integration]
---

# P1-PERM-03 — Autorização: `require_permission` (deps)

## Contexto
A **segurança real está no backend** (esconder botão no front é só UX — INV-A4/S1). O doc [08](../../08_modules_and_permissions.md) define a regra de autorização: autenticado → membro da loja → papel tem a permissão → recurso pertence à loja. Esta task implementa a dependency que aplica isso nas rotas.

## Docs de referência
- [08 — Modules and Permissions](../../08_modules_and_permissions.md) ("Regra de autorização", "Plano + permissão")
- [14 — Security Strategy](../../14_security_strategy.md)
- [Fundações INV-S1/INV-A4](../_foundations-and-bottlenecks.md)

## Escopo (o que ENTRA)
- Dependency `require_permission("catalog.product.update")` que valida, em ordem:
  1. autenticado (`get_current_user`, Fase 0);
  2. **membro** da loja ativa (`get_active_store`, `P1-TEN-01`);
  3. papel do membro **tem a permissão** (`role_permissions`, `P1-PERM-02`);
  4. **gancho de plano** (stub que sempre permite no MVP; gating real na Fase 8).
- Resposta de negação padronizada (403) sem vazar se a loja existe (INV-T4).
- Verificação de **ownership do recurso** (`recurso.store_id == store_id`) como padrão a seguir nas rotas (INV-T2) — documentar/utilitário.

## Fora de escopo (o que NÃO entra)
- Lógica de **plano** (plano permite o recurso) → Fase 8 (só o gancho aqui).
- Overrides de permissão por membro (`store_member_permissions`) → criar só se necessário, fora desta task.
- Permissões globais de plataforma (`platform.*`) → Fase 4.

## Arquivos a criar/alterar
- `backend/app/api/deps.py` (alterar) **ou** `backend/app/modules/tenancy/deps.py` — `require_permission(perm)` (factory de dependency) + gancho de plano.
- (teste) uma rota protegida de exemplo para exercitar a dependency.

## Passos
1. Implementar `require_permission(perm)` compondo `get_current_user` + `get_active_store` + `role_permissions`.
2. Adicionar o gancho de plano (no-op no MVP, ponto de extensão p/ Fase 8).
3. Documentar o padrão de checagem de ownership (`store_id + id`).
4. Testes de integração com papéis distintos.

## Testes
> Fundações §10. Permissão na rota é **fronteira real** → integração.

- **Níveis:** integração.
- **Quando escrever:** durante.
- **Cobrir:**
  - integração — `owner` acessa rota protegida; `support` é **negado** em `layout.update`; não-membro → 403; permissão ausente → 403; recurso de outra loja → 404/403 (ownership).

## Definition of Done
- [x] `require_permission` aplica as checagens (autenticado → membro ativo → papel concede → plano) e nega no backend; teste *(111 testes; cobertura 92%)*.
- [x] Testes por papel (owner permitido / support negado / support permitido p/ permissão concedida) + não-membro (403) verdes.
- [x] Gancho de plano presente (`_plan_allows()`, no-op) para a Fase 8 plugar.

## Notas / Reconciliações
- **Implementado em `app/modules/tenancy/deps.py`:** extraí `get_active_membership` (valida loja+membership, reusado pelo `get_active_store` e pelo `require_permission`); `require_permission(perm)` compõe membership + checa a permissão **no banco** (`store_role_permissions` ⋈ `store_permissions`, consistente com a decisão de tabelas) + `_plan_allows()`.
- **Ownership (INV-T2):** a checagem `recurso.store_id == store_id` é o helper `get_store_scoped` (`P1-TEN-01`); as rotas comerciais o usam. Testado em `test_tenancy.py`.
- **Testes:** decisão por papel testada diretamente (chamando a dependency); não-membro/404 via `get_active_membership`. O **gating ponta-a-ponta por HTTP** numa rota real é exercitado na `P1-STORE-02` (endpoints com `Depends(require_permission(...))`).
- "Plano + permissão" (doc [08](../../08_modules_and_permissions.md)): no MVP só a permissão é ativa; o plano entra na Fase 8.
- **Typing:** `col()` no `onclause` do `join` (o SQLModel infere `bool` sem ele). **Lint deve rodar via `uv run bash scripts/lint.sh`** (o `lint.sh` chama `mypy`/`ty` diretos, que precisam do venv ativo).
