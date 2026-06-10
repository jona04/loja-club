"use client"

import { useState } from "react"

import type { StorefrontProduct } from "@/lib/api"
import { useCart } from "@/lib/cart"

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
  const image = product.images[0]?.url ?? null

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
          onClick={() =>
            cart.add(
              {
                id: product.id,
                slug: product.slug,
                name: product.name,
                priceAmountMinor: product.price_amount_minor,
                priceCurrency: product.price_currency,
                image,
              },
              qty,
            )
          }
          className="flex-1 rounded-xl bg-indigo-600 py-4 font-bold text-white shadow-float transition hover:bg-indigo-700"
        >
          Adicionar ao carrinho
        </button>
      </div>
      <button
        type="button"
        className="flex items-center justify-center gap-2 rounded-xl border-2 border-gray-200 py-4 font-bold text-gray-700 transition hover:border-indigo-600 hover:text-indigo-600"
      >
        <i className="fa-solid fa-cube" /> Personalizar em 3D
      </button>
    </div>
  )
}
