import Link from "next/link"

import type { StorefrontProduct } from "@/lib/api"
import { formatPrice } from "@/lib/format"

/**
 * Studio product card (faithful to the template): a 4:5 contained image with an
 * optional "Novo" badge, an underline-on-hover name and the bold price.
 *
 * @param product - The product to show.
 * @param locale - Store locale for price formatting.
 * @param badge - Whether to show the "Novo" badge.
 * @returns The product card.
 */
export function StudioProductCard({
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
    <Link href={`/products/${product.slug}`} className="group block">
      <div className="relative mb-3 aspect-[4/5] overflow-hidden rounded-md bg-gray-50">
        {image ? (
          <img
            src={image}
            alt={product.name}
            className="h-full w-full object-contain mix-blend-multiply p-4 transition-transform duration-500 group-hover:scale-105"
          />
        ) : null}
        {badge ? (
          <span className="absolute left-2 top-2 rounded-sm border border-gray-200 bg-white px-2 py-1 text-[10px] font-bold uppercase tracking-wider text-gray-900">
            Novo
          </span>
        ) : null}
      </div>
      <div className="flex flex-col">
        <h3 className="line-clamp-1 text-sm font-medium text-gray-900 decoration-1 underline-offset-2 group-hover:underline">
          {product.name}
        </h3>
        <div className="mt-1 text-sm font-bold text-black">
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
