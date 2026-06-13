"use client"

import dynamic from "next/dynamic"
import Link from "next/link"
import { useEffect, useState } from "react"

import { AreaPanel2D } from "@/components/customizer/AreaPanel2D"
import { SceneErrorBoundary } from "@/components/customizer/SceneErrorBoundary"
import type { StorefrontProduct } from "@/lib/api"
import { useCustomizer } from "@/lib/use-customizer"
import { hasWebGL } from "@/lib/webgl"

// The 3D scene is client-only (WebGL) and lazy — never server-rendered.
const Scene3D = dynamic(
  () => import("@/components/customizer/Scene3D").then((m) => m.Scene3D),
  {
    ssr: false,
    loading: () => <PanelMessage>Carregando 3D…</PanelMessage>,
  },
)

function PanelMessage({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-full min-h-80 items-center justify-center rounded-md border bg-gray-50 p-6 text-center text-sm text-gray-500">
      {children}
    </div>
  )
}

/** Fallback when WebGL is unavailable or the model fails: images + a notice. */
function NoEditorFallback({ product }: { product: StorefrontProduct }) {
  return (
    <div className="space-y-4">
      <div className="rounded-md border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
        Não foi possível abrir o editor 3D neste dispositivo/navegador. Veja as
        fotos do produto abaixo e tente novamente em um navegador com WebGL.
      </div>
      {product.images.length > 0 && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          {product.images.map((img) => (
            <img
              key={img.url}
              src={img.url}
              alt={product.name}
              className="aspect-square w-full rounded-md border object-cover"
            />
          ))}
        </div>
      )}
    </div>
  )
}

/**
 * The 3D customization editor shell (P7-EDITOR-01): a 2-panel layout — the 2D
 * editing area + the live 3D preview — backed by an autosaving session. Layers
 * (image/text) and approval arrive in P7-EDITOR-02.
 *
 * @param props.product - The product being customized.
 * @returns The editor shell, or a fallback when 3D is unavailable.
 */
export function Customizer({ product }: { product: StorefrontProduct }) {
  const { session, status, error, saving } = useCustomizer(product.id)
  // Resolve WebGL after mount to avoid an SSR/client hydration mismatch.
  const [webgl, setWebgl] = useState<boolean | null>(null)
  useEffect(() => setWebgl(hasWebGL()), [])

  const area = session?.version.printable_areas[0] ?? null

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <div className="mb-6 flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{product.name}</h1>
          <p className="text-sm text-gray-500">
            Personalize em 3D{saving ? " · salvando…" : ""}
          </p>
        </div>
        <Link
          href={`/products/${product.slug}`}
          className="text-sm text-gray-600 underline underline-offset-2"
        >
          Voltar ao produto
        </Link>
      </div>

      {webgl === false || status === "error" ? (
        <NoEditorFallback product={product} />
      ) : status === "loading" || webgl === null ? (
        <PanelMessage>Preparando o editor…</PanelMessage>
      ) : (
        <div className="grid gap-6 md:grid-cols-2">
          <AreaPanel2D area={area} />
          <div className="h-80 w-full overflow-hidden rounded-md border bg-gray-50 md:h-[28rem]">
            <SceneErrorBoundary
              fallback={
                <PanelMessage>
                  Não foi possível carregar o modelo 3D.
                </PanelMessage>
              }
            >
              {session && <Scene3D glbUrl={session.version.glb_url} />}
            </SceneErrorBoundary>
          </div>
        </div>
      )}

      {error && status !== "error" && (
        <p className="mt-4 text-sm text-red-600">{error}</p>
      )}
    </div>
  )
}

export default Customizer
