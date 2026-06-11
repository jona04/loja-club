/**
 * Shared contract for storefront templates (`P3-TPL-01`).
 *
 * Every template is a tree of components that consumes the **same data** and
 * leads to the **same flow** — only the composition/look changes. The pages
 * fetch the data and hand it to the resolved template's `Home/Category/Product`.
 */
import type { ReactNode } from "react"

import type {
  Category,
  Paginated,
  StorefrontHome,
  StorefrontProduct,
  StorefrontStore,
} from "@/lib/api"

/** Props for a template's home (store identity, theme, highlights, categories). */
export interface HomeProps {
  home: StorefrontHome
  categories: Category[]
}

/** Props for a template's category listing. */
export interface CategoryProps {
  home: StorefrontHome
  categories: Category[]
  category: Category | null
  products: Paginated<StorefrontProduct>
}

/** Props for a template's product detail. */
export interface ProductProps {
  home: StorefrontHome
  categories: Category[]
  product: StorefrontProduct
}

/** Props for a template's chrome — used by the standalone pages (checkout, …). */
export interface ShellProps {
  store: StorefrontStore
  categories: Category[]
  locale: string
  children: ReactNode
}

/** A template's component tree (one per template id). */
export interface Template {
  Home: (props: HomeProps) => ReactNode
  Category: (props: CategoryProps) => ReactNode
  Product: (props: ProductProps) => ReactNode
  Shell: (props: ShellProps) => ReactNode | Promise<ReactNode>
}
