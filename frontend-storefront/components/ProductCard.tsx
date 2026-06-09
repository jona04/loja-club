import Link from "next/link"

import { formatPrice, type StorefrontProduct } from "@/lib/api"

/**
 * A product card linking to its detail page.
 *
 * @param product - The product to render.
 * @param big - Larger image/spacing (used by the modern template).
 * @returns The card.
 */
export function ProductCard({
  product,
  big = false,
}: {
  product: StorefrontProduct
  big?: boolean
}) {
  const cover = product.images[0]?.url
  return (
    <Link
      href={`/products/${product.slug}`}
      className="group block overflow-hidden rounded-lg border border-gray-200 bg-white transition hover:shadow-md"
    >
      <div
        className={`flex items-center justify-center overflow-hidden bg-gray-100 ${big ? "aspect-square" : "aspect-[4/3]"}`}
      >
        {cover ? (
          <img
            src={cover}
            alt={product.name}
            className="h-full w-full object-cover transition group-hover:scale-105"
          />
        ) : (
          <span className="text-sm text-gray-400">sem imagem</span>
        )}
      </div>
      <div className="p-3">
        <h3 className="truncate font-medium text-gray-900">{product.name}</h3>
        <p className="mt-1 text-sm text-gray-600">
          {formatPrice(product.price_amount_minor, product.price_currency)}
        </p>
      </div>
    </Link>
  )
}
