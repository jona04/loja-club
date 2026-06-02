---
id: P0-CFG-02
title: Variáveis de ambiente e domínio de dev
phase: 0
etapa: "Etapa 1 — Fundação do projeto"
area: CFG
status: todo
depends_on: []
blocks: [P0-CFG-03]
---

# P0-CFG-02 — Variáveis de ambiente e domínio de dev

## Contexto
Para exercitar subdomínios de loja localmente (via Traefik wildcard) e preparar o multi-tenant, o ambiente local precisa de um domínio que suporte subdomínios e de CORS para `app.`/`admin.`/`*.`. Também precisamos eliminar os segredos `changethis`.

## Docs de referência
- [03 — System Architecture](../../03_system_architecture.md)
- [06 — Multitenancy and Domains](../../06_multitenancy_and_domains.md)
- [14 — Security Strategy](../../14_security_strategy.md)

## Escopo (o que ENTRA)
- `.env`: `DOMAIN=localhost.tiangolo.com` no dev (resolve `*.localhost.tiangolo.com` em 127.0.0.1, permitindo subdomínios via Traefik).
- `.env`: `BACKEND_CORS_ORIGINS` incluindo `http://app.localhost.tiangolo.com`, `http://admin.localhost.tiangolo.com` e o padrão de subdomínios de loja usado no dev.
- `.env`: `SECRET_KEY` forte; `FIRST_SUPERUSER`/`FIRST_SUPERUSER_PASSWORD` reais.
- `config.py`: derivar hosts da plataforma a partir de `DOMAIN` (helpers `api_host`, `app_host`, `admin_host` e base para wildcard de storefront).

## Fora de escopo (o que NÃO entra)
- DNS/SSL real, `*.loja.club` → Fase 5 (`P5-INFRA-*`).
- Resolução de loja pelo `Host` e tabela `domain_hosts` → Fase 1 (`P1-DOMAINS-*`/`P1-TENANCY-*`).
- Roteamento Traefik dos subdomínios em si → ajustado junto com painel/storefront (Fases 1/3); aqui só o `.env`/settings.

## Arquivos a criar/alterar
- `.env` (alterar) — `DOMAIN`, `BACKEND_CORS_ORIGINS`, `SECRET_KEY`, `FIRST_SUPERUSER*`.
- `backend/app/core/config.py` (alterar) — propriedades derivadas de hosts.

## Passos
1. Definir `DOMAIN=localhost.tiangolo.com` e ajustar `BACKEND_CORS_ORIGINS`.
2. Gerar `SECRET_KEY` forte (`python -c "import secrets; print(secrets.token_urlsafe(32))"`).
3. Adicionar em `config.py` `@computed_field` para `api_host`/`app_host`/`admin_host` baseados em `DOMAIN`.
4. Validar que `all_cors_origins` cobre os hosts do dev.

## Definition of Done
- [ ] `http://app.localhost.tiangolo.com` e um subdomínio de loja de teste resolvem localmente via Traefik.
- [ ] CORS aceita chamadas de `app.`/`*.` locais.
- [ ] Subir local **não** emite warning de secret `changethis`.

## Notas / Reconciliações
- `config.py` já tem `FRONTEND_HOST`, `all_cors_origins` e `parse_cors`; reaproveitar.
- `localhost.tiangolo.com` é a opção de domínio de dev registrada nas decisões pendentes do backlog.
