import type { BufferGeometry } from "three"

/**
 * Physical aspect (width/height) of a cylindrical unwrap: circumference over
 * height (`2πr / h`), so the 2D editing panel and the customer's art are shown
 * at the surface's real proportions (a mug print is much wider than tall). `r`
 * is the median radial distance in XZ (robust to a handle); `h` is the Y span.
 *
 * @param geometry - The model geometry (upright in its own space).
 * @returns The unwrap's width/height aspect (1 if unknown).
 */
export function computeUnwrapAspect(geometry: BufferGeometry): number {
  const pos = geometry.attributes.position
  if (!pos) return 1
  const n = pos.count
  const step = Math.max(1, Math.floor(n / 4000))
  const radii: number[] = []
  let minY = Number.POSITIVE_INFINITY
  let maxY = Number.NEGATIVE_INFINITY
  for (let i = 0; i < n; i += step) {
    const x = pos.getX(i)
    const y = pos.getY(i)
    const z = pos.getZ(i)
    radii.push(Math.hypot(x, z))
    if (y < minY) minY = y
    if (y > maxY) maxY = y
  }
  radii.sort((a, b) => a - b)
  const r = radii[Math.floor(radii.length / 2)] || 1
  const h = maxY - minY || 1
  return (2 * Math.PI * r) / h
}

/**
 * The printable region's true art aspect: the UV rectangle proportions times
 * the unwrap aspect. `(Δu·circumference) / (Δv·height)` — what the customer's
 * art should be shaped like.
 *
 * @param uv - The printable UV rectangle.
 * @param unwrapAspect - The model's unwrap aspect (`computeUnwrapAspect`).
 * @returns The region's width/height aspect.
 */
export function regionAspect(
  uv: { u0: number; v0: number; u1: number; v1: number },
  unwrapAspect: number,
): number {
  const du = Math.abs(uv.u1 - uv.u0) || 1
  const dv = Math.abs(uv.v1 - uv.v0) || 1
  return (du / dv) * unwrapAspect
}
