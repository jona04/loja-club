---
id: P0-MOD-03
title: Remover exemplo items
phase: 0
etapa: "Etapa 2 — Refatoração modular"
area: MOD
status: done
depends_on: [P0-MOD-02]
blocks: [P0-CI-01]
tests: [integration]
---

# P0-MOD-03 — Remover exemplo `items`

## Contexto
O template traz um CRUD de exemplo (`Item`) que não faz parte da Loja Club. Removê-lo limpa o backend e o frontend antes de construir o catálogo real.

## Docs de referência
- [04 — FastAPI Template Adaptation](../../04_fastapi_template_adaptation.md)

## Escopo (o que ENTRA)
- Backend: remover `ItemBase/Item/ItemCreate/ItemUpdate/ItemPublic/ItemsPublic` de `app/models.py`; remover `create_item` de `app/crud.py`; remover `app/api/routes/items.py` e seu include em `app/api/main.py`.
- Remover a relação `items` em `User` (em `app/models.py`).
- Testes: remover `backend/tests/api/routes/test_items.py` e `backend/tests/utils/item.py` (e referências).
- Frontend: remover `frontend/src/routes/_layout/items.tsx` e `frontend/src/components/Items/`.
- Migration Alembic dropando a tabela `item` (dev: perda de dados aceitável).

## Fora de escopo (o que NÃO entra)
- Mexer no `User` além de remover a relação `items` → `P0-MOD-04`.
- Regenerar o client OpenAPI / ajustar CI → `P0-CI-01`.

## Arquivos a criar/alterar
- `backend/app/models.py` (alterar) — remover modelos de Item + relação.
- `backend/app/crud.py` (alterar) — remover `create_item`.
- `backend/app/api/routes/items.py` (remover).
- `backend/app/api/main.py` (alterar) — remover include de items.
- `backend/tests/api/routes/test_items.py` (remover); `backend/tests/utils/item.py` (remover).
- `frontend/src/routes/_layout/items.tsx` (remover); `frontend/src/components/Items/` (remover).
- `backend/app/alembic/versions/xxxx_drop_item.py` (criar).

## Passos
1. Remover modelos/relacionamento e `create_item`.
2. Remover rota e include.
3. Remover testes e utilitários de item.
4. Remover páginas/componentes de item no frontend.
5. Gerar migration que dropa a tabela `item` e aplicar.

## Testes
> Fundações §10.

- **Níveis:** integração/smoke (+ remoção dos testes de item).
- **Quando:** durante.
- **Cobrir:**
  - integração — app sobe sem `items`; migration dropa a tabela `item`; suíte passa sem testes de item.
  - remover `test_items.py` e os utilitários de item.

## Definition of Done
- [x] App sobe sem referência a `items` (backend: models/crud/routes/main/users; frontend: rota/componentes/nav). *(68 testes; `vite build` ok)*
- [x] Migration `f0a1b2c3d4e5` dropa `item` e roda limpa (`alembic upgrade head` em db do zero → só `user` + `alembic_version`).
- [x] Sem testes de item; suíte passa (68).

## Notas / Reconciliações
- Remoção é física aqui (exemplo do template, não registro de negócio); o soft delete vale para entidades de negócio (doc 07/14).
- **Implementado:** Item saiu de `models.py` (+ import `Relationship`), `crud.py` (`create_item` + `import uuid`), `routes/items.py` (rm), `api/main.py`, e **`users.py`** (import `Item` + cleanup no `delete_user` — referência que faltava). Migration `f0a1b2c3d4e5` (drop item). Frontend: `items.tsx`, `components/Items/`, entrada do `AppSidebar` (+ ícone `Briefcase`); route tree regenerado por `vite build`.
- **Pendente p/ P0-CI-01:** o client OpenAPI (`src/client`) ainda exporta `ItemsService`/`ItemPublic` (gerado) — sai ao regenerar o client.
- O db de dev agora está **migration-managed** (após `alembic upgrade head`); os testes seguem com `create_all` por cima (idempotente).
