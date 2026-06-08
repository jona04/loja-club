---
id: P2-MEDIA-02
title: media_files + pipeline de upload + worker de thumbnails
phase: 2
etapa: "Etapa 5 — Mídia e storage"
area: MEDIA
status: todo
depends_on: [P2-MEDIA-01]
blocks: [P2-CAT-02, P2-CUST-03, P2-FE-01]
tests: [integration]
---

# P2-MEDIA-02 — `media_files` + pipeline de upload

## Contexto
Pipeline de imagem do doc [13](../../13_performance_cache_and_cdn.md): valida → S3 (original) → worker gera versões → S3 → CloudFront. **Nunca** servir imagem pelo backend nem salvar binário no banco.

## Docs de referência
- [13 — Performance/Cache/CDN](../../13_performance_cache_and_cdn.md) (fluxo + versões)
- [14 — Security](../../14_security_strategy.md) (validar tipo/MIME/tamanho)
- [07 — Database Strategy](../../07_database_strategy.md) (`media_files` + índices)

## Escopo (o que ENTRA)
- Modelo `media_files`: `store_id`, `owner_type`, `owner_id`, `key` (S3), `url`, `variants` (json: `thumbnail/card/product/zoom`), `content_type`, `size`, timestamps. Índices `store_id+id`, `store_id+owner_type+owner_id`.
- **Upload:** validar tipo/extensão/MIME/tamanho no backend → enviar **original** ao S3 (`storage` de `P2-MEDIA-01`) → registrar `media_files` → **enfileirar** geração de variantes (`enqueue`, `P0-CFG-04`).
- **Worker:** `generate_image_variants` gera `thumbnail/card/product/zoom` (Pillow) → S3 → atualiza `variants`.
- **Servir:** URLs via CDN (`public_url`).
- **Dep:** adicionar **Pillow** (decisão de lib de imagem → registrar nas Fundações).

## Fora de escopo (o que NÃO entra)
- Vincular imagem a produto → `P2-CAT-02`. Arte privada do cliente → `P2-CUST-03` (reusa o `storage`, com presigned).

## Arquivos a criar/alterar
- `backend/app/modules/media/models.py`/`enums.py`/`schemas.py`/`services.py`/`routes.py` (preencher).
- Worker task (em `app/core/queue` ou `media`), `pyproject.toml` (Pillow), migration, `models_registry`.

## Passos
1. Modelo `media_files` + migration.
2. Validação + upload original (S3) + registro.
3. Worker de variantes (Pillow) + atualização do registro.

## Testes
> Fundações §10. S3 e worker são fronteiras reais → integração (`moto` + worker burst).

- **Cobrir:** validação rejeita tipo/tamanho inválido; upload grava original (moto) + cria `media_files`; worker gera as 4 variantes e persiste `variants`; isolamento por `store_id`.

## Definition of Done
- [ ] Upload validado → S3 (original) + `media_files`; worker gera `thumbnail/card/product/zoom` → S3; servidas por CDN.
- [ ] Pillow adicionado; decisão de lib registrada nas Fundações.
- [ ] Testes (moto + worker) verdes.
- [ ] Itens adiados varridos → Follow-ups + README (ou "nenhum").

## Notas / Reconciliações
- Lib de imagem (**Pillow**) — registrar como decisão nas Fundações (DEC nova).

## Follow-ups
- (preencher)
