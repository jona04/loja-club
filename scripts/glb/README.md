# GLB pre-processing (`scripts/glb`)

Pipeline that turns a heavy **4K source GLB** (e.g. a Tripo3D export, ~56 MB) into a **web-ready** asset (a few MB) for the storefront 3D editor. Implements the **gate** of the Fase 7 pipeline — task [`P7-ASSET-01`](../../docs/backlog/phase-7-3d-products/P7-ASSET-01-glb-preprocessing-pipeline.md) (doc [30 §1](../../docs/concepts/30_3d_customization_technical_design.md)).

> **Standalone** — this folder is **not** part of the bun workspace; it has its own `package.json`/`node_modules`. Install once with `npm install` here.

## 1. Optimize (Node)

```bash
cd scripts/glb
npm install                     # once
# mug (cylindrical product): simplify + clean cylindrical UV for the print
# (the published v1 — ~2 MB, 491k tris):
node optimize-glb.mjs ../../glb-models/ceramic-mug-3d-model.glb dist/mug.glb \
  --texture-size 2048 --simplify 0.25 --cylindrical-uv
```

Pipeline: `dedup` + `weld` + (optional) `simplify` + (optional) **`--cylindrical-uv`** + downscale textures to a max edge + **Draco**. Texture **format is kept** (only resized). Prints size/triangle/texture before→after.

**`--cylindrical-uv`** adds a clean cylindrical UV as a second channel (`TEXCOORD_1`): `u` = angle around the Y axis, `v` = height. The original `TEXCOORD_0` (baked textures) is kept; the **printable art uses channel 1**, so a UV rectangle maps to a continuous band on the surface (a real unwrap, not a projection). Needed because the Tripo auto-UV is fragmented. Use it for **cylindrical products** (mug, bottle); models with a clean baked UV (e.g. a Blender-unwrapped fabric) don't need it.

Test (in-memory sample, no network/heavy asset):

```bash
cd scripts/glb && node --test
```

## 2. Upload to the CDN (Python — reuses `app.core.storage`)

```bash
cd backend
uv run python scripts/upload_glb.py ../scripts/glb/dist/mug.glb ceramic-mug 1
# -> public/3d-models/ceramic-mug/v1/model.glb  + prints the public CDN URL
```

The printed CDN URL is what the catalog seed (`P7-CAT-01`) stores in `platform_3d_model_versions.glb_url`.

> Source GLBs live in `glb-models/` (gitignored). When a new public model is added, drop the 4K GLB there and run this pipeline.
