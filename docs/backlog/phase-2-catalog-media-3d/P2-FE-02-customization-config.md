---
id: P2-FE-02
title: Painel — config de personalização no produto + visão de sessões
phase: 2
etapa: "Etapa 6 — Frontend (painel)"
area: FE
status: todo
depends_on: [P2-CUST-03, P2-CAT-02, P2-FE-01]
blocks: []
tests: [unit, e2e]
---

# P2-FE-02 — Painel: personalização do produto + sessões

## Contexto
No painel, o lojista marca um produto como personalizável, escolhe o modelo 3D e acompanha as sessões dos clientes (doc [22](../../22_product_customization_3d.md)/[09](../../09_merchant_dashboard.md)). O editor do **cliente** é Fase 3.

## Docs de referência
- [22 — Product Customization 3D](../../22_product_customization_3d.md) (painel do lojista)
- [09 — Merchant Dashboard](../../09_merchant_dashboard.md)

## Escopo (o que ENTRA)
- No produto compatível: **habilitar personalização** + **escolher modelo 3D** (lista de `P2-CUST-01`) + observações de produção + preview básico do modelo.
- **Visão de sessões** da loja: listar, ver preview da arte, **baixar** arquivo (URL assinada), ver parâmetros, atualizar **status de arte/produção**.
- Gating por `customization.*`. Regenerar client se preciso.

## Fora de escopo (o que NÃO entra)
- Editor 3D do cliente (Three.js) → Fase 3. Pedido com personalização → Fase 4.

## Arquivos a criar/alterar
- `frontend/src/` — config de personalização na tela de produto; tela/aba de sessões de personalização; hooks.

## Passos
1. Config no produto (habilitar + modelo + observações).
2. Lista/visão de sessões + status de arte.
3. Gating; unit + e2e.

## Testes
> Fundações §10.

- **Cobrir:** unit — ações escondidas sem `customization.*`; e2e — habilitar personalização + escolher modelo reflete; abrir uma sessão e mudar status de arte.

## Definition of Done
- [ ] Config de personalização no produto (habilitar + modelo + observações) + visão de sessões com status de arte.
- [ ] Gating por permissão; `tsc`/`vitest` verdes (E2E base ou follow-up).
- [ ] Itens adiados varridos → Follow-ups + README (ou "nenhum").

## Notas / Reconciliações
- Visão "quase em tempo real" = **polling** simples na V1 (doc 22); WebSocket fica para depois.

## Follow-ups
- (preencher)
