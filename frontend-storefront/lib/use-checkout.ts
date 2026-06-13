"use client"

import { type FormEvent, useState } from "react"

import type {
  OrderPublic,
  ShippingMethodPublic,
  StorefrontStore,
} from "@/lib/api"
import { type CartItem, useCart } from "@/lib/cart"
import { submitCheckout } from "@/lib/cart-actions"
import { formatPrice } from "@/lib/format"

/** Country dial options for the checkout phone field. */
export const COUNTRIES = [
  { code: "BR", label: "🇧🇷 +55" },
  { code: "US", label: "🇺🇸 +1" },
  { code: "PT", label: "🇵🇹 +351" },
] as const

const SHIPPING_LABEL: Record<string, string> = {
  fixed_shipping: "Frete fixo",
  free_shipping: "Frete grátis",
  local_pickup: "Retirada local",
  private_delivery: "Entrega combinada (a loja entra em contato)",
}

/**
 * Human label for a shipping method (its own name, else a type fallback).
 *
 * @param method - The shipping method to label.
 * @returns The display label.
 */
export function shippingLabel(method: ShippingMethodPublic): string {
  return method.name || SHIPPING_LABEL[method.type] || method.type
}

/**
 * Build a WhatsApp link with the order pre-filled, to arrange payment.
 *
 * @param whatsapp - The store WhatsApp number (any format).
 * @param order - The placed order.
 * @param locale - Store locale for price formatting.
 * @returns A `https://wa.me/...` link carrying the order summary.
 */
export function orderWhatsappLink(
  whatsapp: string,
  order: OrderPublic,
  locale: string,
): string {
  const lines = order.items
    .map((item) => `• ${item.quantity}x ${item.name}`)
    .join("\n")
  const total = formatPrice(order.total_amount_minor, order.currency, locale)
  const message = `Olá! Fiz o pedido #${order.order_number}.\n${lines}\nTotal: ${total}\nGostaria de combinar o pagamento.`
  return `https://wa.me/${whatsapp.replace(/\D/g, "")}?text=${encodeURIComponent(message)}`
}

/** The checkout controller a template's `CheckoutView` renders. */
export interface CheckoutController {
  /** `empty` (no items), `form` (collecting data) or `done` (order placed). */
  phase: "empty" | "form" | "done"
  /** The placed order, once `phase` is `done`. */
  order: OrderPublic | null
  /** Render-ready cart lines (same source the headers/drawers use). */
  items: CartItem[]
  /** Whether a cart mutation (qty/remove) is in flight. */
  cartLoading: boolean
  setItemQty: (itemId: string, quantity: number) => Promise<void>
  removeItem: (itemId: string) => Promise<void>
  name: string
  setName: (value: string) => void
  email: string
  setEmail: (value: string) => void
  phone: string
  setPhone: (value: string) => void
  country: string
  setCountry: (value: string) => void
  postalCode: string
  setPostalCode: (value: string) => void
  line1: string
  setLine1: (value: string) => void
  number: string
  setNumber: (value: string) => void
  line2: string
  setLine2: (value: string) => void
  neighborhood: string
  setNeighborhood: (value: string) => void
  city: string
  setCity: (value: string) => void
  state: string
  setState: (value: string) => void
  methodId: string
  setMethodId: (value: string) => void
  /** The store's active shipping methods. */
  methods: ShippingMethodPublic[]
  /** The currently selected shipping method, if any. */
  selected: ShippingMethodPublic | undefined
  subtotalMinor: number
  shippingMinor: number
  totalMinor: number
  currency: string
  canSubmit: boolean
  submitting: boolean
  error: string | null
  onSubmit: (event: FormEvent) => Promise<void>
  /** The store WhatsApp number for the confirmation handoff, if set. */
  whatsappNumber: string | null
  locale: string
}

/**
 * Headless checkout logic shared by every template's `CheckoutView`: holds the
 * form state (contact + full address), derives the totals from the server cart +
 * selected shipping, edits the cart lines, and places the order (no login, no
 * gateway). Each template renders the result in its own look; only the
 * presentation differs.
 *
 * @param store - The store (whatsapp + policies + currency).
 * @param methods - The store's active shipping methods.
 * @param locale - Store locale for price formatting.
 * @returns The checkout controller (state, setters, totals, submit).
 */
export function useCheckout(
  store: StorefrontStore,
  methods: ShippingMethodPublic[],
  locale: string,
): CheckoutController {
  const cart = useCart()
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [phone, setPhone] = useState("")
  const [country, setCountry] = useState("BR")
  const [postalCode, setPostalCode] = useState("")
  const [line1, setLine1] = useState("")
  const [number, setNumber] = useState("")
  const [line2, setLine2] = useState("")
  const [neighborhood, setNeighborhood] = useState("")
  const [city, setCity] = useState("")
  const [state, setState] = useState("")
  const [methodId, setMethodId] = useState("")
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [order, setOrder] = useState<OrderPublic | null>(null)

  const selected = methods.find((m) => m.id === methodId)
  const shippingMinor =
    selected?.type === "fixed_shipping" ? (selected.price_amount_minor ?? 0) : 0
  const totalMinor = cart.subtotalMinor + shippingMinor
  const canSubmit =
    !submitting &&
    name.trim() !== "" &&
    line1.trim() !== "" &&
    city.trim() !== "" &&
    methodId !== "" &&
    (email.trim() !== "" || phone.trim() !== "")

  const onSubmit = async (event: FormEvent): Promise<void> => {
    event.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      const result = await submitCheckout({
        contact: {
          name,
          email: email || undefined,
          phone: phone || undefined,
          region: phone ? country : undefined,
        },
        address: {
          line1,
          number: number || undefined,
          line2: line2 || undefined,
          neighborhood: neighborhood || undefined,
          city,
          state: state || undefined,
          postal_code: postalCode || undefined,
          country,
        },
        shipping_method_id: methodId,
      })
      setOrder(result)
      await cart.refresh()
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Não foi possível finalizar.",
      )
    } finally {
      setSubmitting(false)
    }
  }

  const phase: CheckoutController["phase"] = order
    ? "done"
    : cart.items.length
      ? "form"
      : "empty"

  return {
    phase,
    order,
    items: cart.items,
    cartLoading: cart.loading,
    setItemQty: cart.setQty,
    removeItem: cart.remove,
    name,
    setName,
    email,
    setEmail,
    phone,
    setPhone,
    country,
    setCountry,
    postalCode,
    setPostalCode,
    line1,
    setLine1,
    number,
    setNumber,
    line2,
    setLine2,
    neighborhood,
    setNeighborhood,
    city,
    setCity,
    state,
    setState,
    methodId,
    setMethodId,
    methods,
    selected,
    subtotalMinor: cart.subtotalMinor,
    shippingMinor,
    totalMinor,
    currency: cart.currency,
    canSubmit,
    submitting,
    error,
    onSubmit,
    whatsappNumber: store.whatsapp_number,
    locale,
  }
}
