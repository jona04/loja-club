"use client"

import {
  type PointerEvent as ReactPointerEvent,
  useEffect,
  useRef,
} from "react"

import { renderArt } from "@/lib/customizer/compose"
import { clamp, type EditorLayer } from "@/lib/customizer/types"

const BASE_WIDTH = 480

/** Half width/height of an image layer as a fraction of the region. */
function layerHalfExtent(
  layer: EditorLayer,
  images: Map<string, HTMLImageElement>,
  aspect: number,
): { halfW: number; halfH: number } {
  if (layer.kind !== "image") return { halfW: 0, halfH: 0 }
  const scale = layer.transform.scale
  const img = images.get(layer.upload_id)
  const halfW = scale / 2
  const halfH =
    layer.transform.scale_y != null
      ? layer.transform.scale_y / 2
      : img && img.width > 0
        ? (scale * aspect * (img.height / img.width)) / 2
        : scale / 2
  return { halfW, halfH }
}

/**
 * Clamp a layer's center on one axis so the layer can travel the whole region:
 * if it is larger than the region it pans until an edge meets the region edge
 * (always covering it); if smaller it stays fully inside. `half` is the layer's
 * half-extent as a fraction of the region.
 */
function clampAxis(center: number, half: number): number {
  return half >= 0.5
    ? clamp(center, 1 - half, half)
    : clamp(center, half, 1 - half)
}

interface Props {
  layers: EditorLayer[]
  images: Map<string, HTMLImageElement>
  maxFontSize: number
  /** Width/height of the printable region (its real proportions). */
  aspect: number
  selectedId: string | null
  readOnly?: boolean
  /** Move the selected layer to a clamped normalized center. */
  onMove?: (id: string, x: number, y: number) => void
}

/**
 * The 2D editing surface: the printable region at its real proportions, where
 * the art is composed. Drag moves the selected layer (its center is clamped to
 * stay inside the region). Read-only mode (public link) disables dragging.
 *
 * @param props - Layers, loaded images, max font size, region aspect, the
 *   selected layer id, read-only flag and a move callback.
 * @returns The 2D canvas panel.
 */
export function EditorCanvas2D({
  layers,
  images,
  maxFontSize,
  aspect,
  selectedId,
  readOnly = false,
  onMove,
}: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    const ctx = canvas?.getContext("2d")
    if (!canvas || !ctx) return
    const w = BASE_WIDTH
    const h = Math.max(1, Math.round(BASE_WIDTH / (aspect || 1)))
    canvas.width = w
    canvas.height = h
    ctx.clearRect(0, 0, w, h)
    renderArt(ctx, w, h, { layers, images, maxFontSize })
    const selected = layers.find((l) => l.id === selectedId)
    if (selected) {
      ctx.strokeStyle = "rgba(234,88,12,0.9)"
      ctx.lineWidth = 2
      // Pin the marker to the region edge so it never leaves the rectangle, even
      // when a large layer's center is panned outside it.
      const cx = clamp(selected.transform.x * w, 10, w - 10)
      const cy = clamp(selected.transform.y * h, 10, h - 10)
      ctx.strokeRect(cx - 10, cy - 10, 20, 20)
    }
  }, [layers, images, maxFontSize, aspect, selectedId])

  const startDrag = (event: ReactPointerEvent) => {
    if (readOnly || !selectedId || !onMove) return
    const layer = layers.find((l) => l.id === selectedId)
    const box = canvasRef.current?.getBoundingClientRect()
    if (!layer || !box) return
    event.preventDefault()
    // Relative drag: remember where the layer was and where we grabbed, then
    // move by the pointer delta — so a click never re-centers and the layer can
    // travel the whole region.
    const grabX = (event.clientX - box.left) / box.width
    const grabY = (event.clientY - box.top) / box.height
    const originX = layer.transform.x
    const originY = layer.transform.y
    const { halfW, halfH } = layerHalfExtent(layer, images, aspect)
    const move = (e: PointerEvent) => {
      const b = canvasRef.current?.getBoundingClientRect()
      if (!b) return
      const dx = (e.clientX - b.left) / b.width - grabX
      const dy = (e.clientY - b.top) / b.height - grabY
      onMove(
        selectedId,
        clampAxis(originX + dx, halfW),
        clampAxis(originY + dy, halfH),
      )
    }
    const up = () => {
      window.removeEventListener("pointermove", move)
      window.removeEventListener("pointerup", up)
    }
    window.addEventListener("pointermove", move)
    window.addEventListener("pointerup", up)
  }

  return (
    <div className="flex flex-col gap-2">
      <span className="text-sm font-medium text-gray-700">
        Área de personalização
      </span>
      <div
        className="w-full overflow-hidden rounded-md border bg-[repeating-conic-gradient(#eee_0_25%,#fff_0_50%)] bg-[length:20px_20px]"
        style={{ aspectRatio: aspect || 1 }}
      >
        <canvas
          ref={canvasRef}
          onPointerDown={startDrag}
          className={`h-full w-full ${readOnly ? "" : "cursor-move touch-none"}`}
        />
      </div>
      {!readOnly && (
        <p className="text-xs text-gray-500">
          Selecione uma camada e arraste aqui para posicionar.
        </p>
      )}
    </div>
  )
}
