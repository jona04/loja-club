---
id: P5-DEMO-02
title: Loja-demo por template (<id>-demo do demo.json)
phase: 5
etapa: "Etapa 4 — Loja-demo + import de assets"
area: DEMO
status: done
depends_on: [P5-DEMO-01]
blocks: [P5-PREV-01]
tests: [integration]
---

# P5-DEMO-02 — Loja-demo por template

## Contexto
Cada template tem uma **loja-demo própria** (`aurora-demo`/`bazar-demo`/`studio-demo`): uma `store` real, com o template aplicado + catálogo/imagens/textos do `demo.json` (= o design). É o **preview navegável** e o **modelo** que o lojista copia.

## Docs de referência
- [26 — Sistema de templates](../../concepts/26_template_system.md) (§"A loja-demo (por template)")
- [27 — Guia de autoria](../../concepts/27_template_authoring_guide.md) (Passo 6)

## Escopo (o que ENTRA)
- **Monta a loja-demo** de cada template (`<id>-demo`): `store` real com `active_template_id = <id>` + catálogo do `demo.json` (imagens **já no CDN** via `P5-DEMO-01`). **Idempotente**.
- **Reusa tudo** (store/catalog/storefront/settings) — zero render especial; a loja-demo é servida como qualquer vitrine.
- **Aurora/Bazar/Studio** ganham sua loja-demo (carga do `docs/design/`, pelo **mesmo caminho** de um template futuro).

## Fora de escopo (o que NÃO entra)
- O `import_assets` em si: `P5-DEMO-01`.
- O painel abrir o preview navegável: `P5-PREV-01`.

## Arquivos a criar/alterar
- `backend/app/modules/.../seed_template_demo_store` (criar) — cria/atualiza a loja-demo a partir do `demo.json`.

## Passos
1. A partir do `demo.json` (+ imagens no CDN), cria/atualiza a `store` `<id>-demo` (categorias/produtos publicados), `active_template_id = <id>`.
2. Idempotente (re-rodar não duplica).
3. Roda pros 3 templates.

## Testes
- **Níveis:** integração.
- **Quando escrever:** durante.
- **Cobrir:** integração — monta a loja-demo (catálogo do demo, template ativo), idempotente; a vitrine serve a loja-demo como qualquer loja.

## Definition of Done
- [x] `<id>-demo` montada pros 3 templates (`aurora-demo`/`bazar-demo`/`studio-demo` no db de dev): `store` ativa + `active_template_id` + catálogo do `demo.json` (categorias/produtos **publicados** + imagens no CDN via `media_files`) + host `{slug}.localhost`.
- [x] **Idempotente** (todo registro casado por chave natural antes de inserir; re-rodar não duplica).
- [x] **Servida pela vitrine** como loja normal (teste: `GET /storefront/home` com `host=<id>-demo.localhost` → loja + template + destaques).
- [x] **Modos de falha mapeados** (sem `demo.json` → `None`; slug colidindo → `get_or_create`; re-seed → idempotente; **`active_template_id` é FK** → o template tem que existir).
- [x] **Itens adiados varridos** → Follow-ups + README.

> **Entregue:** `app/modules/content/demo_store.py` (`seed_template_demo_store` + helpers + `seed_demo_stores`); ligado no **prestart** (`initial_data.init`, **não** no `init_db` — pra o conftest não pré-seedar); 3 lojas-demo no db de dev; `tests/integration/test_demo_store.py` (5 testes, demo_store **98% cov**).

## Notas / Reconciliações
- O seed é **prestart** (`initial_data.init`), não `init_db`: assim o conftest não pré-seeda (testes cobrem os ramos de criação).
- Reusa **tudo** (store/catalog/media/domain/content) — zero render especial; a loja-demo é servida como qualquer vitrine.
- **Hero/banner da loja-demo:** o `demo.json` ganhou um campo `banner` (hero do design uxpilot, baixado→CDN pelo `import_assets`); `_ensure_theme` seta `theme.banner_image_url` a partir dele, senão o hero dos 3 templates caía no fundo sólido. (Os templates já renderizavam `theme.banner_image_url`.)

## Follow-ups
- [ ] **Update do catálogo da loja-demo** — o re-seed **adiciona** itens novos do `demo.json` mas **não atualiza** os existentes (preço/nome mudados não refletem; `get_or_create` por slug reusa). Decidir se atualiza no re-seed. Origem: `P5-DEMO-02`.
