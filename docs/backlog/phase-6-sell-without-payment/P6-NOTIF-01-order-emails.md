---
id: P6-NOTIF-01
title: E-mails de pedido (worker) + health + E2E do marco
phase: 6
etapa: "Etapa 7 — Notificações + finalização local"
area: NOTIF
status: done
depends_on: [P6-ORD-01, P6-CHK-01]
blocks: []
tests: [integration, e2e]
---

# P6-NOTIF-01 — E-mails de pedido + finalização local

## Contexto
Fecha o marco: cliente e lojista recebem e-mail ao criar pedido (no **worker**, nunca inline — INV-F5), e o fluxo de ponta a ponta roda no Docker Compose com health checks.

## Docs de referência
- [13 — Performance/cache (worker)](../../concepts/13_performance_cache_and_cdn.md)
- [15 — Observability and Operations](../../concepts/15_observability_and_operations.md)
- [16 — Testing strategy](../../concepts/16_testing_strategy.md)

## Escopo (o que ENTRA)
- Templates + envio: **pedido criado** (cliente) e **novo pedido** (lojista) — reaproveitar a base `send_email` + MJML do template.
- **Envio no worker** (task `send_email` enfileirada via `enqueue()`, INV-F5), com retry. Dev: e-mails caem no **Mailcatcher**.
- Health checks `/health`, `/health/db`, `/health/redis` no ambiente local.
- **E2E do marco** (fluxo completo): criar conta → loja → produto → carrinho → checkout → pedido → painel.

## Fora de escopo (o que NÃO entra)
- SES/SMTP real: **Fase 8**.
- E-mails de status/envio (shipped/delivered): follow-up se não couber.

## Arquivos a criar/alterar
- `backend/app/modules/notifications/{services,tasks}.py` (criar) — tasks de e-mail.
- `backend/app/email-templates/...` (criar) — MJML de pedido.
- e2e (Playwright) do marco.

## Passos
1. Templates MJML + tasks de e-mail enfileiradas (worker).
2. Disparar no `create_order` (via `enqueue`).
3. Health checks + E2E do marco.

## Testes
- **Níveis:** integração (e-mail enfileirado, não inline) + e2e (marco).
- **Cobrir:** integração — criar pedido **enfileira** `send_email` (cliente + lojista), não envia inline; falha de envio não derruba o pedido (retry no worker). e2e — fluxo completo do marco cai no Mailcatcher.

## Definition of Done
- [x] E-mails "pedido criado" (cliente) + "novo pedido" (lojista) **no worker** (enqueue, com retry do arq).
- [x] Health checks `/health`/`/health/db`/`/health/redis` (db `SELECT 1`; redis PING).
- [x] **Marco end-to-end coberto por integração** (loja c/ dono → produto → carrinho → checkout → pedido → e-mails enfileirados → painel lista → marca pago); **Playwright do marco = follow-up** (infra de e2e do storefront ainda bloqueada — `P5-SF-01`).
- [x] **Modos de falha mapeados** (enqueue falho → pedido persiste [dispatch best-effort, logado]; worker re-tenta o envio; Mailcatcher fora → e-mail perdido mas pedido ok) → tratados/Follow-ups.
- [x] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- **INV-F5:** todo e-mail é **enfileirado** — `notifications/tasks.py:send_order_email` (registrado no `WorkerSettings.functions`) chama `app.utils.send_email`; o **retry** é o padrão do arq. Dev: cai no **Mailcatcher**.
- **Onde dispara:** o doc dizia "no `create_order`", mas `enqueue` é **async** e `create_order` é sync/reusável; o dispatch fica na **rota de checkout** (`submit_checkout` virou `async`), logo após o pedido ser criado — a fronteira async correta (igual ao `media`). `create_order` segue puro.
- **Best-effort:** `notifications.services.dispatch_order_emails` engloba render+enqueue num `try/except` (loga e engole) — uma falha de fila **nunca** derruba o checkout (o pedido é a fonte da verdade).
- **Destinatário do lojista:** `store_settings.contact_email`; senão **e-mail do dono** (membership `owner` → `User.email`).
- **Templates:** `email-templates/src/order_placed.mjml`/`order_received.mjml` (fonte) + `build/*.html` (Jinja: `store_name`/`order_number`/loop de itens/`total`). O `build/*.html` é **autoral** (CLI do mjml não roda no pipeline) — ver follow-up.

## Follow-ups
- [ ] **Playwright do marco (browser + Mailcatcher)** — o fluxo completo no navegador (criar conta no painel → loja → produto → vitrine → checkout → e-mail no Mailcatcher) depende da infra de e2e do storefront (bloqueio `P5-SF-01`). Coberto por integração por ora. Origem: `P6-NOTIF-01`.
- [ ] **Compilar MJML no pipeline** — os `build/*.html` de pedido são autorais; rodar o CLI do mjml a partir de `src/*.mjml` p/ HTML de e-mail mais robusto (e padronizar com os demais templates). Origem: `P6-NOTIF-01`.
- [ ] **E-mails de status (enviado/entregue)** — só "pedido criado"/"novo pedido" nesta fase; e-mails de transição de status quando precisar. Origem: `P6-NOTIF-01`.
- [ ] **Branding no e-mail** (logo/cores da loja) — templates genéricos por ora. Origem: `P6-NOTIF-01`.
