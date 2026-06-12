import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { render, screen } from "@testing-library/react"
import type { ReactNode } from "react"
import { describe, expect, it, vi } from "vitest"

vi.mock("@/client", () => {
  const summary = {
    id: "c1",
    name: "Ana",
    email: "ana@x.com",
    phone_e164: "+5586999990000",
    created_at: "2026-06-12T10:00:00Z",
  }
  const detail = {
    ...summary,
    addresses: [
      {
        id: "a1",
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
    ],
    orders: [
      {
        id: "o1",
        order_number: 7,
        status: "paid",
        currency: "BRL",
        total_amount_minor: 3900,
        created_at: "2026-06-12T10:00:00Z",
      },
    ],
  }
  return {
    CustomersService: {
      listCustomers: vi.fn().mockResolvedValue({ data: [summary], count: 1 }),
      getCustomer: vi.fn().mockResolvedValue(detail),
    },
  }
})

const activeStore = vi.fn()
vi.mock("@/hooks/useActiveStore", () => ({
  useActiveStore: () => activeStore(),
}))

import { CustomerDetailDialog, CustomersScreen } from "./customers"

function wrapper({ children }: { children: ReactNode }) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>
}

const base = { activeStore: { id: "s1", name: "S", status: "active" } }

describe("CustomersScreen", () => {
  it("lists customers with name, email and phone", async () => {
    activeStore.mockReturnValue({ ...base, permissions: ["customers.view"] })
    render(<CustomersScreen />, { wrapper })
    expect(await screen.findByText("Ana")).toBeInTheDocument()
    expect(screen.getByText("ana@x.com")).toBeInTheDocument()
    expect(screen.getByText("+5586999990000")).toBeInTheDocument()
  })
})

describe("CustomerDetailDialog", () => {
  it("shows the saved address and order history", async () => {
    render(
      <CustomerDetailDialog storeId="s1" customerId="c1" onClose={vi.fn()} />,
      { wrapper },
    )
    expect(
      await screen.findByText("Rua A, 123, Centro, SP, SP, 01000-000"),
    ).toBeInTheDocument()
    expect(screen.getByText("#7")).toBeInTheDocument()
    expect(screen.getByText("Pago")).toBeInTheDocument()
  })
})
