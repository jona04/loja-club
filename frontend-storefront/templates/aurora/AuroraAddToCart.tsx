"use client"

import Link from "next/link"
import { useState } from "react"

import type { StorefrontProduct } from "@/lib/api"
import { useCart } from "@/lib/cart"
import { isCustomizable } from "@/lib/product"

/**
 * Aurora product actions (faithful to the template): a quantity stepper, the
 * "Adicionar ao carrinho" button (adds to the cart + opens the drawer) and the
 * reserved "Personalizar em 3D" placeholder (Fase 5).
 *
 * @param product - The product to add.
 * @returns The quantity + action buttons.
 */
export function AuroraAddToCart({ product }: { product: StorefrontProduct }) {
  const cart = useCart()
  const [qty, setQty] = useState(1)

  return (
    <>
      <div className="mb-6">
        <span className="mb-2 block text-sm font-medium text-gray-700">
          Quantidade
        </span>
        <div className="flex w-max items-center rounded-sm border border-gray-200">
          <button
            type="button"
            onClick={() => setQty((q) => Math.max(1, q - 1))}
            className="px-4 py-2 text-gray-500 transition-colors hover:text-brand-900"
            aria-label="Diminuir"
          >
            -
          </button>
          <span className="w-12 text-center font-medium text-brand-900">
            {qty}
          </span>
          <button
            type="button"
            onClick={() => setQty((q) => q + 1)}
            className="px-4 py-2 text-gray-500 transition-colors hover:text-brand-900"
            aria-label="Aumentar"
          >
            +
          </button>
        </div>
      </div>

      <div className="mt-4 flex flex-col gap-4">
        <button
          type="button"
          disabled={cart.loading}
          onClick={() => cart.add(product.id, qty)}
          className="w-full rounded-sm bg-brand-900 py-4 text-base font-medium text-white shadow-sm transition-colors hover:bg-black disabled:opacity-60"
        >
          Adicionar ao carrinho
        </button>
        {isCustomizable(product) && (
          <Link
            href={`/products/${product.slug}/personalizar`}
            className="flex w-full items-center justify-center gap-2 rounded-sm border border-gray-200 bg-white py-4 text-sm font-medium text-brand-900 transition-colors hover:bg-gray-50"
          >
            <i className="fa-solid fa-cube text-gray-400" /> Personalizar em 3D
          </Link>
        )}
      </div>
    </>
  )
}
