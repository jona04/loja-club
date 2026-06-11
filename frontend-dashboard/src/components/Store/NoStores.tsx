import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Store } from "lucide-react"
import { useState } from "react"

import { StoresService } from "@/client"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useActiveStore } from "@/hooks/useActiveStore"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

/** Supported store countries (must match the backend localization map). */
const COUNTRIES = [
  { code: "BR", name: "Brasil" },
  { code: "PT", name: "Portugal" },
  { code: "US", name: "Estados Unidos" },
  { code: "GB", name: "Reino Unido" },
  { code: "CA", name: "Canadá" },
  { code: "ES", name: "Espanha" },
  { code: "FR", name: "França" },
  { code: "DE", name: "Alemanha" },
  { code: "IT", name: "Itália" },
  { code: "MX", name: "México" },
  { code: "AR", name: "Argentina" },
  { code: "CL", name: "Chile" },
  { code: "CO", name: "Colômbia" },
  { code: "UY", name: "Uruguai" },
  { code: "PY", name: "Paraguai" },
]

/**
 * Empty state shown when the user has no stores, with a minimal "create store" CTA.
 *
 * The richer onboarding checklist is a later task; this only creates the first store.
 * The country is required — it derives the store's currency, locale and price format.
 *
 * @returns The empty state with a create-store dialog.
 */
export function NoStores() {
  const [open, setOpen] = useState(false)
  const [name, setName] = useState("")
  const [country, setCountry] = useState("BR")
  const queryClient = useQueryClient()
  const { setActiveStore } = useActiveStore()
  const { showErrorToast } = useCustomToast()

  const createMutation = useMutation({
    mutationFn: () =>
      StoresService.createStore({ requestBody: { name, country } }),
    onSuccess: (store) => {
      queryClient.invalidateQueries({ queryKey: ["myStores"] })
      setActiveStore(store.id)
      setOpen(false)
    },
    onError: handleError.bind(showErrorToast),
  })

  return (
    <div className="mx-auto max-w-md space-y-4 text-center">
      <Store className="mx-auto size-10 text-muted-foreground" />
      <div>
        <h1 className="text-xl font-semibold">Você ainda não tem lojas</h1>
        <p className="text-muted-foreground">
          Crie sua primeira loja para começar.
        </p>
      </div>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogTrigger asChild>
          <Button>Criar loja</Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Nova loja</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 text-left">
            <div className="space-y-2">
              <Label htmlFor="store-name">Nome da loja</Label>
              <Input
                id="store-name"
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="Minha Loja"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="store-country">País da loja</Label>
              <select
                id="store-country"
                value={country}
                onChange={(event) => setCountry(event.target.value)}
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
              >
                {COUNTRIES.map((item) => (
                  <option key={item.code} value={item.code}>
                    {item.name}
                  </option>
                ))}
              </select>
              <p className="text-xs text-muted-foreground">
                Define a moeda e o formato de preço da loja.
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button
              onClick={() => createMutation.mutate()}
              disabled={!name.trim() || createMutation.isPending}
            >
              Criar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
