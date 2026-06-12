import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import type { ReactNode } from "react"
import { describe, expect, it, vi } from "vitest"

vi.mock("@/client", () => {
  const summary = {
    id: "o1",
    order_number: 7,
    status: "pending_payment",
    currency: "BRL",
    total_amount_minor: 3900,
    item_count: 2,
    customer_name: "Ana",
    created_at: "2026-06-12T10:00:00Z",
  }
  const detail = {
    ...summary,
    subtotal_amount_minor: 3000,
    shipping_amount_minor: 900,
    discount_amount_minor: 0,
    shipping_method_type: "fixed_shipping",
    shipping_method_name: "Frete",
    customer: {
      id: "c1",
      name: "Ana",
      email: "ana@x.com",
      phone_e164: "+5586999990000",
    },
    address: {
      recipient_name: null,
      line1: "Rua A",
      number: "123",
      line2: null,
      neighborhood: "Centro",
      city: "SP",
      state: "SP",
      postal_code: "01000-000",
      country: "BR",
    },
    items: [
      {
        id: "i1",
        product_id: "p1",
        variant_id: null,
        name: "Caneca",
        quantity: 2,
        unit_price_amount_minor: 1500,
        unit_price_currency: "BRL",
        line_total_amount_minor: 3000,
      },
    ],
    status_history: [
      {
        status: "pending_payment",
        note: null,
        created_at: "2026-06-12T10:00:00Z",
      },
    ],
    notes: [],
  }
  return {
    OrdersService: {
      listOrders: vi.fn().mockResolvedValue({ data: [summary], count: 1 }),
      getOrder: vi.fn().mockResolvedValue(detail),
      updateStatus: vi.fn().mockResolvedValue(detail),
      cancelOrder: vi.fn().mockResolvedValue(detail),
      addNote: vi.fn().mockResolvedValue({}),
    },
  }
})

const activeStore = vi.fn()
vi.mock("@/hooks/useActiveStore", () => ({
  useActiveStore: () => activeStore(),
}))

import { OrdersService } from "@/client"
import { OrderDetailDialog, OrdersScreen } from "./orders"

function wrapper({ children }: { children: ReactNode }) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>
}

const base = { activeStore: { id: "s1", name: "S", status: "active" } }

describe("OrdersScreen", () => {
  it("lists orders with number, customer and status", async () => {
    activeStore.mockReturnValue({ ...base, permissions: ["orders.view"] })
    render(<OrdersScreen />, { wrapper })
    expect(await screen.findByText("#7")).toBeInTheDocument()
    expect(screen.getByText("Ana")).toBeInTheDocument()
    expect(screen.getByText("Aguardando pagamento")).toBeInTheDocument()
  })
})

describe("OrderDetailDialog actions", () => {
  it("marks payment received with orders.update_status", async () => {
    render(
      <OrderDetailDialog
        storeId="s1"
        orderId="o1"
        permissions={["orders.view", "orders.update_status"]}
        onClose={vi.fn()}
      />,
      { wrapper },
    )
    const button = await screen.findByRole("button", { name: "Marcar pago" })
    fireEvent.click(button)
    await waitFor(() => {
      expect(OrdersService.updateStatus).toHaveBeenCalledWith({
        storeId: "s1",
        orderId: "o1",
        requestBody: { status: "paid" },
      })
    })
  })

  it("hides the mark-paid action without orders.update_status", async () => {
    render(
      <OrderDetailDialog
        storeId="s1"
        orderId="o1"
        permissions={["orders.view"]}
        onClose={vi.fn()}
      />,
      { wrapper },
    )
    // Wait for the detail to load, then assert the action is absent.
    await screen.findByText("Rua A, 123, Centro, SP, SP, 01000-000")
    expect(
      screen.queryByRole("button", { name: "Marcar pago" }),
    ).not.toBeInTheDocument()
  })
})
