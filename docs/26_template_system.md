# 26 — Sistema de templates (ciclo de vida, CDN, demo e preview)

> Consolida **como os templates existem, são criados, cadastrados, previsualizados, escolhidos e personalizados**. Complementa o doc [10](./10_storefront_and_layouts.md) (storefront/layouts) e o [25](./25_platform_admin.md) (admin). O **passo-a-passo** de criar um template novo está no doc [27](./27_template_authoring_guide.md).

## Princípio: composição ≠ contrato

O **dado é o contrato** (loja, produtos, categorias, identidade) — **igual em todo template**. A **apresentação** (quais blocos, textos de chrome, imagens) é **por template**. Trocar de template **não quebra** o fluxo de compra. Hoje há 3 templates (**Aurora**, **Bazar**, **Studio**), estruturalmente bem distintos, validando esse contrato (Fase 3).

## Código vs dados (o eixo de tudo)

Um template tem **duas naturezas**:

- **Código** — os componentes **React data-driven** (`Shell`/`Home`/`Category`/`Product` + card) que desenham as páginas. É a **cara** do template; só um **dev** cria, e **exige deploy** do `frontend-storefront`.
- **Dados** — metadados, `settings_schema`, **assets no CDN** e o **conteúdo demo**. É o que a **plataforma/admin** gerencia, **sem deploy**.

A vitrine renderiza **React**, não HTML cru — então o `.html` do uxpilot **não vira** um template ao vivo sozinho: um dev **porta pra React** + dá deploy. (Um "motor genérico de HTML" tornaria o cadastro 100% dinâmico, mas joga fora o port fiel/bonito; **fora de escopo na V1**.) O que **é** dinâmico (admin, sem deploy): **registrar**, **importar assets pro CDN**, **montar o demo** e **ativar**.

## Os artefatos de um template

1. **Fonte/design** — o HTML do uxpilot em `docs/design/templates/<id>/` (`.html` por página + imagens com **URL do uxpilot**). **Referência de port**, não é o que o lojista vê.
2. **Código React** — `frontend-storefront/templates/<id>/` (data-driven, lê os dados reais + `theme.settings`). O que **renderiza**.
3. **Manifestos** (no mesmo dir, **fonte única** — importados pelo template React **e** lidos pelo backend):
   - `settings-schema.json` — os **campos editáveis** do chrome `{ key, type, label, group, default, … }`.
   - `demo.json` — o **conteúdo demo** do template: categorias, produtos (nome/preço) e as **URLs de imagem** (do uxpilot) — o material pra vitrine-demo ficar **igual ao design**.
4. **Assets no CDN** — **thumbnail** + **todas as imagens** do template (chrome + demo) em **S3/CloudFront**, importadas das URLs do uxpilot.
5. **Loja-demo** — uma **loja real por template** com o catálogo/imagens do `demo.json`, com `active_template_id` = o template. É o **preview navegável** **e** o **modelo** que o lojista copia.

## A loja-demo (por template) — o modelo bonito

Cada template tem **uma loja-demo própria** (`aurora-demo` / `bazar-demo` / `studio-demo`): um `store` normal, com o template aplicado e o **catálogo + imagens + textos vindos do `demo.json`/schema** (= o design do uxpilot).

- **Reusa tudo** (store/catalog/storefront/settings) — **zero** render especial; a loja-demo é servida como qualquer vitrine.
- É **fiel ao design** e serve de **modelo**: o lojista vê "dá pra ficar bonito, é só seguir o demo".
- O **preview navegável** = o storefront servindo essa loja-demo (cada clique navega de verdade: home → categoria → produto → carrinho).
- **Atualizar o demo é dinâmico** — a loja-demo é uma loja real; quem tem acesso a edita pelo mesmo caminho de qualquer loja (sem código/deploy).

## Pipeline `import_assets` (URLs do uxpilot → CDN)

As imagens do template **nascem** com URL do uxpilot (no `demo.json` e nos defaults `image` do schema). Um job de backend **`import_assets`**: pra cada URL, **baixa → sobe pro S3 (`public/templates/<id>/…`) → CloudFront** → **reescreve** a referência pra **URL do CDN** (no schema seedado **e** no catálogo da loja-demo).

- Roda **no cadastro** do template (ou ação "importar assets") — **mesmo caminho** pra aurora/bazar/studio (carga artificial, do design) **e** pra qualquer template futuro.
- Acaba a dependência do uxpilot e de `public/` hardcoded.

## Ciclo de vida

```text
Designer            Dev (deploy)                  Admin (Fase 4)        Lojista (Fase 5)          Cliente
────────            ────────────                  ─────────────         ────────────────          ───────
cria no uxpilot ──► porta p/ React + manifestos   registra template     escolhe template          navega a
(.html + imgs)      (settings-schema + demo.json)  (id/nome/status)       personaliza (form schema)  vitrine real
                                                   thumbnail no CDN        abre o preview navegável
                    ─────── Fase 5: import_assets (imgs→CDN) · monta a loja-demo · preview navegável ───────
```

- **Cadastro (admin, [Fase 4](./backlog/phase-4-platform-admin.md)):** metadados (id/nome/status) + **thumbnail no CDN** + **registro do schema** (vindo do código). *(Atualizar template existente pelo admin = baixa prioridade.)*
- **Demo + preview + personalização ([Fase 5](./backlog/phase-5-store-configuration.md)):** `import_assets` (imagens→CDN) + monta a **loja-demo por template** (do `demo.json`/design) + **preview navegável** + o lojista **personaliza** (form do schema) e abre o preview.
- **Render (storefront):** resolve `active_template_id` → componentes React, lendo dados reais + `theme.settings[key] ?? default`.

## Personalização schema-driven (o "settings schema")

Cada template **declara** os campos editáveis no `settings-schema.json` (**fonte única**, importado pelo template React **e** seedado em `content_theme_templates.settings_schema` no deploy). O painel renderiza **um form genérico** a partir dele (um componente, N schemas — nem form hardcoded nem tela por template). O **admin não edita os campos** (evita divergência schema↔código): ele sobe o thumbnail, dispara o import e ativa.

- **Campos:** `{ key, type, label, group, default, max_length? }`. Tipos V1: `text` · `textarea` · `image` · `boolean` · `select` (cor do tema = follow-up).
  - Bloco que **só existe num template** → só no schema dele; bloco **opcional** → campo `boolean`.
  - **`image` sempre com default** = a **imagem original do template no CDN** (via `import_assets`) — nunca renderiza fundo vazio.
- **Valores por loja × template** (`content_store_template_settings`, soft delete; **único por par entre ativos**). **Trocar de template não perde** o preenchido; **resetar = excluir** → re-selecionar volta aos defaults. O painel lista **"meus templates"** (os já editados).
- **Universal vs por-template:** `banner_image_url` / `headline` / logo / WhatsApp / cor continuam **universais** (`content_store_theme_settings`); o schema cobre só o **chrome específico** de cada template.
- **Público:** a API da vitrine devolve `theme.settings` (defaults do schema **mesclados** com overrides) do template **ativo**.

## CDN dos assets

Os assets do template (thumbnail + imagens de chrome/demo) vivem em **S3 + CloudFront** (doc [13](./13_performance_cache_and_cdn.md)). O **thumbnail** é enviado pelo admin no cadastro (Fase 4); as **imagens de chrome/demo** entram via `import_assets` (Fase 5). Acaba a dependência de `public/` hardcoded e das URLs temporárias do uxpilot.

## Estado atual e o que falta

- **Feito (Fase 3):** os 3 templates React (`P3-TPL-01/02`), o `Shell` no contrato, o **picker com thumbnail + preview por imagem + upload de banner** no painel (`P3-TPL-03`), defaults de chrome apresentáveis.
- **Feito (Fase 4):** **registro de templates** (CRUD + `settings_schema` do código, `P4-TPL-01`) + **thumbnail no CDN** (`P4-TPL-02`).
- **Falta (Fase 5):** `import_assets` (imagens→CDN) + **loja-demo por template** (do `demo.json`/design, incl. carga de aurora/bazar/studio) + **preview navegável** + **personalização schema-driven** + a vitrine lendo `theme.settings`.
