---
id: P1-STORE-02
title: stores — serviço/rotas (criar→owner+subdomínio, settings, publish) + equipe
phase: 1
etapa: "Etapa 3 — Multi-tenancy (backend)"
area: STORE
status: done
depends_on: [P1-API-01, P1-STORE-01, P1-PERM-01, P1-DOM-01, P1-PERM-03]
blocks: [P1-DASH-02, P1-DASH-03]
tests: [integration]
---

# P1-STORE-02 — `stores`: serviço e rotas (criar loja, settings, publish) + equipe

## Contexto
Com modelos, membership, domínios, tenancy e autorização prontos, esta task entrega os **endpoints do painel** para o ciclo de vida da loja e da equipe (doc [09](../../09_merchant_dashboard.md)/[20](../../20_api_contracts_todo.md)), seguindo o padrão de API (`P1-API-01`). O fluxo central é **criar loja → membership owner + subdomínio automático**, de forma atômica.

## Docs de referência
- [09 — Merchant Dashboard](../../09_merchant_dashboard.md)
- [20 — API Contracts TODO](../../20_api_contracts_todo.md) (grupos Stores e Store Members)
- [06 — Multitenancy and Domains](../../06_multitenancy_and_domains.md) (criação de subdomínio)
- [08 — Modules and Permissions](../../08_modules_and_permissions.md) (gating por permissão)

## Escopo (o que ENTRA)
- **Stores** (`/api/v1/stores`): `POST /` criar loja; `GET /` minhas lojas (do usuário logado); `GET /{store_id}` obter; `PATCH /{store_id}/settings`; `POST /{store_id}/publish`; `POST /{store_id}/pause`.
- **Geração de slug** a partir do nome + **disponibilidade** (coordena com `domains.check_availability`).
- **Fluxo de criação atômico:** `Store` + `StoreMember(role=owner)` + `domain_hosts` `{slug}.{DOMAIN}` (chama `domains.create_platform_subdomain`). Tudo numa transação.
- **Equipe** (`/api/v1/stores/{store_id}/members`): `GET` listar; `POST` convidar; `PATCH /{user_id}` alterar papel; `DELETE /{user_id}` remover. Gated por `team.*`.
- **Permissões do membro ativo:** expor o papel + permissões do usuário na loja (ex.: `GET /api/v1/stores/{store_id}/me`) para o menu dinâmico do painel (`P1-DASH-03`).
- **Gating:** criar loja = qualquer `account_user` autenticado; settings/publish/equipe via `require_permission` (`settings.update`, `team.*`). Respostas no padrão `P1-API-01`.

## Fora de escopo (o que NÃO entra)
- Telas do painel → `P1-DASH-02`/`P1-DASH-03` (esta task entrega só a API).
- Envio de e-mail de convite (texto/fluxo completo) → **pelo worker** (task `send_email`, INV-F5); aqui só o registro do membro `invited`.
- Domínio próprio → fora do MVP (`P1-DOM-01`).

## Arquivos a criar/alterar
- `backend/app/modules/stores/services.py` (criar) — criar loja (atômico), slug, publish/pause.
- `backend/app/modules/stores/routes.py` (criar) — rotas de stores + members.
- `backend/app/modules/stores/repositories.py` (criar) — acesso scoped por `store_id`.
- `backend/app/api/main.py` (alterar) — incluir o router de stores.
- Regenerar client OpenAPI (consumido pelo painel) — ou deixar para `P1-DASH-02`.

## Passos
1. Serviço de criação atômica (Store + owner member + subdomínio); rollback se qualquer passo falhar.
2. Slug a partir do nome + disponibilidade.
3. Rotas de stores (CRUD/publish/pause) e de equipe, com `require_permission`.
4. Incluir router no `api/main.py`; aplicar padrão de paginação em `GET /`.
5. Testes de integração do fluxo e do gating.

## Testes
> Fundações §10.

- **Níveis:** integração (fluxo transacional, constraints e permissões são fronteiras reais).
- **Quando escrever:** durante.
- **Cobrir:**
  - integração — `POST /stores` cria `store_stores` + `store_members(owner)` + `domain_hosts` subdomínio ativo (atômico); `GET /stores` lista só as do usuário; slug duplicado é rejeitado; `support` não publica/edita settings (403); convite cria membro `invited`.

## Definition of Done
- [x] `POST /stores` cria `store_stores` + `store_settings` + `store_members(owner)` + `domain_hosts` (subdomínio ativo) **atomicamente** (teste).
- [x] CRUD/publish/pause + equipe + `GET /{id}/me` no padrão `P1-API-01`, com gating por `require_permission` (teste: owner ok, support 403).
- [x] `GET /stores` lista só as lojas do usuário; não-membro em `GET /{id}` → 403 *(121 testes; cobertura 91%)*.

## Notas / Reconciliações
- **Endpoints:** `POST /` (criar), `GET /` (minhas lojas, `Page`), `GET /{id}` (`ActiveStore`), `PATCH /{id}/settings`, `POST /{id}/publish|pause`, `GET /{id}/me` (papel+permissões p/ o menu da `P1-DASH-03`), e equipe `GET|POST /{id}/members`, `PATCH|DELETE /{id}/members/{user_id}`. Gating via `dependencies=[Depends(require_permission(...))]` no decorator (evita arg não-usado).
- **Slug** derivado do nome (`slugify`, DNS-safe) com override opcional; disponibilidade via `domains.is_subdomain_available`; `currency`/`locale` default do `PLATFORM_DEFAULT_*`.
- **`is_published`** mantido consistente com `status` no publish/pause (active↔paused). Storefront público (Fase 3) decide o que usar.
- **Convite (MVP):** só convida **usuário já existente** (e-mail → `account_user`); cria membro `invited`. Convite por e-mail novo (cria conta shell + e-mail de onboarding) e o **fluxo de aceite** (`invited`→`active`) ficam para depois — ver Follow-ups.
- **Client OpenAPI:** regeneração deixada para a `P1-DASH-02` (quem consome).

## Follow-ups
- [ ] **Convite por e-mail novo** (cria `account_user` shell + **enfileira** o e-mail de onboarding no worker — INV-F5). *Quando:* quando o onboarding de equipe for necessário. → README da fase.
- [ ] **Fluxo de aceite de convite** (`invited`→`active`); hoje membro `invited` não opera. *Quando:* junto do onboarding de equipe. → README da fase.
- [ ] **Proteção do owner** (não permitir alterar papel/remover o último `owner`, evitando órfão). *Quando:* antes de produção. → README da fase.
