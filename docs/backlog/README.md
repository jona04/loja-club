# Backlog — Loja Club

Este diretório contém o **backlog de implementação** da Loja Club, organizado **por fase**, espelhando o [V1 Roadmap](../17_v1_roadmap.md) mas em nível de tarefa.

O **MVP utilizável** (sem pagamento online) vai até a **Fase 4** e roda **100% local**. A **Fase 5** adiciona produtos **3D** (ainda local). As **Fases 6–7** sobem o sistema **no ar na AWS (EC2)** e cobrem conta do cliente, pagamentos, billing, admin, CI/CD e beta.

> **Toda a V1 é ambiente de dev.** Fases 0–5 = **dev local**; Fases 6–7 = **dev online na AWS (EC2)**. Produção robusta (ECS/Fargate) é **pós-V1**. Os arquivos usam **AWS S3 + CloudFront reais desde o dev local** (sem MinIO). Ver [doc 12](../12_aws_infrastructure_and_deployment.md).

> **Estrutura:** o **3D/personalização** é a **Fase 5 — Produtos 3D** (o lojista **gera os modelos via API de terceiros**; não há catálogo 3D da plataforma); **conta do cliente + pagamentos/planos** são a **Fase 6**; **ops/produção** a **Fase 7**. Cada fase é um incremento detalhado antes de virar tasks.

## Arquivos

| Fase | Arquivo | Etapas do roadmap | Objetivo |
|---|---|---|---|
| 0 | [phase-0-foundation.md](./phase-0-foundation.md) · [tasks](./phase-0-foundation/README.md) | 1–2 | Branding, config, Redis, esqueleto modular — **decomposta em tasks** |
| 1 | [phase-1-tenancy-and-dashboard.md](./phase-1-tenancy-and-dashboard.md) · [tasks](./phase-1-tenancy-and-dashboard/README.md) | 3–4 | Multi-tenancy, lojas, permissões, painel base — **decomposta em tasks** |
| 2 | [phase-2-catalog-and-media.md](./phase-2-catalog-and-media.md) · [tasks](./phase-2-catalog-and-media/README.md) | 5 | Catálogo (imagem) + mídia/S3 — **decomposta em tasks** |
| 3 | [phase-3-storefront-and-layouts.md](./phase-3-storefront-and-layouts.md) | 7–8 | Storefront Next.js, layouts (sem editor 3D) |
| 4 | [phase-4-sell-without-payment.md](./phase-4-sell-without-payment.md) | 9–14 + marco | Frete, cupons, carrinho, checkout, pedidos, clientes (guest), notificações — **tudo local** |
| 5 | [phase-5-3d-products.md](./phase-5-3d-products.md) | 6 | **Produtos 3D**: lojista gera via API + personalização + editor 3D no storefront |
| 6 | [phase-6-customer-account-and-payments.md](./phase-6-customer-account-and-payments.md) | 15–18 | **Deploy dev na AWS (EC2)**, conta/login do cliente, pagamentos e split, billing |
| 7 | [phase-7-platform-ops-and-production.md](./phase-7-platform-ops-and-production.md) | 19–22 | Admin da plataforma, segurança/observabilidade, **CI/CD**, beta |

> **Fim do MVP (dev local):** Fase 4. **V1 completa (dev online na AWS):** Fase 7.

## Granularidade: fases, etapas e tasks

```text
Fase     → arquivo .md genérico (visão geral / trilha) — sempre presente
           + pasta phase-N-*/ com README de índice, quando decomposta
 Etapa   → entregável do roadmap (## Etapa N)
  Task   → um arquivo por task na pasta, com ID estável P{fase}-{ÁREA}-{NN}
```

- Cada **task** é um arquivo com descrição, dependências (`depends_on`), docs de referência, **Escopo / Fora de escopo**, arquivos a alterar e **DoD**. Modelo em [`_task-template.md`](./_task-template.md).
- O **status** de cada task fica no frontmatter (`todo|doing|blocked|done`) e é refletido na tabela do README da fase.
- **Follow-ups / débitos técnicos:** cada README de fase tem uma seção **"Follow-ups / débitos técnicos"** (checkboxes). Toda nota de task que diga "fica para depois" **também** entra lá (ou vira task) — não fica só em prosa.
- **Materialização just-in-time:** cada fase **sempre** tem seu **arquivo `.md` genérico** (visão geral / trilha). Ao começar uma fase, ela é **decomposta**: cria-se a **pasta `phase-N-*/`** com uma task por arquivo + README de índice, **mantendo o `.md` genérico** como consulta (a trilha de alto nível que levou às tasks). Até agora as **Fases 0, 1 e 2** foram decompostas (`.md` genérico + pasta com tasks); as **Fases 3–7 seguem só com o `.md` genérico** (esboço) até entrarmos nelas.

## Fundações & Gargalos (leitura obrigatória)

Antes de qualquer fase, ver [`_foundations-and-bottlenecks.md`](./_foundations-and-bottlenecks.md): invariantes e decisões cross-fase (global/i18n, multi-tenancy, dinheiro, API, abstrações, segurança) + os gargalos antecipados. **Não é uma fase** — os itens base já viraram tasks na Fase 0; os demais entram nas fases respectivas.

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

- **Backend:** FastAPI, SQLModel, Pydantic v2, Alembic, JWT (`app/core/security.py`), recuperação de senha + e-mail (`app/utils.py` + MJML em `app/email-templates/`; o **envio passará pelo worker** — INV-F5), settings (`app/core/config.py`), `engine`/`init_db` (`app/core/db.py`), Pytest (`backend/tests/`).
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
4. **Convenção de módulo** (doc [04](../04_fastapi_template_adaptation.md)): cada módulo em `app/modules/<nome>/`, criando conforme a necessidade (não vazios). Responsabilidades: **`models.py` = só tabelas `table=True` + seus `*Base`**; **`schemas.py` = DTOs de API** (`*Create`/`*Update`/`*Public`/…); **`enums.py` = enums** (ex.: status); além de `routes.py`, `services.py`, `repositories.py`, `permissions.py`, `exceptions.py`. **DTOs e enums não ficam em `models.py`** (`schemas.py` importa o `*Base` de `models.py`). **`enums.py` e `schemas.py` são scaffolded em todos os módulos** (placeholder com docstring), populados quando necessário — exceção explícita ao "não criar vazios", que segue valendo para `routes.py`/`services.py`/`repositories.py`/`permissions.py`/`exceptions.py`.
5. **Soft delete** para todo registro de negócio; nunca hard delete (doc [07](../07_database_strategy.md)/[14](../14_security_strategy.md)).
6. **Toda query comercial filtra por `store_id`** (doc [06](../06_multitenancy_and_domains.md)/[14](../14_security_strategy.md)).
7. **APIs do painel** sob `/api/v1/stores/{store_id}/...`; **APIs públicas do storefront** resolvem a loja pelo header `Host` (doc [06](../06_multitenancy_and_domains.md)/[08](../08_modules_and_permissions.md)).
8. **Pagamento fica para a Fase 6.** Até lá, checkout cria pedido `pending_payment` e o pagamento é combinado fora da plataforma (doc [17](../17_v1_roadmap.md)).
9. **Ambiente:** toda a V1 é **dev**. Fases 0–4 rodam **local** (Docker Compose); Fases 6–7 sobem **no ar na AWS (EC2)**. **Storage:** AWS S3 + CloudFront **reais desde o dev local** (sem MinIO), via boto3. Produção (ECS/Fargate) é **pós-V1**. Doc [12](../12_aws_infrastructure_and_deployment.md).
10. **Global desde a base — nada assume Brasil.** Dinheiro é sempre `(valor + moeda ISO 4217)` (expoente não fixo em 2); telefone **E.164 para qualquer país** (lib, sem `+55` hard-coded); endereço **país-aware** (ISO 3166-1); `currency`/`locale` por loja e por cliente; timestamps em **UTC**. Base em `P0-MOD-05`; convenções completas no doc de Fundações.
11. **Clients de serviço externo abrem uma vez e são reusados** (DB, Redis, S3, pool do arq, HTTP `httpx`): **sync** = singleton de módulo em `app/core/*`; **async** (arq, httpx) = criados lazy por accessor e **fechados no lifespan** (`app/main.py`). Nunca abrir/fechar por chamada; por requisição usa-se só uma *unidade de trabalho*. Detalhe: **INV-F6** nas Fundações.

## Decisões pendentes que afetam o MVP

> Não bloqueiam começar, mas precisam ser fechadas dentro da fase indicada. Registrar a escolha aqui e em [18_open_decisions.md](../18_open_decisions.md).

- **Lib de fila/worker** (Fase 0/2): Celery vs RQ vs arq vs `BackgroundTasks`. Os docs pedem "fila leve com Redis" e "worker", sem fixar a lib.
- ~~Storage local~~ **(decidido)**: usar **AWS S3 + CloudFront reais** desde o dev local (sem MinIO). Requer bucket/distribuição/credenciais IAM de dev — tarefa na Fase 2.
- **Domínio de dev** (decidido): `loja.localhost` (e `*.loja.localhost`) localmente, espelhando o `*.loja.club` de produção. `*.localhost` resolve para 127.0.0.1 nos navegadores; usar `/etc/hosts` para ferramentas de CLI que precisarem.
