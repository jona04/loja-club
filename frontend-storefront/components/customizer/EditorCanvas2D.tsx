"use client"

import {
  type PointerEvent as ReactPointerEvent,
  useEffect,
  useRef,
} from "react"

import { paintLayers } from "@/lib/customizer/compose"
import { clamp, type EditorLayer } from "@/lib/customizer/types"

const BASE_WIDTH = 480

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
    paintLayers(ctx, { x: 0, y: 0, w, h }, layers, images, maxFontSize)
    const selected = layers.find((l) => l.id === selectedId)
    if (selected) {
      ctx.strokeStyle = "rgba(234,88,12,0.9)"
      ctx.lineWidth = 2
      const cx = selected.transform.x * w
      const cy = selected.transform.y * h
      ctx.strokeRect(cx - 10, cy - 10, 20, 20)
    }
  }, [layers, images, maxFontSize, aspect, selectedId])

  const startDrag = (event: ReactPointerEvent) => {
    if (readOnly || !selectedId || !onMove) return
    event.preventDefault()
    const move = (e: PointerEvent) => {
      const box = canvasRef.current?.getBoundingClientRect()
      if (!box) return
      onMove(
        selectedId,
        clamp((e.clientX - box.left) / box.width, 0, 1),
        clamp((e.clientY - box.top) / box.height, 0, 1),
      )
    }
    move(event.nativeEvent)
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
