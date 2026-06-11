---
id: P5-SF-01
title: Vitrine lê theme.settings (defaults ⊕ overrides; image default no CDN)
phase: 5
etapa: "Etapa 5 — Vitrine lê settings + preview navegável"
area: SF
status: todo
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
- [ ] Templates leem `theme.settings[key] ?? default` (chrome específico).
- [ ] `image` com default no CDN; sem fundo vazio.
- [ ] Lorem/estático substituído por settings.
- [ ] Gates + e2e/smoke.
- [ ] **Modos de falha mapeados** (settings ausente, chave nova sem default) → tratados ou Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Funde o follow-up "conteúdo estático/lorem → dinâmico" da Fase 3.

## Follow-ups
- [ ] — nenhum (preencher ao implementar).
