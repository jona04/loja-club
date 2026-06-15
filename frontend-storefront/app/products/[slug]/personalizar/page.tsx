import { notFound } from "next/navigation"

import { Customizer } from "@/components/customizer/Customizer"
import { getProduct } from "@/lib/api"
import { isCustomizable } from "@/lib/product"

/**
 * The 3D customization editor route (P7-EDITOR-01). Fetches the product and, if
 * it is customizable, renders the editor shell; otherwise 404.
 *
 * @param params - Route params carrying the product `slug`.
 * @returns The editor page (or `notFound`).
 */
export default async function CustomizePage({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  const product = await getProduct(slug)
  if (!isCustomizable(product)) {
    notFound()
  }
  return <Customizer product={product} />
}
