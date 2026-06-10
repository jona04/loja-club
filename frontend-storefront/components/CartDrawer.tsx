"use client"

import Link from "next/link"
import { useState } from "react"

/**
 * Header cart button + slide-over mini-cart drawer (shared by the templates).
 *
 * The cart logic is Fase 4 — for now the drawer shows the empty state. Client
 * component: it only holds the open/close state.
 *
 * @returns The cart icon button and (when open) the mini-cart drawer.
 */
export function CartButton() {
  const [open, setOpen] = useState(false)

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        aria-label="Abrir carrinho"
        className="grid h-9 w-9 place-items-center rounded-full text-gray-700 transition hover:bg-gray-100"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth={1.6}
          stroke="currentColor"
          className="h-5 w-5"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M2.25 3h1.386c.51 0 .955.343 1.087.835l.383 1.437M7.5 14.25a3 3 0 0 0-3 3h15.75m-12.75-3h11.218c1.121-2.3 2.1-4.684 2.924-7.138a60.114 60.114 0 0 0-16.536-1.84M7.5 14.25 5.106 5.272M6 20.25a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0Zm12.75 0a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0Z"
          />
        </svg>
      </button>

      {open ? (
        <div className="fixed inset-0 z-50">
          <button
            type="button"
            aria-label="Fechar carrinho"
            onClick={() => setOpen(false)}
            className="absolute inset-0 bg-black/40"
          />
          <aside className="absolute inset-y-0 right-0 flex w-full max-w-sm flex-col bg-white shadow-2xl">
            <div className="flex items-center justify-between border-b border-gray-100 px-5 py-4">
              <h2 className="text-sm font-semibold tracking-wider text-gray-900 uppercase">
                Seu carrinho
              </h2>
              <button
                type="button"
                onClick={() => setOpen(false)}
                aria-label="Fechar"
                className="text-gray-400 transition hover:text-gray-900"
              >
                ✕
              </button>
            </div>
            <div className="flex flex-1 flex-col items-center justify-center gap-4 p-8 text-center">
              <p className="text-sm text-gray-500">Seu carrinho está vazio.</p>
              <Link
                href="/products"
                onClick={() => setOpen(false)}
                className="inline-flex rounded-sm px-6 py-3 text-sm font-medium text-white transition"
                style={{ backgroundColor: "var(--primary)" }}
              >
                Ver produtos
              </Link>
            </div>
          </aside>
        </div>
      ) : null}
    </>
  )
}
