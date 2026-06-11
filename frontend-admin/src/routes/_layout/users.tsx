import { useMutation, useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"

import { PlatformAdminService } from "@/client"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogFooter,
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

export const Route = createFileRoute("/_layout/users")({
  component: UsersScreen,
  head: () => ({ meta: [{ title: "Usuários — Admin" }] }),
})

function UsersScreen() {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [search, setSearch] = useState("")
  const [target, setTarget] = useState<{ id: string; email: string } | null>(
    null,
  )

  const usersQuery = useQuery({
    queryKey: ["adminUsers", search],
    queryFn: () =>
      PlatformAdminService.listUsers({
        search: search || undefined,
        limit: 100,
      }),
  })

  const impersonateMutation = useMutation({
    mutationFn: (userId: string) =>
      PlatformAdminService.impersonateUser({ userId }),
    onSuccess: () => {
      showSuccessToast("Acesso de impersonation gerado (ação auditada).")
      setTarget(null)
    },
    onError: handleError.bind(showErrorToast),
  })

  const users = usersQuery.data?.data ?? []

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Usuários</h1>
        <p className="text-muted-foreground">
          Contas + suporte (impersonation auditada).
        </p>
      </div>

      <Input
        placeholder="Buscar por e-mail…"
        value={search}
        onChange={(event) => setSearch(event.target.value)}
        className="max-w-sm"
      />

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>E-mail</TableHead>
            <TableHead>Nome</TableHead>
            <TableHead className="w-0" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {users.map((user) => (
            <TableRow key={user.id}>
              <TableCell>{user.email}</TableCell>
              <TableCell>{user.full_name ?? "—"}</TableCell>
              <TableCell>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setTarget({ id: user.id, email: user.email })}
                >
                  Impersonar
                </Button>
              </TableCell>
            </TableRow>
          ))}
          {users.length === 0 && (
            <TableRow>
              <TableCell colSpan={3} className="text-muted-foreground">
                Nenhum usuário.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>

      <Dialog
        open={!!target}
        onOpenChange={(isOpen) => {
          if (!isOpen) setTarget(null)
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Impersonar usuário</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Você vai gerar um acesso como <strong>{target?.email}</strong>.{" "}
            <strong>Esta ação é auditada.</strong>
          </p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setTarget(null)}>
              Cancelar
            </Button>
            <Button
              onClick={() => target && impersonateMutation.mutate(target.id)}
              disabled={impersonateMutation.isPending}
            >
              Confirmar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
