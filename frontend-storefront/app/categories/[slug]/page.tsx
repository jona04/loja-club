import { getCategories, getHome, listProducts } from "@/lib/api"
import { resolveTemplate } from "@/lib/templates"

/**
 * Category page: fetches the category's products and renders the active
 * template's Category (`P3-TPL-01`).
 *
 * @param params - Route params carrying the category `slug`.
 * @returns The rendered category page.
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
  const category = categories.find((item) => item.slug === slug) ?? null
  const Template = resolveTemplate(home.theme.active_template_id)
  return (
    <Template.Category
      home={home}
      categories={categories}
      category={category}
      products={products}
    />
  )
}
