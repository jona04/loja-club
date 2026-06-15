---
id: P7-CAT-01
title: Catálogo 3D da plataforma — tabelas + seed da caneca
phase: 7
etapa: "Etapa 1 — Catálogo público de modelos 3D (plataforma, via seed)"
area: CAT
status: done
depends_on: [P7-ASSET-01]
blocks: [P7-ADM-01, P7-PROD-01]
tests: [integration]
---

# P7-CAT-01 — Catálogo 3D da plataforma (tabelas + seed)

## Contexto
A plataforma mantém um **catálogo público de modelos 3D** (sem `store_id`), populado por **seed** pelo dev — padrão do registro de templates (Fase 4). O lojista depois **escolhe** desse catálogo (`P7-PROD-01`). A caneca é o 1º modelo.

## Docs de referência
- [30 — §3 Área imprimível / §8 Campos](../../concepts/30_3d_customization_technical_design.md)
- [07 — Personalização 3D + índices](../../concepts/07_database_strategy.md)

## Escopo (o que ENTRA)
- Módulo `customization` (backend): `platform_3d_models` (`name`, `category`, `slug`, `is_active`, soft delete) + `platform_3d_model_versions` (`model_id`, `version`, `glb_url`, `printable_areas` JSON, `text_config` JSON, `art_limits` JSON, `is_active`). Migration.
- **Índices:** `platform_3d_models (slug único quando ativo / category)`, `platform_3d_model_versions (model_id+version único)`.
- **Seed da caneca:** `glb_url` (CDN, de `P7-ASSET-01`) + `printable_areas` (projetor da faixa frontal, doc [30 §3](../../concepts/30_3d_customization_technical_design.md)) + `text_config` (fontes/limites) + `art_limits` (mimes/tamanho/dimensão mín). Análogo a `seed_content_templates`.
- Rota pública (catálogo habilitado) consumível pelo painel do lojista (`P7-PROD-01`).

## Fora de escopo (o que NÃO entra)
- **Otimizar/subir o GLB:** `P7-ASSET-01`.
- **Admin** (habilitar/desabilitar + editar área): `P7-ADM-01`.
- **Vincular ao produto** (por loja): `P7-PROD-01`.
- **Modelos por loja** (gerados via API): **Fase 12** (`customization_3d_models`).

## Arquivos a criar/alterar
- `backend/app/modules/customization/{models,enums,schemas,repositories,services,routes}.py` (criar/alterar).
- `backend/app/models_registry.py` (alterar) — registrar os models.
- seed (em `app/core/db.py` ou `customization/seed.py`) — caneca.
- migration alembic (autogenerate → revisar FKs → `alembic check` vazio).

## Passos
1. Models platform-owned + migration (índices).
2. Seed da caneca (GLB do CDN + áreas/limites JSON).
3. Rota de listagem do catálogo (modelos ativos) + schemas públicos.

## Testes
- **Níveis:** integração.
- **Quando escrever:** durante.
- **Cobrir:** integração — seed cria a caneca com 1 área; `slug`/`model_id+version` únicos; listagem retorna só `is_active`.

## Definition of Done
- [x] Tabelas + índices + migration (`c7c6df86b5d9`, `alembic check` **vazio**); seed da caneca aplicado.
- [x] **Modos de falha mapeados** — re-seed **idempotente** (testado); slug único entre ativos (índice parcial, testado); versão sem GLB no CDN → Follow-up de validação. → tratados/Follow-ups.
- [x] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Campos/índices conferem com o doc [07](../../concepts/07_database_strategy.md).
- **Implementação:** módulo `app/modules/customization/` (`models`/`storage`/`schemas`/`repositories`/`services`/`routes`) — platform-owned (sem `store_id`). Rota `GET /api/v1/3d-catalog/models` (autenticada). Seed da caneca em `init_db`. 7 testes de integração ✅.
- **Slug = fonte única (resolve a observação):** o `glb_url` é **derivado** de `slug`+`version` por `customization.storage.model_glb_key/url`, e o **mesmo helper** é usado no `backend/scripts/upload_glb.py` (`P7-ASSET-01`) — impossível o caminho do CDN divergir do catálogo. Verificado: a URL semeada == objeto live (HTTP 200, 2.05 MB). O **slug é único** entre ativos (índice parcial `WHERE deleted_at IS NULL`).
- **Área imprimível semeada = valor inicial** (`uv_rect` placeholder); calibração visual fica no admin (`P7-ADM-01`).

## Follow-ups
- [ ] **Validar que o GLB existe na chave do slug** no seed/upload — hoje um slug com typo gera `glb_url` que **404** silenciosamente (o acoplamento slug↔caminho está garantido, mas não a existência do objeto). *Quando:* ao automatizar o upload pelo admin (cruza com `P7-ASSET-01`). → README da fase.
- [ ] **Calibrar a região de UV imprimível da caneca** — o seed traz `uv_rect` placeholder. *Quando:* `P7-ADM-01` (picker 2D + preview 3D). → README da fase.
- [ ] **Múltiplas áreas imprimíveis** (ex.: camiseta frente/verso) — a caneca usa **1**; o schema suporta N. *Quando:* ao entrar um modelo multi-face. → README da fase.
