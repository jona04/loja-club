import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { type ChangeEvent, useEffect, useRef, useState } from "react"

import { ContentService, MediaService } from "@/client"
import { StoreGate } from "@/components/Store/StoreGate"
import { TemplateSettingsForm } from "@/components/Store/TemplateSettingsForm"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
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
  const [previewId, setPreviewId] = useState<string | null>(null)
  const bannerRef = useRef<HTMLInputElement>(null)

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

  const myTemplatesQuery = useQuery({
    queryKey: ["layout-my-templates", storeId],
    queryFn: () => ContentService.listMyTemplates({ storeId }),
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

  const bannerUpload = useMutation({
    mutationFn: async (file: File) => {
      const media = await MediaService.uploadMedia({
        storeId,
        formData: { file: file as unknown as string, owner_type: "banner" },
      })
      return media.url
    },
    onSuccess: (url) =>
      setForm((current) => ({ ...current, banner_image_url: url })),
    onError: handleError.bind(showErrorToast),
  })

  if (!activeStore) {
    return null
  }

  const templates = templatesQuery.data ?? []
  const customized = myTemplatesQuery.data ?? []
  const previewTemplate = templates.find((t) => t.id === previewId) ?? null

  const onPickBanner = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      bannerUpload.mutate(file)
    }
    event.target.value = ""
  }

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
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {templates.map((template) => {
              const selected = form.active_template_id === template.id
              return (
                <div
                  key={template.id}
                  className={`overflow-hidden rounded-lg border ${selected ? "border-primary ring-2 ring-primary" : "border-border"}`}
                >
                  <button
                    type="button"
                    className="block aspect-[4/3] w-full bg-muted"
                    onClick={() => setPreviewId(template.id)}
                    title="Pré-visualizar"
                  >
                    {template.preview_image_url ? (
                      <img
                        src={template.preview_image_url}
                        alt={template.name}
                        className="h-full w-full object-cover object-top"
                      />
                    ) : null}
                  </button>
                  <div className="p-3">
                    <div className="flex items-center justify-between gap-2">
                      <h3 className="font-medium">{template.name}</h3>
                      <div className="flex items-center gap-1.5">
                        {customized.includes(template.id) ? (
                          <span className="rounded bg-muted px-1.5 py-0.5 text-xs text-muted-foreground">
                            Personalizado
                          </span>
                        ) : null}
                        {selected ? (
                          <span className="text-xs font-medium text-primary">
                            Ativo
                          </span>
                        ) : null}
                      </div>
                    </div>
                    {template.description ? (
                      <p className="mt-1 line-clamp-2 text-sm text-muted-foreground">
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
                        onClick={() => setPreviewId(template.id)}
                      >
                        Pré-visualizar
                      </Button>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
          <p className="text-sm text-muted-foreground">
            Selecione um template e clique em <strong>Salvar</strong> para
            aplicar na vitrine.
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Aparência</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-1.5">
            <Label>Banner / imagem de destaque</Label>
            <div className="flex items-start gap-4">
              <div className="h-24 w-40 overflow-hidden rounded-md border bg-muted">
                {form.banner_image_url ? (
                  <img
                    src={form.banner_image_url}
                    alt="Banner atual"
                    className="h-full w-full object-cover"
                  />
                ) : (
                  <div className="flex h-full items-center justify-center text-xs text-muted-foreground">
                    Sem imagem
                  </div>
                )}
              </div>
              <div className="flex flex-col gap-2">
                <input
                  ref={bannerRef}
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={onPickBanner}
                />
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  disabled={!canEdit || bannerUpload.isPending}
                  onClick={() => bannerRef.current?.click()}
                >
                  {bannerUpload.isPending ? "Enviando…" : "Enviar imagem"}
                </Button>
                {form.banner_image_url ? (
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    disabled={!canEdit}
                    onClick={() =>
                      setForm((current) => ({
                        ...current,
                        banner_image_url: "",
                      }))
                    }
                  >
                    Remover
                  </Button>
                ) : null}
              </div>
            </div>
          </div>

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

      <TemplateSettingsForm
        storeId={storeId}
        templates={templates}
        canEdit={canEdit}
      />

      <Dialog
        open={previewId !== null}
        onOpenChange={(open) => {
          if (!open) {
            setPreviewId(null)
          }
        }}
      >
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>
              {previewTemplate?.name ?? "Pré-visualização"}
            </DialogTitle>
            <DialogDescription>
              Prévia do design do template. Selecione e salve para aplicar na
              vitrine.
            </DialogDescription>
          </DialogHeader>
          {previewTemplate?.preview_image_url ? (
            <img
              src={previewTemplate.preview_image_url}
              alt={previewTemplate.name}
              className="max-h-[70vh] w-full rounded-md border object-contain"
            />
          ) : (
            <p className="text-sm text-muted-foreground">
              Sem prévia disponível.
            </p>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
