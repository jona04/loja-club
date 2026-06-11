---
id: P2-MEDIA-02
title: media_files + pipeline de upload + worker de thumbnails
phase: 2
etapa: "Etapa 1 — Mídia: storage + pipeline"
area: MEDIA
status: done
depends_on: [P2-MEDIA-01]
blocks: [P2-CAT-02, P2-FE-01]
tests: [integration]
---

# P2-MEDIA-02 — `media_files` + pipeline de upload

## Contexto
Pipeline de imagem do doc [13](../../concepts/13_performance_cache_and_cdn.md): valida → S3 (original) → worker gera versões → S3 → CloudFront. **Nunca** servir imagem pelo backend nem salvar binário no banco.

## Docs de referência
- [13 — Performance/Cache/CDN](../../concepts/13_performance_cache_and_cdn.md) (fluxo + versões)
- [14 — Security](../../concepts/14_security_strategy.md) (validar tipo/MIME/tamanho)
- [07 — Database Strategy](../../concepts/07_database_strategy.md) (`media_files` + índices)

## Escopo (o que ENTRA)
- Modelo `media_files`: `store_id`, `owner_type`, `owner_id`, `key` (S3), `url`, `variants` (json: `thumbnail/card/product/zoom`), `content_type`, `size`, `status` (`processing|ready|failed`), timestamps. Índices `store_id+id`, `store_id+owner_type+owner_id`.
- **Upload:** validar tipo/extensão/MIME/tamanho no backend → enviar **original** ao S3 (`storage` de `P2-MEDIA-01`) → registrar `media_files` → **enfileirar** geração de variantes (`enqueue`, `P0-CFG-04`).
- **Worker:** `generate_image_variants` gera `thumbnail/card/product/zoom` (Pillow) → S3 → atualiza `variants`.
- **Servir:** URLs via CDN (`public_url`).
- **Dep:** adicionar **Pillow** (decisão de lib de imagem → registrar nas Fundações).

## Fora de escopo (o que NÃO entra)
- Vincular imagem a produto → `P2-CAT-02`. Arte privada do cliente → **[Fase 7 — Produtos 3D](../phase-7-3d-products.md)** (reusa o `storage`, com presigned).

## Arquivos a criar/alterar
- `backend/app/modules/media/models.py`/`enums.py`/`schemas.py`/`services.py`/`routes.py` (preencher).
- Worker task (em `app/core/queue` ou `media`), `pyproject.toml` (Pillow), migration, `models_registry`.

## Passos
1. Modelo `media_files` + migration.
2. Validação + upload original (S3) + registro.
3. Worker de variantes (Pillow) + atualização do registro.

## Testes
> Fundações §10. S3 e worker são fronteiras reais. **Dois níveis** (mock + real), como em `P2-MEDIA-01`.

- **Mock (CI/offline):** `moto` + worker burst — validação rejeita tipo/tamanho inválido; upload grava original + cria `media_files`; worker gera as 4 variantes e persiste `variants`; isolamento por `store_id`.
- **Real (env-gated):** com credenciais dev, sobe uma imagem real → original no S3 → worker gera variantes no S3 → **GET de uma variante via CloudFront** retorna a imagem. Pulado no CI sem secrets; roda local/dev.

## Definition of Done
- [x] Upload validado → S3 (original) + `media_files`; worker gera `thumbnail/card/product/zoom` → S3; servidas por CDN.
- [x] Pillow adicionado; decisão registrada nas Fundações (**DEC-11**).
- [x] Testes `moto` verdes **+ smoke real (S3+CloudFront) verde** — suíte 156 passed, cobertura 92%.
- [x] Itens adiados varridos → Follow-ups + README.

## Progresso
- ✅ **Modelo** `media_files` (`media/models.py`): `owner_type`/`owner_id`, `key` (único), `url`, `variants` (JSON), `content_type`, `size`, `status` (`MediaStatus`) — `StoreScopedMixin` + índices do doc 07. Migration `2262615e4dd0` (+ **FK `catalog_product_images.media_file_id` → `media_files`**, fechando a pendência da `P2-CAT-01`). `alembic check` vazio.
- ✅ **Pipeline** (`media/services.py`): `validate_image` (tipo/MIME/tamanho, 415/413) + `_assert_image` (Pillow), `store_original` (S3 + registro `processing`), `generate_variants` (4 variantes Pillow → S3 → `ready`). `storage.download()` adicionado.
- ✅ **Worker** `generate_image_variants` (`media/tasks.py`) registrado no `WorkerSettings`; `enqueue` chamado pela rota.
- ✅ **Rota** `POST /api/v1/stores/{store_id}/media` (multipart) → `MediaPublic`, gating `catalog.product.update`.
- ✅ **Testes** `tests/integration/test_media_pipeline.py`: validação, upload, variantes, isolamento, rota, `_extension`, + smoke real (S3 + GET via CloudFront).

## Notas / Reconciliações
- **Lib de imagem = Pillow** (DEC-11). Variantes mantêm o formato do original (aspect-ratio preservado por `thumbnail()`).
- **Permissão da rota de upload:** reusa **`catalog.product.update`** (consumidor principal são imagens de produto); não há permissão `media.*` dedicada. Se surgir upload fora do catálogo (ex.: logo da loja), avaliar uma permissão própria.
- **FK `media_file_id`:** criada aqui (a `P2-CAT-01` deixou a coluna indexada sem FK porque `media_files` não existia ainda).
- **Originais/variantes são públicos via CDN**; bucket privado (INV-F2). Arte privada do cliente (presigned) é da Fase 7.

## Follow-ups
- [ ] **Falha no `enqueue` após o original já no S3** (ex.: Redis fora): o `media_files` fica preso em `processing` sem job. Falta reconciliação/retry de órfãos (varrer `processing` antigos → re-enfileirar ou marcar `failed`). Origem: P2-MEDIA-02.
- [ ] **Falha no worker (`generate_variants`)** — erro de Pillow/S3 **não** marca `status=failed` (o enum existe mas nunca é setado); o registro fica em `processing`. Falta `try/except` no task + política de retry (arq) → marcar `failed` e/ou reprocessar. Origem: P2-MEDIA-02.
- [ ] **Tamanho validado após ler o arquivo todo em memória** (`await file.read()` → `len(data)`): upload gigante consome memória antes do check. Validar por `Content-Length`/streaming antes de carregar tudo. Origem: P2-MEDIA-02.
- Permissão `media.*` dedicada só se houver upload fora do catálogo (ver Notas).
