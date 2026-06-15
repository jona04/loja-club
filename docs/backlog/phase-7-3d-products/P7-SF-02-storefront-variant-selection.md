---
id: P7-SF-02
title: Vitrine — seleção de variação (geral, não-3D)
phase: 7
etapa: "Etapa 8 — Vitrine: seleção de variação (geral, não-3D)"
area: SF
status: done
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
- [x] Vitrine mostra variações + disponibilidade; add-to-cart manda o `variant_id` certo (3 templates).
- [x] **Modos de falha mapeados** — variação **sem estoque** → `<option>` desabilitada "(esgotado)" + botão "Esgotado" (não adiciona); produto **sem variação** → compra direta; produto sem estoque → "Esgotado". O carrinho ainda **revalida** o estoque no add (409). → tratados.
- [x] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- **Backend:** `StorefrontProduct` (detalhe) ganhou `variants` (`StorefrontVariant`: preço efetivo = override ou do produto + `in_stock`/`available_quantity`) e o estoque do produto (`in_stock`/`available_quantity`). Disponibilidade = `catalog_inventory_items` (sem linha = ilimitado, espelha a checagem do carrinho). Variações **arquivadas** não aparecem. Só no **detalhe** (cards/home ficam leves).
- **Cache:** o detalhe é cache-aside (300 s, [31 §3](../../concepts/31_configuration_and_constants.md)) → disponibilidade pode ficar ≤ 5 min defasada; aceitável porque o carrinho revalida (409). Invalidar o cache do produto ao mudar estoque/variação = follow-up.
- **Frontend:** `useVariantSelection` (estado + disponibilidade) + `VariantSelect` (seletor compartilhado, estilizado por template); `addToCart`/`useCart.add` ganharam `variantId`. Default = 1ª variação em estoque.
- **e2e:** **deferido** — não existe harness Playwright da **vitrine** ainda (o de e2e roda contra o painel:5180; vitrine = Next:3000). Depende da infra `P3-SF-03`, igual ao e2e do fluxo de personalização. Coberto por integração (backend) + unit (`useVariantSelection`).
- Fecha o follow-up "**Vitrine expõe variações + disponibilidade**" (Fase 3) — marcado `[x]` no README.

## Follow-ups
- [ ] **Matriz de variação multi-opção** (ex.: cor × tamanho) se o catálogo evoluir — *Quando:* se variações ganharem múltiplos eixos. → README da fase.
- [ ] **e2e Playwright da vitrine** (escolher variação → carrinho com `variant_id`; esgotado bloqueia) — depende da infra `P3-SF-03`. → README da fase.
- [ ] **Invalidar o cache do produto** ao mudar estoque/variação no painel (hoje ≤ 5 min defasado; o carrinho revalida). → README da fase.
- [ ] **Preço da variação selecionada na página** (hoje o seletor mostra só nome + esgotado; o preço efetivo aparece no carrinho). → README da fase.
