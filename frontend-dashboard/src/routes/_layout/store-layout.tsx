import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useEffect, useState } from "react"

import { ContentService } from "@/client"
import { StoreGate } from "@/components/Store/StoreGate"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useActiveStore } from "@/hooks/useActiveStore"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

export const Route = createFileRoute("/_layout/store-layout")({
  component: StoreLayoutRoute,
  head: () => ({
    meta: [{ title: "Layout da Loja - Loja Club" }],
  }),
})

function StoreLayoutRoute() {
  return (
    <StoreGate>
      <StoreLayoutScreen />
    </StoreGate>
  )
}

interface FormState {
  active_template_id: string
  banner_image_url: string
  headline: string
  featured_collection_id: string
}

const EMPTY_FORM: FormState = {
  active_template_id: "",
  banner_image_url: "",
  headline: "",
  featured_collection_id: "",
}

export function StoreLayoutScreen() {
  const { activeStore, permissions } = useActiveStore()
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [form, setForm] = useState<FormState>(EMPTY_FORM)

  const canEdit = permissions.includes("layout.update")
  const storeId = activeStore?.id ?? ""

  const templatesQuery = useQuery({
    queryKey: ["layout-templates", storeId],
    queryFn: () => ContentService.listTemplates({ storeId }),
    enabled: storeId !== "",
  })

  const layoutQuery = useQuery({
    queryKey: ["layout", storeId],
    queryFn: () => ContentService.getLayout({ storeId }),
    enabled: storeId !== "",
  })

  useEffect(() => {
    const data = layoutQuery.data
    if (!data) {
      return
    }
    setForm({
      active_template_id: data.active_template_id ?? "",
      banner_image_url: data.banner_image_url ?? "",
      headline: data.headline ?? "",
      featured_collection_id: data.featured_collection_id ?? "",
    })
  }, [layoutQuery.data])

  const saveMutation = useMutation({
    mutationFn: () =>
      ContentService.updateLayout({
        storeId,
        requestBody: {
          active_template_id: form.active_template_id,
          banner_image_url: form.banner_image_url || null,
          headline: form.headline || null,
          featured_collection_id: form.featured_collection_id || null,
        },
      }),
    onSuccess: () => {
      showSuccessToast("Layout salvo")
      queryClient.invalidateQueries({ queryKey: ["layout", storeId] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const previewMutation = useMutation({
    mutationFn: (templateId: string) =>
      ContentService.previewLayout({ storeId, templateId }),
    onError: handleError.bind(showErrorToast),
  })

  if (!activeStore) {
    return null
  }

  const templates = templatesQuery.data ?? []
  const preview = previewMutation.data

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Layout da loja</h1>
        <p className="text-muted-foreground">
          Escolha um template e ajuste a aparência da sua vitrine.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Template</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            {templates.map((template) => {
              const selected = form.active_template_id === template.id
              return (
                <div
                  key={template.id}
                  className={`rounded-lg border p-4 ${selected ? "border-primary ring-1 ring-primary" : "border-border"}`}
                >
                  <h3 className="font-medium">{template.name}</h3>
                  {template.description ? (
                    <p className="mt-1 text-sm text-muted-foreground">
                      {template.description}
                    </p>
                  ) : null}
                  <div className="mt-3 flex gap-2">
                    <Button
                      size="sm"
                      variant={selected ? "default" : "outline"}
                      disabled={!canEdit}
                      onClick={() =>
                        setForm((current) => ({
                          ...current,
                          active_template_id: template.id,
                        }))
                      }
                    >
                      {selected ? "Selecionado" : "Selecionar"}
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      disabled={previewMutation.isPending}
                      onClick={() => previewMutation.mutate(template.id)}
                    >
                      Pré-visualizar
                    </Button>
                  </div>
                </div>
              )
            })}
          </div>

          {preview ? (
            <p className="text-sm text-muted-foreground">
              Pré-visualização (não salva) — template{" "}
              <span className="font-medium text-foreground">
                {preview.active_template_id}
              </span>
              .
            </p>
          ) : null}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Aparência</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-1.5">
            <Label htmlFor="headline">Título de destaque</Label>
            <Input
              id="headline"
              value={form.headline}
              disabled={!canEdit}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  headline: event.target.value,
                }))
              }
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="banner_image_url">URL do banner</Label>
            <Input
              id="banner_image_url"
              value={form.banner_image_url}
              disabled={!canEdit}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  banner_image_url: event.target.value,
                }))
              }
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="featured_collection_id">
              ID da coleção em destaque
            </Label>
            <Input
              id="featured_collection_id"
              value={form.featured_collection_id}
              disabled={!canEdit}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  featured_collection_id: event.target.value,
                }))
              }
            />
          </div>

          <div className="pt-2">
            <Button
              onClick={() => saveMutation.mutate()}
              disabled={!canEdit || saveMutation.isPending}
            >
              Salvar
            </Button>
          </div>

          {!canEdit && (
            <p className="text-sm text-muted-foreground">
              Você não tem permissão para editar o layout.
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
