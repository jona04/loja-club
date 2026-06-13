---
id: P7-SESS-01
title: Sessões de personalização (backend) + assistida/link público
phase: 7
etapa: "Etapa 4 — Sessões de personalização (backend)"
area: SESS
status: todo
depends_on: [P7-PROD-01]
blocks: [P7-EDITOR-01, P7-ORD-01, P7-OPS-01]
tests: [integration]
---

# P7-SESS-01 — Sessões de personalização (backend)

## Contexto
O backend que sustenta o editor: criar/recuperar a **sessão**, **autosave** do `state_json`, **upload de arte privado**, **aprovar** (congela snapshot + versão), expirar em 30 dias, e a **personalização assistida** (lojista monta pelo cliente) com **link público**.

## Docs de referência
- [30 — §4 state_json / §5 Snapshot / §6 Storage / §9 Assistida](../../concepts/30_3d_customization_technical_design.md)
- [07 — `customization_sessions`/`uploads` + índices](../../concepts/07_database_strategy.md)

## Escopo (o que ENTRA)
- `customization_sessions` (`state_json`, `platform_3d_model_version_id`, `status`, `guest_session_id`, `customer_id?`, `created_by?`, `snapshot_key?`, `public_token?`, `expires_at`, `approved_at`) + `customization_uploads` (`key` privado, `mime`, `size_bytes`, `width`/`height`). Índices do doc 07 (inclui `public_token` único). Migration.
- Status de sessão (`draft|approved|added_to_cart|ordered|abandoned|expired`) + enum de **status de arte/produção** (`received…production_done`).
- Rotas: iniciar/obter sessão; **autosave** `state_json` (validado contra a versão); **upload de arte** (raster, validado, **privado**, URL assinada); **aprovar** (recebe o snapshot client-side → guarda; congela `version_id` + `state_json` + data).
- **Expirar 30 dias** → `expired` (worker `arq`).
- **Assistida** (doc [30 §9](../../concepts/30_3d_customization_technical_design.md)): criar sessão pela loja (`created_by`) + `create_or_update_customer` (Fase 6) + **`public_token`** assinado; endpoint **público read-only** (ver pelo token) + **aprovar confirmando o contato** (sem conta).

## Fora de escopo (o que NÃO entra)
- Editor no storefront (UI): `P7-EDITOR-*`.
- Congelar no carrinho/pedido: `P7-ORD-01`.
- Tela do lojista pra operar/montar: `P7-OPS-01`.

## Arquivos a criar/alterar
- `backend/app/modules/customization/{models,enums,schemas,repositories,services,routes}.py` (alterar).
- `backend/app/core/storage.py` (reuso) — chaves `private/<store_id>/customizations/...`.
- worker task de expiração (`app/modules/customization/tasks.py` + `WorkerSettings.functions`).
- migration alembic.

## Passos
1. Models + status enums + migration (índices, `public_token` único).
2. Rotas: start/get, autosave, upload privado (presigned), approve (snapshot).
3. Worker de expiração (30 dias → `expired`).
4. Assistida: criar pela loja + `public_token` + endpoint público read-only + aprovar por confirmação de contato.

## Testes
- **Níveis:** integração.
- **Quando escrever:** durante.
- **Cobrir:** integração — autosave persiste e valida contra a versão; upload privado gera URL assinada; aprovar exige snapshot e congela `version_id`; isolamento por loja; `public_token` abre read-only e aprovar pede contato.

## Definition of Done
- [ ] Sessão cria/autosave/upload/aprovar funcionando; arte **privada** (assinada); aprovar **congela** versão+estado+snapshot.
- [ ] Expiração 30 dias no worker (`expired` + `deleted_at`, sem hard delete).
- [ ] Assistida: `public_token` read-only + aprovar por confirmação de contato (sem conta).
- [ ] **Modos de falha mapeados** — upload tipo/tamanho inválido (422)/baixa resolução (aviso); aprovar sem snapshot bloqueia; sessão expirada no autosave; `public_token` inválido/expirado. → tratados/Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- `state_json` validado **no backend** contra a versão (não confiar no cliente). Schema = doc [30 §4](../../concepts/30_3d_customization_technical_design.md).

## Follow-ups
- [ ] **Limpeza de arquivos de sessões expiradas** (mantendo histórico de negócio) — *Quando:* política de retenção. → README da fase.
- [ ] **Anti-abuso no endpoint público** (rate limit do `public_token`) — *Quando:* hardening (Fase 10). → README da fase.
