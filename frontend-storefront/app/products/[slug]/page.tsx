import { StoreShell } from "@/components/StoreShell"
import {
  formatPrice,
  getCategories,
  getHome,
  getProduct,
  whatsappLink,
} from "@/lib/api"

/**
 * Product detail page (image-only V1). Buying happens via WhatsApp until the
 * cart/checkout arrive in Fase 4.
 *
 * @param params - Route params carrying the product `slug`.
 * @returns The product page.
 */
export default async function ProductPage({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  const [home, categories, product] = await Promise.all([
    getHome(),
    getCategories(),
    getProduct(slug),
  ])
  const cover = product.images[0]
  return (
    <StoreShell store={home.store} theme={home.theme} categories={categories}>
      <div className="grid gap-8 md:grid-cols-2">
        <div className="flex aspect-square items-center justify-center overflow-hidden rounded-lg bg-gray-100">
          {cover ? (
            <img
              src={cover.url}
              alt={product.name}
              className="h-full w-full object-cover"
            />
          ) : (
            <span className="text-gray-400">sem imagem</span>
          )}
        </div>
        <div>
          <h1 className="text-2xl font-semibold">{product.name}</h1>
          <p className="mt-2 text-xl text-gray-800">
            {formatPrice(product.price_amount_minor, product.price_currency)}
          </p>
          {product.description ? (
            <p className="mt-4 whitespace-pre-line text-gray-600">
              {product.description}
            </p>
          ) : null}
          {home.store.whatsapp_number ? (
            <a
              href={whatsappLink(home.store.whatsapp_number)}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-6 inline-block rounded-lg bg-green-500 px-6 py-3 font-semibold text-white transition hover:bg-green-600"
            >
              Comprar pelo WhatsApp
            </a>
          ) : null}
          {product.images.length > 1 ? (
            <div className="mt-6 flex flex-wrap gap-2">
              {product.images.slice(1).map((image) => (
                <img
                  key={image.url}
                  src={image.url}
                  alt=""
                  className="h-16 w-16 rounded object-cover"
                />
              ))}
            </div>
          ) : null}
        </div>
      </div>
    </StoreShell>
  )
}
