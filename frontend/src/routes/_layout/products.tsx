import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { type ReactNode, useState } from "react"

import { CatalogService, type ProductPublic } from "@/client"
import { ProductImageUpload } from "@/components/Catalog/ProductImageUpload"
import { StoreGate } from "@/components/Store/StoreGate"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
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

export const Route = createFileRoute("/_layout/products")({
  component: ProductsRoute,
  head: () => ({
    meta: [{ title: "Produtos - Loja Club" }],
  }),
})

function ProductsRoute() {
  return (
    <StoreGate>
      <ProductsScreen />
    </StoreGate>
  )
}

/** Page-size options for the products list. */
const PAGE_SIZE_OPTIONS = [10, 20, 50, 100]

/** Convert a major-unit amount string (e.g. "15.50") to minor units (cents). */
const toMinor = (major: string): number =>
  Math.round((Number.parseFloat(major) || 0) * 100)

/** Format minor units as a 2-decimal major-unit string. */
const fromMinor = (minor: number): string => (minor / 100).toFixed(2)

/**
 * The merchant Products screen: list, create, edit, publish/unpublish and
 * archive products, set stock and upload images — all gated by `catalog.*`
 * (UI gating only; the backend enforces the real authorization).
 *
 * @returns The Products management screen.
 */
export function ProductsScreen() {
  const { activeStore, permissions } = useActiveStore()
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [createOpen, setCreateOpen] = useState(false)
  const [editing, setEditing] = useState<ProductPublic | null>(null)
  const [page, setPage] = useState(0)
  const [pageSize, setPageSize] = useState(20)
  const [form, setForm] = useState({
    name: "",
    price: "",
    description: "",
    featured: false,
  })

  const storeId = activeStore?.id ?? ""
  const canView = permissions.includes("catalog.product.view")
  const canCreate = permissions.includes("catalog.product.create")
  const canUpdate = permissions.includes("catalog.product.update")
  const canArchive = permissions.includes("catalog.product.archive")

  const productsQuery = useQuery({
    queryKey: ["products", storeId, page, pageSize],
    queryFn: () =>
      CatalogService.listProducts({
        storeId,
        skip: page * pageSize,
        limit: pageSize,
      }),
    enabled: storeId !== "" && canView,
  })

  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: ["products", storeId] })

  const createMutation = useMutation({
    mutationFn: () =>
      CatalogService.createProduct({
        storeId,
        requestBody: {
          name: form.name,
          description: form.description || null,
          price_amount_minor: toMinor(form.price),
          is_featured: form.featured,
        },
      }),
    onSuccess: (created) => {
      showSuccessToast("Produto criado")
      invalidate()
      setCreateOpen(false)
      setForm({ name: "", price: "", description: "", featured: false })
      // Continue straight into the product's details (image, stock) — these
      // need the product to exist first (FK), so they live in the edit dialog.
      setEditing(created)
    },
    onError: handleError.bind(showErrorToast),
  })

  const publishMutation = useMutation({
    mutationFn: (vars: { id: string; publish: boolean }) =>
      vars.publish
        ? CatalogService.publishProduct({ storeId, productId: vars.id })
        : CatalogService.unpublishProduct({ storeId, productId: vars.id }),
    onSuccess: invalidate,
    onError: handleError.bind(showErrorToast),
  })

  const archiveMutation = useMutation({
    mutationFn: (id: string) =>
      CatalogService.archiveProduct({ storeId, productId: id }),
    onSuccess: () => {
      showSuccessToast("Produto arquivado")
      invalidate()
    },
    onError: handleError.bind(showErrorToast),
  })

  if (!activeStore) {
    return null
  }

  const products = productsQuery.data?.data ?? []
  const count = productsQuery.data?.count ?? 0
  const totalPages = Math.max(1, Math.ceil(count / pageSize))

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-bold text-2xl tracking-tight">Produtos</h1>
          <p className="text-muted-foreground">
            {productsQuery.data?.count ?? 0} produto(s) em {activeStore.name}
          </p>
        </div>
        <Dialog open={createOpen} onOpenChange={setCreateOpen}>
          <DialogTrigger asChild>
            <Button disabled={!canCreate}>Novo produto</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Novo produto</DialogTitle>
            </DialogHeader>
            <div className="space-y-3">
              <Field label="Nome">
                <Input
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                />
              </Field>
              <Field label="Preço">
                <Input
                  type="number"
                  step="0.01"
                  min="0"
                  value={form.price}
                  onChange={(e) => setForm({ ...form, price: e.target.value })}
                />
              </Field>
              <Field label="Descrição">
                <Input
                  value={form.description}
                  onChange={(e) =>
                    setForm({ ...form, description: e.target.value })
                  }
                />
              </Field>
              <div className="flex items-center gap-2">
                <Checkbox
                  id="create-featured"
                  checked={form.featured}
                  onCheckedChange={(v) =>
                    setForm({ ...form, featured: v === true })
                  }
                />
                <Label htmlFor="create-featured">Destaque</Label>
              </div>
            </div>
            <DialogFooter>
              <Button
                onClick={() => createMutation.mutate()}
                disabled={!form.name.trim() || createMutation.isPending}
              >
                Criar
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Nome</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Preço</TableHead>
            <TableHead className="w-0" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {products.map((product) => (
            <TableRow key={product.id}>
              <TableCell>
                {product.name}
                {product.is_featured && (
                  <Badge variant="secondary" className="ml-2">
                    destaque
                  </Badge>
                )}
              </TableCell>
              <TableCell>
                <Badge
                  variant={
                    product.status === "published" ? "default" : "outline"
                  }
                >
                  {product.status}
                </Badge>
              </TableCell>
              <TableCell>
                {product.price_currency} {fromMinor(product.price_amount_minor)}
              </TableCell>
              <TableCell className="flex justify-end gap-1">
                {canUpdate && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setEditing(product)}
                  >
                    Editar
                  </Button>
                )}
                {canUpdate && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() =>
                      publishMutation.mutate({
                        id: product.id,
                        publish: product.status !== "published",
                      })
                    }
                  >
                    {product.status === "published"
                      ? "Despublicar"
                      : "Publicar"}
                  </Button>
                )}
                {canArchive && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => archiveMutation.mutate(product.id)}
                  >
                    Arquivar
                  </Button>
                )}
              </TableCell>
            </TableRow>
          ))}
          {products.length === 0 && (
            <TableRow>
              <TableCell colSpan={4} className="text-muted-foreground">
                Nenhum produto.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-muted-foreground text-sm">
            Itens por página
          </span>
          <Select
            value={String(pageSize)}
            onValueChange={(v) => {
              setPageSize(Number(v))
              setPage(0)
            }}
          >
            <SelectTrigger className="w-20">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {PAGE_SIZE_OPTIONS.map((size) => (
                <SelectItem key={size} value={String(size)}>
                  {size}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-muted-foreground text-sm">
            Página {page + 1} de {totalPages}
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
            disabled={(page + 1) * pageSize >= count}
            onClick={() => setPage((p) => p + 1)}
          >
            Próxima
          </Button>
        </div>
      </div>

      {editing && (
        <EditProductDialog
          storeId={storeId}
          product={editing}
          canUpdate={canUpdate}
          onClose={() => setEditing(null)}
          onSaved={invalidate}
        />
      )}
    </div>
  )
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="space-y-1.5">
      <Label>{label}</Label>
      {children}
    </div>
  )
}

export function EditProductDialog({
  storeId,
  product,
  canUpdate,
  onClose,
  onSaved,
}: {
  storeId: string
  product: ProductPublic
  canUpdate: boolean
  onClose: () => void
  onSaved: () => void
}) {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [name, setName] = useState(product.name)
  const [price, setPrice] = useState(fromMinor(product.price_amount_minor))
  const [description, setDescription] = useState(product.description ?? "")
  const [featured, setFeatured] = useState(product.is_featured ?? false)
  const [stock, setStock] = useState<string | null>(null)

  const inventoryQuery = useQuery({
    queryKey: ["inventory", storeId, product.id],
    queryFn: () =>
      CatalogService.getInventory({ storeId, productId: product.id }),
  })
  const loadedStock = inventoryQuery.data?.quantity ?? null
  // Show the user's input, falling back to the persisted quantity.
  const stockValue = stock ?? (loadedStock !== null ? String(loadedStock) : "")

  // One save: the product fields, plus the stock when the user changed it.
  const saveMutation = useMutation({
    mutationFn: async () => {
      await CatalogService.updateProduct({
        storeId,
        productId: product.id,
        requestBody: {
          name,
          description: description || null,
          price_amount_minor: toMinor(price),
          is_featured: featured,
        },
      })
      const quantity = Number.parseInt(stockValue || "0", 10)
      if (stock !== null && stockValue !== "" && quantity !== loadedStock) {
        await CatalogService.setInventory({
          storeId,
          productId: product.id,
          requestBody: { quantity },
        })
      }
    },
    onSuccess: () => {
      showSuccessToast("Produto atualizado")
      onSaved()
      onClose()
    },
    onError: handleError.bind(showErrorToast),
  })

  return (
    <Dialog open onOpenChange={(o) => !o && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Editar produto</DialogTitle>
        </DialogHeader>
        <div className="space-y-3">
          <Field label="Nome">
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={!canUpdate}
            />
          </Field>
          <Field label="Preço">
            <Input
              type="number"
              step="0.01"
              min="0"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              disabled={!canUpdate}
            />
          </Field>
          <Field label="Descrição">
            <Input
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              disabled={!canUpdate}
            />
          </Field>
          <div className="flex items-center gap-2">
            <Checkbox
              id="edit-featured"
              checked={featured}
              onCheckedChange={(v) => setFeatured(v === true)}
              disabled={!canUpdate}
            />
            <Label htmlFor="edit-featured">Destaque</Label>
          </div>
          <Field label="Estoque">
            <Input
              type="number"
              min="0"
              value={stockValue}
              placeholder="quantidade"
              onChange={(e) => setStock(e.target.value)}
              disabled={!canUpdate}
            />
          </Field>
          <ProductImageUpload
            storeId={storeId}
            productId={product.id}
            canEdit={canUpdate}
          />
        </div>
        <DialogFooter>
          <Button
            onClick={() => saveMutation.mutate()}
            disabled={!canUpdate || saveMutation.isPending}
          >
            Salvar
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
