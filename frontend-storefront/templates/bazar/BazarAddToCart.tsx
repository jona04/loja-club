"use client"

import Link from "next/link"
import { useState } from "react"

import type { StorefrontProduct } from "@/lib/api"
import { useCart } from "@/lib/cart"
import { isCustomizable } from "@/lib/product"

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

  return (
    <div className="flex flex-col gap-4">
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
          disabled={cart.loading}
          onClick={() => cart.add(product.id, qty)}
          className="flex-1 rounded-xl bg-indigo-600 py-4 font-bold text-white shadow-float transition hover:bg-indigo-700 disabled:opacity-60"
        >
          Adicionar ao carrinho
        </button>
      </div>
      {isCustomizable(product) && (
        <Link
          href={`/products/${product.slug}/personalizar`}
          className="flex items-center justify-center gap-2 rounded-xl border-2 border-gray-200 py-4 font-bold text-gray-700 transition hover:border-indigo-600 hover:text-indigo-600"
        >
          <i className="fa-solid fa-cube" /> Personalizar em 3D
        </Link>
      )}
    </div>
  )
}
