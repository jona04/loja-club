---
id: P3-CONTENT-01
title: Módulo content — modelos de tema/layout
phase: 3
etapa: "Etapa 8 — Módulo de conteúdo/layout"
area: CONTENT
status: done
depends_on: []
blocks: [P3-CONTENT-02, P3-SF-01]
tests: [integration]
---

# P3-CONTENT-01 — Modelos do módulo `content`

## Contexto
A aparência da loja (template ativo, banner, headline, destaque) e conteúdo editorial (páginas, menus, banners). Separado de `store_settings` (Fase 1), que é a fonte de **contato/negócio**.

## Docs de referência
- [10 — Storefront & Layouts](../../10_storefront_and_layouts.md)
- [07 — Database Strategy](../../07_database_strategy.md)

## Escopo (o que ENTRA)
- `content_theme_templates` (**global**, sem `store_id`): `id` (`classic`/`modern`), `name`, `description`, `is_active`, `preview_image_url`. **Seed** dos dois.
- `content_store_theme_settings`: `store_id` (**único**), `active_template_id`, `banner_image_url`, `headline`, `featured_collection_id` + campos preparados (`primary_color`, `background_color`, `font_family`).
- `content_pages`, `content_menus`, `content_menu_items`, `content_banners` (`store_id` + soft delete).
- Migration + índices: `content_store_theme_settings.store_id` único, `content_menus.store_id+location`.

## Fora de escopo (o que NÃO entra)
- Serviço/rotas (aplicar template, editar) → `P3-CONTENT-02`.
- **`logo_url` e descrição da loja** ficam em `store_settings` (Fase 1) — **não** duplicar aqui (ver Reconciliações).
- Editor 3D / produtos 3D → Fase 7.

## Arquivos a criar/alterar
- `app/modules/content/{models,enums,schemas}.py` (criar).
- `app/alembic/versions/*` (criar) — tabelas + índices + seed dos templates.
- `app/models_registry.py` (alterar).

## Passos
1. Modelos com `StoreScopedMixin` (exceto `content_theme_templates`, **global**) + soft delete.
2. Migration autogenerate → revisar (FK ordenadas/nomeadas; índice único de `store_id`); `alembic check` vazio.
3. Seed `classic`/`modern` (idempotente, em `init_db` ou data migration).

## Testes
> Regra em [`_foundations-and-bottlenecks.md`](../_foundations-and-bottlenecks.md) §10.

- **Níveis:** integração.
- **Cobrir:** `store_theme_settings` único por loja; default = template padrão; isolamento por `store_id`; seed cria os 2 templates.

## Definition of Done
- [x] Tabelas + índices criados; migration `532902c21b7e` revisada (ordem de FK; partial unique do slug; `store_id` único no theme); **`alembic check` vazio**.
- [x] `classic`/`modern` seedados (`seed_content_templates` no `init_db`, idempotente); `store_theme_settings` único por loja (teste de integração).
- [x] **Modos de falha mapeados** → Follow-ups.
- [x] Itens adiados varridos → Follow-ups + README.

## Notas / Reconciliações
- **`store_settings` (Fase 1) × `content_store_theme_settings`:** o primeiro é contato/negócio (`public_name`, `description`, `logo_url`, `contact_*`); o theme é **só aparência**. `logo_url`/`description` ficam em `store_settings` — fora do theme.
- **`content_theme_templates` é global** (PK string `classic`/`modern`, sem `store_id`/soft-delete, seedado). Os demais são por loja + soft delete. `content_store_theme_settings` é **1-por-loja** (`store_id` único direto, como `store_settings`).
- **`content_menu_items`/`content_banners` recebem `store_id`** (invariante "store_id em toda tabela comercial") — doc [07](../../07_database_strategy.md) atualizado (lista de `store_id`).
- **`is_published` (page) / `is_active` (banner/template) têm serventia documentada:** lidos por `P3-SF-01`/`P3-CONTENT-02` (vitrine só serve publicado/ativo; só templates ativos são selecionáveis).
- FKs sem nome explícito = padrão das migrations existentes do projeto.

## Follow-ups
- [ ] **Default de theme settings** (`P3-CONTENT-01`): CONTENT-01 **não** cria row de theme por loja; loja sem row → vitrine usa `classic` (fallback **read-side** em `P3-SF-01`/`P3-CONTENT-02`).
- [ ] **`featured_collection_id` de coleção soft-deletada** (`P3-CONTENT-01`): o FK fica satisfeito (soft delete mantém a row), mas a vitrine deve **pular** coleção com `deleted_at` ao renderizar o destaque → tratar em `P3-SF-01`.
- [ ] **e2e polui o DB de host** (`P3-CONTENT-01`, infra): e2e (backend Docker) e testes de host usam o **mesmo** `loja-club-db` (host 5442 = container 5432); o e2e cria usuários que **persistem** e quebram o teste de isolamento (`count==1`). → e2e em DB separado **ou** limpeza pós-e2e. (Nesta entrega limpei 65 usuários `test_*@example.com`.)
