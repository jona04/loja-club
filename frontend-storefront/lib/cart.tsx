"use client"

import {
  createContext,
  type ReactNode,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react"

/** A line in the (client-side) cart. The real cart/order is Fase 4. */
export interface CartItem {
  id: string
  slug: string
  name: string
  subtitle?: string
  priceAmountMinor: number
  priceCurrency: string
  image: string | null
  qty: number
}

interface CartState {
  items: CartItem[]
  isOpen: boolean
  open: () => void
  close: () => void
  add: (item: Omit<CartItem, "qty">, qty?: number) => void
  remove: (id: string) => void
  setQty: (id: string, qty: number) => void
  clear: () => void
  subtotalMinor: number
  count: number
}

const CartContext = createContext<CartState | null>(null)
const STORAGE_KEY = "loja-club-cart"

/**
 * Client-side cart provider (localStorage-backed). Holds the items and the
 * drawer open state; the real cart/checkout is Fase 4.
 *
 * @param children - The subtree that can read/mutate the cart.
 * @returns The provider wrapping its children.
 */
export function CartProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<CartItem[]>([])
  const [isOpen, setIsOpen] = useState(false)

  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (raw) {
        setItems(JSON.parse(raw))
      }
    } catch {
      // Corrupt/blocked storage — start empty.
    }
  }, [])

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items))
  }, [items])

  useEffect(() => {
    document.body.style.overflow = isOpen ? "hidden" : ""
    return () => {
      document.body.style.overflow = ""
    }
  }, [isOpen])

  const value = useMemo<CartState>(() => {
    const add = (item: Omit<CartItem, "qty">, qty = 1) => {
      setItems((cur) => {
        const found = cur.find((i) => i.id === item.id)
        if (found) {
          return cur.map((i) =>
            i.id === item.id ? { ...i, qty: i.qty + qty } : i,
          )
        }
        return [...cur, { ...item, qty }]
      })
      setIsOpen(true)
    }
    const remove = (id: string) =>
      setItems((cur) => cur.filter((i) => i.id !== id))
    const setQty = (id: string, qty: number) =>
      setItems((cur) =>
        cur.map((i) => (i.id === id ? { ...i, qty: Math.max(1, qty) } : i)),
      )
    return {
      items,
      isOpen,
      open: () => setIsOpen(true),
      close: () => setIsOpen(false),
      add,
      remove,
      setQty,
      clear: () => setItems([]),
      subtotalMinor: items.reduce((s, i) => s + i.priceAmountMinor * i.qty, 0),
      count: items.reduce((s, i) => s + i.qty, 0),
    }
  }, [items, isOpen])

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>
}

/**
 * Read/mutate the client cart.
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
