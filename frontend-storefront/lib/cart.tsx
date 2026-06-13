"use client"

import {
  createContext,
  type ReactNode,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react"

import type { CartPublic } from "@/lib/api"
import {
  addToCart,
  getCart,
  removeCartItem,
  updateCartItem,
} from "@/lib/cart-actions"

/** A cart line in the shape the template headers/drawers render. */
export interface CartItem {
  id: string
  slug: string
  name: string
  subtitle?: string
  image: string | null
  priceAmountMinor: number
  priceCurrency: string
  qty: number
}

interface CartState {
  cart: CartPublic | null
  items: CartItem[]
  count: number
  subtotalMinor: number
  currency: string
  isOpen: boolean
  loading: boolean
  error: string | null
  open: () => void
  close: () => void
  add: (productId: string, quantity?: number) => Promise<void>
  setQty: (itemId: string, quantity: number) => Promise<void>
  remove: (itemId: string) => Promise<void>
  refresh: () => Promise<void>
}

const CartContext = createContext<CartState | null>(null)

/**
 * Server-cart provider: the cart lives in the backend (keyed by the guest
 * cookie). Mutations go through Server Actions and replace the cart with the
 * result. Exposes a render-ready view (`items`/`count`/`subtotalMinor`) so the
 * template headers/drawers stay unchanged.
 *
 * @param children - The subtree that can read/mutate the cart.
 * @returns The provider wrapping its children.
 */
export function CartProvider({ children }: { children: ReactNode }) {
  const [cart, setCart] = useState<CartPublic | null>(null)
  const [isOpen, setIsOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    try {
      setCart(await getCart())
    } catch {
      // Keep the current cart on a transient read failure.
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  useEffect(() => {
    document.body.style.overflow = isOpen ? "hidden" : ""
    return () => {
      document.body.style.overflow = ""
    }
  }, [isOpen])

  const run = async (
    action: () => Promise<CartPublic>,
    openOnDone = false,
  ): Promise<void> => {
    setLoading(true)
    setError(null)
    try {
      setCart(await action())
      if (openOnDone) {
        setIsOpen(true)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Algo deu errado.")
    } finally {
      setLoading(false)
    }
  }

  const items: CartItem[] = (cart?.items ?? []).map((line) => ({
    id: line.id,
    slug: line.slug,
    name: line.name,
    image: line.image_url,
    priceAmountMinor: line.unit_price_amount_minor,
    priceCurrency: line.unit_price_currency,
    qty: line.quantity,
  }))

  const value: CartState = {
    cart,
    items,
    count: cart?.item_count ?? 0,
    subtotalMinor: cart?.subtotal_amount_minor ?? 0,
    currency: cart?.currency ?? "BRL",
    isOpen,
    loading,
    error,
    open: () => setIsOpen(true),
    close: () => setIsOpen(false),
    add: (productId, quantity = 1) =>
      run(() => addToCart(productId, quantity), true),
    setQty: (itemId, quantity) => run(() => updateCartItem(itemId, quantity)),
    remove: (itemId) => run(() => removeCartItem(itemId)),
    refresh,
  }

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>
}

/**
 * Read/mutate the server cart.
 *
 * @returns The cart state and actions.
 * @throws If used outside a {@link CartProvider}.
 */
export function useCart(): CartState {
  const ctx = useContext(CartContext)
  if (!ctx) {
    throw new Error("useCart must be used within a CartProvider")
  }
  return ctx
}
