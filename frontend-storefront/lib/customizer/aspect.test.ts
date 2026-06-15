import type { BufferGeometry } from "three"
import { describe, expect, it } from "vitest"

import { computeUnwrapAspect, regionAspect } from "@/lib/customizer/aspect"

describe("regionAspect", () => {
  it("multiplies the UV proportions by the unwrap aspect", () => {
    const uv = { u0: 0.2, v0: 0.3, u1: 0.8, v1: 0.7 } // du=0.6, dv=0.4
    expect(regionAspect(uv, 3)).toBeCloseTo((0.6 / 0.4) * 3)
  })
})

describe("computeUnwrapAspect", () => {
  it("returns 2πr/h for a unit cylinder (r=1, h=2)", () => {
    const n = 64
    const pos = {
      count: n,
      getX: (i: number) => Math.cos((i / n) * Math.PI * 2),
      getZ: (i: number) => Math.sin((i / n) * Math.PI * 2),
      getY: (i: number) => (i % 2 === 0 ? -1 : 1),
    }
    const geometry = {
      attributes: { position: pos },
    } as unknown as BufferGeometry
    expect(computeUnwrapAspect(geometry)).toBeCloseTo(Math.PI, 1)
  })
})
