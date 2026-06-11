# Fase 3 — Storefront público e layouts

> O **editor 3D + personalização** é a [Fase 7 — Produtos 3D](../phase-7-3d-products.md). Esta fase entrega o **storefront base** (só imagem) + os layouts.

> Objetivo: a loja pública abre em `nomedaloja.loja.club` com o template escolhido; produtos (imagem) e categorias renderizam; o lojista troca o template e a vitrine muda.

Docs de referência: [Fundações & Gargalos](../_foundations-and-bottlenecks.md), [05](../../concepts/05_frontend_architecture.md), [06](../../concepts/06_multitenancy_and_domains.md), [10](../../concepts/10_storefront_and_layouts.md), [13](../../concepts/13_performance_cache_and_cdn.md), [07](../../concepts/07_database_strategy.md), [20](../../concepts/20_api_contracts_todo.md), [21](../../concepts/21_design_system_todo.md), [16](../../concepts/16_testing_strategy.md).

> Visão geral / trilha de alto nível: [`../phase-3-storefront-and-layouts.md`](../phase-3-storefront-and-layouts.md). Este README é o **índice detalhado** das tasks.

## Definition of Done da fase

- `frontend-storefront` (Next.js) resolve a loja pelo `Host` e renderiza home/categoria/produto (só **imagem**).
- 2 templates (`classic`/`modern`); o lojista aplica no painel e a vitrine reflete (com **invalidação de cache**).
- Host inexistente / loja não publicada → **"loja não encontrada"** (sem vazar dado interno).
- Testes de resolução por host, publicação e troca de template passando.

> **Fora desta fase:** editor 3D/personalização e `ProductCustomizer` = [Fase 7](../phase-7-3d-products.md); carrinho/checkout completos = [Fase 6](../phase-6-sell-without-payment.md); deploy AWS = Fase 8.

## Construído sobre as Fases 0–2 (não recriar)

- **Tenancy:** `resolve_store_by_host` (`P1-TEN-01`, cache-aside `domain:{host}`); `get_active_store`/`require_permission`. `store_settings` (Fase 1) é a fonte de **contato/negócio** (`public_name`, `description`, `logo_url`); publicação da loja = `status == active`.
- **Catálogo:** produtos/categorias/imagens públicos vêm do módulo `catalog` (Fase 2) — `ImagePublic` já traz `url`/`variants`.
- **API/infra:** `Page[T]`, `AppError`/envelope (`P1-API-01`); cache Redis (doc 13); `Money`.
- **Frontend:** o painel Vite **`frontend-dashboard`** + a vitrine **`frontend-storefront`** (Next.js, scaffold) no workspace `bun`.

## Pré-requisitos

- **Next.js** (`frontend-storefront`, scaffold + placeholder) e o **painel `frontend-dashboard`** — entregues por **`P3-FE-01`** (✅). Telas reais da vitrine = `P3-SF-02`.

## Tasks

| # | ID | Task | Status | Depende de |
|---|---|---|---|---|
| 1 | [P3-FE-01](./P3-FE-01-frontends-setup.md) | Renomear painel → `frontend-dashboard` + scaffold `frontend-storefront` (Next.js) + compose/Traefik | ✅ done | — |
| 2 | [P3-CONTENT-01](./P3-CONTENT-01-content-models.md) | Módulo `content`: modelos de tema/layout + seed `classic`/`modern` + migration | ✅ done | — |
| 3 | [P3-CONTENT-02](./P3-CONTENT-02-content-service-routes.md) | `content`: serviço/rotas do painel (aplicar template + invalidar cache; editar layout) | ✅ done | P3-CONTENT-01 |
| 4 | [P3-SF-01](./P3-SF-01-storefront-public-api.md) | Módulo `storefront`: API pública de leitura + filtro de publicação + cache | ✅ done | P3-CONTENT-01 |
| 5 | [P3-SF-02](./P3-SF-02-storefront-rendering.md) | Storefront Next.js: host + "não encontrada" + templates `classic`/`modern` + cache | ✅ done | P3-FE-01, P3-SF-01 |
| 6 | [P3-FE-02](./P3-FE-02-layout-screen.md) | Painel: tela "Layout da Loja" | ✅ done | P3-CONTENT-02 |
| 7 | [P3-TPL-01](./P3-TPL-01-template-architecture-aurora.md) | **Arquitetura de templates + Aurora (POC):** resolver/registry + blocos compartilhados + Aurora (navegação) | ✅ done | P3-SF-02, P3-FE-02, P3-LOC-01 |
| 8 | [P3-LOC-01](./P3-LOC-01-store-country-currency.md) | **Localização da loja:** país → moeda/locale/símbolo (deriva automático; `formatPrice` por loja) | ✅ done | — |
| 9 | [P3-TPL-02](./P3-TPL-02-templates-bazar-studio.md) | **Bazar + Studio** — o **teste do contrato** (seções de categoria / sidebar; `category_sections`; `Shell` no contrato) | ✅ done | P3-TPL-01 |
| 10 | [P3-TPL-03](./P3-TPL-03-dashboard-template-picker.md) | **Painel — Layout da loja:** seletor de template (nome + **thumb**) + **upload do banner** + **preview** (Dialog) + defaults apresentáveis | ✅ done | P3-TPL-01 |
| 11 | [P3-TPL-04](./P3-TPL-04-template-settings-schema.md) | **Personalização por template** (schema-driven) — é a **[Fase 5](../phase-5-store-configuration.md)** (config da loja) | → Fase 5 | P3-TPL-02, P3-TPL-03 |
| 12 | [P3-SF-03](./P3-SF-03-storefront-e2e.md) | **E2E do storefront** (Playwright) + regra do gate de CI (e2e de todos os frontends → deploy) | todo | P3-SF-02 |

> **Fase 3 concluída** (tasks 1–10 `done`): os 3 templates (Aurora/Bazar/Studio) + picker + banner + preview — o **contrato está VALIDADO** (3 templates distintos consomem os **mesmos dados + fluxo**). A **personalização por template** (`P3-TPL-04`, schema-driven) é a **[Fase 5](../phase-5-store-configuration.md)** — depende do admin cadastrar templates ([Fase 4](../phase-4-platform-admin.md)). Checkout/confirmação = **[Fase 6](../phase-6-sell-without-payment.md)**.

## Ordem sugerida de execução

```text
P3-FE-01  ∥  P3-CONTENT-01 → P3-CONTENT-02 → P3-FE-02
                         └→ P3-SF-01 → P3-SF-02   (SF-02 também depende de P3-FE-01)

P3-TPL-01 (arquitetura + Aurora) → P3-TPL-02 (Bazar + Studio)  ∥  P3-TPL-03 (painel preview) → P3-TPL-04 (settings por template)
                                  └ checkout/confirmação dos templates → Fase 6
```

## Follow-ups / débitos técnicos

> Item adiado vira checkbox aqui (origem + quando), e também na seção Follow-ups da task.

- [ ] **Smoke do Traefik** (`P3-FE-01`): com o proxy rodando, confirmar `app.`→painel, `api.`→backend, `{loja}.${DOMAIN}`→storefront (o wildcard só foi validado por `compose config`, não no roteamento real).
- [ ] **Lint/test/e2e do `frontend-storefront` nos gates** (`P3-FE-01`) **→ `P3-SF-03`**: pre-commit/CI só cobrem `frontend-dashboard`; a `P3-SF-03` adiciona o e2e do storefront + a regra de gate (e2e de todos os frontends bloqueia deploy — wiring na Fase 9).
- [ ] **Pipeline da imagem do `frontend-storefront`** (`P3-FE-01`): `DOCKER_IMAGE_STOREFRONT` + serviço no `compose.yml` existem, mas o build/push (doc [12](../../concepts/12_aws_infrastructure_and_deployment.md)) não está montado — Fase 8/9.
- [ ] **Dockerfile do storefront single-stage** (`P3-FE-01`): otimizar p/ Next standalone depois.
- [ ] **`bun.lock`** (`P3-FE-01`): confirmar/regerar com o `bun` do usuário antes de commitar (regenerado via `oven/bun:1` 1.3.14).
- [x] **Default de theme settings** (`P3-CONTENT-01`): loja sem row de theme → vitrine usa `classic` — fallback **read-side** feito em `P3-SF-01` (`_theme` retorna `classic` sem criar row); o painel cria via `get_or_create` (`P3-CONTENT-02`).
- [ ] **e2e polui o DB de host** (`P3-CONTENT-01`, infra): e2e (backend Docker) e testes de host compartilham o `loja-club-db` (5442↔5432) → usuários do e2e persistem e quebram o teste de isolamento (`count==1`). → e2e em DB separado **ou** limpeza pós-e2e.
- [ ] **Invalidação de cache falha → stale** (`P3-CONTENT-02`): `cache_delete` roda após o commit; Redis fora → escrita persiste mas cache fica stale (request pode 500). Tratar (best-effort/log) ao entrar o cache de leitura (`P3-SF-01`).
- [ ] **Race de aplicar template** (`P3-CONTENT-02`): PATCH concorrente = last-write-wins (sem lock). Aceitável no V1.
- [ ] **CRUD de páginas/menus/banners no painel** (`P3-CONTENT-02`) **→ [Fase 5](../phase-5-store-configuration.md) (Etapa D)**: rotas/UI + `/pages/*` lê `content_pages`.
- [x] **Cache stale após edição de catálogo** (`P3-SF-01`): resolvido — escritas do `catalog` (produto: create/update/publish/archive/delete; categoria: create/update/delete) **invalidam** `store:{id}:home`/`product:{slug}`/`categories` via `_invalidate_storefront_cache`. **Destaque/publicação refletem na hora** (não esperam o TTL de 5 min).
- [ ] **N+1 de imagens na vitrine** (`P3-SF-01`): `list_products`/home chamam `list_images` por produto — otimizar com query em lote.
- [ ] **Destaque por coleção** (`P3-SF-01`): ligar `featured_collection_id` quando existir link produto↔coleção (hoje destaque = `is_featured`); ao ligar, **pular coleção com `deleted_at`** ao renderizar.
- [ ] **Menu + caches `settings`/`theme` separados** (`P3-SF-01`): home dobra settings+theme; menu não servido (sem CRUD); chaves reservadas.
- [ ] **e2e Playwright do storefront** (`P3-SF-02`): suíte é só painel (:5180); render validado por smoke manual — automatizar host→loja / 404 / home-produto-categoria / troca de template.
- [ ] **API fora → erro amigável** (`P3-SF-02`): adicionar `app/error.tsx` (hoje 500 genérico em falha não-404).
- [ ] **next/image** (`P3-SF-02`): trocar `<img>` por `next/image` + `remotePatterns` do CDN.
- [ ] **API URL server-only** (`P3-SF-02`): SSR usa `NEXT_PUBLIC_API_URL` (exposto ao client) — separar `INTERNAL_API_URL`.
- [ ] **Rebuild do storefront + smoke do Traefik** (`P3-SF-02`, infra): `docker compose up -d --build frontend-storefront` + abrir a vitrine em `{loja}.localhost` via Traefik.
- [ ] **Picker de coleção em destaque** (`P3-FE-02`): `featured_collection_id` é UUID cru — select quando houver endpoint de listar coleções (+ vitrine renderizar destaque por coleção, ver `P3-SF-01`).
- [ ] **Preview visual** (`P3-FE-02`) **→ [Fase 5](../phase-5-store-configuration.md) (Etapa C)**: preview navegável (loja-demo) abre a vitrine com o template.
- [ ] **i18n-readiness do storefront** (`P3-SF-02`, `INV-G7`): strings estão **pt-BR inline** — extrair para módulo locale-aware usando `Store.locale` (doc 10 + INV-G7 pedem i18n-ready na Fase 3).
- [ ] **Produto: variações + disponibilidade + relacionados** (`P3-SF-01`/`P3-SF-02`): doc 10 §"Página de produto" — `SF-01` retornar variações/estoque e `SF-02` exibir (hoje só imagem/nome/preço/descrição).
- [ ] **Categoria: paginação-UI + filtros + ordenação** (`P3-SF-02`): doc 10 §"Página de categoria" — a API já pagina (`skip/limit`); faltam a UI de paginação + filtros/ordenação.
- [ ] **Home: contato + links sociais** (`P3-SF-02`): doc 10 §"Componentes da home" — além do WhatsApp, expor contato/links sociais (menu configurável já coberto pelos follow-ups de menu).
- [ ] **Produto: ação de compra (carrinho)** (`P3-SF-02` → Fase 6): a página de produto é **informativa** no V1 (sem botão de compra); o **carrinho** entra na Fase 6. O WhatsApp da vitrine é só o **botão flutuante** de contato (não há "comprar pelo WhatsApp").
- [x] **Layout/design da vitrine — 1ª passada** (`P3-SF-02`): redesenhada com cara de ecommerce — header sticky (logo/inicial + nav em pills), hero (banner no `modern`), cards com hover, galeria de produto interativa, tipografia **Inter**, espaçamento, estados vazios, responsivo e cores do tema via `--primary`/bg/fonte. **Resta:** menu mobile (hamburguer), busca e refinos do [doc 21 — Design System](../../concepts/21_design_system_todo.md). (O salto pra **templates profissionais** é a `P3-TPL-01`.)
- [x] **Admin (loja.club) pra cadastrar templates** (`P3-TPL-03`) **→ `P4-ADMIN-03`** ✅: CRUD de templates + thumbnail no CDN + schema read-only *(import de imagens / loja-demo / preview navegável = [Fase 5](../phase-5-store-configuration.md))*.
- [ ] **Preview ao vivo no painel** (`P3-TPL-03`) **→ [Fase 5](../phase-5-store-configuration.md) (Etapa 4)**: preview navegável (loja-demo por template) em outra aba. (Render inline com os dados da própria loja segue futuro.)
- [ ] **Compatibilidade 3D dos templates** (`P3-TPL-01`/`P3-TPL-02` → Fase 7): reservar o **slot** do editor 3D na página de produto de **todos** os templates.
- [ ] **Checkout + confirmação dos templates** (`P3-TPL-01`/`P3-TPL-02` → **Fase 6**): as telas de **checkout single-page + confirmação** dos 3 templates **já estão desenhadas** (`docs/design/templates/<nome>/`); ficam **funcionais na Fase 6** (carrinho/pedido).
- [ ] **Busca real na vitrine** (`P3-TPL-02`): a barra de busca da topbar do **Studio** é placeholder; busca real é pós-V1.
- [ ] **Filtros avançados / faceted** (`P3-TPL-02`): a sidebar do **Studio** tem filtros simples/visuais; faceted search é pós-V1.
- [ ] **Home 100% configurável (blocos)** (`P3-TPL-02`): o lojista liga/desliga blocos da home; V1 = defaults por template + ordem das categorias.
- [ ] **Carrossel multi-banner na home** (`P3-TPL-01` → `P3-TPL-02`): o hero usa `theme.banner_image_url` único; carrossel (2+ banners) precisa a lista de banners na API pública.
- [ ] **Imagens de categoria** (`P3-TPL-01`): a faixa de categorias usa a inicial do nome (o model `Category` não tem imagem ainda).
- [x] **`preview_image_url` dos templates** (`P3-TPL-01`/`P3-TPL-03`): resolvido — previews **seedados** (`/templates/<id>_preview.png`) servidos do `public/` do dashboard (hardcoded). **CloudFront** feito na `P4-TPL-02` (thumbnail upload → CDN).
- [x] **`formatPrice` por locale da loja** (`P3-LOC-01`): resolvido — a vitrine recebe o `locale` da loja e formata o preço com o símbolo certo por loja (R$ / $ / €).
- [ ] **Multi-moeda / câmbio** (`P3-LOC-01`): uma loja vende em **uma** moeda no V1; multi-moeda + conversão é futuro.
- [ ] **Editar categorias de um produto** (catálogo): criar produto **exige** `category_ids` (≥1, com criação inline de categoria no form); **editar** as categorias ainda não — falta `ProductUpdate` aceitar `category_ids` + expor as categorias atuais no `ProductPublic`/form de edição.
- [x] **`classic`/`modern` removidos** (P3-TPL): templates legados saíram do seed/DB/resolver; **default = `aurora`**; `templates/base` + `StoreShell` removidos da vitrine.
- [x] **Aurora portado FIEL ao template** (`P3-TPL-01`): barra de anúncio, header com 3 ícones, **cart drawer** deslizante + carrinho client (`lib/cart.tsx`, localStorage), cards com overlay "Adicionar", footer escuro `bg-brand-900`, FontAwesome, páginas `/checkout` · `/order-confirmation` · `/account` · `/pages/[slug]`. Build + biome + smoke ✓.
- [x] **Bazar + Studio portados FIEL** (`P3-TPL-02`): Bazar (indigo/rose + Plus Jakarta Sans, home com **seções de categoria**, card marketplace) + Studio (black/gray + **sidebar** catálogo). Backend `StorefrontHome.category_sections`. **Contrato validado** (smoke real dos 3). Build/biome/cov ✓.
- [ ] **Conteúdo de chrome editável** (`P3-TPL-04`) **→ é a [Fase 5](../phase-5-store-configuration.md)** (schema-driven): anúncio, hero, editorial, trust, footer e subtítulo do card editáveis pelo lojista.
- [ ] **FontAwesome via CDN** (`P3-TPL-01`): a vitrine carrega FA por CDN (`layout.tsx`); empacotar local pra produção (offline + performance).
- [ ] **Tema da loja no Aurora** (`P3-TPL-01`): o Aurora usa a paleta fixa `brand` do template; aplicar cores/fonte do lojista (`theme.primary_color` etc.) é futuro.
- [x] **Páginas avulsas via resolver** (`P3-TPL-02`): resolvido — `Template` ganhou `Shell`; `/pages/*` · `/account` · `/checkout` · `/order-confirmation` resolvem o **shell do template ativo**.
- [ ] **Carrinho/checkout reais** (`P3-TPL-01` → Fase 6): o carrinho é client (localStorage) e checkout/pedido são telas de exemplo; o pedido real (sem pagamento) é a Fase 6.
- [ ] **Sidebar do Studio no mobile** (`P3-TPL-02`): hoje `lg:block`; no mobile o catálogo vem por `/products` — drawer mobile é follow-up.
- [ ] **`CheckoutView` compartilhado** (`P3-TPL-02`): mora em `templates/aurora/` mas é usado pelos 3; mover pra local neutro.
- [x] **Banner enviável + preview por imagem** (`P3-TPL-03`): upload do banner via `media` → `banner_image_url`; preview = Dialog com a imagem; thumbnails na lista de templates.
- [ ] **`previewLayout` (backend) sem uso na UI** (`P3-TPL-03`) **→ [Fase 5](../phase-5-store-configuration.md) (Etapa 4)**: remover o endpoint (o preview navegável o substitui).
- [ ] **Permissão do upload do banner** (`P3-TPL-03`) **→ [Fase 5](../phase-5-store-configuration.md) (Etapa 2)**: uploads de layout gated em `layout.update` (hoje `catalog.product.update`).
- [ ] **Páginas institucionais via `content_pages`** (`P3-TPL-03`) **→ [Fase 5](../phase-5-store-configuration.md) (Etapa 5)**: `/pages/*` lê `content_pages` + CRUD no painel.
