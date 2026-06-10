import Link from "next/link"

import { ProductGallery } from "@/components/ProductGallery"
import { formatPrice } from "@/lib/format"
import type { ProductProps } from "@/lib/template-types"
import { StudioShell } from "./Shell"
import { StudioAddToCart } from "./StudioAddToCart"

/**
 * Studio product detail (faithful to the template): a clean full-width layout —
 * breadcrumb, gallery, name, bold price, description and the actions.
 *
 * @param home - Store identity and theme (shell + locale).
 * @param categories - Categories (for the shell).
 * @param product - The product to show.
 * @returns The rendered Studio product page.
 */
export function Product({ home, categories, product }: ProductProps) {
  return (
    <StudioShell
      store={home.store}
      categories={categories}
      locale={home.store.locale}
    >
      <div className="mx-auto w-full max-w-5xl px-4 py-8 lg:px-8">
        <nav className="mb-6 text-sm text-gray-500">
          <Link href="/" className="hover:text-black">
            Início
          </Link>
          <span className="mx-2 text-gray-300">/</span>
          <Link href="/products" className="hover:text-black">
            Produtos
          </Link>
          <span className="mx-2 text-gray-300">/</span>
          <span className="font-medium text-gray-900">{product.name}</span>
        </nav>

        <div className="grid gap-8 lg:grid-cols-2 lg:gap-12">
          <div className="rounded-md bg-gray-50 p-4">
            <ProductGallery images={product.images} alt={product.name} />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl">
              {product.name}
            </h1>
            <p className="mt-4 text-2xl font-bold text-black">
              {formatPrice(
                product.price_amount_minor,
                product.price_currency,
                home.store.locale,
              )}
            </p>
            {product.description ? (
              <div className="mt-6 text-sm leading-relaxed text-gray-600">
                <p className="whitespace-pre-line">{product.description}</p>
              </div>
            ) : null}
            <div className="mt-8">
              <StudioAddToCart product={product} />
            </div>
          </div>
        </div>
      </div>
    </StudioShell>
  )
}
