---
id: P3-CONTENT-01
title: Módulo content — modelos de tema/layout
phase: 3
etapa: "Etapa 8 — Módulo de conteúdo/layout"
area: CONTENT
status: todo
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
- Editor 3D / produtos 3D → Fase 5.

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
- [ ] Tabelas + índices criados; migration revisada; `alembic check` vazio.
- [ ] `classic`/`modern` seedados; `store_theme_settings` único por loja.
- [ ] **Modos de falha mapeados** (loja sem theme settings → usar default; `featured_collection_id` inexistente) → tratados ou Follow-up.
- [ ] Itens adiados varridos → Follow-ups + README, ou "nenhum".

## Notas / Reconciliações
- **`store_settings` (Fase 1) × `content_store_theme_settings`:** o primeiro é contato/negócio (`public_name`, `description`, `logo_url`, `contact_*`, `is_published`); o theme é **só aparência**. `logo_url`/`description` ficam em `store_settings` — fora do theme.

## Follow-ups
- (preencher ao executar)
