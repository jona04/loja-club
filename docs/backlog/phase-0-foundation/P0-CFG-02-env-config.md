---
id: P0-CFG-02
title: Variáveis de ambiente e domínio de dev
phase: 0
etapa: "Etapa 1 — Fundação do projeto"
area: CFG
status: done
depends_on: []
blocks: [P0-CFG-03]
tests: [unit]
---

# P0-CFG-02 — Variáveis de ambiente e domínio de dev

## Contexto
Para exercitar subdomínios de loja localmente (via Traefik wildcard) e preparar o multi-tenant, o ambiente de desenvolvimento precisa de um domínio que suporte subdomínios e de CORS para `app.`/`admin.`/`*.`. Também precisamos eliminar os segredos `changethis`.

## Docs de referência
- [03 — System Architecture](../../03_system_architecture.md)
- [06 — Multitenancy and Domains](../../06_multitenancy_and_domains.md)
- [14 — Security Strategy](../../14_security_strategy.md)

## Escopo (o que ENTRA)
- `.env`: `DOMAIN=localhost` no dev (`*.localhost` resolve para 127.0.0.1 nos navegadores; `/etc/hosts` para ferramentas de CLI), permitindo subdomínios via Traefik.
- `.env`: `BACKEND_CORS_ORIGINS` incluindo `http://app.localhost`, `http://admin.localhost` e o padrão de subdomínios de loja usado no dev.
- Remover os comentários/exemplos residuais do template que citam `localhost.tiangolo.com` (no `.env` e no `compose.override.yml`).
- **Portas de dev próprias** no `compose.override.yml` (evitar defaults e portas já usadas na máquina): db `5442`, redis `6399`, backend `8800`, frontend `5180`, adminer `8810`, mailcatcher `1090`/`1035`, traefik `8088`/`8091`. Front aponta pro backend em `http://localhost:8800`. Para rodar pytest local, conectar no Postgres da Loja Club em `localhost:5442` (`POSTGRES_PORT=5442`).
- `.env`: `SECRET_KEY` forte; `FIRST_SUPERUSER`/`FIRST_SUPERUSER_PASSWORD` reais.
- `config.py`: derivar hosts da plataforma a partir de `DOMAIN` (helpers `api_host`, `app_host`, `admin_host` e base para wildcard de storefront).
- `.env` + `config.py`: `PLATFORM_DEFAULT_CURRENCY` (ISO 4217, ex.: `USD`/`BRL`) e `PLATFORM_DEFAULT_LOCALE` (ex.: `pt-BR`) como **fallback global** (ver `P0-MOD-05`). Loja e cliente terão a própria moeda/locale nas fases seguintes.

## Fora de escopo (o que NÃO entra)
- DNS/SSL real, `*.loja.club` → Fase 6 (`P5-INFRA-*`).
- Resolução de loja pelo `Host` e tabela `domain_hosts` → Fase 1 (`P1-DOMAINS-*`/`P1-TENANCY-*`).
- Roteamento Traefik dos subdomínios em si → ajustado junto com painel/storefront (Fases 1/3); aqui só o `.env`/settings.

## Arquivos a criar/alterar
- `.env` (alterar) — `DOMAIN`, `BACKEND_CORS_ORIGINS`, `SECRET_KEY`, `FIRST_SUPERUSER*`; remover o comentário `# DOMAIN=localhost.tiangolo.com`.
- `compose.override.yml` (alterar) — remover o comentário que cita `localhost.tiangolo.com`.
- `backend/app/core/config.py` (alterar) — propriedades derivadas de hosts.

## Passos
1. Definir `DOMAIN=localhost` e ajustar `BACKEND_CORS_ORIGINS`.
2. Gerar `SECRET_KEY` forte (`python -c "import secrets; print(secrets.token_urlsafe(32))"`).
3. Adicionar em `config.py` `@computed_field` para `api_host`/`app_host`/`admin_host` baseados em `DOMAIN`.
4. Validar que `all_cors_origins` cobre os hosts do dev.

## Testes
> Fundações §10.

- **Níveis:** unit + verificação manual.
- **Quando:** durante.
- **Cobrir:**
  - unit — derivação de `api_host`/`app_host`/`admin_host` a partir de `DOMAIN`; `parse_cors`/`all_cors_origins`.
  - manual — subdomínio resolve via Traefik; sem warning de secret `changethis`.

## Definition of Done
- [x] `config.py` deriva os hosts da plataforma de `DOMAIN` (`api_host`/`app_host`/`admin_host`). *(resolução real via Traefik fica na **Fase 1**)*
- [x] CORS aceita os origins de dev (`localhost:5180`, `app.`/`admin.localhost:8088`). *(CORS de subdomínio de loja `*.` via regex entra com o storefront — **Fase 3**)*
- [x] Subir local **não** emite warning de secret `changethis` (SECRET_KEY/POSTGRES_PASSWORD/FIRST_SUPERUSER_PASSWORD fortes). *(pytest sem warnings)*

## Notas / Reconciliações
- `config.py` já tem `FRONTEND_HOST`, `all_cors_origins` e `parse_cors`; reaproveitar.
- `localhost` é o domínio de dev (índice do backlog).
- **Implementado:** secrets fortes (sem `changethis`); `DOMAIN=localhost`; hosts derivados em `config.py`; `PLATFORM_DEFAULT_CURRENCY=USD`/`PLATFORM_DEFAULT_LOCALE=en-US`; portas próprias (feitas na P0-TEST-01); resíduo tiangolo removido (`.env` + `compose.override.yml`). db recriado com a senha nova.
- **Reconciliação:** a resolução real de `app.`/`*.` via Traefik saiu para a **Fase 1** (roteamento) e **Fase 3** (regex CORS do storefront) — coerente com o "fora de escopo".
- `POSTGRES_PORT` no `.env` segue `5432` (porta interna do container); pytest local usa `POSTGRES_PORT=5442` (host).
