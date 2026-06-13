import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"

import { StoresService } from "@/client"
import { StoreGate } from "@/components/Store/StoreGate"
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { useActiveStore } from "@/hooks/useActiveStore"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

export const Route = createFileRoute("/_layout/team")({
  component: TeamRoute,
  head: () => ({
    meta: [{ title: "Equipe - Kriar" }],
  }),
})

function TeamRoute() {
  return (
    <StoreGate>
      <TeamScreen />
    </StoreGate>
  )
}

const ROLES = ["owner", "admin", "manager", "support", "catalog", "marketing"]

function TeamScreen() {
  const { activeStore, permissions } = useActiveStore()
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [inviteOpen, setInviteOpen] = useState(false)
  const [email, setEmail] = useState("")
  const [inviteRole, setInviteRole] = useState("support")

  const storeId = activeStore?.id ?? ""
  const canInvite = permissions.includes("team.invite")
  const canUpdateRole = permissions.includes("team.update_role")
  const canRemove = permissions.includes("team.remove")

  const membersQuery = useQuery({
    queryKey: ["members", storeId],
    queryFn: () => StoresService.listStoreMembers({ storeId }),
    enabled: storeId !== "",
  })

  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: ["members", storeId] })

  const inviteMutation = useMutation({
    mutationFn: () =>
      StoresService.inviteStoreMember({
        storeId,
        requestBody: { email, role: inviteRole },
      }),
    onSuccess: () => {
      showSuccessToast("Convite enviado")
      invalidate()
      setInviteOpen(false)
      setEmail("")
    },
    onError: handleError.bind(showErrorToast),
  })

  const roleMutation = useMutation({
    mutationFn: (vars: { userId: string; role: string }) =>
      StoresService.updateStoreMemberRole({
        storeId,
        userId: vars.userId,
        requestBody: { role: vars.role },
      }),
    onSuccess: invalidate,
    onError: handleError.bind(showErrorToast),
  })

  const removeMutation = useMutation({
    mutationFn: (userId: string) =>
      StoresService.removeStoreMember({ storeId, userId }),
    onSuccess: invalidate,
    onError: handleError.bind(showErrorToast),
  })

  if (!activeStore) {
    return null
  }

  const members = membersQuery.data?.data ?? []

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Equipe</h1>
          <p className="text-muted-foreground">
            Membros e papéis de {activeStore.name}
          </p>
        </div>
        {canInvite && (
          <Dialog open={inviteOpen} onOpenChange={setInviteOpen}>
            <DialogTrigger asChild>
              <Button>Convidar</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Convidar membro</DialogTitle>
              </DialogHeader>
              <div className="space-y-3">
                <div className="space-y-1.5">
                  <Label htmlFor="invite-email">E-mail</Label>
                  <Input
                    id="invite-email"
                    type="email"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    placeholder="pessoa@exemplo.com"
                  />
                </div>
                <div className="space-y-1.5">
                  <Label>Papel</Label>
                  <Select value={inviteRole} onValueChange={setInviteRole}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {ROLES.map((role) => (
                        <SelectItem key={role} value={role}>
                          {role}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <DialogFooter>
                <Button
                  onClick={() => inviteMutation.mutate()}
                  disabled={!email.trim() || inviteMutation.isPending}
                >
                  Enviar convite
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        )}
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>E-mail</TableHead>
            <TableHead>Papel</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="w-0" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {members.map((member) => (
            <TableRow key={member.id}>
              <TableCell>{member.email}</TableCell>
              <TableCell>
                {canUpdateRole ? (
                  <Select
                    value={member.role}
                    onValueChange={(role) =>
                      roleMutation.mutate({ userId: member.user_id, role })
                    }
                  >
                    <SelectTrigger className="w-36">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {ROLES.map((role) => (
                        <SelectItem key={role} value={role}>
                          {role}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                ) : (
                  member.role
                )}
              </TableCell>
              <TableCell>{member.status}</TableCell>
              <TableCell>
                {canRemove && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeMutation.mutate(member.user_id)}
                  >
                    Remover
                  </Button>
                )}
              </TableCell>
            </TableRow>
          ))}
          {members.length === 0 && (
            <TableRow>
              <TableCell colSpan={4} className="text-muted-foreground">
                Nenhum membro.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  )
}
