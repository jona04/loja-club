# AWS Infrastructure and Deployment

## Decisão principal

A V1 deve usar AWS com custo controlado.

Não usar Kubernetes/EKS no começo.

Usar Docker desde o início.

## Dev vs Produção na V1

> **Dev local nas Fases 0–8; dev online (EC2) nas Fases 9–10.** Produção robusta é a **Fase 11**.

| Etapa | Ambiente | Onde roda | Arquivos / CDN |
|---|---|---|---|
| Fases 0–8 | **dev local** | máquina do desenvolvedor (Docker Compose + Traefik) | **AWS S3 + CloudFront reais** (bucket/distribuição de dev) |
| Fases 9–10 | **dev online na AWS** | **EC2** + Docker Compose + Traefik | AWS S3 + CloudFront |
| Fase 11 | **produção** | ECS/Fargate + ALB (troca a orquestração por serviços gerenciados) | AWS S3 + CloudFront |

Pontos importantes:

- Mesmo no **dev local**, os arquivos (imagens, modelos 3D, artes) usam **AWS S3 + CloudFront de verdade**, com implementação normal via SDK (boto3). **Não usar MinIO** nem stand-ins locais de storage.
- O sistema só vai **para o ar** na **Fase 9**, em **EC2** (necessário, entre outros, para receber webhooks de pagamento em URL pública).
- A migração para **produção** (ECS/Fargate + ALB etc.) é a **Fase 11** e troca apenas a camada de orquestração/entrada, mantendo o mesmo backend, banco e storage.
- **Região AWS (1ª etapa):** **Ohio (`us-east-2`)** — todos os recursos de dev (S3, CloudFront, IAM e, depois, compute) na mesma região. A região de produção é revisada na Fase 11.

## Ambientes

A Kriar terá, ao longo do tempo:

```text
dev local      (Fases 0–8)  — máquina do desenvolvedor
dev online     (Fases 9–10) — EC2 na AWS
production     (Fase 11)    — ECS/Fargate na AWS
```

`dev local` roda na máquina de desenvolvimento, mas já usa S3/CloudFront reais para arquivos.
`dev online` é o mesmo stack publicado em EC2, com domínios, TLS e serviços AWS, para teste compartilhado e beta.
`production` é o ambiente robusto dos lojistas e clientes, montado na **Fase 11**.

## Desenvolvimento local

Baseado no Full Stack FastAPI Template:

```text
Docker Compose
Traefik
backend-api
frontend-dashboard
frontend-admin
frontend-storefront
postgres
redis
worker
scheduler
adminer
mailcatcher
```

## Dev online na AWS (Fases 9–10)

O ambiente online da V1 usa **EC2** (não ECS):

```text
EC2 + Docker Compose + Traefik + RDS + ElastiCache (ou Redis em container) + S3 + CloudFront + Route 53 + ACM/Let's Encrypt
```

Motivo:

- barato;
- rápido;
- próximo do dev local (mesmo Docker Compose);
- bom para beta/teste;
- Traefik facilita subdomínios e HTTPS;
- já permite receber webhooks de pagamento (URL pública).

## Produção robusta (Fase 11)

> Fora do escopo da V1. Quando a V1 (dev) estiver validada, a produção troca a orquestração por serviços gerenciados.

Sugestão:

```text
ECS/Fargate + ALB + RDS + ElastiCache + S3 + CloudFront
```

Serviços:

| Serviço | Uso |
|---|---|
| ECS/Fargate | Rodar containers |
| ECR | Registry das imagens Docker |
| ALB | Load balancer |
| RDS PostgreSQL | Banco principal |
| ElastiCache Redis | Cache/fila/locks |
| S3 | Imagens, arquivos, artes e modelos 3D |
| CloudFront | CDN |
| Route 53 | DNS |
| ACM | SSL/TLS |
| CloudWatch | Logs e métricas |
| SES | E-mails (enviados pelo worker) |
| Sentry | Erros da aplicação |
| Secrets Manager ou SSM | Segredos |

## Containers

| Container | Função |
|---|---|
| `backend-api` | API FastAPI |
| `frontend-dashboard` | Painel do lojista |
| `frontend-admin` | Admin interno da Kriar |
| `frontend-storefront` | Lojas públicas |
| `worker` | Tarefas assíncronas |
| `scheduler` | Tarefas agendadas |

## Traefik

Traefik será usado em:

- local;
- dev;
- possível produção inicial barata em EC2.

Roteamento:

```text
api.kriar.shop        -> backend-api
app.kriar.shop        -> frontend-dashboard
admin.kriar.shop      -> frontend-admin
*.kriar.shop          -> frontend-storefront
```

Traefik não precisa conhecer cada loja. O wildcard envia tudo para o storefront.

## Produção com ALB/CloudFront

Em produção ECS, Traefik pode ser substituído por:

- CloudFront;
- ALB;
- ACM;
- Route 53.

Roteamento conceitual:

```text
api.kriar.shop        -> ALB -> backend-api
app.kriar.shop        -> ALB/CloudFront -> frontend-dashboard
admin.kriar.shop      -> ALB/CloudFront -> frontend-admin
*.kriar.shop          -> CloudFront/ALB -> frontend-storefront
```

## S3 e CloudFront

S3 armazena:

- imagens originais;
- thumbnails;
- banners;
- logos;
- modelos 3D;
- texturas;
- artes enviadas por clientes;
- snapshots aprovados de personalização;
- arquivos públicos controlados.

CloudFront entrega:

- imagens;
- modelos 3D públicos;
- texturas públicas;
- assets estáticos;
- arquivos públicos;
- possivelmente storefront.

Arquivos enviados por clientes em personalização devem usar acesso controlado.
Eles podem ficar no S3, mas não devem ser tratados como assets públicos permanentes.

## Banco

V1 econômica:

```text
RDS PostgreSQL Single-AZ
```

Com backups automáticos.

Quando crescer:

```text
RDS Multi-AZ
read replicas
maior instância
```

## Redis

Opções:

1. Redis container no dev (local e EC2).
2. ElastiCache em produção (Fase 11).

Redis será usado para:

- cache;
- rate limit;
- locks;
- filas leves;
- sessões temporárias;
- sessões de personalização.

## Load balancer

Em produção com ECS:

```text
Application Load Balancer
```

Responsável por:

- receber requisições;
- distribuir para containers;
- health checks;
- SSL via ACM;
- roteamento por host/path.

## DNS

Route 53:

```text
kriar.shop
www.kriar.shop
api.kriar.shop
app.kriar.shop
admin.kriar.shop
*.kriar.shop
```

Wildcard importante:

```text
*.kriar.shop
```

## Certificados

ACM para:

```text
kriar.shop
*.kriar.shop
api.kriar.shop
app.kriar.shop
admin.kriar.shop
```

Domínios próprios de lojistas exigem estratégia adicional de certificado.

## Deploy

Fluxo sugerido:

1. push no GitHub;
2. GitHub Actions roda testes;
3. build das imagens Docker;
4. push para ECR;
5. deploy em dev;
6. validação;
7. deploy em produção.

## Migrações

Antes de atualizar aplicação:

- rodar migrations em dev;
- validar;
- rodar migrations em produção com cuidado;
- atualizar containers.

## Custo inicial

Para V1 barata, a expectativa inicial pode ficar em faixa controlada se usar:

- RDS pequeno;
- poucos containers;
- logs controlados;
- CloudFront/S3 com baixo tráfego;
- dev econômico;
- evitar NAT Gateway se possível;
- evitar EKS/Kubernetes.

## O que evitar no início

- EKS/Kubernetes;
- NAT Gateway caro sem necessidade;
- banco Multi-AZ antes de clientes reais;
- serviços separados demais;
- logs sem retenção;
- imagens passando pelo backend;
- banco dentro da EC2 para produção séria por muito tempo.

## Decisão canônica

A Kriar usará Docker desde o começo. **Dev**: Fases 0–8 em **dev local** (com S3/CloudFront reais) e Fases 9–10 em **dev online na AWS** com EC2 + Docker Compose + Traefik + RDS + Redis/ElastiCache + S3 + CloudFront. A **produção robusta com ECS/Fargate + ALB** é a **Fase 11**.
