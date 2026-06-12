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
  "w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 outline-none transition-all"
const SUBLABEL = "mb-1 block text-xs font-semibold text-gray-500"

/** Bazar quantity stepper + remove for a checkout line (bold/marketplace). */
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
    <div className="mt-4 flex items-center justify-between">
      <div className="flex items-center gap-2 rounded-lg border border-gray-200 bg-gray-50 p-1">
        <button
          type="button"
          disabled={co.cartLoading}
          onClick={() => co.setItemQty(itemId, Math.max(1, qty - 1))}
          className="flex h-8 w-8 items-center justify-center text-gray-500 hover:text-indigo-600 disabled:opacity-50"
          aria-label="Diminuir"
        >
          <i className="fa-solid fa-minus text-sm" />
        </button>
        <span className="w-6 text-center text-sm font-bold text-gray-900">
          {qty}
        </span>
        <button
          type="button"
          disabled={co.cartLoading}
          onClick={() => co.setItemQty(itemId, qty + 1)}
          className="flex h-8 w-8 items-center justify-center text-gray-500 hover:text-indigo-600 disabled:opacity-50"
          aria-label="Aumentar"
        >
          <i className="fa-solid fa-plus text-sm" />
        </button>
      </div>
      <button
        type="button"
        disabled={co.cartLoading}
        onClick={() => co.removeItem(itemId)}
        className="flex items-center gap-1 text-sm font-medium text-red-500 transition hover:text-red-700 disabled:opacity-50"
      >
        <i className="fa-regular fa-trash-can" /> Remover
      </button>
    </div>
  )
}

/**
 * Bazar checkout (vibrant marketplace): rounded cards with icon headings, an
 * editable order review, the full BR address, peer radio delivery cards and a
 * dark sticky summary with an indigo total. On success it shows an inline
 * confirmation with a gradient hero + WhatsApp handoff. Logic in
 * {@link useCheckout}; this is the Bazar look.
 *
 * @param store - The store (whatsapp + policies).
 * @param methods - The store's active shipping methods.
 * @param locale - Store locale for price formatting.
 * @returns The Bazar checkout (or, after submit, the confirmation).
 */
export function CheckoutView({ store, methods, locale }: CheckoutProps) {
  const co = useCheckout(store, methods, locale)

  if (co.phase === "done" && co.order) {
    const order = co.order
    return (
      <div className="mx-auto w-full max-w-3xl px-4 py-12 sm:px-6 md:py-16">
        <div className="overflow-hidden rounded-[2rem] border border-gray-100 bg-white shadow-float">
          <div className="bg-gradient-to-br from-indigo-600 to-indigo-900 px-6 py-12 text-center md:py-16">
            <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-2xl bg-white text-4xl text-indigo-600 shadow-xl">
              <i className="fa-solid fa-check" />
            </div>
            <h1 className="mb-4 text-3xl font-extrabold tracking-tight text-white md:text-5xl">
              Pedido recebido!
            </h1>
            <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-white/20 px-4 py-2 font-medium text-white backdrop-blur-sm">
              <i className="fa-solid fa-hashtag text-sm text-indigo-100" />
              Pedido nº {order.order_number}
            </div>
            <p className="mx-auto max-w-lg text-lg font-medium text-indigo-100">
              A loja entrará em contato para combinar pagamento e entrega.
            </p>
          </div>
          <div className="p-6 md:p-10">
            <div className="mb-8 space-y-4">
              {order.items.map((item) => (
                <div key={item.id} className="flex items-center gap-4">
                  <div className="flex-1">
                    <h4 className="text-sm font-bold text-gray-900">
                      {item.name}
                    </h4>
                    <p className="mt-1 text-xs text-gray-500">
                      Qtd: {item.quantity}
                    </p>
                  </div>
                  <div className="text-sm font-bold text-gray-900">
                    {formatPrice(
                      item.unit_price_amount_minor * item.quantity,
                      order.currency,
                      locale,
                    )}
                  </div>
                </div>
              ))}
            </div>
            <div className="mb-8 flex items-center justify-between border-t border-gray-100 pt-6">
              <span className="text-lg font-medium text-gray-600">Total</span>
              <span className="text-2xl font-extrabold text-indigo-600">
                {formatPrice(order.total_amount_minor, order.currency, locale)}
              </span>
            </div>
            <div className="flex flex-col gap-3 sm:flex-row">
              {co.whatsappNumber ? (
                <a
                  href={orderWhatsappLink(co.whatsappNumber, order, locale)}
                  target="_blank"
                  rel="noreferrer"
                  className="flex flex-1 items-center justify-center gap-2 rounded-2xl bg-green-600 px-6 py-4 font-bold text-white transition-colors hover:bg-green-700"
                >
                  <i className="fa-brands fa-whatsapp text-lg" /> Combinar
                  pagamento no WhatsApp
                </a>
              ) : null}
              <Link
                href="/"
                className="flex items-center justify-center rounded-2xl border-2 border-gray-200 px-6 py-4 font-bold text-gray-700 transition-colors hover:border-indigo-600 hover:text-indigo-600"
              >
                Voltar à loja
              </Link>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (co.phase === "empty") {
    return (
      <div className="mx-auto flex max-w-md flex-col items-center px-4 py-24 text-center">
        <p className="mb-8 text-gray-500">Seu carrinho está vazio.</p>
        <Link
          href="/products"
          className="rounded-xl bg-indigo-600 px-6 py-3 font-bold text-white shadow-float transition hover:bg-indigo-700"
        >
          Ver produtos
        </Link>
      </div>
    )
  }

  return (
    <form
      onSubmit={co.onSubmit}
      className="mx-auto w-full max-w-[1200px] px-4 py-8 sm:px-6 md:py-12 lg:px-8"
    >
      <h1 className="mb-8 text-3xl font-extrabold tracking-tight text-gray-900 md:text-4xl">
        Finalizar Pedido
      </h1>
      <div className="flex flex-col gap-8 lg:flex-row lg:gap-12">
        <div className="w-full space-y-8 lg:w-2/3">
          <section className="rounded-3xl border border-gray-100 bg-white p-6 shadow-sm md:p-8">
            <h2 className="mb-6 flex items-center gap-3 text-xl font-bold text-gray-900">
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-100 text-sm text-indigo-600">
                <i className="fa-solid fa-box" />
              </span>
              Seu pedido
            </h2>
            <div className="space-y-6">
              {co.items.map((item) => (
                <div
                  key={item.id}
                  className="flex gap-4 border-b border-gray-100 pb-6 last:border-0 last:pb-0"
                >
                  <div className="h-24 w-24 flex-shrink-0 overflow-hidden rounded-xl border border-gray-100 bg-gray-50">
                    {item.image ? (
                      <img
                        src={item.image}
                        alt={item.name}
                        className="h-full w-full object-cover"
                      />
                    ) : null}
                  </div>
                  <div className="flex flex-1 flex-col justify-between">
                    <div className="flex items-start justify-between">
                      <h3 className="font-bold text-gray-900">{item.name}</h3>
                      <span className="font-extrabold text-indigo-600">
                        {formatPrice(
                          item.priceAmountMinor * item.qty,
                          item.priceCurrency,
                          locale,
                        )}
                      </span>
                    </div>
                    <Stepper co={co} itemId={item.id} qty={item.qty} />
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-3xl border border-gray-100 bg-white p-6 shadow-sm md:p-8">
            <h2 className="mb-6 flex items-center gap-3 text-xl font-bold text-gray-900">
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-100 text-sm text-indigo-600">
                <i className="fa-regular fa-user" />
              </span>
              Informações de Contato
            </h2>
            <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
              <label className="block md:col-span-2">
                <span className="mb-1.5 block text-sm font-semibold text-gray-700">
                  Nome Completo
                </span>
                <input
                  className={FIELD}
                  placeholder="Ex: João da Silva"
                  value={co.name}
                  onChange={(e) => co.setName(e.target.value)}
                  required
                />
              </label>
              <label className="block">
                <span className="mb-1.5 block text-sm font-semibold text-gray-700">
                  E-mail
                </span>
                <input
                  className={FIELD}
                  type="email"
                  placeholder="seu@email.com"
                  value={co.email}
                  onChange={(e) => co.setEmail(e.target.value)}
                />
              </label>
              <label className="block">
                <span className="mb-1.5 block text-sm font-semibold text-gray-700">
                  WhatsApp / Celular
                </span>
                <div className="flex">
                  <select
                    className="flex-shrink-0 rounded-l-xl border border-r-0 border-gray-200 bg-gray-50 px-3 text-sm font-medium outline-none focus:border-indigo-500"
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
                    className={`${FIELD} rounded-l-none`}
                    placeholder="(11) 99999-9999"
                    value={co.phone}
                    onChange={(e) => co.setPhone(e.target.value)}
                  />
                </div>
              </label>
            </div>
          </section>

          <section className="rounded-3xl border border-gray-100 bg-white p-6 shadow-sm md:p-8">
            <h2 className="mb-6 flex items-center gap-3 text-xl font-bold text-gray-900">
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-100 text-sm text-indigo-600">
                <i className="fa-solid fa-truck-fast" />
              </span>
              Entrega
            </h2>
            <h3 className="mb-4 text-sm font-bold uppercase tracking-wider text-gray-900">
              Endereço de Destino
            </h3>
            <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-12">
              <label className="block sm:col-span-4">
                <span className={SUBLABEL}>CEP</span>
                <input
                  className={FIELD}
                  placeholder="00000-000"
                  value={co.postalCode}
                  onChange={(e) => co.setPostalCode(e.target.value)}
                />
              </label>
              <label className="block sm:col-span-8">
                <span className={SUBLABEL}>Rua / Avenida</span>
                <input
                  className={FIELD}
                  placeholder="Nome da rua"
                  value={co.line1}
                  onChange={(e) => co.setLine1(e.target.value)}
                  required
                />
              </label>
              <label className="block sm:col-span-3">
                <span className={SUBLABEL}>Número</span>
                <input
                  className={FIELD}
                  placeholder="123"
                  value={co.number}
                  onChange={(e) => co.setNumber(e.target.value)}
                />
              </label>
              <label className="block sm:col-span-5">
                <span className={SUBLABEL}>Complemento</span>
                <input
                  className={FIELD}
                  placeholder="Apto, Sala, etc."
                  value={co.line2}
                  onChange={(e) => co.setLine2(e.target.value)}
                />
              </label>
              <label className="block sm:col-span-4">
                <span className={SUBLABEL}>Bairro</span>
                <input
                  className={FIELD}
                  placeholder="Bairro"
                  value={co.neighborhood}
                  onChange={(e) => co.setNeighborhood(e.target.value)}
                />
              </label>
              <label className="block sm:col-span-8">
                <span className={SUBLABEL}>Cidade</span>
                <input
                  className={FIELD}
                  placeholder="Cidade"
                  value={co.city}
                  onChange={(e) => co.setCity(e.target.value)}
                  required
                />
              </label>
              <label className="block sm:col-span-4">
                <span className={SUBLABEL}>Estado</span>
                <input
                  className={FIELD}
                  placeholder="UF"
                  value={co.state}
                  onChange={(e) => co.setState(e.target.value)}
                />
              </label>
            </div>
            <h3 className="mb-4 text-sm font-bold uppercase tracking-wider text-gray-900">
              Opções de Entrega
            </h3>
            <div className="space-y-3">
              {co.methods.map((method) => (
                <label
                  key={method.id}
                  className="relative flex cursor-pointer items-center gap-4 rounded-2xl border border-gray-200 bg-white p-4 shadow-sm transition-all hover:bg-gray-50 has-[:checked]:border-indigo-500 has-[:checked]:bg-indigo-50"
                >
                  <input
                    type="radio"
                    name="delivery_method"
                    value={method.id}
                    checked={co.methodId === method.id}
                    onChange={() => co.setMethodId(method.id)}
                    className="accent-indigo-600"
                  />
                  <div className="flex flex-1 items-center justify-between">
                    <div>
                      <p className="font-bold text-gray-900">
                        {shippingLabel(method)}
                      </p>
                      {method.description ? (
                        <p className="mt-0.5 text-xs text-gray-500">
                          {method.description}
                        </p>
                      ) : null}
                    </div>
                    {method.type === "fixed_shipping" &&
                    method.price_amount_minor != null ? (
                      <span className="font-bold text-gray-900">
                        {formatPrice(
                          method.price_amount_minor,
                          co.currency,
                          locale,
                        )}
                      </span>
                    ) : method.type === "private_delivery" ? (
                      <span className="text-sm font-medium text-gray-500">
                        A combinar
                      </span>
                    ) : (
                      <span className="rounded-md bg-green-50 px-2 py-1 text-sm font-bold text-green-600">
                        Grátis
                      </span>
                    )}
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

          {store.return_policy ||
          store.exchange_policy ||
          store.privacy_policy ? (
            <section className="rounded-3xl border border-gray-100 bg-white p-6 text-xs leading-relaxed text-gray-500 shadow-sm md:p-8">
              <h2 className="mb-2 text-sm font-bold text-gray-900">
                Políticas da loja
              </h2>
              {store.return_policy ? (
                <p className="mb-1">{store.return_policy}</p>
              ) : null}
              {store.exchange_policy ? (
                <p className="mb-1">{store.exchange_policy}</p>
              ) : null}
              {store.privacy_policy ? <p>{store.privacy_policy}</p> : null}
            </section>
          ) : null}
        </div>

        <div className="w-full lg:w-1/3">
          <div className="sticky top-24 rounded-3xl border border-gray-800 bg-gray-900 p-6 text-white shadow-2xl md:p-8">
            <h2 className="mb-6 flex items-center gap-3 text-xl font-bold">
              <i className="fa-solid fa-receipt text-indigo-400" /> Resumo do
              Pedido
            </h2>
            <div className="mb-6 space-y-4">
              <div className="flex items-center justify-between text-gray-400">
                <span>Subtotal</span>
                <span className="font-medium text-white">
                  {formatPrice(co.subtotalMinor, co.currency, locale)}
                </span>
              </div>
              <div className="flex items-center justify-between text-gray-400">
                <span>Frete</span>
                <span className="font-medium text-white">
                  {co.selected && co.selected.type !== "fixed_shipping" ? (
                    <span className="italic text-gray-400">A combinar</span>
                  ) : (
                    formatPrice(co.shippingMinor, co.currency, locale)
                  )}
                </span>
              </div>
            </div>
            <div className="mb-8 flex items-center justify-between border-t border-gray-800 pt-6">
              <span className="text-lg font-medium text-gray-300">Total</span>
              <span className="text-3xl font-extrabold tracking-tight text-indigo-400">
                {formatPrice(co.totalMinor, co.currency, locale)}
              </span>
            </div>
            {co.error ? (
              <p className="mb-4 text-sm text-rose-400">{co.error}</p>
            ) : null}
            <button
              type="submit"
              disabled={!co.canSubmit}
              className="flex w-full items-center justify-center gap-3 rounded-2xl bg-indigo-600 px-6 py-4 text-lg font-extrabold text-white transition-all hover:bg-indigo-500 disabled:opacity-50"
            >
              {co.submitting ? "Enviando…" : "Confirmar Pedido"}
              <i className="fa-solid fa-check" />
            </button>
            <p className="mt-4 text-center text-xs leading-relaxed text-gray-500">
              <i className="fa-solid fa-circle-info mr-1" /> Ao confirmar, seu
              pedido é registrado e a loja combina o pagamento.
            </p>
          </div>
        </div>
      </div>
    </form>
  )
}
