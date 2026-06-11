---
id: P2-FE-01
title: Painel — tela de Produtos + componente de upload de imagem
phase: 2
etapa: "Etapa 3 — Frontend (painel)"
area: FE
status: done
depends_on: [P2-CAT-02, P2-MEDIA-02]
blocks: []
tests: [unit, e2e]
---

# P2-FE-01 — Painel: Produtos + upload de imagem

## Contexto
Tela de Produtos no `frontend-dashboard`, consumindo o `catalog` (`P2-CAT-02`) no contexto da loja ativa (`useActiveStore`), com gating por `catalog.*` (esconder/desabilitar = UX; segurança é backend).

## Docs de referência
- [09 — Merchant Dashboard](../../concepts/09_merchant_dashboard.md) (Produtos)
- [05 — Frontend Architecture](../../concepts/05_frontend_architecture.md)
- [21 — Design System](../../concepts/21_design_system_todo.md) (estado de upload)

## Escopo (o que ENTRA)
- Item de menu **Produtos** (via `buildMenu`/permissão `catalog.product.view`).
- Listar (paginado), criar, editar, **publicar**, **arquivar** (offline reversível), **deletar** (soft-delete); campos: nome, slug, descrição, preço, variações, estoque, categoria, destaque.
- **Componente de upload de imagem:** envia para o `media`, mostra **estado de processamento** (worker gerando variantes) e a versão pronta; vincula ao produto.
- Gating de UI: salvar/publicar exigem a permissão (ex.: sem `catalog.product.update` vê mas não salva). Regenerar client se preciso.

## Fora de escopo (o que NÃO entra)
- Personalização 3D no produto → **[Fase 7 — Produtos 3D](../phase-7-3d-products.md)**. Storefront → Fase 3.

## Arquivos a criar/alterar
- `frontend-dashboard/src/` — rota/tela de Produtos, componente de upload, hooks; `lib/menu.ts` (módulo Produtos).

## Passos
1. Rota + lista paginada + form de produto.
2. Upload de imagem (estado de processamento) + vínculo.
3. Gating por permissão; unit + e2e.

## Testes
> Fundações §10. Lógica de UI por permissão = unit; jornada = E2E.

- **Níveis:** unit (`vitest`) + E2E (Playwright, poucos).
- **Cobrir:** unit — menu/ação escondidos/desabilitados sem permissão; e2e — criar/publicar produto reflete na lista.

## Definition of Done
- [x] Tela de Produtos (lista/criar/editar/publicar/arquivar/deletar) + componente de upload de imagem (estado de processamento), no contexto da loja ativa.
- [x] Gating por permissão (UX); `tsc`/`biome`/`vitest` verdes (17 passed) + `vite build` ok. E2E ao vivo = follow-up.
- [x] Itens adiados varridos → Follow-ups + README.

## Progresso
- ✅ **Menu** "Produtos" (`lib/menu.ts`, permissão `catalog.product.view`) + teste.
- ✅ **Tela** `routes/_layout/products.tsx` (`ProductsScreen` exportado p/ teste): lista **paginada** (`skip`/`limit`, `PAGE_SIZE=20`, prev/próxima), criar/editar (dialogs: nome/preço/descrição/destaque + estoque), publicar/arquivar (offline reversível)/deletar (soft-delete) — gating por `catalog.product.*` (deletar = `catalog.product.delete`).
- ✅ **Upload** `components/Catalog/ProductImageUpload.tsx`: `uploadMedia` → `attachImage`; lista as **imagens salvas** (`listImages` traz `url`/`variants`/`status`), badge **processando** e **polling** (2s) até `ready`.
- ✅ Client OpenAPI já regenerado na `P2-CAT-02`. Verde: biome/tsc/vitest/vite build.

## Notas / Reconciliações
- **Preço** em 2 casas (`×100`/`/100`) — assume expoente 2 (USD/BRL, default); INV-G1 quer o expoente da moeda → follow-up.
- **Imagens:** `listImages` foi **enriquecido** com `url`/`variants`/`status` do media (via `session.get` no serviço — sem `GET /media` separado), então a tela mostra as imagens salvas e **pola** `processing→ready`. `attach_image` retorna o mesmo DTO enriquecido.
- **UX (pós-teste):** o dialog de edição **fecha ao salvar**; **criar** já abre o **editar** no produto novo (imagem/estoque precisam do `product_id`, então ficam lá); **seletor de itens por página** (10/20/50/100). Slug não é exibido (o usuário não precisa); o backend mantém o slug correto (auto-sufixo + acompanha em rascunho).
- **Estoque no Salvar:** o campo **pré-preenche** com o estoque atual (`GET .../inventory`, `P2-CAT-02`) e é salvo **junto com o "Salvar"**. Teste `EditProductDialog stock` (vitest) cobre o pré-preenchimento **e** o save pra não regredir.

## Follow-ups
- [x] **`listImages`/`attachImage` enriquecidos** com `url`/`variants`/`status` (sem `GET /media` separado) → tela mostra imagens salvas e **pola** `processing→ready`. *(feito)*
- [x] **Paginação na UI** (`skip`/`limit` + prev/próxima, `PAGE_SIZE=20`). *(feito)*
- [ ] **Preço com expoente da moeda** (INV-G1) — hoje assume 2 casas; derivar do `currency` (JPY=0, BHD=3). Origem: P2-FE-01.
- [ ] **UI de variações e categorias** — backend (`P2-CAT-02`) suporta; a tela ainda não. Origem: P2-FE-01.
- [ ] **E2E ao vivo** (Playwright) criar/publicar reflete na lista — precisa do stack. Origem: P2-FE-01.
- [ ] **Estado de imagem por push em vez de polling** — hoje o front pola `listImages` (`refetchInterval` 2s) enquanto há `processing`; trocar por **WebSocket/SSE** (o backend avisa `ready`) quando valer a infra. Origem: P2-FE-01.
