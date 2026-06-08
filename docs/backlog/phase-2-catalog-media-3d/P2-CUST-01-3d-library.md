---
id: P2-CUST-01
title: Biblioteca 3D global (customization_3d_models + versões) + seed + listagem
phase: 2
etapa: "Etapa 6 — Personalização 3D"
area: CUST
status: todo
depends_on: []
blocks: [P2-CUST-02]
tests: [integration]
---

# P2-CUST-01 — Biblioteca 3D global

## Contexto
Os modelos 3D são **globais** (criados/publicados pela Loja Club); o lojista só vincula (doc [22](../../22_product_customization_3d.md)). Esta task entrega as **tabelas globais** + um **seed mínimo** (caneca/squeeze/camisa) e a listagem. O admin de modelos (CRUD) é Fase 6; aqui o seed via `init_db` cobre a V1.

## Docs de referência
- [22 — Product Customization 3D](../../22_product_customization_3d.md) (modelos, parâmetros, limites)
- [07 — Database Strategy](../../07_database_strategy.md) (`customization_3d_models`/`_versions`)
- [13 — Performance/Cache/CDN](../../13_performance_cache_and_cdn.md) (GLB otimizado, cache por versão)

## Escopo (o que ENTRA)
- **Modelos globais (sem `store_id`):**
  - `customization_3d_models`: `name`, `category`, `status` (publicado/despublicado), descrição.
  - `customization_3d_model_versions`: `model_id`, `glb_key`/`glb_url` (CDN), `params`/áreas personalizáveis (json), **limites** (área imprimível, tipos aceitos, tamanho máx) e `status`.
- **Enums:** status de modelo/versão.
- **Seed mínimo idempotente** (via `init_db`): caneca, squeeze, camisa — com **GLB placeholder** até os arquivos reais existirem (conteúdo Loja Club).
- **Listagem:** `GET` modelos publicados (consumido pelo produto/painel e, na Fase 3, pelo storefront).
- Migration + `models_registry`.

## Fora de escopo (o que NÃO entra)
- Config por loja/produto + sessões → `P2-CUST-02`/`P2-CUST-03`. CRUD admin de modelos → Fase 6 (`frontend-admin`). GLBs reais → conteúdo Loja Club.

## Arquivos a criar/alterar
- `backend/app/modules/product_customization/models.py` (globais)/`enums.py`/`schemas.py`/`repositories.py` (seed)/`routes.py` (listar).
- `backend/app/core/db.py` (`init_db` chama o seed). Migration + `models_registry`.

## Passos
1. Tabelas globais + enums + migration.
2. Seed idempotente (modelos + 1 versão placeholder cada).
3. Endpoint de listagem dos publicados.

## Testes
> Fundações §10.

- **Cobrir:** seed idempotente (rodar 2x não duplica); listagem traz só publicados; versão carrega limites/params.

## Definition of Done
- [ ] Tabelas globais 3D + seed mínimo idempotente (caneca/squeeze/camisa).
- [ ] Endpoint lista modelos publicados.
- [ ] Migration aplica do zero; testes verdes.
- [ ] Itens adiados varridos → Follow-ups + README (ou "nenhum").

## Notas / Reconciliações
- **GLBs reais** são conteúdo da Loja Club; o seed usa placeholders até lá (registrar follow-up).

## Follow-ups
- (preencher)
