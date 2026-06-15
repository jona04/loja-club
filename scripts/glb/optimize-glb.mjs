/**
 * GLB pre-processing pipeline: turn a heavy 4K source GLB (e.g. a Tripo3D
 * export, ~56 MB) into a web-ready asset (a few MB) for the storefront editor.
 *
 * Pipeline (doc 30 §1): dedup + weld + (optional) simplify + downscale textures
 * to a max edge + Draco mesh compression. Keeps the texture FORMAT (only resizes)
 * so it stays broadly loadable by three.js.
 *
 * Used as a library (unit-tested) and as a CLI:
 *   node optimize-glb.mjs <input.glb> <output.glb> [--texture-size 2048] [--simplify 0.75]
 */

import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { NodeIO } from "@gltf-transform/core";
import {
  ALL_EXTENSIONS,
  KHRDracoMeshCompression,
} from "@gltf-transform/extensions";
import {
  dedup,
  prune,
  simplify,
  textureCompress,
  weld,
} from "@gltf-transform/functions";
import draco3d from "draco3dgltf";
import { MeshoptSimplifier } from "meshoptimizer";
import sharp from "sharp";

/**
 * Build a NodeIO that can read and write Draco-compressed GLB.
 *
 * @returns {Promise<NodeIO>} An IO with all extensions + Draco encoder/decoder.
 */
async function makeIO() {
  return new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({
    "draco3d.decoder": await draco3d.createDecoderModule(),
    "draco3d.encoder": await draco3d.createEncoderModule(),
  });
}

/**
 * Summarize a document: triangle count and the largest texture edge.
 *
 * @param {import("@gltf-transform/core").Document} doc - The glTF document.
 * @param {number} byteLength - Size in bytes of the (de)serialized GLB.
 * @returns {{bytes:number, triangles:number, maxTexture:number}} The stats.
 */
function stats(doc, byteLength) {
  let triangles = 0;
  for (const mesh of doc.getRoot().listMeshes()) {
    for (const prim of mesh.listPrimitives()) {
      const indices = prim.getIndices();
      const position = prim.getAttribute("POSITION");
      const count = indices ? indices.getCount() : (position?.getCount() ?? 0);
      triangles += Math.floor(count / 3);
    }
  }
  let maxTexture = 0;
  for (const texture of doc.getRoot().listTextures()) {
    const size = texture.getSize();
    if (size) {
      maxTexture = Math.max(maxTexture, size[0], size[1]);
    }
  }
  return { bytes: byteLength, triangles, maxTexture };
}

/** Rotate vector `v` by quaternion `q` (xyzw), writing into `out`. */
function quatRotate(out, q, v) {
  const [x, y, z, w] = q;
  const [vx, vy, vz] = v;
  const tx = 2 * (y * vz - z * vy);
  const ty = 2 * (z * vx - x * vz);
  const tz = 2 * (x * vy - y * vx);
  out[0] = vx + w * tx + (y * tz - z * ty);
  out[1] = vy + w * ty + (z * tx - x * tz);
  out[2] = vz + w * tz + (x * ty - y * tx);
  return out;
}

/**
 * Bake each node's local TRS into its mesh geometry and reset the node to
 * identity, so the mesh data is **upright in its own space** (no hidden node
 * rotation). Tripo "straightens" a model via a node rotation, which leaves the
 * raw POSITION tilted — that would tilt the computed cylindrical UV. Baking
 * fixes it. Handles the common single-mesh-per-node case (Tripo output).
 *
 * @param {import("@gltf-transform/core").Document} doc - The glTF document.
 */
function bakeNodeTransforms(doc) {
  for (const node of doc.getRoot().listNodes()) {
    const mesh = node.getMesh();
    if (!mesh) continue;
    const t = node.getTranslation();
    const q = node.getRotation();
    const s = node.getScale();
    const identity =
      t[0] === 0 && t[1] === 0 && t[2] === 0 &&
      q[0] === 0 && q[1] === 0 && q[2] === 0 && q[3] === 1 &&
      s[0] === 1 && s[1] === 1 && s[2] === 1;
    if (identity) continue;
    for (const prim of mesh.listPrimitives()) {
      const pos = prim.getAttribute("POSITION");
      if (pos) {
        const v = [0, 0, 0];
        const o = [0, 0, 0];
        for (let i = 0; i < pos.getCount(); i++) {
          pos.getElement(i, v);
          o[0] = v[0] * s[0];
          o[1] = v[1] * s[1];
          o[2] = v[2] * s[2];
          quatRotate(o, q, [o[0], o[1], o[2]]);
          o[0] += t[0];
          o[1] += t[1];
          o[2] += t[2];
          pos.setElement(i, o);
        }
      }
      const nrm = prim.getAttribute("NORMAL");
      if (nrm) {
        const v = [0, 0, 0];
        const o = [0, 0, 0];
        for (let i = 0; i < nrm.getCount(); i++) {
          nrm.getElement(i, v);
          quatRotate(o, q, v);
          const len = Math.hypot(o[0], o[1], o[2]) || 1;
          nrm.setElement(i, [o[0] / len, o[1] / len, o[2] / len]);
        }
      }
    }
    node.setTranslation([0, 0, 0]).setRotation([0, 0, 0, 1]).setScale([1, 1, 1]);
  }
}

/**
 * Add a clean **cylindrical** UV as a second channel (`TEXCOORD_1`), computed
 * from the geometry: `u` = angle around the Y axis, `v` = normalized height.
 * The original `TEXCOORD_0` (and its baked textures) is kept; the printable art
 * uses this channel, so a UV rectangle maps to a continuous band on the
 * cylinder (a real unwrap — the art follows the surface, not a projection).
 * Note: the wrap seam (back, u≈0/1) is not split, so a front band avoids it.
 *
 * @param {import("@gltf-transform/core").Document} doc - The glTF document.
 */
function addCylindricalUv(doc) {
  for (const mesh of doc.getRoot().listMeshes()) {
    for (const prim of mesh.listPrimitives()) {
      const pos = prim.getAttribute("POSITION");
      if (!pos) continue;
      const count = pos.getCount();
      const el = [0, 0, 0];
      // Scan the (post-bake) Y range directly — don't trust cached min/max.
      let minY = Number.POSITIVE_INFINITY;
      let maxY = Number.NEGATIVE_INFINITY;
      for (let i = 0; i < count; i++) {
        pos.getElement(i, el);
        if (el[1] < minY) minY = el[1];
        if (el[1] > maxY) maxY = el[1];
      }
      const spanY = maxY - minY || 1;
      const uv = new Float32Array(count * 2);
      for (let i = 0; i < count; i++) {
        pos.getElement(i, el);
        uv[i * 2] = Math.atan2(el[0], el[2]) / (2 * Math.PI) + 0.5;
        uv[i * 2 + 1] = 1 - (el[1] - minY) / spanY;
      }
      const accessor = doc
        .createAccessor()
        .setType("VEC2")
        .setArray(uv)
        .setBuffer(pos.getBuffer());
      prim.setAttribute("TEXCOORD_1", accessor);
    }
  }
}

/**
 * Optimize a GLB for the web.
 *
 * @param {Uint8Array} inputBytes - The source GLB bytes.
 * @param {{textureSize?:number, simplifyRatio?:number|null, simplifyError?:number, cylindricalUv?:boolean}} [opts]
 *   textureSize: max texture edge in px (default 2048); simplifyRatio: target
 *   fraction of triangles to keep (null = skip mesh simplification);
 *   simplifyError: simplification error tolerance; cylindricalUv: add a clean
 *   cylindrical `TEXCOORD_1` for the printable art.
 * @returns {Promise<{bytes:Uint8Array, before:object, after:object}>}
 *   The optimized bytes plus before/after stats.
 */
export async function optimizeGlb(inputBytes, opts = {}) {
  const {
    textureSize = 2048,
    simplifyRatio = null,
    simplifyError = 0.001,
    cylindricalUv = false,
  } = opts;
  const io = await makeIO();
  const doc = await io.readBinary(inputBytes);
  const before = stats(doc, inputBytes.byteLength);

  // Bake any node rotation/scale into the geometry first, so the mesh is upright
  // in its own space (Tripo "straightens" via a node rotation that would
  // otherwise tilt the computed cylindrical UV).
  bakeNodeTransforms(doc);

  const transforms = [dedup(), weld()];
  if (simplifyRatio != null) {
    await MeshoptSimplifier.ready;
    transforms.push(
      simplify({
        simplifier: MeshoptSimplifier,
        ratio: simplifyRatio,
        error: simplifyError,
      }),
    );
  }
  // prune (drop unused nodes/materials/textures from the source) BEFORE
  // resizing, so texture downscale is the last thing to touch the survivors.
  transforms.push(
    prune({ keepLeaves: false }),
    textureCompress({ encoder: sharp, resize: [textureSize, textureSize] }),
  );
  await doc.transform(...transforms);

  if (cylindricalUv) {
    addCylindricalUv(doc);
  }

  // Enable Draco mesh compression on write.
  doc
    .createExtension(KHRDracoMeshCompression)
    .setRequired(true)
    .setEncoderOptions({
      method: KHRDracoMeshCompression.EncoderMethod.EDGEBREAKER,
    });

  const bytes = await io.writeBinary(doc);
  const after = stats(doc, bytes.byteLength);
  return { bytes, before, after };
}

/** Format a byte count as MB with two decimals. */
const mb = (n) => `${(n / 1024 / 1024).toFixed(2)} MB`;

/**
 * CLI entry: read args, optimize the input GLB and write the output.
 *
 * @returns {Promise<void>} Resolves after writing the optimized file.
 */
async function main() {
  const [, , inPath, outPath, ...rest] = process.argv;
  if (!inPath || !outPath) {
    console.error(
      "usage: node optimize-glb.mjs <input.glb> <output.glb> [--texture-size N] [--simplify RATIO]",
    );
    process.exit(2);
  }
  let textureSize = 2048;
  let simplifyRatio = null;
  let cylindricalUv = false;
  for (let i = 0; i < rest.length; i++) {
    if (rest[i] === "--texture-size") {
      textureSize = Number(rest[++i]);
    } else if (rest[i] === "--simplify") {
      simplifyRatio = Number(rest[++i]);
    } else if (rest[i] === "--cylindrical-uv") {
      cylindricalUv = true;
    }
  }

  const input = readFileSync(inPath);
  const { bytes, before, after } = await optimizeGlb(input, {
    textureSize,
    simplifyRatio,
    cylindricalUv,
  });
  writeFileSync(outPath, bytes);

  console.log(`optimized ${inPath} -> ${outPath}`);
  console.log(
    `  size:      ${mb(before.bytes)} -> ${mb(after.bytes)} (${((1 - after.bytes / before.bytes) * 100).toFixed(1)}% smaller)`,
  );
  console.log(`  triangles: ${before.triangles} -> ${after.triangles}`);
  console.log(`  texture:   ${before.maxTexture}px -> ${after.maxTexture}px`);
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  main().catch((err) => {
    console.error(err);
    process.exit(1);
  });
}
