import Link from "next/link"

import type { StorefrontProduct } from "@/lib/api"
import { formatPrice } from "@/lib/format"

/**
 * Bazar product card (faithful to the template): rounded card with a soft/float
 * shadow lift, an optional "Novo" badge, a hover heart and the bold price. The
 * whole card links to the product (the add-to-cart lives on the product page).
 *
 * @param product - The product to show.
 * @param locale - Store locale for price formatting.
 * @param badge - Whether to show the "Novo" badge.
 * @returns The product card.
 */
export function BazarProductCard({
  product,
  locale,
  badge = false,
}: {
  product: StorefrontProduct
  locale: string
  badge?: boolean
}) {
  const image = product.images[0]?.url ?? null

  return (
    <Link
      href={`/products/${product.slug}`}
      className="group flex flex-col overflow-hidden rounded-2xl border border-gray-100 bg-white shadow-soft transition-all duration-300 hover:-translate-y-1 hover:shadow-float"
    >
      <div className="relative aspect-square w-full bg-gray-50 p-4">
        {badge ? (
          <span className="absolute left-3 top-3 z-10 rounded-md bg-indigo-600 px-2 py-1 text-[10px] font-bold text-white sm:text-xs">
            Novo
          </span>
        ) : null}
        <span className="absolute right-3 top-3 z-10 flex h-8 w-8 translate-y-2 items-center justify-center rounded-full bg-white text-gray-400 opacity-0 shadow-sm transition group-hover:translate-y-0 group-hover:text-rose-500 group-hover:opacity-100">
          <i className="fa-regular fa-heart" />
        </span>
        {image ? (
          <img
            src={image}
            alt={product.name}
            className="h-full w-full object-contain mix-blend-multiply transition-transform duration-500 group-hover:scale-105"
          />
        ) : null}
      </div>
      <div className="flex flex-1 flex-col p-4">
        <h3 className="mb-2 line-clamp-2 text-sm font-bold leading-tight text-gray-900 transition-colors group-hover:text-indigo-600 sm:text-base">
          {product.name}
        </h3>
        <div className="mt-auto text-lg font-extrabold text-gray-900 sm:text-xl">
          {formatPrice(
            product.price_amount_minor,
            product.price_currency,
            locale,
          )}
        </div>
      </div>
    </Link>
  )
}
