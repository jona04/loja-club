"use client"

import type { StorefrontVariant } from "@/lib/api"

/**
 * A variant `<select>` for the product page (P7-SF-02). Out-of-stock variants
 * are shown disabled with an "(esgotado)" suffix. Presentation-only — each
 * template passes its own `className` for the select.
 *
 * @param props.variants - The product's active variants.
 * @param props.value - The selected variant id.
 * @param props.onChange - Called with the chosen variant id.
 * @param props.className - Tailwind classes for the select (template styling).
 * @param props.label - The field label (default "Variação").
 * @returns The labeled variant select.
 */
export function VariantSelect({
  variants,
  value,
  onChange,
  className,
  label = "Variação",
}: {
  variants: StorefrontVariant[]
  value: string | undefined
  onChange: (id: string) => void
  className?: string
  label?: string
}) {
  return (
    <div className="mb-4">
      <span className="mb-2 block text-sm font-medium text-gray-700">
        {label}
      </span>
      <select
        aria-label={label}
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value)}
        className={className}
      >
        {variants.map((variant) => (
          <option
            key={variant.id}
            value={variant.id}
            disabled={!variant.in_stock}
          >
            {variant.name}
            {variant.in_stock ? "" : " (esgotado)"}
          </option>
        ))}
      </select>
    </div>
  )
}
