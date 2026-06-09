import { ProductCard } from "@/components/ProductCard"
import { StoreShell } from "@/components/StoreShell"
import { getCategories, getHome, listProducts } from "@/lib/api"

/**
 * Full product listing for the host's store.
 *
 * @returns The products page.
 */
export default async function ProductsPage() {
  const [home, categories, products] = await Promise.all([
    getHome(),
    getCategories(),
    listProducts(),
  ])
  return (
    <StoreShell store={home.store} theme={home.theme} categories={categories}>
      <div className="mb-8">
        <h1 className="text-2xl font-bold tracking-tight text-gray-900">
          Produtos
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          {products.count} {products.count === 1 ? "produto" : "produtos"}
        </p>
      </div>
      {products.data.length ? (
        <div className="grid grid-cols-2 gap-x-4 gap-y-8 sm:grid-cols-3 lg:grid-cols-4">
          {products.data.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      ) : (
        <div className="rounded-2xl border border-dashed border-gray-200 py-16 text-center">
          <p className="text-gray-500">Nenhum produto disponível.</p>
        </div>
      )}
    </StoreShell>
  )
}
