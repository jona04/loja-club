import { act, renderHook, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"

import type {
  CustomizationSession,
  CustomizationState,
} from "@/lib/customization-actions"

const startCustomization = vi.fn()
const saveCustomizationState = vi.fn()

vi.mock("@/lib/customization-actions", () => ({
  startCustomization: (id: string) => startCustomization(id),
  saveCustomizationState: (id: string, state: CustomizationState) =>
    saveCustomizationState(id, state),
}))

import { AUTOSAVE_DEBOUNCE_MS, useCustomizer } from "@/lib/use-customizer"

const STATE: CustomizationState = {
  schema_version: 1,
  model: { model_id: "m", version_id: "v" },
  layers: [],
}

const SESSION: CustomizationSession = {
  id: "s1",
  product_id: "p1",
  status: "draft",
  state_json: STATE,
  version: {
    id: "v",
    version: 1,
    glb_url: "https://cdn.test/x.glb",
    printable_areas: [],
    text_config: {},
    art_limits: {},
  },
  snapshot_url: null,
  expires_at: "2099-01-01T00:00:00Z",
  approved_at: null,
}

describe("useCustomizer", () => {
  beforeEach(() => {
    startCustomization.mockReset().mockResolvedValue(SESSION)
    saveCustomizationState.mockReset().mockResolvedValue(SESSION)
  })

  it("starts (restores) the session on mount", async () => {
    const { result } = renderHook(() => useCustomizer("p1"))
    await waitFor(() => expect(result.current.status).toBe("ready"))
    expect(startCustomization).toHaveBeenCalledWith("p1")
    expect(result.current.session?.id).toBe("s1")
  })

  it("does not autosave before any edit", async () => {
    vi.useFakeTimers()
    try {
      const { result } = renderHook(() => useCustomizer("p1"))
      await act(async () => {})
      expect(result.current.status).toBe("ready")
      act(() => {
        vi.advanceTimersByTime(AUTOSAVE_DEBOUNCE_MS * 2)
      })
      expect(saveCustomizationState).not.toHaveBeenCalled()
    } finally {
      vi.useRealTimers()
    }
  })

  it("autosaves (debounced) after a state change", async () => {
    vi.useFakeTimers()
    try {
      const { result } = renderHook(() => useCustomizer("p1"))
      await act(async () => {})
      const next = { ...STATE, layers: [{ id: "l1" }] }
      act(() => result.current.setState(next))
      // Not yet — still within the debounce window.
      act(() => {
        vi.advanceTimersByTime(AUTOSAVE_DEBOUNCE_MS - 1)
      })
      expect(saveCustomizationState).not.toHaveBeenCalled()
      act(() => {
        vi.advanceTimersByTime(1)
      })
      await act(async () => {})
      expect(saveCustomizationState).toHaveBeenCalledTimes(1)
      expect(saveCustomizationState).toHaveBeenCalledWith("s1", next)
    } finally {
      vi.useRealTimers()
    }
  })
})
