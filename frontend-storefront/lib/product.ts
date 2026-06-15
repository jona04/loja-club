/**
 * Client-safe product helpers. Kept out of `lib/api.ts` (which imports
 * `next/headers` and is server-only) so client components can use them.
 */

export type ProductType = "image" | "image_3d" | "image_3d_customizable"

/** Whether a product must be customized in the 3D editor before buying. */
export function isCustomizable(product: { type: ProductType }): boolean {
  return product.type === "image_3d_customizable"
}
