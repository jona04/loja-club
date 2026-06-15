"use client"

import { Bounds, OrbitControls, useGLTF } from "@react-three/drei"
import { Canvas, useThree } from "@react-three/fiber"
import {
  type RefObject,
  Suspense,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react"
import {
  CanvasTexture,
  Mesh,
  MeshBasicMaterial,
  type Object3D,
  SRGBColorSpace,
} from "three"

import { computeUnwrapAspect } from "@/lib/customizer/aspect"
import { EDITOR_TEXTURE_SIZE, renderArtInto } from "@/lib/customizer/compose"
import type { UvRect } from "@/lib/customizer/session-types"
import type { EditorLayer } from "@/lib/customizer/types"

/** First mesh found in a subtree (the model body). */
function firstMesh(root: Object3D): Mesh | null {
  let found: Mesh | null = null
  root.traverse((o) => {
    if (!found && o instanceof Mesh) found = o
  })
  return found
}

interface SceneProps {
  url: string
  layers: EditorLayer[]
  images: Map<string, HTMLImageElement>
  uvRect: UvRect
  maxFontSize: number
  /** The printable region's real width/height (so the art is not warped). */
  artAspect: number
  onAspect?: (aspect: number) => void
}

/**
 * The model with the composited art painted onto its real surface via the clean
 * cylindrical UV (`TEXCOORD_1`): an overlay mesh shares the geometry and samples
 * a canvas texture. The art is rendered in **physical proportions** and drawn
 * into the UV sub-region; the cylindrical UV maps it back without warping, so the
 * 3D matches the 2D panel exactly.
 */
function ModelWithArt({
  url,
  layers,
  images,
  uvRect,
  maxFontSize,
  artAspect,
  onAspect,
}: SceneProps) {
  const { scene } = useGLTF(url)
  const cloned = useMemo(() => scene.clone(true), [scene])
  const canvasRef = useRef<HTMLCanvasElement | null>(
    typeof document !== "undefined" ? document.createElement("canvas") : null,
  )
  // Reused offscreen canvas for the physical art (avoids allocating per repaint).
  const artRef = useRef<HTMLCanvasElement | null>(
    typeof document !== "undefined" ? document.createElement("canvas") : null,
  )
  const texRef = useRef<CanvasTexture | null>(null)

  // Build the overlay mesh once per model (shares geometry + cylindrical UV).
  useEffect(() => {
    const canvas = canvasRef.current
    const body = firstMesh(cloned)
    if (!canvas || !body) return
    onAspect?.(computeUnwrapAspect(body.geometry))
    canvas.width = EDITOR_TEXTURE_SIZE
    canvas.height = EDITOR_TEXTURE_SIZE
    const tex = new CanvasTexture(canvas)
    tex.flipY = false
    tex.channel = 1 // sample TEXCOORD_1 (the clean cylindrical unwrap)
    tex.colorSpace = SRGBColorSpace // render canvas colors as authored (match 2D)
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

  // Repaint when the art changes: render the physical art into the reused
  // offscreen canvas, then draw it into the UV sub-region (the UV un-stretches it).
  useEffect(() => {
    const canvas = canvasRef.current
    const ctx = canvas?.getContext("2d")
    const art = artRef.current
    if (!canvas || !ctx || !art) return
    renderArtInto(
      art,
      { layers, images, maxFontSize },
      artAspect,
      EDITOR_TEXTURE_SIZE,
    )
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    const u0 = Math.min(uvRect.u0, uvRect.u1)
    const v0 = Math.min(uvRect.v0, uvRect.v1)
    ctx.drawImage(
      art,
      u0 * canvas.width,
      v0 * canvas.height,
      Math.abs(uvRect.u1 - uvRect.u0) * canvas.width,
      Math.abs(uvRect.v1 - uvRect.v0) * canvas.height,
    )
    if (texRef.current) texRef.current.needsUpdate = true
  }, [layers, images, uvRect, maxFontSize, artAspect])

  return <primitive object={cloned} />
}

/**
 * Exposes a snapshot function (canvas → PNG data URL) to the parent. The canvas
 * keeps its drawing buffer (`preserveDrawingBuffer`) so the read is reliable
 * across drivers — the production snapshot must not silently fail.
 */
function CaptureBridge({
  captureRef,
}: {
  captureRef: RefObject<(() => string) | null>
}) {
  const gl = useThree((s) => s.gl)
  useEffect(() => {
    captureRef.current = () => gl.domElement.toDataURL("image/png")
    return () => {
      captureRef.current = null
    }
  }, [gl, captureRef])
  return null
}

/** Flags a lost WebGL context so the parent can show a graceful fallback. */
function ContextLostBridge({ onLost }: { onLost: () => void }) {
  const gl = useThree((s) => s.gl)
  useEffect(() => {
    const el = gl.domElement
    const handler = (e: Event) => {
      e.preventDefault() // allow the browser to attempt a restore
      onLost()
    }
    el.addEventListener("webglcontextlost", handler)
    return () => el.removeEventListener("webglcontextlost", handler)
  }, [gl, onLost])
  return null
}

/**
 * The 3D preview: the model + live art overlay, with orbit/zoom/pan. Keeps the
 * drawing buffer so the approval snapshot reads reliably, and degrades
 * gracefully if the GPU context is lost.
 *
 * @param props - Model URL, layers, loaded images, the printable UV rect, the
 *   max font size, the region aspect, an aspect callback and a capture ref.
 * @returns The 3D canvas (or a fallback if the GPU context was lost).
 */
export function Scene3D({
  captureRef,
  ...scene
}: SceneProps & { captureRef?: RefObject<(() => string) | null> }) {
  const [contextLost, setContextLost] = useState(false)

  if (contextLost) {
    return (
      <div className="flex h-full items-center justify-center p-6 text-center text-sm text-gray-500">
        O 3D foi interrompido (GPU). Recarregue a página para continuar.
      </div>
    )
  }

  return (
    <Canvas
      camera={{ position: [2, 1.5, 2.5], fov: 45 }}
      gl={{ preserveDrawingBuffer: true }}
    >
      <ambientLight intensity={0.9} />
      <directionalLight position={[2, 3, 2]} intensity={1.1} />
      <Suspense fallback={null}>
        <Bounds fit clip observe margin={1.2}>
          <ModelWithArt {...scene} />
        </Bounds>
      </Suspense>
      <OrbitControls makeDefault />
      {captureRef && <CaptureBridge captureRef={captureRef} />}
      <ContextLostBridge onLost={() => setContextLost(true)} />
    </Canvas>
  )
}

export default Scene3D
