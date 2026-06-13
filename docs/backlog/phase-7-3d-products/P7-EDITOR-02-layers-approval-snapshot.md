---
id: P7-EDITOR-02
title: Editor — camadas (imagem+texto) + decal + aprovação + snapshot + link público
phase: 7
etapa: "Etapa 5 — Editor 3D no storefront (react-three-fiber)"
area: EDITOR
status: todo
depends_on: [P7-EDITOR-01]
blocks: [P7-ORD-01]
tests: [unit]
---

# P7-EDITOR-02 — Camadas, decal, aprovação, snapshot e link público

## Contexto
O **conteúdo** do editor: aplicar **imagem** e **texto** como camadas (decal) dentro da área, a **aprovação** obrigatória com **snapshot client-side**, e a **visão pública read-only** (link da assistida) com aprovação por confirmação de contato.

## Docs de referência
- [30 — §2 Camadas/decal / §4 state_json / §5 Snapshot / §9 Link público](../../concepts/30_3d_customization_technical_design.md)

## Escopo (o que ENTRA)
- **Camada imagem:** upload raster (PNG/JPG) → **decal** projetado na área; transform (mover/escalar/rotacionar) **dentro do retângulo**; z-order.
- **Camada texto:** conteúdo + **fonte** (conjunto fechado) + **cor do texto** + tamanho → canvas→textura → decal.
- **Aprovação:** habilita com ≥1 camada válida; **gera o snapshot** (canvas → PNG, doc [30 §5](../../concepts/30_3d_customization_technical_design.md)) → envia + chama `aprovar` (`P7-SESS-01`).
- **Link público read-only** (`/p/<token>`): reusa o editor em modo leitura; **aprovar** pede **confirmação de contato** (sem conta).

## Fora de escopo (o que NÃO entra)
- **Cor do produto** (recolor): fora da V1 (a cor aqui é do **texto**).
- **SVG/PDF**: só raster na V1.
- Congelar no pedido: `P7-ORD-01`. Montar a assistida (lado lojista): `P7-OPS-01`.

## Arquivos a criar/alterar
- `frontend-storefront/...` (alterar) — camadas (imagem/texto), decal, handles 2D, painel de aprovação, geração de snapshot.
- `frontend-storefront/app/p/[token]/...` (criar) — visão pública read-only + aprovar por contato.

## Passos
1. Camada imagem (upload → decal + transform na área).
2. Camada texto (canvas→textura → decal; fonte/cor/tamanho).
3. Aprovação + **snapshot** client-side → enviar/aprovar.
4. Visão pública `/p/<token>` (read-only) + aprovar por confirmação de contato.

## Testes
- **Níveis:** unit (vitest).
- **Quando escrever:** durante.
- **Cobrir:** unit — adicionar imagem/texto atualiza o `state_json`; aprovação bloqueada sem camada/snapshot; transform fica **dentro** da área; visão pública é read-only e aprovar exige contato.

## Definition of Done
- [ ] Cliente aplica imagem + texto, aprova com snapshot; link público abre read-only e aprova por contato.
- [ ] **Modos de falha mapeados** — **snapshot falha** → bloqueia aprovação + retry; **glifo ausente** → fonte fallback + aviso; arte inválida → erro de `P7-SESS-01`. → tratados/Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- A **cor** no editor é só a **cor do texto** (camada). A cor **do produto** (recolor) é follow-up.

## Follow-ups
- [ ] **Recolor do produto** (paleta + material nomeado + seletor) — fora da V1 (doc [30 §12](../../concepts/30_3d_customization_technical_design.md)). → README da fase.
- [ ] **Arte vetorial (SVG/PDF)** pra gráficas — *Quando:* depois da V1. → README da fase.
- [ ] **e2e Playwright** do fluxo personalizar→aprovar→carrinho → `P3-SF-03`. → README da fase.
