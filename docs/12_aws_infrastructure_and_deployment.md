# AWS Infrastructure and Deployment

## Decisão principal

A V1 deve usar AWS com custo controlado.

Não usar Kubernetes/EKS no começo.

Usar Docker desde o início.

## Ambientes

A Loja Club deve ter pelo menos:

```text
local
staging
production
```

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

## Staging barato

Sugestão:

```text
EC2 + Docker Compose + Traefik + RDS + S3 + CloudFront
```

Motivo:

- barato;
- rápido;
- próximo do template;
- bom para beta/teste;
- Traefik facilita subdomínios e HTTPS.

## Produção V1 recomendada

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
| SES | E-mails |
| Sentry | Erros da aplicação |
| Secrets Manager ou SSM | Segredos |

## Containers

| Container | Função |
|---|---|
| `backend-api` | API FastAPI |
| `frontend-dashboard` | Painel do lojista |
| `frontend-admin` | Admin interno da Loja Club |
| `frontend-storefront` | Lojas públicas |
| `worker` | Tarefas assíncronas |
| `scheduler` | Tarefas agendadas |

## Traefik

Traefik será usado em:

- local;
- staging;
- possível produção inicial barata em EC2.

Roteamento:

```text
api.loja.club        -> backend-api
app.loja.club        -> frontend-dashboard
admin.loja.club      -> frontend-admin
*.loja.club          -> frontend-storefront
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
api.loja.club        -> ALB -> backend-api
app.loja.club        -> ALB/CloudFront -> frontend-dashboard
admin.loja.club      -> ALB/CloudFront -> frontend-admin
*.loja.club          -> CloudFront/ALB -> frontend-storefront
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

1. Redis container no staging barato.
2. ElastiCache em produção.

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
loja.club
www.loja.club
api.loja.club
app.loja.club
admin.loja.club
*.loja.club
```

Wildcard importante:

```text
*.loja.club
```

## Certificados

ACM para:

```text
loja.club
*.loja.club
api.loja.club
app.loja.club
admin.loja.club
```

Domínios próprios de lojistas exigem estratégia adicional de certificado.

## Deploy

Fluxo sugerido:

1. push no GitHub;
2. GitHub Actions roda testes;
3. build das imagens Docker;
4. push para ECR;
5. deploy em staging;
6. validação;
7. deploy em produção.

## Migrações

Antes de atualizar aplicação:

- rodar migrations em staging;
- validar;
- rodar migrations em produção com cuidado;
- atualizar containers.

## Custo inicial

Para V1 barata, a expectativa inicial pode ficar em faixa controlada se usar:

- RDS pequeno;
- poucos containers;
- logs controlados;
- CloudFront/S3 com baixo tráfego;
- staging econômico;
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

A Loja Club usará Docker desde o começo. Local e staging podem usar Docker Compose + Traefik. Produção V1 recomendada: ECS/Fargate + ALB + RDS PostgreSQL + Redis/ElastiCache + S3 + CloudFront.
