---
id: P7-SF-02
title: Vitrine — seleção de variação (geral, não-3D)
phase: 7
etapa: "Etapa 8 — Vitrine: seleção de variação (geral, não-3D)"
area: SF
status: todo
depends_on: []
blocks: []
tests: [integration, e2e]
---

# P7-SF-02 — Seleção de variação na vitrine

## Contexto
**Veio da Fase 6** (fast-follow `P6-SF-02`): a página de produto da vitrine ganha o **seletor de variação**. Fica aqui porque é a fase que reabre a página de produto (junto do editor 3D). **Não depende de 3D** — só do catálogo (Fase 2) + carrinho (`P6-CART-01`, que já aceita `variant_id`).

## Docs de referência
- [10 — Página de produto](../../concepts/10_storefront_and_layouts.md)
- [07 — variações/estoque](../../concepts/07_database_strategy.md)

## Escopo (o que ENTRA)
- `StorefrontProduct` passa a expor **variações + disponibilidade** (hoje só imagem/nome/preço/descrição) — `backend/app/modules/storefront/{schemas,services}.py`.
- Página de produto (**3 templates**): **escolher a variação** + ver disponibilidade; o add-to-cart envia o `variant_id` (o backend já guarda em `cart_items` desde `P6-CART-01`).

## Fora de escopo (o que NÃO entra)
- Qualquer coisa de 3D/personalização (outras tasks da fase).

## Arquivos a criar/alterar
- `backend/app/modules/storefront/{schemas,services}.py` (alterar) — variações + disponibilidade no payload.
- `frontend-storefront/templates/{aurora,bazar,studio}/...` (alterar) — seletor de variação na página de produto.

## Passos
1. Backend: expor variações/estoque no `StorefrontProduct`.
2. Templates: seletor de variação + disponibilidade + add-to-cart com `variant_id`.

## Testes
- **Níveis:** integração + e2e.
- **Quando escrever:** durante.
- **Cobrir:** integração — payload público traz variações/estoque; e2e (`P3-SF-03`) — escolher variação → carrinho com o `variant_id` certo.

## Definition of Done
- [ ] Vitrine mostra variações + disponibilidade; add-to-cart manda o `variant_id` certo (3 templates).
- [ ] **Modos de falha mapeados** — variação **sem estoque** (desabilita/avisa); produto **sem variação** (compra direta). → tratados/Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Fecha o follow-up "**Vitrine expõe variações + disponibilidade**" (Fase 3, `P3-SF-01`/`P3-SF-02`) — marcar `[x]` na origem ao concluir.

## Follow-ups
- [ ] **Matriz de variação multi-opção** (ex.: cor × tamanho) se o catálogo evoluir — *Quando:* se variações ganharem múltiplos eixos. → README da fase.
