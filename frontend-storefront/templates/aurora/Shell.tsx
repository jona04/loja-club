import Link from "next/link"
import type { ReactNode } from "react"

import type { Category, StorefrontStore } from "@/lib/api"
import { CartProvider } from "@/lib/cart"
import { whatsappLink } from "@/lib/format"

import { AuroraHeader } from "./AuroraHeader"

const FOOTER_PAGES = [
  { slug: "sobre", label: "Sobre a loja" },
  { slug: "privacidade", label: "Política de Privacidade" },
  { slug: "termos", label: "Termos de Uso" },
  { slug: "trocas", label: "Trocas e Devoluções" },
]

/**
 * Aurora chrome (faithful to the template): top announcement bar, sticky header
 * (3 icons + mini-cart drawer), dark footer and the floating WhatsApp button.
 * Wraps the page in the client {@link CartProvider} so "add to cart" works.
 *
 * @param store - The public store identity.
 * @param categories - The store's categories (for the nav and footer).
 * @param locale - The store locale (price formatting in the drawer).
 * @param children - The page content.
 * @returns The wrapped Aurora page.
 */
export function AuroraShell({
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

  return (
    <CartProvider>
      <div className="flex min-h-screen flex-col bg-white text-brand-900 antialiased">
        <div className="bg-brand-900 py-2 text-center text-xs font-medium uppercase tracking-widest text-white">
          Frete grátis em compras acima de R$ 500
        </div>

        <AuroraHeader
          name={name}
          logoUrl={store.logo_url}
          categories={categories}
          locale={locale}
        />

        <main className="flex-1">{children}</main>

        <footer className="border-t border-gray-200 bg-brand-900 pb-8 pt-16 text-white">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="mb-12 grid grid-cols-1 gap-12 border-b border-gray-800 pb-12 md:grid-cols-4">
              <div>
                <Link
                  href="/"
                  className="mb-6 inline-block text-2xl font-semibold tracking-tight text-white"
                >
                  {name}
                </Link>
                <p className="mb-6 text-sm leading-relaxed text-gray-400">
                  {store.description ||
                    "Curadoria de peças atemporais para transformar sua casa em um refúgio de calma e elegância."}
                </p>
                <div className="flex space-x-4">
                  {["instagram", "pinterest", "tiktok"].map((s) => (
                    <Link
                      key={s}
                      href="/pages/sobre"
                      className="text-gray-400 transition-colors hover:text-white"
                      aria-label={s}
                    >
                      <i className={`fa-brands fa-${s} text-xl`} />
                    </Link>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="mb-6 text-sm font-semibold uppercase tracking-wider text-gray-100">
                  Navegue
                </h3>
                <ul className="space-y-4">
                  {categories.slice(0, 4).map((c) => (
                    <li key={c.id}>
                      <Link
                        href={`/categories/${c.slug}`}
                        className="text-sm text-gray-400 transition-colors hover:text-white"
                      >
                        {c.name}
                      </Link>
                    </li>
                  ))}
                  <li>
                    <Link
                      href="/products"
                      className="text-sm text-gray-400 transition-colors hover:text-white"
                    >
                      Todos os produtos
                    </Link>
                  </li>
                </ul>
              </div>

              <div>
                <h3 className="mb-6 text-sm font-semibold uppercase tracking-wider text-gray-100">
                  Institucional
                </h3>
                <ul className="space-y-4">
                  {FOOTER_PAGES.map((item) => (
                    <li key={item.slug}>
                      <Link
                        href={`/pages/${item.slug}`}
                        className="text-sm text-gray-400 transition-colors hover:text-white"
                      >
                        {item.label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h3 className="mb-6 text-sm font-semibold uppercase tracking-wider text-gray-100">
                  Atendimento
                </h3>
                <ul className="space-y-4 text-sm text-gray-400">
                  {store.whatsapp_number ? (
                    <li className="flex items-start">
                      <i className="fa-brands fa-whatsapp mr-3 mt-1 text-white" />
                      <div>
                        <span className="block">WhatsApp</span>
                        <a
                          href={whatsappLink(store.whatsapp_number)}
                          className="transition-colors hover:text-white"
                        >
                          {store.whatsapp_number}
                        </a>
                      </div>
                    </li>
                  ) : null}
                  <li className="flex items-start">
                    <i className="fa-regular fa-envelope mr-3 mt-1 text-white" />
                    <div>
                      <span className="block">E-mail</span>
                      <span>contato@{store.slug}.com.br</span>
                    </div>
                  </li>
                  <li className="mt-4">
                    Horário de atendimento:
                    <br />
                    Seg a Sex, das 9h às 18h.
                  </li>
                </ul>
              </div>
            </div>

            <div className="flex flex-col items-center justify-between text-xs text-gray-500 md:flex-row">
              <p>
                © {new Date().getFullYear()} {name}. Todos os direitos
                reservados.
              </p>
              <span className="mt-4 md:mt-0">Plataforma Loja Club</span>
            </div>
          </div>
        </footer>

        {store.whatsapp_number ? (
          <a
            href={whatsappLink(store.whatsapp_number)}
            target="_blank"
            rel="noreferrer"
            className="group fixed bottom-6 right-6 z-40 flex h-14 w-14 items-center justify-center rounded-full bg-[#25D366] text-white shadow-lg transition-transform duration-300 hover:scale-110"
            aria-label="Fale no WhatsApp"
          >
            <i className="fa-brands fa-whatsapp text-3xl" />
            <span className="pointer-events-none absolute right-16 whitespace-nowrap rounded bg-white px-3 py-2 text-xs font-medium text-gray-800 opacity-0 shadow-md transition-opacity group-hover:opacity-100">
              Fale conosco
            </span>
          </a>
        ) : null}
      </div>
    </CartProvider>
  )
}
