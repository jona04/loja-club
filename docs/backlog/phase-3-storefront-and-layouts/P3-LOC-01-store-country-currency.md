---
id: P3-LOC-01
title: Localização da loja — país → moeda/locale/símbolo
phase: 3
etapa: "Etapa 7 — Localização da loja"
area: LOC
status: done
depends_on: []
blocks: [P3-TPL-01]
tests: [unit, integration]
---

# P3-LOC-01 — Localização da loja (país → moeda/locale/símbolo)

## Contexto
O preço é **global** — depende do **país da loja**. Hoje a `Store` carrega `currency` (ISO 4217) + `locale`, mas **setados manualmente / default da plataforma**; **não há `country`** nem derivação automática. E a vitrine **`formatPrice` hardcoda `pt-BR`**, então o **símbolo sai errado** pra loja não-BR (`USD` → `US$ 10,00` em vez de `$10.00`). Esta task faz a loja **escolher o país** e derivar **moeda + locale** (e o **símbolo**, derivável via `Intl`), de forma consistente entre backend, painel e vitrine.

## Docs de referência
- [07 — Database Strategy](../../07_database_strategy.md) (`store_stores`)
- [10 — Storefront & Layouts](../../10_storefront_and_layouts.md) (exibição de preço)
- `INV-D5` (dinheiro = minor units + ISO 4217) em [`_foundations`](../_foundations-and-bottlenecks.md)

## Escopo (o que ENTRA)
- **`country`** (ISO 3166-1 alpha-2) na `Store`.
- **Loja escolhe o país** (na criação e/ou em Configurações) → **`currency` (ISO 4217) + `locale`** preenchidos automaticamente.
- **Referência país → moeda (+ locale + símbolo)**: derivar de uma **lib** (ex.: `babel`/`pycountry`) — **não** manter 250 linhas à mão. Um **seed**/serviço expõe `country → {currency, locale, symbol}`.
- **Vitrine:** `formatPrice` usar o **locale da loja** (não `pt-BR` fixo) → símbolo certo por moeda/país (`R$` / `$` / `€` …).
- **Painel:** exibir a **moeda/símbolo** da loja onde houver preço (catálogo), e o seletor de país nas Configurações.

## Fora de escopo (o que NÃO entra)
- **Multi-moeda por loja** (uma loja = uma moeda) e **conversão de câmbio** → futuro.
- **i18n completo dos textos** da vitrine (strings) → `INV-G7` (follow-up de `P3-SF-02`).
- País do **cliente** no telefone do checkout (E.164, doc 23) — é coisa **distinta** (país do comprador, não da loja); não confundir.

## Arquivos a criar/alterar (provável)
- `backend/app/modules/stores/{models,schemas,services}.py` (alterar) — `country` + derivação na criação + migration.
- `backend/app/core/localization.py` (criar) — `localize_country` + **mapa curado** dos países suportados.
- `frontend-storefront/lib/api.ts` (alterar) — `formatPrice` usar o locale da loja (`locale` no `StorefrontStore`).
- `frontend-dashboard/.../Store/NoStores.tsx` (alterar) — seletor de país **obrigatório** no form de criar loja.
- `docs/07_database_strategy.md` (alterar) — `country` na `store_stores`.

## Passos
1. Helper `country → {currency, locale, symbol}` (lib) + testes.
2. `country` na `Store` + derivação no `create_store`/settings + migration.
3. Expor `locale` (e/ou símbolo) no contrato público do storefront; `formatPrice` passa a usar o locale da loja.
4. Painel: seletor de país; exibir moeda/símbolo.

## Testes
- **unit:** `country → {currency, locale, symbol}` (BR→BRL/pt-BR/R$; US→USD/en-US/$; PT→EUR/pt-PT/€).
- **integração:** criar loja com país → currency/locale corretos; preço público formatado no símbolo certo.

## Definition of Done
- [x] `Store.country` (ISO 3166-1, default `BR`); criar loja escolhendo país preenche `currency`/`locale` (`localize_country`).
- [x] Referência país→moeda(+locale+símbolo) = **mapa curado** dos países suportados (`app/core/localization.py`), sem tabela de 250 à mão.
- [x] Vitrine formata o preço no **símbolo certo por loja** (`formatPrice` usa o locale da loja — verificado: pt-BR/BRL=`R$`, en-US/USD=`$`).
- [x] Migration `5a9d5d61b771` (`alembic check` vazio) + a **loja existente atualizada** p/ BR/BRL/pt-BR. doc 07 não detalha as colunas da loja → sem mudança lá.
- [x] **Modos de falha mapeados:** país não suportado → **422 `country_not_supported`** (testado, unit + API).
- [x] Itens adiados varridos → Follow-ups + README.

## Notas / Reconciliações
- **O símbolo não precisa ser armazenado** — é derivado de `currency`+`locale` via `Intl.NumberFormat` (vitrine) / lib (backend). O que importa é o **país→moeda+locale**; o símbolo entra no helper por conveniência.
- **Bloqueia `P3-TPL-01`** no sentido de exibição: os templates devem formatar o preço com o **locale da loja** (não `pt-BR` fixo) — fechar este antes/junto da implementação dos templates.
- Os **prompts dos templates seguem com `R$`** (sample data) — a moeda real é resolvida na implementação por loja.
- Implementado com **mapa curado** (`app/core/localization.py`, ~15 países), não babel — mais previsível e sem dep nova; expandir/trocar por lib depois é trivial.
- `Store.country` tem default `BR` no model (Brazil-first); a **obrigatoriedade** é no `StoreCreate`/form (API). `PLATFORM_DEFAULT_CURRENCY`/`_LOCALE` (mortos) foram **removidos**.
- O seletor de país ficou no **form de criar loja** (`NoStores`, obrigatório, default BR); um seletor em **Configurações** pra *trocar* o país depois é follow-up.

## Follow-ups
- [ ] **Multi-moeda / câmbio** — *Quando:* se uma loja precisar vender em mais de uma moeda (não previsto no V1). → README.
