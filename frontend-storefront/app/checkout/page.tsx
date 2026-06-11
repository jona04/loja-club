import { getCategories, getHome } from "@/lib/api"
import { resolveTemplate } from "@/lib/templates"
import { CheckoutView } from "@/templates/aurora/CheckoutView"

/**
 * Checkout page: renders the single-page checkout (client cart) inside the
 * active template's shell. The real order is Fase 4.
 *
 * @returns The checkout page.
 */
export default async function CheckoutPage() {
  const [home, categories] = await Promise.all([getHome(), getCategories()])
  const Template = resolveTemplate(home.theme.active_template_id)
  return (
    <Template.Shell
      store={home.store}
      categories={categories}
      locale={home.store.locale}
    >
      <CheckoutView locale={home.store.locale} />
    </Template.Shell>
  )
}
