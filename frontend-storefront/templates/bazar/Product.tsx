import Link from "next/link"

import { ProductGallery } from "@/components/ProductGallery"
import { formatPrice } from "@/lib/format"
import type { ProductProps } from "@/lib/template-types"

import { BazarAddToCart } from "./BazarAddToCart"
import { BazarShell } from "./Shell"

/**
 * Bazar product detail (faithful to the template): breadcrumb, gallery in a
 * card, name, bold indigo price, description and the add-to-cart / 3D actions.
 *
 * @param home - Store identity and theme (shell + locale).
 * @param categories - Categories for the nav.
 * @param product - The product to show.
 * @returns The rendered Bazar product page.
 */
export function Product({ home, categories, product }: ProductProps) {
  return (
    <BazarShell
      store={home.store}
      categories={categories}
      locale={home.store.locale}
    >
      <div className="mx-auto max-w-[1400px] px-4 py-8 sm:px-6 lg:px-8">
        <nav className="mb-6 text-sm text-gray-500">
          <Link href="/" className="transition-colors hover:text-indigo-600">
            Início
          </Link>
          <span className="mx-2 text-gray-300">/</span>
          <Link
            href="/products"
            className="transition-colors hover:text-indigo-600"
          >
            Produtos
          </Link>
          <span className="mx-2 text-gray-300">/</span>
          <span className="font-semibold text-gray-900">{product.name}</span>
        </nav>

        <div className="grid gap-8 lg:grid-cols-2 lg:gap-12">
          <div className="rounded-2xl border border-gray-100 bg-white p-4 shadow-soft">
            <ProductGallery images={product.images} alt={product.name} />
          </div>
          <div>
            <h1 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
              {product.name}
            </h1>
            <p className="mt-4 text-3xl font-extrabold text-indigo-600">
              {formatPrice(
                product.price_amount_minor,
                product.price_currency,
                home.store.locale,
              )}
            </p>
            {product.description ? (
              <div className="mt-6 leading-relaxed text-gray-600">
                <p className="whitespace-pre-line">{product.description}</p>
              </div>
            ) : null}
            <div className="mt-8">
              <BazarAddToCart product={product} />
            </div>
          </div>
        </div>
      </div>
    </BazarShell>
  )
}
