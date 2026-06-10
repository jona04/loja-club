---
id: P3-TPL-03
title: Painel — Layout da loja (template + thumb, banner, preview)
phase: 3
etapa: "Etapa 8 — Templates no storefront"
area: TPL
status: done
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
- **Defaults de chrome apresentáveis** (não-lorem): trocar os textos lorem/placeholder dos templates (ex.: faixa editorial do Aurora) por **defaults genéricos mas profissionais** — pra lançar nos defaults sem cara de quebrado. (Tornar esses textos **editáveis** pelo lojista = `P3-TPL-04`.)

## Fora de escopo (o que NÃO entra)
- **Preview ao vivo** (render real da loja com o template) → futuro.
- **Admin (loja.club) pra cadastrar/gerenciar templates** → Fase 4.
- **Personalização por template** (editar textos de chrome, ligar/desligar blocos, cores do tema) → **[`P3-TPL-04`](./P3-TPL-04-template-settings-schema.md)** (schema-driven).

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
- [x] Painel lista os templates **com thumbnail** (`preview_image_url`) + **Dialog em tamanho real**; selecionar **grava** o `active_template_id`; o ativo fica marcado ("Ativo").
- [x] A **vitrine reflete** o template escolhido (já desde o `P3-TPL-02`).
- [x] **Banner** enviável (upload → `media`/S3 → `banner_image_url`) + **preview** funcionando (Dialog com a imagem); **defaults de chrome apresentáveis** (páginas institucionais sem lorem).
- [x] Gates verdes (dashboard `tsc`/biome + storefront build/biome) + docs 09 reconciliado; **e2e não cobre a tela de Layout** (specs = auth/settings) → sem impacto; previews confirmados no DB.
- [x] **Modos de falha mapeados:** `preview_image_url` ausente → sem thumb/"Sem prévia"; lista vazia → grade vazia; upload falha → toast.
- [x] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Reaproveita o endpoint de seleção de template do `P3-FE-02` quando existir; senão, cria um mínimo.
- **Dividida:** a personalização por template (editar anúncio/editorial/etc. + cores) saiu pra **[`P3-TPL-04`](./P3-TPL-04-template-settings-schema.md)** (schema-driven). Aqui fica o **picker + banner + preview** (+ defaults apresentáveis).
- **Implementação (frontend-only):** thumbnails de `preview_image_url` (PNGs em `frontend-dashboard/public/templates/`); **preview = Dialog** com a imagem em tamanho real (substitui o texto inútil — `previewLayout` do backend ficou sem uso, ver Follow-ups); **banner = upload** via `MediaService.uploadMedia(owner_type="banner")` → `media.url` → `banner_image_url` (o lojista salva). Defaults apresentáveis em `/pages/[slug]` (sem lorem).

## Follow-ups
- [ ] **Preview ao vivo no painel** — *Quando:* pós-V1 (hoje só a imagem). → README.
- [ ] **Admin de cadastro de templates** — *Quando:* Fase 4. → README.
- [ ] **Previews no CloudFront** — *Quando:* antes de produção (hoje os PNGs vêm do `public/` do dashboard; subir pro S3/CloudFront + `preview_image_url` com URL real). → README.
- [ ] **`previewLayout` (backend) sem uso na UI** — o preview virou imagem (client); **remover** o endpoint/serviço ou **repurpose** pra live-preview. → README.
- [ ] **Permissão do upload do banner** — reusa o endpoint de `media` (gated `catalog.product.update`); pra layout deveria aceitar `layout.update`. → README.
- [ ] **Páginas institucionais via `content_pages`** — `/pages/*` mostram defaults apresentáveis; o conteúdo real (editável pelo lojista) sai de `content_pages` (feature à parte). → README.
