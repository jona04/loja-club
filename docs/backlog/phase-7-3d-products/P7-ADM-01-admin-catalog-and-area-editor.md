---
id: P7-ADM-01
title: Admin — habilitar/desabilitar + editor visual da área imprimível
phase: 7
etapa: "Etapa 2 — Admin: habilitar/desabilitar + editar a área imprimível"
area: ADM
status: done
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
- [x] Admin **habilita/desabilita** (modelo) e **edita a área/limites** (versão, persistido); editar afeta só **sessões novas** (o congelamento copia no pedido → `P7-ORD-01`).
- [x] **Modos de falha mapeados** — área malformada (sem `id`) → **422** (testado); modelo/versão inexistente → **404** (testado); editar versão vale só p/ sessões novas (design). → tratados.
- [x] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- **Backend:** 3 rotas em `platform_admin` (`GET /platform/3d-models`, `PATCH /platform/3d-models/{model_id}`, `PATCH /platform/3d-models/versions/{version_id}`), gated `platform.3d_models.view`/`.manage` (já no catálogo de permissões). Lógica/validação em `customization.services`. **6 testes** ✅.
- **Frontend-admin:** tela **"Modelos 3D"** (`/_layout/models-3d`) — lista + ativar/desativar + **editor visual 3D da área** + campos numéricos (size_cm/proporção/camadas) + JSON p/ `text_config`/`art_limits`; coluna GLB com **Ver 3D** (viewer read-only `ModelViewer3D`, girar/zoom) e **Baixar**. Client OpenAPI regenerado.
- **CORS do CDN:** o GLB carrega cross-origin no `three.js`; foi preciso ligar `Access-Control-Allow-Origin` no CloudFront (response-headers-policy `SimpleCORS` + invalidação). Sem código — config de CDN (doc [30 §6](../../concepts/30_3d_customization_technical_design.md)); reproduzir em prod (Follow-up no README).
- **Editor visual da área = região de UV** (`components/Models3D/{AreaEditor3D,UvRectPicker}.tsx`): `@react-three/fiber` + `@react-three/drei` + `three` (adicionados ao `frontend-admin`; `bun.lock` atualizado). **Picker 2D** (`UvRectPicker`) = painel do espaço UV com retângulo arrastável/redimensionável; **preview 3D** (`AreaEditor3D`) carrega o GLB (`useGLTF`, Draco), `OrbitControls`, e pinta a `uv_rect` **na superfície real** via um overlay com a UV do mesh (acompanha a curvatura/dobras). A arte/área é **mapeada pela UV do GLB** (não projeção) → cola na superfície. Chunk **lazy** (~270 KB gzip). É o **componente reusável na Fase 12**.
- **Picker proporcional à superfície** (não quadrado): o `AreaEditor3D` mede a geometria (`computeUnwrapAspect` — `r` mediano em XZ, vão em Y → `2πr ÷ h`) e devolve o aspecto via `onAspect`; o `UvRectPicker` aplica `aspect-ratio`, então a região aparece nas proporções reais (a faixa da caneca é ~2,5× mais larga que alta) e não engana o lojista com um quadrado. Doc [30 §3](../../concepts/30_3d_customization_technical_design.md).
- **Auto-enquadramento** (`AreaEditor3D` **e** `ModelViewer3D`): a câmera usa o `Bounds` do drei (`fit clip observe`) — enquadra o modelo qualquer que seja a escala real do GLB (a caneca tem ~0,9 unidades, não metros), então a câmera **nunca começa dentro** do modelo. Ambos os 3D carregam a URL com `?v=<versionId>` (cache-bust do browser).

## Follow-ups
- [ ] **QA visual no browser** do editor 3D (a caneca carrega? o retângulo projeta certo na superfície? arrastar/girar/redimensionar fluido?) — não dá pra inspecionar 3D fora do browser. Origem: `P7-ADM-01`. → README da fase.
- [ ] **e2e Playwright** do admin 3D (lista/toggle/editar área) — *Quando:* infra de e2e do admin. → README da fase.
- [ ] **Aspecto da arte do cliente na vitrine** — o admin já enquadra o picker no aspecto físico da superfície; o editor do storefront (`P7-EDITOR-02`) deve enquadrar o upload no aspecto da `uv_rect` pra o cliente mandar arte na proporção certa (faixa ~2:1, não quadrada). → README da fase.
