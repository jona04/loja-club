import { Bounds, OrbitControls, useGLTF } from "@react-three/drei"
import { Canvas } from "@react-three/fiber"
import { Suspense } from "react"

/** Render the catalog GLB. */
function Model({ url }: { url: string }) {
  const { scene } = useGLTF(url)
  return <primitive object={scene} />
}

/**
 * Read-only 3D viewer: shows the GLB in the browser with orbit + zoom (no
 * editing gizmo). Use it to preview a model without downloading it. `Bounds`
 * auto-frames the model whatever its real scale, so the camera never starts
 * inside it.
 *
 * @param props.glbUrl - The CDN URL of the model's GLB.
 * @returns The viewer canvas.
 */
export function ModelViewer3D({ glbUrl }: { glbUrl: string }) {
  return (
    <div className="h-[28rem] w-full overflow-hidden rounded-md border bg-muted">
      <Canvas camera={{ position: [2, 1.5, 2.5], fov: 45 }}>
        <ambientLight intensity={0.8} />
        <directionalLight position={[1, 2, 1]} intensity={1.2} />
        <Suspense fallback={null}>
          <Bounds fit clip observe margin={1.2}>
            <Model url={glbUrl} />
          </Bounds>
        </Suspense>
        <OrbitControls makeDefault />
      </Canvas>
    </div>
  )
}
