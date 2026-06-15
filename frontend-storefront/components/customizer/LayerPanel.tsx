"use client"

import { useRef } from "react"

import { ProgressBar } from "@/components/customizer/ProgressBar"
import { formatBytes } from "@/lib/customizer/format"
import type {
  EditorLayer,
  LayerTransform,
  TextLayer,
} from "@/lib/customizer/types"
import type { UploadProgress } from "@/lib/customizer/upload-xhr"

interface Props {
  layers: EditorLayer[]
  selectedId: string | null
  fonts: string[]
  minFont: number
  maxFont: number
  uploading: boolean
  /** Max bytes per uploaded image (from `art_limits`), for the limit hint + bar. */
  maxBytes: number
  /** Live upload progress, or null when idle. */
  uploadProgress: UploadProgress | null
  onAddImage: (file: File) => void
  onAddText: () => void
  onSelect: (id: string) => void
  onUpdate: (layer: EditorLayer) => void
  onRemove: (id: string) => void
  onReorder: (id: string, dir: -1 | 1) => void
  /** Toggle free (non-uniform) distortion for an image layer. */
  onToggleDistort: (id: string, on: boolean) => void
}

/**
 * The editing controls: add image/text, the layer list (select, reorder,
 * delete) and the selected layer's properties (transform; text font/size/color).
 *
 * @param props - Layers, selection, font limits and the mutation callbacks.
 * @returns The controls panel.
 */
export function LayerPanel({
  layers,
  selectedId,
  fonts,
  minFont,
  maxFont,
  uploading,
  maxBytes,
  uploadProgress,
  onAddImage,
  onAddText,
  onSelect,
  onUpdate,
  onRemove,
  onReorder,
  onToggleDistort,
}: Props) {
  const fileRef = useRef<HTMLInputElement>(null)
  const selected = layers.find((l) => l.id === selectedId) ?? null

  const setTransform = (patch: Partial<LayerTransform>) => {
    if (!selected) return
    onUpdate({ ...selected, transform: { ...selected.transform, ...patch } })
  }
  const setText = (patch: Partial<TextLayer>) => {
    if (selected?.kind === "text") onUpdate({ ...selected, ...patch })
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <input
          ref={fileRef}
          type="file"
          accept="image/png,image/jpeg"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0]
            if (file) onAddImage(file)
            e.target.value = ""
          }}
        />
        <button
          type="button"
          disabled={uploading}
          onClick={() => fileRef.current?.click()}
          className="rounded-md border px-3 py-2 text-sm font-medium hover:bg-gray-50 disabled:opacity-60"
        >
          {uploading ? "Enviando…" : "Adicionar imagem"}
        </button>
        <button
          type="button"
          onClick={onAddText}
          className="rounded-md border px-3 py-2 text-sm font-medium hover:bg-gray-50"
        >
          Adicionar texto
        </button>
      </div>
      <p className="text-xs text-gray-400">
        PNG ou JPG, até {formatBytes(maxBytes)} por imagem.
      </p>
      {uploading && (
        <ProgressBar progress={uploadProgress} label="Enviando imagem…" />
      )}

      {/* Top of the list = topmost layer (highest z) — most intuitive. */}
      <ul className="divide-y rounded-md border">
        {layers.length === 0 && (
          <li className="p-3 text-sm text-gray-500">Nenhuma camada ainda.</li>
        )}
        {[...layers]
          .sort((a, b) => b.z - a.z)
          .map((layer) => (
            <li
              key={layer.id}
              className={`flex items-center justify-between gap-2 p-2 text-sm ${layer.id === selectedId ? "bg-orange-50" : ""}`}
            >
              <button
                type="button"
                onClick={() => onSelect(layer.id)}
                className="flex-1 truncate text-left"
              >
                {layer.kind === "text"
                  ? `Texto: ${layer.text || "—"}`
                  : "Imagem"}
              </button>
              <div className="flex shrink-0 gap-1 text-gray-500">
                <button
                  type="button"
                  aria-label="Subir"
                  onClick={() => onReorder(layer.id, 1)}
                >
                  ↑
                </button>
                <button
                  type="button"
                  aria-label="Descer"
                  onClick={() => onReorder(layer.id, -1)}
                >
                  ↓
                </button>
                <button
                  type="button"
                  aria-label="Remover"
                  onClick={() => onRemove(layer.id)}
                  className="text-red-600"
                >
                  ✕
                </button>
              </div>
            </li>
          ))}
      </ul>

      {selected && (
        <div className="space-y-3 rounded-md border p-3">
          {selected.kind === "text" && (
            <>
              <Field label="Texto">
                <input
                  value={selected.text}
                  onChange={(e) => setText({ text: e.target.value })}
                  className="w-full rounded-md border px-2 py-1 text-sm"
                />
              </Field>
              <Field label="Fonte">
                <select
                  value={selected.font}
                  onChange={(e) => setText({ font: e.target.value })}
                  className="w-full rounded-md border px-2 py-1 text-sm"
                >
                  {fonts.map((f) => (
                    <option key={f} value={f}>
                      {f}
                    </option>
                  ))}
                </select>
              </Field>
              <Field label={`Tamanho (${selected.font_size})`}>
                <input
                  type="range"
                  min={minFont}
                  max={maxFont}
                  value={selected.font_size}
                  onChange={(e) =>
                    setText({ font_size: Number(e.target.value) })
                  }
                  className="w-full"
                />
              </Field>
              <Field label="Cor">
                <input
                  type="color"
                  value={selected.color}
                  onChange={(e) => setText({ color: e.target.value })}
                />
              </Field>
            </>
          )}
          {selected.kind === "image" && (
            <>
              <Field
                label={
                  selected.transform.scale_y != null
                    ? `Largura (${selected.transform.scale.toFixed(2)})`
                    : `Tamanho (${selected.transform.scale.toFixed(2)})`
                }
              >
                <input
                  type="range"
                  min={0.1}
                  max={1.5}
                  step={0.05}
                  value={selected.transform.scale}
                  onChange={(e) =>
                    setTransform({ scale: Number(e.target.value) })
                  }
                  className="w-full"
                />
              </Field>
              <label className="flex items-center gap-2 text-xs font-medium text-gray-600">
                <input
                  type="checkbox"
                  checked={selected.transform.scale_y != null}
                  onChange={(e) =>
                    onToggleDistort(selected.id, e.target.checked)
                  }
                />
                Distorcer (largura/altura livres)
              </label>
              {selected.transform.scale_y != null && (
                <Field
                  label={`Altura (${selected.transform.scale_y.toFixed(2)})`}
                >
                  <input
                    type="range"
                    min={0.1}
                    max={1.5}
                    step={0.05}
                    value={selected.transform.scale_y}
                    onChange={(e) =>
                      setTransform({ scale_y: Number(e.target.value) })
                    }
                    className="w-full"
                  />
                </Field>
              )}
            </>
          )}
          <Field
            label={`Rotação (${Math.round(selected.transform.rotation_deg)}°)`}
          >
            <input
              type="range"
              min={-180}
              max={180}
              value={selected.transform.rotation_deg}
              onChange={(e) =>
                setTransform({ rotation_deg: Number(e.target.value) })
              }
              className="w-full"
            />
          </Field>
        </div>
      )}
    </div>
  )
}

function Field({
  label,
  children,
}: {
  label: string
  children: React.ReactNode
}) {
  return (
    <div className="space-y-1 text-xs font-medium text-gray-600">
      <span className="block">{label}</span>
      {children}
    </div>
  )
}
