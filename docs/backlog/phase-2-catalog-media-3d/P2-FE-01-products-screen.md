---
id: P2-FE-01
title: Painel — tela de Produtos + componente de upload de imagem
phase: 2
etapa: "Etapa 5/6 — Frontend (painel)"
area: FE
status: todo
depends_on: [P2-CAT-02, P2-MEDIA-02]
blocks: [P2-FE-02]
tests: [unit, e2e]
---

# P2-FE-01 — Painel: Produtos + upload de imagem

## Contexto
Tela de Produtos no `frontend-dashboard`, consumindo o `catalog` (`P2-CAT-02`) no contexto da loja ativa (`useActiveStore`), com gating por `catalog.*` (esconder/desabilitar = UX; segurança é backend).

## Docs de referência
- [09 — Merchant Dashboard](../../09_merchant_dashboard.md) (Produtos)
- [05 — Frontend Architecture](../../05_frontend_architecture.md)
- [21 — Design System](../../21_design_system_todo.md) (estado de upload)

## Escopo (o que ENTRA)
- Item de menu **Produtos** (via `buildMenu`/permissão `catalog.product.view`).
- Listar (paginado), criar, editar, **arquivar**, **publicar/despublicar**; campos: nome, slug, descrição, preço, variações, estoque, categoria, destaque.
- **Componente de upload de imagem:** envia para o `media`, mostra **estado de processamento** (worker gerando variantes) e a versão pronta; vincula ao produto.
- Gating de UI: salvar/publicar exigem a permissão (ex.: sem `catalog.product.update` vê mas não salva). Regenerar client se preciso.

## Fora de escopo (o que NÃO entra)
- Personalização 3D no produto → `P2-FE-02`. Storefront → Fase 3.

## Arquivos a criar/alterar
- `frontend/src/` — rota/tela de Produtos, componente de upload, hooks; `lib/menu.ts` (módulo Produtos).

## Passos
1. Rota + lista paginada + form de produto.
2. Upload de imagem (estado de processamento) + vínculo.
3. Gating por permissão; unit + e2e.

## Testes
> Fundações §10. Lógica de UI por permissão = unit; jornada = E2E.

- **Níveis:** unit (`vitest`) + E2E (Playwright, poucos).
- **Cobrir:** unit — menu/ação escondidos/desabilitados sem permissão; e2e — criar/publicar produto reflete na lista.

## Definition of Done
- [ ] Tela de Produtos (CRUD/publicar) + upload de imagem com estado de processamento, no contexto da loja ativa.
- [ ] Gating por permissão (UX); `tsc`/`vitest` verdes (E2E base ou follow-up).
- [ ] Itens adiados varridos → Follow-ups + README (ou "nenhum").

## Notas / Reconciliações
- E2E ao vivo pode virar follow-up (precisa do stack), como na Fase 1.

## Follow-ups
- (preencher)
