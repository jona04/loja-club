import { whatsappLink } from "@/lib/api"

/**
 * Floating WhatsApp button, shown only when the store has a number.
 *
 * @param phone - The store's WhatsApp number (any format), or null.
 * @returns The floating button, or nothing when no number is set.
 */
export function WhatsAppButton({ phone }: { phone: string | null }) {
  if (!phone) {
    return null
  }
  return (
    <a
      href={whatsappLink(phone)}
      target="_blank"
      rel="noopener noreferrer"
      aria-label="Falar no WhatsApp"
      className="fixed bottom-5 right-5 z-50 rounded-full bg-green-500 px-5 py-3 font-semibold text-white shadow-lg transition hover:bg-green-600"
    >
      WhatsApp
    </a>
  )
}
