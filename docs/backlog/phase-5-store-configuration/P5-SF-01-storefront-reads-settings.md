---
id: P5-SF-01
title: Vitrine lê theme.settings (defaults ⊕ overrides; image default no CDN)
phase: 5
etapa: "Etapa 5 — Vitrine lê settings + preview navegável"
area: SF
status: done
depends_on: [P5-CFG-01]
blocks: [P5-PREV-01]
tests: [e2e]
---

# P5-SF-01 — Vitrine lê os settings

## Contexto
Com a API pública devolvendo `theme.settings` (`P5-CFG-01`), os templates da vitrine passam a **ler os valores** (`theme.settings[key] ?? default`) em vez de texto/imagem hardcoded — o chrome específico de cada template fica editável.

## Docs de referência
- [26 — Sistema de templates](../../concepts/26_template_system.md) (§"Personalização schema-driven", §"Render")
- [10 — Storefront and Layouts](../../concepts/10_storefront_and_layouts.md)

## Escopo (o que ENTRA)
- Os templates (`frontend-storefront/templates/<id>/*`) leem `theme.settings[key] ?? default` para o **chrome específico** (anúncio/subtítulo/seções opcionais/etc.).
- **Campos de imagem** têm default = a **imagem original do template no CDN** (importada na `P5-DEMO-01`); nunca fundo vazio.
- O conteúdo estático/lorem (anúncio/editorial/institucional/subtítulo) → dinâmico via settings.

## Fora de escopo (o que NÃO entra)
- API/storage dos settings: `P5-CFG-01`.
- O form no painel: `P5-CFG-02`.
- O preview navegável: `P5-PREV-01`.

## Arquivos a criar/alterar
- `frontend-storefront/templates/{aurora,bazar,studio}/*` (alterar) — ler `theme.settings`.
- `frontend-storefront/lib/...` (alterar) — expor `theme.settings` ao template.

## Passos
1. A API pública da vitrine já entrega `theme.settings` (`P5-CFG-01`); expor ao template.
2. Cada template lê `theme.settings[key] ?? default` no chrome específico.
3. Campos `image` usam o default no CDN.

## Testes
- **Níveis:** e2e (Playwright) + smoke real.
- **Cobrir:** e2e — settar um campo no painel reflete na vitrine; campo vazio cai no default; imagem default no CDN.

## Definition of Done
- [x] Os 3 templates (aurora/bazar/studio) leem `theme.settings[key] ?? default` no chrome específico: anúncio (`announcement_text`), subtítulo do hero / intro do catálogo (`hero_subtitle`/`catalog_intro`), seções toggle (`show_trust_badges`/`show_category_strip`/`show_filters`) e contato do rodapé (`footer_contact`).
- [ ] `image` com default no CDN — **diferido** (nenhum schema V1 tem campo `image`; depende de `P5-DEMO-01`).
- [x] Lorem/estático do chrome **editável** substituído por settings (o resto é design fixo do template).
- [x] Gates (`biome` + `next build` + `tsc`); **e2e/smoke do storefront diferido** (storefront sem infra de e2e) — Follow-up.
- [x] **Modos de falha mapeados** (settings ausente → `?? {}`; chave sem valor → `?? default`).
- [x] **Itens adiados varridos** → Follow-ups + README.

> **Entregue:** `StorefrontTheme.settings` (tipo); `getHome` memoizado (React `cache`); **Shell async** que busca os settings sozinho (sem prop-drilling) nos 3 templates; chrome lendo `settings[key] ?? default`. tsc/biome/`next build` verdes. O self-fetch dedupa via `cache()` → 1 call/request, anúncio/rodapé consistentes em toda página.

## Notas / Reconciliações
- **Fecha** o follow-up "conteúdo estático/lorem → dinâmico" da Fase 3 (o chrome editável agora vem de settings).
- Cada template mapeia no seu chrome: bazar tem o anúncio no `BazarHeader`; studio mostra o anúncio só se preenchido (design minimalista) e os filtros via `StudioSidebar`.

## Follow-ups
- [ ] **e2e/smoke do storefront** (vitrine reflete `theme.settings`) — o storefront não tem infra de e2e/Playwright; a API de `theme.settings` é coberta por teste de integração (backend) e o render é type-validado (`tsc`/`next build`). Montar a infra + um e2e real. Origem: `P5-SF-01`.
- [ ] **Campos `image` com default no CDN** — quando um template tiver campo `image`, o default vem da imagem original no CDN (importada na `P5-DEMO-01`). Origem: `P5-SF-01`.
