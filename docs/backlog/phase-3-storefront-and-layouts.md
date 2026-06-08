# Fase 3 — Storefront público e layouts

> Roadmap: Etapas 7–8. Objetivo: loja pública abre em `nomedaloja.loja.club` com o template escolhido; produtos e categorias renderizam; produto personalizável abre o editor 3D que salva a sessão; lojista troca o template e a loja pública muda.

Docs de referência: [05](../05_frontend_architecture.md), [10](../10_storefront_and_layouts.md), [22](../22_product_customization_3d.md), [13](../13_performance_cache_and_cdn.md), [21](../21_design_system_todo.md), [16](../16_testing_strategy.md).

> **Nota:** o storefront base (home/categoria/produto, templates) é desta fase; o **editor 3D + personalização** é a **[Fase 5 — Produtos 3D](./phase-5-3d-products.md)** (modelos gerados pelo lojista via API).

## Definition of Done da fase

- `frontend-storefront` (Next.js) resolve a loja pelo `Host` e renderiza home/categoria/produto.
- Produto `customizable_3d` abre editor Three.js: upload de arte, cor, texto, posição/escala/rotação, preview, autosave e aprovação antes do carrinho.
- 2 templates (`classic`, `modern`); lojista aplica no painel e a loja pública reflete (com invalidação de cache).
- Host inexistente → página "loja não encontrada".

---

## Etapa 7 — Projeto `frontend-storefront` (Next.js) — NOVO

> Decisão fechada (doc [05](../05_frontend_architecture.md)/[10](../10_storefront_and_layouts.md)/[18](../18_open_decisions.md)): Next.js no storefront, Three.js no editor. É um projeto **separado** do `frontend-dashboard`.

- [ ] Criar `frontend-storefront/` (Next.js, TypeScript, Tailwind). Pode reutilizar componentes/cliente OpenAPI e padrões visuais do dashboard, mas com build/deploy próprios. Doc [05](../05_frontend_architecture.md).
- [ ] Resolução por `Host`: middleware/SSR lê o host → chama API pública → obtém `store_id` e dados públicos. Doc [06](../06_multitenancy_and_domains.md)/[10](../10_storefront_and_layouts.md).
- [ ] Página **"loja não encontrada"** amigável (sem vazar dado interno). Doc [06](../06_multitenancy_and_domains.md).
- [ ] Cache público (SSR/ISR + Redis no backend). Doc [13](../13_performance_cache_and_cdn.md).
- [ ] Botão flutuante de **WhatsApp** quando a loja tiver número. Doc [10](../10_storefront_and_layouts.md)/[22](../22_product_customization_3d.md).
- [ ] Compose: serviço `frontend-storefront`; Traefik com **wildcard** `*.${DOMAIN}` → storefront. Doc [03](../03_system_architecture.md)/[12](../12_aws_infrastructure_and_deployment.md).

**Reconciliação:** o template só tem o frontend Vite (dashboard). O storefront Next.js é novo projeto, conforme doc [05](../05_frontend_architecture.md) — sem divergência.

---

## Etapa 7 — Módulo `storefront` (API pública)

> Endpoints públicos, **sem login**, loja resolvida pelo `Host`. Leitura otimizada e cacheada. Doc [10](../10_storefront_and_layouts.md)/[13](../13_performance_cache_and_cdn.md)/[20](../20_api_contracts_todo.md).

- [ ] **Publicação:** `resolve_store_by_host` **já existe** (`P1-TEN-01`, cache-aside `domain:{host}`); falta **filtrar por loja publicada/`active`** (loja `draft`/`paused`/`suspended`/`blocked` → "loja não encontrada", sem vazar) + as chaves de cache de leitura abaixo. Ver Reconciliações.
- [ ] `GET` home (config + destaques), tema ativo, categorias, produtos públicos (paginado), produto por slug, página pública. Doc [20](../20_api_contracts_todo.md).
- [ ] Chaves de cache do doc [13](../13_performance_cache_and_cdn.md): `store:{id}:settings|theme|home|categories|product:{slug}|menu`.
- [ ] Separar consultas públicas das administrativas; evitar joins pesados na vitrine. Doc [07](../07_database_strategy.md)/[13](../13_performance_cache_and_cdn.md).

---

## Etapa 7 — Editor de personalização 3D (storefront)

> Experiência interativa da página de produto, não um app à parte. Doc [22](../22_product_customization_3d.md)/[10](../10_storefront_and_layouts.md).

- [ ] Carregar o GLB do modelo+versão **do lojista** (gerado via API, servido por CDN).
- [ ] Upload de arte/imagem pelo cliente; aplicar como textura.
- [ ] Texto (nome/frase) com fonte, cor, tamanho dentro da área imprimível.
- [ ] Cor do produto quando o modelo permitir.
- [ ] Mover/escala/rotação dentro da área imprimível; preview em tempo real.
- [ ] **Autosave** da sessão (chama `product_customization` API).
- [ ] **Aprovação visual** obrigatória antes de adicionar ao carrinho (gera snapshot aprovado).
- [ ] Restaurar sessão pelo cookie `guest_session_id` ao voltar. Doc [22](../22_product_customization_3d.md)/[23](../23_customer_identity_and_guest_checkout.md).
- [ ] Aviso de baixa resolução quando possível. Doc [22](../22_product_customization_3d.md).
- [ ] Estados do editor conforme doc [21](../21_design_system_todo.md).

---

## Etapa 8 — Módulo de conteúdo/layout

### Modelos (com `store_id`, exceto templates globais)
- [ ] `content_theme_templates` (global): `id` (`classic`/`modern`), `name`, `description`, `is_active`, `preview_image_url`. Doc [10](../10_storefront_and_layouts.md)/[07](../07_database_strategy.md).
- [ ] `content_store_theme_settings`: `store_id` (único), `active_template_id`, `banner_image_url`, `headline`, `featured_collection_id`, e campos preparados para o futuro (`primary_color`, `background_color`, `font_family`). **`logo_url` e a descrição da loja vêm de `store_settings` (Fase 1) — não duplicar aqui** (ver Reconciliações). Doc [10](../10_storefront_and_layouts.md).
- [ ] `content_pages`, `content_menus`, `content_menu_items`, `content_banners`. Doc [07](../07_database_strategy.md).

### Rotas/serviço (doc [20](../20_api_contracts_todo.md))
- [ ] Listar templates; obter template ativo; preview; **aplicar template** (salva `active_template_id` + **invalida cache** `store:{id}:theme|home|settings`); atualizar logo/banner/textos/destaque. Doc [10](../10_storefront_and_layouts.md)/[13](../13_performance_cache_and_cdn.md).
- [ ] Índice `content_store_theme_settings.store_id` único; `content_menus.store_id+location`. Doc [07](../07_database_strategy.md).

### Templates no storefront
- [ ] Implementar `classic` e `modern` com HomePage, ProductPage, ProductCustomizer, CategoryPage, CartPage, CheckoutPage (carrinho/checkout completados na Fase 4). Doc [10](../10_storefront_and_layouts.md).

---

## Etapa 8 — Frontend (painel)
- [ ] Tela **"Layout da Loja"**: ver 2 templates, visualizar preview com dados reais, aplicar; editar logo, banner, headline, descrição e produtos em destaque. Doc [09](../09_merchant_dashboard.md)/[10](../10_storefront_and_layouts.md).

---

## Etapa 7/8 — Testes (doc [16](../16_testing_strategy.md))
- [ ] Domínio resolve a loja; host inexistente → "loja não encontrada".
- [ ] Home, produto e categoria carregam; editor 3D carrega só em produto personalizável.
- [ ] Sessão de personalização é retomada pelo cookie.
- [ ] Loja inicia com template padrão; aplicar `classic`/`modern` invalida cache e o storefront retorna o template ativo correto.

---

## Reconciliações (registrar aqui)
- **`resolve_store_by_host` já implementado na `P1-TEN-01`** (cache-aside `domain:{host}`, tolera stale). A Fase 3 só adiciona o **filtro de publicação** (resolver apenas loja `active`/publicada; demais → "loja não encontrada") e as chaves de cache de leitura (`store:{id}:settings|theme|home|...`).
- **Sobreposição `store_settings` (Fase 1) × `content_store_theme_settings` (Fase 3):** `store_settings` é a fonte de **contato/negócio** (`public_name`, `description`, `logo_url`, `contact_*`, `whatsapp_number`, `address`, `is_published`); o theme é **só aparência/layout** (template, banner, headline, cores, fonte, coleção em destaque). **`logo_url` e `description` ficam em `store_settings`** — removidos do theme para não duplicar dado.
