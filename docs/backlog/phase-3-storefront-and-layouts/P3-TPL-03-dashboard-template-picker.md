---
id: P3-TPL-03
title: Painel — seletor de template com preview
phase: 3
etapa: "Etapa 8 — Templates no storefront"
area: TPL
status: todo
depends_on: [P3-TPL-01]
blocks: []
tests: [e2e]
---

# P3-TPL-03 — Painel: seletor de template com preview

## Contexto
A tela "Layout da Loja" (`P3-FE-02`) evolui pra mostrar a **lista de templates com imagem de preview**: o lojista escolhe o template ativo **pela imagem** (sem preview ao vivo ainda) e a vitrine passa a renderizar o escolhido. Depende do registro `content_theme_templates` (com `preview_image_url`) criado em `P3-TPL-01`.

## Docs de referência
- [09 — Merchant Dashboard](../../09_merchant_dashboard.md) (§"Layout da loja")
- [`P3-FE-02`](./P3-FE-02-layout-screen.md) (tela atual) · [`P3-TPL-01`](./P3-TPL-01-rich-templates-spec.md) (registry/`active_template_id`)

## Escopo (o que ENTRA)
- **Lista de templates** (de `content_theme_templates`) com **`preview_image_url`** + nome/descrição, na tela "Layout da Loja".
- **Selecionar** um template → grava `active_template_id` da loja (endpoint existente do `P3-FE-02` ou novo).
- **Indicar o ativo** (estado selecionado) e refletir na vitrine.

## Fora de escopo (o que NÃO entra)
- **Preview ao vivo** (render real da loja com o template) → futuro.
- **Admin (loja.club) pra cadastrar/gerenciar templates** → Fase 7.
- **Config de blocos por template** (ligar/desligar) → futuro.

## Arquivos a criar/alterar
- `frontend-dashboard/src/routes/_layout/store-layout.tsx` (alterar) — grade de templates com imagem + seleção.
- `backend` (alterar, se preciso) — endpoint que lista templates com `preview_image_url` / grava `active_template_id`.
- `docs/09_merchant_dashboard.md` (alterar) — reconciliar a tela.

## Passos
1. Endpoint/where: listar templates (com `preview_image_url`) + gravar o ativo.
2. UI: grade de cards (imagem + nome) com seleção; marca o ativo.
3. e2e: selecionar template → persiste → vitrine reflete.

## Testes
> Regra em [`_foundations-and-bottlenecks.md`](../_foundations-and-bottlenecks.md) §10.

- **Níveis:** e2e (selecionar template no painel). **Quando:** durante.
- **Cobrir:**
  - e2e — painel lista os templates com imagem; trocar grava o ativo e a vitrine passa a renderizar o novo.

## Definition of Done
- [ ] Painel lista os templates **com imagem de preview**; selecionar **grava** o `active_template_id`; o ativo fica indicado.
- [ ] A **vitrine reflete** o template escolhido.
- [ ] Gates verdes (dashboard `tsc`/biome/`vitest` + **e2e local**) + docs 09 reconciliado.
- [ ] **Modos de falha mapeados** (`preview_image_url` ausente → placeholder; lista vazia; gravação falha) → tratados **ou** Follow-up.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Reaproveita o endpoint de seleção de template do `P3-FE-02` quando existir; senão, cria um mínimo.

## Follow-ups
- [ ] **Preview ao vivo no painel** — *Quando:* pós-V1 (hoje só a imagem). → README.
- [ ] **Admin de cadastro de templates** — *Quando:* Fase 7. → README.
