# Fase 5 — Configuração da loja pelo lojista (dev local)

> Objetivo: com os templates **registrados pela plataforma** (admin, [Fase 4](./phase-4-platform-admin.md): metadados + thumbnail + schema), esta fase entrega o **conteúdo demo** dos templates (loja-demo por template, imagens no CDN), a **personalização** schema-driven, o **preview navegável** e o **conteúdo das páginas** — o lojista monta a vitrine no painel (`app.${DOMAIN}`). O picker de template + upload de banner + preview por imagem já existem desde a **[Fase 3](./phase-3-storefront-and-layouts.md)** (`P3-TPL-03`).

Docs de referência: [26](../26_template_system.md) (sistema de templates), [27](../27_template_authoring_guide.md) (autoria de template), [09](../09_merchant_dashboard.md) (painel), [10](../10_storefront_and_layouts.md) (storefront), [25](../25_platform_admin.md) (de onde vêm os templates/schema/thumbnail), [07](../07_database_strategy.md), [13](../13_performance_cache_and_cdn.md), [16](../16_testing_strategy.md).

> **Depende da Fase 4:** o `settings_schema` (vindo do **código** do template) e o **thumbnail no CDN** são registrados no admin. O **import das imagens (chrome/demo) pro CDN**, a **loja-demo por template** e o **preview navegável** são **desta fase**.

## Definition of Done da fase
- Cada template tem sua **loja-demo** (catálogo/imagens do `demo.json`, imagens no **CDN**) — é o **preview navegável** **e** o **modelo** que o lojista copia.
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

## Etapa 3 — Loja-demo por template + import de assets (backend)

> O **conteúdo demo** de cada template (categorias/produtos/imagens) vem de um manifesto **`demo.json`** no código do template (junto do `settings-schema.json`); as imagens **nascem com URL do uxpilot** e são **importadas pro CDN**. Doc [26](../26_template_system.md)/[27](../27_template_authoring_guide.md).

### Manifesto + import (doc [26](../26_template_system.md)/[13](../13_performance_cache_and_cdn.md))
- [ ] **`demo.json` por template** (`frontend-storefront/templates/<id>/`): categorias, produtos (nome/preço/categoria) e **URLs de imagem** (uxpilot). Para Aurora/Bazar/Studio, **transcrito** do `docs/design/`.
- [ ] **`import_assets`** (backend): pra cada URL (uxpilot), **baixa → S3/CloudFront → reescreve** a referência pra URL do CDN (defaults `image` do schema **e** catálogo do demo). Acaba a dependência do uxpilot + de `public/`. *(funde follow-up "imagens-default no CDN" da Fase 4)*

### Loja-demo por template (doc [26](../26_template_system.md))
- [ ] **Monta a loja-demo** de cada template (`<id>-demo`): um `store` real com `active_template_id = <id>` + catálogo do `demo.json` (imagens já no CDN). **Idempotente**; é o **modelo** que o lojista copia.
- [ ] **Aurora/Bazar/Studio** ganham sua loja-demo (carga artificial do `docs/design/`, pelo **mesmo caminho** de um template futuro — doc [27](../27_template_authoring_guide.md)).

---

## Etapa 4 — Vitrine lê os settings + preview navegável

### Vitrine (doc [10](../10_storefront_and_layouts.md)/[26](../26_template_system.md))
- [ ] Aurora/Bazar/Studio leem `theme.settings[key] ?? <default do template>` nos textos/imagens de chrome.
- [ ] **Campos de imagem com default no CDN** — a imagem original do template (importada na Etapa 3) preenche o default; nunca fundo vazio.

### Preview navegável (doc [26](../26_template_system.md))
- [ ] Botão **"ver preview completo"** no painel → abre, em **outra aba**, o **template navegável** (storefront servindo a **loja-demo** do template — Etapa 3) — cada clique funciona.
- [ ] **Remover o `previewLayout`** (backend) — sem uso desde o `P3-TPL-03` (o preview navegável o substitui). *(funde follow-ups "previewLayout sem uso" + "preview ao vivo")*

---

## Etapa 5 — Conteúdo das páginas (content_pages/menus/banners)

> Os modelos (`content_pages`/`content_menus`/`content_menu_items`/`content_banners`) já existem (`P3-CONTENT-01`); faltam **rotas + UI** no painel e o **wiring** na vitrine.

### Painel (doc [09](../09_merchant_dashboard.md))
- [ ] **CRUD de páginas** (institucionais: sobre/privacidade/termos/trocas + avulsas), **menus** e **banners** no painel — o lojista escreve o conteúdo real. *(funde "CRUD de páginas/menus/banners" + "páginas institucionais via content_pages" da Fase 3)*

### Vitrine (doc [10](../10_storefront_and_layouts.md))
- [ ] `/pages/[slug]` passa a ler de **`content_pages`** (hoje mostra defaults apresentáveis do `P3-TPL-03`); fallback pro default quando a página não existir.

---

## Fora de escopo
- **Registro do template** (id/nome/thumbnail/schema) no admin → [Fase 4](./phase-4-platform-admin.md) (aqui entram o **import das imagens**, a **loja-demo** e o **preview**).
- **Cores do tema por loja** (acento aplicado a cada template) → task à parte (cada template usa as cores originais por ora).
- **Editor visual drag-drop / reordenar blocos livres** → V1 = campos declarados no schema (blocos opcionais = campos `boolean`).
- **Motor genérico de HTML** (cadastrar template 100% sem deploy) → fora da V1 (mantém o port React fiel — doc [26](../26_template_system.md)).

---

## Testes (doc [16](../16_testing_strategy.md))
- [ ] `import_assets`: baixa a URL de origem → sobe pro CDN → reescreve a referência (mock S3 `moto`).
- [ ] Loja-demo montada do `demo.json` (idempotente); Aurora/Bazar/Studio têm loja-demo; o storefront serve a loja-demo com o template.
- [ ] Form renderiza do schema do template ativo (sem código por template); valor inválido (tipo/`max_length`) → 422.
- [ ] Salvar grava por **loja × template**; **trocar de template preserva** os valores de cada um; reset volta aos defaults.
- [ ] Vitrine reflete os settings (defaults quando vazio); campo `image` sem valor → default do CDN.
- [ ] `/pages/[slug]` lê `content_pages`; página inexistente → fallback.

---

## Reconciliações
- A **personalização do lojista** (`P3-TPL-04`) é desta fase — **depende** do admin (Fase 4) registrar o template/schema/thumbnail. A Fase 3 entrega os 3 templates + picker + banner + preview por imagem. Decisões no doc [26](../26_template_system.md).
- O **conteúdo demo** (loja-demo por template + `import_assets`) e o **preview navegável** são desta fase — dependem da vitrine ler `theme.settings` + do catálogo demo (não dá pra ficar "bonito como o design" sem isso). Passo-a-passo de autoria no doc [27](../27_template_authoring_guide.md).
- **content_pages/menus/banners** entram aqui (config da loja pelo lojista): a vitrine deixa os defaults apresentáveis e passa a usar o conteúdo real.
