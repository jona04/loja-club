---
id: P6-SHIP-02
title: Frete completo — zonas/tarifas/regras (fast-follow)
phase: 6
etapa: "Etapa 1 — Módulo shipping (frete)"
area: SHIP
status: todo
depends_on: [P6-SHIP-01]
blocks: []
tests: [integration]
---

# P6-SHIP-02 — Frete completo: zonas/tarifas/regras (fast-follow)

## Contexto
**Fast-follow** do `P6-SHIP-01`: além dos métodos MVP, frete por **região** (cidade/estado) com zonas e tarifas.

## Docs de referência
- [07 — Database](../../concepts/07_database_strategy.md)
- [11 — Entrega combinada](../../concepts/11_checkout_payments_and_split.md)
- [09 — Frete](../../concepts/09_merchant_dashboard.md)

## Escopo (o que ENTRA)
- `shipping_zones`, `shipping_rates`, `shipping_method_rules` (cidade/região/estado, com `store_id`).
- CRUD no painel + cálculo do frete no checkout por região (inclui limitar `private_delivery` por cidade/região/estado).

## Fora de escopo (o que NÃO entra)
- Integração com transportadora / cálculo via API externa: pós-V1.

## Arquivos a criar/alterar
- `backend/app/modules/shipping/{models,schemas,services,routes}.py` (alterar).
- migration alembic.

## Passos
1. Modelos de zona/tarifa/regra + migration.
2. CRUD + cálculo por região no checkout.

## Testes
- **Níveis:** integração.
- **Cobrir:** tarifa por região aplicada no checkout; `private_delivery` limitada por região; isolamento por loja.

## Definition of Done
- [ ] Zonas/tarifas/regras + migration (`alembic check` vazio).
- [ ] Cálculo por região no checkout.
- [ ] **Modos de falha mapeados** (região sem tarifa; endereço fora de cobertura) → tratados/Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- (preencher ao implementar.)

## Follow-ups
- [ ] — nenhum (preencher ao implementar).
