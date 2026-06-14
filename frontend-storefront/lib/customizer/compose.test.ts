import { describe, expect, it, vi } from "vitest"

import { type ArtScene, renderArt } from "@/lib/customizer/compose"
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

const W = 200
const H = 100

describe("clamp", () => {
  it("keeps values inside [lo, hi]", () => {
    expect(clamp(1.5, 0, 1)).toBe(1)
    expect(clamp(-0.2, 0, 1)).toBe(0)
    expect(clamp(0.4, 0, 1)).toBe(0.4)
  })
})

describe("renderArt", () => {
  it("draws an image at its natural aspect (no distortion)", () => {
    const ctx = mockCtx()
    const img = { width: 100, height: 50 } as HTMLImageElement
    const scene: ArtScene = {
      maxFontSize: 96,
      images: new Map([["u1", img]]),
      layers: [
        {
          id: "l1",
          kind: "image",
          area_id: "front",
          z: 0,
          transform: { x: 0.5, y: 0.5, scale: 0.5, rotation_deg: 0 },
          upload_id: "u1",
        },
      ],
    }
    renderArt(ctx as unknown as CanvasRenderingContext2D, W, H, scene)
    // width = 0.5*200 = 100; natural height = 100*(50/100) = 50.
    const [, , , w, h] = ctx.drawImage.mock.calls[0]
    expect(w).toBe(100)
    expect(h).toBe(50)
  })

  it("uses scale_y for free distortion when set", () => {
    const ctx = mockCtx()
    const img = { width: 100, height: 50 } as HTMLImageElement
    const scene: ArtScene = {
      maxFontSize: 96,
      images: new Map([["u1", img]]),
      layers: [
        {
          id: "l1",
          kind: "image",
          area_id: "front",
          z: 0,
          transform: {
            x: 0.5,
            y: 0.5,
            scale: 0.5,
            scale_y: 0.9,
            rotation_deg: 0,
          },
          upload_id: "u1",
        },
      ],
    }
    renderArt(ctx as unknown as CanvasRenderingContext2D, W, H, scene)
    const [, , , w, h] = ctx.drawImage.mock.calls[0]
    expect(w).toBe(100) // 0.5*200
    expect(h).toBe(90) // 0.9*100 (free height, ignores natural aspect)
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
    renderArt(ctx as unknown as CanvasRenderingContext2D, W, H, {
      layers,
      images: new Map(),
      maxFontSize: 96,
    })
    expect(ctx.fillText.mock.calls.map((c) => c[0])).toEqual(["A", "B"])
  })
})
