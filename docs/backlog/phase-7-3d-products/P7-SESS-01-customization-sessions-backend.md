---
id: P7-SESS-01
title: Sessões de personalização (backend) + assistida/link público
phase: 7
etapa: "Etapa 4 — Sessões de personalização (backend)"
area: SESS
status: done
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
- [x] Sessão cria/autosave/upload/aprovar funcionando; arte **privada** (URL assinada); aprovar **congela** versão+estado+snapshot.
- [x] Expiração 30 dias no worker (`expired` + `deleted_at`, sem hard delete).
- [x] Assistida: `public_token` read-only + aprovar por confirmação de contato (sem conta).
- [x] **Modos de falha mapeados** — upload tipo (422)/tamanho (413)/baixa resolução (aviso, não bloqueia); aprovar exige snapshot PNG; autosave/upload/aprovar em sessão **expirada → 410** ou **não-draft → 409**; `state_json` inválido (fonte/área/transform/camadas/versão) → 422; `public_token` inválido (404)/expirado (410). Cobertos por testes.
- [x] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- `state_json` validado **no backend** contra a versão fixada (não confiar no cliente): `schema_version`, `model.version_id` == versão da sessão, `area_id` ∈ áreas da versão, `transform.x/y ∈ [0,1]` + `scale > 0`, camada `image` referencia upload da sessão, camada `text` usa fonte permitida + `font_size` no range, `max_layers` por área. Schema = doc [30 §4](../../concepts/30_3d_customization_technical_design.md).
- **Lógica de sessão** em `app/modules/customization/sessions.py` (separada do catálogo em `services.py`, como `customers` separa `normalization.py`). Tabelas `customization_sessions` + `customization_uploads` (migration `c5405babf7da`; índices do doc 07 incl. `public_token` único parcial; `alembic check` vazio).
- **Rotas:** storefront público (guest cookie, host-resolvido) `POST/GET /storefront/customizations[...]` + `/state` + `/uploads` + `/approve`; link público `GET /storefront/p/{token}` + `POST .../approve`; painel `POST /stores/{id}/customizations/assisted` (gate `customization.sessions.view`).
- **Snapshot** = PNG client-side obrigatório no approve (doc §5); guardado privado em `private/<store_id>/customizations/<session_id>/...` (URL assinada). Upload de arte idem; nome de arquivo gerado por uuid (não confia no nome do cliente).
- **Worker:** `cron` `expire_customization_sessions` varre `draft`/`approved` vencidas → `expired` + `deleted_at` (nunca hard delete; não `added_to_cart`/`ordered`, comprometidas com a compra). A expiração também é aplicada **no acesso** (vencida → **410**), então o cron é só faxina. **Valores (TTL, agendamento, limites de upload, etc.) = fonte de verdade em [doc 31 §4](../../concepts/31_configuration_and_constants.md).**
- **`public_token`** = `secrets.token_urlsafe(32)` (inadivinhável) + validade pelo `expires_at` da sessão; read-only. (Doc diz "assinado"; um token aleatório com lookup no banco + expiry é equivalente em escopo/segurança aqui — sem JWT.)
- **Status de arte/produção** (`received…production_done`) **não** entra aqui: ninguém o lê na Fase 7 até o pedido existir (regra "status tem que ter serventia"). Entra em `P7-ORD-01`/`P7-OPS-01`, no **item do pedido** congelado (quem decide algo com ele). Enum de **sessão** (`draft|approved|added_to_cart|ordered|abandoned|expired`) entregue.

## Follow-ups
- [ ] **Limpeza de arquivos de sessões expiradas** (S3) mantendo histórico de negócio — *Quando:* política de retenção. → README da fase.
- [ ] **Anti-abuso no endpoint público** (rate limit do `public_token`) — *Quando:* hardening (Fase 10). → README da fase.
- [ ] **Strip de metadados/sanitização real da imagem** (re-encode) no upload — hoje valida mime/tamanho/decodificação e gera nome próprio, mas não re-encoda pra remover EXIF. Origem: `P7-SESS-01`. → README.
- [ ] **Status de arte/produção no item do pedido** (`received…production_done`) — criar onde é lido (`P7-ORD-01`/`P7-OPS-01`). → README.
