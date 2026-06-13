"use client"

import { Bounds, OrbitControls, useGLTF } from "@react-three/drei"
import { Canvas } from "@react-three/fiber"
import { Suspense } from "react"

/** Loads and renders the catalog GLB (Draco via drei's default decoder). */
function Model({ url }: { url: string }) {
  const { scene } = useGLTF(url)
  return <primitive object={scene} />
}

/**
 * The 3D preview panel: the model from the CDN with orbit/zoom/pan. `Bounds`
 * auto-frames it whatever its real scale, so the camera never starts inside.
 * Editing happens in the 2D panel (P7-EDITOR-02); here it is view-only.
 *
 * @param props.glbUrl - The CDN URL of the pinned version's GLB.
 * @returns The 3D canvas.
 */
export function Scene3D({ glbUrl }: { glbUrl: string }) {
  return (
    <Canvas camera={{ position: [2, 1.5, 2.5], fov: 45 }}>
      <ambientLight intensity={0.9} />
      <directionalLight position={[2, 3, 2]} intensity={1.1} />
      <Suspense fallback={null}>
        <Bounds fit clip observe margin={1.2}>
          <Model url={glbUrl} />
        </Bounds>
      </Suspense>
      <OrbitControls makeDefault />
    </Canvas>
  )
}

export default Scene3D
