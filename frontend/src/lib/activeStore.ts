import type { StorePublic } from "@/client"

/** localStorage key holding the user's last chosen active store id. */
export const ACTIVE_STORE_KEY = "active_store_id"

/** Outcome of resolving which store should be active after login. */
export type StoreResolution =
  | { status: "none" }
  | { status: "select" }
  | { status: "ready"; store: StorePublic }

/**
 * Decide which store should be active given the user's stores and a persisted choice.
 *
 * Rules: no stores -> "none"; a valid persisted id wins; a single store is
 * auto-selected; otherwise (multiple, no valid choice) -> "select".
 *
 * @param stores - The stores the user is an active member of.
 * @param persistedId - The previously chosen store id (from storage), if any.
 * @returns The resolution describing whether to enter, prompt, or show an empty state.
 */
export function resolveActiveStore(
  stores: StorePublic[],
  persistedId: string | null,
): StoreResolution {
  if (stores.length === 0) {
    return { status: "none" }
  }
  if (persistedId) {
    const match = stores.find((store) => store.id === persistedId)
    if (match) {
      return { status: "ready", store: match }
    }
  }
  if (stores.length === 1) {
    return { status: "ready", store: stores[0] }
  }
  return { status: "select" }
}
