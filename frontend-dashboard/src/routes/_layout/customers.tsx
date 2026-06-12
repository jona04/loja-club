import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"

import { CustomersService, type OrderStatus } from "@/client"
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

export const Route = createFileRoute("/_layout/customers")({
  component: CustomersRoute,
  head: () => ({ meta: [{ title: "Clientes - Loja Club" }] }),
})

function CustomersRoute() {
  return (
    <StoreGate>
      <CustomersScreen />
    </StoreGate>
  )
}

const PAGE_SIZE = 20

/** Human pt-BR label for an order status (shown in the purchase history). */
const STATUS_LABEL: Record<OrderStatus, string> = {
  pending_payment: "Aguardando pagamento",
  paid: "Pago",
  processing: "Em preparação",
  shipped: "Enviado",
  delivered: "Entregue",
  canceled: "Cancelado",
}

/** Format minor units + currency, e.g. `BRL 39.00`. */
const money = (minor: number, currency: string): string =>
  `${currency} ${(minor / 100).toFixed(2)}`

/** Format an ISO timestamp for pt-BR display. */
const when = (iso: string): string => new Date(iso).toLocaleString("pt-BR")

/** Build a WhatsApp link to talk to a customer. */
const whatsappLink = (phone: string): string =>
  `https://wa.me/${phone.replace(/\D/g, "")}`

/**
 * The merchant Customers screen: list/search customers (name/email/phone) and
 * open one to see the profile, saved addresses and order history — gated by
 * `customers.view` (UI gating only; the backend enforces the real
 * authorization). Read-only in this phase.
 *
 * @returns The Customers screen.
 */
export function CustomersScreen() {
  const { activeStore, permissions } = useActiveStore()
  const [page, setPage] = useState(0)
  const [search, setSearch] = useState("")
  const [openId, setOpenId] = useState<string | null>(null)

  const storeId = activeStore?.id ?? ""
  const canView = permissions.includes("customers.view")

  const customersQuery = useQuery({
    queryKey: ["customers", storeId, page, search],
    queryFn: () =>
      CustomersService.listCustomers({
        storeId,
        skip: page * PAGE_SIZE,
        limit: PAGE_SIZE,
        search: search.trim() || undefined,
      }),
    enabled: storeId !== "" && canView,
  })

  if (!activeStore) {
    return null
  }

  const customers = customersQuery.data?.data ?? []
  const count = customersQuery.data?.count ?? 0

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="font-bold text-2xl tracking-tight">Clientes</h1>
          <p className="text-muted-foreground">
            {count} cliente(s) em {activeStore.name}
          </p>
        </div>
        <Input
          className="w-72"
          placeholder="Buscar por nome, e-mail ou telefone"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value)
            setPage(0)
          }}
        />
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Nome</TableHead>
            <TableHead>E-mail</TableHead>
            <TableHead>Telefone</TableHead>
            <TableHead>Desde</TableHead>
            <TableHead className="w-0" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {customers.map((customer) => (
            <TableRow key={customer.id}>
              <TableCell className="font-medium">{customer.name}</TableCell>
              <TableCell>{customer.email ?? "—"}</TableCell>
              <TableCell>{customer.phone_e164 ?? "—"}</TableCell>
              <TableCell className="text-muted-foreground">
                {when(customer.created_at)}
              </TableCell>
              <TableCell className="flex justify-end">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setOpenId(customer.id)}
                >
                  Ver
                </Button>
              </TableCell>
            </TableRow>
          ))}
          {customers.length === 0 && (
            <TableRow>
              <TableCell colSpan={5} className="text-muted-foreground">
                Nenhum cliente.
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
        <CustomerDetailDialog
          storeId={storeId}
          customerId={openId}
          onClose={() => setOpenId(null)}
        />
      )}
    </div>
  )
}

export function CustomerDetailDialog({
  storeId,
  customerId,
  onClose,
}: {
  storeId: string
  customerId: string
  onClose: () => void
}) {
  const detailQuery = useQuery({
    queryKey: ["customer", storeId, customerId],
    queryFn: () => CustomersService.getCustomer({ storeId, customerId }),
  })
  const customer = detailQuery.data

  return (
    <Dialog open onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="max-h-[90vh] max-w-2xl overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{customer ? customer.name : "Cliente"}</DialogTitle>
        </DialogHeader>

        {!customer ? (
          <p className="text-muted-foreground text-sm">Carregando…</p>
        ) : (
          <div className="space-y-5">
            <section className="space-y-1 text-sm">
              {customer.email && (
                <p className="text-muted-foreground">{customer.email}</p>
              )}
              {customer.phone_e164 && (
                <div className="flex items-center gap-2">
                  <span className="text-muted-foreground">
                    {customer.phone_e164}
                  </span>
                  <a
                    href={whatsappLink(customer.phone_e164)}
                    target="_blank"
                    rel="noreferrer"
                    className="text-green-600 text-xs underline underline-offset-2"
                  >
                    Falar no WhatsApp
                  </a>
                </div>
              )}
              <p className="text-muted-foreground text-xs">
                Cliente desde {when(customer.created_at)}
              </p>
            </section>

            <Separator />

            <section className="space-y-2">
              <h3 className="font-semibold text-sm">Endereços</h3>
              {customer.addresses.length === 0 ? (
                <p className="text-muted-foreground text-sm">
                  Nenhum endereço salvo.
                </p>
              ) : (
                <ul className="space-y-1 text-sm text-muted-foreground">
                  {customer.addresses.map((address) => (
                    <li key={address.id}>
                      {[
                        address.line1,
                        address.number,
                        address.line2,
                        address.neighborhood,
                        address.city,
                        address.state,
                        address.postal_code,
                      ]
                        .filter(Boolean)
                        .join(", ")}
                    </li>
                  ))}
                </ul>
              )}
            </section>

            <section className="space-y-2">
              <h3 className="font-semibold text-sm">Histórico de pedidos</h3>
              {customer.orders.length === 0 ? (
                <p className="text-muted-foreground text-sm">Nenhum pedido.</p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Nº</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Total</TableHead>
                      <TableHead>Data</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {customer.orders.map((order) => (
                      <TableRow key={order.id}>
                        <TableCell className="font-medium">
                          #{order.order_number}
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">
                            {STATUS_LABEL[order.status]}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {money(order.total_amount_minor, order.currency)}
                        </TableCell>
                        <TableCell className="text-muted-foreground">
                          {when(order.created_at)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </section>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
