---
id: P6-NOTIF-01
title: E-mails de pedido (worker) + health + E2E do marco
phase: 6
etapa: "Etapa 7 — Notificações + finalização local"
area: NOTIF
status: todo
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
- [ ] E-mails "pedido criado" (cliente) + "novo pedido" (lojista) **no worker** (enqueue, com retry).
- [ ] Health checks `/health`/`/health/db`/`/health/redis`.
- [ ] **E2E do marco** verde (criar conta → … → pedido → painel) no Compose local.
- [ ] **Modos de falha mapeados** (worker/enqueue falho → pedido persiste, e-mail re-tenta; Mailcatcher fora) → tratados/Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- INV-F5: **todo e-mail é enfileirado** (nunca inline).

## Follow-ups
- [ ] — nenhum (preencher ao implementar).
