"use client"

import { Bounds, OrbitControls, useGLTF } from "@react-three/drei"
import { Canvas, useThree } from "@react-three/fiber"
import { type RefObject, Suspense, useEffect, useMemo, useRef } from "react"
import { CanvasTexture, Mesh, MeshBasicMaterial, type Object3D } from "three"

import { computeUnwrapAspect } from "@/lib/customizer/aspect"
import { EDITOR_TEXTURE_SIZE, paintLayers } from "@/lib/customizer/compose"
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
  onAspect?: (aspect: number) => void
}

/**
 * The model with the composited art painted onto its real surface via the clean
 * cylindrical UV (`TEXCOORD_1`): an overlay mesh shares the geometry and samples
 * a canvas texture, so the art conforms to the surface (not a flat projection).
 */
function ModelWithArt({
  url,
  layers,
  images,
  uvRect,
  maxFontSize,
  onAspect,
}: SceneProps) {
  const { scene } = useGLTF(url)
  const cloned = useMemo(() => scene.clone(true), [scene])
  const canvasRef = useRef<HTMLCanvasElement | null>(
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

  // Repaint the art whenever the layers or loaded images change.
  useEffect(() => {
    const canvas = canvasRef.current
    const ctx = canvas?.getContext("2d")
    if (!canvas || !ctx) return
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    const u0 = Math.min(uvRect.u0, uvRect.u1)
    const v0 = Math.min(uvRect.v0, uvRect.v1)
    paintLayers(
      ctx,
      {
        x: u0 * canvas.width,
        y: v0 * canvas.height,
        w: Math.abs(uvRect.u1 - uvRect.u0) * canvas.width,
        h: Math.abs(uvRect.v1 - uvRect.v0) * canvas.height,
      },
      layers,
      images,
      maxFontSize,
    )
    if (texRef.current) texRef.current.needsUpdate = true
  }, [layers, images, uvRect, maxFontSize])

  return <primitive object={cloned} />
}

/** Exposes a snapshot function (canvas → PNG data URL) to the parent. */
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

/**
 * The 3D preview: the model + live art overlay, with orbit/zoom/pan. The canvas
 * keeps its drawing buffer so the approval snapshot can read it (`toDataURL`).
 *
 * @param props - Model URL, layers, loaded images, the printable UV rect, the
 *   max font size, an aspect callback and a snapshot-capture ref.
 * @returns The 3D canvas.
 */
export function Scene3D({
  captureRef,
  ...scene
}: SceneProps & { captureRef?: RefObject<(() => string) | null> }) {
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
    </Canvas>
  )
}

export default Scene3D
