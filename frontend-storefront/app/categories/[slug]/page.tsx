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
  const category = categories.find((c) => c.slug === slug)
  return (
    <StoreShell store={home.store} theme={home.theme} categories={categories}>
      <h1 className="mb-6 text-2xl font-semibold">
        {category?.name ?? "Categoria"}
      </h1>
      {products.data.length ? (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          {products.data.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      ) : (
        <p className="text-gray-500">Nenhum produto nesta categoria.</p>
      )}
    </StoreShell>
  )
}
