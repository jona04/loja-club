---
id: P4-TPL-02
title: Assets de template no CDN — thumbnail + imagens-default
phase: 4
etapa: "Etapa 3 — Cadastro/gestão de templates"
area: TPL
status: todo
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
- [ ] Thumbnail + imagens-default no **CDN**, vinculados ao template; hardcode de `public/` + URLs temporárias removidos.
- [ ] **Modos de falha / edge cases mapeados** (upload falho, arquivo grande, tipo inválido) → tratados ou Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Fecha o follow-up `P3-TPL-03` ("Previews no CloudFront") — marcar `[x]` na origem (README da Fase 3) ao concluir.

## Follow-ups
- [ ] — (preencher ao implementar) → README da fase.
