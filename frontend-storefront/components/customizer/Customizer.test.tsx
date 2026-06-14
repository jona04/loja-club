import { fireEvent, render, screen } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"

import type { StorefrontProduct } from "@/lib/api"
import type { CustomizationSession } from "@/lib/customizer/session-types"
import type { CustomizerController } from "@/lib/use-customizer"

// next/dynamic → render the loaded component synchronously (skip the 3D import).
vi.mock("next/dynamic", () => ({
  default: () => () => <div data-testid="scene3d" />,
}))

let webgl = true
vi.mock("@/lib/webgl", () => ({ hasWebGL: () => webgl }))

vi.mock("@/lib/customization-actions", () => ({
  uploadCustomizationArt: vi.fn(),
  approveCustomization: vi.fn(),
}))

vi.mock("@/lib/cart-actions", () => ({ addToCart: vi.fn() }))

vi.mock("@/lib/customizer/use-session-images", () => ({
  useSessionImages: () => new Map(),
}))

let controller: CustomizerController
vi.mock("@/lib/use-customizer", () => ({
  AUTOSAVE_DEBOUNCE_MS: 800,
  useCustomizer: () => controller,
}))

import { Customizer } from "@/components/customizer/Customizer"

const PRODUCT = {
  id: "p1",
  slug: "caneca",
  name: "Caneca",
  description: null,
  type: "image_3d_customizable",
  price_amount_minor: 2500,
  price_currency: "BRL",
  is_featured: false,
  images: [{ url: "https://cdn.test/a.png" }],
} as StorefrontProduct

const SESSION: CustomizationSession = {
  id: "s1",
  product_id: "p1",
  status: "draft",
  state_json: {
    schema_version: 1,
    model: { model_id: "m", version_id: "v" },
    layers: [],
  },
  version: {
    id: "v",
    version: 1,
    glb_url: "https://cdn.test/x.glb",
    printable_areas: [
      {
        id: "front",
        label: "Frente",
        uv_rect: { u0: 0.2, v0: 0.3, u1: 0.8, v1: 0.7 },
      },
    ],
    text_config: { fonts: ["inter"], min_size: 8, max_size: 96 },
    art_limits: {},
  },
  uploads: [],
  snapshot_url: null,
  expires_at: "",
  approved_at: null,
}

const setState = vi.fn()

function ready(
  layers: CustomizationSession["state_json"]["layers"] = [],
): CustomizerController {
  const state = { ...SESSION.state_json, layers }
  return {
    session: { ...SESSION, state_json: state },
    state,
    status: "ready",
    error: null,
    saving: false,
    setState,
  }
}

describe("Customizer (editor)", () => {
  beforeEach(() => {
    webgl = true
    setState.mockReset()
    controller = ready()
  })

  it("mounts the editor (2D area + 3D) when ready", () => {
    render(<Customizer product={PRODUCT} />)
    expect(screen.getByText("Área de personalização")).toBeInTheDocument()
    expect(screen.getByTestId("scene3d")).toBeInTheDocument()
  })

  it("falls back when WebGL is unavailable", () => {
    webgl = false
    render(<Customizer product={PRODUCT} />)
    expect(screen.queryByTestId("scene3d")).not.toBeInTheDocument()
    expect(
      screen.getByText(/não foi possível abrir o editor 3d/i),
    ).toBeInTheDocument()
  })

  it("blocks approval until there is a layer", () => {
    render(<Customizer product={PRODUCT} />)
    expect(
      screen.getByRole("button", { name: /aprovar personalização/i }),
    ).toBeDisabled()
  })

  it("enables approval with a layer", () => {
    controller = ready([
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
    ])
    render(<Customizer product={PRODUCT} />)
    expect(
      screen.getByRole("button", { name: /aprovar personalização/i }),
    ).not.toBeDisabled()
  })

  it("adds a text layer to the state on 'Adicionar texto'", () => {
    render(<Customizer product={PRODUCT} />)
    fireEvent.click(screen.getByRole("button", { name: "Adicionar texto" }))
    expect(setState).toHaveBeenCalledTimes(1)
    const next = setState.mock.calls[0][0]
    expect(next.layers).toHaveLength(1)
    expect(next.layers[0].kind).toBe("text")
  })
})
