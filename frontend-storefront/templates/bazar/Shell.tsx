import Link from "next/link"
import type { CSSProperties, ReactNode } from "react"

import type { Category, StorefrontStore } from "@/lib/api"
import { CartProvider } from "@/lib/cart"
import { whatsappLink } from "@/lib/format"

import { BazarHeader } from "./BazarHeader"

const HELP_LINKS = [
  { slug: "como-comprar", label: "Como comprar" },
  { slug: "entregas", label: "Prazos e Entregas" },
  { slug: "trocas", label: "Trocas e Devoluções" },
  { slug: "faq", label: "Perguntas Frequentes" },
  { slug: "contato", label: "Fale Conosco" },
]

/**
 * Bazar chrome (faithful to the template): promo header, vibrant cart drawer,
 * dark footer with departments/help/contact columns and the green WhatsApp
 * button. Wraps the page in the client {@link CartProvider}. Uses Plus Jakarta
 * Sans (loaded in the root layout as `--font-jakarta`).
 *
 * @param store - The public store identity.
 * @param categories - The store's categories (nav and footer).
 * @param locale - The store locale (price formatting in the drawer).
 * @param children - The page content.
 * @returns The wrapped Bazar page.
 */
export function BazarShell({
  store,
  categories,
  locale,
  children,
}: {
  store: StorefrontStore
  categories: Category[]
  locale: string
  children: ReactNode
}) {
  const name = store.public_name || store.name
  const rootStyle = {
    fontFamily: "var(--font-jakarta), sans-serif",
  } as CSSProperties

  return (
    <CartProvider>
      <div
        className="flex min-h-screen flex-col bg-gray-50 text-gray-900 antialiased"
        style={rootStyle}
      >
        <BazarHeader name={name} categories={categories} locale={locale} />

        <main className="flex-1">{children}</main>

        <footer className="border-t border-gray-800 bg-gray-900 pb-8 pt-16 text-gray-300">
          <div className="mx-auto max-w-[1400px] px-4 sm:px-6 lg:px-8">
            <div className="mb-12 grid grid-cols-1 gap-12 md:grid-cols-2 lg:grid-cols-4 lg:gap-8">
              <div className="text-center md:text-left">
                <Link
                  href="/"
                  className="mb-6 flex items-center justify-center gap-2 md:justify-start"
                >
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500 text-xl font-bold text-white">
                    <i className="fa-solid fa-bolt" />
                  </div>
                  <span className="text-2xl font-bold tracking-tight text-white">
                    {name}
                  </span>
                </Link>
                <p className="mb-6 text-sm leading-relaxed text-gray-400">
                  {store.description ||
                    "Sua loja de confiança com os melhores produtos, preços imbatíveis e o atendimento que você merece."}
                </p>
                <div className="flex items-center justify-center gap-4 md:justify-start">
                  {["instagram", "facebook-f", "tiktok"].map((s) => (
                    <Link
                      key={s}
                      href="/pages/sobre"
                      className="flex h-10 w-10 items-center justify-center rounded-full bg-gray-800 transition-colors hover:bg-indigo-500 hover:text-white"
                      aria-label={s}
                    >
                      <i className={`fa-brands fa-${s}`} />
                    </Link>
                  ))}
                </div>
              </div>

              <div className="text-center md:text-left">
                <h4 className="mb-6 text-sm font-bold uppercase tracking-wider text-white">
                  Departamentos
                </h4>
                <ul className="space-y-3">
                  {categories.slice(0, 5).map((c) => (
                    <li key={c.id}>
                      <Link
                        href={`/categories/${c.slug}`}
                        className="transition-colors hover:text-indigo-400"
                      >
                        {c.name}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="text-center md:text-left">
                <h4 className="mb-6 text-sm font-bold uppercase tracking-wider text-white">
                  Ajuda &amp; Suporte
                </h4>
                <ul className="space-y-3">
                  {HELP_LINKS.map((item) => (
                    <li key={item.slug}>
                      <Link
                        href={`/pages/${item.slug}`}
                        className="transition-colors hover:text-indigo-400"
                      >
                        {item.label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="rounded-2xl border border-gray-700/50 bg-gray-800/50 p-6 text-center md:text-left">
                <h4 className="mb-4 text-lg font-bold text-white">
                  Atendimento
                </h4>
                <p className="mb-6 text-sm text-gray-400">
                  Estamos aqui para ajudar com suas dúvidas e pedidos.
                </p>
                {store.whatsapp_number ? (
                  <a
                    href={whatsappLink(store.whatsapp_number)}
                    className="mb-4 flex items-center justify-center gap-3 rounded-xl bg-green-500 px-4 py-3 font-bold text-white transition-colors hover:bg-green-600 md:justify-start"
                  >
                    <i className="fa-brands fa-whatsapp text-xl" />{" "}
                    {store.whatsapp_number}
                  </a>
                ) : null}
                <p className="text-xs text-gray-500">
                  <i className="fa-regular fa-envelope mr-1" /> contato@
                  {store.slug}.com.br
                </p>
              </div>
            </div>

            <div className="flex flex-col items-center justify-between gap-4 border-t border-gray-800 pt-8 md:flex-row">
              <p className="text-center text-sm text-gray-500 md:text-left">
                © {new Date().getFullYear()} {name}. Todos os direitos
                reservados. Plataforma Loja Club.
              </p>
              <div className="flex items-center gap-4 text-2xl text-gray-600">
                <i className="fa-brands fa-cc-visa" />
                <i className="fa-brands fa-cc-mastercard" />
                <i className="fa-brands fa-pix" />
              </div>
            </div>
          </div>
        </footer>

        {store.whatsapp_number ? (
          <a
            href={whatsappLink(store.whatsapp_number)}
            target="_blank"
            rel="noreferrer"
            className="fixed bottom-6 right-6 z-40 flex h-14 w-14 items-center justify-center rounded-full bg-green-500 text-3xl text-white shadow-float transition-all hover:scale-110 hover:bg-green-600"
            aria-label="Fale no WhatsApp"
          >
            <i className="fa-brands fa-whatsapp" />
          </a>
        ) : null}
      </div>
    </CartProvider>
  )
}
