"use client"

import Link from "next/link"
import { useState } from "react"

import type { StorefrontProduct } from "@/lib/api"
import { useCart } from "@/lib/cart"
import { isCustomizable } from "@/lib/product"

/**
 * Studio product actions (faithful to the template): a quantity stepper, the
 * black "Adicionar ao carrinho" button (adds to the cart + opens the drawer) and
 * the reserved "Personalizar em 3D" placeholder (Fase 5).
 *
 * @param product - The product to add.
 * @returns The quantity + action buttons.
 */
export function StudioAddToCart({ product }: { product: StorefrontProduct }) {
  const cart = useCart()
  const [qty, setQty] = useState(1)

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-3">
        <div className="flex items-center rounded-md border border-gray-200">
          <button
            type="button"
            onClick={() => setQty((q) => Math.max(1, q - 1))}
            className="px-3 py-3 text-gray-500 hover:text-black"
            aria-label="Diminuir"
          >
            -
          </button>
          <span className="w-10 text-center font-medium">{qty}</span>
          <button
            type="button"
            onClick={() => setQty((q) => q + 1)}
            className="px-3 py-3 text-gray-500 hover:text-black"
            aria-label="Aumentar"
          >
            +
          </button>
        </div>
        <button
          type="button"
          disabled={cart.loading}
          onClick={() => cart.add(product.id, qty)}
          className="flex-1 rounded-md bg-black py-3.5 text-sm font-medium text-white transition-colors hover:bg-gray-800 disabled:opacity-60"
        >
          Adicionar ao carrinho
        </button>
      </div>
      {isCustomizable(product) && (
        <Link
          href={`/products/${product.slug}/personalizar`}
          className="flex items-center justify-center gap-2 rounded-md border border-gray-300 py-3.5 text-sm font-medium text-gray-700 transition-colors hover:border-black hover:text-black"
        >
          <i className="fa-solid fa-cube text-gray-400" /> Personalizar em 3D
        </Link>
      )}
    </div>
  )
}
