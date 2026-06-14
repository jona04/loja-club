/**
 * Editor layer types — the typed shape of `state_json.layers` (doc 30 §4).
 * Client-safe (no server imports) so both the editor and tests can use them.
 */

/** A layer's placement, normalized [0..1] inside the printable UV region. */
export interface LayerTransform {
  /** Center X within the region (0..1). */
  x: number
  /** Center Y within the region (0..1). */
  y: number
  /** Size as a fraction of the region width (images) / unused for text. */
  scale: number
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
