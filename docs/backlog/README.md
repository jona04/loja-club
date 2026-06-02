# Backlog — Loja Club

Este diretório contém o **backlog de implementação** da Loja Club, organizado **por fase**, espelhando o [V1 Roadmap](../17_v1_roadmap.md) mas em nível de tarefa.

O foco atual é **finalizar tudo até a Fase 4** (o MVP utilizável para teste, sem pagamento online). As Fases 5 e 6 ganharão backlog próprio quando chegarmos nelas, para não inchar os arquivos.

## Arquivos

| Fase | Arquivo | Etapas do roadmap | Objetivo |
|---|---|---|---|
| 0 | [phase-0-foundation.md](./phase-0-foundation.md) | 1–2 | Branding, config, Redis, esqueleto modular |
| 1 | [phase-1-tenancy-and-dashboard.md](./phase-1-tenancy-and-dashboard.md) | 3–4 | Multi-tenancy, lojas, permissões, painel base |
| 2 | [phase-2-catalog-media-3d.md](./phase-2-catalog-media-3d.md) | 5–6 | Catálogo, mídia/S3, personalização 3D |
| 3 | [phase-3-storefront-and-layouts.md](./phase-3-storefront-and-layouts.md) | 7–8 | Storefront Next.js, editor 3D, layouts |
| 4 | [phase-4-sell-without-payment.md](./phase-4-sell-without-payment.md) | 9–14 + marco | Frete, cupons, carrinho, checkout, pedidos, clientes, notificações, deploy de teste |
| 5–6 | *(a criar)* | 15–21 | Conta do cliente, pagamentos, billing, admin, segurança, infra, beta |

## Regra de ouro (alinhamento código ↔ docs)

1. O **código imita a lógica dos docs**. Não inventar lógica de negócio nova no código.
2. Se uma **limitação técnica** impedir seguir o doc, **atualizar o `.md`** para refletir o que o código realmente faz.
3. **Nunca** deixar o doc dizendo uma coisa e o código fazendo outra.
4. Toda divergência resolvida deve ser anotada na seção **"Reconciliações"** da fase, citando o doc afetado.

## Legenda de status

- `[ ]` a fazer
- `[~]` em andamento
- `[x]` concluído

Todas as tarefas começam em `[ ]`.

## Estado atual do código (baseline)

> Verificado em 2026-06-01. Tudo abaixo é o **Full Stack FastAPI Template** sem alterações de produto — só docs foram commitados.

O que o template **já entrega** e vamos reaproveitar:

- **Backend:** FastAPI, SQLModel, Pydantic v2, Alembic, JWT (`app/core/security.py`), recuperação de senha + e-mail (`app/utils.py` + MJML em `app/email-templates/`), settings (`app/core/config.py`), `engine`/`init_db` (`app/core/db.py`), Pytest (`backend/tests/`).
- **Frontend (painel):** React 19, Vite 7, TanStack Router + Query + Table, Tailwind v4, shadcn/Radix, react-hook-form, zod, axios, cliente OpenAPI gerado via `@hey-api/openapi-ts` (`frontend/src/client/`).
- **Infra dev:** Docker Compose (`compose.yml` + `compose.override.yml`), Traefik (`proxy`), Postgres 18 (`db`), Adminer, Mailcatcher, Playwright; Dockerfiles; GitHub Actions; pre-commit.

O que **não existe** ainda e precisa ser criado (resumo; detalhe nas fases):

- nenhum módulo: `app/models.py` só tem `User` e `Item`; `app/crud.py` único.
- sem `Store`, `store_id`, multi-tenancy, permissões por loja, `domain_hosts`.
- sem **Redis**, **worker**, **S3**, **storefront Next.js**, **frontend-admin**.
- `PROJECT_NAME` ainda é `"Full Stack FastAPI Project"`; Traefik roteia `api.`, `dashboard.`, `adminer.` (docs querem `api.`, `app.`, `admin.`, `*.`).

## Decisões técnicas globais (valem para todas as fases)

Estas decisões alinham o template aos docs e evitam divergência:

1. **PK = UUID** (padrão do template). Os exemplos com id inteiro nos docs (`id: 123`) são ilustrativos, não normativos.
2. **Nomes de tabela com prefixo de domínio** (doc [07](../07_database_strategy.md)): definir `__tablename__` explicitamente (ex.: `account_users`, `store_stores`, `catalog_products`). O template usa `user`/`item` por padrão — será sobrescrito.
3. **Mixins base** em `app/db/` (ou `app/core/`): `UUIDMixin`, `TimestampMixin` (`created_at`/`updated_at`), `SoftDeleteMixin` (`deleted_at`/`deleted_by_user_id`/`delete_reason`), `StoreScopedMixin` (`store_id`). Doc [07](../07_database_strategy.md), [14](../14_security_strategy.md).
4. **Convenção de módulo** (doc [04](../04_fastapi_template_adaptation.md)): cada módulo em `app/modules/<nome>/` com `models.py`, `schemas.py`, `routes.py`, `services.py`, `repositories.py`, `permissions.py`, `exceptions.py` (criar conforme a necessidade, não vazios).
5. **Soft delete** para todo registro de negócio; nunca hard delete (doc [07](../07_database_strategy.md)/[14](../14_security_strategy.md)).
6. **Toda query comercial filtra por `store_id`** (doc [06](../06_multitenancy_and_domains.md)/[14](../14_security_strategy.md)).
7. **APIs do painel** sob `/api/v1/stores/{store_id}/...`; **APIs públicas do storefront** resolvem a loja pelo header `Host` (doc [06](../06_multitenancy_and_domains.md)/[08](../08_modules_and_permissions.md)).
8. **Pagamento fica para a Fase 5.** Até lá, checkout cria pedido `pending_payment` e o pagamento é combinado fora da plataforma (doc [17](../17_v1_roadmap.md)).

## Decisões pendentes que afetam o MVP

> Não bloqueiam começar, mas precisam ser fechadas dentro da fase indicada. Registrar a escolha aqui e em [18_open_decisions.md](../18_open_decisions.md).

- **Lib de fila/worker** (Fase 0/2): Celery vs RQ vs arq vs `BackgroundTasks`. Os docs pedem "fila leve com Redis" e "worker", sem fixar a lib.
- **Storage local em dev** (Fase 2): MinIO (S3-compatible) como stand-in do S3 em dev. Docs assumem S3/CloudFront em produção — MinIO não contradiz, é compatível.
- **Domínio de teste** (Fase 1/4): usar `localhost.tiangolo.com` (e `*.localhost.tiangolo.com`) localmente para exercitar subdomínios via Traefik antes do `*.loja.club` real.
