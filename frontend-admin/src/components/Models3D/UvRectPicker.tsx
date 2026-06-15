import { type PointerEvent as ReactPointerEvent, useRef } from "react"

import type { UvRect } from "@/components/Models3D/AreaEditor3D"

const MIN = 0.05
const clamp = (n: number, lo: number, hi: number) =>
  Math.max(lo, Math.min(hi, n))
const round = (n: number) => Math.round(n * 1000) / 1000

/**
 * 2D picker for the printable UV rectangle: a panel that stands for the model's
 * unwrapped surface (UV space 0..1), shaped to the surface's real proportions
 * (`aspect` = width/height) so a mug's wide print reads as wide, not square.
 * Drag the orange box to move it, drag the corner handle to resize. Pairs with
 * the 3D preview, which shows the same region on the real surface.
 *
 * @param props.rect - The current UV rectangle.
 * @param props.onChange - Called with the updated rectangle on drag/resize.
 * @param props.aspect - The unwrapped surface's width/height ratio (default 1).
 * @returns The 2D UV picker.
 */
export function UvRectPicker({
  rect,
  onChange,
  aspect = 1,
}: {
  rect: UvRect
  onChange: (rect: UvRect) => void
  aspect?: number
}) {
  const ref = useRef<HTMLDivElement>(null)

  const toUv = (event: ReactPointerEvent): { u: number; v: number } => {
    const box = ref.current?.getBoundingClientRect()
    if (!box) return { u: 0, v: 0 }
    return {
      u: clamp((event.clientX - box.left) / box.width, 0, 1),
      v: clamp((event.clientY - box.top) / box.height, 0, 1),
    }
  }

  const startMove = (event: ReactPointerEvent) => {
    event.preventDefault()
    event.stopPropagation()
    const start = toUv(event)
    const ou0 = rect.u0
    const ov0 = rect.v0
    const w = rect.u1 - rect.u0
    const h = rect.v1 - rect.v0
    const target = event.currentTarget
    target.setPointerCapture(event.pointerId)
    const move = (e: PointerEvent) => {
      const box = ref.current?.getBoundingClientRect()
      if (!box) return
      const u = clamp((e.clientX - box.left) / box.width, 0, 1)
      const v = clamp((e.clientY - box.top) / box.height, 0, 1)
      const u0 = clamp(ou0 + (u - start.u), 0, 1 - w)
      const v0 = clamp(ov0 + (v - start.v), 0, 1 - h)
      onChange({
        u0: round(u0),
        v0: round(v0),
        u1: round(u0 + w),
        v1: round(v0 + h),
      })
    }
    const up = () => {
      window.removeEventListener("pointermove", move)
      window.removeEventListener("pointerup", up)
    }
    window.addEventListener("pointermove", move)
    window.addEventListener("pointerup", up)
  }

  const startResize = (event: ReactPointerEvent) => {
    event.preventDefault()
    event.stopPropagation()
    event.currentTarget.setPointerCapture(event.pointerId)
    const move = (e: PointerEvent) => {
      const box = ref.current?.getBoundingClientRect()
      if (!box) return
      const u = clamp((e.clientX - box.left) / box.width, 0, 1)
      const v = clamp((e.clientY - box.top) / box.height, 0, 1)
      onChange({
        u0: rect.u0,
        v0: rect.v0,
        u1: round(Math.max(u, rect.u0 + MIN)),
        v1: round(Math.max(v, rect.v0 + MIN)),
      })
    }
    const up = () => {
      window.removeEventListener("pointermove", move)
      window.removeEventListener("pointerup", up)
    }
    window.addEventListener("pointermove", move)
    window.addEventListener("pointerup", up)
  }

  const pct = (n: number) => `${n * 100}%`

  return (
    <div className="space-y-1.5">
      <div className="text-xs text-muted-foreground">
        Espaço UV do modelo (desembrulhado) — arraste a caixa pra mover, a alça
        pra redimensionar.
      </div>
      <div
        ref={ref}
        className="relative w-full max-w-md rounded-md border bg-[repeating-conic-gradient(#e5e7eb_0_25%,#fff_0_50%)] bg-[length:24px_24px]"
        style={{ aspectRatio: aspect }}
      >
        <div
          className="absolute cursor-move border-2 border-orange-500 bg-orange-500/30"
          style={{
            left: pct(Math.min(rect.u0, rect.u1)),
            top: pct(Math.min(rect.v0, rect.v1)),
            width: pct(Math.abs(rect.u1 - rect.u0)),
            height: pct(Math.abs(rect.v1 - rect.v0)),
          }}
          onPointerDown={startMove}
        >
          <div
            className="absolute right-0 bottom-0 h-3 w-3 translate-x-1/2 translate-y-1/2 cursor-se-resize rounded-full bg-orange-600"
            onPointerDown={startResize}
          />
        </div>
      </div>
    </div>
  )
}
