---
id: P7-EDITOR-01
title: Editor storefront — 2 painéis + carregar GLB + orbit/zoom + autosave
phase: 7
etapa: "Etapa 5 — Editor 3D no storefront (react-three-fiber)"
area: EDITOR
status: done
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
- Camadas de **imagem/texto**, **composição na UV**, **aprovação**, **snapshot**, **link público**: `P7-EDITOR-02`.
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
- [x] Editor abre com 2 painéis; GLB carrega do CDN (Draco); câmera gira/zoom/move (`OrbitControls` + `Bounds`); autosave (debounced) persiste a sessão; restaura pela guest session (o `start` retoma o draft).
- [x] **Modos de falha mapeados** — **WebGL indisponível** (`hasWebGL`) **e** GLB não carrega (`SceneErrorBoundary`) → fallback (fotos + aviso, sem editor); sessão **expirada** responde 410 no backend (autosave/upload). "Oferecer clonar" virou follow-up. → tratados/Follow-ups.
- [x] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- O 3D é **visualização**; a **edição** (camadas) é `P7-EDITOR-02`. Doc [30 §2](../../concepts/30_3d_customization_technical_design.md).
- **Frontend-storefront (Next/app router):** rota dedicada **`/products/[slug]/personalizar`** (server: busca o produto, 404 se não-`image_3d_customizable`) → renderiza `<Customizer>` (client). Layout **2 painéis** (`md:grid-cols-2`, empilha no mobile): `AreaPanel2D` (área imprimível) + `Scene3D` (Canvas r3f, **lazy via `next/dynamic` `ssr:false`**). GLB do CDN por `useGLTF` (Draco pelo decoder padrão do drei) + `Bounds`/`OrbitControls`. O GLB carrega **cross-origin** (CORS do CDN já ligado em `P7-ADM-01`).
- **Sessão/autosave:** Server Actions em `lib/customization-actions.ts` (espelham `cart-actions`: encaminham `Host` + cookie `guest_session_id`, re-emitem `Set-Cookie`); hook `lib/use-customizer.ts` inicia/retoma no mount e faz **autosave debounced** (`AUTOSAVE_DEBOUNCE_MS` = 800 ms, [doc 31 §4](../../concepts/31_configuration_and_constants.md)) do `state_json`. `state` só "suja" após edição → não salva no load.
- **Entrada:** os 3 templates (Aurora/Bazar/Studio) trocaram o placeholder "Personalizar em 3D" por um `Link` pra a rota, **só quando `image_3d_customizable`** (`isCustomizable`, em `lib/product.ts` — client-safe, fora do `lib/api.ts` que importa `next/headers`).
- **Testes:** vitest montado no storefront (`vitest.config.ts` + `test/setup.ts`, deps declaradas no `package.json`). Cobre: hook inicia sessão, **não** salva antes de editar, autosave dispara após o debounce; `Customizer` monta os 2 painéis e cai no fallback sem WebGL/erro de sessão. `tsc`/`biome`/`next build` limpos.

## Follow-ups
- [ ] **`dispose` de texturas/geometrias** ao fechar/trocar (perf mobile). → README da fase.
- [ ] **Chrome do template no editor** — a rota `/personalizar` é standalone (sem header/footer da loja); aplicar o `Shell` do template ativo. → README.
- [ ] **Painel 2D proporcional à superfície** (como no admin: `computeUnwrapAspect`/`onAspect`) — hoje é um quadrado de UV; refinar junto com a composição da arte. Origem: `P7-EDITOR-01` → `P7-EDITOR-02`.
- [ ] **Sessão expirada no autosave → oferecer clonar** (hoje mostra o erro do backend 410). → README.
