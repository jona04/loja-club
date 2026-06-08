import type { ReactNode } from "react"

import { NoStores } from "@/components/Store/NoStores"
import { StoreSelector } from "@/components/Store/StoreSelector"
import { useActiveStore } from "@/hooks/useActiveStore"

/**
 * Gate store-scoped screens on the active-store resolution.
 *
 * Shows a loading state, the empty-state CTA, or the store selector until a
 * store is active; only then renders ``children``. Non-store screens (e.g.
 * account settings) must NOT use this gate so they stay reachable without a store.
 *
 * @param props.children - Store-scoped content, mounted only when a store is active.
 * @returns The gated content or the appropriate placeholder.
 */
export function StoreGate({ children }: { children: ReactNode }) {
  const { isLoading, resolution } = useActiveStore()

  if (isLoading) {
    return <p className="text-muted-foreground">Carregando…</p>
  }
  if (resolution.status === "none") {
    return <NoStores />
  }
  if (resolution.status === "select") {
    return <StoreSelector />
  }
  return <>{children}</>
}
