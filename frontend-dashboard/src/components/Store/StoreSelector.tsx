import { Store } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { useActiveStore } from "@/hooks/useActiveStore"

/**
 * Full prompt shown when the user belongs to several stores and none is chosen yet.
 *
 * @returns A list of stores; picking one sets it as the active store.
 */
export function StoreSelector() {
  const { stores, setActiveStore } = useActiveStore()

  return (
    <div className="mx-auto max-w-md space-y-4">
      <div>
        <h1 className="text-xl font-semibold">Selecione uma loja</h1>
        <p className="text-muted-foreground">
          Você administra mais de uma loja. Escolha com qual deseja trabalhar.
        </p>
      </div>
      <div className="space-y-2">
        {stores.map((store) => (
          <Card key={store.id} className="p-0">
            <Button
              variant="ghost"
              className="h-auto w-full justify-start gap-3 p-4"
              onClick={() => setActiveStore(store.id)}
            >
              <Store className="size-5 shrink-0" />
              <span className="flex flex-col text-left">
                <span className="font-medium">{store.name}</span>
                <span className="text-sm text-muted-foreground">
                  {store.slug}
                </span>
              </span>
            </Button>
          </Card>
        ))}
      </div>
    </div>
  )
}
