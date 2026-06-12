---
id: P6-SF-02
title: Seleção de variação na vitrine (fast-follow)
phase: 6
etapa: "Etapa 4 — Frontend storefront"
area: SF
status: todo
depends_on: [P6-CART-01]
blocks: []
tests: [integration, e2e]
---

# P6-SF-02 — Seleção de variação na vitrine (fast-follow)

## Contexto
**Fast-follow:** o núcleo vende produto `image` simples. Quando a loja tiver variações (tamanho/cor), a vitrine precisa expor variações + disponibilidade e capturar a variação escolhida no carrinho. Adianta o follow-up de produto da Fase 3.

## Docs de referência
- [10 — Página de produto](../../concepts/10_storefront_and_layouts.md)
- [07 — Database](../../concepts/07_database_strategy.md)

## Escopo (o que ENTRA)
- `StorefrontProduct` passa a trazer **variações + estoque** (hoje só imagem/nome/preço/descrição).
- Página de produto: **escolher a variação** (e ver disponibilidade); o `cart_item` guarda o `variant_id` selecionado (o backend já aceita desde `P6-CART-01`).

## Fora de escopo (o que NÃO entra)
- Produtos relacionados: follow-up.

## Arquivos a criar/alterar
- `backend/app/modules/storefront/{schemas,services}.py` (alterar) — expor variações/estoque.
- `frontend-storefront/templates/*/` (alterar) — seletor de variação + disponibilidade.

## Passos
1. Backend expõe variações/estoque no `StorefrontProduct`.
2. Vitrine: seletor de variação + disponibilidade; add-to-cart envia `variant_id`.

## Testes
- **Níveis:** integração (backend) + e2e (vitrine, se houver infra).
- **Cobrir:** integração — variações/estoque no payload público. e2e — escolher variação → vai pro carrinho com o `variant_id` certo.

## Definition of Done
- [ ] `StorefrontProduct` expõe variações + disponibilidade.
- [ ] Vitrine seleciona a variação; carrinho recebe o `variant_id`.
- [ ] **Modos de falha mapeados** (variação sem estoque; produto sem variação) → tratados/Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Fecha o follow-up "Variações + disponibilidade na vitrine" (Fase 3, `P3-SF-01`/`P3-SF-02`) — marcar na origem ao concluir.

## Follow-ups
- [ ] — nenhum (preencher ao implementar).
