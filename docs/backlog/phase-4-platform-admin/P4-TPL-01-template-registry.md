---
id: P4-TPL-01
title: Registro de templates — CRUD + schema seedado do código
phase: 4
etapa: "Etapa 3 — Cadastro/gestão de templates"
area: TPL
status: done
depends_on: [P4-PLAT-01]
blocks: [P4-TPL-02, P4-ADMIN-03]
tests: [integration]
---

# P4-TPL-01 — Registro de templates (backend)

## Contexto
O admin gerencia o **registro** (dados) de um template; o **código** (componentes React + manifesto) vive no `frontend-storefront`. O **`settings_schema` vem do código** (manifesto), seedado no DB — o admin **não autora** os campos. Estende `content_theme_templates` (`P3-CONTENT-01`).

## Docs de referência
- [26 — Template System](../../26_template_system.md)
- [25 — Platform Admin](../../25_platform_admin.md)
- [08 — Modules and Permissions](../../08_modules_and_permissions.md) (`platform.templates.*`)
- [07 — Database Strategy](../../07_database_strategy.md)

## Escopo (o que ENTRA)
- Estender `content_theme_templates`: `settings_schema` (jsonb) + status (ativo/inativo) + descrição (campos que faltarem).
- **CRUD admin** (gated `platform.templates.manage`): criar/editar/ativar/desativar o registro de um template cujo código já existe na vitrine.
- **Seed do `settings_schema`** a partir do **`settings-schema.json` por template** (`frontend-storefront/templates/<id>/settings-schema.json` — fonte única, doc [26](../../26_template_system.md)) em `content_theme_templates.settings_schema`, **idempotente**.

## Fora de escopo (o que NÃO entra)
- Upload do **thumbnail pro CDN** → `P4-TPL-02`.
- **Import de imagens (chrome/demo), loja-demo e preview navegável** → **Fase 5**.
- Telas → `P4-ADMIN-03`.
- Consumo do schema pelo lojista (form) → **Fase 5**.

## Arquivos a criar/alterar
- `app/modules/content/{models,schemas,services}.py` (alterar) — `settings_schema`/status + CRUD admin.
- `app/modules/platform_admin/routes.py` (alterar) — rotas de template (gated `platform.templates.*`).
- `app/alembic/versions/*` (criar) — coluna `settings_schema` + seed.
- `frontend-storefront/templates/<id>/settings-schema.json` (criar) — manifesto por template (fonte única; o template React importa + o backend seeda).

## Passos
1. Migration: `settings_schema` + status em `content_theme_templates`.
2. CRUD admin gated `platform.templates.manage`.
3. Seed do `settings_schema` a partir do `settings-schema.json` por template, idempotente.
4. `alembic check` vazio.

## Testes
> Regra em [`_foundations-and-bottlenecks.md`](../_foundations-and-bottlenecks.md) §10.
- **Níveis:** integração.
- **Cobrir:** CRUD gated `platform.templates.*`; seed do schema idempotente; só template **ativo** é selecionável (consumo na vitrine/Fase 5); `alembic check` vazio.

## Definition of Done
- [x] `content_theme_templates` com `settings_schema` (JSON) + status (`is_active`); CRUD admin (`/platform/templates`) gated `platform.templates.view`/`manage`; schema **seedado** do `settings-schema.json` por template; `alembic check` vazio.
- [x] **Modos de falha mapeados** → tratados (id duplicado → 409, não-encontrado → 404) ou Follow-ups.
- [x] **Itens adiados varridos** → Follow-ups + README.

> **Entregue:** coluna `settings_schema` em `content_theme_templates` (migration `18847c0960d7`); `settings-schema.json` por template (aurora/bazar/studio) em `frontend-storefront/templates/<id>/`; o seed lê + sincroniza o schema; CRUD em `platform_admin`. Gate: **235 testes** (8 novos), cobertura **94%**, lint verde.

## Notas / Reconciliações
- **Schema vem do código** (manifesto `settings-schema.json` por template), não autorado no admin — evita divergência schema↔código (doc [26](../../26_template_system.md)). Reusa `content_theme_templates` (`P3-CONTENT-01`).
- **`platform.templates.*`** foi acrescentado ao catálogo do doc [08](../../08_modules_and_permissions.md) (sob `platform_catalog`/`platform_owner`) — não existia.
- **Mecanismo do seed:** o seed do `content` lê cada `settings-schema.json` (do `frontend-storefront`) e **sincroniza** `content_theme_templates.settings_schema` (insere o que falta; atualiza quando o JSON muda) — o JSON é a fonte única.

## Follow-ups
- [ ] **Empacotar os `settings-schema.json` no deploy do backend:** o seed lê de `frontend-storefront/templates/<id>/settings-schema.json` (caminho relativo). Na **imagem Docker do backend** esse diretório **não** está presente → o build precisa **copiar** os JSONs pro backend, senão o seed não encontra o schema (em deploy fica `null`). → README da fase.
- [ ] **Conteúdo do schema por template** (Fase 5): os `settings-schema.json` têm um conjunto **representativo** de campos; o schema completo de cada template + a vitrine lendo `theme.settings[key]` são a Fase 5. → README da fase.
