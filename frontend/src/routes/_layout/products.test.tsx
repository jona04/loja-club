import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { render, screen } from "@testing-library/react"
import type { ReactNode } from "react"
import { describe, expect, it, vi } from "vitest"

vi.mock("@/client", () => ({
  CatalogService: {
    listProducts: vi.fn().mockResolvedValue({ data: [], count: 0 }),
  },
}))

const activeStore = vi.fn()
vi.mock("@/hooks/useActiveStore", () => ({
  useActiveStore: () => activeStore(),
}))

import { ProductsScreen } from "./products"

function wrapper({ children }: { children: ReactNode }) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>
}

const base = { activeStore: { id: "s1", name: "S", status: "draft" } }

describe("ProductsScreen permission gating", () => {
  it("disables creating without catalog.product.create", () => {
    activeStore.mockReturnValue({
      ...base,
      permissions: ["catalog.product.view"],
    })
    render(<ProductsScreen />, { wrapper })
    expect(screen.getByRole("button", { name: "Novo produto" })).toBeDisabled()
  })

  it("enables creating with catalog.product.create", () => {
    activeStore.mockReturnValue({
      ...base,
      permissions: ["catalog.product.view", "catalog.product.create"],
    })
    render(<ProductsScreen />, { wrapper })
    expect(
      screen.getByRole("button", { name: "Novo produto" }),
    ).not.toBeDisabled()
  })
})
