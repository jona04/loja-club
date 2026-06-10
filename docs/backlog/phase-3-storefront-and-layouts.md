# Fase 3 — Storefront público e layouts

> Objetivo: loja pública abre em `nomedaloja.loja.club` com o template escolhido; produtos (de imagem) e categorias renderizam; lojista troca o template e a loja pública muda. O **editor 3D + personalização** é a **[Fase 7](./phase-7-3d-products.md)**.

Docs de referência: [05](../05_frontend_architecture.md), [10](../10_storefront_and_layouts.md), [22](../22_product_customization_3d.md), [13](../13_performance_cache_and_cdn.md), [21](../21_design_system_todo.md), [16](../16_testing_strategy.md).

> **Nota:** o storefront base (home/categoria/produto, templates) é desta fase; o **editor 3D + personalização** é a **[Fase 7 — Produtos 3D](./phase-7-3d-products.md)** (modelos gerados pelo lojista via API).

## Definition of Done da fase

- `frontend-storefront` (Next.js) resolve a loja pelo `Host` e renderiza home/categoria/produto (só **imagem** nesta fase).
- 2 templates (`classic`, `modern`); lojista aplica no painel e a loja pública reflete (com invalidação de cache).
- Host inexistente → página "loja não encontrada".

---

## Etapa 1 — Projeto `frontend-storefront` (Next.js) — NOVO

> Decisão fechada (doc [05](../05_frontend_architecture.md)/[10](../10_storefront_and_layouts.md)/[18](../18_open_decisions.md)): Next.js no storefront, Three.js no editor. É um projeto **separado** do `frontend-dashboard`.

- [ ] **Renomear o `frontend/` atual para `frontend-dashboard/`** (o painel Vite): os docs ([05](../05_frontend_architecture.md)/[12](../12_aws_infrastructure_and_deployment.md)) já usam esse nome, mas o diretório ficou como `frontend/` nas Fases 0–2 para evitar churn antes de existir um segundo frontend. Ao introduzir o storefront, renomear o diretório + ajustar `compose*.yml`, Traefik, workspace `bun` (lockfile na raiz) e CI.
- [ ] Criar `frontend-storefront/` (Next.js, TypeScript, Tailwind). Pode reutilizar componentes/cliente OpenAPI e padrões visuais do dashboard, mas com build/deploy próprios. Doc [05](../05_frontend_architecture.md).
- [ ] Resolução por `Host`: middleware/SSR lê o host → chama API pública → obtém `store_id` e dados públicos. Doc [06](../06_multitenancy_and_domains.md)/[10](../10_storefront_and_layouts.md).
- [ ] Página **"loja não encontrada"** amigável (sem vazar dado interno). Doc [06](../06_multitenancy_and_domains.md).
- [ ] Cache público (SSR/ISR + Redis no backend). Doc [13](../13_performance_cache_and_cdn.md).
- [ ] Botão flutuante de **WhatsApp** quando a loja tiver número. Doc [10](../10_storefront_and_layouts.md)/[22](../22_product_customization_3d.md).
- [ ] Compose: serviço `frontend-storefront`; Traefik com **wildcard** `*.${DOMAIN}` → storefront. Doc [03](../03_system_architecture.md)/[12](../12_aws_infrastructure_and_deployment.md).

**Reconciliação:** o template só tem o frontend Vite (dashboard). O storefront Next.js é novo projeto, conforme doc [05](../05_frontend_architecture.md) — sem divergência.

---

## Etapa 2 — Módulo `storefront` (API pública)

> Endpoints públicos, **sem login**, loja resolvida pelo `Host`. Leitura otimizada e cacheada. Doc [10](../10_storefront_and_layouts.md)/[13](../13_performance_cache_and_cdn.md)/[20](../20_api_contracts_todo.md).

- [ ] **Publicação:** `resolve_store_by_host` **já existe** (`P1-TEN-01`, cache-aside `domain:{host}`); falta **filtrar por loja publicada/`active`** (loja `draft`/`paused`/`suspended`/`blocked` → "loja não encontrada", sem vazar) + as chaves de cache de leitura abaixo. Ver Reconciliações.
- [ ] `GET` home (config + destaques), tema ativo, categorias, produtos públicos (paginado), produto por slug, página pública. Doc [20](../20_api_contracts_todo.md).
- [ ] Chaves de cache do doc [13](../13_performance_cache_and_cdn.md): `store:{id}:settings|theme|home|categories|product:{slug}|menu`.
- [ ] Separar consultas públicas das administrativas; evitar joins pesados na vitrine. Doc [07](../07_database_strategy.md)/[13](../13_performance_cache_and_cdn.md).

---

## Etapa 3 — Módulo de conteúdo/layout

### Modelos (com `store_id`, exceto templates globais)
- [ ] `content_theme_templates` (global): `id` (`classic`/`modern`), `name`, `description`, `is_active`, `preview_image_url`. Doc [10](../10_storefront_and_layouts.md)/[07](../07_database_strategy.md).
- [ ] `content_store_theme_settings`: `store_id` (único), `active_template_id`, `banner_image_url`, `headline`, `featured_collection_id`, e campos preparados para o futuro (`primary_color`, `background_color`, `font_family`). **`logo_url` e a descrição da loja vêm de `store_settings` (Fase 1) — não duplicar aqui** (ver Reconciliações). Doc [10](../10_storefront_and_layouts.md).
- [ ] `content_pages`, `content_menus`, `content_menu_items`, `content_banners`. Doc [07](../07_database_strategy.md).

### Rotas/serviço (doc [20](../20_api_contracts_todo.md))
- [ ] Listar templates; obter template ativo; preview; **aplicar template** (salva `active_template_id` + **invalida cache** `store:{id}:theme|home|settings`); atualizar logo/banner/textos/destaque. Doc [10](../10_storefront_and_layouts.md)/[13](../13_performance_cache_and_cdn.md).
- [ ] Índice `content_store_theme_settings.store_id` único; `content_menus.store_id+location`. Doc [07](../07_database_strategy.md).

### Templates no storefront
- [ ] Implementar `classic` e `modern` com HomePage, ProductPage, CategoryPage, CartPage, CheckoutPage (carrinho/checkout completados na Fase 6; o **ProductCustomizer/editor 3D** é a Fase 7). Doc [10](../10_storefront_and_layouts.md).

---

## Etapa 4 — Frontend (painel)
- [ ] Tela **"Layout da Loja"**: ver 2 templates, visualizar preview com dados reais, aplicar; editar logo, banner, headline, descrição e produtos em destaque. Doc [09](../09_merchant_dashboard.md)/[10](../10_storefront_and_layouts.md).

---

## Testes (doc [16](../16_testing_strategy.md))
- [ ] Domínio resolve a loja; host inexistente → "loja não encontrada".
- [ ] Home, produto e categoria carregam (produtos de imagem).
- [ ] Loja inicia com template padrão; aplicar `classic`/`modern` invalida cache e o storefront retorna o template ativo correto.

---

## Reconciliações (registrar aqui)
- **`resolve_store_by_host` já implementado na `P1-TEN-01`** (cache-aside `domain:{host}`, tolera stale). A Fase 3 só adiciona o **filtro de publicação** (resolver apenas loja `active`/publicada; demais → "loja não encontrada") e as chaves de cache de leitura (`store:{id}:settings|theme|home|...`).
- **Sobreposição `store_settings` (Fase 1) × `content_store_theme_settings` (Fase 3):** `store_settings` é a fonte de **contato/negócio** (`public_name`, `description`, `logo_url`, `contact_*`, `whatsapp_number`, `address`); o theme é **só aparência/layout** (template, banner, headline, cores, fonte, coleção em destaque). **`logo_url` e `description` ficam em `store_settings`** — removidos do theme para não duplicar dado.
