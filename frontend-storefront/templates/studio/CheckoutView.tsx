"use client"

import Link from "next/link"

import { formatPrice } from "@/lib/format"
import type { CheckoutProps } from "@/lib/template-types"
import {
  type CheckoutController,
  COUNTRIES,
  orderWhatsappLink,
  shippingLabel,
  useCheckout,
} from "@/lib/use-checkout"

const FIELD =
  "block w-full rounded-md border border-gray-300 py-2.5 px-3.5 text-gray-900 placeholder-gray-400 focus:border-black focus:ring-1 focus:ring-black sm:text-sm transition-colors"
const SUBLABEL = "mb-1.5 block text-sm font-medium text-gray-900"

/** A numbered step badge (Studio's utilitarian section marker). */
function Step({ n, children }: { n: number; children: string }) {
  return (
    <h2 className="mb-6 flex items-center gap-2 text-xl font-bold text-gray-900">
      <span className="flex h-6 w-6 items-center justify-center rounded-full bg-black text-xs font-bold text-white">
        {n}
      </span>
      {children}
    </h2>
  )
}

/** Studio quantity stepper + remove for a checkout line (clean/utilitarian). */
function Stepper({
  co,
  itemId,
  qty,
}: {
  co: CheckoutController
  itemId: string
  qty: number
}) {
  return (
    <div className="mt-auto flex items-center justify-between pt-4">
      <div className="flex items-center rounded-md border border-gray-300">
        <button
          type="button"
          disabled={co.cartLoading}
          onClick={() => co.setItemQty(itemId, Math.max(1, qty - 1))}
          className="flex h-8 w-8 items-center justify-center text-gray-500 transition-colors hover:bg-gray-50 hover:text-gray-900 disabled:opacity-50"
          aria-label="Diminuir"
        >
          -
        </button>
        <span className="w-10 text-center text-sm font-medium text-gray-900">
          {qty}
        </span>
        <button
          type="button"
          disabled={co.cartLoading}
          onClick={() => co.setItemQty(itemId, qty + 1)}
          className="flex h-8 w-8 items-center justify-center text-gray-500 transition-colors hover:bg-gray-50 hover:text-gray-900 disabled:opacity-50"
          aria-label="Aumentar"
        >
          +
        </button>
      </div>
      <button
        type="button"
        disabled={co.cartLoading}
        onClick={() => co.removeItem(itemId)}
        className="text-sm font-medium text-gray-400 underline underline-offset-2 transition-colors hover:text-red-600 disabled:opacity-50"
      >
        Remover
      </button>
    </div>
  )
}

/**
 * Studio checkout (clean utilitarian catalog): numbered steps, an editable order
 * review, the full BR address, a surface-toned sticky summary with a black total
 * and a "no payment now" notice. On success it shows a centered inline
 * confirmation. Logic in {@link useCheckout}; this is the Studio look.
 *
 * @param store - The store (whatsapp + policies).
 * @param methods - The store's active shipping methods.
 * @param locale - Store locale for price formatting.
 * @returns The Studio checkout (or, after submit, the confirmation).
 */
export function CheckoutView({ store, methods, locale }: CheckoutProps) {
  const co = useCheckout(store, methods, locale)

  if (co.phase === "done" && co.order) {
    const order = co.order
    return (
      <div className="mx-auto w-full max-w-[1000px] px-4 py-12 lg:px-8 lg:py-20">
        <section className="mb-12 text-center">
          <div className="mb-6 inline-flex h-20 w-20 items-center justify-center rounded-full bg-green-50">
            <i className="fa-solid fa-check text-4xl text-green-500" />
          </div>
          <h1 className="mb-3 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
            Pedido recebido!
          </h1>
          <p className="mb-2 text-lg font-medium text-gray-600">
            A loja entrará em contato para combinar o pagamento e a entrega.
          </p>
          <div className="mt-4 inline-block rounded-lg border border-gray-200 bg-gray-50 px-6 py-3">
            <span className="mb-1 block text-sm text-gray-500">
              Número do pedido
            </span>
            <span className="text-xl font-bold text-black">
              #{order.order_number}
            </span>
          </div>
        </section>
        <section className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
          <div className="bg-gray-50/30 p-6 sm:p-8">
            <h2 className="mb-6 text-lg font-bold text-gray-900">
              Itens do pedido
            </h2>
            <ul className="divide-y divide-gray-100">
              {order.items.map((item) => (
                <li
                  key={item.id}
                  className="flex justify-between gap-4 py-4 first:pt-0"
                >
                  <div>
                    <h3 className="text-sm font-medium text-gray-900">
                      {item.name}
                    </h3>
                    <p className="mt-1 text-xs text-gray-500">
                      Qtd: {item.quantity}
                    </p>
                  </div>
                  <span className="text-sm font-bold text-gray-900">
                    {formatPrice(
                      item.unit_price_amount_minor * item.quantity,
                      order.currency,
                      locale,
                    )}
                  </span>
                </li>
              ))}
            </ul>
          </div>
          <div className="flex items-center justify-between border-t border-gray-200 p-6 sm:p-8">
            <span className="text-base font-semibold text-gray-900">Total</span>
            <span className="text-2xl font-bold tracking-tight text-black">
              {formatPrice(order.total_amount_minor, order.currency, locale)}
            </span>
          </div>
        </section>
        <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center">
          {co.whatsappNumber ? (
            <a
              href={orderWhatsappLink(co.whatsappNumber, order, locale)}
              target="_blank"
              rel="noreferrer"
              className="flex items-center justify-center gap-2 rounded-md bg-green-600 px-8 py-3.5 text-sm font-medium text-white transition-colors hover:bg-green-700"
            >
              <i className="fa-brands fa-whatsapp text-lg" /> Combinar pagamento
              no WhatsApp
            </a>
          ) : null}
          <Link
            href="/"
            className="flex items-center justify-center rounded-md border border-gray-300 px-8 py-3.5 text-sm font-medium text-gray-700 transition-colors hover:border-black hover:text-black"
          >
            Voltar à loja
          </Link>
        </div>
      </div>
    )
  }

  if (co.phase === "empty") {
    return (
      <div className="mx-auto flex max-w-md flex-col items-center px-4 py-24 text-center">
        <p className="mb-8 text-sm text-gray-500">Seu carrinho está vazio.</p>
        <Link
          href="/products"
          className="rounded-md bg-black px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-gray-800"
        >
          Ver produtos
        </Link>
      </div>
    )
  }

  return (
    <form
      onSubmit={co.onSubmit}
      className="mx-auto w-full max-w-[1200px] px-4 py-10 lg:px-8 lg:py-16"
    >
      <nav className="mb-8 flex text-xs text-gray-500" aria-label="Breadcrumb">
        <ol className="inline-flex items-center space-x-2">
          <li>Carrinho</li>
          <li className="flex items-center">
            <i className="fa-solid fa-chevron-right mx-2 text-[8px]" />
            <span className="font-medium text-gray-900">Finalizar Pedido</span>
          </li>
        </ol>
      </nav>
      <div className="grid grid-cols-1 gap-10 lg:grid-cols-12 lg:gap-16">
        <div className="flex flex-col gap-12 lg:col-span-7">
          <section>
            <Step n={1}>Seu pedido</Step>
            <div className="overflow-hidden rounded-lg border border-gray-200">
              <ul className="divide-y divide-gray-200">
                {co.items.map((item) => (
                  <li key={item.id} className="flex gap-4 bg-white p-4 sm:p-6">
                    <div className="h-24 w-20 flex-shrink-0 overflow-hidden rounded-md border border-gray-100 bg-gray-50">
                      {item.image ? (
                        <img
                          src={item.image}
                          alt={item.name}
                          className="h-full w-full object-contain p-2 mix-blend-multiply"
                        />
                      ) : null}
                    </div>
                    <div className="flex flex-1 flex-col">
                      <div className="flex items-start justify-between gap-4">
                        <h3 className="text-base font-medium text-gray-900">
                          {item.name}
                        </h3>
                        <span className="text-base font-bold text-gray-900">
                          {formatPrice(
                            item.priceAmountMinor * item.qty,
                            item.priceCurrency,
                            locale,
                          )}
                        </span>
                      </div>
                      <Stepper co={co} itemId={item.id} qty={item.qty} />
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </section>

          <section>
            <Step n={2}>Contato</Step>
            <p className="-mt-2 mb-6 text-sm text-gray-500">
              Usaremos estes dados para falar sobre o seu pedido. Não é
              necessário criar conta.
            </p>
            <div className="grid grid-cols-1 gap-x-6 gap-y-5">
              <label className="block">
                <span className={SUBLABEL}>Nome completo</span>
                <input
                  className={FIELD}
                  placeholder="João da Silva"
                  value={co.name}
                  onChange={(e) => co.setName(e.target.value)}
                  required
                />
              </label>
              <label className="block">
                <span className={SUBLABEL}>E-mail</span>
                <input
                  className={FIELD}
                  type="email"
                  placeholder="joao@exemplo.com"
                  value={co.email}
                  onChange={(e) => co.setEmail(e.target.value)}
                />
              </label>
              <label className="block">
                <span className={SUBLABEL}>WhatsApp / Telefone</span>
                <div className="flex overflow-hidden rounded-md border border-gray-300 transition-colors focus-within:border-black focus-within:ring-1 focus-within:ring-black">
                  <select
                    className="border-r border-gray-300 bg-gray-50 px-3 text-sm text-gray-500 outline-none"
                    value={co.country}
                    onChange={(e) => co.setCountry(e.target.value)}
                  >
                    {COUNTRIES.map((c) => (
                      <option key={c.code} value={c.code}>
                        {c.label}
                      </option>
                    ))}
                  </select>
                  <input
                    className="block flex-1 border-0 bg-white px-3.5 py-2.5 text-gray-900 placeholder-gray-400 outline-none sm:text-sm"
                    placeholder="(00) 00000-0000"
                    value={co.phone}
                    onChange={(e) => co.setPhone(e.target.value)}
                  />
                </div>
              </label>
            </div>
          </section>

          <section>
            <Step n={3}>Entrega</Step>
            <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-gray-900">
              Endereço de destino
            </h3>
            <div className="mb-8 grid grid-cols-1 gap-x-6 gap-y-5 md:grid-cols-6">
              <label className="block md:col-span-2">
                <span className={SUBLABEL}>CEP</span>
                <input
                  className={FIELD}
                  placeholder="00000-000"
                  value={co.postalCode}
                  onChange={(e) => co.setPostalCode(e.target.value)}
                />
              </label>
              <label className="block md:col-span-4">
                <span className={SUBLABEL}>Endereço</span>
                <input
                  className={FIELD}
                  placeholder="Rua, Avenida, etc."
                  value={co.line1}
                  onChange={(e) => co.setLine1(e.target.value)}
                  required
                />
              </label>
              <label className="block md:col-span-2">
                <span className={SUBLABEL}>Número</span>
                <input
                  className={FIELD}
                  value={co.number}
                  onChange={(e) => co.setNumber(e.target.value)}
                />
              </label>
              <label className="block md:col-span-4">
                <span className={SUBLABEL}>
                  Complemento{" "}
                  <span className="font-normal text-gray-400">(Opcional)</span>
                </span>
                <input
                  className={FIELD}
                  placeholder="Apto, Bloco, etc."
                  value={co.line2}
                  onChange={(e) => co.setLine2(e.target.value)}
                />
              </label>
              <label className="block md:col-span-2">
                <span className={SUBLABEL}>Bairro</span>
                <input
                  className={FIELD}
                  value={co.neighborhood}
                  onChange={(e) => co.setNeighborhood(e.target.value)}
                />
              </label>
              <label className="block md:col-span-3">
                <span className={SUBLABEL}>Cidade</span>
                <input
                  className={FIELD}
                  value={co.city}
                  onChange={(e) => co.setCity(e.target.value)}
                  required
                />
              </label>
              <label className="block md:col-span-1">
                <span className={SUBLABEL}>UF</span>
                <input
                  className={FIELD}
                  value={co.state}
                  onChange={(e) => co.setState(e.target.value)}
                />
              </label>
            </div>
            <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-gray-900">
              Opções de Entrega
            </h3>
            <div className="space-y-3">
              {co.methods.map((method) => (
                <label
                  key={method.id}
                  className="flex cursor-pointer gap-4 rounded-lg border border-gray-200 bg-white p-4 transition-colors hover:bg-gray-50 has-[:checked]:border-black has-[:checked]:bg-gray-50 sm:p-5"
                >
                  <input
                    type="radio"
                    name="delivery_method"
                    value={method.id}
                    checked={co.methodId === method.id}
                    onChange={() => co.setMethodId(method.id)}
                    className="mt-0.5 accent-black"
                  />
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-900">
                        {shippingLabel(method)}
                      </span>
                      {method.type === "fixed_shipping" &&
                      method.price_amount_minor != null ? (
                        <span className="text-sm font-bold text-gray-900">
                          {formatPrice(
                            method.price_amount_minor,
                            co.currency,
                            locale,
                          )}
                        </span>
                      ) : method.type === "private_delivery" ? (
                        <span className="text-sm font-bold text-gray-900">
                          A combinar
                        </span>
                      ) : (
                        <span className="text-sm font-bold text-green-600">
                          Grátis
                        </span>
                      )}
                    </div>
                    {method.description ? (
                      <span className="mt-1 block text-sm text-gray-500">
                        {method.description}
                      </span>
                    ) : null}
                  </div>
                </label>
              ))}
              {co.methods.length === 0 ? (
                <p className="text-sm text-gray-500">
                  Esta loja ainda não configurou formas de entrega.
                </p>
              ) : null}
            </div>
          </section>
        </div>

        <div className="lg:col-span-5">
          <div className="sticky top-24 flex flex-col gap-6 rounded-xl border border-gray-200 bg-gray-50 p-6 sm:p-8">
            <h2 className="border-b border-gray-200 pb-4 text-lg font-bold text-gray-900">
              Resumo do Pedido
            </h2>
            <div className="space-y-3 border-b border-gray-200 pb-6 text-sm">
              <div className="flex justify-between text-gray-600">
                <span>Subtotal</span>
                <span className="font-medium text-gray-900">
                  {formatPrice(co.subtotalMinor, co.currency, locale)}
                </span>
              </div>
              <div className="flex justify-between text-gray-600">
                <span>Frete</span>
                <span className="font-medium text-gray-900">
                  {co.selected && co.selected.type !== "fixed_shipping"
                    ? "A combinar"
                    : formatPrice(co.shippingMinor, co.currency, locale)}
                </span>
              </div>
            </div>
            <div className="flex items-end justify-between">
              <span className="text-base font-semibold text-gray-900">
                Total
              </span>
              <span className="text-3xl font-bold tracking-tight text-black">
                {formatPrice(co.totalMinor, co.currency, locale)}
              </span>
            </div>
            <div className="flex gap-3 rounded-md border border-yellow-200 bg-yellow-50 p-4">
              <i className="fa-solid fa-bell mt-0.5 text-yellow-600" />
              <p className="text-xs leading-relaxed text-yellow-800">
                <strong>Nenhum pagamento é exigido agora.</strong> Ao confirmar,
                seu pedido é registrado e a loja entra em contato para finalizar
                o pagamento e a entrega.
              </p>
            </div>
            {co.error ? (
              <p className="text-sm text-red-600">{co.error}</p>
            ) : null}
            <button
              type="submit"
              disabled={!co.canSubmit}
              className="flex h-14 w-full items-center justify-center gap-2 rounded-md bg-black text-lg font-bold text-white transition-colors hover:bg-gray-800 disabled:opacity-50"
            >
              {co.submitting ? "Enviando…" : "Confirmar Pedido"}
              <i className="fa-solid fa-check" />
            </button>
            {store.return_policy ||
            store.exchange_policy ||
            store.privacy_policy ? (
              <div className="text-xs leading-relaxed text-gray-500">
                {store.return_policy ? (
                  <p className="mb-1">{store.return_policy}</p>
                ) : null}
                {store.exchange_policy ? (
                  <p className="mb-1">{store.exchange_policy}</p>
                ) : null}
                {store.privacy_policy ? <p>{store.privacy_policy}</p> : null}
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </form>
  )
}
