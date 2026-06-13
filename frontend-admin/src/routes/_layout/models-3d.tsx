import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"

import { type Platform3DModelAdmin, PlatformAdminService } from "@/client"
import {
  AreaEditor3D,
  type PrintableArea,
  type UvRect,
} from "@/components/Models3D/AreaEditor3D"
import { ModelViewer3D } from "@/components/Models3D/ModelViewer3D"
import { UvRectPicker } from "@/components/Models3D/UvRectPicker"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

export const Route = createFileRoute("/_layout/models-3d")({
  component: Models3DScreen,
  head: () => ({ meta: [{ title: "Modelos 3D — Admin" }] }),
})

function Models3DScreen() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [editing, setEditing] = useState<Platform3DModelAdmin | null>(null)
  const [viewing, setViewing] = useState<Platform3DModelAdmin | null>(null)

  const modelsQuery = useQuery({
    queryKey: ["admin3dModels"],
    queryFn: () => PlatformAdminService.list3dModels(),
  })
  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: ["admin3dModels"] })

  const toggleMutation = useMutation({
    mutationFn: (model: Platform3DModelAdmin) =>
      PlatformAdminService.update3dModel({
        modelId: model.id,
        requestBody: { is_active: !model.is_active },
      }),
    onSuccess: () => {
      showSuccessToast("Modelo atualizado")
      invalidate()
    },
    onError: handleError.bind(showErrorToast),
  })

  const models = modelsQuery.data ?? []

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Modelos 3D</h1>
        <p className="text-muted-foreground">
          Catálogo público (via seed). Habilite/desabilite e ajuste a área
          imprimível e os limites de cada modelo.
        </p>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Nome</TableHead>
            <TableHead>Slug</TableHead>
            <TableHead>Categoria</TableHead>
            <TableHead>Versão</TableHead>
            <TableHead>GLB</TableHead>
            <TableHead>Ativo</TableHead>
            <TableHead className="w-0" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {models.map((model) => (
            <TableRow key={model.id}>
              <TableCell className="font-medium">{model.name}</TableCell>
              <TableCell className="font-mono text-xs">{model.slug}</TableCell>
              <TableCell>{model.category}</TableCell>
              <TableCell>{model.active_version?.version ?? "—"}</TableCell>
              <TableCell>
                {model.active_version ? (
                  <div className="flex gap-3 text-xs">
                    <button
                      type="button"
                      className="underline underline-offset-2"
                      onClick={() => setViewing(model)}
                    >
                      Ver 3D
                    </button>
                    <a
                      href={model.active_version.glb_url}
                      download
                      className="text-muted-foreground underline underline-offset-2"
                    >
                      Baixar
                    </a>
                  </div>
                ) : (
                  "—"
                )}
              </TableCell>
              <TableCell>
                <Badge variant={model.is_active ? "default" : "outline"}>
                  {model.is_active ? "sim" : "não"}
                </Badge>
              </TableCell>
              <TableCell className="flex justify-end gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  disabled={!model.active_version}
                  onClick={() => setEditing(model)}
                >
                  Editar área
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => toggleMutation.mutate(model)}
                >
                  {model.is_active ? "Desativar" : "Ativar"}
                </Button>
              </TableCell>
            </TableRow>
          ))}
          {models.length === 0 && (
            <TableRow>
              <TableCell colSpan={7} className="text-muted-foreground">
                Nenhum modelo no catálogo.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>

      {editing?.active_version && (
        <AreaEditorDialog
          model={editing}
          onClose={() => setEditing(null)}
          onSaved={() => {
            invalidate()
            setEditing(null)
          }}
        />
      )}
      {viewing?.active_version && (
        <ModelViewerDialog model={viewing} onClose={() => setViewing(null)} />
      )}
    </div>
  )
}

function ModelViewerDialog({
  model,
  onClose,
}: {
  model: Platform3DModelAdmin
  onClose: () => void
}) {
  // Guarded by the caller: this dialog only opens with an active version.
  const version = model.active_version!
  return (
    <Dialog open onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>
            {model.name} · v{version.version}
          </DialogTitle>
        </DialogHeader>
        <ModelViewer3D glbUrl={`${version.glb_url}?v=${version.id}`} />
        <p className="text-xs text-muted-foreground">
          Arraste para girar · scroll para zoom.
        </p>
      </DialogContent>
    </Dialog>
  )
}

/** Pretty-print a JSON value for editing in a textarea. */
const pretty = (value: unknown): string => JSON.stringify(value, null, 2)

const DEFAULT_UV_RECT: UvRect = { u0: 0.05, v0: 0.3, u1: 0.95, v1: 0.7 }

/** Coerce a raw printable-area object into a typed one with a UV rectangle. */
function asPrintableArea(value: unknown): PrintableArea {
  const raw = (value ?? {}) as Partial<PrintableArea>
  return {
    ...raw,
    uv_rect: (raw.uv_rect as UvRect) ?? DEFAULT_UV_RECT,
  } as PrintableArea
}

function AreaEditorDialog({
  model,
  onClose,
  onSaved,
}: {
  model: Platform3DModelAdmin
  onClose: () => void
  onSaved: () => void
}) {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  // Guarded by the caller: this dialog only opens with an active version.
  const version = model.active_version!
  const otherAreas = version.printable_areas.slice(1)
  const [area, setArea] = useState<PrintableArea>(() =>
    asPrintableArea(version.printable_areas[0]),
  )
  const [textConfig, setTextConfig] = useState(pretty(version.text_config))
  const [artLimits, setArtLimits] = useState(pretty(version.art_limits))
  const [isActive, setIsActive] = useState(version.is_active)
  // Width/height of the unwrapped surface; the 3D preview measures it from the
  // geometry and feeds it back so the 2D picker shows the print at real
  // proportions (a mug is far wider than tall). Seed with a mug-ish guess.
  const [uvAspect, setUvAspect] = useState(2.5)

  const saveMutation = useMutation({
    mutationFn: () =>
      PlatformAdminService.update3dModelVersion({
        versionId: version.id,
        requestBody: {
          printable_areas: [area, ...otherAreas],
          text_config: JSON.parse(textConfig),
          art_limits: JSON.parse(artLimits),
          is_active: isActive,
        },
      }),
    onSuccess: () => {
      showSuccessToast("Versão atualizada")
      onSaved()
    },
    onError: handleError.bind(showErrorToast),
  })

  const onSave = () => {
    try {
      JSON.parse(textConfig)
      JSON.parse(artLimits)
    } catch {
      showErrorToast("JSON inválido em texto/limites.")
      return
    }
    saveMutation.mutate()
  }

  const setRect = (rect: UvRect) => setArea({ ...area, uv_rect: rect })

  return (
    <Dialog open onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="max-h-[90vh] max-w-4xl overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {model.name} · v{version.version}
          </DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <p className="text-xs text-muted-foreground">
            A área imprimível é uma região de UV: ela cola na superfície real do
            modelo. Editar afeta só sessões novas; pedidos aprovados ficam
            congelados.
          </p>

          <div className="flex flex-wrap items-start gap-4">
            <div className="w-72 max-w-full">
              <UvRectPicker
                rect={area.uv_rect}
                onChange={setRect}
                aspect={uvAspect}
              />
            </div>
            <div className="min-w-[18rem] flex-1">
              <AreaEditor3D
                glbUrl={`${version.glb_url}?v=${version.id}`}
                rect={area.uv_rect}
                onAspect={setUvAspect}
              />
            </div>
          </div>

          <div className="grid max-w-xs grid-cols-1 gap-3">
            <NumField
              label="Camadas máx."
              value={area.max_layers ?? 0}
              onChange={(value) => setArea({ ...area, max_layers: value })}
            />
          </div>

          <JsonField
            label="Configuração de texto (fontes, tamanho mín/máx)"
            value={textConfig}
            onChange={setTextConfig}
            rows={4}
          />
          <JsonField
            label="Limites de arte (mimes, tamanho, dimensão mín)"
            value={artLimits}
            onChange={setArtLimits}
            rows={4}
          />

          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={isActive}
              onChange={(event) => setIsActive(event.target.checked)}
            />
            Versão ativa
          </label>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancelar
          </Button>
          <Button onClick={onSave} disabled={saveMutation.isPending}>
            Salvar
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

function NumField({
  label,
  value,
  onChange,
  step,
}: {
  label: string
  value: number
  onChange: (value: number) => void
  step?: number
}) {
  return (
    <div className="space-y-1.5">
      <Label>{label}</Label>
      <Input
        type="number"
        step={step ?? 1}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
      />
    </div>
  )
}

function JsonField({
  label,
  value,
  onChange,
  rows,
}: {
  label: string
  value: string
  onChange: (value: string) => void
  rows: number
}) {
  return (
    <div className="space-y-1.5">
      <Label>{label}</Label>
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        rows={rows}
        spellCheck={false}
        className="w-full rounded-md border bg-background p-2 font-mono text-xs"
      />
    </div>
  )
}
