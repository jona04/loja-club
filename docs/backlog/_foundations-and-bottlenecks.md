# Fundações & Gargalos

> **Não é uma fase.** É um doc de **referência cross-fase**: invariantes e decisões que a base precisa honrar, e os **gargalos** que, se ignorados, causam retrabalho caro. Cada item aponta **em qual fase/task** é implementado. Lido junto, dá a visão de sistema para ajustar a base cedo.

> **Sequência de fases:** **3D/personalização = [Fase 5 — Produtos 3D](./phase-5-3d-products.md)** (lojista gera os modelos via API de terceiros; sem catálogo da plataforma) e **planos + pagamentos = Fase 6**. Os invariantes de personalização (congelar arte no pedido — INV-P5; arte privada — INV-S2) e de pagamento valem **a partir da fase** correspondente.

Relaciona-se com: [03](../03_system_architecture.md), [06](../06_multitenancy_and_domains.md), [07](../07_database_strategy.md), [08](../08_modules_and_permissions.md), [11](../11_checkout_payments_and_split.md), [13](../13_performance_cache_and_cdn.md), [14](../14_security_strategy.md), [20](../20_api_contracts_todo.md), [23](../23_customer_identity_and_guest_checkout.md).

## Como usar
- **Invariante** = regra que todo código deve seguir (não negociável).
- **Decisão** = escolha técnica travada aqui (com recomendação + status).
- **Gargalo** = risco antecipado + mitigação + onde é tratado.
- O **mapa no fim** liga cada fundação à fase/task que a implementa.

---

## 1. Global / i18n (nada assume Brasil)

- **INV-G1 — Dinheiro é sempre `(valor + moeda)`.** Valor em **unidades menores** + **moeda ISO 4217**; expoente por moeda (não fixo em 2). Nunca número solto. → `P0-MOD-05`.
- **INV-G2 — Soma/compara só entre a mesma moeda.** Operação entre moedas diferentes é erro. → `P0-MOD-05`.
- **INV-G3 — `currency` e `locale` por loja e por cliente**, com fallback no default da plataforma. → loja (Fase 1), cliente (Fase 4), defaults (`P0-CFG-02`).
- **INV-G4 — Telefone em E.164 para qualquer país**, via lib (libphonenumber/`phonenumbers`); país vem do seletor → código de discagem. Sem `+55`/DDD hard-coded. → convenção no [doc 23](../23_customer_identity_and_guest_checkout.md); util na Fase 4.
- **INV-G5 — Endereço país-aware** (ISO 3166-1; campos flexíveis; sem CEP/UF fixos). → modelo (Fase 4).
- **INV-G6 — Timestamps em UTC** no banco; formatação por locale/timezone só no frontend. → template já faz; confirmado em `P0-MOD-05`.
- **INV-G7 — Storefront e e-mails i18n-ready** (textos parametrizáveis por locale). → storefront (Fase 3), e-mails (Fase 4).

## 2. Multi-tenancy (isolamento)

- **INV-T1 — Toda entidade comercial tem `store_id`** e toda query comercial filtra por ele. → mixin `StoreScopedMixin` (`P0-MOD-01`).
- **INV-T2 — Nunca buscar recurso comercial só por id.** Sempre `store_id + id` (ou `store_id + slug`). → guard central (Fase 1).
- **INV-T3 — Guard central de tenant** (dependency + base de repositório), não filtro manual espalhado. → Fase 1 (`tenancy`).
- **INV-T4 — Loja pública resolvida pelo `Host`**, com cache `domain:{host}`. → Fase 1 (`domains`/`tenancy`), consumo Fase 3.
- **GARGALO:** vazamento entre lojas é o pior bug possível. Mitigação: guard central + testes de isolamento em toda fase (doc [16](../16_testing_strategy.md)).

## 3. Identidade & autenticação

- **INV-I1 — Três identidades separadas:** admin de plataforma e lojista/equipe em `account_users`; cliente final em `customer_profiles`. → Fase 0 (accounts), Fase 4 (customers).
- **INV-I2 — Auth do cliente é um sistema separado** do `account_users` (token por loja; código/senha/Google). Projetar `accounts` sem acoplar a auth do cliente. → desenho em Fase 0 (`P0-MOD-04`), implementação Fase 6.
- **INV-I3 — Dedup do customer por loja** = e-mail normalizado e telefone E.164, match priorizando e-mail; primeiro-nome-vence. → Fase 4.
- **INV-I4 — Compra sem login** via `guest_session_id` (cookie HTTP-only). → Fase 4.

## 4. Dados & persistência

- **INV-D1 — PK = UUID** (padrão do template). → `P0-MOD-01`.
- **INV-D2 — Soft delete** em registros de negócio (`deleted_at`/`deleted_by_user_id`/`delete_reason`); nunca hard delete. → `P0-MOD-01`.
- **INV-D3 — Prefixo de domínio nas tabelas** (`account_users`, `store_stores`, `catalog_products`…). → cada módulo.
- **INV-D4 — Colunas de dinheiro padronizadas** (`*_amount_minor` + `*_currency`). → `P0-MOD-05`.
- **INV-D5 — Índices compostos com `store_id`** desde a criação da feature (lista no doc [07](../07_database_strategy.md)). → cada módulo.
- **INV-D6 — Migrations com disciplina** (Alembic; rodar em dev antes; sem alteração manual em prod). → todas as fases; CD na Fase 7.
- **GARGALO:** queries sem índice `store_id+…` derrubam a vitrine. Mitigação: índices junto da feature + revisão (doc [13](../13_performance_cache_and_cdn.md)).

## 5. Convenções de API

- **INV-A1 — Versionada** sob `/api/v1`. Painel sob `/stores/{store_id}/…`; storefront público resolve por `Host`. → Fase 1.
- **DEC-A2 — Padrão de paginação/erro/response** unificado. **Travado em `P1-API-01`:** lista = `{data, count}` (offset `skip`/`limit`); erro = `{error: {code, message, details?}}`. Documentado no doc [20](../20_api_contracts_todo.md). → Fase 1.
- **INV-A3 — Idempotency-Key** em operações sensíveis (criar pedido/pagamento) além da idempotência de webhook. → Fase 4/5.
- **INV-A4 — Autorização sempre no backend** (frontend esconder botão não é segurança). → Fase 1+.
- **GARGALO:** padronizar resposta/erro depois que há 10 endpoints = retrabalho em todos. Mitigação: fixar em Fase 1.

## 6. Assíncrono & abstrações de infra

- **INV-F1 — Abstração de fila** (`app/core/queue.py` `enqueue()`); domínio não conhece a lib. → `P0-CFG-04`.
- **INV-F2 — Abstração de storage** (`app/core/storage.py`): S3 + CloudFront reais (boto3) desde o dev local; URLs assinadas para privados. → Fase 2 (`media`).
- **INV-F3 — Cache no Redis com chaves padronizadas** e **invalidação centralizada** (doc [13](../13_performance_cache_and_cdn.md)). → `P0-CFG-03` + Fases 1/3.
- **INV-F4 — Notificações por canal abstrato** (e-mail agora; SMS/WhatsApp na Fase 6) atrás de uma interface. → Fase 4 (e-mail), Fase 6 (SMS/WhatsApp).
- **GARGALO:** acoplar direto a um SDK (fila/storage/gateway) trava troca de provedor. Mitigação: interfaces finas desde já.

## 7. Pagamentos & split

- **INV-P1 — Abstração de provedor de pagamento** (não assumir um único gateway BR; permitir multi-região, ex.: Stripe internacional). → Fase 6.
- **INV-P2 — Confirmação só por webhook** assinado + **idempotente** (tabela `payment_webhooks`, `gateway_event_id` único). → Fase 6.
- **INV-P3 — Nunca armazenar cartão**; dados sensíveis no gateway. → Fase 6.
- **INV-P4 — Split usa a comissão do plano**; Loja Club não retém dinheiro. → Fase 6 (billing/payments).
- **INV-P5 — Personalização aprovada é congelada no pedido** (cópia própria), independente da sessão viva. → Fase 4.

## 8. Segurança & privacidade

- **INV-S1 — Permissão por loja no backend** (membership + papel; + plano na Fase 6). → Fase 1, gating de plano Fase 6.
- **INV-S2 — Arte do cliente é privada** (URLs assinadas, separada por `store_id`). → Fase 2/4.
- **INV-S3 — Segredos fora do código** (env seguro/SSM). → todas; reforço Fase 7.
- **INV-S4 — LGPD/consentimento + minimização**; `customer_consents`. → Fase 4.
- **INV-S5 — Rate limit** em login/recuperação/checkout/códigos/APIs públicas. → baseline Fase 4, completo Fase 7.

## 9. Frontends

- **INV-FE1 — Três projetos separados:** `frontend-dashboard` (`app.`), `frontend-admin` (`admin.`), `frontend-storefront` (Next.js, `*.`). → Fases 1/3/6.
- **INV-FE2 — Cliente OpenAPI gerado e compartilhado**; regenerar quando a API muda. → todas que mexem em API.
- **INV-FE3 — URL da API por env** (sem hardcode). → todas.

## 10. Testes

**Princípio — INV-TEST-1:** testar **comportamento e intenção**, não implementação. Teste pelo **contrato público** (entradas → saídas/efeitos observáveis); assim resiste a refactor. O nome do teste expressa a intenção. **Mock só nas fronteiras reais** (rede, I/O, relógio, aleatoriedade, S3, gateway, e-mail).

**Pirâmide:** muitos **unit**, alguns **integração**, poucos **E2E**. Duas regras de bolso:
- *empurre o teste pro nível mais barato que ainda pega o bug;*
- *não mocke o que você precisa testar de verdade* (mockar o DB pra "testar uma query" não prova nada → vira integração).

**Quando cada nível (INV-TEST-2):**

| Situação | Nível |
|---|---|
| Lógica pura/determinística com ramos (cálculo, validação, normalização, invariante) | **unit** (exaustivo) |
| Correção depende de fronteira real (query filtra `store_id`, migration, permissão na rota, constraint único, idempotência) | **integração** (no seam) |
| Lógica rica **E** fronteira crítica | **os dois** (unit cobre os ramos + 1 integração no caminho feliz) |
| Jornada cross-sistema com valor de negócio | **E2E** (poucos) |

Não duplicar cobertura de ramos no nível de cima.

**Smoke test (esclarecimento):** é **automatizado**, raso e rápido — verifica que o sistema **sobe e os caminhos críticos não quebram** (app inicia, `/health` responde, OpenAPI carrega, home retorna 200). Roda cedo para pegar quebra grosseira; é um subconjunto raso de integração/E2E. **Não é teste manual.** Quando uma task não tem teste automatizado, dizemos *verificação manual* (humano conferindo) — que é outra coisa.

**Isolamento multi-tenant** (item nº1 do doc [16](../16_testing_strategy.md)) é majoritariamente **integração** (duas lojas no DB real → assert de "A não vê B"), sempre no **resultado observável** (403/404/ausência de dado), nunca no SQL interno.

**Ferramentas:**
- Backend: `pytest` com `tests/unit` e `tests/integration`; **isolamento por teste** (transação + rollback); `coverage` + `mypy strict`.
- Frontend: **`vitest` + Testing Library** (unit/componente, foco em comportamento) + **Playwright** (E2E).
- Mocks: **S3 via `moto`/botocore stubber**, gateway/e-mail/relógio/random nas fronteiras.
- **Serviço externo real (S3/CloudFront/gateway):** além do **mock no CI**, um **smoke real env-gated** (roda com credenciais em local/dev; **pulado** sem secrets) prova que **provisionamento + credenciais funcionam de fato**. A task que depende do serviço **provisiona + verifica** (não assume que "alguém configurou"). → AWS na **Fase 2** (`P2-MEDIA-01`); gateway na **Fase 6**.

**Onde:** fundação de testes em `P0-TEST-01`; unit de lógica pura junto de onde a lógica nasce (Money em `P0-MOD-05`; dedup/telefone na Fase 4; split na Fase 6); **fixtures/factories multi-tenant + testes de isolamento na Fase 1** (precisam de `Store`).

---

## Decisões a travar

| ID | Decisão | Recomendação | Status |
|---|---|---|---|
| DEC-1 | Representação de dinheiro | inteiro em unidades menores + moeda ISO 4217 (estilo Stripe); `Money` próprio + `babel` p/ expoente/format (não `py-moneyed`, que é Decimal) | **decidido** (alt.: Decimal+moeda) |
| DEC-2 | Arredondamento monetário | `ROUND_HALF_UP`; rateio de split por maior-resto | recomendado, confirmar antes da Fase 6 |
| DEC-3 | Lib de fila | `arq` (async, Redis) | recomendado (`P0-CFG-04`) |
| DEC-4 | Lib de telefone | `phonenumbers` (libphonenumber) | recomendado (Fase 4) |
| DEC-5 | Paginação | **offset (`skip`/`limit`) + envelope `{data, count}`** | **decidido** (`P1-API-01`) |
| DEC-6 | Gateway(s) de pagamento | abstrair; escolher BR (Pagar.me/MercadoPago/Asaas) + plano p/ internacional | **pendente** (Fase 6, doc [18](../18_open_decisions.md)) |
| DEC-7 | Provedor SMS/WhatsApp | a definir | **pendente** (Fase 6) |
| DEC-8 | Storage local em dev | AWS S3 + CloudFront reais (sem MinIO) | **decidido** (Fase 2) |
| DEC-9 | Runner de unit no frontend | `vitest` + Testing Library | **decidido** (`P0-TEST-01`) |
| DEC-10 | Isolamento de DB em teste | transação por teste (rollback/savepoint) | recomendado (`P0-TEST-01`) |
| DEC-11 | Mock de AWS S3 em teste | `moto` (ou botocore Stubber) | recomendado (`P0-TEST-01`) |
| DEC-12 | Lib de teste backend | `pytest` (+ `coverage`, já no template) | **decidido** |
| DEC-13 | Docstrings Python | **Google style, em inglês**, em toda classe/método; enforce Ruff `D` | **decidido** (`CLAUDE.md`, `P0-CI-01`) |

## Gargalos antecipados (resumo)

1. **Retrofit de multi-moeda** → mitigado por `P0-MOD-05` (dinheiro global desde já).
2. **Vazamento entre lojas** → guard central de `store_id` (Fase 1) + testes de isolamento.
3. **Auth do cliente acoplada à do staff** → desenho separado desde a Fase 0.
4. **Lock-in de gateway/storage/fila** → interfaces finas (`queue`, `storage`, `payments`).
5. **Padrão de API tardio** → travar paginação/erro/response na Fase 1.
6. **Idempotência de webhook/pedido** → tabela + Idempotency-Key.
7. **Cache da vitrine inconsistente** → chaves + invalidação centralizadas.
8. **Divergência do client OpenAPI entre 3 frontends** → geração compartilhada.
9. **Congelar personalização no pedido** → cópia própria, não depender da sessão.
10. **Privacidade da arte do cliente** → URLs assinadas, escopo por `store_id`.
11. **Suíte sem isolamento** (estado vaza entre testes, ordem importa) → rollback por teste (`P0-TEST-01`).

## Mapa item → fase/task

| Fundação | Fase / task |
|---|---|
| Money/Currency/locale/UTC | Fase 0 — `P0-MOD-05` |
| Mixins (UUID/timestamps/soft delete/store_id) | Fase 0 — `P0-MOD-01` |
| Abstração de fila | Fase 0 — `P0-CFG-04` |
| Cache Redis | Fase 0 — `P0-CFG-03` |
| Auth do cliente separada (desenho) | Fase 0 — `P0-MOD-04` → Fase 6 |
| Guard de `store_id` / tenancy | Fase 1 |
| Padrão de API (paginação/erro/response) | Fase 1 |
| `currency`/`locale` na loja | Fase 1 |
| Abstração de storage + URLs assinadas | Fase 2 |
| Telefone E.164 / endereço país-aware / dedup | Fase 4 |
| Congelar personalização no pedido | Fase 4 |
| Idempotência de webhook + abstração de gateway | Fase 6 |
| SMS/WhatsApp | Fase 6 |
| Fundação de testes (layout, isolamento, mocks, vitest) | Fase 0 — `P0-TEST-01` |
| Fixtures/factories multi-tenant + testes de isolamento | Fase 1 |
| Auditoria, rate limit completo, segredos, backups | Fase 7 |
