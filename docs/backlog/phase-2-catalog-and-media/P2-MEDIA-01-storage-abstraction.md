---
id: P2-MEDIA-01
title: Abstração de storage (S3/boto3) + provisionamento AWS dev (guiado) + verificação
phase: 2
etapa: "Etapa 1 — Mídia: storage + pipeline"
area: MEDIA
status: done
depends_on: []
blocks: [P2-MEDIA-02]
tests: [integration]
---

# P2-MEDIA-01 — Storage (S3/boto3) + AWS dev funcionando

## Contexto
A Fase 2 sobe imagens de produto e artes de cliente. Esta task entrega **(a)** a abstração fina de storage (INV-F2; domínio nunca conhece boto3) e **(b)** a AWS de **dev realmente provisionada e verificada** — não só código. S3 + CloudFront **reais** desde o dev local (DEC-8, sem MinIO). **Prod (bucket/credenciais de produção) é a 2ª etapa (Fase 9).**

## Docs de referência
- [Fundações](../_foundations-and-bottlenecks.md) (INV-F2, INV-S2/S3, DEC-8, DEC-11)
- [12 — AWS Infrastructure](../../concepts/12_aws_infrastructure_and_deployment.md)
- [13 — Cache/CDN](../../concepts/13_performance_cache_and_cdn.md) · [14 — Security](../../concepts/14_security_strategy.md)

## Escopo (o que ENTRA)
### 1. Código
- `app/core/storage.py`: cliente boto3 a partir do `config`; funções finas — `upload_fileobj(key, fileobj, content_type, *, public)`, `generate_presigned_url(key, expires)`, `delete(key)`, `public_url(key)` (URL do **CloudFront** p/ públicos). Sem expor o SDK ao domínio.
- Config (`config.py` + `.env`/`.env.example`): `S3_BUCKET`, `S3_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `CDN_BASE_URL`. Segredos fora do código (INV-S3).

### 2. Provisionamento AWS dev — **guiado (eu te ajudo passo a passo)**
Criar e deixar **funcionando** (melhores práticas):
- **Região:** **Ohio (`us-east-2`)** na 1ª etapa — todos os recursos (S3 + CloudFront + IAM) na mesma região.
- **Bucket S3 (dev):** Block Public Access **ON**; prefixos separados (`public/` p/ imagens, `private/` p/ arte do cliente por `store_id`); **lifecycle** p/ expirar temporários (doc 07/22); CORS só se houver upload direto do browser.
- **CloudFront:** distribuição com **Origin Access Control (OAC)** lendo o bucket **privado** (nada de ACL public-read); imagens públicas servidas pelo CDN; arte privada **não** vai pelo CDN público → `generate_presigned_url` (S3 GET direto).
- **IAM:** usuário **least-privilege** (`s3:PutObject/GetObject/DeleteObject` só no ARN do bucket) — sem `*`. Em **prod (Fase 9)** usar **role** na compute (sem chave longa).
- **Eu forneço:** os passos (console/CLI) + a **policy IAM** + config de OAC/CORS/lifecycle. **Você executa na sua conta** e me devolve os valores.

### 3. Verificação de que está funcionando
- **Smoke real** (com as credenciais dev): upload → get → presigned → delete no bucket; GET de um objeto público via **CloudFront**. Prova que provisionamento + credenciais funcionam **local/dev**.

## Inputs manuais que vou te pedir (na implementação)
`S3_REGION` (= **`us-east-2` / Ohio**, 1ª etapa), `S3_BUCKET`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `CDN_BASE_URL` (domínio do CloudFront). *(São de DEV; prod fica para a Fase 9.)*

## Fora de escopo (o que NÃO entra)
- `media_files`/pipeline/thumbnails → `P2-MEDIA-02`. AWS de **produção** → Fase 9.

## Arquivos a criar/alterar
- `backend/app/core/storage.py` (criar); `backend/app/core/config.py`, `.env`/`.env.example` (alterar).

## Testes
> Fundações §10. **Dois níveis** (para garantir local/dev/remoto):
- **Mock (CI/offline) — sempre:** `moto` (DEC-11) cobre upload/presigned/delete/`public_url`.
- **Real (env-gated) — confiança:** marcador `aws` + `skipif` sem credenciais; sobe/baixa/assina/apaga no **bucket dev real** e faz GET via **CloudFront**. Roda local/dev com as chaves; **pulado** no CI sem secrets.

## Definition of Done
- [x] `storage.py` (upload/presigned/delete/public_url) sem boto3 vazando; vars no `config.py`/`.env` (`S3_REGION=us-east-2`).
- [x] **AWS dev provisionada** (bucket privado `loja-club-dev-media` + CloudFront/OAC `dsqh10bjdo174.cloudfront.net` + IAM least-privilege) e **smoke real verde** (S3 roundtrip em us-east-2).
- [x] Testes `moto` (CI) **+ smoke real** verdes *(suíte 140 passed, cobertura 91%)*.
- [x] Itens adiados varridos → Follow-ups + README.

## Progresso
- ✅ **Código:** `app/core/storage.py` (4 funções, boto3 isolado), vars em `config.py` + `.env`, testes `moto` + smoke real (`tests/integration/test_storage.py`). Smoke real env-gated por `settings.storage_enabled`.
- ✅ **AWS dev (us-east-2):** bucket `loja-club-dev-media` (privado, Block Public Access) + CloudFront `dsqh10bjdo174.cloudfront.net` (OAC + bucket policy) + usuário IAM least-privilege. **Smoke real verde** (upload/head/presigned/delete no bucket de verdade).

## Notas / Reconciliações
- **Públicas via CDN (OAC) / privadas via presigned** — bucket sempre privado (Block Public Access).
- **Assinatura de `upload_fileobj`:** **sem** o param `public` da descrição original — com bucket privado + OAC não há ACL; público vs privado é decisão de **entrega** (`public_url`/CDN vs `generate_presigned_url`), e o chamador escolhe o prefixo (`public/...` vs `private/...`).
- **Smoke real cobre o S3** (roundtrip); o **GET público via CloudFront** é exercitado na `P2-MEDIA-02` (quando há imagem pública servida).
- **Secrets:** `.env` virou **gitignored** + `.env.example` committed; CI faz `cp .env.example .env`. `SECRET_KEY` rotacionado (repo público). Prod (Fase 9): GitHub Secrets/SSM + IAM role.
- **Padrão "mock + smoke real env-gated"** registrado nas Fundações §10 (vale p/ o gateway na Fase 8).

## Follow-ups
- [x] **`_s3_client()` cacheado** (reuso process-wide, INV-F6) + `reset_client()` chamado nos fixtures `s3`/smokes. *(feito)*
- [ ] **`_s3_client()` lazy-init sem lock:** na 1ª chamada concorrente (threadpool de rotas sync) duas threads podem criar dois clients boto3 — um é descartado. **Benigno** (boto3 é thread-safe; sem erro de correção). Eliminável com lock / `functools.cache` / criar no startup. Origem: refactor INV-F6.
- O GET público via CloudFront é coberto pela `P2-MEDIA-02`; rotação de senhas locais (`POSTGRES_PASSWORD`/`FIRST_SUPERUSER_PASSWORD`) é tarefa do usuário.
