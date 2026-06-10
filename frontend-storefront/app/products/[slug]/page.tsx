import { getCategories, getHome, getProduct } from "@/lib/api"
import { resolveTemplate } from "@/lib/templates"

/**
 * Product detail page: fetches the product and renders the active template's
 * Product (`P3-TPL-01`).
 *
 * @param params - Route params carrying the product `slug`.
 * @returns The rendered product page.
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
  const Template = resolveTemplate(home.theme.active_template_id)
  return (
    <Template.Product home={home} categories={categories} product={product} />
  )
}
