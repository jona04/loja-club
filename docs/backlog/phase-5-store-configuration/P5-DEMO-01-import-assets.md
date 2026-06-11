---
id: P5-DEMO-01
title: demo.json (aurora/bazar/studio) + import_assets (uxpilot → CDN)
phase: 5
etapa: "Etapa 4 — Loja-demo + import de assets"
area: DEMO
status: todo
depends_on: [P4-TPL-01, P4-TPL-02]
blocks: [P5-DEMO-02, P5-TPL-01]
tests: [integration]
---

# P5-DEMO-01 — Manifestos demo + import_assets

## Contexto
As imagens do template nascem com **URL do uxpilot** (no `demo.json` e nos defaults `image` do schema). O `import_assets` baixa → S3/CloudFront → reescreve pra URL de CDN. Acaba a dependência do uxpilot e de `public/` hardcoded.

## Docs de referência
- [26 — Sistema de templates](../../concepts/26_template_system.md) (§"Pipeline import_assets", §"Os artefatos")
- [27 — Guia de autoria](../../concepts/27_template_authoring_guide.md) (Passos 3 e 6)
- [13 — Performance, Cache e CDN](../../concepts/13_performance_cache_and_cdn.md)

## Escopo (o que ENTRA)
- **`demo.json` por template** (`frontend-storefront/templates/<id>/`): categorias, produtos (nome/preço/categoria) + **URLs de imagem** (uxpilot). Para Aurora/Bazar/Studio, **transcrito** do `docs/design/`.
- **`import_assets`** (backend): pra cada URL (uxpilot), **baixa → S3 (`public/templates/<id>/…`) → CloudFront → reescreve** a referência pra URL do CDN — nos **defaults `image` do schema**, no **catálogo do demo** e no **thumbnail** do template (hoje caminho relativo `/templates/<id>_preview.png`).
- **Mesmo caminho** pra aurora/bazar/studio (carga do design) **e** pra qualquer template futuro.

## Fora de escopo (o que NÃO entra)
- Montar a loja-demo a partir do demo: `P5-DEMO-02`.
- Refinos das telas que consomem os thumbnails de CDN: `P5-TPL-01`.

## Arquivos a criar/alterar
- `frontend-storefront/templates/{aurora,bazar,studio}/demo.json` (criar).
- `backend/app/modules/.../import_assets` (criar) — download + upload S3 + rewrite (reusa `app.core.storage`).
- (guardar os defaults `image` **separado** do `settings_schema` p/ o seed não sobrescrever — ver follow-up da Fase 4.)

## Passos
1. `demo.json` dos 3 templates (transcrito do `docs/design/`).
2. `import_assets`: baixa cada URL → `storage.upload_fileobj` (`public/templates/<id>/…`) → `public_url` → reescreve.
3. Cobre defaults `image` do schema + catálogo do demo + thumbnail.

## Testes
- **Níveis:** integração (mock S3 `moto`) + smoke real env-gated.
- **Quando escrever:** durante.
- **Cobrir:** integração — `import_assets` baixa a URL de origem → sobe pro CDN → reescreve; idempotente; URL já-CDN não re-importa.

## Definition of Done
- [ ] `demo.json` dos 3 templates (formato do doc 27).
- [ ] `import_assets` move imagens (schema/demo/thumbnail) → CDN e reescreve as referências.
- [ ] Idempotente; testes com `moto`.
- [ ] **Modos de falha mapeados** (URL 404, download grande, S3 falho, re-import) → tratados ou Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Funde os follow-ups da Fase 4: "imagens-default no CDN", "thumb relativo do seed", "remover PNGs de `public/`".

## Follow-ups
- [ ] — nenhum (preencher ao implementar).
