import { PublicCustomizer } from "@/components/customizer/PublicCustomizer"
import { getPublicCustomization } from "@/lib/api"

/**
 * Public shared-customization page (doc 30 §9): opens a session by its token in
 * read-only mode and lets the customer approve by confirming their contact.
 *
 * @param params - Route params carrying the session `token`.
 * @returns The public viewer (or `notFound` if the token is invalid/expired).
 */
export default async function PublicCustomizationPage({
  params,
}: {
  params: Promise<{ token: string }>
}) {
  const { token } = await params
  const session = await getPublicCustomization(token)
  return <PublicCustomizer token={token} session={session} />
}
