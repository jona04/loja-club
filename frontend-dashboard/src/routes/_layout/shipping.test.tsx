import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import type { ReactNode } from "react"
import { describe, expect, it, vi } from "vitest"

vi.mock("@/client", () => ({
  ShippingService: {
    listMethods: vi.fn().mockResolvedValue([
      {
        id: "m1",
        store_id: "s1",
        type: "fixed_shipping",
        name: "Correios",
        description: null,
        is_active: true,
        price_amount_minor: 1500,
        min_order_amount_minor: null,
      },
    ]),
    createMethod: vi.fn().mockResolvedValue({}),
    updateMethod: vi.fn().mockResolvedValue({}),
    deleteMethod: vi.fn().mockResolvedValue(undefined),
  },
}))

const activeStore = vi.fn()
vi.mock("@/hooks/useActiveStore", () => ({
  useActiveStore: () => activeStore(),
}))

import { ShippingService } from "@/client"
import { ShippingScreen } from "./shipping"

function wrapper({ children }: { children: ReactNode }) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>
}

const base = { activeStore: { id: "s1", name: "S", status: "active" } }

describe("ShippingScreen", () => {
  it("lists methods with type and value", async () => {
    activeStore.mockReturnValue({ ...base, permissions: ["shipping.view"] })
    render(<ShippingScreen />, { wrapper })
    expect(await screen.findByText("Correios")).toBeInTheDocument()
    expect(screen.getByText("Frete fixo")).toBeInTheDocument() // type label
    expect(screen.getByText("R$ 15.00")).toBeInTheDocument()
    expect(screen.getByText("Ativo")).toBeInTheDocument()
  })

  it("disables creating without shipping.create", () => {
    activeStore.mockReturnValue({ ...base, permissions: ["shipping.view"] })
    render(<ShippingScreen />, { wrapper })
    expect(screen.getByRole("button", { name: "Novo método" })).toBeDisabled()
  })

  it("toggles a method's active state with shipping.update", async () => {
    activeStore.mockReturnValue({
      ...base,
      permissions: ["shipping.view", "shipping.update"],
    })
    render(<ShippingScreen />, { wrapper })
    fireEvent.click(await screen.findByRole("button", { name: "Desativar" }))
    await waitFor(() => {
      expect(ShippingService.updateMethod).toHaveBeenCalledWith({
        storeId: "s1",
        methodId: "m1",
        requestBody: { is_active: false },
      })
    })
  })
})
