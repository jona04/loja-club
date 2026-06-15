# Fase 13 — Kriar Pay multi-provider + Mercado Pago

> Objetivo: evoluir o `payments` depois do Kriar Pay Nativo, mantendo **Asaas BaaS** como provider nativo e adicionando **Mercado Pago** como provider conectado via OAuth. A fase endurece a UX, os contratos e a operação para lojas com providers diferentes sem duplicar checkout, pedidos ou painel.

Docs de referência: [11](../concepts/11_checkout_payments_and_split.md), [09](../concepts/09_merchant_dashboard.md), [02](../concepts/02_business_model_and_rules.md), [07](../concepts/07_database_strategy.md), [08](../concepts/08_modules_and_permissions.md), [14](../concepts/14_security_strategy.md), [18](../concepts/18_open_decisions.md), [20](../concepts/20_api_contracts_todo.md), [17](../concepts/17_v1_roadmap.md), [16](../concepts/16_testing_strategy.md).

> **Entrada da fase:** a Fase 8 já tem `payments` multi-provider no desenho, mas só implementa `asaas_baas`. Esta fase implementa o provider `mercado_pago` e revisa a convivência de providers em produção.

## Definition of Done da fase
- Uma loja pode usar `asaas_baas` ou `mercado_pago` como provider ativo sem mudar carrinho, checkout, pedido ou billing.
- Mercado Pago conecta por OAuth, com armazenamento seguro de tokens e renovação quando aplicável.
- O painel **Pagamentos / Kriar Pay** renderiza blocos por `capabilities`, mostrando gestão nativa no Asaas BaaS e caminho externo quando o Mercado Pago exigir.
- Webhooks, reembolsos, chargebacks, relatórios e comissões preservam o provider usado em cada transação.
- Trocar provider ativo segue regra segura, sem reescrever histórico nem quebrar transações pendentes.

---

## Etapa 1 — Endurecer abstração multi-provider

Doc [11](../concepts/11_checkout_payments_and_split.md), [07](../concepts/07_database_strategy.md), [20](../concepts/20_api_contracts_todo.md).

### Provider registry e capabilities
- [ ] Revisar a interface `PaymentProvider` criada na Fase 8: criar/conectar conta, status, criar pagamento, reembolso, parse de webhook, capabilities.
- [ ] Garantir que o checkout chama apenas a abstração, nunca SDK específico de Asaas/Mercado Pago.
- [ ] Persistir `provider`, `mode`, `provider_account_id`, `capabilities`, `external_dashboard_url` e referência segura para credenciais em `payment_accounts`.
- [ ] Preservar `provider` em transações, webhooks, chargebacks e comissões.

### Regras de troca de provider
- [ ] Permitir apenas **um provider ativo por loja** no checkout.
- [ ] Bloquear troca de provider quando houver pagamento pendente, disputa aberta ou webhook crítico sem processar.
- [ ] Manter histórico financeiro no provider original; não migrar transações antigas.

---

## Etapa 2 — Mercado Pago como conta conectada

Doc [11](../concepts/11_checkout_payments_and_split.md), [18](../concepts/18_open_decisions.md), [14](../concepts/14_security_strategy.md).

### OAuth e conta conectada
- [ ] Implementar conexão OAuth do lojista com Mercado Pago.
- [ ] Guardar access/refresh tokens por referência segura, não em `metadata`.
- [ ] Renovar token quando aplicável e refletir status `active|blocked|rejected` em `payment_accounts`.
- [ ] Mapear capabilities do Mercado Pago, incluindo `requires_oauth_connection=true` e `needs_external_dashboard=true` quando uma ação depender do painel externo.

### Pagamentos e comissão
- [ ] Criar pagamento usando as credenciais do vendedor conectado.
- [ ] Aplicar comissão da Kriar pelo campo de fee suportado pelo checkout escolhido.
- [ ] Mapear status do Mercado Pago para os status internos (`created|pending|authorized|paid|refused|canceled|refunded|chargeback`).
- [ ] Tratar Pix, cartão e boleto conforme disponibilidade do checkout escolhido.

---

## Etapa 3 — UX unificada de Kriar Pay

Doc [09](../concepts/09_merchant_dashboard.md), [05](../concepts/05_frontend_architecture.md).

### Painel do lojista
- [ ] Manter uma única área **Pagamentos / Kriar Pay**.
- [ ] Exibir "Kriar Pay Nativo" para `asaas_baas` e "Kriar Pay via Mercado Pago" para `mercado_pago`.
- [ ] Renderizar saldo, repasses, métodos, disputas e reembolsos conforme `capabilities`.
- [ ] Exibir ação "Abrir Mercado Pago" quando `needs_external_dashboard=true`.
- [ ] Evitar prometer gestão completa dentro da Kriar para providers conectados que não exponham todos os dados por API.

### Storefront e checkout
- [ ] Checkout usa o provider ativo sem expor complexidade ao cliente final.
- [ ] Mensagens de erro devem ser normalizadas em linguagem da Kriar, preservando detalhes técnicos em logs.

---

## Etapa 4 — Operação e admin da plataforma

Doc [14](../concepts/14_security_strategy.md), [15](../concepts/15_observability_and_operations.md), [09](../concepts/09_merchant_dashboard.md).

### Admin Kriar
- [ ] Ver provider ativo por loja, status, capabilities e últimos erros.
- [ ] Listar webhooks por provider e reprocessar eventos internos com segurança.
- [ ] Auditar conexão/desconexão/troca de provider.
- [ ] Alertar lojas com token expirado, conta bloqueada ou provider indisponível.

### Observabilidade
- [ ] Métricas por provider: sucesso/recusa, latência, falhas de webhook, reembolso e chargeback.
- [ ] Logs estruturados com `provider`, `store_id`, `order_id` e `gateway_event_id` quando aplicável; idempotência usa `provider + gateway_event_id`.

---

## Etapa 5 — Migração e coexistência

Doc [07](../concepts/07_database_strategy.md), [11](../concepts/11_checkout_payments_and_split.md), [16](../concepts/16_testing_strategy.md).

- [ ] Backfill seguro para lojas existentes em `asaas_baas`.
- [ ] Feature flag para liberar Mercado Pago por loja/plano.
- [ ] Fluxo de rollback: desativar Mercado Pago sem afetar lojas em Asaas BaaS.
- [ ] Documentar suporte: quando pedir ao lojista para acessar painel externo do Mercado Pago.

---

## Testes (doc [16](../concepts/16_testing_strategy.md))
- [ ] Provider registry escolhe provider por loja e isola credenciais.
- [ ] Loja A em Asaas BaaS e Loja B em Mercado Pago vendem sem misturar transações/webhooks.
- [ ] OAuth Mercado Pago: conectar, renovar, falhar e reconectar.
- [ ] Comissão da Kriar aplicada corretamente em Asaas BaaS e Mercado Pago.
- [ ] Troca de provider bloqueia quando há pendência crítica.
- [ ] Frontend renderiza blocos por `capabilities`.
- [ ] Webhook duplicado/idempotente por provider.

---

## Fora de escopo
- Wallet interna da Kriar.
- Reter saldo do lojista.
- Fazer a Kriar virar vendedora oficial do produto.
- Carrinho com múltiplos vendedores/providers no mesmo pedido.
- Implementar Pagar.me nesta fase.

## Reconciliações
- A Fase 8 implementa **Asaas BaaS como Kriar Pay Nativo** e deixa Mercado Pago fora do escopo. Esta fase adiciona Mercado Pago mantendo a abstração de provider definida no doc [11](../concepts/11_checkout_payments_and_split.md).
