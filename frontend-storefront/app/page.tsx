import Link from "next/link"

import { ProductCard } from "@/components/ProductCard"
import { StoreShell } from "@/components/StoreShell"
import { getCategories, getHome } from "@/lib/api"

/**
 * Storefront home. The active template drives the hero: `modern` shows a banner
 * with an overlay headline; `classic` shows a clean centered headline.
 *
 * @returns The rendered home page for the host's store.
 */
export default async function HomePage() {
  const [home, categories] = await Promise.all([getHome(), getCategories()])
  const { store, theme, featured_products: featured } = home
  const isModern = theme.active_template_id === "modern"
  const name = store.public_name || store.name

  return (
    <StoreShell store={store} theme={theme} categories={categories}>
      {isModern && theme.banner_image_url ? (
        <section className="relative mb-12 overflow-hidden rounded-2xl">
          <img
            src={theme.banner_image_url}
            alt=""
            className="h-72 w-full object-cover sm:h-96"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />
          <div className="absolute inset-x-0 bottom-0 p-6 sm:p-10">
            <h1 className="max-w-2xl text-3xl font-bold tracking-tight text-white sm:text-4xl">
              {theme.headline || name}
            </h1>
            <Link
              href="/products"
              className="mt-5 inline-flex rounded-full bg-white px-5 py-2.5 text-sm font-semibold text-gray-900 shadow-sm transition hover:bg-gray-100"
            >
              Ver produtos
            </Link>
          </div>
        </section>
      ) : (
        <section className="mb-12 py-6 text-center sm:py-10">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
            {theme.headline || name}
          </h1>
          {store.description ? (
            <p className="mx-auto mt-3 max-w-xl text-gray-500">
              {store.description}
            </p>
          ) : null}
        </section>
      )}

      {categories.length ? (
        <div className="mb-12 flex flex-wrap justify-center gap-2">
          {categories.map((category) => (
            <Link
              key={category.id}
              href={`/categories/${category.slug}`}
              className="rounded-full border border-gray-200 px-4 py-1.5 text-sm font-medium text-gray-700 transition hover:border-gray-900 hover:text-gray-900"
            >
              {category.name}
            </Link>
          ))}
        </div>
      ) : null}

      <section>
        <div className="mb-6 flex items-end justify-between">
          <h2 className="text-xl font-semibold tracking-tight text-gray-900">
            Destaques
          </h2>
          {featured.length ? (
            <Link
              href="/products"
              className="text-sm font-medium text-gray-500 transition hover:text-gray-900"
            >
              Ver tudo →
            </Link>
          ) : null}
        </div>
        {featured.length ? (
          <div className="grid grid-cols-2 gap-x-4 gap-y-8 sm:grid-cols-3 lg:grid-cols-4">
            {featured.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                locale={store.locale}
              />
            ))}
          </div>
        ) : (
          <div className="rounded-2xl border border-dashed border-gray-200 py-16 text-center">
            <p className="text-gray-500">Novidades em breve por aqui.</p>
          </div>
        )}
      </section>
    </StoreShell>
  )
}
