import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { render, screen, waitFor } from "@testing-library/react"
import type { ReactNode } from "react"
import { describe, expect, it, vi } from "vitest"

import type { ThemeTemplatePublic } from "@/client"

const getLayoutSettings = vi.fn()
const updateLayoutSettings = vi.fn().mockResolvedValue({})
const resetLayoutSettings = vi.fn().mockResolvedValue({})

vi.mock("@/client", () => ({
  ContentService: {
    getLayoutSettings: () => getLayoutSettings(),
    updateLayoutSettings: (args: unknown) => updateLayoutSettings(args),
    resetLayoutSettings: (args: unknown) => resetLayoutSettings(args),
  },
}))

vi.mock("@/hooks/useCustomToast", () => ({
  default: () => ({ showSuccessToast: vi.fn(), showErrorToast: vi.fn() }),
}))

import { TemplateSettingsForm } from "./TemplateSettingsForm"

const TEMPLATES: ThemeTemplatePublic[] = [
  {
    id: "aurora",
    name: "Aurora",
    is_active: true,
    settings_schema: [
      {
        key: "announcement_text",
        type: "text",
        label: "Anúncio",
        group: "Topo",
        default: "",
      },
      {
        key: "show_trust_badges",
        type: "boolean",
        label: "Selos",
        group: "Home",
        default: true,
      },
    ],
  },
]

function wrapper({ children }: { children: ReactNode }) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>
}

describe("TemplateSettingsForm", () => {
  it("renders the active template's schema fields with merged values", async () => {
    getLayoutSettings.mockResolvedValue({
      template_id: "aurora",
      settings: { announcement_text: "Promo" },
    })
    render(
      <TemplateSettingsForm storeId="s1" templates={TEMPLATES} canEdit />,
      {
        wrapper,
      },
    )
    const input = await screen.findByLabelText("Anúncio")
    await waitFor(() => expect(input).toHaveValue("Promo"))
    // show_trust_badges has no override → falls back to its schema default (true).
    expect(screen.getByRole("checkbox")).toBeChecked()
    expect(
      screen.getByRole("button", { name: "Salvar personalização" }),
    ).not.toBeDisabled()
  })

  it("renders nothing when the active template has no schema", async () => {
    getLayoutSettings.mockResolvedValue({ template_id: "other", settings: {} })
    const { container } = render(
      <TemplateSettingsForm storeId="s1" templates={TEMPLATES} canEdit />,
      { wrapper },
    )
    await waitFor(() => expect(getLayoutSettings).toHaveBeenCalled())
    expect(container.querySelector("button")).toBeNull()
  })

  it("disables every control without layout.update", async () => {
    getLayoutSettings.mockResolvedValue({ template_id: "aurora", settings: {} })
    render(
      <TemplateSettingsForm
        storeId="s1"
        templates={TEMPLATES}
        canEdit={false}
      />,
      { wrapper },
    )
    expect(await screen.findByLabelText("Anúncio")).toBeDisabled()
    expect(
      screen.getByRole("button", { name: "Salvar personalização" }),
    ).toBeDisabled()
  })
})
