# Fase 3 — Storefront público e layouts

> O **editor 3D + personalização** é a [Fase 5 — Produtos 3D](../phase-5-3d-products.md). Esta fase entrega o **storefront base** (só imagem) + os layouts.

> Roadmap: Etapas 7–8. Objetivo: a loja pública abre em `nomedaloja.loja.club` com o template escolhido; produtos (imagem) e categorias renderizam; o lojista troca o template e a vitrine muda.

Docs de referência: [Fundações & Gargalos](../_foundations-and-bottlenecks.md), [05](../../05_frontend_architecture.md), [06](../../06_multitenancy_and_domains.md), [10](../../10_storefront_and_layouts.md), [13](../../13_performance_cache_and_cdn.md), [07](../../07_database_strategy.md), [20](../../20_api_contracts_todo.md), [21](../../21_design_system_todo.md), [16](../../16_testing_strategy.md).

> Visão geral / trilha de alto nível: [`../phase-3-storefront-and-layouts.md`](../phase-3-storefront-and-layouts.md). Este README é o **índice detalhado** das tasks.

## Definition of Done da fase

- `frontend-storefront` (Next.js) resolve a loja pelo `Host` e renderiza home/categoria/produto (só **imagem**).
- 2 templates (`classic`/`modern`); o lojista aplica no painel e a vitrine reflete (com **invalidação de cache**).
- Host inexistente / loja não publicada → **"loja não encontrada"** (sem vazar dado interno).
- Testes de resolução por host, publicação e troca de template passando.

> **Fora desta fase:** editor 3D/personalização e `ProductCustomizer` = [Fase 5](../phase-5-3d-products.md); carrinho/checkout completos = [Fase 4](../phase-4-sell-without-payment.md); deploy AWS = Fase 6.

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
| 7 | [P3-TPL-01](./P3-TPL-01-rich-templates-spec.md) | **Arquitetura de templates + Aurora (POC):** resolver/registry + blocos compartilhados + Aurora (navegação) | todo | P3-SF-02, P3-FE-02, P3-LOC-01 |
| 8 | [P3-LOC-01](./P3-LOC-01-store-country-currency.md) | **Localização da loja:** país → moeda/locale/símbolo (deriva automático; `formatPrice` por loja) | ✅ done | — |
| 9 | [P3-TPL-02](./P3-TPL-02-templates-bazar-studio.md) | **Bazar + Studio (navegação)** — o teste do contrato (seções de categoria / sidebar) + dado produtos-por-categoria | todo | P3-TPL-01 |
| 10 | [P3-TPL-03](./P3-TPL-03-dashboard-template-picker.md) | **Painel: seletor de template com preview** (imagem cadastrada) | todo | P3-TPL-01 |

> **Base da Fase 3 completa** (tasks 1–6 `done`) + `P3-LOC-01` `done`. Os **templates profissionais** (designs prontos em `docs/design/templates/`, guia em [`README.md`](../../design/templates/README.md)) entram em **3 tasks**: **`P3-TPL-01`** (arquitetura + Aurora POC), **`P3-TPL-02`** (Bazar + Studio — o **teste do contrato**) e **`P3-TPL-03`** (painel com preview). O **checkout/confirmação** dos templates (já desenhados) fica pra **[Fase 4](../phase-4-sell-without-payment.md)** (carrinho/pedido).

## Ordem sugerida de execução

```text
P3-FE-01  ∥  P3-CONTENT-01 → P3-CONTENT-02 → P3-FE-02
                         └→ P3-SF-01 → P3-SF-02   (SF-02 também depende de P3-FE-01)

P3-TPL-01 (arquitetura + Aurora) → P3-TPL-02 (Bazar + Studio)  ∥  P3-TPL-03 (painel preview)
                                  └ checkout/confirmação dos templates → Fase 4
```

## Follow-ups / débitos técnicos

> Item adiado vira checkbox aqui (origem + quando), e também na seção Follow-ups da task.

- [ ] **Smoke do Traefik** (`P3-FE-01`): com o proxy rodando, confirmar `app.`→painel, `api.`→backend, `{loja}.${DOMAIN}`→storefront (o wildcard só foi validado por `compose config`, não no roteamento real).
- [ ] **Lint/test do `frontend-storefront` nos gates** (`P3-FE-01`): pre-commit/CI só cobrem `frontend-dashboard` — plugar quando o storefront tiver código real (`P3-SF-02`).
- [ ] **Pipeline da imagem do `frontend-storefront`** (`P3-FE-01`): `DOCKER_IMAGE_STOREFRONT` + serviço no `compose.yml` existem, mas o build/push (doc [12](../../12_aws_infrastructure_and_deployment.md)) não está montado — Fase 6/7.
- [ ] **Dockerfile do storefront single-stage** (`P3-FE-01`): otimizar p/ Next standalone depois.
- [ ] **`bun.lock`** (`P3-FE-01`): confirmar/regerar com o `bun` do usuário antes de commitar (regenerado via `oven/bun:1` 1.3.14).
- [x] **Default de theme settings** (`P3-CONTENT-01`): loja sem row de theme → vitrine usa `classic` — fallback **read-side** feito em `P3-SF-01` (`_theme` retorna `classic` sem criar row); o painel cria via `get_or_create` (`P3-CONTENT-02`).
- [ ] **e2e polui o DB de host** (`P3-CONTENT-01`, infra): e2e (backend Docker) e testes de host compartilham o `loja-club-db` (5442↔5432) → usuários do e2e persistem e quebram o teste de isolamento (`count==1`). → e2e em DB separado **ou** limpeza pós-e2e.
- [ ] **Invalidação de cache falha → stale** (`P3-CONTENT-02`): `cache_delete` roda após o commit; Redis fora → escrita persiste mas cache fica stale (request pode 500). Tratar (best-effort/log) ao entrar o cache de leitura (`P3-SF-01`).
- [ ] **Race de aplicar template** (`P3-CONTENT-02`): PATCH concorrente = last-write-wins (sem lock). Aceitável no V1.
- [ ] **CRUD de páginas/menus/banners no painel** (`P3-CONTENT-02`): modelos existem, faltam rotas/UI — adicionar quando a UI precisar.
- [ ] **Cache stale após edição de catálogo** (`P3-SF-01`): escritas do `catalog` não invalidam `store:{id}:categories|product:{slug}|home` (só o TTL de 5 min). Adicionar invalidação no `catalog` antes da vitrine ir pra produção.
- [ ] **N+1 de imagens na vitrine** (`P3-SF-01`): `list_products`/home chamam `list_images` por produto — otimizar com query em lote.
- [ ] **Destaque por coleção** (`P3-SF-01`): ligar `featured_collection_id` quando existir link produto↔coleção (hoje destaque = `is_featured`); ao ligar, **pular coleção com `deleted_at`** ao renderizar.
- [ ] **Menu + caches `settings`/`theme` separados** (`P3-SF-01`): home dobra settings+theme; menu não servido (sem CRUD); chaves reservadas.
- [ ] **e2e Playwright do storefront** (`P3-SF-02`): suíte é só painel (:5180); render validado por smoke manual — automatizar host→loja / 404 / home-produto-categoria / troca de template.
- [ ] **API fora → erro amigável** (`P3-SF-02`): adicionar `app/error.tsx` (hoje 500 genérico em falha não-404).
- [ ] **next/image** (`P3-SF-02`): trocar `<img>` por `next/image` + `remotePatterns` do CDN.
- [ ] **API URL server-only** (`P3-SF-02`): SSR usa `NEXT_PUBLIC_API_URL` (exposto ao client) — separar `INTERNAL_API_URL`.
- [ ] **Rebuild do storefront + smoke do Traefik** (`P3-SF-02`, infra): `docker compose up -d --build frontend-storefront` + abrir a vitrine em `{loja}.localhost` via Traefik.
- [ ] **Picker de coleção em destaque** (`P3-FE-02`): `featured_collection_id` é UUID cru — select quando houver endpoint de listar coleções (+ vitrine renderizar destaque por coleção, ver `P3-SF-01`).
- [ ] **Preview visual** (`P3-FE-02`): hoje o preview é aviso de dados (template aplicado); evoluir para abrir a vitrine com o template previsto / render visual.
- [ ] **i18n-readiness do storefront** (`P3-SF-02`, `INV-G7`): strings estão **pt-BR inline** — extrair para módulo locale-aware usando `Store.locale` (doc 10 + INV-G7 pedem i18n-ready na Fase 3).
- [ ] **Produto: variações + disponibilidade + relacionados** (`P3-SF-01`/`P3-SF-02`): doc 10 §"Página de produto" — `SF-01` retornar variações/estoque e `SF-02` exibir (hoje só imagem/nome/preço/descrição).
- [ ] **Categoria: paginação-UI + filtros + ordenação** (`P3-SF-02`): doc 10 §"Página de categoria" — a API já pagina (`skip/limit`); faltam a UI de paginação + filtros/ordenação.
- [ ] **Home: contato + links sociais** (`P3-SF-02`): doc 10 §"Componentes da home" — além do WhatsApp, expor contato/links sociais (menu configurável já coberto pelos follow-ups de menu).
- [ ] **Produto: ação de compra (carrinho)** (`P3-SF-02` → Fase 4): a página de produto é **informativa** no V1 (sem botão de compra); o **carrinho** entra na Fase 4. O WhatsApp da vitrine é só o **botão flutuante** de contato (não há "comprar pelo WhatsApp").
- [x] **Layout/design da vitrine — 1ª passada** (`P3-SF-02`): redesenhada com cara de ecommerce — header sticky (logo/inicial + nav em pills), hero (banner no `modern`), cards com hover, galeria de produto interativa, tipografia **Inter**, espaçamento, estados vazios, responsivo e cores do tema via `--primary`/bg/fonte. **Resta:** menu mobile (hamburguer), busca e refinos do [doc 21 — Design System](../../21_design_system_todo.md). (O salto pra **templates profissionais** é a `P3-TPL-01`.)
- [ ] **Admin (loja.club) pra cadastrar templates** (`P3-TPL-03` → Fase 7/admin): por ora os templates entram via seed/código; a tela de admin (nome/descrição/`preview_image_url`/ativar) é futura.
- [ ] **Preview ao vivo no painel** (`P3-TPL-03`): hoje o lojista escolhe o template pela **imagem cadastrada**; render real da loja com o template é futuro.
- [ ] **Compatibilidade 3D dos templates** (`P3-TPL-01`/`P3-TPL-02` → Fase 5): reservar o **slot** do editor 3D na página de produto de **todos** os templates.
- [ ] **Checkout + confirmação dos templates** (`P3-TPL-01`/`P3-TPL-02` → **Fase 4**): as telas de **checkout single-page + confirmação** dos 3 templates **já estão desenhadas** (`docs/design/templates/<nome>/`); ficam **funcionais na Fase 4** (carrinho/pedido).
- [ ] **Busca real na vitrine** (`P3-TPL-02`): a barra de busca da topbar do **Studio** é placeholder; busca real é pós-V1.
- [ ] **Filtros avançados / faceted** (`P3-TPL-02`): a sidebar do **Studio** tem filtros simples/visuais; faceted search é pós-V1.
- [ ] **Home 100% configurável (blocos)** (`P3-TPL-02`): o lojista liga/desliga blocos da home; V1 = defaults por template + ordem das categorias.
- [x] **`formatPrice` por locale da loja** (`P3-LOC-01`): resolvido — a vitrine recebe o `locale` da loja e formata o preço com o símbolo certo por loja (R$ / $ / €).
- [ ] **Multi-moeda / câmbio** (`P3-LOC-01`): uma loja vende em **uma** moeda no V1; multi-moeda + conversão é futuro.
