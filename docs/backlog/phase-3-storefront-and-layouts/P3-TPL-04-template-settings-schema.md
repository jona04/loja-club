---
id: P3-TPL-04
title: Personalização por template (theme settings schema-driven)
phase: 3
etapa: "Etapa 3 — Módulo de conteúdo/layout"
area: TPL
status: todo
depends_on: [P3-TPL-02, P3-TPL-03]
blocks: []
tests: [unit, integration, e2e]
---

# P3-TPL-04 — Personalização por template (settings schema-driven)

## Contexto
Cada template tem **blocos e textos de chrome diferentes** — barra de anúncio + faixa editorial + trust indicators (Aurora), promo + badge "Oferta Especial" (Bazar), "Nova Coleção" + subtítulo do banner (Studio). **Alguns blocos existem num template e não no outro.** Logo, **não serve** um form genérico único, e **tela-por-template não escala** (quebraria a Fase 4, onde o admin cadastra template novo). A solução é **schema-driven**: cada template **declara** os campos que expõe; o painel renderiza **um form genérico** a partir desse schema; os valores ficam por **loja × template**; a vitrine lê com **defaults**. Encaixa no princípio do sistema: o **dado é contrato** (compartilhado), a **apresentação é por template**.

## Abordagem (schema-driven — como Shopify / WP Customizer)
- **Manifesto por template** (`settings_schema`): campos `{ key, type, label, group, default, max_length? }`. Tipos V1: `text` · `textarea` · `image` · `boolean` · `select` (cor = Follow-up).
  - **Todo bloco/frase é editável**; o `default` já vem preenchido (texto genérico que serve a qualquer ecommerce) — o lojista altera se quiser.
  - **Campo `image` tem default = a imagem original do template** (hospedada) — nunca renderiza fundo vazio.
  - Bloco que **só existe num template** → está só no schema dele; bloco **opcional** (liga/desliga) → campo `boolean` que condiciona os dependentes.
- **Valores por loja × template** — trocar de template e voltar **não perde** o preenchido. O painel **lista os templates já editados**; **resetar = excluir** (soft delete) → re-selecionar volta **zerado** (defaults).
- **Painel = 1 renderizador genérico** (`TemplateSettingsForm`): monta o form do schema do template ativo (input por `type`, agrupado por `group`). **Um componente, N schemas.**
- **Vitrine** lê `theme.settings[key] ?? <default do template>` (cada template conhece suas chaves).
- **Fase 4:** admin cadastra template + schema → painel e vitrine **só funcionam**, sem código de painel novo.

## Docs de referência
- [`P3-TPL-03`](./P3-TPL-03-dashboard-template-picker.md) (picker + banner) · [`P3-TPL-01`](./P3-TPL-01-template-architecture-aurora.md) (templates/contrato) · [`P3-TPL-02`](./P3-TPL-02-templates-bazar-studio.md)
- [09 — Merchant Dashboard](../../concepts/09_merchant_dashboard.md) · [10 — Storefront & Layouts](../../concepts/10_storefront_and_layouts.md)

## Escopo (o que ENTRA)
- **`settings_schema` por template** — coluna em `content_theme_templates`, **seedada** (Aurora/Bazar/Studio) com **todos os blocos/frases editáveis** de cada um + defaults (os textos apresentáveis do `P3-TPL-03` viram esses defaults). Tipos V1: `text`/`textarea`/`image`/`boolean`/`select`.
- **Defaults de imagem** — todo campo `image` tem default = a **imagem original do template** (baixada das fontes do template / `docs/design/templates/<id>/` → hospedada em S3/CloudFront ou `public/`), pra nunca renderizar fundo vazio.
- **Storage por loja × template** — `content_store_template_settings(store_id, template_id, settings jsonb)` (soft delete; **único por par entre os ativos** — índice parcial `deleted_at IS NULL`). **Resetar = soft-delete** da linha → re-selecionar cria fresca (defaults).
- **"Meus templates" no painel** — lista os templates que o lojista **já editou** (linhas ativas), pra ele saber o que fez + poder **resetar** (excluir) um.
- **API pública** — `StorefrontTheme.settings` (defaults do schema **mesclados** com os overrides da loja, pro template **ativo**); **invalida cache** ao salvar.
- **API painel** — `GET …/templates` devolve o `settings_schema`; `GET/PATCH …/layout/settings` lê/grava (validado contra o schema; gating `layout.update`); `DELETE` **reseta** o template.
- **Form genérico no painel** — `TemplateSettingsForm` (render por `type`, agrupado por `group`); upload de imagem reusa `media`.
- **Vitrine lê os settings** — Aurora/Bazar/Studio leem `theme.settings[key]` (defaults como fallback) nos textos/imagens de chrome.

## Fora de escopo (o que NÃO entra)
- **Editor visual drag-drop / reordenar blocos livres** → V1 = campos declarados no schema.
- **Cadastro de template novo pelo admin** → Fase 4 (mas o design já prevê).
- **Preview ao vivo enquanto edita** → follow-up (o preview por imagem é do `P3-TPL-03`).
- **Schema por idioma (i18n)** → futuro.
- **Cores do tema** (acento por loja) → **task à parte** (por ora cada template usa as cores originais — ver Follow-ups).

## Arquivos a criar/alterar
- `backend/app/modules/content/models.py` — `settings_schema` em `ThemeTemplate` + `StoreTemplateSettings` (store × template).
- `backend/app/modules/content/repositories.py` — seed dos schemas por template; get/upsert dos valores.
- `backend/app/modules/content/{services,routes,schemas}.py` — merge defaults+overrides, validação contra schema, endpoints do painel, invalidação de cache.
- `backend/app/modules/storefront/{services,schemas}.py` — `StorefrontTheme.settings` (do template ativo).
- `backend/alembic/versions/*` — migration (coluna + tabela).
- `frontend-dashboard/src/.../TemplateSettingsForm.tsx` + a tela de Layout (aba "Conteúdo do template").
- `frontend-storefront/templates/{aurora,bazar,studio}/*` — ler `theme.settings`; `lib/api.ts` (tipo `settings`).
- `docs/{09_merchant_dashboard,10_storefront_and_layouts}.md` — reconciliar.

## Passos
1. Backend: coluna `settings_schema` + seed (Aurora/Bazar/Studio) + tabela de valores.
2. Backend: merge defaults+overrides → `theme.settings` (público) + endpoints do painel (schema + valores) + validação + cache.
3. Painel: `TemplateSettingsForm` genérico (por `type`, agrupado) na tela de Layout.
4. Vitrine: os 3 templates leem `theme.settings[key] ?? default`.
5. e2e: editar um campo do template ativo no painel → vitrine reflete; trocar de template **preserva** os valores de cada um.

## Testes
> Regra em [`_foundations-and-bottlenecks.md`](../_foundations-and-bottlenecks.md) §10.
- **Níveis:** unit (merge defaults+overrides; validação contra schema) + integração (endpoints painel/público) + e2e (editar → refletir; trocar template preserva). **Quando:** durante.
- **Cobrir:** campo ausente → default; valor inválido (tipo / `max_length`) → 422; bloco opcional off → vitrine esconde; trocar template **não vaza** valores de um pro outro.

## Definition of Done
- [ ] Cada template tem `settings_schema` seedado; o painel **renderiza o form do template ativo a partir do schema** (sem código por template).
- [ ] Salvar grava por **loja × template**; **trocar de template preserva** os valores de cada um.
- [ ] A **vitrine reflete** os settings (defaults quando não preenchido); os 3 templates leem `theme.settings`.
- [ ] Campos `image` têm **default** (imagem original do template) — nunca fundo vazio.
- [ ] Painel **lista os templates editados** + **resetar** (excluir → volta aos defaults).
- [ ] Gates verdes (backend lint/cobertura + dashboard `tsc`/biome/`vitest` + storefront build + **e2e local**) + docs 09/10 reconciliados.
- [ ] **Modos de falha mapeados** (schema ausente; valor inválido; imagem falha; bloco opcional) → tratados ou Follow-up.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- **Sai do `P3-TPL-03`** (que ficou com picker + banner + preview). Os **defaults apresentáveis** definidos lá viram os **defaults do schema** aqui — sem retrabalho.
- **Campo universal vs por-template:** `banner_image_url` / `headline` / `primary_color` / logo / WhatsApp continuam **universais** (em `content_store_theme_settings`); o schema cobre só o **chrome específico** de cada template.
- **Decisão ao entrar:** se na hora pesar demais pro lançamento, **pode ir pro pós-lançamento** — os defaults apresentáveis (`P3-TPL-03`) já deixam a vitrine lançável sem isto.

## Follow-ups
- [ ] **Preview ao vivo enquanto edita** — *Quando:* pós-V1. → README.
- [ ] **Schema por idioma (i18n)** — *Quando:* pós-V1. → README.
- [ ] **Admin cadastra template + schema** — *Quando:* Fase 4 (o design já prevê). → README.
- [ ] **Cores do tema por loja** (acento aplicado a cada template) — *Quando:* task à parte (por ora cada template usa as cores originais). → README.
