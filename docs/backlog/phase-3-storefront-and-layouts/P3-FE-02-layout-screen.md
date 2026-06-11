---
id: P3-FE-02
title: Painel — tela "Layout da Loja"
phase: 3
etapa: "Etapa 4 — Frontend (painel)"
area: FE
status: done
depends_on: [P3-CONTENT-02]
blocks: []
tests: [unit]
---

# P3-FE-02 — Tela "Layout da Loja" (painel)

## Contexto
No `frontend-dashboard`, o lojista vê os 2 templates, faz preview com dados reais, **aplica** e edita banner/headline/destaque — refletindo na vitrine (a invalidação de cache é feita no backend).

## Docs de referência
- [09 — Merchant Dashboard](../../concepts/09_merchant_dashboard.md)
- [10 — Storefront & Layouts](../../concepts/10_storefront_and_layouts.md)

## Escopo (o que ENTRA)
- Tela "Layout da Loja": listar templates, **preview**, **aplicar**; editar banner, headline e coleção em destaque.
- Gating por **`layout.*`** (menu = `layout.view`; aplicar/editar = `layout.update`); consome as rotas da `P3-CONTENT-02`.

## Fora de escopo (o que NÃO entra)
- `logo_url`/descrição (ficam em **Configurações**, Fase 1).
- CRUD de páginas/menus → Follow-up.
- Editor 3D → Fase 7.

## Arquivos a criar/alterar
- `frontend-dashboard/src/routes/_layout/store-layout.tsx` (criar) + entrada no menu (`lib/menu.ts`).
- `frontend-dashboard/src/client/*` (regen, se a API mudou).

## Passos
1. Item de menu (por permissão); query dos templates + tema ativo.
2. Preview + aplicar (mutation → invalida no servidor); editar campos do tema.
3. Teste de gating (espelha `products.test.tsx`).

## Testes
> Regra em [`_foundations-and-bottlenecks.md`](../_foundations-and-bottlenecks.md) §10.

- **Níveis:** unit (vitest) — gating; `tsc`/`biome`/`vitest` verdes.
- **Cobrir:** aplicar desabilitado sem permissão; aplicar dispara a mutation correta.

## Definition of Done
- [x] Tela lista/preview/aplica template + edita banner/headline/destaque; gating por permissão (testado).
- [x] `tsc`/`biome`/`vitest` verdes (+ `vite build` regenera o routeTree com a rota).
- [x] **Modos de falha mapeados** (aplicar falha → toast `handleError`; preview sem dados → mostra o template; sem permissão → campos/botões desabilitados) → tratados/Follow-up.
- [x] Itens adiados varridos → Follow-ups + README.

## Notas / Reconciliações
- A invalidação de cache é responsabilidade do backend (`P3-CONTENT-02`); a tela só dispara a ação.
- Espelha `store-settings.tsx` (TanStack Query + `ContentService` + `useActiveStore` + `StoreGate` + toast/`handleError`). Rota `/_layout/store-layout`; menu **"Layout"** gated por `layout.view`; editar/salvar gated por `layout.update`.
- **Templates** (`listTemplates`) em cards (selecionar) + **preview** (`previewLayout`); **aplicar + editar** num único `Salvar` (`updateLayout` → `ThemeUpdate`).
- `featured_collection_id` é Input de UUID cru (sem endpoint de listar coleções, e a vitrine ainda não renderiza destaque por coleção) — forward-looking. `logo_url`/descrição ficam em **Configurações** (Fase 1), fora daqui.
- e2e (Playwright) **não** cobre esta tela (suíte só painel-base: login/signup/user-settings); a mudança é aditiva e isolada (gating é unit).

## Follow-ups
- [ ] **Picker de coleção em destaque** (`P3-FE-02`): `featured_collection_id` é UUID cru — trocar por um select quando existir endpoint de listar coleções (+ a vitrine renderizar destaque por coleção, ver `P3-SF-01`).
- [ ] **Preview visual** (`P3-FE-02`): hoje o preview é um aviso de dados (template aplicado); evoluir para abrir a vitrine com o template previsto / render visual.
- [ ] **CRUD de páginas/menus no painel** (`P3-FE-02`): fora de escopo aqui; adicionar quando a UI precisar (espelha o follow-up da `P3-CONTENT-02`).
