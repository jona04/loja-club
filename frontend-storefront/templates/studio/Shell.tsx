import Link from "next/link"
import type { ReactNode } from "react"

import { type Category, getHome, type StorefrontStore } from "@/lib/api"
import { CartProvider } from "@/lib/cart"
import { whatsappLink } from "@/lib/format"

import { StudioHeader } from "./StudioHeader"

/**
 * Studio chrome (faithful to the template): a slim topbar with search and cart,
 * the mini-cart drawer, the page content (the browsing pages add the catalog
 * sidebar) and a minimal footer. Clean black/white catalog look (Inter font).
 *
 * @param store - The public store identity.
 * @param categories - The store's categories.
 * @param locale - The store locale (price formatting in the drawer).
 * @param children - The page content.
 * @returns The wrapped Studio page.
 */
export async function StudioShell({
  store,
  categories: _categories,
  locale,
  children,
}: {
  store: StorefrontStore
  categories: Category[]
  locale: string
  children: ReactNode
}) {
  const name = store.public_name || store.name
  const { theme } = await getHome()
  const settings = theme.settings ?? {}
  const announcement = (settings.announcement_text as string) || ""
  const footerContact = (settings.footer_contact as string) || ""

  return (
    <CartProvider>
      <div className="flex min-h-screen flex-col bg-white text-gray-900 antialiased">
        {announcement ? (
          <div className="bg-black py-2 text-center text-xs font-medium tracking-wide text-white">
            {announcement}
          </div>
        ) : null}
        <StudioHeader name={name} locale={locale} />

        <main className="flex flex-1 flex-col">{children}</main>

        <footer className="border-t border-gray-200 bg-white py-8">
          <div className="mx-auto flex max-w-[1600px] flex-col items-center justify-between gap-3 px-4 text-xs text-gray-500 sm:flex-row lg:px-8">
            <p>
              © {new Date().getFullYear()} {name}. Plataforma Loja Club.
            </p>
            {footerContact ? (
              <p className="whitespace-pre-line text-center">{footerContact}</p>
            ) : null}
            <div className="flex gap-5">
              <Link href="/pages/sobre" className="hover:text-black">
                Sobre
              </Link>
              <Link href="/pages/privacidade" className="hover:text-black">
                Privacidade
              </Link>
              <Link href="/pages/termos" className="hover:text-black">
                Termos
              </Link>
            </div>
          </div>
        </footer>

        {store.whatsapp_number ? (
          <a
            href={whatsappLink(store.whatsapp_number)}
            target="_blank"
            rel="noreferrer"
            className="fixed bottom-6 right-6 z-40 flex h-12 w-12 items-center justify-center rounded-full bg-black text-2xl text-white shadow-lg transition-transform hover:scale-110"
            aria-label="Fale no WhatsApp"
          >
            <i className="fa-brands fa-whatsapp" />
          </a>
        ) : null}
      </div>
    </CartProvider>
  )
}
