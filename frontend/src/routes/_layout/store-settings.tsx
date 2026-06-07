import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useEffect, useState } from "react"

import { StoresService } from "@/client"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useActiveStore } from "@/hooks/useActiveStore"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

export const Route = createFileRoute("/_layout/store-settings")({
  component: StoreSettingsScreen,
  head: () => ({
    meta: [{ title: "Configurações - Loja Club" }],
  }),
})

const FIELDS = [
  { key: "public_name", label: "Nome público" },
  { key: "description", label: "Descrição" },
  { key: "logo_url", label: "URL do logo" },
  { key: "contact_email", label: "E-mail de contato" },
  { key: "contact_phone", label: "Telefone" },
  { key: "whatsapp_number", label: "WhatsApp" },
  { key: "address", label: "Endereço" },
] as const

type FormState = Record<(typeof FIELDS)[number]["key"], string>

const EMPTY_FORM: FormState = {
  public_name: "",
  description: "",
  logo_url: "",
  contact_email: "",
  contact_phone: "",
  whatsapp_number: "",
  address: "",
}

export function StoreSettingsScreen() {
  const { activeStore, permissions } = useActiveStore()
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [form, setForm] = useState<FormState>(EMPTY_FORM)

  const canEdit = permissions.includes("settings.update")
  const storeId = activeStore?.id ?? ""

  const settingsQuery = useQuery({
    queryKey: ["settings", storeId],
    queryFn: () => StoresService.getStoreSettings({ storeId }),
    enabled: storeId !== "",
  })

  useEffect(() => {
    const data = settingsQuery.data
    if (!data) {
      return
    }
    setForm({
      public_name: data.public_name ?? "",
      description: data.description ?? "",
      logo_url: data.logo_url ?? "",
      contact_email: data.contact_email ?? "",
      contact_phone: data.contact_phone ?? "",
      whatsapp_number: data.whatsapp_number ?? "",
      address: data.address ?? "",
    })
  }, [settingsQuery.data])

  const saveMutation = useMutation({
    mutationFn: () =>
      StoresService.updateStoreSettings({ storeId, requestBody: form }),
    onSuccess: () => {
      showSuccessToast("Configurações salvas")
      queryClient.invalidateQueries({ queryKey: ["settings", storeId] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const statusMutation = useMutation({
    mutationFn: (publish: boolean) =>
      publish
        ? StoresService.publishStore({ storeId })
        : StoresService.pauseStore({ storeId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["myStores"] })
    },
    onError: handleError.bind(showErrorToast),
  })

  if (!activeStore) {
    return null
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">
          Configurações da loja
        </h1>
        <p className="text-muted-foreground">
          Status:{" "}
          <span className="font-medium text-foreground">
            {activeStore.status}
          </span>
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Informações</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {FIELDS.map((field) => (
            <div key={field.key} className="space-y-1.5">
              <Label htmlFor={field.key}>{field.label}</Label>
              <Input
                id={field.key}
                value={form[field.key]}
                disabled={!canEdit}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    [field.key]: event.target.value,
                  }))
                }
              />
            </div>
          ))}

          <div className="flex flex-wrap gap-2 pt-2">
            <Button
              onClick={() => saveMutation.mutate()}
              disabled={!canEdit || saveMutation.isPending}
            >
              Salvar
            </Button>
            {activeStore.status === "active" ? (
              <Button
                variant="outline"
                disabled={!canEdit || statusMutation.isPending}
                onClick={() => statusMutation.mutate(false)}
              >
                Pausar loja
              </Button>
            ) : (
              <Button
                variant="outline"
                disabled={!canEdit || statusMutation.isPending}
                onClick={() => statusMutation.mutate(true)}
              >
                Publicar loja
              </Button>
            )}
          </div>

          {!canEdit && (
            <p className="text-sm text-muted-foreground">
              Você não tem permissão para editar as configurações.
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
