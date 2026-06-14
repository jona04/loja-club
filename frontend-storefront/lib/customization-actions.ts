"use server"

/**
 * Server Actions for the 3D customization editor (P7-EDITOR-01/02).
 *
 * Like the cart, the browser cannot reach the backend directly (the API host is
 * docker-internal and the guest cookie is cross-origin). These run on the Next
 * server, forwarding the store `Host` + `guest_session_id` cookie and re-emitting
 * the backend's `Set-Cookie`, so the session is owned by the same guest browser.
 */

import { cookies, headers } from "next/headers"

import type {
  CustomizationSession,
  CustomizationState,
  UploadPublic,
} from "@/lib/customizer/session-types"

export type {
  CustomizationSession,
  CustomizationState,
  PrintableArea,
  SessionVersion,
  UploadPublic,
  UvRect,
} from "@/lib/customizer/session-types"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8800"
const GUEST_COOKIE = "guest_session_id"
const GUEST_MAX_AGE = 60 * 60 * 24 * 30

/** Re-emit the backend's guest cookie to the browser (same origin as Next). */
async function persistGuestCookie(res: Response): Promise<void> {
  const headerBag = res.headers as unknown as { getSetCookie?: () => string[] }
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
  // Only set JSON for string bodies; FormData must keep its multipart boundary.
  if (typeof init.body === "string") {
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
      error?: { code?: string; message?: string }
    } | null
    const err = new Error(
      body?.error?.message ?? `Request failed (${res.status})`,
    )
    ;(err as Error & { status?: number }).status = res.status
    throw err
  }
  return (await res.json()) as T
}

/** Start (or resume) the guest's customization session for a product. */
export async function startCustomization(
  productId: string,
): Promise<CustomizationSession> {
  return parse<CustomizationSession>(
    await call("/storefront/customizations", {
      method: "POST",
      body: JSON.stringify({ product_id: productId }),
    }),
  )
}

/** Autosave the editor state for a session. */
export async function saveCustomizationState(
  sessionId: string,
  state: CustomizationState,
): Promise<CustomizationSession> {
  return parse<CustomizationSession>(
    await call(`/storefront/customizations/${sessionId}/state`, {
      method: "PUT",
      body: JSON.stringify(state),
    }),
  )
}

/** Upload raster art (multipart) and get the recorded upload + presigned URL. */
export async function uploadCustomizationArt(
  sessionId: string,
  formData: FormData,
): Promise<UploadPublic> {
  return parse<UploadPublic>(
    await call(`/storefront/customizations/${sessionId}/uploads`, {
      method: "POST",
      body: formData,
    }),
  )
}

/** Approve a session with the client-side snapshot (freezes it). */
export async function approveCustomization(
  sessionId: string,
  formData: FormData,
): Promise<CustomizationSession> {
  return parse<CustomizationSession>(
    await call(`/storefront/customizations/${sessionId}/approve`, {
      method: "POST",
      body: formData,
    }),
  )
}

/** Approve a shared session via its public token (contact + snapshot multipart). */
export async function approveCustomizationViaToken(
  token: string,
  formData: FormData,
): Promise<CustomizationSession> {
  return parse<CustomizationSession>(
    await call(`/storefront/p/${token}/approve`, {
      method: "POST",
      body: formData,
    }),
  )
}
