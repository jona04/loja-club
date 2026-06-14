"use client"

import Link from "next/link"
import { useEffect, useRef, useState } from "react"

import { LayerPanel } from "@/components/customizer/LayerPanel"
import { Panels } from "@/components/customizer/Panels"
import type { StorefrontProduct } from "@/lib/api"
import {
  approveCustomization,
  uploadCustomizationArt,
} from "@/lib/customization-actions"
import type { UploadPublic } from "@/lib/customizer/session-types"
import { snapshotFormData } from "@/lib/customizer/snapshot"
import {
  clamp,
  type EditorLayer,
  type ImageLayer,
  newLayerId,
  type TextLayer,
} from "@/lib/customizer/types"
import { useSessionImages } from "@/lib/customizer/use-session-images"
import { useCustomizer } from "@/lib/use-customizer"
import { hasWebGL } from "@/lib/webgl"

/** Fallback when WebGL is unavailable: product images + a notice (no editor). */
function NoEditorFallback({ product }: { product: StorefrontProduct }) {
  return (
    <div className="space-y-4">
      <div className="rounded-md border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
        Não foi possível abrir o editor 3D neste dispositivo/navegador. Tente em
        um navegador com WebGL.
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
 * The customer 3D customization editor (P7-EDITOR-02): image + text layers
 * composed onto the surface, with an autosaving session and an approval that
 * captures a client-side snapshot. Layers and the approval gate are also
 * enforced by the backend.
 *
 * @param props.product - The product being customized.
 * @returns The editor, or a fallback when 3D is unavailable.
 */
export function Customizer({ product }: { product: StorefrontProduct }) {
  const { session, state, status, error, saving, setState } = useCustomizer(
    product.id,
  )
  const [webgl, setWebgl] = useState<boolean | null>(null)
  useEffect(() => setWebgl(hasWebGL()), [])

  const [uploads, setUploads] = useState<UploadPublic[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [aspect, setAspect] = useState(2.5)
  const [uploading, setUploading] = useState(false)
  const [approving, setApproving] = useState(false)
  const [actionError, setActionError] = useState<string | null>(null)
  const [approved, setApproved] = useState(false)
  const captureRef = useRef<(() => string) | null>(null)

  const seeded = useRef(false)
  useEffect(() => {
    if (session && !seeded.current) {
      setUploads(session.uploads)
      seeded.current = true
    }
  }, [session])

  const images = useSessionImages(uploads)
  const layers = state?.layers ?? []
  const areaId = session?.version.printable_areas[0]?.id ?? "front"
  const fonts = session?.version.text_config.fonts ?? ["inter"]
  const minFont = session?.version.text_config.min_size ?? 8
  const maxFont = session?.version.text_config.max_size ?? 96

  const setLayers = (next: EditorLayer[]) => {
    if (state) setState({ ...state, layers: next })
  }

  const addImage = async (file: File) => {
    if (!session) return
    setUploading(true)
    setActionError(null)
    try {
      const fd = new FormData()
      fd.append("file", file)
      const up = await uploadCustomizationArt(session.id, fd)
      setUploads((u) => [...u, up])
      const layer: ImageLayer = {
        id: newLayerId(),
        kind: "image",
        area_id: areaId,
        z: layers.length,
        transform: { x: 0.5, y: 0.5, scale: 0.6, rotation_deg: 0 },
        upload_id: up.id,
      }
      setLayers([...layers, layer])
      setSelectedId(layer.id)
    } catch (e) {
      setActionError((e as Error).message)
    } finally {
      setUploading(false)
    }
  }

  const addText = () => {
    const layer: TextLayer = {
      id: newLayerId(),
      kind: "text",
      area_id: areaId,
      z: layers.length,
      transform: { x: 0.5, y: 0.5, scale: 1, rotation_deg: 0 },
      text: "Seu texto",
      font: fonts[0] ?? "inter",
      font_size: clamp(48, minFont, maxFont),
      color: "#222222",
    }
    setLayers([...layers, layer])
    setSelectedId(layer.id)
  }

  const updateLayer = (layer: EditorLayer) =>
    setLayers(layers.map((l) => (l.id === layer.id ? layer : l)))

  const removeLayer = (id: string) => {
    setLayers(layers.filter((l) => l.id !== id).map((l, i) => ({ ...l, z: i })))
    if (selectedId === id) setSelectedId(null)
  }

  const reorder = (id: string, dir: -1 | 1) => {
    const idx = layers.findIndex((l) => l.id === id)
    const next = idx + dir
    if (idx < 0 || next < 0 || next >= layers.length) return
    const arr = [...layers]
    ;[arr[idx], arr[next]] = [arr[next], arr[idx]]
    setLayers(arr.map((l, i) => ({ ...l, z: i })))
  }

  const moveLayer = (id: string, x: number, y: number) => {
    const layer = layers.find((l) => l.id === id)
    if (layer)
      updateLayer({ ...layer, transform: { ...layer.transform, x, y } })
  }

  const onApprove = async () => {
    if (!session || !captureRef.current) return
    setApproving(true)
    setActionError(null)
    try {
      const fd = await snapshotFormData(captureRef.current)
      await approveCustomization(session.id, fd)
      setApproved(true)
    } catch {
      setActionError(
        "Não foi possível gerar a prévia para aprovação. Tente novamente.",
      )
    } finally {
      setApproving(false)
    }
  }

  const noEditor = webgl === false || status === "error"
  const loading = status === "loading" || webgl === null

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

      {noEditor ? (
        <NoEditorFallback product={product} />
      ) : loading || !session ? (
        <div className="flex min-h-80 items-center justify-center rounded-md border bg-gray-50 text-sm text-gray-500">
          Preparando o editor…
        </div>
      ) : approved ? (
        <div className="space-y-4 rounded-md border border-green-200 bg-green-50 p-6 text-sm text-green-800">
          <p className="font-medium">Personalização aprovada! 🎉</p>
          <p>
            Sua arte foi salva. Volte ao produto para adicionar ao carrinho.
          </p>
          <Link
            href={`/products/${product.slug}`}
            className="inline-block rounded-md bg-green-700 px-4 py-2 font-medium text-white"
          >
            Voltar ao produto
          </Link>
        </div>
      ) : (
        <div className="space-y-6">
          <Panels
            session={session}
            layers={layers}
            images={images}
            aspect={aspect}
            selectedId={selectedId}
            onAspect={setAspect}
            onMove={moveLayer}
            captureRef={captureRef}
          />
          <LayerPanel
            layers={layers}
            selectedId={selectedId}
            fonts={fonts}
            minFont={minFont}
            maxFont={maxFont}
            uploading={uploading}
            onAddImage={addImage}
            onAddText={addText}
            onSelect={setSelectedId}
            onUpdate={updateLayer}
            onRemove={removeLayer}
            onReorder={reorder}
          />
          <div className="flex items-center gap-3">
            <button
              type="button"
              disabled={layers.length === 0 || approving}
              onClick={onApprove}
              className="rounded-md bg-black px-5 py-3 text-sm font-medium text-white disabled:opacity-50"
            >
              {approving ? "Aprovando…" : "Aprovar personalização"}
            </button>
            {layers.length === 0 && (
              <span className="text-xs text-gray-500">
                Adicione ao menos uma camada para aprovar.
              </span>
            )}
          </div>
        </div>
      )}

      {(actionError || (error && status !== "error")) && (
        <p className="mt-4 text-sm text-red-600">{actionError ?? error}</p>
      )}
    </div>
  )
}

export default Customizer
