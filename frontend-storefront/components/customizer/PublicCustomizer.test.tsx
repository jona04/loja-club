import { fireEvent, render, screen } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"

import type { CustomizationSession } from "@/lib/customizer/session-types"

vi.mock("next/dynamic", () => ({
  default: () => () => <div data-testid="scene3d" />,
}))
vi.mock("@/lib/customizer/use-session-images", () => ({
  useSessionImages: () => new Map(),
}))
vi.mock("@/lib/customization-actions", () => ({
  approveCustomizationViaToken: vi.fn(),
}))

import { PublicCustomizer } from "@/components/customizer/PublicCustomizer"

const SESSION: CustomizationSession = {
  id: "s1",
  product_id: "p1",
  status: "draft",
  state_json: {
    schema_version: 1,
    model: { model_id: "m", version_id: "v" },
    layers: [
      {
        id: "l1",
        kind: "text",
        area_id: "front",
        z: 0,
        transform: { x: 0.5, y: 0.5, scale: 1, rotation_deg: 0 },
        text: "Oi",
        font: "inter",
        font_size: 48,
        color: "#222",
      },
    ],
  },
  version: {
    id: "v",
    version: 1,
    glb_url: "https://cdn.test/x.glb",
    printable_areas: [
      { id: "front", uv_rect: { u0: 0.2, v0: 0.3, u1: 0.8, v1: 0.7 } },
    ],
    text_config: { max_size: 96 },
    art_limits: {},
  },
  uploads: [],
  snapshot_url: null,
  expires_at: "",
  approved_at: null,
}

describe("PublicCustomizer (read-only)", () => {
  it("is read-only: no add-layer controls", () => {
    render(<PublicCustomizer token="t1" session={SESSION} />)
    expect(screen.queryByRole("button", { name: "Adicionar texto" })).toBeNull()
    expect(screen.getByTestId("scene3d")).toBeInTheDocument()
  })

  it("requires a contact to approve", () => {
    render(<PublicCustomizer token="t1" session={SESSION} />)
    const approve = screen.getByRole("button", { name: /aprovar/i })
    expect(approve).toBeDisabled()
    fireEvent.change(screen.getByPlaceholderText(/e-mail/i), {
      target: { value: "joao@x.com" },
    })
    expect(approve).not.toBeDisabled()
  })

  it("shows approved state when already approved", () => {
    render(
      <PublicCustomizer
        token="t1"
        session={{ ...SESSION, status: "approved" }}
      />,
    )
    expect(screen.getByText(/personalização aprovada/i)).toBeInTheDocument()
  })
})
