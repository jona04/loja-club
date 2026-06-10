/**
 * Server-side client for the public storefront API (`P3-SF-01`).
 *
 * SSR reads the incoming store host and forwards it as `X-Forwarded-Host` so the
 * backend resolves the right store. A 404 (unknown/unpublished host, or missing
 * resource) triggers Next's `notFound()` → the "loja não encontrada" page.
 */
import { headers } from "next/headers"
import { notFound } from "next/navigation"

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
}

export interface StorefrontTheme {
  active_template_id: string
  banner_image_url: string | null
  headline: string | null
  featured_collection_id: string | null
  primary_color: string | null
  background_color: string | null
  font_family: string | null
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

export interface StorefrontHome {
  store: StorefrontStore
  theme: StorefrontTheme
  featured_products: StorefrontProduct[]
}

export interface Category {
  id: string
  name: string
  slug: string
  description: string | null
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

/** Fetch the host's storefront home (store identity, theme and highlights). */
export const getHome = (): Promise<StorefrontHome> =>
  apiGet<StorefrontHome>("/home")

/** Fetch the host store's categories. */
export const getCategories = (): Promise<Category[]> =>
  apiGet<Category[]>("/categories")

/** Fetch a published product by slug. */
export const getProduct = (slug: string): Promise<StorefrontProduct> =>
  apiGet<StorefrontProduct>(`/products/${encodeURIComponent(slug)}`)

/** List published products, optionally filtered by a category slug. */
export const listProducts = (
  category?: string,
): Promise<Paginated<StorefrontProduct>> =>
  apiGet<Paginated<StorefrontProduct>>(
    category
      ? `/products?category=${encodeURIComponent(category)}`
      : "/products",
  )

export { formatPrice, whatsappLink } from "@/lib/format"
