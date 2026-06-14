"use client"

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
