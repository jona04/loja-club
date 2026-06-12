"use client"

import Link from "next/link"
import { useState } from "react"

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
  "w-full rounded-sm border border-gray-200 px-3 py-2.5 text-sm focus:border-brand-900 focus:outline-none"

/** Aurora quantity stepper + remove for a checkout line (minimal/editorial). */
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
    <div className="mt-2 flex items-center gap-4 text-sm">
      <div className="flex items-center rounded-sm border border-gray-200">
        <button
          type="button"
          disabled={co.cartLoading}
          onClick={() => co.setItemQty(itemId, Math.max(1, qty - 1))}
          className="px-2.5 py-1 text-gray-500 hover:text-brand-900 disabled:opacity-50"
          aria-label="Diminuir"
        >
          −
        </button>
        <span className="w-8 text-center text-brand-900">{qty}</span>
        <button
          type="button"
          disabled={co.cartLoading}
          onClick={() => co.setItemQty(itemId, qty + 1)}
          className="px-2.5 py-1 text-gray-500 hover:text-brand-900 disabled:opacity-50"
          aria-label="Aumentar"
        >
          +
        </button>
      </div>
      <button
        type="button"
        disabled={co.cartLoading}
        onClick={() => co.removeItem(itemId)}
        className="text-gray-400 underline-offset-2 hover:text-brand-900 hover:underline disabled:opacity-50"
      >
        Remover
      </button>
    </div>
  )
}

/**
 * Aurora checkout (premium minimalista): editorial single-page layout — an
 * editable order review, contact (split first/last name) + full address +
 * shipping with a sticky summary, and an inline confirmation (order number +
 * WhatsApp handoff). The logic lives in {@link useCheckout}; this is the look.
 *
 * @param store - The store (whatsapp + policies).
 * @param methods - The store's active shipping methods.
 * @param locale - Store locale for price formatting.
 * @returns The Aurora checkout (or, after submit, the confirmation).
 */
export function CheckoutView({ store, methods, locale }: CheckoutProps) {
  const co = useCheckout(store, methods, locale)
  const [firstName, setFirstName] = useState("")
  const [lastName, setLastName] = useState("")

  if (co.phase === "done" && co.order) {
    const order = co.order
    return (
      <div className="mx-auto flex max-w-lg flex-col items-center px-4 py-20 text-center sm:px-6">
        <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-green-50 text-2xl text-green-600">
          <i className="fa-solid fa-check" />
        </div>
        <h1 className="mb-2 text-3xl font-semibold tracking-tight text-brand-900">
          Pedido recebido!
        </h1>
        <p className="mb-6 text-xs font-medium uppercase tracking-wider text-gray-500">
          Pedido #{order.order_number}
        </p>
        <p className="mb-6 max-w-md rounded-md border border-gray-200 bg-gray-50 p-4 text-sm leading-relaxed text-gray-700">
          Sem pagamento online — combine o pagamento direto com a loja. Total:{" "}
          <strong>
            {formatPrice(order.total_amount_minor, order.currency, locale)}
          </strong>
          .
        </p>
        {co.whatsappNumber ? (
          <a
            href={orderWhatsappLink(co.whatsappNumber, order, locale)}
            target="_blank"
            rel="noreferrer"
            className="mb-3 inline-flex items-center gap-2 rounded-md bg-green-600 px-8 py-4 text-sm font-medium text-white transition-colors hover:bg-green-700"
          >
            <i className="fa-brands fa-whatsapp text-lg" /> Combinar pagamento
            no WhatsApp
          </a>
        ) : null}
        <Link
          href="/"
          className="rounded-md px-8 py-3 text-sm font-medium text-gray-600 transition-colors hover:text-brand-900"
        >
          Voltar à loja
        </Link>
      </div>
    )
  }

  if (co.phase === "empty") {
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

  return (
    <form
      onSubmit={co.onSubmit}
      className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8"
    >
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
              {co.items.map((item) => (
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
                  <div className="flex flex-1 justify-between">
                    <div>
                      <p className="text-sm font-medium text-brand-900">
                        {item.name}
                      </p>
                      <Stepper co={co} itemId={item.id} qty={item.qty} />
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
              <input
                className={FIELD}
                placeholder="Nome"
                value={firstName}
                onChange={(e) => {
                  setFirstName(e.target.value)
                  co.setName(`${e.target.value} ${lastName}`.trim())
                }}
                required
              />
              <input
                className={FIELD}
                placeholder="Sobrenome"
                value={lastName}
                onChange={(e) => {
                  setLastName(e.target.value)
                  co.setName(`${firstName} ${e.target.value}`.trim())
                }}
              />
              <input
                className={`${FIELD} sm:col-span-2`}
                placeholder="E-mail"
                type="email"
                value={co.email}
                onChange={(e) => co.setEmail(e.target.value)}
              />
              <div className="flex gap-2 sm:col-span-2">
                <select
                  className={`${FIELD} w-28`}
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
                  className={FIELD}
                  placeholder="Telefone / WhatsApp"
                  value={co.phone}
                  onChange={(e) => co.setPhone(e.target.value)}
                />
              </div>
            </div>
          </section>

          <section>
            <h2 className="mb-4 text-lg font-medium text-brand-900">
              Endereço de entrega
            </h2>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-6">
              <input
                className={`${FIELD} sm:col-span-2`}
                placeholder="CEP"
                value={co.postalCode}
                onChange={(e) => co.setPostalCode(e.target.value)}
              />
              <input
                className={`${FIELD} sm:col-span-4`}
                placeholder="Endereço (Rua, Avenida...)"
                value={co.line1}
                onChange={(e) => co.setLine1(e.target.value)}
                required
              />
              <input
                className={`${FIELD} sm:col-span-2`}
                placeholder="Número"
                value={co.number}
                onChange={(e) => co.setNumber(e.target.value)}
              />
              <input
                className={`${FIELD} sm:col-span-4`}
                placeholder="Complemento (Apto, Bloco)"
                value={co.line2}
                onChange={(e) => co.setLine2(e.target.value)}
              />
              <input
                className={`${FIELD} sm:col-span-2`}
                placeholder="Bairro"
                value={co.neighborhood}
                onChange={(e) => co.setNeighborhood(e.target.value)}
              />
              <input
                className={`${FIELD} sm:col-span-3`}
                placeholder="Cidade"
                value={co.city}
                onChange={(e) => co.setCity(e.target.value)}
                required
              />
              <input
                className={`${FIELD} sm:col-span-1`}
                placeholder="Estado"
                value={co.state}
                onChange={(e) => co.setState(e.target.value)}
              />
            </div>
          </section>

          <section>
            <h2 className="mb-4 text-lg font-medium text-brand-900">Entrega</h2>
            <div className="space-y-2">
              {co.methods.map((method) => (
                <label
                  key={method.id}
                  className="flex items-center gap-3 rounded-sm border border-gray-200 px-4 py-3 text-sm text-gray-700"
                >
                  <input
                    type="radio"
                    name="shipping"
                    value={method.id}
                    checked={co.methodId === method.id}
                    onChange={() => co.setMethodId(method.id)}
                    className="accent-brand-900"
                  />
                  <span className="flex-1">
                    {shippingLabel(method)}
                    {method.description ? (
                      <span className="block text-xs text-gray-500">
                        {method.description}
                      </span>
                    ) : null}
                  </span>
                  {method.type === "fixed_shipping" &&
                  method.price_amount_minor != null ? (
                    <span className="text-gray-900">
                      {formatPrice(
                        method.price_amount_minor,
                        co.currency,
                        locale,
                      )}
                    </span>
                  ) : null}
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
            <section className="text-xs leading-relaxed text-gray-500">
              <h2 className="mb-2 text-sm font-medium text-brand-900">
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

        <aside className="h-max rounded-sm border border-gray-100 bg-gray-50 p-6 lg:sticky lg:top-24">
          <h2 className="mb-4 text-lg font-medium text-brand-900">Resumo</h2>
          <dl className="space-y-3 text-sm text-gray-600">
            <div className="flex justify-between">
              <dt>Subtotal</dt>
              <dd className="font-medium text-brand-900">
                {formatPrice(co.subtotalMinor, co.currency, locale)}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt>Frete</dt>
              <dd>
                {co.selected && co.selected.type !== "fixed_shipping" ? (
                  <span className="italic text-gray-500">A combinar</span>
                ) : (
                  formatPrice(co.shippingMinor, co.currency, locale)
                )}
              </dd>
            </div>
            <div className="flex justify-between border-t border-gray-200 pt-3 text-base font-medium text-brand-900">
              <dt>Total</dt>
              <dd>{formatPrice(co.totalMinor, co.currency, locale)}</dd>
            </div>
          </dl>
          {co.error ? (
            <p className="mt-4 text-sm text-red-600">{co.error}</p>
          ) : null}
          <button
            type="submit"
            disabled={!co.canSubmit}
            className="mt-6 w-full rounded-sm bg-brand-900 py-4 text-base font-medium text-white shadow-sm transition-colors hover:bg-black disabled:opacity-50"
          >
            {co.submitting ? "Enviando…" : "Confirmar pedido"}
          </button>
          <p className="mt-3 text-center text-xs text-gray-400">
            Sem pagamento online — a loja combina o pagamento.
          </p>
        </aside>
      </div>
    </form>
  )
}
