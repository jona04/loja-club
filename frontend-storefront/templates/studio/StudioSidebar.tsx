import Link from "next/link"

import type { Category } from "@/lib/api"

/**
 * Studio catalog sidebar (faithful to the template): the category list (with the
 * active one highlighted), a simple price filter and a sort select. The filter
 * and sort are visual placeholders for now (real filtering is a follow-up).
 *
 * @param categories - The store's categories.
 * @param activeSlug - The active category slug (highlighted), if any.
 * @returns The desktop sidebar.
 */
export function StudioSidebar({
  categories,
  activeSlug = null,
}: {
  categories: Category[]
  activeSlug?: string | null
}) {
  return (
    <aside className="hidden w-64 flex-shrink-0 border-r border-gray-200 lg:block">
      <div className="flex flex-col gap-8 p-6">
        <div>
          <h3 className="mb-4 text-xs font-semibold uppercase tracking-wider text-gray-400">
            Categorias
          </h3>
          <ul className="space-y-3 text-sm">
            {categories.map((c) => (
              <li key={c.id}>
                <Link
                  href={`/categories/${c.slug}`}
                  className={`flex items-center justify-between transition-colors hover:text-black ${
                    c.slug === activeSlug
                      ? "font-medium text-black"
                      : "text-gray-600"
                  }`}
                >
                  {c.name}
                </Link>
              </li>
            ))}
            <li className="mt-1 border-t border-gray-100 pt-3">
              <Link
                href="/products"
                className="flex items-center gap-2 font-medium text-gray-900 transition-colors hover:text-black"
              >
                Todas as categorias{" "}
                <i className="fa-solid fa-arrow-right text-[10px]" />
              </Link>
            </li>
          </ul>
        </div>

        <div>
          <h3 className="mb-4 text-xs font-semibold uppercase tracking-wider text-gray-400">
            Filtrar por Preço
          </h3>
          <div className="flex items-center gap-2">
            <input
              type="number"
              placeholder="Min"
              className="h-9 w-full rounded border border-gray-200 bg-gray-50 px-3 text-sm focus:border-black focus:outline-none"
            />
            <span className="text-gray-400">-</span>
            <input
              type="number"
              placeholder="Max"
              className="h-9 w-full rounded border border-gray-200 bg-gray-50 px-3 text-sm focus:border-black focus:outline-none"
            />
          </div>
          <button
            type="button"
            className="mt-3 h-9 w-full rounded bg-gray-100 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-200"
          >
            Aplicar filtro
          </button>
        </div>

        <div>
          <h3 className="mb-4 text-xs font-semibold uppercase tracking-wider text-gray-400">
            Ordenar
          </h3>
          <select className="h-9 w-full cursor-pointer rounded border border-gray-200 bg-gray-50 pl-3 pr-8 text-sm focus:border-black focus:outline-none">
            <option>Mais recentes</option>
            <option>Menor preço</option>
            <option>Maior preço</option>
          </select>
        </div>
      </div>
    </aside>
  )
}
