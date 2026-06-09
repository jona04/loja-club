import Link from "next/link"

import { ProductCard } from "@/components/ProductCard"
import { StoreShell } from "@/components/StoreShell"
import { getCategories, getHome, listProducts } from "@/lib/api"

/**
 * Category page: the category's published products.
 *
 * @param params - Route params carrying the category `slug`.
 * @returns The category page.
 */
export default async function CategoryPage({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  const [home, categories, products] = await Promise.all([
    getHome(),
    getCategories(),
    listProducts(slug),
  ])
  const category = categories.find((item) => item.slug === slug)
  return (
    <StoreShell store={home.store} theme={home.theme} categories={categories}>
      <nav className="mb-6 text-sm text-gray-400">
        <Link href="/" className="transition hover:text-gray-700">
          Início
        </Link>
        <span className="px-1.5">/</span>
        <span className="text-gray-600">{category?.name ?? "Categoria"}</span>
      </nav>
      <div className="mb-8">
        <h1 className="text-2xl font-bold tracking-tight text-gray-900">
          {category?.name ?? "Categoria"}
        </h1>
        {category?.description ? (
          <p className="mt-1 text-sm text-gray-500">{category.description}</p>
        ) : null}
      </div>
      {products.data.length ? (
        <div className="grid grid-cols-2 gap-x-4 gap-y-8 sm:grid-cols-3 lg:grid-cols-4">
          {products.data.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              locale={home.store.locale}
            />
          ))}
        </div>
      ) : (
        <div className="rounded-2xl border border-dashed border-gray-200 py-16 text-center">
          <p className="text-gray-500">Nenhum produto nesta categoria.</p>
        </div>
      )}
    </StoreShell>
  )
}
