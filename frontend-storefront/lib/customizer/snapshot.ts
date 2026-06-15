"use client"

import {
  type ArtScene,
  COMPOSITE_WIDTH,
  renderArtCanvas,
} from "@/lib/customizer/compose"

/**
 * Max approval payload (snapshot + composite) the client sends, just under the
 * Next Server/Route body limit (50 MB, doc 31 §4) to leave multipart headroom.
 * The composite is one flat PNG so it rarely approaches this, but we guard it.
 */
export const APPROVE_PAYLOAD_LIMIT_BYTES = 48 * 1024 * 1024

/**
 * Total bytes of the Blob/File parts in a form data (the upload payload size).
 *
 * @param fd - The multipart form data.
 * @returns The summed byte size of all Blob/File entries.
 */
export function formDataBytes(fd: FormData): number {
  let total = 0
  for (const value of fd.values()) {
    if (value instanceof Blob) total += value.size
  }
  return total
}

/**
 * Turn a canvas snapshot (PNG data URL) into multipart form data for the approve
 * endpoints. May throw if the canvas is tainted (cross-origin art without CORS)
 * — callers must catch and offer a retry (doc 30 §5).
 *
 * @param capture - Returns the canvas as a PNG data URL.
 * @param extra - Optional extra form fields (e.g. the public contact).
 * @returns Form data carrying the `snapshot` file plus any extras.
 */
export async function snapshotFormData(
  capture: () => string,
  extra: Record<string, string> = {},
): Promise<FormData> {
  const dataUrl = capture()
  const blob = await (await fetch(dataUrl)).blob()
  const fd = new FormData()
  fd.append("snapshot", blob, "snapshot.png")
  for (const [k, v] of Object.entries(extra)) {
    if (v) fd.append(k, v)
  }
  return fd
}

/**
 * Render the high-quality production composite (the flat rectangle of the
 * printable region, at real proportions) and append it to `fd` as `composite`.
 * Throws if the canvas cannot be encoded (e.g. tainted) so approval is blocked.
 *
 * @param fd - The approve form data to extend.
 * @param scene - The art to compose.
 * @param regionAspect - The printable region's real width/height.
 */
export async function appendComposite(
  fd: FormData,
  scene: ArtScene,
  regionAspect: number,
): Promise<void> {
  const canvas = renderArtCanvas(scene, regionAspect, COMPOSITE_WIDTH)
  const blob = await new Promise<Blob | null>((resolve) =>
    canvas.toBlob(resolve, "image/png"),
  )
  if (!blob) throw new Error("composite_failed")
  fd.append("composite", blob, "composite.png")
}
