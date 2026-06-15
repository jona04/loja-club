import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import type { ReactNode } from "react"
import { describe, expect, it, vi } from "vitest"

vi.mock("@/client", () => ({
  CatalogService: {
    listProducts: vi.fn().mockResolvedValue({ data: [], count: 0 }),
    getInventory: vi.fn().mockResolvedValue({ quantity: 200 }),
    listImages: vi.fn().mockResolvedValue([]),
    updateProduct: vi.fn().mockResolvedValue({}),
    setInventory: vi.fn().mockResolvedValue({ quantity: 50 }),
  },
  CustomizationService: {
    getProductModel: vi.fn().mockResolvedValue(null),
    linkProductModel: vi.fn().mockResolvedValue({}),
    unlinkProductModel: vi.fn().mockResolvedValue(undefined),
  },
  DCatalogService: { listModels: vi.fn().mockResolvedValue([]) },
  MediaService: { uploadMedia: vi.fn() },
}))

const activeStore = vi.fn()
vi.mock("@/hooks/useActiveStore", () => ({
  useActiveStore: () => activeStore(),
}))

import { CatalogService, type ProductPublic } from "@/client"
import { EditProductDialog, ProductsScreen } from "./products"

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

describe("EditProductDialog stock", () => {
  it("pre-fills the stock and saves it together with Salvar", async () => {
    const product: ProductPublic = {
      id: "p1",
      store_id: "s1",
      name: "Mug",
      slug: "mug",
      description: null,
      status: "draft",
      price_amount_minor: 1000,
      price_currency: "USD",
      is_featured: false,
    }
    render(
      <EditProductDialog
        storeId="s1"
        product={product}
        canUpdate
        canManage3d
        onClose={vi.fn()}
        onSaved={vi.fn()}
      />,
      { wrapper },
    )
    // Pre-filled from getInventory (the bug was that it came empty).
    const stockInput = await screen.findByDisplayValue("200")
    fireEvent.change(stockInput, { target: { value: "50" } })
    // A single "Salvar" must persist the stock too (no separate button).
    fireEvent.click(screen.getByRole("button", { name: "Salvar" }))
    await waitFor(() => {
      expect(CatalogService.setInventory).toHaveBeenCalledWith({
        storeId: "s1",
        productId: "p1",
        requestBody: { quantity: 50 },
      })
    })
  })
})
