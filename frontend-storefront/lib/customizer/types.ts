/**
 * Editor layer types — the typed shape of `state_json.layers` (doc 30 §4).
 * Client-safe (no server imports) so both the editor and tests can use them.
 */

/** A layer's placement, normalized [0..1] inside the printable region. */
export interface LayerTransform {
  /** Center X within the region (0..1). */
  x: number
  /** Center Y within the region (0..1). */
  y: number
  /** Width as a fraction of the region width (images); image keeps its natural
   * aspect unless `scale_y` is set. */
  scale: number
  /** Optional height as a fraction of the region height — set only when the
   * user opts into free (non-uniform) distortion; `null`/absent = natural. */
  scale_y?: number | null
  rotation_deg: number
}

interface BaseLayer {
  id: string
  area_id: string
  z: number
  transform: LayerTransform
}

/** A raster image layer, referencing a private upload. */
export interface ImageLayer extends BaseLayer {
  kind: "image"
  upload_id: string
}

/** A text layer rendered to a canvas. */
export interface TextLayer extends BaseLayer {
  kind: "text"
  text: string
  font: string
  font_size: number
  color: string
}

export type EditorLayer = ImageLayer | TextLayer

/** Clamp a value into the inclusive range [lo, hi]. */
export const clamp = (n: number, lo: number, hi: number): number =>
  Math.max(lo, Math.min(hi, n))

/** A fresh layer id (unique enough for an editing session). */
export const newLayerId = (): string =>
  `l_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 7)}`
