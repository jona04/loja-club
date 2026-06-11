---
id: P5-CFG-02
title: Form genérico de settings no painel (1 componente, N schemas)
phase: 5
etapa: "Etapa 3 — Form genérico no painel"
area: CFG
status: todo
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
- [ ] Form genérico renderiza o schema do template ativo (todos os `type` V1).
- [ ] "Meus templates" + resetar.
- [ ] Upload de imagem gated `layout.assets.update`.
- [ ] Gates (`tsc`/`biome`) + e2e.
- [ ] **Modos de falha mapeados** (schema vazio, valor inválido, upload falho) → tratados ou Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Reaproveita padrões do `frontend-dashboard` (form/upload existentes).

## Follow-ups
- [ ] — nenhum (preencher ao implementar).
