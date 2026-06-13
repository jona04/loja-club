import { render, screen } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"

import type { StorefrontProduct } from "@/lib/api"
import type { CustomizerController } from "@/lib/use-customizer"

// next/dynamic → render the loaded component synchronously (skip the 3D import).
vi.mock("next/dynamic", () => ({
  default: () => () => <div data-testid="scene3d" />,
}))

let webgl = true
vi.mock("@/lib/webgl", () => ({ hasWebGL: () => webgl }))

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

function ready(): CustomizerController {
  return {
    session: {
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
        text_config: {},
        art_limits: {},
      },
      snapshot_url: null,
      expires_at: "",
      approved_at: null,
    },
    state: null,
    status: "ready",
    error: null,
    saving: false,
    setState: vi.fn(),
  }
}

const renderEditor = () => render(<Customizer product={PRODUCT} />)

describe("Customizer", () => {
  beforeEach(() => {
    webgl = true
    controller = ready()
  })

  it("mounts the 2 panels (area + 3D) when ready", () => {
    renderEditor()
    expect(screen.getByText("Frente")).toBeInTheDocument()
    expect(screen.getByTestId("scene3d")).toBeInTheDocument()
  })

  it("falls back (no 3D) when WebGL is unavailable", () => {
    webgl = false
    renderEditor()
    expect(screen.queryByTestId("scene3d")).not.toBeInTheDocument()
    expect(
      screen.getByText(/não foi possível abrir o editor 3d/i),
    ).toBeInTheDocument()
  })

  it("falls back when the session errors", () => {
    controller = { ...ready(), status: "error", error: "boom" }
    renderEditor()
    expect(screen.queryByTestId("scene3d")).not.toBeInTheDocument()
    expect(
      screen.getByText(/não foi possível abrir o editor 3d/i),
    ).toBeInTheDocument()
  })
})
