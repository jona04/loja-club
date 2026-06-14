import type { EditorLayer } from "@/lib/customizer/types"

/** Texture resolution for the composited art (doc 31 §4). */
export const EDITOR_TEXTURE_SIZE = 1024

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

/** A pixel rectangle to paint into. */
export interface Rect {
  x: number
  y: number
  w: number
  h: number
}

/**
 * Paint the editor layers into a 2D context within `rect`, in z-order. Used for
 * both the 3D texture (rect = the UV sub-region × texture size) and the 2D panel
 * (rect = the whole panel) — one source of truth for what the art looks like.
 *
 * @param ctx - The 2D canvas context to draw into.
 * @param rect - The printable region in pixels.
 * @param layers - The editor layers (image/text).
 * @param images - Loaded images keyed by `upload_id` (image layers).
 * @param maxFontSize - The version's max text size (for the size mapping).
 */
export function paintLayers(
  ctx: CanvasRenderingContext2D,
  rect: Rect,
  layers: EditorLayer[],
  images: Map<string, HTMLImageElement>,
  maxFontSize: number,
): void {
  for (const layer of [...layers].sort((a, b) => a.z - b.z)) {
    const t = layer.transform
    ctx.save()
    ctx.translate(rect.x + t.x * rect.w, rect.y + t.y * rect.h)
    ctx.rotate((t.rotation_deg * Math.PI) / 180)
    if (layer.kind === "image") {
      const img = images.get(layer.upload_id)
      if (img && img.width > 0) {
        const w = Math.max(1, t.scale * rect.w)
        const h = w * (img.height / img.width)
        ctx.drawImage(img, -w / 2, -h / 2, w, h)
      }
    } else {
      const px =
        (layer.font_size / maxFontSize) * rect.h * TEXT_MAX_HEIGHT_FRACTION
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
 * Load an image for canvas compositing. `crossOrigin` is required so drawing the
 * (presigned S3) image does not taint the canvas — otherwise the approval
 * snapshot (`toDataURL`) would throw.
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
