import Link from "next/link"

import { formatPrice, type StorefrontProduct } from "@/lib/api"

/**
 * A product card linking to its detail page. The price uses the store's theme
 * accent (`--primary`).
 *
 * @param product - The product to render.
 * @returns The card.
 */
export function ProductCard({
  product,
  locale,
}: {
  product: StorefrontProduct
  locale: string
}) {
  const cover = product.images[0]?.url
  return (
    <Link href={`/products/${product.slug}`} className="group block">
      <div className="aspect-square overflow-hidden rounded-xl bg-gray-100">
        {cover ? (
          <img
            src={cover}
            alt={product.name}
            className="h-full w-full object-cover transition duration-300 group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full items-center justify-center text-sm text-gray-400">
            sem imagem
          </div>
        )}
      </div>
      <div className="mt-3">
        <h3 className="truncate text-sm font-medium text-gray-900">
          {product.name}
        </h3>
        <p
          className="mt-1 text-sm font-semibold"
          style={{ color: "var(--primary)" }}
        >
          {formatPrice(
            product.price_amount_minor,
            product.price_currency,
            locale,
          )}
        </p>
      </div>
    </Link>
  )
}
