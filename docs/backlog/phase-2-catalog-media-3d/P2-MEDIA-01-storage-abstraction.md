---
id: P2-MEDIA-01
title: Abstração de storage (S3/boto3) + config + setup AWS dev
phase: 2
etapa: "Etapa 5 — Mídia e storage"
area: MEDIA
status: todo
depends_on: []
blocks: [P2-MEDIA-02, P2-CUST-03]
tests: [integration]
---

# P2-MEDIA-01 — Abstração de storage (S3/boto3)

## Contexto
A Fase 2 sobe imagens de produto e artes de cliente. Antes de qualquer pipeline, é preciso a **abstração fina de storage** (INV-F2): o domínio nunca conhece o boto3; usa `app/core/storage.py`. S3 + CloudFront **reais** desde o dev local (DEC-8, sem MinIO).

## Docs de referência
- [Fundações](../_foundations-and-bottlenecks.md) (INV-F2, DEC-8, INV-S2)
- [12 — AWS Infrastructure](../../12_aws_infrastructure_and_deployment.md)
- [13 — Performance/Cache/CDN](../../13_performance_cache_and_cdn.md) (imagens nunca pelo backend)
- [14 — Security](../../14_security_strategy.md) (URLs assinadas, arte privada)

## Escopo (o que ENTRA)
- `app/core/storage.py`: cliente boto3 a partir do `config`; funções finas — `upload_fileobj(key, fileobj, content_type, *, public)`, `generate_presigned_url(key, expires)`, `delete(key)`, `public_url(key)` (monta URL do **CDN** para públicos). Sem expor o SDK ao domínio.
- **Config** (`app/core/config.py` + `.env`/`.env.example`): `S3_BUCKET`, `S3_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `CDN_BASE_URL`.
- **Setup AWS dev (manual, documentar):** bucket S3 de dev + distribuição CloudFront + usuário/credenciais IAM com acesso mínimo. Registrar o passo a passo (doc [12](../../12_aws_infrastructure_and_deployment.md)).

## Fora de escopo (o que NÃO entra)
- `media_files`/pipeline/thumbnails → `P2-MEDIA-02`.
- Uso por catálogo/personalização → `P2-CAT-02`/`P2-CUST-03`.

## Arquivos a criar/alterar
- `backend/app/core/storage.py` (criar).
- `backend/app/core/config.py` (alterar) — vars S3/AWS/CDN.
- `.env` / `.env.example` (alterar).

## Passos
1. Vars de config (com defaults seguros p/ dev; segredos fora do código — INV-S3).
2. `storage.py` com as 4 funções finas (público vs privado: público → URL de CDN; privado → presigned).
3. Documentar o setup AWS de dev (bucket/CloudFront/IAM).

## Testes
> Fundações §10. Fronteira real (S3) → integração com **`moto`** (DEC-11).

- **Níveis:** integração (mock S3 via `moto`).
- **Cobrir:** upload grava o objeto; `generate_presigned_url` retorna URL assinada; `delete` remove; `public_url` monta a URL do CDN.

## Definition of Done
- [ ] `storage.py` com upload/presigned/delete/public_url, configurável por env (sem boto3 vazando p/ o domínio).
- [ ] Vars S3/AWS/CDN no `config.py`/`.env(.example)`.
- [ ] Testes com `moto` verdes; passo a passo do setup AWS dev documentado.
- [ ] Itens adiados varridos → Follow-ups + README (ou "nenhum").

## Notas / Reconciliações
- O **provisionamento AWS** (bucket/CloudFront/IAM) é **manual/externo** — pré-requisito para uso real; os testes rodam com `moto` sem AWS.

## Follow-ups
- (preencher)
