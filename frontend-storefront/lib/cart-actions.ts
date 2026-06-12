"use server"

/**
 * Server Actions for the cart + checkout.
 *
 * The browser cannot reach the backend directly (`NEXT_PUBLIC_API_URL` is the
 * docker-internal host, and the guest cookie is cross-origin). These actions run
 * on the Next server: they forward the store `Host` and the `guest_session_id`
 * cookie to the backend, and re-emit the backend's `Set-Cookie` to the browser
 * (same origin), so the anonymous cart survives across requests.
 */

import { cookies, headers } from "next/headers"

import type { CartPublic, OrderPublic } from "@/lib/api"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8800"
const GUEST_COOKIE = "guest_session_id"
const GUEST_MAX_AGE = 60 * 60 * 24 * 30

/** The checkout submission shape (mirrors the backend `CheckoutInput`). */
export interface CheckoutInput {
  contact: {
    name: string
    email?: string
    phone?: string
    region?: string
  }
  address: {
    recipient_name?: string
    line1: string
    number?: string
    line2?: string
    neighborhood?: string
    city: string
    state?: string
    postal_code?: string
    country: string
  }
  shipping_method_id: string
}

/** Re-emit the backend's guest cookie to the browser (same origin as Next). */
async function persistGuestCookie(res: Response): Promise<void> {
  const headerBag = res.headers as unknown as {
    getSetCookie?: () => string[]
  }
  for (const raw of headerBag.getSetCookie?.() ?? []) {
    const match = raw.match(/guest_session_id=([^;]+)/)
    if (match) {
      const jar = await cookies()
      jar.set(GUEST_COOKIE, match[1], {
        httpOnly: true,
        sameSite: "lax",
        path: "/",
        maxAge: GUEST_MAX_AGE,
      })
    }
  }
}

/** Call the backend forwarding the store host + the guest cookie. */
async function call(path: string, init: RequestInit = {}): Promise<Response> {
  const incoming = await headers()
  const host = incoming.get("x-forwarded-host") ?? incoming.get("host") ?? ""
  const jar = await cookies()
  const guest = jar.get(GUEST_COOKIE)?.value

  const reqHeaders: Record<string, string> = { "x-forwarded-host": host }
  if (guest) {
    reqHeaders.cookie = `${GUEST_COOKIE}=${guest}`
  }
  if (init.body) {
    reqHeaders["content-type"] = "application/json"
  }

  const res = await fetch(`${API_URL}/api/v1${path}`, {
    ...init,
    headers: {
      ...reqHeaders,
      ...((init.headers as Record<string, string>) ?? {}),
    },
    cache: "no-store",
  })
  await persistGuestCookie(res)
  return res
}

/** Parse a JSON response, surfacing the backend's error envelope message. */
async function parse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = (await res.json().catch(() => null)) as {
      error?: { message?: string }
    } | null
    throw new Error(body?.error?.message ?? `Request failed (${res.status})`)
  }
  return (await res.json()) as T
}

/** Get (or start) the guest's cart. */
export async function getCart(): Promise<CartPublic> {
  return parse<CartPublic>(await call("/storefront/cart"))
}

/** Add a product to the cart. */
export async function addToCart(
  productId: string,
  quantity: number,
): Promise<CartPublic> {
  return parse<CartPublic>(
    await call("/storefront/cart/items", {
      method: "POST",
      body: JSON.stringify({ product_id: productId, quantity }),
    }),
  )
}

/** Set a cart line's quantity. */
export async function updateCartItem(
  itemId: string,
  quantity: number,
): Promise<CartPublic> {
  return parse<CartPublic>(
    await call(`/storefront/cart/items/${itemId}`, {
      method: "PATCH",
      body: JSON.stringify({ quantity }),
    }),
  )
}

/** Remove a cart line. */
export async function removeCartItem(itemId: string): Promise<CartPublic> {
  return parse<CartPublic>(
    await call(`/storefront/cart/items/${itemId}`, { method: "DELETE" }),
  )
}

/** Place the order (no login, no gateway) and return the confirmation. */
export async function submitCheckout(
  input: CheckoutInput,
): Promise<OrderPublic> {
  return parse<OrderPublic>(
    await call("/storefront/checkout", {
      method: "POST",
      body: JSON.stringify(input),
    }),
  )
}
