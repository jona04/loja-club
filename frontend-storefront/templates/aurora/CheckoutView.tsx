"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { useCart } from "@/lib/cart"
import { formatPrice } from "@/lib/format"

const DELIVERY = [
  "Frete fixo",
  "Frete grátis acima de R$ 500",
  "Retirada local",
  "Entrega combinada (a loja entrará em contato)",
]

/**
 * Aurora single-page checkout (placeholder flow): reviews the client cart,
 * collects contact/delivery (lorem inputs, no backend yet) and "Confirmar
 * pedido" clears the cart and goes to the confirmation. The real order is Fase 4.
 *
 * @param locale - Store locale for price formatting.
 * @returns The checkout view.
 */
export function CheckoutView({ locale }: { locale: string }) {
  const cart = useCart()
  const router = useRouter()

  if (!cart.items.length) {
    return (
      <div className="mx-auto flex max-w-md flex-col items-center px-4 py-24 text-center">
        <p className="mb-8 text-sm text-gray-500">Seu carrinho está vazio.</p>
        <Link
          href="/products"
          className="rounded-sm bg-brand-900 px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-black"
        >
          Ver produtos
        </Link>
      </div>
    )
  }

  const currency = cart.items[0].priceCurrency
  const confirm = () => {
    cart.clear()
    router.push("/order-confirmation")
  }
  const field =
    "w-full rounded-sm border border-gray-200 px-3 py-2.5 text-sm focus:border-brand-900 focus:outline-none"

  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <h1 className="mb-10 text-3xl font-light tracking-tight text-brand-900">
        Finalizar compra
      </h1>
      <div className="grid grid-cols-1 gap-12 lg:grid-cols-3">
        <div className="space-y-10 lg:col-span-2">
          <section>
            <h2 className="mb-4 text-lg font-medium text-brand-900">
              Seu pedido
            </h2>
            <div className="divide-y divide-gray-100 border-y border-gray-100">
              {cart.items.map((item) => (
                <div key={item.id} className="flex gap-4 py-4">
                  <div className="h-20 w-16 flex-shrink-0 overflow-hidden rounded-sm bg-gray-50">
                    {item.image ? (
                      <img
                        src={item.image}
                        alt={item.name}
                        className="h-full w-full object-cover"
                      />
                    ) : null}
                  </div>
                  <div className="flex flex-1 items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-brand-900">
                        {item.name}
                      </p>
                      <p className="text-xs text-gray-500">Qtd: {item.qty}</p>
                    </div>
                    <p className="text-sm font-medium text-brand-900">
                      {formatPrice(
                        item.priceAmountMinor * item.qty,
                        item.priceCurrency,
                        locale,
                      )}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section>
            <h2 className="mb-4 text-lg font-medium text-brand-900">Contato</h2>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <input className={field} placeholder="Nome completo" />
              <input className={field} placeholder="E-mail" />
              <div className="flex gap-2 sm:col-span-2">
                <select className={`${field} w-28`} defaultValue="BR">
                  <option value="BR">🇧🇷 +55</option>
                  <option value="US">🇺🇸 +1</option>
                  <option value="PT">🇵🇹 +351</option>
                </select>
                <input className={field} placeholder="Telefone" />
              </div>
            </div>
          </section>

          <section>
            <h2 className="mb-4 text-lg font-medium text-brand-900">Entrega</h2>
            <input
              className={`${field} mb-4`}
              placeholder="Endereço completo"
            />
            <div className="space-y-2">
              {DELIVERY.map((opt, i) => (
                <label
                  key={opt}
                  className="flex items-center gap-3 rounded-sm border border-gray-200 px-4 py-3 text-sm text-gray-700"
                >
                  <input
                    type="radio"
                    name="delivery"
                    defaultChecked={i === 0}
                    className="accent-brand-900"
                  />
                  {opt}
                </label>
              ))}
            </div>
          </section>
        </div>

        <aside className="h-max rounded-sm border border-gray-100 bg-gray-50 p-6 lg:sticky lg:top-24">
          <h2 className="mb-4 text-lg font-medium text-brand-900">Resumo</h2>
          <dl className="space-y-3 text-sm text-gray-600">
            <div className="flex justify-between">
              <dt>Subtotal</dt>
              <dd className="font-medium text-brand-900">
                {formatPrice(cart.subtotalMinor, currency, locale)}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt>Frete</dt>
              <dd className="italic text-gray-500">A combinar</dd>
            </div>
            <div className="flex justify-between border-t border-gray-200 pt-3 text-base font-medium text-brand-900">
              <dt>Total</dt>
              <dd>{formatPrice(cart.subtotalMinor, currency, locale)}</dd>
            </div>
          </dl>
          <button
            type="button"
            onClick={confirm}
            className="mt-6 w-full rounded-sm bg-brand-900 py-4 text-base font-medium text-white shadow-sm transition-colors hover:bg-black"
          >
            Confirmar pedido
          </button>
          <p className="mt-3 text-center text-xs text-gray-400">
            Sem pagamento online — a loja entra em contato.
          </p>
        </aside>
      </div>
    </div>
  )
}
