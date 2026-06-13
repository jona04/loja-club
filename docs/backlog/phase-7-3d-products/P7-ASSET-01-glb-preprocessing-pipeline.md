---
id: P7-ASSET-01
title: Pipeline de pré-processamento do GLB (4K→web) + CDN
phase: 7
etapa: "Etapa 1 — Catálogo público de modelos 3D (plataforma, via seed)"
area: ASSET
status: done
depends_on: []
blocks: [P7-CAT-01]
tests: [unit]
---

# P7-ASSET-01 — Pipeline de pré-processamento do GLB (4K→web) + CDN

## Contexto
O GLB de origem **vem sempre em 4K** (texturas 4096²) — a caneca crua tem **~56 MB**, inviável de carregar no navegador. Antes de qualquer coisa (catálogo, editor) o asset precisa virar **web-ready**. Este é o **gate** da pipeline 3D. Origem dos arquivos: `glb-models/`.

## Docs de referência
- [30 — §1 Pipeline do asset / §6 Storage / §10 Performance](../../concepts/30_3d_customization_technical_design.md)

## Escopo (o que ENTRA)
- **Script de otimização** (Node, via `gltf-transform`): reamostrar texturas **4K → ~1–2K**, `weld`/`simplify` (decimate, **< ~150k tri**), **Draco**. Reproduzível, parte de `glb-models/<arquivo>.glb`.
- **Upload do GLB otimizado** ao CDN sob chave **versionada** `public/3d-models/<slug>/v<N>/model.glb` (reusa `app.core.storage`).
- Validar: arquivo final **poucos MB**, GLB **válido/carregável**, texturas ≤ alvo.

## Fora de escopo (o que NÃO entra)
- Definir a **área imprimível** e o **seed** do modelo: `P7-CAT-01`.
- Editor/preview no storefront: `P7-EDITOR-01`.
- Geração do GLB pelo lojista (API): **Fase 12**.

## Arquivos a criar/alterar
- `scripts/optimize-glb.ts` (criar) — pipeline `gltf-transform` (resample + simplify + draco).
- script/passo de **upload ao CDN** (criar) — chave versionada via `app.core.storage`.
- doc do comando no [`backend/README.md`](../../../backend/README.md) ou no doc 30.

## Passos
1. Script `gltf-transform` (resample 4K→~1–2K, weld, simplify, draco).
2. Rodar na caneca (`glb-models/ceramic-mug-3d-model.glb`) → conferir tamanho final + validade.
3. Subir o GLB otimizado ao CDN (chave versionada).
4. Documentar o comando (reproduzível pra próximos modelos).

## Testes
- **Níveis:** unit.
- **Quando escrever:** durante.
- **Cobrir:** unit — rodar a otimização num GLB de fixture reduz tamanho, mantém GLB **válido** e texturas ≤ alvo (sem depender da rede; upload é mockado).

## Definition of Done
- [x] Caneca otimizada (**2.05 MB**, perfil final) no CDN sob chave versionada; comando **reproduzível** a partir de `glb-models/`. URL: `https://dsqh10bjdo174.cloudfront.net/public/3d-models/ceramic-mug/v1/model.glb` (HTTP 200, `model/gltf-binary`, `content-length` = 2 146 376).
- [x] **Modos de falha mapeados** — GLB inválido → `io.readBinary` lança → CLI sai !=0; textura/transform falho → lança; upload falho → `SystemExit`, nada é "registrado" (o registro é o seed do `P7-CAT-01`). → tratados.
- [x] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- O pré-processamento é **automatizável (CLI)**, sem Blender; só a **área imprimível** (`P7-CAT-01`) é manual/visual. Doc [30 §1](../../concepts/30_3d_customization_technical_design.md).
- **Implementação:** otimizador Node em [`scripts/glb/`](../../../scripts/glb/) (isolado do workspace bun: `package.json`/`node_modules` próprios) — `optimize-glb.mjs` (gltf-transform: `dedup`+`weld`+opcional `simplify`+`prune`+`textureCompress` resize+**Draco**) + teste `node --test` **verde**. Upload em [`backend/scripts/upload_glb.py`](../../../backend/scripts/upload_glb.py) reusando `app.core.storage.upload_fileobj` → key `public/3d-models/<slug>/v<N>/model.glb`. `prune()` dobra textura **sólida** em `baseColorFactor` (esperado).
- **Medições na caneca real (54.8 MB, 1.96M tris, tex 4K→2K):** sem simplify → **5.49 MB**; `--simplify 0.20` → **1.74 MB** (393k tris); **`--simplify 0.25` → 2.05 MB (491k tris)**; `--simplify 0.30` → **2.33 MB** (589k tris); `--simplify 0.40` → **2.89 MB** (786k tris).
- **v1 publicado (versão final):** `node optimize-glb.mjs ../../glb-models/ceramic-mug-3d-model.glb dist/mug.glb --texture-size 2048 --simplify 0.25 --cylindrical-uv` → `uv run python scripts/upload_glb.py ../scripts/glb/dist/mug.glb ceramic-mug 1` (chave canônica `model.glb`). **Live no CDN** (2.05 MB, 491k tris). O `--cylindrical-uv` gera a UV cilíndrica limpa (`TEXCOORD_1`) — a UV automática do Tripo é fragmentada e não serve pra mapear a faixa imprimível (confirmado: o GLB cru também é fragmentado).

## Follow-ups
- [ ] **Disparar a otimização pelo admin** (upload na UI → pipeline → CDN) em vez de script local — *Quando:* quando o admin ganhar upload de GLB (cruza com Fase 12). → README da fase.
