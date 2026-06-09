import { ProductCard } from "@/components/ProductCard"
import { StoreShell } from "@/components/StoreShell"
import { getCategories, getHome } from "@/lib/api"

/**
 * Storefront home. The active template drives the layout: `modern` shows a hero
 * banner and larger cards; `classic` is a simple headline + grid.
 *
 * @returns The rendered home page for the host's store.
 */
export default async function HomePage() {
  const [home, categories] = await Promise.all([getHome(), getCategories()])
  const { store, theme, featured_products: featured } = home
  const isModern = theme.active_template_id === "modern"

  return (
    <StoreShell store={store} theme={theme} categories={categories}>
      {isModern && theme.banner_image_url ? (
        <section className="relative mb-8 overflow-hidden rounded-xl">
          <img
            src={theme.banner_image_url}
            alt=""
            className="h-64 w-full object-cover"
          />
          {theme.headline ? (
            <div className="absolute inset-0 flex items-center bg-black/30 p-8">
              <h1 className="text-3xl font-bold text-white">
                {theme.headline}
              </h1>
            </div>
          ) : null}
        </section>
      ) : (
        <h1 className="mb-6 text-2xl font-semibold">
          {theme.headline || store.public_name || store.name}
        </h1>
      )}

      <h2 className="mb-4 text-lg font-medium">Destaques</h2>
      {featured.length ? (
        <div
          className={`grid gap-4 ${isModern ? "grid-cols-2 md:grid-cols-3" : "grid-cols-2 md:grid-cols-4"}`}
        >
          {featured.map((product) => (
            <ProductCard key={product.id} product={product} big={isModern} />
          ))}
        </div>
      ) : (
        <p className="text-gray-500">Em breve.</p>
      )}
    </StoreShell>
  )
}
