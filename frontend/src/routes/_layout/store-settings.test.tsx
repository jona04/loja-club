import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { render, screen } from "@testing-library/react"
import type { ReactNode } from "react"
import { describe, expect, it, vi } from "vitest"

vi.mock("@/client", () => ({
  StoresService: { getStoreSettings: vi.fn().mockResolvedValue({}) },
}))

const activeStore = vi.fn()
vi.mock("@/hooks/useActiveStore", () => ({
  useActiveStore: () => activeStore(),
}))

import { StoreSettingsScreen } from "./store-settings"

function wrapper({ children }: { children: ReactNode }) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>
}

const base = { activeStore: { id: "s1", name: "S", status: "draft" } }

describe("StoreSettingsScreen permission gating", () => {
  it("disables saving without settings.update", () => {
    activeStore.mockReturnValue({ ...base, permissions: [] })
    render(<StoreSettingsScreen />, { wrapper })
    expect(screen.getByRole("button", { name: "Salvar" })).toBeDisabled()
  })

  it("enables saving with settings.update", () => {
    activeStore.mockReturnValue({ ...base, permissions: ["settings.update"] })
    render(<StoreSettingsScreen />, { wrapper })
    expect(screen.getByRole("button", { name: "Salvar" })).not.toBeDisabled()
  })
})
