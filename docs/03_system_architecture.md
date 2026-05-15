# System Architecture

## Decisão principal

A Loja Club V1 será construída como um **monólito modular em FastAPI**, usando o **Full Stack FastAPI Template** como base.

O sistema será multi-tenant: várias lojas dentro da mesma plataforma, usando uma infraestrutura central e um banco compartilhado com separação por `store_id`.

Existem três identidades diferentes:

- admin interno da Loja Club;
- lojista/equipe da loja;
- cliente final da loja.

Admins e lojistas usam `account_users`.
Clientes finais usam `customer_profiles` e podem comprar sem login.

## Componentes principais

A arquitetura terá:

- backend FastAPI central;
- painel do lojista;
- admin da plataforma;
- storefront público das lojas;
- PostgreSQL;
- Redis;
- worker assíncrono;
- storage de imagens;
- storage de modelos 3D e artes enviadas por clientes;
- CDN;
- gateway de pagamento;
- fila/tarefas assíncronas;
- observabilidade;
- deploy com Docker.

## Serviços lógicos

| Serviço | Função |
|---|---|
| `backend-api` | API principal FastAPI |
| `frontend-dashboard` | Painel do lojista |
| `frontend-admin` | Admin interno da Loja Club |
| `frontend-storefront` | Loja pública dos lojistas |
| `worker` | Tarefas assíncronas |
| `scheduler` | Tarefas agendadas |
| `postgres` | Banco principal em desenvolvimento local |
| `redis` | Cache, locks e fila leve |
| `traefik` | Reverse proxy local/dev |
| `mailcatcher` | Captura de e-mails em desenvolvimento |
| `adminer` | Acesso técnico ao banco em desenvolvimento |

## URLs da plataforma

| URL | Responsabilidade |
|---|---|
| `loja.club` | Site institucional da Loja Club |
| `www.loja.club` | Site institucional da Loja Club |
| `api.loja.club` | Backend FastAPI |
| `app.loja.club` | Painel do lojista |
| `admin.loja.club` | Admin interno da plataforma |
| `*.loja.club` | Lojas públicas dos lojistas |

Exemplos de lojas:

- `brindesfortaleza.loja.club`
- `presentescriativos.loja.club`
- `empresaexemplo.loja.club`

## Produção com AWS

Para produção V1, a sugestão é:

- ECS/Fargate para containers;
- ALB para balanceamento;
- RDS PostgreSQL;
- ElastiCache Redis;
- S3 para arquivos;
- CloudFront para CDN;
- Route 53 para DNS;
- ACM para certificados;
- CloudWatch para logs;
- Sentry para erros;
- SES para e-mails.

## Dev remoto barato

Para dev remoto ou beta inicial, uma alternativa barata é:

- EC2;
- Docker Compose;
- Traefik;
- RDS PostgreSQL;
- S3;
- CloudFront;
- Redis em container ou ElastiCache.

## Por que monólito modular

A V1 não deve começar com microserviços.

Motivos:

- menor complexidade;
- deploy mais simples;
- menor custo;
- menos contratos internos;
- menos problemas de rede;
- melhor velocidade de desenvolvimento;
- mais facilidade para alterar o domínio de negócio.

O monólito será modular internamente. Cada domínio terá seu módulo próprio.

## Módulos do backend

| Módulo | Responsabilidade |
|---|---|
| `accounts` | usuários, login, autenticação |
| `stores` | lojas e configurações |
| `domains` | subdomínio e domínio próprio |
| `tenancy` | resolução de loja e contexto multi-tenant |
| `catalog` | produtos, categorias, variações |
| `media` | upload e imagens |
| `product_customization` | modelos 3D, sessões de personalização e arte aprovada |
| `storefront` | dados para loja pública |
| `cart` | carrinho |
| `checkout` | fluxo de checkout |
| `payments` | gateway, split e webhooks |
| `orders` | pedidos |
| `customers` | clientes finais, guest sessions e histórico por loja |
| `shipping` | frete e entrega |
| `discounts` | cupons |
| `billing` | planos e cobrança da Loja Club |
| `notifications` | e-mails e notificações |
| `audit` | logs de auditoria |
| `platform_admin` | administração interna |
| `reports` | relatórios básicos |

## Princípios arquiteturais

1. Toda entidade comercial pertence a uma loja.
2. Toda consulta comercial deve filtrar por `store_id`.
3. O usuário não possui produto diretamente; a loja possui produto.
4. Um usuário pode participar de várias lojas.
5. Uma loja pode ter vários usuários.
6. Permissões são avaliadas por loja.
7. Plano da loja e permissão do usuário são camadas diferentes.
8. A loja pública é resolvida pelo domínio/subdomínio.
9. O checkout deve ser confirmado por webhook, não apenas pelo retorno visual do cliente.
10. A Loja Club não deve armazenar cartão.
11. A Loja Club não deve reter dinheiro de lojista.
12. Arquivos e imagens devem ficar fora do backend, em storage próprio.
13. Imagens públicas devem ser entregues por CDN.
14. Modelos 3D e artes enviadas por clientes devem ficar em storage próprio, com controle de acesso.
15. A personalização aprovada pelo cliente deve ser congelada no carrinho/pedido.
16. Cliente final pode comprar sem login obrigatório.
17. Registros de negócio usam soft delete/status arquivado.
18. Tarefas pesadas devem ir para fila.
19. Relatórios pesados não devem impactar a navegação pública.

## Estratégia de crescimento

A arquitetura deve permitir evoluir depois para:

- mais containers da API;
- mais workers;
- banco maior;
- read replicas;
- particionamento de tabelas;
- cache mais agressivo;
- serviços separados para checkout/pagamentos;
- isolamento especial para clientes grandes.

Mas a V1 não deve implementar complexidade antes da necessidade.
