# Fase 0 — Fundação

> Roadmap: Etapas 1–2. Objetivo: deixar o projeto com a cara da Loja Club, com Redis, esqueleto modular e o exemplo `items` removido, pronto para construir os domínios reais.

Docs de referência: [03](../03_system_architecture.md), [04](../04_fastapi_template_adaptation.md), [07](../07_database_strategy.md), [16](../16_testing_strategy.md).

## Definition of Done da fase

- `docker compose watch` sobe backend, frontend, db, redis, traefik com branding Loja Club.
- `app/modules/` existe com mixins base e convenção de módulos.
- `Item` removido; `User` migrado para o módulo `accounts` como tabela `account_users`.
- Login/recuperação de senha continuam funcionando após o refactor.
- CI verde (lint + type check + testes).

---

## Etapa 1 — Branding e configuração

### Branding
- [ ] `.env`: `PROJECT_NAME="Loja Club"`, `STACK_NAME=loja-club`, `DOCKER_IMAGE_BACKEND`/`FRONTEND` para `loja-club-*`.
- [ ] `.env`: `DOMAIN=localhost.tiangolo.com` em dev (permite subdomínios via Traefik); documentar `DOMAIN=loja.club` para produção.
- [ ] `.env`: `BACKEND_CORS_ORIGINS` incluir `app.`, `admin.` e padrão de `*.` do domínio (doc [14](../14_security_strategy.md)).
- [ ] `.env`: gerar `SECRET_KEY` forte; ajustar `FIRST_SUPERUSER`/`FIRST_SUPERUSER_PASSWORD`.
- [ ] `frontend/index.html`: título e favicon Loja Club; substituir logo placeholder.
- [ ] `EMAILS_FROM_NAME` herda de `PROJECT_NAME` (já no `config.py`) — validar.
- [ ] Atualizar `README.md` raiz e `copier.yml` (nome do projeto).

### Settings (`backend/app/core/config.py`)
- [ ] Adicionar settings de **Redis**: `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD?`, `REDIS_DB`, e `@computed_field REDIS_URL`.
- [ ] Adicionar hosts da plataforma como settings derivados do `DOMAIN`: `api.`, `app.`, `admin.`, base para `*.` (doc [03](../03_system_architecture.md)/[06](../06_multitenancy_and_domains.md)).

---

## Etapa 1 — Redis

- [ ] `compose.yml`: serviço `redis` (`redis:7`/`redis:8`), com healthcheck; rede `default`.
- [ ] `compose.override.yml`: expor `6379` em dev.
- [ ] `backend/pyproject.toml`: dependência `redis` (cliente async).
- [ ] `app/core/cache.py`: factory `get_redis()` + helpers de get/set com TTL e prefixo de chave (doc [13](../13_performance_cache_and_cdn.md)).
- [ ] Healthcheck `/health/redis` (esqueleto; completo na Fase 4) (doc [15](../15_observability_and_operations.md)).

**Reconciliação:** o template não traz Redis. Adicioná-lo segue o doc [03](../03_system_architecture.md)/[13](../13_performance_cache_and_cdn.md) — sem divergência.

---

## Etapa 1 — Fila/worker (base)

> Decisão pendente: lib de fila (ver README do backlog). Manter mínimo nesta fase; o worker real entra na Fase 2 (thumbnails).

- [ ] Decidir lib de fila e registrar em [18_open_decisions.md](../18_open_decisions.md).
- [ ] Se a escolha exigir processo próprio, adicionar serviço `worker` (e `scheduler`, se aplicável) ao `compose.yml` (doc [03](../03_system_architecture.md)/[12](../12_aws_infrastructure_and_deployment.md)).
- [ ] `app/core/queue.py`: interface mínima `enqueue(task, *args)` para desacoplar o resto do código da lib escolhida.

---

## Etapa 2 — Esqueleto modular

### Base compartilhada
- [ ] Criar `app/db/base.py` com mixins: `UUIDMixin`, `TimestampMixin`, `SoftDeleteMixin`, `StoreScopedMixin` (doc [07](../07_database_strategy.md)).
- [ ] Criar `app/modules/__init__.py` e subpacotes (criar conforme uso): `accounts`, `stores`, `tenancy`, `domains`, `catalog`, `media`, `product_customization`, `storefront`, `cart`, `checkout`, `orders`, `customers`, `shipping`, `discounts`, `notifications`, `audit` (doc [03](../03_system_architecture.md)/[04](../04_fastapi_template_adaptation.md)).
- [ ] Definir convenção de 7 arquivos por módulo (doc [04](../04_fastapi_template_adaptation.md)).
- [ ] `app/api/main.py`: agregar routers dos módulos (substituir include de `items`).
- [ ] Garantir que todos os models sejam importados antes do `init_db` (comentário já existe em `app/core/db.py`) — criar `app/models_registry.py` ou importar em `app/modules/__init__.py`.

### Remover exemplo genérico `items`
- [ ] Remover `Item*` de `app/models.py`, `create_item` de `app/crud.py`, `app/api/routes/items.py`, `backend/tests/api/routes/test_items.py`, `backend/tests/utils/item.py`.
- [ ] Remover do frontend: `routes/_layout/items.tsx`, `components/Items/`.
- [ ] Migration Alembic para **dropar a tabela `item`** (dev: perda de dados aceitável).
- [ ] Remover include de `items` em `app/api/main.py`.

### Mover `User` → módulo `accounts`
- [ ] Mover modelos de usuário para `app/modules/accounts/models.py` como tabela **`account_users`** (`__tablename__ = "account_users"`), mantendo campos atuais (email único, is_active, is_superuser, full_name, hashed_password, created_at).
- [ ] Mover `create_user`/`update_user`/`get_user_by_email`/`authenticate` para `accounts/repositories.py` + `accounts/services.py`.
- [ ] Mover rotas de `login.py`/`users.py` para `accounts/routes.py` (manter paths atuais por ora).
- [ ] Atualizar `app/api/deps.py` (`get_current_user`) e `app/core/db.py` (`init_db`) para o novo import.
- [ ] Migration Alembic renomeando `user` → `account_users` (ou recriar a tabela).

**Reconciliação:** doc [07](../07_database_strategy.md) chama a tabela de `account_users`; o template usa `user`. Resolvido via `__tablename__`. `is_superuser` do template será mapeado depois para o conceito de admin de plataforma (doc [08](../08_modules_and_permissions.md)) — anotar na Fase 1.

---

## Etapa 2 — CI, lint e testes

- [ ] Ajustar GitHub Actions e pre-commit para os novos paths de módulos.
- [ ] Garantir `scripts/lint.sh`/`format.sh`/`test.sh` rodando após o refactor.
- [ ] Atualizar/conferir testes do template que referenciam `items`/`user` antigos.
- [ ] `frontend`: regenerar cliente OpenAPI (`npm run generate-client`) após mudanças de rota (doc [16](../16_testing_strategy.md)).

---

## Reconciliações (registrar aqui)

- (preencher conforme surgirem divergências código ↔ doc nesta fase)
