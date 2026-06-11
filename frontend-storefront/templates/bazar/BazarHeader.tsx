"use client"

import Link from "next/link"

import type { Category } from "@/lib/api"
import { useCart } from "@/lib/cart"
import { formatPrice } from "@/lib/format"

/**
 * Bazar header (faithful to the template): promo top bar, logo, category nav,
 * search field and the cart button (with a count badge), plus the slide-over
 * mini-cart drawer driven by the client cart. Vibrant indigo/rose marketplace.
 *
 * @param name - The store display name.
 * @param categories - Categories for the nav.
 * @param locale - Store locale for price formatting.
 * @returns The header and cart drawer.
 */
export function BazarHeader({
  name,
  categories,
  locale,
  announcement,
}: {
  name: string
  categories: Category[]
  locale: string
  announcement: string
}) {
  const cart = useCart()

  return (
    <>
      <header className="sticky top-0 z-40 w-full border-b border-gray-200 bg-white/95 shadow-sm backdrop-blur-md">
        <div className="bg-indigo-900 py-1.5 text-center text-xs font-medium text-indigo-50">
          {announcement}
        </div>
        <div className="mx-auto max-w-[1400px] px-4 sm:px-6 lg:px-8">
          <div className="flex h-20 items-center justify-between gap-4">
            <Link href="/" className="group flex items-center gap-2">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-xl font-bold text-white shadow-md transition-transform group-hover:scale-105">
                <i className="fa-solid fa-bolt" />
              </div>
              <span className="text-2xl font-bold tracking-tight text-gray-900">
                {name}
              </span>
            </Link>

            <nav className="hidden items-center gap-8 font-medium text-gray-600 lg:flex">
              {categories.slice(0, 5).map((c) => (
                <Link
                  key={c.id}
                  href={`/categories/${c.slug}`}
                  className="transition-colors hover:text-indigo-600"
                >
                  {c.name}
                </Link>
              ))}
              <Link
                href="/products"
                className="flex items-center gap-1.5 font-bold text-indigo-600 transition-colors hover:text-indigo-700"
              >
                <i className="fa-solid fa-layer-group" /> Todas as categorias
              </Link>
            </nav>

            <div className="flex items-center gap-3 sm:gap-5">
              <Link
                href="/products"
                className="relative hidden w-64 md:flex xl:w-80"
                aria-label="Buscar"
              >
                <span className="w-full rounded-full border-transparent bg-gray-100 py-2.5 pl-10 pr-4 text-sm text-gray-400">
                  Buscar produtos...
                </span>
                <i className="fa-solid fa-magnifying-glass absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
              </Link>
              <button
                type="button"
                onClick={cart.open}
                className="group relative p-2 text-gray-700 transition-colors hover:text-indigo-600"
                aria-label="Abrir carrinho"
              >
                <i className="fa-solid fa-cart-shopping text-xl transition-transform group-hover:scale-110" />
                {cart.count > 0 ? (
                  <span className="absolute right-0 top-0 -mr-1 -mt-1 flex h-5 w-5 items-center justify-center rounded-full border-2 border-white bg-rose-500 text-[10px] font-bold text-white shadow-sm">
                    {cart.count}
                  </span>
                ) : null}
              </button>
            </div>
          </div>
        </div>
      </header>

      <button
        type="button"
        onClick={cart.close}
        aria-label="Fechar carrinho"
        className={`fixed inset-0 z-50 bg-black/50 transition-opacity duration-300 ${
          cart.isOpen ? "opacity-100" : "pointer-events-none opacity-0"
        }`}
      />
      <aside
        className={`fixed right-0 top-0 z-50 flex h-full w-full transform flex-col bg-white shadow-2xl transition-transform duration-300 ease-in-out sm:w-[400px] ${
          cart.isOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between border-b border-gray-100 bg-white p-4">
          <h2 className="flex items-center gap-2 text-xl font-bold">
            <i className="fa-solid fa-cart-shopping text-indigo-600" /> Seu
            Carrinho ({cart.count})
          </h2>
          <button
            type="button"
            onClick={cart.close}
            className="rounded-full p-2 text-gray-400 transition hover:bg-gray-100 hover:text-gray-600"
            aria-label="Fechar"
          >
            <i className="fa-solid fa-xmark text-lg" />
          </button>
        </div>

        {cart.items.length ? (
          <div className="flex-1 space-y-4 overflow-y-auto p-4">
            {cart.items.map((item) => (
              <div
                key={item.id}
                className="flex gap-4 rounded-xl border border-gray-100 bg-white p-3 shadow-soft"
              >
                <div className="h-20 w-20 flex-shrink-0 overflow-hidden rounded-lg border border-gray-100 bg-gray-50">
                  {item.image ? (
                    <img
                      src={item.image}
                      alt={item.name}
                      className="h-full w-full object-cover"
                    />
                  ) : null}
                </div>
                <div className="flex flex-1 flex-col justify-between">
                  <h3 className="line-clamp-2 text-sm font-semibold">
                    <Link href={`/products/${item.slug}`} onClick={cart.close}>
                      {item.name}
                    </Link>
                  </h3>
                  <div className="mt-2 flex items-center justify-between">
                    <span className="font-bold text-indigo-600">
                      {formatPrice(
                        item.priceAmountMinor,
                        item.priceCurrency,
                        locale,
                      )}
                    </span>
                    <div className="flex items-center gap-2 rounded-lg border border-gray-200 bg-gray-50 p-1">
                      <button
                        type="button"
                        onClick={() => cart.setQty(item.id, item.qty - 1)}
                        className="flex h-6 w-6 items-center justify-center text-gray-500 hover:text-indigo-600"
                        aria-label="Diminuir"
                      >
                        <i className="fa-solid fa-minus text-xs" />
                      </button>
                      <span className="w-4 text-center text-sm font-medium">
                        {item.qty}
                      </span>
                      <button
                        type="button"
                        onClick={() => cart.setQty(item.id, item.qty + 1)}
                        className="flex h-6 w-6 items-center justify-center text-gray-500 hover:text-indigo-600"
                        aria-label="Aumentar"
                      >
                        <i className="fa-solid fa-plus text-xs" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex flex-1 flex-col items-center justify-center gap-4 p-8 text-center">
            <p className="text-sm text-gray-500">Seu carrinho está vazio.</p>
            <Link
              href="/products"
              onClick={cart.close}
              className="rounded-xl bg-indigo-600 px-6 py-3 text-sm font-bold text-white transition-colors hover:bg-indigo-700"
            >
              Ver produtos
            </Link>
          </div>
        )}

        {cart.items.length ? (
          <div className="border-t border-gray-100 bg-gray-50 p-4">
            <div className="mb-4 flex items-center justify-between">
              <span className="text-gray-500">Subtotal</span>
              <span className="text-xl font-bold">
                {formatPrice(
                  cart.subtotalMinor,
                  cart.items[0].priceCurrency,
                  locale,
                )}
              </span>
            </div>
            <Link
              href="/checkout"
              onClick={cart.close}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-indigo-600 py-4 font-bold text-white shadow-float transition-colors hover:bg-indigo-700"
            >
              Finalizar Compra <i className="fa-solid fa-arrow-right" />
            </Link>
          </div>
        ) : null}
      </aside>
    </>
  )
}
