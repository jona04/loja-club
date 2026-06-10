---
id: P3-TPL-03
title: Painel — Layout da loja (template + thumb, banner, preview)
phase: 3
etapa: "Etapa 8 — Templates no storefront"
area: TPL
status: todo
depends_on: [P3-TPL-01]
blocks: []
tests: [e2e]
---

# P3-TPL-03 — Painel: Layout da loja (template + banner + preview)

## Contexto
A tela "Layout da Loja" (`P3-FE-02`) evolui pra mostrar a **lista de templates com imagem de preview**: o lojista escolhe o template ativo **pela imagem** (sem preview ao vivo ainda) e a vitrine passa a renderizar o escolhido. Depende do registro `content_theme_templates` (com `preview_image_url`) criado em `P3-TPL-01`.

## Docs de referência
- [09 — Merchant Dashboard](../../09_merchant_dashboard.md) (§"Layout da loja")
- [`P3-FE-02`](./P3-FE-02-layout-screen.md) (tela atual) · [`P3-TPL-01`](./P3-TPL-01-template-architecture-aurora.md) (registry/`active_template_id`)

> **Princípio:** todo recurso que o template usa (banner/hero, destaques, …) precisa ter **como o lojista usar/editar** no painel. Hoje há funcionalidades no template **sem UI** pra alimentá-las.

## Escopo (o que ENTRA)
- **Lista de templates** (de `content_theme_templates`) com **NOME + THUMBNAIL** (a `preview_image_url`) na tela "Layout da Loja" — hoje mostra **só o nome**. As imagens já estão **seedadas** (`/templates/<id>_preview.png`) e **servidas hardcoded** do `frontend-dashboard/public/templates/` (subir pro CloudFront = follow-up).
- **Selecionar** um template → grava `active_template_id` da loja (endpoint existente do `P3-FE-02` ou novo).
- **Indicar o ativo** (estado selecionado) e refletir na vitrine.
- **Upload da imagem do banner/hero** da home: o lojista **sobe a imagem** pela tela "Layout da Loja" (S3 + CloudFront, como as imagens de produto/`media`), gravando em `banner_image_url`. Hoje o template tem hero/banner mas **não há como enviar a imagem**.
- **Corrigir o botão "Preview"** da tela de Layout (hoje **não funciona**).
- **Tornar editável o conteúdo hoje fixo/lorem** do template: subtítulo do hero, **barra de anúncio**, seção editorial, trust indicators, **páginas institucionais** (`/institucional/*` → `content_pages`), contato do footer e subtítulo do card. (Hoje hardcoded/lorem no Aurora — `P3-TPL-01`.)
- **Aplicar o tema da loja** (cores/fonte: `theme.primary_color` etc.) nos templates — hoje o Aurora usa a **paleta fixa** do template.

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
- [ ] **Banner** enviável (S3) + **preview** funcionando; o conteúdo hoje fixo/lorem do template (anúncio, editorial, institucional, etc.) tem **campos no painel**; o **tema da loja** (cores) reflete no template.
- [ ] Gates verdes (dashboard `tsc`/biome/`vitest` + **e2e local**) + docs 09 reconciliado.
- [ ] **Modos de falha mapeados** (`preview_image_url` ausente → placeholder; lista vazia; gravação falha) → tratados **ou** Follow-up.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Reaproveita o endpoint de seleção de template do `P3-FE-02` quando existir; senão, cria um mínimo.
- A task **cresceu** (picker + banner + preview + tornar todo o conteúdo editável + tema): ao fechar o spec, **provável dividir** — ex.: `P3-TPL-03a` (picker + banner + preview) e `P3-TPL-03b` (editor do conteúdo do template + tema).

## Follow-ups
- [ ] **Preview ao vivo no painel** — *Quando:* pós-V1 (hoje só a imagem). → README.
- [ ] **Admin de cadastro de templates** — *Quando:* Fase 7. → README.
- [ ] **Previews no CloudFront** — *Quando:* antes de produção (hoje os PNGs vêm do `public/` do dashboard; subir pro S3/CloudFront + `preview_image_url` com URL real). → README.
