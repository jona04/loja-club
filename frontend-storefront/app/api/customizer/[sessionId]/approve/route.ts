import { forwardMultipart } from "@/lib/backend-proxy"

/**
 * Proxy a session approval (snapshot + high-res composite, multipart) to the
 * backend. Used via XHR so the editor can show real progress while the snapshot
 * and composite upload (they can be several MB).
 *
 * @param request - The multipart request with `snapshot` + `composite`.
 * @param ctx - Route params with the customization `sessionId`.
 * @returns The approved session, or the backend's error.
 */
export async function POST(
  request: Request,
  ctx: { params: Promise<{ sessionId: string }> },
) {
  const { sessionId } = await ctx.params
  const formData = await request.formData()
  return forwardMultipart(
    `/storefront/customizations/${sessionId}/approve`,
    formData,
  )
}
