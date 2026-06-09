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
      <h1 className="mb-6 text-2xl font-semibold">Produtos</h1>
      {products.data.length ? (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          {products.data.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      ) : (
        <p className="text-gray-500">Nenhum produto disponível.</p>
      )}
    </StoreShell>
  )
}
