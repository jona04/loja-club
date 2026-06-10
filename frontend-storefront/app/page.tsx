import { getCategories, getHome } from "@/lib/api"
import { resolveTemplate } from "@/lib/templates"

/**
 * Storefront home: fetches the host store's data and renders the **active
 * template's** Home (`P3-TPL-01`). Unknown templates fall back to base.
 *
 * @returns The rendered home for the host's store.
 */
export default async function HomePage() {
  const [home, categories] = await Promise.all([getHome(), getCategories()])
  const Template = resolveTemplate(home.theme.active_template_id)
  return <Template.Home home={home} categories={categories} />
}
