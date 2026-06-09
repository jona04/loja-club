import Link from "next/link"
import type { CSSProperties, ReactNode } from "react"

import { WhatsAppButton } from "@/components/WhatsAppButton"
import type { Category, StorefrontStore, StorefrontTheme } from "@/lib/api"

/**
 * Shared storefront chrome: sticky header (logo/name + category nav), footer and
 * the floating WhatsApp button. Applies the active theme's colours via the
 * `--primary` CSS variable and the background/font.
 *
 * @param store - The public store identity.
 * @param theme - The active theme/appearance.
 * @param categories - Categories for the nav.
 * @param children - The page content.
 * @returns The wrapped page.
 */
export function StoreShell({
  store,
  theme,
  categories,
  children,
}: {
  store: StorefrontStore
  theme: StorefrontTheme
  categories: Category[]
  children: ReactNode
}) {
  const name = store.public_name || store.name
  const rootStyle = {
    "--primary": theme.primary_color || "#111827",
    backgroundColor: theme.background_color || "#ffffff",
    fontFamily: theme.font_family || undefined,
  } as CSSProperties

  return (
    <div
      className="flex min-h-screen flex-col"
      data-template={theme.active_template_id}
      style={rootStyle}
    >
      <header className="sticky top-0 z-40 border-b border-gray-100 bg-white/90 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-6xl items-center gap-6 px-4">
          <Link href="/" className="flex shrink-0 items-center gap-2.5">
            {store.logo_url ? (
              <img
                src={store.logo_url}
                alt={name}
                className="h-9 w-9 rounded-full object-cover"
              />
            ) : (
              <span
                className="grid h-9 w-9 place-items-center rounded-full text-sm font-bold text-white"
                style={{ backgroundColor: "var(--primary)" }}
              >
                {name.charAt(0).toUpperCase()}
              </span>
            )}
            <span className="text-lg font-semibold tracking-tight text-gray-900">
              {name}
            </span>
          </Link>
          <nav className="ml-auto hidden items-center gap-1 sm:flex">
            <Link
              href="/products"
              className="rounded-full px-3 py-1.5 text-sm font-medium text-gray-600 transition hover:bg-gray-100 hover:text-gray-900"
            >
              Produtos
            </Link>
            {categories.slice(0, 5).map((category) => (
              <Link
                key={category.id}
                href={`/categories/${category.slug}`}
                className="rounded-full px-3 py-1.5 text-sm font-medium text-gray-600 transition hover:bg-gray-100 hover:text-gray-900"
              >
                {category.name}
              </Link>
            ))}
          </nav>
        </div>
      </header>

      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8 sm:py-10">
        {children}
      </main>

      <footer className="mt-16 border-t border-gray-100 bg-gray-50">
        <div className="mx-auto max-w-6xl px-4 py-10">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <p className="text-base font-semibold text-gray-900">{name}</p>
              {store.description ? (
                <p className="mt-1 max-w-md text-sm text-gray-500">
                  {store.description}
                </p>
              ) : null}
            </div>
            {store.whatsapp_number ? (
              <p className="text-sm text-gray-500">
                WhatsApp:{" "}
                <span className="font-medium text-gray-700">
                  {store.whatsapp_number}
                </span>
              </p>
            ) : null}
          </div>
          <p className="mt-8 text-xs text-gray-400">
            © {new Date().getFullYear()} {name}. Feito com Loja Club.
          </p>
        </div>
      </footer>

      <WhatsAppButton phone={store.whatsapp_number} />
    </div>
  )
}
