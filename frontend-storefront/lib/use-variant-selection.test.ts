import { act, renderHook } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import type { StorefrontProduct, StorefrontVariant } from "@/lib/api"
import { useVariantSelection } from "@/lib/use-variant-selection"

const PRODUCT: StorefrontProduct = {
  id: "p1",
  slug: "tee",
  name: "Tee",
  description: null,
  type: "image",
  price_amount_minor: 1500,
  price_currency: "BRL",
  is_featured: false,
  images: [],
  variants: [],
  in_stock: true,
  available_quantity: null,
}

const variant = (
  id: string,
  in_stock: boolean,
  available_quantity: number | null,
): StorefrontVariant => ({
  id,
  name: id.toUpperCase(),
  attributes: null,
  price_amount_minor: 1800,
  price_currency: "BRL",
  in_stock,
  available_quantity,
})

describe("useVariantSelection", () => {
  it("variant-less product is addable from product-level stock", () => {
    const { result } = renderHook(() => useVariantSelection(PRODUCT))
    expect(result.current.hasVariants).toBe(false)
    expect(result.current.canAdd).toBe(true)
    expect(result.current.cartVariantId).toBeUndefined()
  })

  it("variant-less out-of-stock product cannot be added", () => {
    const { result } = renderHook(() =>
      useVariantSelection({ ...PRODUCT, in_stock: false }),
    )
    expect(result.current.outOfStock).toBe(true)
    expect(result.current.canAdd).toBe(false)
  })

  it("defaults to the first in-stock variant and sends its id", () => {
    const product = {
      ...PRODUCT,
      variants: [variant("v1", false, 0), variant("v2", true, null)],
    }
    const { result } = renderHook(() => useVariantSelection(product))
    expect(result.current.selectedId).toBe("v2")
    expect(result.current.cartVariantId).toBe("v2")
    expect(result.current.canAdd).toBe(true)
  })

  it("selecting an out-of-stock variant blocks the add", () => {
    const product = {
      ...PRODUCT,
      variants: [variant("v1", false, 0), variant("v2", true, null)],
    }
    const { result } = renderHook(() => useVariantSelection(product))
    act(() => result.current.setSelectedId("v1"))
    expect(result.current.outOfStock).toBe(true)
    expect(result.current.canAdd).toBe(false)
  })
})
