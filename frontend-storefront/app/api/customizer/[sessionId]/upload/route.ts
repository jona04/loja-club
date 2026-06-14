import { forwardMultipart } from "@/lib/backend-proxy"

/**
 * Proxy an art upload (multipart) to the backend. Used via XHR so the editor can
 * show real upload progress for large images.
 *
 * @param request - The multipart request carrying the `file` field.
 * @param ctx - Route params with the customization `sessionId`.
 * @returns The recorded upload (presigned URL), or the backend's error.
 */
export async function POST(
  request: Request,
  ctx: { params: Promise<{ sessionId: string }> },
) {
  const { sessionId } = await ctx.params
  const formData = await request.formData()
  return forwardMultipart(
    `/storefront/customizations/${sessionId}/uploads`,
    formData,
  )
}
