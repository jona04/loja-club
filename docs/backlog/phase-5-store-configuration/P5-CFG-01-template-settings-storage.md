---
id: P5-CFG-01
title: content_store_template_settings + API (storage dos settings)
phase: 5
etapa: "Etapa 2 — Settings: storage + API"
area: CFG
status: todo
depends_on: [P4-TPL-01]
blocks: [P5-CFG-02, P5-SF-01]
tests: [integration]
---

# P5-CFG-01 — Settings por template: storage + API

## Contexto
O `settings_schema` vem do **código** (seedado em `content_theme_templates` na Fase 4). Esta task entrega o **armazenamento dos valores** do lojista (por loja × template) + as APIs pública (vitrine) e do painel.

## Docs de referência
- [26 — Sistema de templates](../../concepts/26_template_system.md) (§"Personalização schema-driven")
- [07 — Database Strategy](../../concepts/07_database_strategy.md) (`content_store_template_settings`)
- [08 — Modules and Permissions](../../concepts/08_modules_and_permissions.md) (`layout.*`)

## Escopo (o que ENTRA)
- **Modelo `content_store_template_settings`** (`store_id`, `template_id`, `settings` jsonb, soft delete; **único por (store, template) entre ativos** — índice parcial `deleted_at IS NULL`).
- **API pública** (vitrine): `StorefrontTheme.settings` = **defaults do schema ⊕ overrides** da loja, do template **ativo**; **invalida cache** (`store:{id}:theme|home|settings`) ao salvar.
- **API painel:** `GET …/templates` devolve o `settings_schema`; `GET/PATCH …/layout/settings` lê/grava (**validado contra o schema**; gating `layout.update`); `DELETE …/layout/settings` **reseta** (soft-delete a linha → re-selecionar zera).

## Fora de escopo (o que NÃO entra)
- O **form** no painel: `P5-CFG-02`.
- A **vitrine lendo** `theme.settings`: `P5-SF-01`.
- Os settings **universais** (`content_store_theme_settings`: banner/headline/cor) — já existem (Fase 3).

## Arquivos a criar/alterar
- `backend/app/modules/content/models.py` (alterar) — `ContentStoreTemplateSettings`.
- `backend/app/modules/content/{schemas,services,routes}.py` (alterar) — DTOs + merge + rotas.
- `backend/app/alembic/versions/*` (criar) — tabela + índice parcial.
- (doc 07 já tem a tabela/índice.)

## Passos
1. Modelo + migration (índice parcial único por par ativo).
2. Serviço de **merge** (defaults do schema ⊕ overrides) + validação do PATCH contra o schema.
3. Rotas painel (GET/PATCH/DELETE, gated `layout.update`) + a pública (`theme.settings`).
4. Invalida cache ao salvar/resetar.

## Testes
- **Níveis:** integração.
- **Quando escrever:** antes (contrato do merge claro).
- **Cobrir:** integração — merge (default quando vazio, override quando preenchido), validação (chave fora do schema rejeitada), reset (soft-delete → volta ao default), único por par, cache invalidado, gating `layout.update`.

## Definition of Done
- [ ] Tabela + índice parcial; `alembic check` vazio.
- [ ] Pública devolve `theme.settings` (defaults ⊕ overrides) do template ativo.
- [ ] Painel GET/PATCH/DELETE gated `layout.update`; PATCH validado vs schema; DELETE reseta.
- [ ] Cache invalidado ao salvar/resetar.
- [ ] **Modos de falha mapeados** (chave fora do schema, par duplicado, template sem schema seedado) → tratados ou Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- —

## Follow-ups
- [ ] — nenhum (preencher ao implementar).
