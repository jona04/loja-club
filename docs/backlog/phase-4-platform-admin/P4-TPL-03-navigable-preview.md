---
id: P4-TPL-03
title: Preview navegável — loja-demo + host de preview por template
phase: 4
etapa: "Etapa 3 — Cadastro/gestão de templates"
area: TPL
status: todo
depends_on: [P4-TPL-01]
blocks: [P4-ADMIN-03]
tests: [e2e]
---

# P4-TPL-03 — Preview navegável (loja-demo)

## Contexto
O preview navegável é o **storefront real** rodando contra uma **loja-demo** seedada, **forçando** um template — cada clique navega de verdade. É o que o painel do lojista (Fase 5) abre em outra aba. Não é HTML estático (o `docs/design/*.html` segue como fonte de design).

## Docs de referência
- [26 — Template System](../../26_template_system.md)
- [10 — Storefront and Layouts](../../10_storefront_and_layouts.md)
- [06 — Multitenancy and Domains](../../06_multitenancy_and_domains.md)

## Escopo (o que ENTRA)
- **Loja-demo** seedada (produtos/categorias de exemplo, da plataforma), idempotente.
- Servir o `frontend-storefront` sob o **host de preview** **`preview.${DOMAIN}/<template-id>`** (doc [26](../../26_template_system.md)) **forçando** o `active_template_id` = `<template-id>`, contra a loja-demo.
- **Registrar/publicar** a URL do preview navegável por template (consumida na Fase 5).

## Fora de escopo (o que NÃO entra)
- Registro/CRUD + schema → `P4-TPL-01`. Assets CDN → `P4-TPL-02`.
- Botão "ver preview completo" no painel do lojista → **Fase 5**.
- Telas do admin → `P4-ADMIN-03`.

## Arquivos a criar/alterar
- `app/...` seed da loja-demo (criar) — idempotente.
- `frontend-storefront/...` (alterar) — resolver template forçado pelo host/parâmetro de preview.
- `compose.yml` + Traefik (alterar) — host `preview.`.
- `app/modules/content/...` (alterar) — guardar a URL de preview por template.

## Passos
1. Seed da loja-demo (idempotente).
2. Resolver o template forçado pelo `<template-id>` no path de `preview.${DOMAIN}/`, contra a loja-demo.
3. Roteamento `preview.` no Traefik; registrar a URL por template.
4. Validar navegação real (home → categoria → produto) por template.

## Testes
> Regra em [`_foundations-and-bottlenecks.md`](../_foundations-and-bottlenecks.md) §10.
- **Níveis:** e2e (smoke).
- **Cobrir:** `preview.../<template-id>` abre a loja-demo com o template forçado; navegação real funciona; trocar `<template-id>` troca o template.

## Definition of Done
- [ ] Loja-demo seedada + preview navegável por template (storefront real, host de preview); URL registrada por template.
- [ ] **Modos de falha / edge cases mapeados** (template inexistente, loja-demo vazia) → tratados ou Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Decisão (doc [26](../../26_template_system.md)): preview = **storefront + loja-demo**, não HTML estático. Fecha os follow-ups `P3-TPL-03`/`P3-FE-02` de preview ao vivo (marcar na origem ao consumir na Fase 5).

## Follow-ups
- [ ] — (preencher ao implementar) → README da fase.
