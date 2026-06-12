import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { render, screen } from "@testing-library/react"
import type { ReactNode } from "react"
import { describe, expect, it, vi } from "vitest"

vi.mock("@/client", () => ({
  ContentService: {
    listTemplates: vi.fn().mockResolvedValue([]),
    getLayout: vi.fn().mockResolvedValue({}),
    updateLayout: vi.fn().mockResolvedValue({}),
    getLayoutSettings: vi.fn().mockResolvedValue({}),
    updateLayoutSettings: vi.fn().mockResolvedValue({}),
    resetLayoutSettings: vi.fn().mockResolvedValue({}),
    listMyTemplates: vi.fn().mockResolvedValue([]),
  },
}))

const activeStore = vi.fn()
vi.mock("@/hooks/useActiveStore", () => ({
  useActiveStore: () => activeStore(),
}))

import { StoreLayoutScreen } from "./store-layout"

function wrapper({ children }: { children: ReactNode }) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>
}

const base = { activeStore: { id: "s1", name: "S", status: "draft" } }

describe("StoreLayoutScreen permission gating", () => {
  it("disables saving without layout.update", () => {
    activeStore.mockReturnValue({ ...base, permissions: [] })
    render(<StoreLayoutScreen />, { wrapper })
    expect(screen.getByRole("button", { name: "Salvar template e aparência" })).toBeDisabled()
  })

  it("enables saving with layout.update", () => {
    activeStore.mockReturnValue({ ...base, permissions: ["layout.update"] })
    render(<StoreLayoutScreen />, { wrapper })
    expect(screen.getByRole("button", { name: "Salvar template e aparência" })).not.toBeDisabled()
  })
})
