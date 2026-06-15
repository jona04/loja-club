/**
 * Unit test for the GLB optimizer. Builds a tiny GLB with an oversized texture
 * in memory (no dependency on the heavy real asset), optimizes it and asserts
 * the result is smaller, still a valid GLB, and the texture was downscaled.
 */

import assert from "node:assert/strict";
import { test } from "node:test";

import { Document, NodeIO } from "@gltf-transform/core";
import {
  ALL_EXTENSIONS,
  KHRDracoMeshCompression,
} from "@gltf-transform/extensions";
import draco3d from "draco3dgltf";
import sharp from "sharp";

import { optimizeGlb } from "./optimize-glb.mjs";

/**
 * Build a minimal valid GLB: one textured quad with a 2048² PNG texture.
 *
 * @returns {Promise<Uint8Array>} The source GLB bytes.
 */
async function buildSampleGlb() {
  const doc = new Document();
  const buffer = doc.createBuffer();

  const position = doc
    .createAccessor()
    .setType("VEC3")
    .setArray(
      // biome-ignore format: one vertex per line for readability
      new Float32Array([
        0, 0, 0,
        1, 0, 0,
        1, 1, 0,
        0, 1, 0,
      ]),
    )
    .setBuffer(buffer);
  const uv = doc
    .createAccessor()
    .setType("VEC2")
    .setArray(new Float32Array([0, 0, 1, 0, 1, 1, 0, 1]))
    .setBuffer(buffer);
  const indices = doc
    .createAccessor()
    .setType("SCALAR")
    .setArray(new Uint16Array([0, 1, 2, 0, 2, 3]))
    .setBuffer(buffer);

  // A NON-solid texture (gradient): a solid color would be folded into a
  // baseColorFactor by prune(), which is correct but would defeat the test.
  const W = 512;
  const raw = Buffer.alloc(W * W * 3);
  for (let y = 0; y < W; y++) {
    for (let x = 0; x < W; x++) {
      const i = (y * W + x) * 3;
      raw[i] = x % 256;
      raw[i + 1] = y % 256;
      raw[i + 2] = (x ^ y) % 256;
    }
  }
  const png = await sharp(raw, { raw: { width: W, height: W, channels: 3 } })
    .png()
    .toBuffer();
  const texture = doc
    .createTexture("body")
    .setMimeType("image/png")
    .setImage(new Uint8Array(png));
  const material = doc.createMaterial("body").setBaseColorTexture(texture);

  const prim = doc
    .createPrimitive()
    .setAttribute("POSITION", position)
    .setAttribute("TEXCOORD_0", uv)
    .setIndices(indices)
    .setMaterial(material);
  const node = doc.createNode().setMesh(doc.createMesh().addPrimitive(prim));
  doc.createScene().addChild(node);

  return new NodeIO().writeBinary(doc);
}

test("optimizeGlb shrinks the file, keeps it valid and downscales textures", async () => {
  const input = await buildSampleGlb();
  const { bytes, before, after } = await optimizeGlb(input, {
    textureSize: 128,
  });

  // Smaller than the source.
  assert.ok(
    after.bytes < before.bytes,
    `expected ${after.bytes} < ${before.bytes}`,
  );

  // Still a valid GLB: a Draco-aware reader can parse it back.
  const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({
    "draco3d.decoder": await draco3d.createDecoderModule(),
    "draco3d.encoder": await draco3d.createEncoderModule(),
  });
  const roundtrip = await io.readBinary(bytes);
  assert.equal(roundtrip.getRoot().listMeshes().length, 1);
  assert.ok(
    roundtrip.getRoot().listExtensionsUsed().some((e) =>
      e.extensionName === KHRDracoMeshCompression.EXTENSION_NAME,
    ),
    "expected Draco compression to be applied",
  );

  // The texture survived and was downscaled to the requested max edge (read
  // from the round-tripped output — catches a wrongly pruned texture).
  const textures = roundtrip.getRoot().listTextures();
  assert.equal(textures.length, 1, "expected the texture to survive");
  const [w, h] = textures[0].getSize();
  assert.ok(
    Math.max(w, h) === 128,
    `expected texture downscaled to 128, got ${w}x${h}`,
  );
});
