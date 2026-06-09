import Link from "next/link"
import type { ReactNode } from "react"
import { WhatsAppButton } from "@/components/WhatsAppButton"
import type { Category, StorefrontStore, StorefrontTheme } from "@/lib/api"

/**
 * Shared storefront chrome: header (logo/name + nav), footer and the floating
 * WhatsApp button. Applies the active theme's colours; the `data-template`
 * attribute lets templates tweak styling.
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
  return (
    <div
      className="flex min-h-screen flex-col"
      data-template={theme.active_template_id}
      style={
        theme.background_color
          ? { backgroundColor: theme.background_color }
          : undefined
      }
    >
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto flex max-w-5xl items-center gap-4 px-4 py-3">
          <Link
            href="/"
            className="flex items-center gap-2 font-semibold"
            style={
              theme.primary_color ? { color: theme.primary_color } : undefined
            }
          >
            {store.logo_url ? (
              <img
                src={store.logo_url}
                alt={name}
                className="h-8 w-8 rounded object-cover"
              />
            ) : null}
            <span>{name}</span>
          </Link>
          <nav className="ml-auto flex flex-wrap gap-4 text-sm text-gray-600">
            <Link href="/products" className="hover:text-gray-900">
              Produtos
            </Link>
            {categories.slice(0, 5).map((category) => (
              <Link
                key={category.id}
                href={`/categories/${category.slug}`}
                className="hover:text-gray-900"
              >
                {category.name}
              </Link>
            ))}
          </nav>
        </div>
      </header>
      <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-6">
        {children}
      </main>
      <footer className="border-t border-gray-200 bg-white py-4 text-center text-sm text-gray-500">
        {name}
      </footer>
      <WhatsAppButton phone={store.whatsapp_number} />
    </div>
  )
}
