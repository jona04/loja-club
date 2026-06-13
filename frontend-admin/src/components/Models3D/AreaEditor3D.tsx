import { Bounds, OrbitControls, useGLTF } from "@react-three/drei"
import { Canvas } from "@react-three/fiber"
import { Suspense, useEffect, useMemo, useRef } from "react"
import {
  type BufferGeometry,
  CanvasTexture,
  Mesh,
  MeshBasicMaterial,
  type Object3D,
} from "three"

/** A printable region in the model's UV space (normalized 0..1). */
export interface UvRect {
  u0: number
  v0: number
  u1: number
  v1: number
}

/** A printable area as stored in a model version's `printable_areas`. */
export interface PrintableArea {
  id?: string
  label?: string
  uv_rect: UvRect
  max_layers?: number
  [key: string]: unknown
}

const TEX = 1024

/** Draw the printable rectangle onto the overlay canvas (transparent base). */
function drawRect(canvas: HTMLCanvasElement, rect: UvRect): void {
  const ctx = canvas.getContext("2d")
  if (!ctx) return
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  const x = Math.min(rect.u0, rect.u1) * canvas.width
  const y = Math.min(rect.v0, rect.v1) * canvas.height
  const w = Math.abs(rect.u1 - rect.u0) * canvas.width
  const h = Math.abs(rect.v1 - rect.v0) * canvas.height
  ctx.fillStyle = "rgba(249,115,22,0.5)"
  ctx.fillRect(x, y, w, h)
  ctx.strokeStyle = "rgba(234,88,12,1)"
  ctx.lineWidth = 8
  ctx.strokeRect(x, y, w, h)
}

/** First mesh found in a subtree (the model body). */
function firstMesh(root: Object3D): Mesh | null {
  let found: Mesh | null = null
  root.traverse((o) => {
    if (!found && o instanceof Mesh) {
      found = o
    }
  })
  return found
}

/**
 * Physical aspect (width/height) of the cylindrical unwrap: circumference over
 * height (`2πr / h`), so the UV picker can show the printable surface at its
 * real proportions (a mug print is much wider than tall). `r` is the median
 * radial distance in XZ (robust to the handle); `h` is the Y span.
 *
 * @param geometry - The model geometry (upright in its own space).
 * @returns The unwrap's width/height aspect (1 if unknown).
 */
function computeUnwrapAspect(geometry: BufferGeometry): number {
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
 * The GLB with the printable area painted onto its real surface via the model's
 * UVs: an overlay mesh (same geometry + UVs) shows the region exactly where the
 * art will sit, so it follows the surface (mug curve, fabric folds, …).
 */
function ModelWithArea({
  url,
  rect,
  onAspect,
}: {
  url: string
  rect: UvRect
  onAspect?: (aspect: number) => void
}) {
  const { scene } = useGLTF(url)
  const cloned = useMemo(() => scene.clone(true), [scene])
  const canvasRef = useRef<HTMLCanvasElement>(
    typeof document !== "undefined" ? document.createElement("canvas") : null,
  )
  const texRef = useRef<CanvasTexture | null>(null)

  // Build the overlay mesh once (shares the body geometry + UVs).
  useEffect(() => {
    const canvas = canvasRef.current
    const body = firstMesh(cloned)
    if (!canvas || !body) return
    if (onAspect) onAspect(computeUnwrapAspect(body.geometry))
    canvas.width = TEX
    canvas.height = TEX
    const tex = new CanvasTexture(canvas)
    tex.flipY = false
    // Sample the model's cylindrical UV channel (TEXCOORD_1), not the baked
    // TEXCOORD_0 — so the printable region is a clean band on the surface.
    tex.channel = 1
    texRef.current = tex
    const material = new MeshBasicMaterial({
      map: tex,
      transparent: true,
      depthWrite: false,
      polygonOffset: true,
      polygonOffsetFactor: -2,
      polygonOffsetUnits: -2,
    })
    const overlay = new Mesh(body.geometry, material)
    body.add(overlay)
    return () => {
      body.remove(overlay)
      material.dispose()
      tex.dispose()
    }
  }, [cloned, onAspect])

  // Repaint when the rectangle changes.
  useEffect(() => {
    if (canvasRef.current) {
      drawRect(canvasRef.current, rect)
      if (texRef.current) {
        texRef.current.needsUpdate = true
      }
    }
  }, [rect])

  return <primitive object={cloned} />
}

/**
 * Live 3D preview of a model's printable area, mapped onto the real surface via
 * the model's UVs. Orbit/zoom only; the region itself is set by the UV picker.
 *
 * @param props.glbUrl - The CDN URL of the model's GLB.
 * @param props.rect - The printable UV rectangle to highlight.
 * @param props.onAspect - Called with the unwrap's width/height aspect, so the
 *   2D picker can match the printable surface's real proportions.
 * @returns The 3D preview canvas.
 */
export function AreaEditor3D({
  glbUrl,
  rect,
  onAspect,
}: {
  glbUrl: string
  rect: UvRect
  onAspect?: (aspect: number) => void
}) {
  return (
    <div className="h-80 w-full overflow-hidden rounded-md border bg-muted">
      <Canvas camera={{ position: [2, 1.5, 2.5], fov: 45 }}>
        <ambientLight intensity={0.9} />
        <directionalLight position={[2, 3, 2]} intensity={1.1} />
        <Suspense fallback={null}>
          <Bounds fit clip observe margin={1.2}>
            <ModelWithArea url={glbUrl} rect={rect} onAspect={onAspect} />
          </Bounds>
        </Suspense>
        <OrbitControls makeDefault />
      </Canvas>
    </div>
  )
}
