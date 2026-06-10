"use client"

import Link from "next/link"
import type { Category } from "@/lib/api"
import { useCart } from "@/lib/cart"
import { formatPrice } from "@/lib/format"

/**
 * Aurora header (faithful to the template): mobile menu button, centered logo,
 * category nav and the 3 icons (search / account / cart with a count badge),
 * plus the slide-over mini-cart drawer driven by the client cart.
 *
 * @param name - The store display name (logo text).
 * @param logoUrl - Optional logo image URL.
 * @param categories - Categories for the nav.
 * @param locale - Store locale for price formatting.
 * @returns The header and cart drawer.
 */
export function AuroraHeader({
  name,
  logoUrl,
  categories,
  locale,
}: {
  name: string
  logoUrl: string | null
  categories: Category[]
  locale: string
}) {
  const cart = useCart()

  return (
    <>
      <header className="sticky top-0 z-40 border-b border-gray-100 bg-white/95 backdrop-blur-sm">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-20 items-center justify-between">
            <Link
              href="/products"
              className="-ml-2 p-2 text-gray-500 hover:text-brand-900 md:hidden"
              aria-label="Menu"
            >
              <i className="fa-solid fa-bars text-xl" />
            </Link>

            <div className="absolute left-1/2 flex flex-shrink-0 -translate-x-1/2 items-center justify-center md:relative md:left-0 md:translate-x-0">
              <Link
                href="/"
                className="flex items-center gap-2 text-2xl font-semibold tracking-tight text-brand-900"
              >
                {logoUrl ? (
                  <img
                    src={logoUrl}
                    alt={name}
                    className="h-9 w-9 rounded-full object-cover"
                  />
                ) : null}
                {name}
              </Link>
            </div>

            <nav className="absolute left-1/2 hidden -translate-x-1/2 space-x-8 md:flex">
              {categories.slice(0, 5).map((c) => (
                <Link
                  key={c.id}
                  href={`/categories/${c.slug}`}
                  className="text-sm font-medium text-gray-600 transition-colors hover:text-brand-900"
                >
                  {c.name}
                </Link>
              ))}
              <Link
                href="/products"
                className="text-sm font-medium text-gray-600 transition-colors hover:text-brand-900"
              >
                Todas as categorias
              </Link>
            </nav>

            <div className="flex items-center space-x-4 md:space-x-6">
              <Link
                href="/products"
                className="hidden text-gray-500 transition-colors hover:text-brand-900 sm:block"
                aria-label="Buscar"
              >
                <i className="fa-solid fa-magnifying-glass text-lg" />
              </Link>
              <Link
                href="/account"
                className="text-gray-500 transition-colors hover:text-brand-900"
                aria-label="Minha conta"
              >
                <i className="fa-regular fa-user text-lg" />
              </Link>
              <button
                type="button"
                onClick={cart.open}
                className="relative text-gray-500 transition-colors hover:text-brand-900"
                aria-label="Abrir carrinho"
              >
                <i className="fa-solid fa-bag-shopping text-lg" />
                {cart.count > 0 ? (
                  <span className="absolute -right-2 -top-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-brand-900 text-[10px] font-bold text-white">
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
        className={`fixed inset-0 z-50 bg-black/30 transition-opacity duration-300 ${
          cart.isOpen ? "opacity-100" : "pointer-events-none opacity-0"
        }`}
      />
      <aside
        className={`fixed right-0 top-0 z-50 flex h-full w-full transform flex-col bg-white shadow-2xl transition-transform duration-300 ease-in-out sm:w-96 ${
          cart.isOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between border-b border-gray-100 px-6 py-4">
          <h2 className="text-lg font-semibold text-brand-900">Seu Carrinho</h2>
          <button
            type="button"
            onClick={cart.close}
            className="-mr-2 p-2 text-gray-400 transition-colors hover:text-gray-600"
            aria-label="Fechar"
          >
            <i className="fa-solid fa-xmark text-xl" />
          </button>
        </div>

        {cart.items.length ? (
          <div className="flex-1 space-y-6 overflow-y-auto p-6">
            {cart.items.map((item) => (
              <div key={item.id} className="flex gap-4">
                <div className="h-24 w-20 flex-shrink-0 overflow-hidden rounded-sm bg-gray-50">
                  {item.image ? (
                    <img
                      src={item.image}
                      alt={item.name}
                      className="h-full w-full object-cover object-center"
                    />
                  ) : null}
                </div>
                <div className="flex flex-1 flex-col justify-between">
                  <div>
                    <div className="flex justify-between text-sm font-medium text-brand-900">
                      <h3>
                        <Link
                          href={`/products/${item.slug}`}
                          onClick={cart.close}
                        >
                          {item.name}
                        </Link>
                      </h3>
                      <p className="ml-4">
                        {formatPrice(
                          item.priceAmountMinor,
                          item.priceCurrency,
                          locale,
                        )}
                      </p>
                    </div>
                    {item.subtitle ? (
                      <p className="mt-1 text-sm text-gray-500">
                        {item.subtitle}
                      </p>
                    ) : null}
                  </div>
                  <div className="flex flex-1 items-end justify-between text-sm">
                    <div className="flex items-center rounded-sm border border-gray-200">
                      <button
                        type="button"
                        onClick={() => cart.setQty(item.id, item.qty - 1)}
                        className="px-2 py-1 text-gray-500 hover:text-brand-900"
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
                        className="px-2 py-1 text-gray-500 hover:text-brand-900"
                        aria-label="Aumentar"
                      >
                        +
                      </button>
                    </div>
                    <button
                      type="button"
                      onClick={() => cart.remove(item.id)}
                      className="text-xs font-medium text-gray-400 underline hover:text-red-500"
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
              className="rounded-sm bg-brand-900 px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-black"
            >
              Ver produtos
            </Link>
          </div>
        )}

        {cart.items.length ? (
          <div className="border-t border-gray-100 bg-gray-50 p-6">
            <div className="mb-4 flex justify-between text-base font-medium text-brand-900">
              <p>Subtotal</p>
              <p>
                {formatPrice(
                  cart.subtotalMinor,
                  cart.items[0].priceCurrency,
                  locale,
                )}
              </p>
            </div>
            <p className="mb-6 text-sm text-gray-500">
              Frete calculado na próxima etapa.
            </p>
            <Link
              href="/checkout"
              onClick={cart.close}
              className="flex w-full items-center justify-center rounded-sm border border-transparent bg-brand-900 px-6 py-4 text-base font-medium text-white shadow-sm transition-colors hover:bg-black"
            >
              Finalizar compra
            </Link>
          </div>
        ) : null}
      </aside>
    </>
  )
}
