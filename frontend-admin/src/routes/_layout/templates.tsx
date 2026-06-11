import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"

import { PlatformAdminService, type ThemeTemplateAdminPublic } from "@/client"
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

export const Route = createFileRoute("/_layout/templates")({
  component: TemplatesScreen,
  head: () => ({ meta: [{ title: "Templates — Admin" }] }),
})

function TemplatesScreen() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [form, setForm] = useState<{
    template: ThemeTemplateAdminPublic | null
  } | null>(null)
  const [detailId, setDetailId] = useState<string | null>(null)

  const templatesQuery = useQuery({
    queryKey: ["adminTemplates"],
    queryFn: () => PlatformAdminService.listTemplates(),
  })
  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: ["adminTemplates"] })

  const toggleMutation = useMutation({
    mutationFn: (template: ThemeTemplateAdminPublic) =>
      PlatformAdminService.updateTemplate({
        templateId: template.id,
        requestBody: { is_active: !template.is_active },
      }),
    onSuccess: () => {
      showSuccessToast("Template atualizado")
      invalidate()
    },
    onError: handleError.bind(showErrorToast),
  })

  const templates = templatesQuery.data ?? []

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Templates</h1>
          <p className="text-muted-foreground">
            Registro de templates (schema vem do código; thumbnail no CDN).
          </p>
        </div>
        <Button onClick={() => setForm({ template: null })}>
          Novo template
        </Button>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Thumb</TableHead>
            <TableHead>ID</TableHead>
            <TableHead>Nome</TableHead>
            <TableHead>Ativo</TableHead>
            <TableHead className="w-0" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {templates.map((template) => (
            <TableRow key={template.id}>
              <TableCell>
                {template.preview_image_url ? (
                  <img
                    src={template.preview_image_url}
                    alt={template.name}
                    className="h-8 w-12 rounded object-cover"
                  />
                ) : (
                  "—"
                )}
              </TableCell>
              <TableCell>{template.id}</TableCell>
              <TableCell>{template.name}</TableCell>
              <TableCell>{template.is_active ? "sim" : "não"}</TableCell>
              <TableCell className="flex gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setDetailId(template.id)}
                >
                  Detalhes
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setForm({ template })}
                >
                  Editar
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => toggleMutation.mutate(template)}
                >
                  {template.is_active ? "Desativar" : "Ativar"}
                </Button>
              </TableCell>
            </TableRow>
          ))}
          {templates.length === 0 && (
            <TableRow>
              <TableCell colSpan={5} className="text-muted-foreground">
                Nenhum template.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>

      {form && (
        <TemplateFormDialog
          template={form.template}
          onClose={() => setForm(null)}
          onSaved={() => {
            invalidate()
            setForm(null)
          }}
        />
      )}
      {detailId && (
        <TemplateDetailDialog
          templateId={detailId}
          onClose={() => setDetailId(null)}
          onChanged={invalidate}
        />
      )}
    </div>
  )
}

function TemplateFormDialog({
  template,
  onClose,
  onSaved,
}: {
  template: ThemeTemplateAdminPublic | null
  onClose: () => void
  onSaved: () => void
}) {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [id, setId] = useState(template?.id ?? "")
  const [name, setName] = useState(template?.name ?? "")
  const [description, setDescription] = useState(template?.description ?? "")
  const [isActive, setIsActive] = useState(template?.is_active ?? true)

  const saveMutation = useMutation({
    mutationFn: () => {
      const fields = {
        name,
        description: description || null,
        is_active: isActive,
      }
      return template
        ? PlatformAdminService.updateTemplate({
            templateId: template.id,
            requestBody: fields,
          })
        : PlatformAdminService.createTemplate({
            requestBody: { id, ...fields },
          })
    },
    onSuccess: () => {
      showSuccessToast("Template salvo")
      onSaved()
    },
    onError: handleError.bind(showErrorToast),
  })

  return (
    <Dialog
      open
      onOpenChange={(isOpen) => {
        if (!isOpen) onClose()
      }}
    >
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            {template ? "Editar template" : "Novo template"}
          </DialogTitle>
        </DialogHeader>
        <div className="space-y-3">
          {template?.preview_image_url && (
            <img
              src={template.preview_image_url}
              alt={template.name}
              className="h-20 w-32 rounded border object-cover"
            />
          )}
          {!template && (
            <div className="space-y-1.5">
              <Label>ID (o código já deve existir na vitrine)</Label>
              <Input
                value={id}
                onChange={(event) => setId(event.target.value)}
                placeholder="aurora"
              />
            </div>
          )}
          <div className="space-y-1.5">
            <Label>Nome</Label>
            <Input
              value={name}
              onChange={(event) => setName(event.target.value)}
            />
          </div>
          <div className="space-y-1.5">
            <Label>Descrição</Label>
            <Input
              value={description}
              onChange={(event) => setDescription(event.target.value)}
            />
          </div>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={isActive}
              onChange={(event) => setIsActive(event.target.checked)}
            />
            Ativo (aparece no picker do lojista)
          </label>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancelar
          </Button>
          <Button
            onClick={() => saveMutation.mutate()}
            disabled={
              saveMutation.isPending ||
              !name.trim() ||
              (!template && !id.trim())
            }
          >
            Salvar
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

function TemplateDetailDialog({
  templateId,
  onClose,
  onChanged,
}: {
  templateId: string
  onClose: () => void
  onChanged: () => void
}) {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const detailQuery = useQuery({
    queryKey: ["adminTemplate", templateId],
    queryFn: () => PlatformAdminService.getTemplate({ templateId }),
  })

  const uploadMutation = useMutation({
    mutationFn: (file: File) =>
      PlatformAdminService.uploadTemplateThumbnail({
        templateId,
        formData: { file: file as unknown as string },
      }),
    onSuccess: () => {
      showSuccessToast("Thumbnail enviado para o CDN")
      detailQuery.refetch()
      onChanged()
    },
    onError: handleError.bind(showErrorToast),
  })

  const template = detailQuery.data
  const schema = template?.settings_schema ?? []

  return (
    <Dialog
      open
      onOpenChange={(isOpen) => {
        if (!isOpen) onClose()
      }}
    >
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{template?.name ?? "Template"}</DialogTitle>
        </DialogHeader>
        {template && (
          <div className="space-y-4 text-sm">
            <div className="flex items-center gap-3">
              {template.preview_image_url ? (
                <img
                  src={template.preview_image_url}
                  alt={template.name}
                  className="h-16 w-24 rounded object-cover"
                />
              ) : (
                <div className="flex h-16 w-24 items-center justify-center rounded border text-xs text-muted-foreground">
                  sem thumb
                </div>
              )}
              <label>
                <input
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={(event) => {
                    const file = event.target.files?.[0]
                    if (file) uploadMutation.mutate(file)
                  }}
                />
                <span className="inline-flex cursor-pointer items-center rounded-md border px-3 py-1.5 text-sm hover:bg-muted">
                  {uploadMutation.isPending ? "Enviando…" : "Enviar thumbnail"}
                </span>
              </label>
            </div>

            <div className="space-y-1">
              <div>
                <span className="font-medium">Descrição:</span>{" "}
                {template.description || "—"}
              </div>
              <div>
                <span className="font-medium">Ativo:</span>{" "}
                {template.is_active ? "sim" : "não"}
              </div>
            </div>

            <div>
              <div className="font-medium">
                settings_schema (read-only — vem do código)
              </div>
              {schema.length === 0 ? (
                <p className="text-muted-foreground">Sem schema seedado.</p>
              ) : (
                <ul className="mt-1 space-y-0.5 text-muted-foreground">
                  {schema.map((field, index) => (
                    <li key={index}>
                      <span className="font-mono">{String(field.key)}</span> ·{" "}
                      {String(field.type)} · {String(field.label)}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
