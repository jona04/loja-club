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

- **Tenancy:** `resolve_store_by_host` (`P1-TEN-01`, cache-aside `domain:{host}`); `get_active_store`/`require_permission`. `store_settings` (Fase 1) é a fonte de **contato/negócio** (`public_name`, `description`, `logo_url`, `is_published`).
- **Catálogo:** produtos/categorias/imagens públicos vêm do módulo `catalog` (Fase 2) — `ImagePublic` já traz `url`/`variants`.
- **API/infra:** `Page[T]`, `AppError`/envelope (`P1-API-01`); cache Redis (doc 13); `Money`.
- **Frontend:** o painel Vite existente (a renomear para `frontend-dashboard`).

## Pré-requisitos (o que ainda falta)

- **Next.js** (novo projeto `frontend-storefront`) — decisão fechada (doc [05](../../05_frontend_architecture.md)/[18](../../18_open_decisions.md)).
- Renomear `frontend/` → `frontend-dashboard/` (`P3-FE-01`).

## Tasks

| # | ID | Task | Status | Depende de |
|---|---|---|---|---|
| 1 | [P3-FE-01](./P3-FE-01-frontends-setup.md) | Renomear painel → `frontend-dashboard` + scaffold `frontend-storefront` (Next.js) + compose/Traefik | todo | — |
| 2 | [P3-CONTENT-01](./P3-CONTENT-01-content-models.md) | Módulo `content`: modelos de tema/layout + seed `classic`/`modern` + migration | todo | — |
| 3 | [P3-CONTENT-02](./P3-CONTENT-02-content-service-routes.md) | `content`: serviço/rotas do painel (aplicar template + invalidar cache; editar layout) | todo | P3-CONTENT-01 |
| 4 | [P3-SF-01](./P3-SF-01-storefront-public-api.md) | Módulo `storefront`: API pública de leitura + filtro de publicação + cache | todo | P3-CONTENT-01 |
| 5 | [P3-SF-02](./P3-SF-02-storefront-rendering.md) | Storefront Next.js: host + "não encontrada" + templates `classic`/`modern` + cache | todo | P3-FE-01, P3-SF-01 |
| 6 | [P3-FE-02](./P3-FE-02-layout-screen.md) | Painel: tela "Layout da Loja" | todo | P3-CONTENT-02 |

## Ordem sugerida de execução

```text
P3-FE-01  ∥  P3-CONTENT-01 → P3-CONTENT-02 → P3-FE-02
                         └→ P3-SF-01 → P3-SF-02   (SF-02 também depende de P3-FE-01)
```

## Follow-ups / débitos técnicos

> Item adiado vira checkbox aqui (origem + quando), e também na seção Follow-ups da task.

- (nenhum aberto — a fase ainda não começou)
