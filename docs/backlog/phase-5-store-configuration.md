# Fase 5 — Configuração da loja pelo lojista (dev local)

> Objetivo: com os templates **cadastrados pela plataforma** (admin, [Fase 4](./phase-4-platform-admin.md)), o lojista **personaliza** a loja dele no painel (`app.${DOMAIN}`) — a **personalização do template** (schema-driven, `P3-TPL-04`) + o **preview navegável completo** + o **conteúdo das páginas** (institucionais/menus/banners). O picker de template + upload de banner + preview por imagem já existem desde a **[Fase 3](./phase-3-storefront-and-layouts.md)** (`P3-TPL-03`).

Docs de referência: [26](../26_template_system.md) (sistema de templates), [09](../09_merchant_dashboard.md) (painel), [10](../10_storefront_and_layouts.md) (storefront), [25](../25_platform_admin.md) (de onde vêm os templates/schema/CDN), [07](../07_database_strategy.md), [13](../13_performance_cache_and_cdn.md), [16](../16_testing_strategy.md).

> **Depende da Fase 4:** o `settings_schema` (vindo do **código** do template) e os **assets no CDN** (imagens-default) são registrados no admin; aqui o lojista **consome** isso.

## Definition of Done da fase
- O lojista **personaliza o template** por um **form gerado do schema** (campos do template ativo), com valores por **loja × template** (não perde ao trocar) e **reset** (excluir → volta aos defaults).
- A **vitrine reflete** os settings (defaults quando vazio); **campos de imagem** têm default = a imagem original do template **no CDN**.
- O painel abre o **preview navegável completo** do template (outra aba).
- O lojista **edita as páginas** (institucionais/menus/banners); a vitrine (`/pages/*`) mostra o conteúdo real.

---

## Etapa 1 — Settings schema: storage + API (backend)

> O schema **vem do código** (manifesto), seedado em `content_theme_templates.settings_schema` na [Fase 4](./phase-4-platform-admin.md). Aqui entra o **armazenamento dos valores** do lojista + a API.

### Modelo (com `store_id`) (doc [07](../07_database_strategy.md)/[26](../26_template_system.md))
- [ ] `content_store_template_settings`: `store_id`, `template_id`, `settings` (jsonb), soft delete. **Único por (store, template) entre os ativos** (índice parcial `deleted_at IS NULL`).

### Serviço/rotas (doc [26](../26_template_system.md))
- [ ] **API pública:** `StorefrontTheme.settings` = defaults do schema **mesclados** com os overrides da loja, do template **ativo**; **invalida cache** ao salvar.
- [ ] **API painel:** `GET …/templates` devolve o `settings_schema`; `GET/PATCH …/layout/settings` lê/grava (validado contra o schema; gating `layout.update`); `DELETE` **reseta** (soft-delete a linha → re-selecionar zera).

---

## Etapa 2 — Form genérico no painel

### `TemplateSettingsForm` (doc [09](../09_merchant_dashboard.md)/[26](../26_template_system.md))
- [ ] Renderizador **genérico** a partir do schema do template ativo (input por `type`: `text`/`textarea`/`image`/`boolean`/`select`), agrupado por `group`. **Um componente, N schemas.**
- [ ] **"Meus templates":** lista os templates que o lojista **já editou** (linhas ativas) + **resetar** (excluir).
- [ ] Upload de imagem (campos `image`) reusa `media`. **Fix:** o upload no contexto de **layout** deve ser gated em **`layout.update`** (hoje o endpoint de `media` exige `catalog.product.update`). *(funde follow-up "permissão do upload do banner" da Fase 3)*

---

## Etapa 3 — Vitrine lê os settings + preview navegável

### Vitrine (doc [10](../10_storefront_and_layouts.md)/[26](../26_template_system.md))
- [ ] Aurora/Bazar/Studio leem `theme.settings[key] ?? <default do template>` nos textos/imagens de chrome.
- [ ] **Campos de imagem com default no CDN** — a imagem original do template (cadastrada na Fase 4) preenche o default; nunca fundo vazio.

### Preview navegável (doc [26](../26_template_system.md))
- [ ] Botão **"ver preview completo"** no painel → abre, em **outra aba**, o **template navegável** (storefront renderizando a **loja-demo** com o template — Fase 4) — cada clique funciona.
- [ ] **Remover o `previewLayout`** (backend) — sem uso desde o `P3-TPL-03` (o preview navegável o substitui). *(funde follow-ups "previewLayout sem uso" + "preview ao vivo")*

---

## Etapa 4 — Conteúdo das páginas (content_pages/menus/banners)

> Os modelos (`content_pages`/`content_menus`/`content_menu_items`/`content_banners`) já existem (`P3-CONTENT-01`); faltam **rotas + UI** no painel e o **wiring** na vitrine.

### Painel (doc [09](../09_merchant_dashboard.md))
- [ ] **CRUD de páginas** (institucionais: sobre/privacidade/termos/trocas + avulsas), **menus** e **banners** no painel — o lojista escreve o conteúdo real. *(funde "CRUD de páginas/menus/banners" + "páginas institucionais via content_pages" da Fase 3)*

### Vitrine (doc [10](../10_storefront_and_layouts.md))
- [ ] `/pages/[slug]` passa a ler de **`content_pages`** (hoje mostra defaults apresentáveis do `P3-TPL-03`); fallback pro default quando a página não existir.

---

## Fora de escopo
- **Cores do tema por loja** (acento aplicado a cada template) → task à parte (cada template usa as cores originais por ora).
- **Editor visual drag-drop / reordenar blocos livres** → V1 = campos declarados no schema (blocos opcionais = campos `boolean`).
- **Cadastro de template novo** (admin, schema, CDN) → [Fase 4](./phase-4-platform-admin.md).

---

## Testes (doc [16](../16_testing_strategy.md))
- [ ] Form renderiza do schema do template ativo (sem código por template); valor inválido (tipo/`max_length`) → 422.
- [ ] Salvar grava por **loja × template**; **trocar de template preserva** os valores de cada um; reset volta aos defaults.
- [ ] Vitrine reflete os settings (defaults quando vazio); campo `image` sem valor → default do CDN.
- [ ] `/pages/[slug]` lê `content_pages`; página inexistente → fallback.

---

## Reconciliações
- A **personalização do lojista** (`P3-TPL-04`) é desta fase — **depende** do admin (Fase 4) cadastrar templates/schema/CDN. A Fase 3 entrega os 3 templates + picker + banner + preview por imagem. Decisões no doc [26](../26_template_system.md).
- **content_pages/menus/banners** entram aqui (config da loja pelo lojista): a vitrine deixa os defaults apresentáveis e passa a usar o conteúdo real.
