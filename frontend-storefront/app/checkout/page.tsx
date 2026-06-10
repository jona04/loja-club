import { getCategories, getHome } from "@/lib/api"
import { CheckoutView } from "@/templates/aurora/CheckoutView"
import { AuroraShell } from "@/templates/aurora/Shell"

/**
 * Checkout page: renders the Aurora single-page checkout (client cart) inside
 * the template shell. The real order is Fase 4.
 *
 * @returns The checkout page.
 */
export default async function CheckoutPage() {
  const [home, categories] = await Promise.all([getHome(), getCategories()])
  return (
    <AuroraShell
      store={home.store}
      categories={categories}
      locale={home.store.locale}
    >
      <CheckoutView locale={home.store.locale} />
    </AuroraShell>
  )
}
