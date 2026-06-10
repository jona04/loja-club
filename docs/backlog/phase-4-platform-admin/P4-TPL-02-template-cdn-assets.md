---
id: P4-TPL-02
title: Assets de template no CDN — thumbnail + imagens-default
phase: 4
etapa: "Etapa 3 — Cadastro/gestão de templates"
area: TPL
status: done
depends_on: [P4-TPL-01]
blocks: [P4-ADMIN-03]
tests: [integration]
---

# P4-TPL-02 — Assets de template no CDN (backend)

## Contexto
Hoje o thumbnail do template é PNG hardcoded em `frontend-dashboard/public/` e as imagens-default apontam pra URLs temporárias. Esta task move os assets pro **S3 + CloudFront** (via `media`/`storage`, Fase 2), vinculados ao registro do template.

## Docs de referência
- [26 — Template System](../../26_template_system.md)
- [13 — Performance, Cache and CDN](../../13_performance_cache_and_cdn.md)
- [25 — Platform Admin](../../25_platform_admin.md)

## Escopo (o que ENTRA)
- Upload (gated `platform.templates.manage`) de **thumbnail** + **imagens-default** do template → S3/CloudFront, reusando `app/core/storage.py` + `media` (Fase 2).
- Vincular as URLs ao `content_theme_templates` (`preview_image_url` + URLs default referenciadas pelas chaves `image` do `settings_schema`).

## Fora de escopo (o que NÃO entra)
- CRUD/registro + schema → `P4-TPL-01`.
- Preview navegável → `P4-TPL-03`. Telas/upload-UI → `P4-ADMIN-03`.
- Defaults de imagem **consumidos** pelo lojista → **Fase 5**.

## Arquivos a criar/alterar
- `app/modules/platform_admin/{services,routes}.py` (alterar) — upload de assets de template.
- `app/modules/content/models.py` (alterar) — campos/URLs dos assets, se faltarem.
- `frontend-dashboard/public/templates/*` (remover) — sai do hardcode (após migrar).

## Passos
1. Endpoint de upload de asset de template (thumbnail/default) → storage/CDN.
2. Persistir as URLs no registro do template.
3. Migrar os PNGs de `public/` + URLs temporárias para o CDN; remover o hardcode.

## Testes
> Regra em [`_foundations-and-bottlenecks.md`](../_foundations-and-bottlenecks.md) §10.
- **Níveis:** integração (`moto` no CI + smoke real env-gated).
- **Cobrir:** upload → URL de CDN persistida; gating `platform.*`; tipo/limite de arquivo validado.

## Definition of Done
- [x] **Thumbnail no CDN** (`POST /platform/templates/{id}/thumbnail` → `preview_image_url`), gated `platform.templates.manage`; validação de tipo/tamanho. Fecha "Previews no CloudFront".
- [ ] **Imagens-default no CDN** → **adiado**: não há campos `image` no `settings_schema` ainda (vêm na Fase 5) → Follow-up.
- [x] **Modos de falha mapeados** (tipo inválido → 422, arquivo grande → 413, template inexistente → 404) → tratados ou Follow-ups.
- [x] **Itens adiados varridos** → Follow-ups + README.

> **Entregue:** `set_template_thumbnail` (upload S3 público via `storage` + `public_url` CDN) + rota; testes com `moto` (S3 mockado). Gate: **240 testes** (5 novos), cobertura **94%**, lint verde.

## Notas / Reconciliações
- **Fecha o follow-up "Previews no CloudFront"** (Fase 3, `P3-TPL-03`) — o thumbnail agora vai pro CDN; marcado `[x]` na origem.
- **Templates são globais → uso o `storage` core direto** num key público (`public/templates/<id>/...`), sem `media_files` por loja (o módulo `media` é tenant-scoped). Key com uuid (cache-busting).
- **Escopo (decisão):** entreguei o **thumbnail**; as **imagens-default** referenciam chaves `image` do schema, que **não existem ainda** → Follow-up (Fase 5), sem especular.

## Follow-ups
- [ ] **Imagens-default no CDN** (Fase 5): quando o schema tiver campos `image`, subir as imagens-default e **guardá-las separado do `settings_schema`** (ex.: `default_assets` `field_key→URL`) — senão o **seed re-sincroniza o schema do JSON e sobrescreve** o que foi subido; a vitrine mescla (default do asset ?? default do schema). → README da fase.
- [ ] **Limpar asset antigo no S3** no re-upload (a key usa uuid pra cache-busting; o anterior fica órfão). → README da fase.
- [ ] **Remover os PNGs hardcoded de `public/templates/`** + o default do seed (`/templates/<id>_preview.png`) depois que todos os templates tiverem thumbnail no CDN. → README da fase.
