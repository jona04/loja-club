"use client"

import { useState } from "react"

import type { StorefrontProduct, StorefrontVariant } from "@/lib/api"

/** The variant selection state shared by every template's add-to-cart. */
export interface VariantSelection {
  /** Whether the product has selectable variants. */
  hasVariants: boolean
  variants: StorefrontVariant[]
  selectedId: string | undefined
  setSelectedId: (id: string) => void
  /** Whether add-to-cart is allowed (a selection that is in stock). */
  canAdd: boolean
  /** Whether the current selection (or the variant-less product) is sold out. */
  outOfStock: boolean
  /** The `variant_id` to send to the cart (undefined for variant-less products). */
  cartVariantId: string | undefined
}

/**
 * Drive variant selection + availability for a product page (P7-SF-02).
 *
 * Defaults to the first in-stock variant; reports whether adding to the cart is
 * allowed and which `variant_id` to send. For variant-less products, falls back
 * to the product-level stock.
 *
 * @param product - The storefront product (detail payload, with `variants`).
 * @returns The selection state + helpers.
 */
export function useVariantSelection(
  product: StorefrontProduct,
): VariantSelection {
  const variants = product.variants ?? []
  const hasVariants = variants.length > 0
  const [selectedId, setSelectedId] = useState<string | undefined>(
    () => (variants.find((v) => v.in_stock) ?? variants[0])?.id,
  )

  const selected = hasVariants
    ? (variants.find((v) => v.id === selectedId) ?? null)
    : null
  const outOfStock = hasVariants
    ? !(selected?.in_stock ?? false)
    : !product.in_stock

  return {
    hasVariants,
    variants,
    selectedId,
    setSelectedId,
    canAdd: !outOfStock,
    outOfStock,
    cartVariantId: hasVariants ? selectedId : undefined,
  }
}
