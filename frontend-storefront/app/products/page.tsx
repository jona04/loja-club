import type { Category } from "@/lib/api"
import { getCategories, getHome, listProducts } from "@/lib/api"
import { resolveTemplate } from "@/lib/templates"

const ALL_PRODUCTS: Category = {
  id: "all",
  name: "Todos os produtos",
  slug: "",
  description: null,
}

/**
 * Full product listing: renders the active template's Category with a synthetic
 * "all products" category (`P3-TPL-01`).
 *
 * @returns The products page.
 */
export default async function ProductsPage() {
  const [home, categories, products] = await Promise.all([
    getHome(),
    getCategories(),
    listProducts(),
  ])
  const Template = resolveTemplate(home.theme.active_template_id)
  return (
    <Template.Category
      home={home}
      categories={categories}
      category={ALL_PRODUCTS}
      products={products}
    />
  )
}
