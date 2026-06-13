import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect, useRef, useState } from "react"

import {
  CustomizationService,
  DCatalogService,
  type ProductType,
} from "@/client"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

/** The two 3D product types the merchant can choose when linking a model. */
const TYPE_OPTIONS: { value: ProductType; label: string }[] = [
  {
    value: "image_3d_customizable",
    label: "3D personalizável (cliente edita)",
  },
  { value: "image_3d", label: "3D (só visualização)" },
]

/**
 * Lets the merchant link a product to a platform 3D-model from the catalog (or
 * unlink it). Linking sets the product's `type`; unlinking reverts it to a
 * regular `image` product. UI-gated by `canManage`; the backend enforces the
 * real authorization.
 *
 * @param props.storeId - The active store id.
 * @param props.productId - The product being edited.
 * @param props.canManage - Whether the member may assign 3D models.
 * @param props.onChanged - Called after a successful link/unlink (to refresh
 *   the product list so the type badge updates).
 * @returns The product 3D-model section.
 */
export function Product3DModelSection({
  storeId,
  productId,
  canManage,
  onChanged,
}: {
  storeId: string
  productId: string
  canManage: boolean
  onChanged: () => void
}) {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const catalogQuery = useQuery({
    queryKey: ["3dCatalog"],
    queryFn: () => DCatalogService.listModels(),
  })
  const linkQuery = useQuery({
    queryKey: ["product3dModel", storeId, productId],
    queryFn: () => CustomizationService.getProductModel({ storeId, productId }),
  })

  // Only models that have an active version can be linked (the backend rejects
  // the rest with 422).
  const models = (catalogQuery.data ?? []).filter((m) => m.active_version)
  const link = linkQuery.data ?? null

  const [modelId, setModelId] = useState("")
  const [type, setType] = useState<ProductType>("image_3d_customizable")
  const [notes, setNotes] = useState("")
  // Seed the form from the persisted link once it loads, without clobbering
  // edits the user makes afterwards.
  const seeded = useRef(false)
  useEffect(() => {
    if (seeded.current || !linkQuery.isFetched) return
    if (link) {
      setModelId(link.platform_3d_model_id)
      setType(link.type)
      setNotes(link.production_notes ?? "")
    }
    seeded.current = true
  }, [linkQuery.isFetched, link])

  const refresh = () => {
    queryClient.invalidateQueries({
      queryKey: ["product3dModel", storeId, productId],
    })
    onChanged()
  }

  const linkMutation = useMutation({
    mutationFn: () =>
      CustomizationService.linkProductModel({
        storeId,
        productId,
        requestBody: {
          platform_3d_model_id: modelId,
          type,
          production_notes: notes || null,
        },
      }),
    onSuccess: () => {
      showSuccessToast("Modelo 3D vinculado")
      refresh()
    },
    onError: handleError.bind(showErrorToast),
  })

  const unlinkMutation = useMutation({
    mutationFn: () =>
      CustomizationService.unlinkProductModel({ storeId, productId }),
    onSuccess: () => {
      showSuccessToast("Modelo 3D desvinculado")
      setModelId("")
      setNotes("")
      refresh()
    },
    onError: handleError.bind(showErrorToast),
  })

  const busy = linkMutation.isPending || unlinkMutation.isPending

  return (
    <div className="space-y-3 rounded-md border p-3">
      <div className="flex items-center justify-between">
        <Label className="text-sm font-medium">Modelo 3D</Label>
        {link && (
          <span className="text-muted-foreground text-xs">
            Vinculado: {link.model_name}
          </span>
        )}
      </div>
      <p className="text-muted-foreground text-xs">
        Escolha um modelo do catálogo da plataforma. Vincular define o tipo do
        produto; desvincular volta para um produto comum.
      </p>

      <div className="space-y-1.5">
        <Label className="text-xs">Modelo do catálogo</Label>
        <Select
          value={modelId}
          onValueChange={setModelId}
          disabled={!canManage}
        >
          <SelectTrigger>
            <SelectValue placeholder="Selecione um modelo" />
          </SelectTrigger>
          <SelectContent>
            {models.map((m) => (
              <SelectItem key={m.id} value={m.id}>
                {m.name}
                {m.category ? ` · ${m.category}` : ""}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {models.length === 0 && !catalogQuery.isPending && (
          <p className="text-muted-foreground text-xs">
            Nenhum modelo disponível no catálogo.
          </p>
        )}
      </div>

      <div className="space-y-1.5">
        <Label className="text-xs">Tipo</Label>
        <Select
          value={type}
          onValueChange={(v) => setType(v as ProductType)}
          disabled={!canManage}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {TYPE_OPTIONS.map((o) => (
              <SelectItem key={o.value} value={o.value}>
                {o.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-1.5">
        <Label className="text-xs">Observações de produção</Label>
        <Input
          value={notes}
          placeholder="Ex.: centralizar a arte na faixa frontal"
          onChange={(e) => setNotes(e.target.value)}
          disabled={!canManage}
        />
      </div>

      <div className="flex gap-2">
        <Button
          type="button"
          size="sm"
          disabled={!canManage || !modelId || busy}
          onClick={() => linkMutation.mutate()}
        >
          {link ? "Atualizar vínculo" : "Vincular"}
        </Button>
        {link && (
          <Button
            type="button"
            size="sm"
            variant="outline"
            disabled={!canManage || busy}
            onClick={() => unlinkMutation.mutate()}
          >
            Desvincular
          </Button>
        )}
      </div>
    </div>
  )
}
