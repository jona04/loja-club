import { useQuery } from "@tanstack/react-query"
import {
  createContext,
  type ReactNode,
  useCallback,
  useContext,
  useMemo,
  useState,
} from "react"

import { type StorePublic, StoresService } from "@/client"
import {
  ACTIVE_STORE_KEY,
  resolveActiveStore,
  type StoreResolution,
} from "@/lib/activeStore"

interface ActiveStoreContextValue {
  /** All stores the user is an active member of. */
  stores: StorePublic[]
  /** True while the user's stores are being fetched. */
  isLoading: boolean
  /** How the active store was resolved (none / select / ready). */
  resolution: StoreResolution
  /** The active store, or null while none is resolved. */
  activeStore: StorePublic | null
  /** Persist and switch the active store. */
  setActiveStore: (storeId: string) => void
  /** Permission keys of the current user in the active store. */
  permissions: string[]
  /** The current user's role key in the active store, or null. */
  role: string | null
}

const ActiveStoreContext = createContext<ActiveStoreContextValue | null>(null)

/**
 * Provide the active-store context for the dashboard: fetches the user's stores,
 * resolves/persists the active one, and exposes its role/permissions.
 *
 * @param props.children - The dashboard subtree that consumes the context.
 * @returns The provider element.
 */
export function ActiveStoreProvider({ children }: { children: ReactNode }) {
  const [activeStoreId, setActiveStoreId] = useState<string | null>(() =>
    localStorage.getItem(ACTIVE_STORE_KEY),
  )

  const storesQuery = useQuery({
    queryKey: ["myStores"],
    queryFn: () => StoresService.listMyStores(),
  })

  const stores = useMemo(() => storesQuery.data?.data ?? [], [storesQuery.data])
  const resolution = useMemo(
    () => resolveActiveStore(stores, activeStoreId),
    [stores, activeStoreId],
  )
  const activeStore = resolution.status === "ready" ? resolution.store : null
  const activeId = activeStore?.id ?? null

  const membershipQuery = useQuery({
    queryKey: ["membership", activeId],
    queryFn: () =>
      StoresService.getMyMembership({ storeId: activeId as string }),
    enabled: activeId !== null,
  })

  const setActiveStore = useCallback((storeId: string) => {
    localStorage.setItem(ACTIVE_STORE_KEY, storeId)
    setActiveStoreId(storeId)
  }, [])

  const value = useMemo<ActiveStoreContextValue>(
    () => ({
      stores,
      isLoading: storesQuery.isLoading,
      resolution,
      activeStore,
      setActiveStore,
      permissions: membershipQuery.data?.permissions ?? [],
      role: membershipQuery.data?.role ?? null,
    }),
    [
      stores,
      storesQuery.isLoading,
      resolution,
      activeStore,
      setActiveStore,
      membershipQuery.data,
    ],
  )

  return (
    <ActiveStoreContext.Provider value={value}>
      {children}
    </ActiveStoreContext.Provider>
  )
}

/**
 * Access the active-store context.
 *
 * @returns The active store, the user's stores, role/permissions, and a setter.
 * @throws If used outside an {@link ActiveStoreProvider}.
 */
export function useActiveStore(): ActiveStoreContextValue {
  const ctx = useContext(ActiveStoreContext)
  if (!ctx) {
    throw new Error("useActiveStore must be used within an ActiveStoreProvider")
  }
  return ctx
}
