import { forwardMultipart } from "@/lib/backend-proxy"

/**
 * Proxy a public (assisted) session approval via its token (contact + snapshot +
 * composite, multipart) to the backend. Used via XHR for upload progress.
 *
 * @param request - The multipart request with contact + `snapshot` + `composite`.
 * @param ctx - Route params with the session's public `token`.
 * @returns The approved session, or the backend's error.
 */
export async function POST(
  request: Request,
  ctx: { params: Promise<{ token: string }> },
) {
  const { token } = await ctx.params
  const formData = await request.formData()
  return forwardMultipart(`/storefront/p/${token}/approve`, formData)
}
