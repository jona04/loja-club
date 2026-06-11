import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"

import { type BillingPlanPublic, PlatformAdminService } from "@/client"
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

export const Route = createFileRoute("/_layout/plans")({
  component: PlansScreen,
  head: () => ({ meta: [{ title: "Planos — Admin" }] }),
})

function formatMoney(minor: number, currency: string) {
  return (minor / 100).toLocaleString("pt-BR", { style: "currency", currency })
}

function PlansScreen() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [form, setForm] = useState<{ plan: BillingPlanPublic | null } | null>(
    null,
  )

  const plansQuery = useQuery({
    queryKey: ["adminPlans"],
    queryFn: () => PlatformAdminService.listPlans({ limit: 100 }),
  })
  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: ["adminPlans"] })

  const deleteMutation = useMutation({
    mutationFn: (planId: string) => PlatformAdminService.deletePlan({ planId }),
    onSuccess: () => {
      showSuccessToast("Plano removido")
      invalidate()
    },
    onError: handleError.bind(showErrorToast),
  })

  const plans = plansQuery.data?.data ?? []

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Planos</h1>
          <p className="text-muted-foreground">
            Definições de plano (mensalidade + comissão).
          </p>
        </div>
        <Button onClick={() => setForm({ plan: null })}>Novo plano</Button>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Chave</TableHead>
            <TableHead>Nome</TableHead>
            <TableHead>Mensalidade</TableHead>
            <TableHead>Comissão</TableHead>
            <TableHead>Ativo</TableHead>
            <TableHead className="w-0" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {plans.map((plan) => (
            <TableRow key={plan.id}>
              <TableCell>{plan.key}</TableCell>
              <TableCell>{plan.name}</TableCell>
              <TableCell>
                {formatMoney(
                  plan.monthly_price_amount_minor,
                  plan.monthly_price_currency,
                )}
              </TableCell>
              <TableCell>{(plan.commission_bps / 100).toFixed(2)}%</TableCell>
              <TableCell>{plan.is_active ? "sim" : "não"}</TableCell>
              <TableCell className="flex gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setForm({ plan })}
                >
                  Editar
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => deleteMutation.mutate(plan.id)}
                >
                  Remover
                </Button>
              </TableCell>
            </TableRow>
          ))}
          {plans.length === 0 && (
            <TableRow>
              <TableCell colSpan={6} className="text-muted-foreground">
                Nenhum plano.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>

      {form && (
        <PlanFormDialog
          plan={form.plan}
          onClose={() => setForm(null)}
          onSaved={() => {
            invalidate()
            setForm(null)
          }}
        />
      )}
    </div>
  )
}

function PlanFormDialog({
  plan,
  onClose,
  onSaved,
}: {
  plan: BillingPlanPublic | null
  onClose: () => void
  onSaved: () => void
}) {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [key, setKey] = useState(plan?.key ?? "")
  const [name, setName] = useState(plan?.name ?? "")
  const [priceMinor, setPriceMinor] = useState(
    String(plan?.monthly_price_amount_minor ?? 0),
  )
  const [currency, setCurrency] = useState(
    plan?.monthly_price_currency ?? "BRL",
  )
  const [commissionBps, setCommissionBps] = useState(
    String(plan?.commission_bps ?? 0),
  )
  const [description, setDescription] = useState(plan?.description ?? "")

  const saveMutation = useMutation({
    mutationFn: () => {
      const fields = {
        name,
        monthly_price_amount_minor: Number(priceMinor),
        monthly_price_currency: currency,
        commission_bps: Number(commissionBps),
        description: description || null,
      }
      return plan
        ? PlatformAdminService.updatePlan({
            planId: plan.id,
            requestBody: fields,
          })
        : PlatformAdminService.createPlan({ requestBody: { key, ...fields } })
    },
    onSuccess: () => {
      showSuccessToast("Plano salvo")
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
          <DialogTitle>{plan ? "Editar plano" : "Novo plano"}</DialogTitle>
        </DialogHeader>
        <div className="space-y-3">
          {!plan && (
            <div className="space-y-1.5">
              <Label>Chave</Label>
              <Input
                value={key}
                onChange={(event) => setKey(event.target.value)}
                placeholder="free"
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
            <Label>Mensalidade (centavos)</Label>
            <Input
              type="number"
              value={priceMinor}
              onChange={(event) => setPriceMinor(event.target.value)}
            />
          </div>
          <div className="space-y-1.5">
            <Label>Moeda (ISO 4217)</Label>
            <Input
              value={currency}
              maxLength={3}
              onChange={(event) => setCurrency(event.target.value)}
            />
          </div>
          <div className="space-y-1.5">
            <Label>Comissão (basis points — 500 = 5%)</Label>
            <Input
              type="number"
              value={commissionBps}
              onChange={(event) => setCommissionBps(event.target.value)}
            />
          </div>
          <div className="space-y-1.5">
            <Label>Descrição</Label>
            <Input
              value={description}
              onChange={(event) => setDescription(event.target.value)}
            />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancelar
          </Button>
          <Button
            onClick={() => saveMutation.mutate()}
            disabled={
              saveMutation.isPending || !name.trim() || (!plan && !key.trim())
            }
          >
            Salvar
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
