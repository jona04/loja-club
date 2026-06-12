import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { type ReactNode, useState } from "react"

import {
  type ShippingMethodPublic,
  type ShippingMethodType,
  ShippingService,
} from "@/client"
import { StoreGate } from "@/components/Store/StoreGate"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { useActiveStore } from "@/hooks/useActiveStore"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

export const Route = createFileRoute("/_layout/shipping")({
  component: ShippingRoute,
  head: () => ({ meta: [{ title: "Frete - Loja Club" }] }),
})

function ShippingRoute() {
  return (
    <StoreGate>
      <ShippingScreen />
    </StoreGate>
  )
}

/** Human pt-BR label for each shipping method type. */
const TYPE_LABEL: Record<ShippingMethodType, string> = {
  fixed_shipping: "Frete fixo",
  free_shipping: "Frete grátis",
  local_pickup: "Retirada local",
  private_delivery: "Entrega combinada",
}

/** Convert a major-unit amount string (e.g. "15.50") to minor units (cents). */
const toMinor = (major: string): number =>
  Math.round((Number.parseFloat(major) || 0) * 100)

/** Format minor units as a 2-decimal major-unit string. */
const fromMinor = (minor: number | null | undefined): string =>
  minor != null ? (minor / 100).toFixed(2) : ""

interface MethodForm {
  type: ShippingMethodType
  name: string
  description: string
  isActive: boolean
  price: string
  minOrder: string
}

const EMPTY_FORM: MethodForm = {
  type: "fixed_shipping",
  name: "",
  description: "",
  isActive: true,
  price: "",
  minOrder: "",
}

/** Describe a method's price/condition for the list. */
function methodValue(method: ShippingMethodPublic): string {
  if (method.type === "fixed_shipping") {
    return method.price_amount_minor != null
      ? `R$ ${fromMinor(method.price_amount_minor)}`
      : "—"
  }
  if (method.type === "free_shipping") {
    return method.min_order_amount_minor
      ? `Grátis acima de R$ ${fromMinor(method.min_order_amount_minor)}`
      : "Grátis"
  }
  if (method.type === "local_pickup") {
    return "Grátis (retirada)"
  }
  return "A combinar"
}

/**
 * The merchant Shipping screen: list, create, edit, enable/disable and delete
 * the store's delivery methods (retirada/combinada/fixo/grátis) — gated by
 * `shipping.*` (UI gating only; the backend enforces the real authorization).
 * The active methods are what the storefront checkout offers.
 *
 * @returns The Shipping management screen.
 */
export function ShippingScreen() {
  const { activeStore, permissions } = useActiveStore()
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [createOpen, setCreateOpen] = useState(false)
  const [editing, setEditing] = useState<ShippingMethodPublic | null>(null)
  const [form, setForm] = useState<MethodForm>(EMPTY_FORM)

  const storeId = activeStore?.id ?? ""
  const canView = permissions.includes("shipping.view")
  const canCreate = permissions.includes("shipping.create")
  const canUpdate = permissions.includes("shipping.update")
  const canDelete = permissions.includes("shipping.delete")

  const methodsQuery = useQuery({
    queryKey: ["shipping", storeId],
    queryFn: () => ShippingService.listMethods({ storeId }),
    enabled: storeId !== "" && canView,
  })

  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: ["shipping", storeId] })

  const createMutation = useMutation({
    mutationFn: () =>
      ShippingService.createMethod({
        storeId,
        requestBody: {
          type: form.type,
          name: form.name,
          description: form.description || null,
          is_active: form.isActive,
          price_amount_minor:
            form.type === "fixed_shipping" ? toMinor(form.price) : null,
          min_order_amount_minor:
            form.type === "free_shipping" && form.minOrder
              ? toMinor(form.minOrder)
              : null,
        },
      }),
    onSuccess: () => {
      showSuccessToast("Método criado")
      invalidate()
      setCreateOpen(false)
      setForm(EMPTY_FORM)
    },
    onError: handleError.bind(showErrorToast),
  })

  const toggleMutation = useMutation({
    mutationFn: (method: ShippingMethodPublic) =>
      ShippingService.updateMethod({
        storeId,
        methodId: method.id,
        requestBody: { is_active: !method.is_active },
      }),
    onSuccess: () => invalidate(),
    onError: handleError.bind(showErrorToast),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) =>
      ShippingService.deleteMethod({ storeId, methodId: id }),
    onSuccess: () => {
      showSuccessToast("Método removido")
      invalidate()
    },
    onError: handleError.bind(showErrorToast),
  })

  if (!activeStore) {
    return null
  }

  const methods = methodsQuery.data ?? []
  const createDisabled =
    !form.name.trim() ||
    (form.type === "fixed_shipping" && toMinor(form.price) <= 0) ||
    createMutation.isPending

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-bold text-2xl tracking-tight">Frete</h1>
          <p className="text-muted-foreground">
            Formas de entrega que aparecem no checkout de {activeStore.name}
          </p>
        </div>
        <Dialog
          open={createOpen}
          onOpenChange={(o) => {
            setCreateOpen(o)
            if (o) {
              setForm(EMPTY_FORM)
            }
          }}
        >
          <DialogTrigger asChild>
            <Button disabled={!canCreate}>Novo método</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Novo método de entrega</DialogTitle>
            </DialogHeader>
            <MethodFields form={form} setForm={setForm} typeEditable />
            <DialogFooter>
              <Button
                onClick={() => createMutation.mutate()}
                disabled={createDisabled}
              >
                Criar
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Nome</TableHead>
            <TableHead>Tipo</TableHead>
            <TableHead>Valor / condição</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="w-0" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {methods.map((method) => (
            <TableRow key={method.id}>
              <TableCell className="font-medium">{method.name}</TableCell>
              <TableCell>{TYPE_LABEL[method.type]}</TableCell>
              <TableCell>{methodValue(method)}</TableCell>
              <TableCell>
                <Badge variant={method.is_active ? "default" : "outline"}>
                  {method.is_active ? "Ativo" : "Inativo"}
                </Badge>
              </TableCell>
              <TableCell className="flex justify-end gap-1">
                {canUpdate && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => toggleMutation.mutate(method)}
                  >
                    {method.is_active ? "Desativar" : "Ativar"}
                  </Button>
                )}
                {canUpdate && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setEditing(method)}
                  >
                    Editar
                  </Button>
                )}
                {canDelete && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => deleteMutation.mutate(method.id)}
                  >
                    Remover
                  </Button>
                )}
              </TableCell>
            </TableRow>
          ))}
          {methods.length === 0 && (
            <TableRow>
              <TableCell colSpan={5} className="text-muted-foreground">
                Nenhuma forma de entrega. Crie ao menos uma para o checkout
                funcionar.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>

      {editing && (
        <EditMethodDialog
          storeId={storeId}
          method={editing}
          canUpdate={canUpdate}
          onClose={() => setEditing(null)}
          onSaved={invalidate}
        />
      )}
    </div>
  )
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="space-y-1.5">
      <Label>{label}</Label>
      {children}
    </div>
  )
}

function MethodFields({
  form,
  setForm,
  typeEditable,
}: {
  form: MethodForm
  setForm: (f: MethodForm) => void
  typeEditable: boolean
}) {
  return (
    <div className="space-y-3">
      <Field label="Tipo">
        <Select
          value={form.type}
          onValueChange={(v) =>
            setForm({ ...form, type: v as ShippingMethodType })
          }
          disabled={!typeEditable}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {(Object.keys(TYPE_LABEL) as ShippingMethodType[]).map((t) => (
              <SelectItem key={t} value={t}>
                {TYPE_LABEL[t]}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </Field>
      <Field label="Nome (exibido no checkout)">
        <Input
          value={form.name}
          placeholder="Ex: Frete fixo"
          onChange={(e) => setForm({ ...form, name: e.target.value })}
        />
      </Field>
      <Field label="Descrição (opcional)">
        <Input
          value={form.description}
          placeholder="Ex: Entrega em 5-7 dias úteis"
          onChange={(e) => setForm({ ...form, description: e.target.value })}
        />
      </Field>
      {form.type === "fixed_shipping" && (
        <Field label="Valor (R$)">
          <Input
            type="number"
            step="0.01"
            min="0"
            value={form.price}
            onChange={(e) => setForm({ ...form, price: e.target.value })}
          />
        </Field>
      )}
      {form.type === "free_shipping" && (
        <Field label="Grátis acima de (R$, opcional)">
          <Input
            type="number"
            step="0.01"
            min="0"
            value={form.minOrder}
            placeholder="vazio = sempre grátis"
            onChange={(e) => setForm({ ...form, minOrder: e.target.value })}
          />
        </Field>
      )}
      <div className="flex items-center gap-2">
        <Checkbox
          id="method-active"
          checked={form.isActive}
          onCheckedChange={(v) => setForm({ ...form, isActive: v === true })}
        />
        <Label htmlFor="method-active">Ativo (aparece no checkout)</Label>
      </div>
    </div>
  )
}

export function EditMethodDialog({
  storeId,
  method,
  canUpdate,
  onClose,
  onSaved,
}: {
  storeId: string
  method: ShippingMethodPublic
  canUpdate: boolean
  onClose: () => void
  onSaved: () => void
}) {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [form, setForm] = useState<MethodForm>({
    type: method.type,
    name: method.name,
    description: method.description ?? "",
    isActive: method.is_active ?? true,
    price: fromMinor(method.price_amount_minor),
    minOrder: fromMinor(method.min_order_amount_minor),
  })

  const saveMutation = useMutation({
    mutationFn: () =>
      ShippingService.updateMethod({
        storeId,
        methodId: method.id,
        requestBody: {
          name: form.name,
          description: form.description || null,
          is_active: form.isActive,
          price_amount_minor:
            form.type === "fixed_shipping" ? toMinor(form.price) : null,
          min_order_amount_minor:
            form.type === "free_shipping" && form.minOrder
              ? toMinor(form.minOrder)
              : null,
        },
      }),
    onSuccess: () => {
      showSuccessToast("Método atualizado")
      onSaved()
      onClose()
    },
    onError: handleError.bind(showErrorToast),
  })

  return (
    <Dialog open onOpenChange={(o) => !o && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Editar método de entrega</DialogTitle>
        </DialogHeader>
        <MethodFields form={form} setForm={setForm} typeEditable={false} />
        <DialogFooter>
          <Button
            onClick={() => saveMutation.mutate()}
            disabled={
              !canUpdate ||
              !form.name.trim() ||
              (form.type === "fixed_shipping" && toMinor(form.price) <= 0) ||
              saveMutation.isPending
            }
          >
            Salvar
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
