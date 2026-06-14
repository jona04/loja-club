import type { EditorLayer } from "@/lib/customizer/types"

/** Texture resolution for the 3D art overlay (doc 31 §4). */
export const EDITOR_TEXTURE_SIZE = 1024

/** Resolution (px width) of the high-quality production composite (doc 31 §4). */
export const COMPOSITE_WIDTH = 2048

// The largest allowed font occupies this fraction of the region height.
const TEXT_MAX_HEIGHT_FRACTION = 0.6

const FONT_STACKS: Record<string, string> = {
  inter: "'Inter', sans-serif",
  roboto: "'Roboto', sans-serif",
  montserrat: "'Montserrat', sans-serif",
}

/** Map a catalog font key to a CSS family (fallback to a generic stack). */
function cssFont(key: string): string {
  return FONT_STACKS[key] ?? "sans-serif"
}

/** The art to compose: ordered layers + their loaded images + the size cap. */
export interface ArtScene {
  layers: EditorLayer[]
  images: Map<string, HTMLImageElement>
  maxFontSize: number
}

/**
 * Render the art into a **physical art space**: a context whose pixel box `w×h`
 * already has the printable region's real proportions (`w/h = regionAspect`).
 *
 * Drawing here is undistorted by construction — an image keeps its natural
 * aspect, text is not stretched. The 2D panel shows this directly; the 3D
 * overlay draws this canvas into the (square) UV sub-region, which the cylindrical
 * UV then maps back onto the real surface — so both sides look identical and the
 * art never warps. This same render is the production composite.
 *
 * @param ctx - The 2D context to draw into.
 * @param w - Physical-space width in px.
 * @param h - Physical-space height in px.
 * @param scene - The layers, loaded images and max font size.
 */
export function renderArt(
  ctx: CanvasRenderingContext2D,
  w: number,
  h: number,
  scene: ArtScene,
): void {
  for (const layer of [...scene.layers].sort((a, b) => a.z - b.z)) {
    const t = layer.transform
    ctx.save()
    ctx.translate(t.x * w, t.y * h)
    ctx.rotate((t.rotation_deg * Math.PI) / 180)
    if (layer.kind === "image") {
      const img = scene.images.get(layer.upload_id)
      if (img && img.width > 0) {
        const pw = Math.max(1, t.scale * w)
        // Natural aspect unless the user opted into free distortion (scale_y).
        const ph =
          t.scale_y != null
            ? Math.max(1, t.scale_y * h)
            : pw * (img.height / img.width)
        ctx.drawImage(img, -pw / 2, -ph / 2, pw, ph)
      }
    } else {
      const px =
        (layer.font_size / scene.maxFontSize) * h * TEXT_MAX_HEIGHT_FRACTION
      ctx.font = `${Math.max(1, px)}px ${cssFont(layer.font)}`
      ctx.fillStyle = layer.color
      ctx.textAlign = "center"
      ctx.textBaseline = "middle"
      ctx.fillText(layer.text, 0, 0)
    }
    ctx.restore()
  }
}

/**
 * Render the art to an offscreen canvas at physical proportions. Used for the 3D
 * overlay (drawn into the UV sub-region) and the production composite.
 *
 * @param scene - The art to compose.
 * @param regionAspect - The printable region's real width/height.
 * @param width - The output width in px (height follows the aspect).
 * @returns The rendered canvas.
 */
export function renderArtInto(
  target: HTMLCanvasElement,
  scene: ArtScene,
  regionAspect: number,
  width: number,
): void {
  const w = Math.max(1, Math.round(width))
  const h = Math.max(1, Math.round(width / (regionAspect || 1)))
  if (target.width !== w) target.width = w
  if (target.height !== h) target.height = h
  const ctx = target.getContext("2d")
  if (!ctx) return
  ctx.clearRect(0, 0, w, h)
  renderArt(ctx, w, h, scene)
}

export function renderArtCanvas(
  scene: ArtScene,
  regionAspect: number,
  width: number,
): HTMLCanvasElement {
  const canvas = document.createElement("canvas")
  renderArtInto(canvas, scene, regionAspect, width)
  return canvas
}

/**
 * Load an image for canvas compositing. `crossOrigin` is required so drawing the
 * (presigned S3) image does not taint the canvas — otherwise the approval
 * snapshot/composite (`toDataURL`/`toBlob`) would throw.
 *
 * @param url - The image URL (presigned).
 * @returns The loaded image element.
 */
export function loadImage(url: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.crossOrigin = "anonymous"
    img.onload = () => resolve(img)
    img.onerror = () => reject(new Error(`Failed to load image: ${url}`))
    img.src = url
  })
}
