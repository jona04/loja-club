"use client"

import type { PrintableArea } from "@/lib/customization-actions"

/**
 * The 2D editing panel: the model's printable area as a region on a neutral
 * board, where the customer will place art (layers land in P7-EDITOR-02). For
 * now it shows *where* the print goes; it is not yet interactive.
 *
 * @param props.area - The printable area (UV rectangle + label).
 * @returns The 2D area panel.
 */
export function AreaPanel2D({ area }: { area: PrintableArea | null }) {
  const rect = area?.uv_rect
  const pct = (n: number) => `${n * 100}%`
  return (
    <div className="flex flex-col gap-2">
      <span className="text-sm font-medium text-gray-700">
        {area?.label ?? "Área de personalização"}
      </span>
      <div className="relative aspect-square w-full overflow-hidden rounded-md border bg-[repeating-conic-gradient(#e5e7eb_0_25%,#fff_0_50%)] bg-[length:24px_24px]">
        {rect && (
          <div
            className="absolute border-2 border-orange-500 bg-orange-500/20"
            style={{
              left: pct(Math.min(rect.u0, rect.u1)),
              top: pct(Math.min(rect.v0, rect.v1)),
              width: pct(Math.abs(rect.u1 - rect.u0)),
              height: pct(Math.abs(rect.v1 - rect.v0)),
            }}
          />
        )}
      </div>
      <p className="text-xs text-gray-500">
        Em breve: adicione imagem e texto aqui — o 3D atualiza ao lado.
      </p>
    </div>
  )
}
