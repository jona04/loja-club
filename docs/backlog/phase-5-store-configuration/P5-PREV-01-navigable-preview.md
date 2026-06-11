---
id: P5-PREV-01
title: Preview navegável (painel abre a loja-demo do template)
phase: 5
etapa: "Etapa 5 — Vitrine lê settings + preview navegável"
area: PREV
status: todo
depends_on: [P5-DEMO-02, P5-SF-01]
blocks: []
tests: [e2e]
---

# P5-PREV-01 — Preview navegável

## Contexto
O preview navegável = o storefront servindo a **loja-demo** do template (cada clique navega de verdade: home → categoria → produto → carrinho). O painel abre esse preview em vez de só uma imagem.

## Docs de referência
- [26 — Sistema de templates](../../concepts/26_template_system.md) (§"A loja-demo", §"Ciclo de vida")
- [27 — Guia de autoria](../../concepts/27_template_authoring_guide.md) (Passo 8)
- [10 — Storefront and Layouts](../../concepts/10_storefront_and_layouts.md) (§"Preview")

## Escopo (o que ENTRA)
- O painel abre o **preview navegável completo** do template (outra aba) — a **loja-demo** (`<id>-demo`) servida pelo storefront.
- **Remover o `previewLayout`** (backend) — sem uso desde o `P3-TPL-03` (o preview navegável o substitui).

## Fora de escopo (o que NÃO entra)
- Montar a loja-demo: `P5-DEMO-02`.
- A vitrine ler settings: `P5-SF-01`.

## Arquivos a criar/alterar
- `frontend-dashboard/src/routes/_layout/store-layout.tsx` (alterar) — botão "abrir preview navegável".
- `backend/app/modules/content/{services,routes}.py` (alterar) — remover `previewLayout`.

## Passos
1. Painel: botão abre a loja-demo do template (URL do storefront).
2. Remover o `previewLayout` do backend (e do painel).

## Testes
- **Níveis:** e2e (Playwright).
- **Cobrir:** e2e — abrir o preview navega na loja-demo (home → categoria → produto).

## Definition of Done
- [ ] Painel abre o preview navegável (loja-demo do template).
- [ ] `previewLayout` removido (backend + painel).
- [ ] Gates + e2e.
- [ ] **Modos de falha mapeados** (loja-demo ausente, template sem demo) → tratados ou Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Funde os follow-ups "previewLayout sem uso" e "preview ao vivo / botão abrir preview" das Fases 3/4.

## Follow-ups
- [ ] — nenhum (preencher ao implementar).
