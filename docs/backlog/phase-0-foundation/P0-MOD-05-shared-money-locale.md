---
id: P0-MOD-05
title: Tipos compartilhados globais (Money/Currency, locale, UTC)
phase: 0
etapa: "Etapa 2 — Refatoração modular"
area: MOD
status: done
depends_on: [P0-MOD-01]
blocks: []
tests: [unit]
---

# P0-MOD-05 — Tipos compartilhados globais (Money/Currency, locale, UTC)

## Contexto
A Kriar terá clientes **internacionais**. A base não pode assumir Brasil/Real/2 casas decimais. Como preço aparece já no catálogo (Fase 2) e cascateia para carrinho, pedido, split e billing, o **tipo de dinheiro global** precisa nascer na fundação, antes de qualquer modelo com valor monetário.

## Docs de referência
- [07 — Database Strategy](../../concepts/07_database_strategy.md)
- [02 — Business Model and Rules](../../concepts/02_business_model_and_rules.md) (comissão/split)
- [11 — Checkout, Payments and Split](../../concepts/11_checkout_payments_and_split.md)
- [Fundações & Gargalos](../_foundations-and-bottlenecks.md) — DEC-1, DEC-2, INV-G1..G6

## Escopo (o que ENTRA)
- `app/core/money.py`: representação de dinheiro = **valor inteiro em unidades menores + código de moeda ISO 4217** (ex.: `Money(amount_minor=1990, currency="USD")` = US$ 19,90).
  - registro de **expoente por moeda** (BRL/USD/EUR = 2, JPY = 0, etc.) via **`babel`** (`get_currency_precision`), em vez de tabela manual.
  - operações seguras: **soma/subtração só entre a mesma moeda** (erro explícito caso contrário); multiplicação por escalar (qty) e por taxa (%) com regra de **arredondamento** definida.
- Convenção de coluna para dinheiro em SQLModel: par `*_amount_minor: int` + `*_currency: str(3)` (ou um type composto), aplicado por todos os módulos que guardam valor.
- Referência **ISO 4217 (moedas)** e **ISO 3166-1 (países)** disponível para seletores/validação.
- Confirmar/registrar como regra: **timestamps sempre em UTC** (template já usa `DateTime(timezone=True)`); formatação por locale é no frontend.
- Convenção de `currency` e `locale` que **loja** e **cliente** vão carregar (campos criados nas fases respectivas — Fase 1/6), com fallback nos defaults da plataforma (`P0-CFG-02`).

## Fora de escopo (o que NÃO entra)
- Conversão multi-moeda / câmbio em tempo real → pós-V1.
- i18n completo das UIs → frontends, fases respectivas.
- Imposto/fiscal → responsabilidade do lojista (doc 02), fora da V1.
- Modelo de endereço país-aware em si → Fase 6 (`customers`); aqui só fica a convenção/ISO 3166.
- Normalização de telefone E.164 → Fase 6 (`customers`); aqui só registramos a convenção global.

## Arquivos a criar/alterar
- `backend/app/core/money.py` (criar) — `Money` + helpers + arredondamento.
- `backend/pyproject.toml` (alterar) — `babel` (expoente/format de moeda e locale).
- `backend/app/db/base.py` (alterar) — convenção/type de coluna para dinheiro (reaproveita `P0-MOD-01`).

## Passos
1. Adicionar `babel` e implementar um `Money` próprio (valor inteiro em unidades menores + moeda).
2. Implementar `Money` (valor em unidades menores + moeda) com guard de mesma-moeda e arredondamento.
3. Definir a convenção de colunas de dinheiro e expor em `app/db/base.py`.
4. Disponibilizar a referência ISO 4217/3166 para selects/validação.
5. Testes: soma de moedas diferentes falha; formatação correta para 2 casas (USD/BRL) e 0 casas (JPY); cálculo de comissão (%) arredonda como definido.

## Testes
> Fundações §10. Lógica pura — vitrine de unit test; segue o layout de `P0-TEST-01`.

- **Níveis:** unit (exaustivo).
- **Quando:** antes/durante (TDD — contrato claro).
- **Cobrir:**
  - unit — soma rejeita moedas diferentes; formatação correta com 0 e 2 casas (JPY/BRL/USD); arredondamento `ROUND_HALF_UP`; cálculo de comissão (%).

## Definition of Done
- [x] Tipo `Money` (valor + moeda ISO 4217); nenhum valor monetário é número solto.
- [x] Soma entre moedas diferentes falha (`CurrencyMismatchError`).
- [x] Formata 0/2/3 casas via babel (testado USD/JPY/BHD; sem assumir 2/BRL).
- [x] Convenção de colunas (`*_amount_minor: int` + `*_currency: str(3)`) documentada em `money.py` para o catálogo (Fase 2).

## Notas / Reconciliações
- **DEC-1 (Fundações) — decidido:** inteiro em unidades menores + moeda ISO 4217 (estilo Stripe). `Money` é um value object próprio; `babel` fornece expoente e formatação. **Não usar `py-moneyed`** (baseado em `Decimal`, conflita com unidades menores). Alternativa histórica considerada: `Decimal` + moeda.
- **DEC-2 (Fundações):** arredondamento recomendado `ROUND_HALF_UP`; rateio de split por maior-resto. Confirmar antes do split (Fase 8).
- **Implementado:** `app/core/money.py` (`Money`: `+`, `-`, `*int`, `apply_rate(Decimal)` half-up, `decimal_amount`, `format(locale)`) + `CurrencyMismatchError`; `babel` para expoente/format. 14 testes unit verdes; gate `app` verde.
- **Reconciliação:** não editei `base.py` — dinheiro não cabe como mixin (um modelo pode ter vários valores monetários: preço, total…). A convenção de colunas vive no docstring de `money.py`; sem type composto no MVP.
- **Refino do harness (P0-TEST-01):** movi os fixtures de DB para `tests/integration/conftest.py`, então `tests/unit` roda **sem DB** (14 testes em 0,55s). Os testes do Money provaram isso.
