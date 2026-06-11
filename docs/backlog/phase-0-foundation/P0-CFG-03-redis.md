---
id: P0-CFG-03
title: Redis (cache/locks/fila leve)
phase: 0
etapa: "Etapa 1 — Fundação do projeto"
area: CFG
status: done
depends_on: [P0-CFG-02]
blocks: [P0-CFG-04]
tests: [unit, integration]
---

# P0-CFG-03 — Redis (cache/locks/fila leve)

## Contexto
Os docs preveem Redis para cache (domínio→loja, tema, home), locks de checkout, rate limit e fila leve. O template **não** traz Redis — precisa ser adicionado.

## Docs de referência
- [03 — System Architecture](../../concepts/03_system_architecture.md)
- [13 — Performance, Cache and CDN](../../concepts/13_performance_cache_and_cdn.md)

## Escopo (o que ENTRA)
- `compose.yml`: serviço `redis` (imagem `redis:7`/`redis:8`) com healthcheck, na rede `default`.
- `compose.override.yml`: expor `6379` no dev.
- `backend/pyproject.toml`: dependência do cliente `redis` (async).
- `backend/app/core/config.py`: `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD` (opcional), `REDIS_DB` e `@computed_field REDIS_URL`.
- `backend/app/core/cache.py`: `get_redis()` + helpers de get/set com TTL e prefixo de chave.
- Health checks **top-level** `/health` e `/health/redis` (este faz `PING`), seguindo o padrão do doc [15](../../concepts/15_observability_and_operations.md). `/health/db` e demais são completados na Fase 6.

## Fora de escopo (o que NÃO entra)
- Chaves de cache de domínio/storefront e invalidação → Fases 1/3.
- Rate limit → Fase 9.
- Fila/worker (usa Redis, mas é outra task) → `P0-CFG-04`.

## Arquivos a criar/alterar
- `compose.yml` (alterar) — serviço `redis` + `depends_on` no backend.
- `compose.override.yml` (alterar) — porta 6379.
- `backend/pyproject.toml` (alterar) — dep `redis`.
- `backend/app/core/config.py` (alterar) — settings de Redis.
- `backend/app/core/cache.py` (criar) — cliente + helpers.
- `backend/app/main.py` (alterar) — endpoints `/health` e `/health/redis` **top-level** (fora de `/api/v1`).

## Passos
1. Adicionar o serviço `redis` no compose + porta no override.
2. Declarar a dependência `redis` no `pyproject.toml`.
3. Settings + `REDIS_URL` em `config.py`.
4. `cache.py` com `get_redis()` e helpers `cache_get`/`cache_set(ttl, prefix)`.
5. `/health` e `/health/redis` (este fazendo `PING` no Redis), top-level.

## Testes
> Fundações §10. Segue o layout de `P0-TEST-01`.

- **Níveis:** unit + integração.
- **Quando:** durante.
- **Cobrir:**
  - unit — construção de chave/prefixo e TTL do cache.
  - integração — round-trip `cache_set`/`cache_get` no Redis real; `GET /health/redis` faz PING.

## Definition of Done
- [x] `redis` sobe no `docker compose` e o backend conecta. *(loja-club-redis-1 healthy, 6399)*
- [x] `GET /health/redis` retorna OK. *(test_health_redis_ok)*
- [x] `cache_set`/`cache_get` funcionam. *(teste automatizado, não só manual)*

## Notas / Reconciliações
- Em dev local, Redis é container; em dev online (Fase 8) pode ser container no EC2 ou ElastiCache (doc [12](../../concepts/12_aws_infrastructure_and_deployment.md)).
- **Reconciliação (feito):** padronizei para `/health*` (doc [15](../../concepts/15_observability_and_operations.md)); o `test:` do healthcheck do backend no `compose.yml` aponta para `/health`. O endpoint antigo `/api/v1/utils/health-check/` do template segue existindo (inofensivo) — remover depois se quiser.
- **Implementado:** `redis:8` (host **6399**, interno 6379); `REDIS_HOST=redis` no container; pytest local usa `REDIS_PORT=6399` (o `.env` mantém `6379` interno). `cache.py` = redis-py **síncrono** (estilo do template); `Redis` não é genérico no redis-py 8 (sem `Redis[str]`). 67 testes passam; gate `app` verde.
