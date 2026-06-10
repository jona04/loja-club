import Link from "next/link"

import type { CategoryProps } from "@/lib/template-types"

import { BazarProductCard } from "./BazarProductCard"
import { BazarShell } from "./Shell"

/**
 * Bazar category listing (faithful to the template): breadcrumb, a bold title
 * with the product count and a dense grid.
 *
 * @param home - Store identity and theme.
 * @param categories - Categories for the nav.
 * @param category - The active category (or null).
 * @param products - The category's published products.
 * @returns The rendered Bazar category page.
 */
export function Category({
  home,
  categories,
  category,
  products,
}: CategoryProps) {
  return (
    <BazarShell
      store={home.store}
      categories={categories}
      locale={home.store.locale}
    >
      <div className="mx-auto max-w-[1400px] px-4 py-10 sm:px-6 lg:px-8">
        <nav className="mb-6 text-sm text-gray-500">
          <Link href="/" className="transition-colors hover:text-indigo-600">
            Início
          </Link>
          <span className="mx-2 text-gray-300">/</span>
          <span className="font-semibold text-gray-900">
            {category?.name ?? "Categoria"}
          </span>
        </nav>
        <div className="mb-8">
          <h1 className="text-3xl font-extrabold text-gray-900">
            {category?.name ?? "Categoria"}
          </h1>
          {category?.description ? (
            <p className="mt-2 max-w-2xl text-gray-500">
              {category.description}
            </p>
          ) : null}
          <p className="mt-3 text-sm font-medium text-gray-400">
            {products.count} {products.count === 1 ? "produto" : "produtos"}
          </p>
        </div>
        {products.data.length ? (
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4 lg:grid-cols-5 lg:gap-6">
            {products.data.map((product, i) => (
              <BazarProductCard
                key={product.id}
                product={product}
                locale={home.store.locale}
                badge={i === 0}
              />
            ))}
          </div>
        ) : (
          <div className="rounded-2xl border border-dashed border-gray-200 bg-white py-16 text-center">
            <p className="text-gray-500">Nenhum produto nesta categoria.</p>
          </div>
        )}
      </div>
    </BazarShell>
  )
}
