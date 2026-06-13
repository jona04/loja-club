---
id: P7-EDITOR-01
title: Editor storefront — 2 painéis + carregar GLB + orbit/zoom + autosave
phase: 7
etapa: "Etapa 5 — Editor 3D no storefront (react-three-fiber)"
area: EDITOR
status: todo
depends_on: [P7-SESS-01, P7-CAT-01]
blocks: [P7-EDITOR-02]
tests: [unit]
---

# P7-EDITOR-01 — Editor 3D (shell): 2 painéis + GLB + câmera + autosave

## Contexto
A **casca** do editor 3D do storefront: o layout de **2 painéis** (2D edita / 3D preview), carregar o GLB do catálogo e a navegação de câmera (girar/zoom/mover). As **camadas** (imagem/texto) e a aprovação são o `P7-EDITOR-02`.

## Docs de referência
- [30 — §2 Arquitetura do editor (layout/2 painéis) / §10 Performance](../../concepts/30_3d_customization_technical_design.md)
- [10 — Storefront (editor 3D)](../../concepts/10_storefront_and_layouts.md)

## Escopo (o que ENTRA)
- Componente **client-only** (`"use client"`, `next/dynamic` `ssr:false`, **lazy**) com **react-three-fiber + drei**.
- **Layout de 2 painéis** (doc [30 §2](../../concepts/30_3d_customization_technical_design.md)): **painel 2D** (retângulo da área imprimível) + **painel 3D** (preview). Responsivo: mobile empilha/abas.
- **Carregar o GLB** da versão escolhida (CDN, `useGLTF` + **DRACOLoader**, `Suspense`/placeholder).
- **`OrbitControls`**: girar / **zoom** / mover a câmera.
- **Autosave** do `state_json` (debounce → `PUT` da sessão, `P7-SESS-01`); **restaurar** pela `guest_session_id`.

## Fora de escopo (o que NÃO entra)
- Camadas de **imagem/texto**, **decal**, **aprovação**, **snapshot**, **link público**: `P7-EDITOR-02`.
- Backend de sessão: `P7-SESS-01`.

## Arquivos a criar/alterar
- `frontend-storefront/...` (criar) — componente do editor (shell), hook de sessão/autosave, integração com a página de produto (`Personalizar`).
- dependências r3f/drei no workspace bun (raiz).

## Passos
1. Scaffolding do editor (lazy, client-only) + layout 2 painéis (responsivo).
2. Carregar GLB (Draco) + `OrbitControls` (girar/zoom/mover).
3. Hook de sessão: iniciar/restaurar + **autosave** debounced do `state_json`.

## Testes
- **Níveis:** unit (vitest).
- **Quando escrever:** durante.
- **Cobrir:** unit — o componente monta os 2 painéis; autosave dispara (debounced) ao mudar o estado; fallback quando o GLB não resolve.

## Definition of Done
- [ ] Editor abre com 2 painéis; GLB carrega do CDN; câmera gira/zoom/move; autosave persiste a sessão; restaura pela guest session.
- [ ] **Modos de falha mapeados** — **WebGL indisponível**/GLB não carrega → fallback (imagens + aviso, Personalizar desabilitado); autosave em sessão expirada → oferecer clonar. → tratados/Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- O 3D é **visualização**; a **edição** acontece no painel 2D (`P7-EDITOR-02`). Doc [30 §2](../../concepts/30_3d_customization_technical_design.md).

## Follow-ups
- [ ] **`dispose` de texturas/geometrias** ao fechar/trocar (perf mobile) — *Quando:* polir performance. → README da fase.
