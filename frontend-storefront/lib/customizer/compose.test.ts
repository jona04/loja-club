import { describe, expect, it, vi } from "vitest"

import { paintLayers, type Rect } from "@/lib/customizer/compose"
import { clamp, type EditorLayer } from "@/lib/customizer/types"

function mockCtx() {
  return {
    save: vi.fn(),
    restore: vi.fn(),
    translate: vi.fn(),
    rotate: vi.fn(),
    drawImage: vi.fn(),
    fillText: vi.fn(),
    font: "",
    fillStyle: "",
    textAlign: "",
    textBaseline: "",
  }
}

const RECT: Rect = { x: 0, y: 0, w: 200, h: 100 }

describe("clamp", () => {
  it("keeps values inside [lo, hi]", () => {
    expect(clamp(1.5, 0, 1)).toBe(1)
    expect(clamp(-0.2, 0, 1)).toBe(0)
    expect(clamp(0.4, 0, 1)).toBe(0.4)
  })
})

describe("paintLayers", () => {
  it("draws an image layer when its image is loaded", () => {
    const ctx = mockCtx()
    const img = { width: 100, height: 50 } as HTMLImageElement
    const layers: EditorLayer[] = [
      {
        id: "l1",
        kind: "image",
        area_id: "front",
        z: 0,
        transform: { x: 0.5, y: 0.5, scale: 0.5, rotation_deg: 0 },
        upload_id: "u1",
      },
    ]
    paintLayers(
      ctx as unknown as CanvasRenderingContext2D,
      RECT,
      layers,
      new Map([["u1", img]]),
      96,
    )
    expect(ctx.drawImage).toHaveBeenCalledTimes(1)
  })

  it("draws text layers in z-order", () => {
    const ctx = mockCtx()
    const layers: EditorLayer[] = [
      {
        id: "b",
        kind: "text",
        area_id: "front",
        z: 1,
        transform: { x: 0.5, y: 0.5, scale: 1, rotation_deg: 0 },
        text: "B",
        font: "inter",
        font_size: 48,
        color: "#111",
      },
      {
        id: "a",
        kind: "text",
        area_id: "front",
        z: 0,
        transform: { x: 0.5, y: 0.5, scale: 1, rotation_deg: 0 },
        text: "A",
        font: "inter",
        font_size: 48,
        color: "#111",
      },
    ]
    paintLayers(
      ctx as unknown as CanvasRenderingContext2D,
      RECT,
      layers,
      new Map(),
      96,
    )
    expect(ctx.fillText.mock.calls.map((c) => c[0])).toEqual(["A", "B"])
  })
})
