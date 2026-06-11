import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"

import { PlatformAdminService } from "@/client"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

export const Route = createFileRoute("/_layout/stores")({
  component: StoresScreen,
  head: () => ({ meta: [{ title: "Lojas — Admin" }] }),
})

function StoresScreen() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [search, setSearch] = useState("")
  const [detailId, setDetailId] = useState<string | null>(null)

  const storesQuery = useQuery({
    queryKey: ["adminStores", search],
    queryFn: () =>
      PlatformAdminService.listStores({
        search: search || undefined,
        limit: 100,
      }),
  })
  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: ["adminStores"] })

  const blockMutation = useMutation({
    mutationFn: (storeId: string) =>
      PlatformAdminService.blockStore({ storeId }),
    onSuccess: () => {
      showSuccessToast("Loja bloqueada")
      invalidate()
    },
    onError: handleError.bind(showErrorToast),
  })
  const unblockMutation = useMutation({
    mutationFn: (storeId: string) =>
      PlatformAdminService.unblockStore({ storeId }),
    onSuccess: () => {
      showSuccessToast("Loja desbloqueada")
      invalidate()
    },
    onError: handleError.bind(showErrorToast),
  })

  const stores = storesQuery.data?.data ?? []

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Lojas</h1>
        <p className="text-muted-foreground">
          Operação de lojas da plataforma.
        </p>
      </div>

      <Input
        placeholder="Buscar por nome ou slug…"
        value={search}
        onChange={(event) => setSearch(event.target.value)}
        className="max-w-sm"
      />

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Nome</TableHead>
            <TableHead>Slug</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="w-0" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {stores.map((store) => (
            <TableRow key={store.id}>
              <TableCell>{store.name}</TableCell>
              <TableCell>{store.slug}</TableCell>
              <TableCell>{store.status}</TableCell>
              <TableCell className="flex gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setDetailId(store.id)}
                >
                  Detalhes
                </Button>
                {store.status === "blocked" ? (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => unblockMutation.mutate(store.id)}
                  >
                    Desbloquear
                  </Button>
                ) : (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => blockMutation.mutate(store.id)}
                  >
                    Bloquear
                  </Button>
                )}
              </TableCell>
            </TableRow>
          ))}
          {stores.length === 0 && (
            <TableRow>
              <TableCell colSpan={4} className="text-muted-foreground">
                Nenhuma loja.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>

      {detailId && (
        <StoreDetailDialog
          storeId={detailId}
          onClose={() => setDetailId(null)}
        />
      )}
    </div>
  )
}

function StoreDetailDialog({
  storeId,
  onClose,
}: {
  storeId: string
  onClose: () => void
}) {
  const detailQuery = useQuery({
    queryKey: ["adminStore", storeId],
    queryFn: () => PlatformAdminService.getStore({ storeId }),
  })
  const store = detailQuery.data
  const members = store?.members ?? []

  return (
    <Dialog
      open
      onOpenChange={(isOpen) => {
        if (!isOpen) onClose()
      }}
    >
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{store?.name ?? "Loja"}</DialogTitle>
        </DialogHeader>
        {store && (
          <div className="space-y-3 text-sm">
            <div>
              <span className="text-muted-foreground">Slug:</span> {store.slug}
            </div>
            <div>
              <span className="text-muted-foreground">Status:</span>{" "}
              {store.status}
            </div>
            <div>
              <div className="font-medium">Configurações</div>
              <div className="text-muted-foreground">
                {store.settings?.public_name ?? store.name} ·{" "}
                {store.settings?.description ?? "sem descrição"}
              </div>
            </div>
            <div>
              <div className="font-medium">Membros ({members.length})</div>
              <ul className="text-muted-foreground">
                {members.map((member) => (
                  <li key={member.id}>
                    {member.email} · {member.role}
                  </li>
                ))}
              </ul>
            </div>
            <p className="text-xs text-muted-foreground">
              Pedidos, volume, webhooks e comissões entram quando esses módulos
              existirem (Fase 6/8).
            </p>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
