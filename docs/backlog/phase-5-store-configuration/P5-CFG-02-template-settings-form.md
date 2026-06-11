---
id: P5-CFG-02
title: Form genérico de settings no painel (1 componente, N schemas)
phase: 5
etapa: "Etapa 3 — Form genérico no painel"
area: CFG
status: done
depends_on: [P5-CFG-01]
blocks: []
tests: [e2e]
---

# P5-CFG-02 — Form genérico de settings no painel

## Contexto
Com o storage + API prontos (`P5-CFG-01`), o painel ganha **um form genérico** que renderiza o `settings_schema` do template ativo — um componente, N schemas (nem form hardcoded, nem tela por template).

## Docs de referência
- [09 — Merchant Dashboard](../../concepts/09_merchant_dashboard.md) (§"Personalização do template (schema-driven, Fase 5)")
- [26 — Sistema de templates](../../concepts/26_template_system.md) (§"Personalização schema-driven")

## Escopo (o que ENTRA)
- **`TemplateSettingsForm`**: renderiza por `type` (`text`/`textarea`/`image`/`boolean`/`select`), agrupado por `group`; lê/grava via a API do painel (`P5-CFG-01`).
- **"Meus templates":** lista os templates que a loja **já editou** (linhas ativas) + **resetar** (excluir → volta aos defaults).
- **Upload de imagem** (campos `image`) reusa `media`, **gated `layout.assets.update`**.

## Fora de escopo (o que NÃO entra)
- Storage/API: `P5-CFG-01`.
- A vitrine refletir os valores: `P5-SF-01`.
- Campo de **cor** do tema: follow-up (doc 26).

## Arquivos a criar/alterar
- `frontend-dashboard/src/routes/_layout/store-layout.tsx` (alterar) — seção de personalização.
- `frontend-dashboard/src/components/.../TemplateSettingsForm.tsx` (criar).

## Passos
1. `TemplateSettingsForm` (input por `type`, agrupado por `group`).
2. Liga ao `ContentService` (GET schema+valores, PATCH, DELETE-reset).
3. "Meus templates" + resetar.
4. Upload de imagem gated `layout.assets.update`.

## Testes
- **Níveis:** e2e (Playwright) + unit do render se útil.
- **Quando escrever:** durante.
- **Cobrir:** e2e — editar um campo → salva → reflete; resetar → volta ao default; sem `layout.update` não salva.

## Definition of Done
- [x] Form genérico (`TemplateSettingsForm`) renderiza o schema do template ativo — `text`/`textarea`/`boolean` (os usados nos templates V1; `select`/`image` também tratados).
- [x] "Meus templates": badge **"Personalizado"** no grid (via `GET …/layout/settings/mine`) + **resetar** (linha ativa).
- [ ] Upload de imagem gated `layout.assets.update` — **diferido** (nenhum template V1 tem campo `image`); Follow-up.
- [x] Gates (`tsc`/`biome`/`vitest`) + **e2e** (`store-layout.spec.ts`: cria loja → personaliza → salva → persiste).
- [x] **Modos de falha mapeados** (schema vazio → form não renderiza; valor inválido → 422 do backend; upload de imagem → diferido).
- [x] **Itens adiados varridos** → Follow-ups + README.

> **Entregue:** `TemplateSettingsForm.tsx` (+ teste unit) ligado em `store-layout.tsx`; badge "Personalizado" + `listMyTemplates`; backend `GET /layout/settings/mine` (+ teste integração); e2e `store-layout.spec.ts`. Backend **251 testes / 94% cov**; frontend tsc/biome/**vitest 23/23**; **e2e verde**.

## Notas / Reconciliações
- "Meus templates" implementado como **badge no grid** (não lista separada) — doc 09 reconciliado.
- Todos os schemas V1 (aurora/bazar/studio) usam só `text`/`textarea`/`boolean`; `select`/`image` ficam tratados no form mas sem template que os exercite.

## Follow-ups
- [ ] **Upload de imagem nos campos `image`** (reusa `media`, gated `layout.assets.update`) — diferido: nenhum template V1 tem campo `image` e `layout.assets.update` ainda não está ligada a rota. Fazer quando um template tiver campo `image`. Origem: `P5-CFG-02`.
