import Link from "next/link"

import { getCategories, getHome } from "@/lib/api"
import { AuroraShell } from "@/templates/aurora/Shell"

/**
 * Customer account (placeholder): the real customer area + login is Fase 6.
 *
 * @returns The account placeholder page.
 */
export default async function ContaPage() {
  const [home, categories] = await Promise.all([getHome(), getCategories()])

  return (
    <AuroraShell
      store={home.store}
      categories={categories}
      locale={home.store.locale}
    >
      <div className="mx-auto flex max-w-md flex-col items-center px-4 py-24 text-center sm:px-6">
        <i className="fa-regular fa-user mb-6 text-4xl text-gray-300" />
        <h1 className="mb-3 text-2xl font-light tracking-tight text-brand-900">
          Minha conta
        </h1>
        <p className="mb-8 text-sm text-gray-500">
          Em breve você poderá acompanhar seus pedidos e endereços por aqui. A
          compra continua sem precisar criar conta.
        </p>
        <Link
          href="/products"
          className="rounded-sm bg-brand-900 px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-black"
        >
          Continuar comprando
        </Link>
      </div>
    </AuroraShell>
  )
}
