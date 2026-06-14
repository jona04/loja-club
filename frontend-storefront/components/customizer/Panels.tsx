"use client"

import dynamic from "next/dynamic"
import type { RefObject } from "react"

import { EditorCanvas2D } from "@/components/customizer/EditorCanvas2D"
import { SceneErrorBoundary } from "@/components/customizer/SceneErrorBoundary"
import { regionAspect } from "@/lib/customizer/aspect"
import type { CustomizationSession } from "@/lib/customizer/session-types"
import type { EditorLayer } from "@/lib/customizer/types"

// The 3D scene is client-only (WebGL) and lazy — never server-rendered.
const Scene3D = dynamic(
  () => import("@/components/customizer/Scene3D").then((m) => m.Scene3D),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-full items-center justify-center text-sm text-gray-500">
        Carregando 3D…
      </div>
    ),
  },
)

interface PanelsProps {
  session: CustomizationSession
  layers: EditorLayer[]
  images: Map<string, HTMLImageElement>
  aspect: number
  selectedId: string | null
  readOnly?: boolean
  onAspect: (aspect: number) => void
  onMove?: (id: string, x: number, y: number) => void
  captureRef?: RefObject<(() => string) | null>
}

/**
 * The shared 2-panel editor body: the 2D editing surface + the live 3D preview.
 * Used by both the customer editor and the read-only public view.
 *
 * @param props - The session, layers, loaded images, region aspect, selection,
 *   read-only flag, aspect/move callbacks and the snapshot-capture ref.
 * @returns The two panels.
 */
export function Panels({
  session,
  layers,
  images,
  aspect,
  selectedId,
  readOnly = false,
  onAspect,
  onMove,
  captureRef,
}: PanelsProps) {
  const area = session.version.printable_areas[0]
  const uvRect = area?.uv_rect ?? { u0: 0, v0: 0, u1: 1, v1: 1 }
  const maxFontSize = session.version.text_config.max_size ?? 96
  const panelAspect = regionAspect(uvRect, aspect)

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <EditorCanvas2D
        layers={layers}
        images={images}
        maxFontSize={maxFontSize}
        aspect={panelAspect}
        selectedId={selectedId}
        readOnly={readOnly}
        onMove={onMove}
      />
      <div className="h-80 w-full overflow-hidden rounded-md border bg-gray-50 md:h-[28rem]">
        <SceneErrorBoundary
          fallback={
            <div className="flex h-full items-center justify-center p-6 text-center text-sm text-gray-500">
              Não foi possível carregar o modelo 3D.
            </div>
          }
        >
          <Scene3D
            url={`${session.version.glb_url}?v=${session.version.id}`}
            layers={layers}
            images={images}
            uvRect={uvRect}
            maxFontSize={maxFontSize}
            artAspect={panelAspect}
            onAspect={onAspect}
            captureRef={captureRef}
          />
        </SceneErrorBoundary>
      </div>
    </div>
  )
}
