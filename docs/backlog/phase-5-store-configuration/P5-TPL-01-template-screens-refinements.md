---
id: P5-TPL-01
title: Refinos das telas de template (admin + dashboard, thumbnail no CDN)
phase: 5
etapa: "Etapa 4 — Loja-demo + import de assets"
area: TPL
status: done
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
- [x] Admin: thumb na lista/detalhe + detalhe com mais campos + thumb no editar.
- [x] Dashboard: picker usa `preview_image_url` (CDN).
- [x] Gates (`tsc`/`biome`) + e2e (admin `templates.spec.ts` + dashboard `store-layout.spec.ts`).
- [x] **Modos de falha mapeados** (sem thumb ainda, URL quebrada) → tratados ou Follow-ups.
- [x] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Fecha os follow-ups "ADMIN-03 thumb relativo" e "dashboard thumbnail do CDN" da Fase 4.
- O seed deriva `preview_image_url` do key do CDN (`storage.public_url("public/templates/<id>/preview.png")`), absoluto — não mais relativo; `import_assets.import_template_thumbnail` sobe o `preview.png` (movido para `frontend-storefront/templates/<id>/`). PNGs de `frontend-dashboard/public/templates/` removidos.
- **Sem thumb / URL quebrada:** a UI cai no placeholder (`—` na lista, "sem thumb" no detalhe) — tratado, sem follow-up.

## Follow-ups
- [ ] **Detalhe do admin sem conteúdo-demo + defaults** — o escopo pedia mostrar "conteúdo demo + defaults" no detalhe, mas `ThemeTemplateAdminPublic` expõe só id/nome/descrição/ativo/thumb/`settings_schema`; falta o backend expor o `demo.json` resolvido e os defaults do schema. Expor + exibir.
