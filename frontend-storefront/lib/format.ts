/**
 * Pure formatting helpers — safe to import from client components (they pull in
 * no server-only modules like `next/headers`, unlike `lib/api`).
 */

/** Format a minor-unit price with its ISO currency, using the store's locale. */
export function formatPrice(
  amountMinor: number,
  currency: string,
  locale: string,
): string {
  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency,
  }).format(amountMinor / 100)
}

/** Build a wa.me link from a (possibly formatted) phone number. */
export function whatsappLink(phone: string): string {
  return `https://wa.me/${phone.replace(/\D/g, "")}`
}
