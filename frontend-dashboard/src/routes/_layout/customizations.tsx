import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"

import {
  CatalogService,
  type CustomizationProductionStatus,
  CustomizationService,
  type CustomizationSessionStatus,
  type MerchantSessionListItem,
} from "@/client"
import { StoreGate } from "@/components/Store/StoreGate"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
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
import { Separator } from "@/components/ui/separator"
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

export const Route = createFileRoute("/_layout/customizations")({
  component: CustomizationsRoute,
  head: () => ({ meta: [{ title: "Personalizações - Kriar" }] }),
})

function CustomizationsRoute() {
  return (
    <StoreGate>
      <CustomizationsScreen />
    </StoreGate>
  )
}

const PAGE_SIZE = 20
// Near-real-time view of sessions being edited (doc 22): poll, no WebSocket yet.
const POLL_INTERVAL_MS = 10_000

/** Human pt-BR label for each session status. */
const SESSION_LABEL: Record<CustomizationSessionStatus, string> = {
  draft: "Em edição",
  approved: "Aprovada",
  added_to_cart: "No carrinho",
  ordered: "No pedido",
  abandoned: "Abandonada",
  expired: "Expirada",
}

/** Human pt-BR label for each production status (doc 22). */
const PRODUCTION_LABEL: Record<CustomizationProductionStatus, string> = {
  received: "Arte recebida",
  reviewing: "Avaliando",
  needs_contact: "Falar com cliente",
  approved_for_production: "Liberada p/ produção",
  in_production: "Em produção",
  production_done: "Produção concluída",
}

const PRODUCTION_STATUSES = Object.keys(
  PRODUCTION_LABEL,
) as CustomizationProductionStatus[]

const SESSION_VARIANT: Record<
  CustomizationSessionStatus,
  "default" | "secondary" | "outline" | "destructive"
> = {
  draft: "outline",
  approved: "secondary",
  added_to_cart: "secondary",
  ordered: "default",
  abandoned: "destructive",
  expired: "destructive",
}

/** Format an ISO timestamp for pt-BR display. */
const when = (iso: string): string => new Date(iso).toLocaleString("pt-BR")

/**
 * The merchant Customizations screen (P7-OPS-01): a near-real-time list of the
 * store's 3D customization sessions (polling), opening each to preview the art,
 * download the production files and advance the production status, plus
 * assembling an assisted customization and sharing its public link. Gated by
 * `customization.*` (UI gating only; the backend enforces authorization).
 *
 * @returns The Customizations management screen.
 */
export function CustomizationsScreen() {
  const { activeStore, permissions } = useActiveStore()
  const [page, setPage] = useState(0)
  const [status, setStatus] = useState<CustomizationSessionStatus | "all">(
    "all",
  )
  const [openId, setOpenId] = useState<string | null>(null)
  const [assistOpen, setAssistOpen] = useState(false)

  const storeId = activeStore?.id ?? ""
  const canView = permissions.includes("customization.sessions.view")

  const listQuery = useQuery({
    queryKey: ["customizations", storeId, page, status],
    queryFn: () =>
      CustomizationService.listCustomizations({
        storeId,
        skip: page * PAGE_SIZE,
        limit: PAGE_SIZE,
        status: status === "all" ? undefined : status,
      }),
    enabled: storeId !== "" && canView,
    refetchInterval: POLL_INTERVAL_MS,
  })

  if (!activeStore) {
    return null
  }

  const rows = listQuery.data?.data ?? []
  const count = listQuery.data?.count ?? 0

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-bold text-2xl tracking-tight">Personalizações</h1>
          <p className="text-muted-foreground">
            {count} personalização(ões) em {activeStore.name}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Select
            value={status}
            onValueChange={(v) => {
              setStatus(v as CustomizationSessionStatus | "all")
              setPage(0)
            }}
          >
            <SelectTrigger className="w-48">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos os status</SelectItem>
              {(Object.keys(SESSION_LABEL) as CustomizationSessionStatus[]).map(
                (s) => (
                  <SelectItem key={s} value={s}>
                    {SESSION_LABEL[s]}
                  </SelectItem>
                ),
              )}
            </SelectContent>
          </Select>
          {canView && (
            <Button onClick={() => setAssistOpen(true)}>
              Montar personalização
            </Button>
          )}
        </div>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-16">Arte</TableHead>
            <TableHead>Produto</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Produção</TableHead>
            <TableHead>Atualizado</TableHead>
            <TableHead className="w-0" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row) => (
            <CustomizationRow
              key={row.id}
              row={row}
              onOpen={() => setOpenId(row.id)}
            />
          ))}
          {rows.length === 0 && (
            <TableRow>
              <TableCell colSpan={6} className="text-muted-foreground">
                Nenhuma personalização ainda.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>

      <div className="flex items-center justify-end gap-2">
        <span className="text-muted-foreground text-sm">
          Página {page + 1} de {Math.max(1, Math.ceil(count / PAGE_SIZE))}
        </span>
        <Button
          variant="outline"
          size="sm"
          disabled={page === 0}
          onClick={() => setPage((p) => p - 1)}
        >
          Anterior
        </Button>
        <Button
          variant="outline"
          size="sm"
          disabled={(page + 1) * PAGE_SIZE >= count}
          onClick={() => setPage((p) => p + 1)}
        >
          Próxima
        </Button>
      </div>

      {openId && (
        <CustomizationDetailDialog
          storeId={storeId}
          sessionId={openId}
          permissions={permissions}
          onClose={() => setOpenId(null)}
        />
      )}
      {assistOpen && (
        <AssistedDialog
          storeId={storeId}
          onClose={() => setAssistOpen(false)}
        />
      )}
    </div>
  )
}

function CustomizationRow({
  row,
  onOpen,
}: {
  row: MerchantSessionListItem
  onOpen: () => void
}) {
  return (
    <TableRow>
      <TableCell>
        {row.snapshot_url ? (
          <img
            src={row.snapshot_url}
            alt={`Arte de ${row.product_name}`}
            className="h-10 w-10 rounded-md border object-cover"
          />
        ) : (
          <div className="h-10 w-10 rounded-md border bg-muted" />
        )}
      </TableCell>
      <TableCell className="font-medium">
        {row.product_name}
        {row.is_assisted && (
          <Badge variant="outline" className="ml-2">
            Assistida
          </Badge>
        )}
      </TableCell>
      <TableCell>
        <Badge variant={SESSION_VARIANT[row.status]}>
          {SESSION_LABEL[row.status]}
        </Badge>
      </TableCell>
      <TableCell className="text-muted-foreground">
        {row.production_status ? PRODUCTION_LABEL[row.production_status] : "—"}
      </TableCell>
      <TableCell className="text-muted-foreground">
        {when(row.updated_at)}
      </TableCell>
      <TableCell className="flex justify-end">
        <Button variant="ghost" size="sm" onClick={onOpen}>
          Ver
        </Button>
      </TableCell>
    </TableRow>
  )
}

export function CustomizationDetailDialog({
  storeId,
  sessionId,
  permissions,
  onClose,
}: {
  storeId: string
  sessionId: string
  permissions: string[]
  onClose: () => void
}) {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const canUpdate = permissions.includes(
    "customization.production_status.update",
  )

  const detailQuery = useQuery({
    queryKey: ["customization", storeId, sessionId],
    queryFn: () =>
      CustomizationService.getCustomization({ storeId, sessionId }),
  })

  const statusMutation = useMutation({
    mutationFn: (next: CustomizationProductionStatus) =>
      CustomizationService.updateProductionStatus({
        storeId,
        sessionId,
        requestBody: { production_status: next },
      }),
    onSuccess: () => {
      showSuccessToast("Status de produção atualizado")
      queryClient.invalidateQueries({
        queryKey: ["customization", storeId, sessionId],
      })
      queryClient.invalidateQueries({ queryKey: ["customizations", storeId] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const detail = detailQuery.data

  return (
    <Dialog open onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="max-h-[90vh] max-w-2xl overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {detail ? detail.product_name : "Personalização"}
          </DialogTitle>
        </DialogHeader>

        {!detail ? (
          <p className="text-muted-foreground text-sm">Carregando…</p>
        ) : (
          <div className="space-y-5">
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant={SESSION_VARIANT[detail.status]}>
                {SESSION_LABEL[detail.status]}
              </Badge>
              {detail.is_assisted && <Badge variant="outline">Assistida</Badge>}
            </div>

            {detail.snapshot_url && (
              <img
                src={detail.snapshot_url}
                alt={`Prévia de ${detail.product_name}`}
                className="mx-auto max-h-72 rounded-md border object-contain"
              />
            )}

            <section className="space-y-2">
              <h3 className="font-semibold text-sm">Baixar arquivos</h3>
              <div className="flex flex-wrap gap-2">
                <DownloadLink
                  url={detail.composite_url}
                  label="Arte de produção (composite)"
                />
                <DownloadLink
                  url={detail.snapshot_url}
                  label="Prévia (mockup)"
                />
                {detail.uploads.map((u, i) => (
                  <DownloadLink
                    key={u.id}
                    url={u.url}
                    label={`Imagem enviada ${i + 1}`}
                  />
                ))}
              </div>
              {!detail.composite_url && (
                <p className="text-muted-foreground text-xs">
                  A arte de produção fica disponível após a aprovação.
                </p>
              )}
            </section>

            <Separator />

            <section className="space-y-2">
              <h3 className="font-semibold text-sm">Produção</h3>
              {detail.order_item_id ? (
                <div className="flex items-center gap-3">
                  <Select
                    value={detail.production_status ?? "received"}
                    disabled={!canUpdate || statusMutation.isPending}
                    onValueChange={(v) =>
                      statusMutation.mutate(v as CustomizationProductionStatus)
                    }
                  >
                    <SelectTrigger className="w-64">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {PRODUCTION_STATUSES.map((s) => (
                        <SelectItem key={s} value={s}>
                          {PRODUCTION_LABEL[s]}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              ) : (
                <p className="text-muted-foreground text-sm">
                  O status de produção fica disponível quando a personalização
                  vira um pedido.
                </p>
              )}
            </section>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}

function DownloadLink({ url, label }: { url: string | null; label: string }) {
  if (!url) return null
  return (
    <a href={url} target="_blank" rel="noreferrer" download>
      <Button variant="outline" size="sm">
        {label}
      </Button>
    </a>
  )
}

const STOREFRONT_URL =
  (import.meta.env.VITE_STOREFRONT_URL as string | undefined) ?? ""

export function AssistedDialog({
  storeId,
  onClose,
}: {
  storeId: string
  onClose: () => void
}) {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [productId, setProductId] = useState("")
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [phone, setPhone] = useState("")
  const [token, setToken] = useState<string | null>(null)

  const productsQuery = useQuery({
    queryKey: ["products-customizable", storeId],
    queryFn: () => CatalogService.listProducts({ storeId, limit: 100 }),
  })
  const customizable = (productsQuery.data?.data ?? []).filter(
    (p) => p.type === "image_3d_customizable",
  )

  const createMutation = useMutation({
    mutationFn: () =>
      CustomizationService.createAssistedSession({
        storeId,
        requestBody: {
          product_id: productId,
          name,
          email: email || null,
          phone: phone || null,
        },
      }),
    onSuccess: (res) => {
      setToken(res.public_token)
      showSuccessToast("Personalização criada — compartilhe o link")
      queryClient.invalidateQueries({ queryKey: ["customizations", storeId] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const publicLink = token ? `${STOREFRONT_URL}/p/${token}` : ""

  return (
    <Dialog open onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Montar personalização (assistida)</DialogTitle>
        </DialogHeader>

        {token ? (
          <div className="space-y-3">
            <p className="text-sm">
              Pronto! Envie este link para o cliente revisar e aprovar:
            </p>
            <div className="flex gap-2">
              <Input readOnly value={publicLink} />
              <Button
                variant="outline"
                onClick={() => {
                  navigator.clipboard.writeText(publicLink)
                  showSuccessToast("Link copiado")
                }}
              >
                Copiar
              </Button>
            </div>
            <Button onClick={onClose}>Concluir</Button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="space-y-1">
              <Label>Produto personalizável</Label>
              <Select value={productId} onValueChange={setProductId}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecione um produto" />
                </SelectTrigger>
                <SelectContent>
                  {customizable.map((p) => (
                    <SelectItem key={p.id} value={p.id}>
                      {p.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {customizable.length === 0 && (
                <p className="text-muted-foreground text-xs">
                  Nenhum produto personalizável. Marque um produto como
                  personalizável primeiro.
                </p>
              )}
            </div>
            <div className="space-y-1">
              <Label>Nome do cliente</Label>
              <Input value={name} onChange={(e) => setName(e.target.value)} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label>E-mail</Label>
                <Input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              <div className="space-y-1">
                <Label>Telefone</Label>
                <Input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                />
              </div>
            </div>
            <p className="text-muted-foreground text-xs">
              O cliente confirma o contato (e-mail ou telefone) para aprovar.
            </p>
            <Button
              disabled={
                !productId ||
                !name.trim() ||
                (!email.trim() && !phone.trim()) ||
                createMutation.isPending
              }
              onClick={() => createMutation.mutate()}
            >
              {createMutation.isPending ? "Criando…" : "Criar e gerar link"}
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
