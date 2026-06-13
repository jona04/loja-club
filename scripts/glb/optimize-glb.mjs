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

/**
 * Optimize a GLB for the web.
 *
 * @param {Uint8Array} inputBytes - The source GLB bytes.
 * @param {{textureSize?:number, simplifyRatio?:number|null, simplifyError?:number}} [opts]
 *   textureSize: max texture edge in px (default 2048); simplifyRatio: target
 *   fraction of triangles to keep (null = skip mesh simplification);
 *   simplifyError: simplification error tolerance.
 * @returns {Promise<{bytes:Uint8Array, before:object, after:object}>}
 *   The optimized bytes plus before/after stats.
 */
export async function optimizeGlb(inputBytes, opts = {}) {
  const { textureSize = 2048, simplifyRatio = null, simplifyError = 0.001 } =
    opts;
  const io = await makeIO();
  const doc = await io.readBinary(inputBytes);
  const before = stats(doc, inputBytes.byteLength);

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
  for (let i = 0; i < rest.length; i++) {
    if (rest[i] === "--texture-size") {
      textureSize = Number(rest[++i]);
    } else if (rest[i] === "--simplify") {
      simplifyRatio = Number(rest[++i]);
    }
  }

  const input = readFileSync(inPath);
  const { bytes, before, after } = await optimizeGlb(input, {
    textureSize,
    simplifyRatio,
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
