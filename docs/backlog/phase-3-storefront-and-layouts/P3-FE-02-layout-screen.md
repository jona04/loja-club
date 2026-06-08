---
id: P3-FE-02
title: Painel — tela "Layout da Loja"
phase: 3
etapa: "Etapa 8 — Frontend (painel)"
area: FE
status: todo
depends_on: [P3-CONTENT-02]
blocks: []
tests: [unit]
---

# P3-FE-02 — Tela "Layout da Loja" (painel)

## Contexto
No `frontend-dashboard`, o lojista vê os 2 templates, faz preview com dados reais, **aplica** e edita banner/headline/destaque — refletindo na vitrine (a invalidação de cache é feita no backend).

## Docs de referência
- [09 — Merchant Dashboard](../../09_merchant_dashboard.md)
- [10 — Storefront & Layouts](../../10_storefront_and_layouts.md)

## Escopo (o que ENTRA)
- Tela "Layout da Loja": listar templates, **preview**, **aplicar**; editar banner, headline e coleção em destaque.
- Gating por **`layout.*`** (menu = `layout.view`; aplicar/editar = `layout.update`); consome as rotas da `P3-CONTENT-02`.

## Fora de escopo (o que NÃO entra)
- `logo_url`/descrição (ficam em **Configurações**, Fase 1).
- CRUD de páginas/menus → Follow-up.
- Editor 3D → Fase 5.

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
- [ ] Tela lista/preview/aplica template + edita banner/headline/destaque; gating por permissão.
- [ ] `tsc`/`biome`/`vitest` verdes.
- [ ] **Modos de falha mapeados** (aplicar falha, preview sem dados, sem permissão) → tratados ou Follow-up.
- [ ] Itens adiados varridos → Follow-ups + README, ou "nenhum".

## Notas / Reconciliações
- A invalidação de cache é responsabilidade do backend (`P3-CONTENT-02`); a tela só dispara a ação.

## Follow-ups
- (preencher ao executar)
