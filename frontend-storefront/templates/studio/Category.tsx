import Link from "next/link"

import type { CategoryProps } from "@/lib/template-types"
import { StudioShell } from "./Shell"
import { StudioProductCard } from "./StudioProductCard"
import { StudioSidebar } from "./StudioSidebar"

/**
 * Studio category listing (faithful to the template): the catalog sidebar (with
 * the active category highlighted), a results bar and a dense grid.
 *
 * @param home - Store identity and theme.
 * @param categories - Categories for the sidebar.
 * @param category - The active category (or null).
 * @param products - The category's published products.
 * @returns The rendered Studio category page.
 */
export function Category({
  home,
  categories,
  category,
  products,
}: CategoryProps) {
  return (
    <StudioShell
      store={home.store}
      categories={categories}
      locale={home.store.locale}
    >
      <div className="mx-auto flex w-full max-w-[1600px] flex-1">
        <StudioSidebar
          categories={categories}
          activeSlug={category?.slug ?? null}
        />
        <main className="flex min-w-0 flex-1 flex-col pb-16">
          <div className="border-b border-gray-100 px-4 py-5 lg:px-6">
            <nav className="mb-1 text-xs text-gray-400">
              <Link href="/" className="hover:text-black">
                Início
              </Link>{" "}
              / {category?.name ?? "Categoria"}
            </nav>
            <div className="flex items-center justify-between">
              <h1 className="text-lg font-bold text-gray-900">
                {category?.name ?? "Categoria"}
              </h1>
              <span className="text-sm text-gray-500">
                {products.count} {products.count === 1 ? "produto" : "produtos"}
              </span>
            </div>
            {category?.description ? (
              <p className="mt-1 max-w-2xl text-sm text-gray-500">
                {category.description}
              </p>
            ) : null}
          </div>
          {products.data.length ? (
            <div className="grid grid-cols-2 gap-4 p-4 md:grid-cols-3 md:gap-6 lg:p-6 xl:grid-cols-4">
              {products.data.map((product, i) => (
                <StudioProductCard
                  key={product.id}
                  product={product}
                  locale={home.store.locale}
                  badge={i === 0}
                />
              ))}
            </div>
          ) : (
            <div className="p-6">
              <p className="text-gray-500">Nenhum produto nesta categoria.</p>
            </div>
          )}
        </main>
      </div>
    </StudioShell>
  )
}
