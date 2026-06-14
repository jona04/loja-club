import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { render, screen } from "@testing-library/react"
import type { ReactNode } from "react"
import { describe, expect, it, vi } from "vitest"

vi.mock("@/client", () => {
  const item = {
    id: "cs1",
    product_id: "p1",
    product_name: "Caneca",
    status: "ordered",
    is_assisted: false,
    snapshot_url: "http://cdn.test/s.png",
    created_at: "2026-06-12T10:00:00Z",
    updated_at: "2026-06-12T11:00:00Z",
    approved_at: "2026-06-12T11:00:00Z",
    order_id: "ord1",
    order_item_id: "oi1",
    production_status: "received",
  }
  const detail = {
    ...item,
    state_json: {},
    version: {
      id: "v1",
      version: 1,
      glb_url: "x",
      printable_areas: [],
      text_config: {},
      art_limits: {},
    },
    uploads: [],
    composite_url: "http://cdn.test/c.png",
    expires_at: "2026-07-12T10:00:00Z",
  }
  return {
    CustomizationService: {
      listCustomizations: vi.fn().mockResolvedValue({ data: [item], count: 1 }),
      getCustomization: vi.fn().mockResolvedValue(detail),
      updateProductionStatus: vi.fn().mockResolvedValue(detail),
      createAssistedSession: vi
        .fn()
        .mockResolvedValue({ ...detail, public_token: "tok" }),
    },
    CatalogService: {
      listProducts: vi.fn().mockResolvedValue({ data: [], count: 0 }),
    },
  }
})

const activeStore = vi.fn()
vi.mock("@/hooks/useActiveStore", () => ({
  useActiveStore: () => activeStore(),
}))

import {
  CustomizationDetailDialog,
  CustomizationsScreen,
} from "./customizations"

function wrapper({ children }: { children: ReactNode }) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>
}

const base = { activeStore: { id: "s1", name: "S", status: "active" } }

describe("CustomizationsScreen", () => {
  it("lists sessions with product, status and production status", async () => {
    activeStore.mockReturnValue({
      ...base,
      permissions: ["customization.sessions.view"],
    })
    render(<CustomizationsScreen />, { wrapper })
    expect(await screen.findByText("Caneca")).toBeInTheDocument()
    expect(screen.getByText("No pedido")).toBeInTheDocument()
    expect(screen.getByText("Arte recebida")).toBeInTheDocument()
  })
})

describe("CustomizationDetailDialog", () => {
  it("offers the production composite download", async () => {
    render(
      <CustomizationDetailDialog
        storeId="s1"
        sessionId="cs1"
        permissions={["customization.files.download"]}
        onClose={vi.fn()}
      />,
      { wrapper },
    )
    expect(
      await screen.findByText("Arte de produção (composite)"),
    ).toBeInTheDocument()
  })

  it("shows the production status control for an ordered customization", async () => {
    render(
      <CustomizationDetailDialog
        storeId="s1"
        sessionId="cs1"
        permissions={[
          "customization.files.download",
          "customization.production_status.update",
        ]}
        onClose={vi.fn()}
      />,
      { wrapper },
    )
    // The select renders with the current production label.
    expect(await screen.findByText("Produção")).toBeInTheDocument()
    expect(screen.getByRole("combobox")).toBeInTheDocument()
  })
})
