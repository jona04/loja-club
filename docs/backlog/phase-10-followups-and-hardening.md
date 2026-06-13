# Fase 10 — Follow-ups, débito técnico e revisão geral de segurança (dev online)

> Objetivo: **zerar os follow-ups e o débito técnico** acumulados nas fases anteriores e fazer uma **revisão geral de segurança** (+ os detalhes que faltam), deixando o sistema sólido **antes da produção** (Fase 11). É a fase de **consolidação** — não introduz produto novo, endurece o que existe.

Docs de referência: [14](../concepts/14_security_strategy.md), [15](../concepts/15_observability_and_operations.md), [07](../concepts/07_database_strategy.md), [13](../concepts/13_performance_cache_and_cdn.md), [19](../concepts/19_legal_and_compliance_todo.md), [16](../concepts/16_testing_strategy.md).

> **Entrada da fase:** as seções **"Follow-ups / débitos técnicos"** dos READMEs de cada fase (0–9) + as seções **Follow-ups** das tasks. Tudo que ficou `[ ]` aberto entra aqui (implementar ou decidir conscientemente), marcando `[x]` na **origem**.

## Definition of Done da fase
- **Nenhum follow-up aberto** sem destino: cada um virou implementação, decisão registrada, ou foi explicitamente descartado.
- Módulo `audit` no ar + hardening completo de segurança (além do mínimo da Fase 9).
- Revisão de **performance/cache/índices** e de **edge cases** conhecidos feita.

---

## Etapa 1 — Varredura de follow-ups & débito técnico

> Implementar/decidir os follow-ups das Fases 0–9. Exemplos conhecidos (não exaustivo — a fonte é o README de cada fase):
- [ ] **Vitrine — campo de cupom no checkout** (ligar os 3 checkouts ao `POST/DELETE /storefront/cart/coupon`) + **tela de Cupons no painel** (CRUD; backend pronto desde `P6-DISC-01`). Origem: Fase 6.
- [ ] **Corridas/idempotência:** `order_number` (retry/lock), limite de uso de cupom (atômico) + limite por cliente, upsert de estoque. Origem: Fase 6/2.
- [ ] **Limpeza por worker:** guest sessions e `checkout_sessions` expiradas/abandonadas (já têm `expires_at`). Origem: Fase 6.
- [ ] **N+1 / snapshots:** payload do carrinho (`to_public` busca por item); snapshot de preço stale. Origem: Fase 6.
- [ ] **LGPD:** `customer_consents` (consentimento) + `customers.export`/`customers.delete` (exportar/anonimizar). Origem: Fase 6.
- [ ] **Storefront:** `next/image` + `INTERNAL_API_URL` (separar do `NEXT_PUBLIC_API_URL`) + `app/error.tsx` (erro amigável). Origem: Fase 3.
- [ ] **Permissões órfãs:** `shipping.private_delivery.update` (resolvida na Fase 8 Etapa 5) e `layout.preview` — varrer e limpar/usar. Origem: Fase 1/5/6.
- [ ] **MJML no pipeline** (compilar `src/*.mjml` → `build/*.html`) + e-mails de status (enviado/entregue) + branding. Origem: Fase 6.
- [ ] **Recap completo na confirmação** (breakdown/dados do cliente por template). Origem: Fase 6.
- [ ] **Demais itens** das seções "Follow-ups" — varrer todos os READMEs e fechar.

## Etapa 2 — Módulo `audit` (auditoria de negócio)

Doc [14](../concepts/14_security_strategy.md), [15](../concepts/15_observability_and_operations.md), [07](../concepts/07_database_strategy.md).
- [ ] `audit_logs` (ações críticas), `account_login_events` (logins/falhas), `audit_security_events`. Índices `store_id+created_at`, `user_id+created_at`.
- [ ] Registrar ações sensíveis (doc [08](../concepts/08_modules_and_permissions.md)/[14](../concepts/14_security_strategy.md)): alterar plano/conta de pagamento/domínio/permissão, convidar/remover usuário, cancelar/reembolsar pedido, bloquear loja, acesso de suporte, acesso a arte do cliente, alteração de preço/modelo 3D.

## Etapa 3 — Hardening completo de segurança

> Além do **mínimo** que subiu na Fase 9. Doc [14](../concepts/14_security_strategy.md).
- [ ] **Restore testado** dos backups do RDS (plano de recuperação executado de verdade).
- [ ] **Uploads/arte privada** endurecidos: validação + URLs assinadas + separação por `store_id` revisadas.
- [ ] **CSP completa** + revisão de headers; **CORS** revisado.
- [ ] **Retenção de logs** (app 14–30 dias; auditoria por mais tempo).
- [ ] **Revisão de permissões** end-to-end (backend é a fonte da verdade; UI só gating) + varredura de status/flags "enfeite" (todo status é lido em código).
- [ ] Revisão de **segredos**, rate limits e validação de webhook consolidadas.

## Etapa 4 — Revisão geral (performance, dados, UX)

Doc [13](../concepts/13_performance_cache_and_cdn.md), [07](../concepts/07_database_strategy.md).
- [ ] Revisão de **cache** (chaves/invalidão) e **índices** (consultas quentes).
- [ ] Revisão de **edge cases** conhecidos e de **acessibilidade/i18n** pendentes.

---

## Testes (doc [16](../concepts/16_testing_strategy.md))
- [ ] **Auditoria:** ações sensíveis geram entrada; isolamento por loja/usuário.
- [ ] **Segurança:** rate limit; URL assinada para arquivo privado; permissão validada no backend; restore executado.
- [ ] **Regressão:** a varredura de follow-ups não quebrou nada (suítes verdes).

---

## Reconciliações
- Vinda da **Fase 9**: módulo `audit` + hardening completo + retenção + restore testado migraram pra cá (a Fase 9 sobe só o mínimo).
