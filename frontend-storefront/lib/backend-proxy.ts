/**
 * Backend proxy for Route Handlers.
 *
 * The heavy customization operations (art upload, approval snapshot + composite)
 * go through Route Handlers instead of Server Actions so the browser can report
 * real upload progress (XHR). Like the Server Actions, the browser cannot reach
 * the backend directly, so these forward the store `Host` + `guest_session_id`
 * cookie and re-emit the backend's `Set-Cookie`.
 */

import { cookies, headers } from "next/headers"
import { NextResponse } from "next/server"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8800"
const GUEST_COOKIE = "guest_session_id"
const GUEST_MAX_AGE = 60 * 60 * 24 * 30

/**
 * Forward a multipart request to a backend storefront path, carrying the store
 * host + the guest cookie, and re-emitting the backend's guest cookie.
 *
 * @param backendPath - Path under `/api/v1` (e.g. `/storefront/...`).
 * @param formData - The multipart body to forward unchanged.
 * @returns The backend's JSON response (status preserved), with any guest cookie.
 */
export async function forwardMultipart(
  backendPath: string,
  formData: FormData,
): Promise<NextResponse> {
  const incoming = await headers()
  const host = incoming.get("x-forwarded-host") ?? incoming.get("host") ?? ""
  const jar = await cookies()
  const guest = jar.get(GUEST_COOKIE)?.value

  const reqHeaders: Record<string, string> = { "x-forwarded-host": host }
  if (guest) reqHeaders.cookie = `${GUEST_COOKIE}=${guest}`

  const res = await fetch(`${API_URL}/api/v1${backendPath}`, {
    method: "POST",
    headers: reqHeaders,
    body: formData,
    cache: "no-store",
  })

  const bag = res.headers as unknown as { getSetCookie?: () => string[] }
  for (const raw of bag.getSetCookie?.() ?? []) {
    const match = raw.match(/guest_session_id=([^;]+)/)
    if (match) {
      jar.set(GUEST_COOKIE, match[1], {
        httpOnly: true,
        sameSite: "lax",
        path: "/",
        maxAge: GUEST_MAX_AGE,
      })
    }
  }

  const body = await res.text()
  return new NextResponse(body, {
    status: res.status,
    headers: {
      "content-type": res.headers.get("content-type") ?? "application/json",
    },
  })
}
