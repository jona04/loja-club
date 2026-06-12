/**
 * Server-side client for the public storefront API (`P3-SF-01`).
 *
 * SSR reads the incoming store host and forwards it as `X-Forwarded-Host` so the
 * backend resolves the right store. A 404 (unknown/unpublished host, or missing
 * resource) triggers Next's `notFound()` → the "loja não encontrada" page.
 */
import { headers } from "next/headers"
import { notFound } from "next/navigation"
import { cache } from "react"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8800"

export interface StorefrontStore {
  name: string
  slug: string
  currency: string
  locale: string
  public_name: string | null
  description: string | null
  logo_url: string | null
  whatsapp_number: string | null
  return_policy: string | null
  exchange_policy: string | null
  privacy_policy: string | null
}

export interface CartItemPublic {
  id: string
  product_id: string
  variant_id: string | null
  name: string
  slug: string
  image_url: string | null
  quantity: number
  unit_price_amount_minor: number
  unit_price_currency: string
  line_total_amount_minor: number
}

export interface CartPublic {
  id: string
  currency: string
  item_count: number
  subtotal_amount_minor: number
  items: CartItemPublic[]
}

export interface ShippingMethodPublic {
  id: string
  type: string
  name: string
  description: string | null
  is_active: boolean
  price_amount_minor: number | null
  min_order_amount_minor: number | null
}

export interface OrderItemPublic {
  id: string
  product_id: string
  variant_id: string | null
  name: string
  quantity: number
  unit_price_amount_minor: number
  unit_price_currency: string
  line_total_amount_minor: number
}

export interface OrderPublic {
  id: string
  order_number: number
  status: string
  currency: string
  subtotal_amount_minor: number
  shipping_amount_minor: number
  discount_amount_minor: number
  total_amount_minor: number
  shipping_method_type: string | null
  shipping_method_name: string | null
  items: OrderItemPublic[]
}

export interface StorefrontTheme {
  active_template_id: string
  banner_image_url: string | null
  headline: string | null
  featured_collection_id: string | null
  primary_color: string | null
  background_color: string | null
  font_family: string | null
  settings: Record<string, unknown>
}

export interface ProductImage {
  url: string
}

export interface StorefrontProduct {
  id: string
  slug: string
  name: string
  description: string | null
  price_amount_minor: number
  price_currency: string
  is_featured: boolean
  images: ProductImage[]
}

export interface StorefrontCategorySection {
  category: Category
  products: StorefrontProduct[]
}

export interface StorefrontHome {
  store: StorefrontStore
  theme: StorefrontTheme
  featured_products: StorefrontProduct[]
  category_sections: StorefrontCategorySection[]
}

export interface Category {
  id: string
  name: string
  slug: string
  description: string | null
}

export interface ContentPage {
  id: string
  slug: string
  title: string
  body: string | null
  is_published: boolean
}

export interface Paginated<T> {
  data: T[]
  count: number
}

async function apiGet<T>(path: string): Promise<T> {
  const incoming = await headers()
  const host = incoming.get("x-forwarded-host") ?? incoming.get("host") ?? ""
  // No Next-level cache: it keys by URL and would leak across store hosts.
  // Caching is the backend's job (per-store Redis, doc 13).
  const res = await fetch(`${API_URL}/api/v1/storefront${path}`, {
    headers: { "x-forwarded-host": host },
    cache: "no-store",
  })
  if (res.status === 404) {
    notFound()
  }
  if (!res.ok) {
    throw new Error(`Storefront API ${res.status} for ${path}`)
  }
  return (await res.json()) as T
}

/**
 * Fetch the host's storefront home (store identity, theme and highlights).
 *
 * Memoized per request (React `cache`) so the page and the template chrome
 * (which reads `theme.settings`) share a single backend call.
 */
export const getHome = cache(
  (): Promise<StorefrontHome> => apiGet<StorefrontHome>("/home"),
)

/** Fetch the host store's categories. */
export const getCategories = (): Promise<Category[]> =>
  apiGet<Category[]>("/categories")

/** Fetch a published product by slug. */
export const getProduct = (slug: string): Promise<StorefrontProduct> =>
  apiGet<StorefrontProduct>(`/products/${encodeURIComponent(slug)}`)

/**
 * Fetch a published editorial page by slug, or `null` when the store has none.
 *
 * Unlike the other reads, a 404 here is expected (the merchant may not have
 * written this page), so it returns `null` to let the caller fall back to the
 * default copy instead of triggering `notFound()`.
 */
export const getPage = async (slug: string): Promise<ContentPage | null> => {
  const incoming = await headers()
  const host = incoming.get("x-forwarded-host") ?? incoming.get("host") ?? ""
  const res = await fetch(
    `${API_URL}/api/v1/storefront/pages/${encodeURIComponent(slug)}`,
    { headers: { "x-forwarded-host": host }, cache: "no-store" },
  )
  if (res.status === 404) {
    return null
  }
  if (!res.ok) {
    throw new Error(`Storefront API ${res.status} for /pages/${slug}`)
  }
  return (await res.json()) as ContentPage
}

/** List published products, optionally filtered by a category slug. */
export const listProducts = (
  category?: string,
): Promise<Paginated<StorefrontProduct>> =>
  apiGet<Paginated<StorefrontProduct>>(
    category
      ? `/products?category=${encodeURIComponent(category)}`
      : "/products",
  )

/** Fetch the host store's active shipping methods (for the checkout). */
export const getShippingMethods = (): Promise<ShippingMethodPublic[]> =>
  apiGet<ShippingMethodPublic[]>("/shipping-methods")

export { formatPrice, whatsappLink } from "@/lib/format"
