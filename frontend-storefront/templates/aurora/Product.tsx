import Link from "next/link"

import { ProductGallery } from "@/components/ProductGallery"
import { formatPrice } from "@/lib/format"
import type { ProductProps } from "@/lib/template-types"

import { AuroraAddToCart } from "./AuroraAddToCart"
import { AuroraShell } from "./Shell"

/**
 * Aurora product detail (faithful to the template): breadcrumb, gallery, name,
 * price, description and the add-to-cart / 3D actions.
 *
 * @param home - Store identity and theme (shell + locale).
 * @param categories - Categories for the nav.
 * @param product - The product to show.
 * @returns The rendered Aurora product page.
 */
export function Product({ home, categories, product }: ProductProps) {
  return (
    <AuroraShell
      store={home.store}
      categories={categories}
      locale={home.store.locale}
    >
      <div className="mx-auto max-w-7xl px-4 pb-24 pt-8 sm:px-6 lg:px-8">
        <nav className="mb-8 text-sm text-gray-500">
          <Link href="/" className="transition-colors hover:text-brand-900">
            Início
          </Link>
          <span className="mx-2 text-gray-300">/</span>
          <Link
            href="/products"
            className="transition-colors hover:text-brand-900"
          >
            Produtos
          </Link>
          <span className="mx-2 text-gray-300">/</span>
          <span className="font-medium text-brand-900">{product.name}</span>
        </nav>

        <div className="lg:grid lg:grid-cols-2 lg:gap-x-12 xl:gap-x-16">
          <div className="mb-10 lg:mb-0">
            <ProductGallery images={product.images} alt={product.name} />
          </div>

          <div className="flex flex-col justify-start">
            <h1 className="mb-2 text-3xl font-light tracking-tight text-brand-900 sm:text-4xl">
              {product.name}
            </h1>
            <p className="mb-6 text-2xl font-medium text-brand-900">
              {formatPrice(
                product.price_amount_minor,
                product.price_currency,
                home.store.locale,
              )}
            </p>
            {product.description ? (
              <div className="mb-8 text-sm leading-relaxed text-gray-500">
                <p className="whitespace-pre-line">{product.description}</p>
              </div>
            ) : null}
            <AuroraAddToCart product={product} />
          </div>
        </div>
      </div>
    </AuroraShell>
  )
}
