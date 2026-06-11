import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect, useState } from "react"

import { ContentService, type ThemeTemplatePublic } from "@/client"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

interface SchemaField {
  key: string
  type: string
  label: string
  group?: string
  default?: unknown
  max_length?: number
  options?: string[]
}

const CONTROL_CLASS =
  "flex w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"

interface TemplateSettingsFormProps {
  storeId: string
  templates: ThemeTemplatePublic[]
  canEdit: boolean
}

/**
 * Schema-driven settings form for the store's active template.
 *
 * Renders the active template's `settings_schema` fields (one component, N
 * schemas) grouped by `group`, reads/saves the per-store overrides through the
 * panel API, and supports reset (back to the schema defaults). Renders nothing
 * when the active template has no editable schema.
 *
 * @param storeId - The active store id.
 * @param templates - The available templates (each carrying `settings_schema`).
 * @param canEdit - Whether the member may edit (gated `layout.update`).
 * @returns The personalization card, or `null` when there is no schema.
 */
export function TemplateSettingsForm({
  storeId,
  templates,
  canEdit,
}: TemplateSettingsFormProps) {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [values, setValues] = useState<Record<string, unknown>>({})

  const settingsQuery = useQuery({
    queryKey: ["layout-settings", storeId],
    queryFn: () => ContentService.getLayoutSettings({ storeId }),
    enabled: storeId !== "",
  })

  const activeTemplateId = settingsQuery.data?.template_id
  const schema = (templates.find((t) => t.id === activeTemplateId)
    ?.settings_schema ?? []) as unknown as SchemaField[]

  useEffect(() => {
    const data = settingsQuery.data
    if (!data) {
      return
    }
    const fields = (templates.find((t) => t.id === data.template_id)
      ?.settings_schema ?? []) as unknown as SchemaField[]
    const overrides = (data.settings ?? {}) as Record<string, unknown>
    const next: Record<string, unknown> = {}
    for (const field of fields) {
      next[field.key] =
        field.key in overrides ? overrides[field.key] : field.default
    }
    setValues(next)
  }, [settingsQuery.data, templates])

  const saveMutation = useMutation({
    mutationFn: () =>
      ContentService.updateLayoutSettings({
        storeId,
        requestBody: { settings: values },
      }),
    onSuccess: () => {
      showSuccessToast("Personalização salva")
      queryClient.invalidateQueries({ queryKey: ["layout-settings", storeId] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const resetMutation = useMutation({
    mutationFn: () => ContentService.resetLayoutSettings({ storeId }),
    onSuccess: () => {
      showSuccessToast("Personalização resetada")
      queryClient.invalidateQueries({ queryKey: ["layout-settings", storeId] })
    },
    onError: handleError.bind(showErrorToast),
  })

  if (schema.length === 0) {
    return null
  }

  const groups = new Map<string, SchemaField[]>()
  for (const field of schema) {
    const group = field.group ?? "Geral"
    const list = groups.get(group) ?? []
    list.push(field)
    groups.set(group, list)
  }

  const setValue = (key: string, value: unknown) =>
    setValues((current) => ({ ...current, [key]: value }))

  const renderField = (field: SchemaField) => {
    const value = values[field.key]
    if (field.type === "boolean") {
      return (
        <div className="flex items-center gap-2">
          <Checkbox
            id={field.key}
            checked={Boolean(value)}
            disabled={!canEdit}
            onCheckedChange={(checked) => setValue(field.key, checked === true)}
          />
          <Label htmlFor={field.key}>{field.label}</Label>
        </div>
      )
    }
    if (field.type === "textarea") {
      return (
        <div className="space-y-1.5">
          <Label htmlFor={field.key}>{field.label}</Label>
          <textarea
            id={field.key}
            className={`${CONTROL_CLASS} min-h-20`}
            value={String(value ?? "")}
            maxLength={field.max_length}
            disabled={!canEdit}
            onChange={(event) => setValue(field.key, event.target.value)}
          />
        </div>
      )
    }
    if (field.type === "select") {
      return (
        <div className="space-y-1.5">
          <Label htmlFor={field.key}>{field.label}</Label>
          <select
            id={field.key}
            className={CONTROL_CLASS}
            value={String(value ?? "")}
            disabled={!canEdit}
            onChange={(event) => setValue(field.key, event.target.value)}
          >
            {(field.options ?? []).map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>
      )
    }
    if (field.type === "image") {
      return (
        <div className="space-y-1.5">
          <Label>{field.label}</Label>
          <p className="text-sm text-muted-foreground">
            Imagens deste template serão configuráveis em breve.
          </p>
        </div>
      )
    }
    return (
      <div className="space-y-1.5">
        <Label htmlFor={field.key}>{field.label}</Label>
        <Input
          id={field.key}
          value={String(value ?? "")}
          maxLength={field.max_length}
          disabled={!canEdit}
          onChange={(event) => setValue(field.key, event.target.value)}
        />
      </div>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Personalização do template</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {[...groups.entries()].map(([group, fields]) => (
          <div key={group} className="space-y-4">
            <h3 className="text-sm font-medium text-muted-foreground">
              {group}
            </h3>
            {fields.map((field) => (
              <div key={field.key}>{renderField(field)}</div>
            ))}
          </div>
        ))}
        <div className="flex gap-2 pt-2">
          <Button
            onClick={() => saveMutation.mutate()}
            disabled={!canEdit || saveMutation.isPending}
          >
            Salvar personalização
          </Button>
          <Button
            variant="outline"
            onClick={() => resetMutation.mutate()}
            disabled={!canEdit || resetMutation.isPending}
          >
            Resetar
          </Button>
        </div>
        {!canEdit && (
          <p className="text-sm text-muted-foreground">
            Você não tem permissão para editar o layout.
          </p>
        )}
      </CardContent>
    </Card>
  )
}
