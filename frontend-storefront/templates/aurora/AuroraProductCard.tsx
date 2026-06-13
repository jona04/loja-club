"use client"

import Link from "next/link"
import type { StorefrontProduct } from "@/lib/api"
import { useCart } from "@/lib/cart"
import { formatPrice } from "@/lib/format"

/**
 * Aurora product card (faithful to the template): square image with a "Novo"
 * badge and a hover "Adicionar" overlay that adds the product to the cart.
 *
 * @param product - The product to show.
 * @param locale - Store locale for price formatting.
 * @param badge - Whether to show the "Novo" badge.
 * @returns The product card.
 */
export function AuroraProductCard({
  product,
  locale,
  badge = false,
}: {
  product: StorefrontProduct
  locale: string
  badge?: boolean
}) {
  const cart = useCart()
  const image = product.images[0]?.url ?? null
  const subtitle = product.description?.split("\n")[0]?.slice(0, 40) ?? null

  return (
    <div className="group relative">
      <div className="relative mb-4 aspect-square w-full overflow-hidden rounded-sm bg-gray-100">
        {image ? (
          <img
            src={image}
            alt={product.name}
            className="h-full w-full object-cover object-center transition-transform duration-700 group-hover:scale-105"
          />
        ) : null}
        {badge ? (
          <div className="absolute left-3 top-3 rounded-sm bg-white px-2 py-1 text-[10px] font-bold uppercase tracking-wider text-brand-900">
            Novo
          </div>
        ) : null}
        <div className="absolute inset-x-0 bottom-0 hidden translate-y-4 p-4 opacity-0 transition-all duration-300 group-hover:translate-y-0 group-hover:opacity-100 md:block">
          <button
            type="button"
            disabled={cart.loading}
            onClick={() => cart.add(product.id)}
            className="w-full rounded-sm bg-white/95 py-3 text-sm font-medium text-brand-900 shadow-sm backdrop-blur-sm transition-colors hover:bg-brand-900 hover:text-white disabled:opacity-60"
          >
            Adicionar
          </button>
        </div>
      </div>
      <h3 className="mb-1 text-sm font-medium leading-tight text-brand-900">
        <Link href={`/products/${product.slug}`}>
          <span aria-hidden="true" className="absolute inset-0 md:hidden" />
          {product.name}
        </Link>
      </h3>
      {subtitle ? (
        <p className="mb-2 text-sm text-gray-500">{subtitle}</p>
      ) : null}
      <p className="text-sm font-medium text-brand-900">
        {formatPrice(
          product.price_amount_minor,
          product.price_currency,
          locale,
        )}
      </p>
    </div>
  )
}
