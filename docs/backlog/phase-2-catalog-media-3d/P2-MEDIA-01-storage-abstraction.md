---
id: P2-MEDIA-01
title: Abstração de storage (S3/boto3) + provisionamento AWS dev (guiado) + verificação
phase: 2
etapa: "Etapa 5 — Mídia e storage"
area: MEDIA
status: todo
depends_on: []
blocks: [P2-MEDIA-02, P2-CUST-03]
tests: [integration]
---

# P2-MEDIA-01 — Storage (S3/boto3) + AWS dev funcionando

## Contexto
A Fase 2 sobe imagens de produto e artes de cliente. Esta task entrega **(a)** a abstração fina de storage (INV-F2; domínio nunca conhece boto3) e **(b)** a AWS de **dev realmente provisionada e verificada** — não só código. S3 + CloudFront **reais** desde o dev local (DEC-8, sem MinIO). **Prod (bucket/credenciais de produção) é a 2ª etapa (Fase 6).**

## Docs de referência
- [Fundações](../_foundations-and-bottlenecks.md) (INV-F2, INV-S2/S3, DEC-8, DEC-11)
- [12 — AWS Infrastructure](../../12_aws_infrastructure_and_deployment.md)
- [13 — Cache/CDN](../../13_performance_cache_and_cdn.md) · [14 — Security](../../14_security_strategy.md)

## Escopo (o que ENTRA)
### 1. Código
- `app/core/storage.py`: cliente boto3 a partir do `config`; funções finas — `upload_fileobj(key, fileobj, content_type, *, public)`, `generate_presigned_url(key, expires)`, `delete(key)`, `public_url(key)` (URL do **CloudFront** p/ públicos). Sem expor o SDK ao domínio.
- Config (`config.py` + `.env`/`.env.example`): `S3_BUCKET`, `S3_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `CDN_BASE_URL`. Segredos fora do código (INV-S3).

### 2. Provisionamento AWS dev — **guiado (eu te ajudo passo a passo)**
Criar e deixar **funcionando** (melhores práticas):
- **Região:** **Ohio (`us-east-2`)** na 1ª etapa — todos os recursos (S3 + CloudFront + IAM) na mesma região.
- **Bucket S3 (dev):** Block Public Access **ON**; prefixos separados (`public/` p/ imagens, `private/` p/ arte do cliente por `store_id`); **lifecycle** p/ expirar temporários (doc 07/22); CORS só se houver upload direto do browser.
- **CloudFront:** distribuição com **Origin Access Control (OAC)** lendo o bucket **privado** (nada de ACL public-read); imagens públicas servidas pelo CDN; arte privada **não** vai pelo CDN público → `generate_presigned_url` (S3 GET direto).
- **IAM:** usuário **least-privilege** (`s3:PutObject/GetObject/DeleteObject` só no ARN do bucket) — sem `*`. Em **prod (Fase 6)** usar **role** na compute (sem chave longa).
- **Eu forneço:** os passos (console/CLI) + a **policy IAM** + config de OAC/CORS/lifecycle. **Você executa na sua conta** e me devolve os valores.

### 3. Verificação de que está funcionando
- **Smoke real** (com as credenciais dev): upload → get → presigned → delete no bucket; GET de um objeto público via **CloudFront**. Prova que provisionamento + credenciais funcionam **local/dev**.

## Inputs manuais que vou te pedir (na implementação)
`S3_REGION` (= **`us-east-2` / Ohio**, 1ª etapa), `S3_BUCKET`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `CDN_BASE_URL` (domínio do CloudFront). *(São de DEV; prod fica para a Fase 6.)*

## Fora de escopo (o que NÃO entra)
- `media_files`/pipeline/thumbnails → `P2-MEDIA-02`. AWS de **produção** → Fase 6.

## Arquivos a criar/alterar
- `backend/app/core/storage.py` (criar); `backend/app/core/config.py`, `.env`/`.env.example` (alterar).

## Testes
> Fundações §10. **Dois níveis** (para garantir local/dev/remoto):
- **Mock (CI/offline) — sempre:** `moto` (DEC-11) cobre upload/presigned/delete/`public_url`.
- **Real (env-gated) — confiança:** marcador `aws` + `skipif` sem credenciais; sobe/baixa/assina/apaga no **bucket dev real** e faz GET via **CloudFront**. Roda local/dev com as chaves; **pulado** no CI sem secrets.

## Definition of Done
- [ ] `storage.py` (upload/presigned/delete/public_url) sem boto3 vazando; vars no `config.py`/`.env(.example)`.
- [ ] **AWS dev provisionada com você** (bucket privado + CloudFront/OAC + IAM least-privilege) e **smoke real verde** (local/dev).
- [ ] Testes `moto` verdes (CI) + smoke real verde (com credenciais).
- [ ] Itens adiados varridos → Follow-ups + README (ou "nenhum").

## Notas / Reconciliações
- **Públicas via CDN (OAC) / privadas via presigned** — bucket sempre privado. Registrar a decisão de design.
- **Prod (Fase 6):** bucket/distribuição de prod + **IAM role** (sem chave longa) + segredos via SSM. *(2ª etapa.)*
- **Padrão de teste com serviço real (mock + smoke env-gated)** vale para qualquer dependência externa — candidato a virar convenção nas Fundações §10.

## Follow-ups
- (preencher)
