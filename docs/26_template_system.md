# 26 — Sistema de templates (ciclo de vida, CDN e preview navegável)

> Consolida as decisões sobre **como os templates existem, são cadastrados, previsualizados, escolhidos e personalizados**. Complementa o doc [10](./10_storefront_and_layouts.md) (storefront/layouts) e o [25](./25_platform_admin.md) (admin).

## Princípio: composição ≠ contrato

O **dado é o contrato** (loja, produtos, categorias, identidade) — **igual em todo template**. A **apresentação** (quais blocos, textos de chrome, imagens) é **por template**. Trocar de template **não quebra** o fluxo de compra. Hoje há 3 templates (**Aurora**, **Bazar**, **Studio**), estruturalmente bem distintos, validando esse contrato (Fase 3).

## Os 4 artefatos de um template

1. **Fonte/design** — o HTML original (uxpilot) em `docs/design/templates/<id>/`. É **referência de port** (não é o que o lojista vê). Pode ter `.html` por página + o `_preview.png`.
2. **Template real** — os componentes React **data-driven** em `frontend-storefront/templates/<id>/` (`Shell`/`Home`/`Category`/`Product` + card). É o que **renderiza pra loja escolhida**, lendo os dados reais + `theme.settings`.
3. **Assets no CDN** — **thumbnail** + **imagens-default** do template, hospedados em **S3/CloudFront**. Substituem os PNGs hardcoded em `public/` e as URLs temporárias do uxpilot.
4. **Preview navegável** — uma versão **navegável** do template, aberta do painel em outra aba (cada clique funciona). **Decisão abaixo.**

## Decisão: preview navegável = storefront + loja-demo

O **preview navegável completo** **não** é HTML estático duplicado. É o **próprio storefront renderizando uma "loja-demo"** (produtos/categorias de exemplo) com o template **forçado** pela URL: **`preview.${DOMAIN}/<template-id>`** (host de preview dedicado; o `<template-id>` no path força o `active_template_id` da loja-demo).

**Por quê:**
- **Sempre fiel** — é o template real; nunca diverge de uma cópia HTML.
- **Cada clique funciona** — é o storefront navegável de verdade (home → categoria → produto → carrinho).
- **Reuso total** — zero HTML a manter em paralelo; a loja-demo é seedada uma vez.
- **Cadastrou, já previsualiza** — ao admin cadastrar um template (Fase 4), ele fica previsualizável (demo) **e** usável (lojas escolhem).

> O `docs/design/*.html` continua como **fonte/referência**; **não** vira o preview navegável. (A alternativa de hospedar HTML-estático-navegável no CDN foi descartada por duplicar manutenção e divergir do template real.)

## Ciclo de vida

```text
Admin (Fase 4)                         Lojista (Fase 5)              Cliente
─────────────                          ────────────────             ───────
cadastra template  ─┬─ assets → CDN    escolhe template (picker)    vê a vitrine
(id/nome/status)    ├─ settings schema  personaliza (form do schema) navegando o
                    └─ publica preview   abre preview navegável        template real
                       navegável (demo)  (outra aba)                   da loja
```

- **Cadastro (admin, [Fase 4](./backlog/phase-4-platform-admin.md)):** metadados + **upload de assets pro CDN** + **registro do schema** (vindo do código, seedado) + **preview navegável** publicado.
- **Configuração (lojista, [Fase 5](./backlog/phase-5-store-configuration.md)):** escolhe o template + **personaliza via form gerado do schema** + abre o **preview navegável completo**.
- **Render (storefront):** a vitrine resolve `active_template_id` → componentes React, lendo dados reais + `theme.settings[key] ?? default`.

## Personalização schema-driven (o "settings schema")

Cada template **declara** os campos editáveis num **manifesto** (`settings_schema`): um **`settings-schema.json` por template** (`frontend-storefront/templates/<id>/settings-schema.json`), **importado pelo próprio template React** (render) **e lido pelo seed do backend** — **fonte única, sem drift**. É **seedado** em `content_theme_templates.settings_schema` no deploy. O painel renderiza **um form genérico** a partir dele (um componente, N schemas — nem form hardcoded nem tela por template). O **admin não edita os campos** (evita divergência schema↔código): ele sobe assets + ativa. Um template **genuinamente novo** exige deploy do `frontend-storefront` (código + manifesto); cadastro 100% dinâmico é evolução futura.

- **Campos:** `{ key, type, label, group, default, max_length? }`. Tipos V1: `text` · `textarea` · `image` · `boolean` · `select` (cor do tema = follow-up).
  - Bloco que **só existe num template** → só no schema dele; bloco **opcional** → campo `boolean`.
  - **`image` sempre com default** = a **imagem original do template no CDN** — nunca renderiza fundo vazio.
- **Valores por loja × template** (`content_store_template_settings`, soft delete; **único por par entre ativos**). **Trocar de template não perde** o preenchido; **resetar = excluir** → re-selecionar volta aos defaults. O painel lista **"meus templates"** (os já editados).
- **Universal vs por-template:** `banner_image_url` / `headline` / logo / WhatsApp / cor continuam **universais** (`content_store_theme_settings`); o schema cobre só o **chrome específico** de cada template.
- **Público:** a API da vitrine devolve `theme.settings` (defaults do schema **mesclados** com overrides) do template **ativo**.

## CDN dos assets

Os assets do template (thumbnail + imagens-default) vivem em **S3 + CloudFront** (doc [13](./13_performance_cache_and_cdn.md)), enviados pelo **admin** ao cadastrar (Fase 4). Acaba a dependência de `public/` hardcoded e de URLs temporárias do uxpilot.

## Estado atual (Fase 3, concluída) e o que falta

- **Feito (Fase 3):** os 3 templates React (`P3-TPL-01/02`), o `Shell` no contrato, o **picker com thumbnail + preview por imagem + upload de banner** no painel (`P3-TPL-03`), defaults de chrome apresentáveis.
- **Falta:** **cadastro pelo admin + assets no CDN** (Fase 4); **personalização schema-driven + preview navegável** (Fase 5). O **cadastro inteligente de templates** pelo admin e os assets no CDN são o que destrava tirar isso do hardcoded.
