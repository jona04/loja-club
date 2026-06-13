---
id: P6-CUST-01
title: Identidade do cliente + deduplicação (guest)
phase: 6
etapa: "Etapa 3 — Módulo customers (identidade + dedup)"
area: CUST
status: done
depends_on: []
blocks: [P6-CHK-01, P6-CUST-02]
tests: [unit, integration]
---

# P6-CUST-01 — Identidade do cliente + deduplicação (guest)

## Contexto
Vender sem login exige saber "quem é quem" por **e-mail/telefone normalizados**, com deduplicação por loja e **primeiro-nome-vence**. É a base do checkout e do painel de clientes.

## Docs de referência
- [23 — Customer Identity and Guest Checkout](../../concepts/23_customer_identity_and_guest_checkout.md)
- [07 — Database](../../concepts/07_database_strategy.md)

## Escopo (o que ENTRA)
- Modelos (com `store_id`, soft delete): `customer_profiles` (e-mail normalizado, `phone_e164`, nome), `customer_addresses` (vários por customer), `customer_guest_sessions` (`guest_session_id` único, `expires_at`).
- Índices únicos: `store_id+email` (quando existir), `store_id+phone_e164` (quando existir), `guest_session_id` único, `store_id+expires_at`.
- Normalização: **e-mail** (trim + minúsculas; **não** remover ponto/`+tag`); **telefone → E.164** via `phonenumbers` (região do seletor de país ISO 3166 — sem `+55`/DDD hard-coded).
- **Serviço público** `create_or_update_customer(...)`: match por e-mail → senão `phone_e164` → senão cria; **primeiro-nome-vence**; preenche faltante só se não pertencer a outro; conflito (e-mail de um, telefone de outro) **vence o e-mail**; endereço novo → +1 (não duplica idêntico).
- **Guest session:** cookie HTTP-only `guest_session_id` (criar/recuperar/renovar; validade 30 dias).

## Fora de escopo (o que NÃO entra)
- Login por **código/senha/Google** + área do cliente + sincronização guest↔conta: **Fase 8**.
- Painel de clientes (UI): `P6-CUST-02`.
- `customer_consents` (LGPD): follow-up se não couber aqui.

## Arquivos a criar/alterar
- `backend/app/modules/customers/{models,enums,schemas,services,repositories,routes}.py` (criar).
- `backend/app/modules/customers/normalization.py` (criar) — utils e-mail/telefone.
- `backend/pyproject.toml` (alterar) — dep `phonenumbers`.
- migration alembic.

## Passos
1. Modelos + índices únicos + migration.
2. Utils de normalização (e-mail; telefone E.164 com região).
3. `create_or_update_customer` (dedup + primeiro-nome-vence + conflito + endereço).
4. Guest session (cookie HTTP-only + tabela).

## Testes
- **Níveis:** unit (normalização/dedup) + integração (serviço/guest).
- **Quando escrever:** antes (regras de dedup claras — estilo TDD).
- **Cobrir:** unit — e-mail/telefone normalizados; dedup match e-mail→phone→cria; primeiro-nome-vence; conflito vence e-mail. integração — endereço novo não duplica idêntico; cookie cria/recupera sessão; **isolamento por loja** (mesmo e-mail em 2 lojas = 2 customers).

## Definition of Done
- [x] Modelos + índices únicos (email/phone quando existirem) + migration (`alembic check` vazio).
- [x] Normalização de e-mail + telefone **E.164** (qualquer país via lib).
- [x] `create_or_update_customer` (dedup, primeiro-nome-vence, conflito) — **serviço público** reusável.
- [x] Guest session por cookie (30 dias).
- [x] **Modos de falha mapeados** (telefone inválido/sem região → 422; sem contato → 422; e-mail e telefone de customers diferentes → vence e-mail, sem roubar contato; cookie ausente/expirado → nova sessão) → tratados/Follow-ups.
- [x] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- `create_or_update_customer` exposto como **serviço de módulo** (não embutido na rota de checkout) — reusado pela **personalização assistida** (Fase 7) e pelo checkout (`P6-CHK-01`).
- **Implementação:** `customer_profiles`/`customer_addresses` (soft delete) + `customer_guest_sessions` (sem soft delete; expira por `expires_at`); índices parciais únicos `store_id+email`/`store_id+phone_e164` (quando `IS NOT NULL AND deleted_at IS NULL`) + `guest_session_id` único + `store_id+expires_at`. Normalização em `normalization.py` (e-mail trim+lower; telefone via `phonenumbers`→E.164, região do seletor). Dedup: match e-mail→phone→cria; preenche contato faltante só se livre (conflito vence e-mail, sem roubar). Cookie via dependency `customers/deps.py:guest_session` (httponly, samesite=lax, 30d). Dep nova: `phonenumbers`. Migration `6eeee8b19085`. 20 testes, módulo 100%.

## Follow-ups
- [ ] **`customer_consents` (LGPD)** — não incluído nesta task; quando precisar registrar consentimento (marketing/dados). Origem: `P6-CUST-01`.
- [ ] **Limpeza de guest sessions expiradas** — `expires_at` existe, mas não há worker que marque/limpe as expiradas (doc 23 pede marcar `expired`). Origem: `P6-CUST-01`.
- [ ] **Cookie `secure`/`domain` + Set-Cookie via SSR do storefront** — hoje o cookie é `httponly`+`samesite=lax` **sem `secure`** (dev http); em produção (https) precisa `secure=True`, decidir `domain` (subdomínio da loja) e garantir que o Next.js repasse o `Set-Cookie`. Tratar ao ligar no carrinho/checkout (`P6-CART-01`/`P6-SF-01`). Origem: `P6-CUST-01`.
