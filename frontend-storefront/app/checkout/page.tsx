import { getCategories, getHome, getShippingMethods } from "@/lib/api"
import { resolveTemplate } from "@/lib/templates"

/**
 * Checkout page: renders the active template's single-page checkout (server
 * cart) inside its shell, with the store's active shipping methods.
 *
 * @returns The checkout page.
 */
export default async function CheckoutPage() {
  const [home, categories, methods] = await Promise.all([
    getHome(),
    getCategories(),
    getShippingMethods(),
  ])
  const Template = resolveTemplate(home.theme.active_template_id)
  return (
    <Template.Shell
      store={home.store}
      categories={categories}
      locale={home.store.locale}
    >
      <Template.Checkout
        store={home.store}
        methods={methods}
        locale={home.store.locale}
      />
    </Template.Shell>
  )
}
