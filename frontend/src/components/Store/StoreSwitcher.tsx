import { Check, ChevronsUpDown, Store } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useActiveStore } from "@/hooks/useActiveStore"

/**
 * Header control showing the active store and letting the user switch stores.
 *
 * Renders nothing while no store is active (loading / selection / empty states).
 *
 * @returns The switcher element, or null when there is no active store.
 */
export function StoreSwitcher() {
  const { stores, activeStore, setActiveStore } = useActiveStore()

  if (!activeStore) {
    return null
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm" className="gap-2">
          <Store className="size-4" />
          <span className="max-w-[12rem] truncate">{activeStore.name}</span>
          <ChevronsUpDown className="size-4 opacity-60" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        {stores.map((store) => (
          <DropdownMenuItem
            key={store.id}
            onClick={() => setActiveStore(store.id)}
          >
            <span className="flex-1 truncate">{store.name}</span>
            {store.id === activeStore.id && <Check className="size-4" />}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
