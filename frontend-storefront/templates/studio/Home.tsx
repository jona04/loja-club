import type { HomeProps } from "@/lib/template-types"
import { StudioShell } from "./Shell"
import { StudioProductCard } from "./StudioProductCard"
import { StudioSidebar } from "./StudioSidebar"

/**
 * Studio home (faithful to the template): a clean catalog — the category/filter
 * sidebar, a slim banner, the results bar and a dense product grid.
 *
 * @param home - Store identity, theme and highlights.
 * @param categories - Categories for the sidebar.
 * @returns The rendered Studio home.
 */
export function Home({ home, categories }: HomeProps) {
  const { store, theme, featured_products: featured } = home
  const settings = theme.settings ?? {}
  const catalogIntro =
    (settings.catalog_intro as string) ||
    store.description ||
    "Peças utilitárias desenhadas para o conforto do dia a dia."
  const showFilters = settings.show_filters !== false

  return (
    <StudioShell store={store} categories={categories} locale={store.locale}>
      <div className="mx-auto flex w-full max-w-[1600px] flex-1">
        <StudioSidebar categories={categories} showFilters={showFilters} />
        <main className="flex min-w-0 flex-1 flex-col pb-16">
          <div className="w-full p-4 pb-0 lg:p-6">
            <div className="relative h-32 w-full overflow-hidden rounded-lg bg-gray-100 md:h-48">
              {theme.banner_image_url ? (
                <img
                  src={theme.banner_image_url}
                  alt=""
                  className="h-full w-full object-cover"
                />
              ) : null}
              <div className="absolute inset-0 flex items-center bg-black/10 p-8 md:p-12">
                <div className="max-w-md">
                  <span className="mb-2 block text-xs font-bold uppercase tracking-widest text-black">
                    Nova Coleção
                  </span>
                  <h2 className="mb-2 text-2xl font-bold text-gray-900 md:text-3xl">
                    {theme.headline || "Catálogo Completo"}
                  </h2>
                  <p className="hidden text-sm text-gray-700 md:block">
                    {catalogIntro}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-2 flex items-center justify-between border-b border-gray-100 px-4 py-5 lg:px-6">
            <h1 className="text-lg font-bold text-gray-900">Catálogo</h1>
            <span className="text-sm text-gray-500">
              {featured.length} {featured.length === 1 ? "produto" : "produtos"}
            </span>
          </div>

          {featured.length ? (
            <div className="grid grid-cols-2 gap-4 p-4 md:grid-cols-3 md:gap-6 lg:p-6 xl:grid-cols-4">
              {featured.map((product, i) => (
                <StudioProductCard
                  key={product.id}
                  product={product}
                  locale={store.locale}
                  badge={i === 0}
                />
              ))}
            </div>
          ) : (
            <div className="p-6">
              <p className="text-gray-500">Novidades em breve por aqui.</p>
            </div>
          )}
        </main>
      </div>
    </StudioShell>
  )
}
