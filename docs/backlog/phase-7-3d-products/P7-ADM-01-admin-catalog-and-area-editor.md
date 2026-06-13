---
id: P7-ADM-01
title: Admin — habilitar/desabilitar + editor visual da área imprimível
phase: 7
etapa: "Etapa 2 — Admin: habilitar/desabilitar + editar a área imprimível"
area: ADM
status: todo
depends_on: [P7-CAT-01]
blocks: []
tests: [integration]
---

# P7-ADM-01 — Admin: catálogo 3D + editor da área imprimível

## Contexto
O admin **não cria** modelos (GLB é seed), mas **governa** o catálogo e **ajusta os parâmetros** da área imprimível/limites — uma **ferramenta visual de mapeamento** que será **reaproveitada na Fase 12** (lojista mapeia o próprio GLB). Por isso nasce genérica.

## Docs de referência
- [30 — §3 Área imprimível (editável no admin)](../../concepts/30_3d_customization_technical_design.md)
- [25 — Platform admin](../../concepts/25_platform_admin.md)

## Escopo (o que ENTRA)
- `platform_admin` (backend): listar modelos + **habilitar/desabilitar** (`is_active`) + obter detalhe/preview; **editar** `printable_areas`/`text_config`/`art_limits` de uma versão. Gated por permissão de plataforma.
- `frontend-admin`: tela do catálogo 3D — lista + toggle + **preview 3D** + **editor visual da área** (ajustar `projector`/retângulo/limites sobre o preview e salvar).
- **Editar afeta sessões novas**; pedidos/itens congelados **não mudam** (doc [30 §3](../../concepts/30_3d_customization_technical_design.md)).

## Fora de escopo (o que NÃO entra)
- Criar/otimizar/subir GLB: `P7-ASSET-01`/`P7-CAT-01`.
- Painel do **lojista** (escolher/vincular): `P7-PROD-01`.
- Editor do **cliente** (storefront): `P7-EDITOR-*`.

## Arquivos a criar/alterar
- `backend/app/modules/platform_admin/{routes,services}.py` (alterar) — endpoints do catálogo 3D.
- `frontend-admin/src/routes/...` (criar) — tela catálogo 3D + editor de área (componente reutilizável).
- regen do client OpenAPI do admin.

## Passos
1. Rotas admin (list/toggle/get + update dos JSONs da versão).
2. Tela: lista + toggle + preview 3D.
3. **Editor visual da área** (componente genérico, reusável na Fase 12).

## Testes
- **Níveis:** integração.
- **Quando escrever:** durante.
- **Cobrir:** integração — toggle muda visibilidade; update da área persiste e valida (retângulo dentro de limites); só modelos ativos aparecem pro lojista.

## Definition of Done
- [ ] Admin habilita/desabilita e **edita a área** (persistido na versão); editar **não** altera pedido congelado.
- [ ] **Modos de falha mapeados** — parâmetros inválidos (retângulo fora) → 422; editar versão em uso → vale só pra sessões novas. → tratados/Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- O **componente de mapeamento da área** é a base da **[Fase 12](../phase-12-merchant-3d-generation.md)** (Etapa 3) — manter genérico (não acoplar ao "platform").

## Follow-ups
- [ ] **e2e do admin (Playwright)** do editor de área — *Quando:* infra de e2e do admin. → README da fase.
