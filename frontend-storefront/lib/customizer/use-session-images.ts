"use client"

import { useEffect, useState } from "react"

import { loadImage } from "@/lib/customizer/compose"
import type { UploadPublic } from "@/lib/customizer/session-types"

/**
 * Loads the session's uploads into `HTMLImageElement`s (keyed by upload id) for
 * the compositor — both the ones restored from the session and ones added in
 * this browser session. Cross-origin images load with `crossOrigin` so the
 * approval snapshot canvas is not tainted.
 *
 * @param uploads - The uploads to load (id + presigned url).
 * @returns A map of `upload_id → image` (grows as images finish loading).
 */
export function useSessionImages(
  uploads: UploadPublic[],
): Map<string, HTMLImageElement> {
  const [images, setImages] = useState<Map<string, HTMLImageElement>>(new Map())

  useEffect(() => {
    let active = true
    for (const upload of uploads) {
      loadImage(upload.url)
        .then((img) => {
          if (!active) return
          setImages((current) => {
            // Skip ones already loaded; never reload.
            if (current.has(upload.id)) return current
            return new Map(current).set(upload.id, img)
          })
        })
        .catch(() => {
          // A broken/expired URL just leaves the layer without its image; the
          // editor still works and the snapshot won't include it.
        })
    }
    return () => {
      active = false
    }
  }, [uploads])

  return images
}
