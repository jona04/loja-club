"use client"

import Link from "next/link"
import { useState } from "react"

import { VariantSelect } from "@/components/VariantSelect"
import type { StorefrontProduct } from "@/lib/api"
import { useCart } from "@/lib/cart"
import { isCustomizable } from "@/lib/product"
import { useVariantSelection } from "@/lib/use-variant-selection"

/**
 * Bazar product actions (faithful to the template): a quantity stepper + a bold
 * "Adicionar ao carrinho" (adds to the cart + opens the drawer) and the reserved
 * "Personalizar em 3D" placeholder (Fase 5).
 *
 * @param product - The product to add.
 * @returns The quantity + action buttons.
 */
export function BazarAddToCart({ product }: { product: StorefrontProduct }) {
  const cart = useCart()
  const [qty, setQty] = useState(1)
  const variant = useVariantSelection(product)

  if (isCustomizable(product)) {
    return (
      <Link
        href={`/products/${product.slug}/personalizar`}
        className="flex items-center justify-center gap-2 rounded-xl bg-indigo-600 py-4 font-bold text-white shadow-float transition hover:bg-indigo-700"
      >
        <i className="fa-solid fa-cube" /> Personalizar em 3D
      </Link>
    )
  }

  return (
    <div className="flex flex-col gap-4">
      {variant.hasVariants && (
        <VariantSelect
          variants={variant.variants}
          value={variant.selectedId}
          onChange={variant.setSelectedId}
          className="w-full rounded-xl border border-gray-200 bg-gray-50 px-3 py-3 font-medium"
        />
      )}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 rounded-xl border border-gray-200 bg-gray-50 p-1.5">
          <button
            type="button"
            onClick={() => setQty((q) => Math.max(1, q - 1))}
            className="flex h-8 w-8 items-center justify-center text-gray-500 hover:text-indigo-600"
            aria-label="Diminuir"
          >
            <i className="fa-solid fa-minus text-xs" />
          </button>
          <span className="w-8 text-center font-bold">{qty}</span>
          <button
            type="button"
            onClick={() => setQty((q) => q + 1)}
            className="flex h-8 w-8 items-center justify-center text-gray-500 hover:text-indigo-600"
            aria-label="Aumentar"
          >
            <i className="fa-solid fa-plus text-xs" />
          </button>
        </div>
        <button
          type="button"
          disabled={cart.loading || !variant.canAdd}
          onClick={() => cart.add(product.id, qty, variant.cartVariantId)}
          className="flex-1 rounded-xl bg-indigo-600 py-4 font-bold text-white shadow-float transition hover:bg-indigo-700 disabled:opacity-60"
        >
          {variant.outOfStock ? "Esgotado" : "Adicionar ao carrinho"}
        </button>
      </div>
    </div>
  )
}
