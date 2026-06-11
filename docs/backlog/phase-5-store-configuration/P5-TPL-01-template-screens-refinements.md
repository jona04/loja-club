---
id: P5-TPL-01
title: Refinos das telas de template (admin + dashboard, thumbnail no CDN)
phase: 5
etapa: "Etapa 4 — Loja-demo + import de assets"
area: TPL
status: todo
depends_on: [P5-DEMO-01]
blocks: []
tests: [e2e]
---

# P5-TPL-01 — Refinos das telas de template

## Contexto
Com o **thumbnail no CDN** (absoluto, via `P5-DEMO-01`), as telas de template (admin + painel do lojista) ganham o thumb funcionando + mais campos. Hoje o thumb seedado é caminho relativo (`/templates/<id>_preview.png`), que só o dashboard serve.

## Docs de referência
- [25 — Platform Admin](../../concepts/25_platform_admin.md)
- [26 — Sistema de templates](../../concepts/26_template_system.md)

## Escopo (o que ENTRA)
- **Admin (`frontend-admin`):** com o thumbnail no CDN, a **lista/detalhe** mostram o thumb (hoje o relativo quebra no admin); o **detalhe** mostra mais coisas (além do thumb + `settings_schema`: descrição, ativo, **conteúdo demo**, defaults); o **dialog de editar** mostra o **thumb atual**.
- **Dashboard (`P3-TPL-03`):** o **picker do lojista** passa a usar o **thumbnail do CDN** (`preview_image_url`) em vez do PNG hardcoded de `public/templates/`.

## Fora de escopo (o que NÃO entra)
- O `import_assets` que gera os thumbnails de CDN: `P5-DEMO-01`.

## Arquivos a criar/alterar
- `frontend-admin/src/routes/_layout/templates.tsx` (alterar) — detalhe + editar.
- `frontend-dashboard/src/routes/_layout/store-layout.tsx` (alterar) — picker usa CDN.

## Passos
1. Admin: detalhe mostra thumb (CDN) + descrição/ativo/demo/defaults; editar mostra o thumb atual.
2. Dashboard: picker lê `preview_image_url` (CDN).

## Testes
- **Níveis:** e2e (admin + dashboard).
- **Cobrir:** e2e — admin mostra o thumb na lista/detalhe; picker do dashboard mostra o thumb do CDN.

## Definition of Done
- [ ] Admin: thumb na lista/detalhe + detalhe com mais campos + thumb no editar.
- [ ] Dashboard: picker usa `preview_image_url` (CDN).
- [ ] Gates (`tsc`/`biome`) + e2e.
- [ ] **Modos de falha mapeados** (sem thumb ainda, URL quebrada) → tratados ou Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Fecha os follow-ups "ADMIN-03 thumb relativo" e "dashboard thumbnail do CDN" da Fase 4.

## Follow-ups
- [ ] — nenhum (preencher ao implementar).
