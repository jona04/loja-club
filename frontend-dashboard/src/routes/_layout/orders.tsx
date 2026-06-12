import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"

import { type OrderStatus, OrdersService } from "@/client"
import { StoreGate } from "@/components/Store/StoreGate"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"
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

export const Route = createFileRoute("/_layout/orders")({
  component: OrdersRoute,
  head: () => ({ meta: [{ title: "Pedidos - Kriar" }] }),
})

function OrdersRoute() {
  return (
    <StoreGate>
      <OrdersScreen />
    </StoreGate>
  )
}

const PAGE_SIZE = 20

/** Human pt-BR label for each order status. */
const STATUS_LABEL: Record<OrderStatus, string> = {
  pending_payment: "Aguardando pagamento",
  paid: "Pago",
  processing: "Em preparação",
  shipped: "Enviado",
  delivered: "Entregue",
  canceled: "Cancelado",
}

/** Badge variant per status. */
const STATUS_VARIANT: Record<
  OrderStatus,
  "default" | "secondary" | "outline" | "destructive"
> = {
  pending_payment: "outline",
  paid: "default",
  processing: "secondary",
  shipped: "secondary",
  delivered: "default",
  canceled: "destructive",
}

/** The next operational status (mirrors the backend forward chain). */
const NEXT_STATUS: Partial<Record<OrderStatus, OrderStatus>> = {
  pending_payment: "paid",
  paid: "processing",
  processing: "shipped",
  shipped: "delivered",
}

const CANCELABLE: ReadonlySet<OrderStatus> = new Set<OrderStatus>([
  "pending_payment",
  "paid",
  "processing",
])

/** Format minor units + currency, e.g. `BRL 39.00`. */
const money = (minor: number, currency: string): string =>
  `${currency} ${(minor / 100).toFixed(2)}`

/** Format an ISO timestamp for pt-BR display. */
const when = (iso: string): string => new Date(iso).toLocaleString("pt-BR")

/** Build a WhatsApp link to talk to the customer about an order. */
const whatsappLink = (phone: string, orderNumber: number): string => {
  const text = encodeURIComponent(`Olá! Sobre o seu pedido #${orderNumber}.`)
  return `https://wa.me/${phone.replace(/\D/g, "")}?text=${text}`
}

/**
 * The merchant Orders screen: list orders (with a status filter), open an order
 * to see the customer/address/items/history, mark payment received, advance the
 * operational status, cancel (restocking) and add internal notes — gated by
 * `orders.*` (UI gating only; the backend enforces the real authorization).
 *
 * @returns The Orders management screen.
 */
export function OrdersScreen() {
  const { activeStore, permissions } = useActiveStore()
  const [page, setPage] = useState(0)
  const [status, setStatus] = useState<OrderStatus | "all">("all")
  const [openId, setOpenId] = useState<string | null>(null)

  const storeId = activeStore?.id ?? ""
  const canView = permissions.includes("orders.view")

  const ordersQuery = useQuery({
    queryKey: ["orders", storeId, page, status],
    queryFn: () =>
      OrdersService.listOrders({
        storeId,
        skip: page * PAGE_SIZE,
        limit: PAGE_SIZE,
        status: status === "all" ? undefined : status,
      }),
    enabled: storeId !== "" && canView,
  })

  if (!activeStore) {
    return null
  }

  const orders = ordersQuery.data?.data ?? []
  const count = ordersQuery.data?.count ?? 0

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-bold text-2xl tracking-tight">Pedidos</h1>
          <p className="text-muted-foreground">
            {count} pedido(s) em {activeStore.name}
          </p>
        </div>
        <Select
          value={status}
          onValueChange={(v) => {
            setStatus(v as OrderStatus | "all")
            setPage(0)
          }}
        >
          <SelectTrigger className="w-56">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Todos os status</SelectItem>
            {(Object.keys(STATUS_LABEL) as OrderStatus[]).map((s) => (
              <SelectItem key={s} value={s}>
                {STATUS_LABEL[s]}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Nº</TableHead>
            <TableHead>Cliente</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Itens</TableHead>
            <TableHead>Total</TableHead>
            <TableHead>Data</TableHead>
            <TableHead className="w-0" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {orders.map((order) => (
            <TableRow key={order.id}>
              <TableCell className="font-medium">
                #{order.order_number}
              </TableCell>
              <TableCell>{order.customer_name ?? "—"}</TableCell>
              <TableCell>
                <Badge variant={STATUS_VARIANT[order.status]}>
                  {STATUS_LABEL[order.status]}
                </Badge>
              </TableCell>
              <TableCell>{order.item_count}</TableCell>
              <TableCell>
                {money(order.total_amount_minor, order.currency)}
              </TableCell>
              <TableCell className="text-muted-foreground">
                {when(order.created_at)}
              </TableCell>
              <TableCell className="flex justify-end">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setOpenId(order.id)}
                >
                  Ver
                </Button>
              </TableCell>
            </TableRow>
          ))}
          {orders.length === 0 && (
            <TableRow>
              <TableCell colSpan={7} className="text-muted-foreground">
                Nenhum pedido.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>

      <div className="flex items-center justify-end gap-2">
        <span className="text-muted-foreground text-sm">
          Página {page + 1} de {Math.max(1, Math.ceil(count / PAGE_SIZE))}
        </span>
        <Button
          variant="outline"
          size="sm"
          disabled={page === 0}
          onClick={() => setPage((p) => p - 1)}
        >
          Anterior
        </Button>
        <Button
          variant="outline"
          size="sm"
          disabled={(page + 1) * PAGE_SIZE >= count}
          onClick={() => setPage((p) => p + 1)}
        >
          Próxima
        </Button>
      </div>

      {openId && (
        <OrderDetailDialog
          storeId={storeId}
          orderId={openId}
          permissions={permissions}
          onClose={() => setOpenId(null)}
        />
      )}
    </div>
  )
}

export function OrderDetailDialog({
  storeId,
  orderId,
  permissions,
  onClose,
}: {
  storeId: string
  orderId: string
  permissions: string[]
  onClose: () => void
}) {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [note, setNote] = useState("")

  const canUpdateStatus = permissions.includes("orders.update_status")
  const canCancel = permissions.includes("orders.cancel")
  const canAddNote = permissions.includes("orders.add_note")

  const detailQuery = useQuery({
    queryKey: ["order", storeId, orderId],
    queryFn: () => OrdersService.getOrder({ storeId, orderId }),
  })

  const refresh = () => {
    queryClient.invalidateQueries({ queryKey: ["order", storeId, orderId] })
    queryClient.invalidateQueries({ queryKey: ["orders", storeId] })
  }

  const statusMutation = useMutation({
    mutationFn: (next: OrderStatus) =>
      OrdersService.updateStatus({
        storeId,
        orderId,
        requestBody: { status: next },
      }),
    onSuccess: () => {
      showSuccessToast("Status atualizado")
      refresh()
    },
    onError: handleError.bind(showErrorToast),
  })

  const cancelMutation = useMutation({
    mutationFn: () => OrdersService.cancelOrder({ storeId, orderId }),
    onSuccess: () => {
      showSuccessToast("Pedido cancelado (estoque devolvido)")
      refresh()
    },
    onError: handleError.bind(showErrorToast),
  })

  const noteMutation = useMutation({
    mutationFn: (body: string) =>
      OrdersService.addNote({ storeId, orderId, requestBody: { body } }),
    onSuccess: () => {
      setNote("")
      refresh()
    },
    onError: handleError.bind(showErrorToast),
  })

  const order = detailQuery.data
  const next = order ? NEXT_STATUS[order.status] : undefined
  const busy = statusMutation.isPending || cancelMutation.isPending

  return (
    <Dialog open onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="max-h-[90vh] max-w-2xl overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {order ? `Pedido #${order.order_number}` : "Pedido"}
          </DialogTitle>
        </DialogHeader>

        {!order ? (
          <p className="text-muted-foreground text-sm">Carregando…</p>
        ) : (
          <div className="space-y-5">
            <div className="flex flex-wrap items-center gap-3">
              <Badge variant={STATUS_VARIANT[order.status]}>
                {STATUS_LABEL[order.status]}
              </Badge>
              <span className="text-muted-foreground text-sm">
                {when(order.created_at)}
              </span>
            </div>

            <div className="flex flex-wrap gap-2">
              {order.status === "pending_payment" && canUpdateStatus && (
                <Button
                  size="sm"
                  disabled={busy}
                  onClick={() => statusMutation.mutate("paid")}
                >
                  Marcar pago
                </Button>
              )}
              {order.status !== "pending_payment" &&
                next &&
                canUpdateStatus && (
                  <Button
                    size="sm"
                    disabled={busy}
                    onClick={() => statusMutation.mutate(next)}
                  >
                    Avançar para {STATUS_LABEL[next]}
                  </Button>
                )}
              {CANCELABLE.has(order.status) && canCancel && (
                <Button
                  size="sm"
                  variant="destructive"
                  disabled={busy}
                  onClick={() => cancelMutation.mutate()}
                >
                  Cancelar
                </Button>
              )}
            </div>

            <Separator />

            <section className="space-y-1 text-sm">
              <h3 className="font-semibold">Cliente</h3>
              {order.customer ? (
                <>
                  <p>{order.customer.name}</p>
                  {order.customer.email && (
                    <p className="text-muted-foreground">
                      {order.customer.email}
                    </p>
                  )}
                  {order.customer.phone_e164 && (
                    <div className="flex items-center gap-2">
                      <span className="text-muted-foreground">
                        {order.customer.phone_e164}
                      </span>
                      <a
                        href={whatsappLink(
                          order.customer.phone_e164,
                          order.order_number,
                        )}
                        target="_blank"
                        rel="noreferrer"
                        className="text-green-600 text-xs underline underline-offset-2"
                      >
                        Falar no WhatsApp
                      </a>
                    </div>
                  )}
                </>
              ) : (
                <p className="text-muted-foreground">Convidado</p>
              )}
            </section>

            {order.address && (
              <section className="space-y-1 text-sm">
                <h3 className="font-semibold">Entrega</h3>
                <p className="text-muted-foreground">
                  {[
                    order.address.line1,
                    order.address.number,
                    order.address.line2,
                    order.address.neighborhood,
                    order.address.city,
                    order.address.state,
                    order.address.postal_code,
                  ]
                    .filter(Boolean)
                    .join(", ")}
                </p>
                {order.shipping_method_name && (
                  <p className="text-muted-foreground">
                    Frete: {order.shipping_method_name}
                  </p>
                )}
              </section>
            )}

            <section className="space-y-2">
              <h3 className="font-semibold text-sm">Itens</h3>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Produto</TableHead>
                    <TableHead>Qtd</TableHead>
                    <TableHead>Unit.</TableHead>
                    <TableHead>Total</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {order.items.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell>{item.name}</TableCell>
                      <TableCell>{item.quantity}</TableCell>
                      <TableCell>
                        {money(
                          item.unit_price_amount_minor,
                          item.unit_price_currency,
                        )}
                      </TableCell>
                      <TableCell>
                        {money(
                          item.line_total_amount_minor,
                          item.unit_price_currency,
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              <div className="flex flex-col items-end gap-0.5 text-sm">
                <span className="text-muted-foreground">
                  Subtotal: {money(order.subtotal_amount_minor, order.currency)}
                </span>
                <span className="text-muted-foreground">
                  Frete: {money(order.shipping_amount_minor, order.currency)}
                </span>
                {order.discount_amount_minor > 0 && (
                  <span className="text-muted-foreground">
                    Desconto: -
                    {money(order.discount_amount_minor, order.currency)}
                  </span>
                )}
                <span className="font-semibold">
                  Total: {money(order.total_amount_minor, order.currency)}
                </span>
              </div>
            </section>

            <Separator />

            <section className="space-y-2">
              <h3 className="font-semibold text-sm">Histórico</h3>
              <ul className="space-y-1 text-sm">
                {order.status_history.map((h) => (
                  <li
                    key={`${h.status}-${h.created_at}`}
                    className="flex justify-between text-muted-foreground"
                  >
                    <span>{STATUS_LABEL[h.status]}</span>
                    <span>{when(h.created_at)}</span>
                  </li>
                ))}
              </ul>
            </section>

            <section className="space-y-2">
              <h3 className="font-semibold text-sm">Notas internas</h3>
              <ul className="space-y-1 text-sm">
                {order.notes.map((n) => (
                  <li key={n.id} className="rounded-md bg-muted px-3 py-2">
                    <p>{n.body}</p>
                    <p className="text-muted-foreground text-xs">
                      {when(n.created_at)}
                    </p>
                  </li>
                ))}
                {order.notes.length === 0 && (
                  <li className="text-muted-foreground">Nenhuma nota.</li>
                )}
              </ul>
              {canAddNote && (
                <div className="flex gap-2">
                  <Input
                    placeholder="Adicionar nota interna"
                    value={note}
                    onChange={(e) => setNote(e.target.value)}
                  />
                  <Button
                    variant="outline"
                    disabled={!note.trim() || noteMutation.isPending}
                    onClick={() => noteMutation.mutate(note.trim())}
                  >
                    Adicionar
                  </Button>
                </div>
              )}
            </section>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
