import { describe, expect, it } from "vitest"

import type { StorePublic } from "@/client"
import { resolveActiveStore } from "./activeStore"

const store = (id: string): StorePublic => ({ id }) as StorePublic

describe("resolveActiveStore", () => {
  it("returns 'none' when the user has no stores", () => {
    expect(resolveActiveStore([], null)).toEqual({ status: "none" })
  })

  it("auto-selects the only store (enters directly)", () => {
    const only = store("a")
    expect(resolveActiveStore([only], null)).toEqual({
      status: "ready",
      store: only,
    })
  })

  it("requires a choice with multiple stores and nothing persisted", () => {
    expect(resolveActiveStore([store("a"), store("b")], null)).toEqual({
      status: "select",
    })
  })

  it("uses the persisted store when it is still valid", () => {
    const b = store("b")
    expect(resolveActiveStore([store("a"), b], "b")).toEqual({
      status: "ready",
      store: b,
    })
  })

  it("falls back to selection when the persisted id is stale", () => {
    expect(resolveActiveStore([store("a"), store("b")], "gone")).toEqual({
      status: "select",
    })
  })

  it("still auto-selects a single store when the persisted id is stale", () => {
    const a = store("a")
    expect(resolveActiveStore([a], "gone")).toEqual({
      status: "ready",
      store: a,
    })
  })
})
