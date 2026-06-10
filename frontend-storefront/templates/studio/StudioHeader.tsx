"use client"

import Link from "next/link"

import { useCart } from "@/lib/cart"
import { formatPrice } from "@/lib/format"

/**
 * Studio topbar (faithful to the template): logo, centered search and the cart
 * button (with a count badge), plus the slide-over mini-cart drawer. Clean
 * black/white catalog look.
 *
 * @param name - The store display name.
 * @param locale - Store locale for price formatting.
 * @returns The topbar and cart drawer.
 */
export function StudioHeader({
  name,
  locale,
}: {
  name: string
  locale: string
}) {
  const cart = useCart()

  return (
    <>
      <header className="sticky top-0 z-40 flex h-16 w-full items-center justify-between border-b border-gray-200 bg-white px-4 lg:px-8">
        <div className="flex items-center gap-4">
          <Link
            href="/products"
            className="text-gray-600 hover:text-black lg:hidden"
            aria-label="Menu"
          >
            <i className="fa-solid fa-bars text-xl" />
          </Link>
          <Link
            href="/"
            className="flex items-center gap-2 text-xl font-bold tracking-tight text-black"
          >
            <i className="fa-solid fa-shapes" />
            {name}
          </Link>
        </div>

        <Link
          href="/products"
          className="relative mx-8 hidden max-w-xl flex-1 md:flex"
          aria-label="Buscar"
        >
          <span className="h-10 w-full rounded-md border border-gray-300 bg-gray-50 pl-10 pr-4 pt-2.5 text-sm text-gray-400">
            Buscar produtos, categorias...
          </span>
          <i className="fa-solid fa-magnifying-glass absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
        </Link>

        <div className="flex items-center gap-5">
          <Link
            href="/products"
            className="text-gray-600 hover:text-black md:hidden"
            aria-label="Buscar"
          >
            <i className="fa-solid fa-magnifying-glass text-lg" />
          </Link>
          <button
            type="button"
            onClick={cart.open}
            className="relative text-gray-600 transition-colors hover:text-black"
            aria-label="Abrir carrinho"
          >
            <i className="fa-solid fa-bag-shopping text-xl" />
            {cart.count > 0 ? (
              <span className="absolute -right-2 -top-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-black text-[10px] font-bold text-white">
                {cart.count}
              </span>
            ) : null}
          </button>
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
        className={`fixed right-0 top-0 z-50 flex h-full w-full transform flex-col bg-white shadow-2xl transition-transform duration-300 ease-in-out sm:w-96 ${
          cart.isOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-black">
            Carrinho ({cart.count})
          </h2>
          <button
            type="button"
            onClick={cart.close}
            className="text-gray-400 transition-colors hover:text-black"
            aria-label="Fechar"
          >
            <i className="fa-solid fa-xmark text-xl" />
          </button>
        </div>

        {cart.items.length ? (
          <div className="flex-1 space-y-4 overflow-y-auto p-6">
            {cart.items.map((item) => (
              <div key={item.id} className="flex gap-4">
                <div className="h-20 w-16 flex-shrink-0 overflow-hidden rounded-md bg-gray-50">
                  {item.image ? (
                    <img
                      src={item.image}
                      alt={item.name}
                      className="h-full w-full object-contain mix-blend-multiply p-1"
                    />
                  ) : null}
                </div>
                <div className="flex flex-1 flex-col justify-between">
                  <div className="flex justify-between text-sm">
                    <h3 className="font-medium text-gray-900">
                      <Link
                        href={`/products/${item.slug}`}
                        onClick={cart.close}
                      >
                        {item.name}
                      </Link>
                    </h3>
                    <span className="ml-4 font-bold text-black">
                      {formatPrice(
                        item.priceAmountMinor,
                        item.priceCurrency,
                        locale,
                      )}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center rounded-md border border-gray-200">
                      <button
                        type="button"
                        onClick={() => cart.setQty(item.id, item.qty - 1)}
                        className="px-2 py-1 text-gray-500 hover:text-black"
                        aria-label="Diminuir"
                      >
                        -
                      </button>
                      <span className="px-2 py-1 text-gray-700">
                        {item.qty}
                      </span>
                      <button
                        type="button"
                        onClick={() => cart.setQty(item.id, item.qty + 1)}
                        className="px-2 py-1 text-gray-500 hover:text-black"
                        aria-label="Aumentar"
                      >
                        +
                      </button>
                    </div>
                    <button
                      type="button"
                      onClick={() => cart.remove(item.id)}
                      className="text-xs text-gray-400 underline hover:text-red-500"
                    >
                      Remover
                    </button>
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
              className="rounded-md bg-black px-6 py-3 text-sm font-medium text-white"
            >
              Ver produtos
            </Link>
          </div>
        )}

        {cart.items.length ? (
          <div className="border-t border-gray-200 p-6">
            <div className="mb-4 flex justify-between text-base font-bold text-black">
              <span>Subtotal</span>
              <span>
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
              className="flex w-full items-center justify-center rounded-md bg-black px-6 py-4 text-sm font-medium text-white transition-colors hover:bg-gray-800"
            >
              Finalizar compra
            </Link>
          </div>
        ) : null}
      </aside>
    </>
  )
}
