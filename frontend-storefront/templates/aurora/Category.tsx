import Link from "next/link"

import type { CategoryProps } from "@/lib/template-types"

import { AuroraProductCard } from "./AuroraProductCard"
import { AuroraShell } from "./Shell"

/**
 * Aurora category listing (faithful to the template): breadcrumb, an editorial
 * title with the category description and product count, and the grid.
 *
 * @param home - Store identity and theme.
 * @param categories - Categories for the nav.
 * @param category - The active category (or null).
 * @param products - The category's published products.
 * @returns The rendered Aurora category page.
 */
export function Category({
  home,
  categories,
  category,
  products,
}: CategoryProps) {
  return (
    <AuroraShell
      store={home.store}
      categories={categories}
      locale={home.store.locale}
    >
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8 lg:py-16">
        <nav className="mb-6 text-sm text-gray-500">
          <Link href="/" className="transition-colors hover:text-brand-900">
            Início
          </Link>
          <span className="mx-2 text-gray-300">/</span>
          <span className="font-medium text-brand-900">
            {category?.name ?? "Categoria"}
          </span>
        </nav>
        <div className="mb-10 border-b border-gray-100 pb-6">
          <h1 className="text-3xl font-light tracking-tight text-brand-900">
            {category?.name ?? "Categoria"}
          </h1>
          <p className="mt-2 max-w-xl text-sm text-gray-500">
            {category?.description ||
              "Uma seleção de peças escolhidas a dedo para esta coleção."}
          </p>
          <p className="mt-3 text-sm text-gray-400">
            {products.count} {products.count === 1 ? "produto" : "produtos"}
          </p>
        </div>
        {products.data.length ? (
          <div className="grid grid-cols-2 gap-x-6 gap-y-12 sm:gap-y-16 lg:grid-cols-4">
            {products.data.map((product, i) => (
              <AuroraProductCard
                key={product.id}
                product={product}
                locale={home.store.locale}
                badge={i === 0}
              />
            ))}
          </div>
        ) : (
          <div className="rounded-sm border border-dashed border-gray-200 py-16 text-center">
            <p className="text-gray-500">Nenhum produto nesta categoria.</p>
          </div>
        )}
      </div>
    </AuroraShell>
  )
}
