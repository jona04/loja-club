---
id: P0-CFG-03
title: Redis (cache/locks/fila leve)
phase: 0
etapa: "Etapa 1 — Fundação do projeto"
area: CFG
status: todo
depends_on: [P0-CFG-02]
blocks: [P0-CFG-04]
---

# P0-CFG-03 — Redis (cache/locks/fila leve)

## Contexto
Os docs preveem Redis para cache (domínio→loja, tema, home), locks de checkout, rate limit e fila leve. O template **não** traz Redis — precisa ser adicionado.

## Docs de referência
- [03 — System Architecture](../../03_system_architecture.md)
- [13 — Performance, Cache and CDN](../../13_performance_cache_and_cdn.md)

## Escopo (o que ENTRA)
- `compose.yml`: serviço `redis` (imagem `redis:7`/`redis:8`) com healthcheck, na rede `default`.
- `compose.override.yml`: expor `6379` no dev.
- `backend/pyproject.toml`: dependência do cliente `redis` (async).
- `backend/app/core/config.py`: `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD` (opcional), `REDIS_DB` e `@computed_field REDIS_URL`.
- `backend/app/core/cache.py`: `get_redis()` + helpers de get/set com TTL e prefixo de chave.
- Health check `/health/redis` (stub que dá `PING`).

## Fora de escopo (o que NÃO entra)
- Chaves de cache de domínio/storefront e invalidação → Fases 1/3.
- Rate limit → Fase 6 (`P6-SEC-*`).
- Fila/worker (usa Redis, mas é outra task) → `P0-CFG-04`.

## Arquivos a criar/alterar
- `compose.yml` (alterar) — serviço `redis` + `depends_on` no backend.
- `compose.override.yml` (alterar) — porta 6379.
- `backend/pyproject.toml` (alterar) — dep `redis`.
- `backend/app/core/config.py` (alterar) — settings de Redis.
- `backend/app/core/cache.py` (criar) — cliente + helpers.
- `backend/app/api/routes/utils.py` (alterar) — `/health/redis`.

## Passos
1. Adicionar o serviço `redis` no compose + porta no override.
2. Declarar a dependência `redis` no `pyproject.toml`.
3. Settings + `REDIS_URL` em `config.py`.
4. `cache.py` com `get_redis()` e helpers `cache_get`/`cache_set(ttl, prefix)`.
5. `/health/redis` fazendo `PING`.

## Definition of Done
- [ ] `redis` sobe no `docker compose` e o backend conecta.
- [ ] `GET /api/v1/utils/health/redis` retorna OK.
- [ ] `cache_set`/`cache_get` funcionam num teste manual.

## Notas / Reconciliações
- Em dev local, Redis é container; em dev online (Fase 5) pode ser container no EC2 ou ElastiCache (doc [12](../../12_aws_infrastructure_and_deployment.md)).
