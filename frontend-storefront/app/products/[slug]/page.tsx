import Link from "next/link"

import { ProductGallery } from "@/components/ProductGallery"
import { StoreShell } from "@/components/StoreShell"
import { formatPrice, getCategories, getHome, getProduct } from "@/lib/api"

/**
 * Product detail page (image-only V1): gallery, name, price and description.
 * Purchasing arrives with the cart in Fase 4; the only WhatsApp element is the
 * store-wide floating button (see StoreShell).
 *
 * @param params - Route params carrying the product `slug`.
 * @returns The product page.
 */
export default async function ProductPage({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  const [home, categories, product] = await Promise.all([
    getHome(),
    getCategories(),
    getProduct(slug),
  ])
  return (
    <StoreShell store={home.store} theme={home.theme} categories={categories}>
      <nav className="mb-6 text-sm text-gray-400">
        <Link href="/" className="transition hover:text-gray-700">
          Início
        </Link>
        <span className="px-1.5">/</span>
        <Link href="/products" className="transition hover:text-gray-700">
          Produtos
        </Link>
        <span className="px-1.5">/</span>
        <span className="text-gray-600">{product.name}</span>
      </nav>
      <div className="grid gap-8 lg:grid-cols-2 lg:gap-12">
        <ProductGallery images={product.images} alt={product.name} />
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-gray-900 sm:text-3xl">
            {product.name}
          </h1>
          <p
            className="mt-4 text-3xl font-semibold"
            style={{ color: "var(--primary)" }}
          >
            {formatPrice(product.price_amount_minor, product.price_currency)}
          </p>
          {product.description ? (
            <div className="mt-6 border-t border-gray-100 pt-6">
              <h2 className="text-sm font-medium text-gray-900">Descrição</h2>
              <p className="mt-2 text-sm leading-relaxed whitespace-pre-line text-gray-600">
                {product.description}
              </p>
            </div>
          ) : null}
        </div>
      </div>
    </StoreShell>
  )
}
