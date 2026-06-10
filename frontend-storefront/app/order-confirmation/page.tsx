import Link from "next/link"

import { getCategories, getHome } from "@/lib/api"
import { resolveTemplate } from "@/lib/templates"

/**
 * Order confirmation (placeholder): the real order creation is Fase 4. Shown
 * after "Confirmar pedido" in the checkout, inside the active template's shell.
 *
 * @returns The confirmation page.
 */
export default async function OrderConfirmationPage() {
  const [home, categories] = await Promise.all([getHome(), getCategories()])
  const Template = resolveTemplate(home.theme.active_template_id)

  return (
    <Template.Shell
      store={home.store}
      categories={categories}
      locale={home.store.locale}
    >
      <div className="mx-auto flex max-w-lg flex-col items-center px-4 py-24 text-center sm:px-6">
        <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-green-50 text-2xl text-green-600">
          <i className="fa-solid fa-check" />
        </div>
        <h1 className="mb-2 text-3xl font-semibold tracking-tight text-gray-900">
          Pedido recebido!
        </h1>
        <p className="mb-1 text-xs font-medium uppercase tracking-wider text-gray-500">
          Pedido #1042
        </p>
        <p className="mb-8 max-w-md rounded-md border border-gray-200 bg-gray-50 p-4 text-sm leading-relaxed text-gray-700">
          A loja vai entrar em contato para confirmar o pagamento e combinar a
          entrega. Enviamos os detalhes para o seu e-mail/WhatsApp.
        </p>
        <Link
          href="/"
          className="rounded-md bg-gray-900 px-8 py-4 text-sm font-medium text-white transition-colors hover:bg-black"
        >
          Voltar à loja
        </Link>
      </div>
    </Template.Shell>
  )
}
