---
id: P0-MOD-02
title: Esqueleto de módulos
phase: 0
etapa: "Etapa 2 — Refatoração modular"
area: MOD
status: todo
depends_on: [P0-MOD-01]
blocks: [P0-MOD-03, P0-MOD-04]
---

# P0-MOD-02 — Esqueleto de módulos

## Contexto
O backend será um monólito **modular**: cada domínio em `app/modules/<nome>/` com a convenção de arquivos do doc 04. Esta task cria a estrutura e o agregador de routers — sem implementar lógica.

## Docs de referência
- [03 — System Architecture](../../03_system_architecture.md)
- [04 — FastAPI Template Adaptation](../../04_fastapi_template_adaptation.md)

## Escopo (o que ENTRA)
- Criar `app/modules/__init__.py` e os subpacotes que vamos usar até a Fase 4: `accounts`, `stores`, `tenancy`, `domains`, `catalog`, `media`, `product_customization`, `storefront`, `cart`, `checkout`, `orders`, `customers`, `shipping`, `discounts`, `notifications`, `audit`.
- Convenção por módulo (criar conforme uso, não arquivos vazios à toa): `models.py`, `schemas.py`, `routes.py`, `services.py`, `repositories.py`, `permissions.py`, `exceptions.py`.
- Registrar a convenção de **nome de tabela com prefixo de domínio** (INV-D3 / doc [07](../../07_database_strategy.md)): cada modelo define `__tablename__` explícito (ex.: `store_stores`, `catalog_products`), nunca o default do template.
- `app/api/main.py` agregando os routers dos módulos (substitui os includes do template).
- Garantir o import de todos os models antes do `init_db` (registry em `app/modules/__init__.py` ou `app/models_registry.py`).

## Fora de escopo (o que NÃO entra)
- Implementar qualquer regra de negócio dos módulos (fases seguintes).
- Remover `items` → `P0-MOD-03`.
- Mover `User` → `P0-MOD-04`.

## Arquivos a criar/alterar
- `backend/app/modules/__init__.py` (criar) + subpastas com `__init__.py`.
- `backend/app/api/main.py` (alterar) — agregação de routers.
- `backend/app/models_registry.py` (criar, opcional) — import central de models.

## Passos
1. Criar a árvore `app/modules/*`.
2. Definir o padrão de `routes.py` por módulo (router com prefixo/escopo).
3. Reescrever `app/api/main.py` para incluir os routers existentes via módulos.
4. Garantir o registry de models para o Alembic/`init_db`.

## Definition of Done
- [ ] `app/modules/` criado com os subpacotes e a convenção documentada.
- [ ] App sobe com `app/api/main.py` agregando routers (sem quebrar login/users por enquanto).
- [ ] Models são descobertos pelo Alembic (autogenerate enxerga as tabelas).

## Notas / Reconciliações
- A convenção de 7 arquivos vem do doc 04; criar só os que o módulo realmente usa.
