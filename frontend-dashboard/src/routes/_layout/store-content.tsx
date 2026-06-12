import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"

import {
  type ContentBannerPublic,
  type ContentMenuPublic,
  type ContentPagePublic,
  ContentService,
  MediaService,
  type MenuLocation,
} from "@/client"
import { StoreGate } from "@/components/Store/StoreGate"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogFooter,
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useActiveStore } from "@/hooks/useActiveStore"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

export const Route = createFileRoute("/_layout/store-content")({
  component: StoreContentRoute,
  head: () => ({ meta: [{ title: "Conteúdo da Loja - Kriar" }] }),
})

function StoreContentRoute() {
  return (
    <StoreGate>
      <StoreContentScreen />
    </StoreGate>
  )
}

const TEXTAREA_CLASS =
  "w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"

interface SectionProps {
  storeId: string
  canEdit: boolean
}

function StoreContentScreen() {
  const { activeStore, permissions } = useActiveStore()
  const canEdit = permissions.includes("layout.update")
  const storeId = activeStore?.id ?? ""

  if (!activeStore) {
    return null
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Conteúdo da loja</h1>
        <p className="text-muted-foreground">
          Páginas institucionais, banners e menus da sua vitrine.
        </p>
      </div>

      <Tabs defaultValue="pages">
        <TabsList>
          <TabsTrigger value="pages">Páginas</TabsTrigger>
          <TabsTrigger value="banners">Banners</TabsTrigger>
          <TabsTrigger value="menus">Menus</TabsTrigger>
        </TabsList>
        <TabsContent value="pages">
          <PagesSection storeId={storeId} canEdit={canEdit} />
        </TabsContent>
        <TabsContent value="banners">
          <BannersSection storeId={storeId} canEdit={canEdit} />
        </TabsContent>
        <TabsContent value="menus">
          <MenusSection storeId={storeId} canEdit={canEdit} />
        </TabsContent>
      </Tabs>
    </div>
  )
}

// --- Pages -----------------------------------------------------------------

function PagesSection({ storeId, canEdit }: SectionProps) {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [dialog, setDialog] = useState<{
    page: ContentPagePublic | null
  } | null>(null)

  const pagesQuery = useQuery({
    queryKey: ["content-pages", storeId],
    queryFn: () => ContentService.listPages({ storeId }),
    enabled: storeId !== "",
  })
  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: ["content-pages", storeId] })

  const deleteMutation = useMutation({
    mutationFn: (pageId: string) =>
      ContentService.deletePage({ storeId, pageId }),
    onSuccess: () => {
      showSuccessToast("Página excluída")
      invalidate()
    },
    onError: handleError.bind(showErrorToast),
  })

  const pages = pagesQuery.data ?? []

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0">
        <CardTitle>Páginas</CardTitle>
        {canEdit && (
          <Button size="sm" onClick={() => setDialog({ page: null })}>
            Nova página
          </Button>
        )}
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Slug</TableHead>
              <TableHead>Título</TableHead>
              <TableHead>Publicada</TableHead>
              <TableHead className="w-0" />
            </TableRow>
          </TableHeader>
          <TableBody>
            {pages.map((page) => (
              <TableRow key={page.id}>
                <TableCell className="font-mono">{page.slug}</TableCell>
                <TableCell>{page.title}</TableCell>
                <TableCell>{page.is_published ? "sim" : "não"}</TableCell>
                <TableCell className="flex gap-2">
                  {canEdit && (
                    <>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setDialog({ page })}
                      >
                        Editar
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => deleteMutation.mutate(page.id)}
                      >
                        Excluir
                      </Button>
                    </>
                  )}
                </TableCell>
              </TableRow>
            ))}
            {pages.length === 0 && (
              <TableRow>
                <TableCell colSpan={4} className="text-muted-foreground">
                  Nenhuma página.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </CardContent>
      {dialog && (
        <PageDialog
          storeId={storeId}
          page={dialog.page}
          onClose={() => setDialog(null)}
          onSaved={() => {
            invalidate()
            setDialog(null)
          }}
        />
      )}
    </Card>
  )
}

function PageDialog({
  storeId,
  page,
  onClose,
  onSaved,
}: {
  storeId: string
  page: ContentPagePublic | null
  onClose: () => void
  onSaved: () => void
}) {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [slug, setSlug] = useState(page?.slug ?? "")
  const [title, setTitle] = useState(page?.title ?? "")
  const [body, setBody] = useState(page?.body ?? "")
  const [isPublished, setIsPublished] = useState(page?.is_published ?? false)

  const saveMutation = useMutation({
    mutationFn: () => {
      const requestBody = {
        slug,
        title,
        body: body || null,
        is_published: isPublished,
      }
      return page
        ? ContentService.updatePage({ storeId, pageId: page.id, requestBody })
        : ContentService.createPage({ storeId, requestBody })
    },
    onSuccess: () => {
      showSuccessToast("Página salva")
      onSaved()
    },
    onError: handleError.bind(showErrorToast),
  })

  return (
    <Dialog open onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{page ? "Editar página" : "Nova página"}</DialogTitle>
        </DialogHeader>
        <div className="space-y-3">
          <div className="space-y-1.5">
            <Label htmlFor="page-slug">Slug</Label>
            <Input
              id="page-slug"
              value={slug}
              onChange={(event) => setSlug(event.target.value)}
              placeholder="sobre"
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="page-title">Título</Label>
            <Input
              id="page-title"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="page-body">Conteúdo</Label>
            <textarea
              id="page-body"
              className={TEXTAREA_CLASS}
              rows={8}
              value={body}
              onChange={(event) => setBody(event.target.value)}
              placeholder="Separe os parágrafos com uma linha em branco."
            />
          </div>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={isPublished}
              onChange={(event) => setIsPublished(event.target.checked)}
            />
            Publicada (visível na vitrine)
          </label>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancelar
          </Button>
          <Button
            onClick={() => saveMutation.mutate()}
            disabled={saveMutation.isPending || !slug.trim() || !title.trim()}
          >
            Salvar
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// --- Banners ---------------------------------------------------------------

function BannersSection({ storeId, canEdit }: SectionProps) {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [dialog, setDialog] = useState<{
    banner: ContentBannerPublic | null
  } | null>(null)

  const bannersQuery = useQuery({
    queryKey: ["content-banners", storeId],
    queryFn: () => ContentService.listBanners({ storeId }),
    enabled: storeId !== "",
  })
  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: ["content-banners", storeId] })

  const deleteMutation = useMutation({
    mutationFn: (bannerId: string) =>
      ContentService.deleteBanner({ storeId, bannerId }),
    onSuccess: () => {
      showSuccessToast("Banner excluído")
      invalidate()
    },
    onError: handleError.bind(showErrorToast),
  })

  const banners = bannersQuery.data ?? []

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0">
        <CardTitle>Banners</CardTitle>
        {canEdit && (
          <Button size="sm" onClick={() => setDialog({ banner: null })}>
            Novo banner
          </Button>
        )}
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Imagem</TableHead>
              <TableHead>Título</TableHead>
              <TableHead>Posição</TableHead>
              <TableHead>Ativo</TableHead>
              <TableHead className="w-0" />
            </TableRow>
          </TableHeader>
          <TableBody>
            {banners.map((banner) => (
              <TableRow key={banner.id}>
                <TableCell>
                  <img
                    src={banner.image_url}
                    alt={banner.title ?? "Banner"}
                    className="h-8 w-16 rounded object-cover"
                  />
                </TableCell>
                <TableCell>{banner.title ?? "—"}</TableCell>
                <TableCell>{banner.position}</TableCell>
                <TableCell>{banner.is_active ? "sim" : "não"}</TableCell>
                <TableCell className="flex gap-2">
                  {canEdit && (
                    <>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setDialog({ banner })}
                      >
                        Editar
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => deleteMutation.mutate(banner.id)}
                      >
                        Excluir
                      </Button>
                    </>
                  )}
                </TableCell>
              </TableRow>
            ))}
            {banners.length === 0 && (
              <TableRow>
                <TableCell colSpan={5} className="text-muted-foreground">
                  Nenhum banner.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </CardContent>
      {dialog && (
        <BannerDialog
          storeId={storeId}
          banner={dialog.banner}
          onClose={() => setDialog(null)}
          onSaved={() => {
            invalidate()
            setDialog(null)
          }}
        />
      )}
    </Card>
  )
}

function BannerDialog({
  storeId,
  banner,
  onClose,
  onSaved,
}: {
  storeId: string
  banner: ContentBannerPublic | null
  onClose: () => void
  onSaved: () => void
}) {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [imageUrl, setImageUrl] = useState(banner?.image_url ?? "")
  const [linkUrl, setLinkUrl] = useState(banner?.link_url ?? "")
  const [title, setTitle] = useState(banner?.title ?? "")
  const [isActive, setIsActive] = useState(banner?.is_active ?? true)
  const [position, setPosition] = useState(String(banner?.position ?? 0))

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const media = await MediaService.uploadMedia({
        storeId,
        formData: { file: file as unknown as string, owner_type: "banner" },
      })
      return media.url
    },
    onSuccess: (url) => setImageUrl(url),
    onError: handleError.bind(showErrorToast),
  })

  const saveMutation = useMutation({
    mutationFn: () => {
      const requestBody = {
        image_url: imageUrl,
        link_url: linkUrl || null,
        title: title || null,
        is_active: isActive,
        position: Number(position) || 0,
      }
      return banner
        ? ContentService.updateBanner({
            storeId,
            bannerId: banner.id,
            requestBody,
          })
        : ContentService.createBanner({ storeId, requestBody })
    },
    onSuccess: () => {
      showSuccessToast("Banner salvo")
      onSaved()
    },
    onError: handleError.bind(showErrorToast),
  })

  return (
    <Dialog open onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{banner ? "Editar banner" : "Novo banner"}</DialogTitle>
        </DialogHeader>
        <div className="space-y-3">
          <div className="space-y-1.5">
            <Label>Imagem</Label>
            <div className="flex items-center gap-3">
              <div className="h-16 w-28 overflow-hidden rounded border bg-muted">
                {imageUrl ? (
                  <img
                    src={imageUrl}
                    alt="Banner"
                    className="h-full w-full object-cover"
                  />
                ) : (
                  <div className="flex h-full items-center justify-center text-xs text-muted-foreground">
                    Sem imagem
                  </div>
                )}
              </div>
              <label>
                <input
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={(event) => {
                    const file = event.target.files?.[0]
                    if (file) uploadMutation.mutate(file)
                    event.target.value = ""
                  }}
                />
                <span className="inline-flex cursor-pointer items-center rounded-md border px-3 py-1.5 text-sm hover:bg-muted">
                  {uploadMutation.isPending ? "Enviando…" : "Enviar imagem"}
                </span>
              </label>
            </div>
          </div>
          <div className="space-y-1.5">
            <Label>Título</Label>
            <Input
              value={title}
              onChange={(event) => setTitle(event.target.value)}
            />
          </div>
          <div className="space-y-1.5">
            <Label>Link (URL)</Label>
            <Input
              value={linkUrl}
              onChange={(event) => setLinkUrl(event.target.value)}
              placeholder="/products?category=ofertas"
            />
          </div>
          <div className="space-y-1.5">
            <Label>Posição</Label>
            <Input
              type="number"
              value={position}
              onChange={(event) => setPosition(event.target.value)}
            />
          </div>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={isActive}
              onChange={(event) => setIsActive(event.target.checked)}
            />
            Ativo (visível na vitrine)
          </label>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancelar
          </Button>
          <Button
            onClick={() => saveMutation.mutate()}
            disabled={saveMutation.isPending || !imageUrl}
          >
            Salvar
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// --- Menus -----------------------------------------------------------------

function MenusSection({ storeId, canEdit }: SectionProps) {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [dialog, setDialog] = useState<{
    menu: ContentMenuPublic | null
  } | null>(null)

  const menusQuery = useQuery({
    queryKey: ["content-menus", storeId],
    queryFn: () => ContentService.listMenus({ storeId }),
    enabled: storeId !== "",
  })
  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: ["content-menus", storeId] })

  const deleteMutation = useMutation({
    mutationFn: (menuId: string) =>
      ContentService.deleteMenu({ storeId, menuId }),
    onSuccess: () => {
      showSuccessToast("Menu excluído")
      invalidate()
    },
    onError: handleError.bind(showErrorToast),
  })

  const menus = menusQuery.data ?? []

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0">
        <CardTitle>Menus</CardTitle>
        {canEdit && (
          <Button size="sm" onClick={() => setDialog({ menu: null })}>
            Novo menu
          </Button>
        )}
      </CardHeader>
      <CardContent className="space-y-4">
        {menus.map((menu) => (
          <MenuCard
            key={menu.id}
            storeId={storeId}
            menu={menu}
            canEdit={canEdit}
            onChanged={invalidate}
            onEdit={() => setDialog({ menu })}
            onDelete={() => deleteMutation.mutate(menu.id)}
          />
        ))}
        {menus.length === 0 && (
          <p className="text-sm text-muted-foreground">Nenhum menu.</p>
        )}
      </CardContent>
      {dialog && (
        <MenuDialog
          storeId={storeId}
          menu={dialog.menu}
          onClose={() => setDialog(null)}
          onSaved={() => {
            invalidate()
            setDialog(null)
          }}
        />
      )}
    </Card>
  )
}

function MenuCard({
  storeId,
  menu,
  canEdit,
  onChanged,
  onEdit,
  onDelete,
}: {
  storeId: string
  menu: ContentMenuPublic
  canEdit: boolean
  onChanged: () => void
  onEdit: () => void
  onDelete: () => void
}) {
  const { showErrorToast } = useCustomToast()
  const [label, setLabel] = useState("")
  const [url, setUrl] = useState("")

  const addItem = useMutation({
    mutationFn: () =>
      ContentService.addMenuItem({
        storeId,
        menuId: menu.id,
        requestBody: { label, url, position: menu.items?.length ?? 0 },
      }),
    onSuccess: () => {
      setLabel("")
      setUrl("")
      onChanged()
    },
    onError: handleError.bind(showErrorToast),
  })

  const removeItem = useMutation({
    mutationFn: (itemId: string) =>
      ContentService.deleteMenuItem({ storeId, itemId }),
    onSuccess: onChanged,
    onError: handleError.bind(showErrorToast),
  })

  return (
    <div className="rounded-lg border p-3">
      <div className="flex items-center justify-between">
        <div className="font-medium">
          {menu.name}{" "}
          <span className="text-xs text-muted-foreground">
            ({menu.location})
          </span>
        </div>
        {canEdit && (
          <div className="flex gap-2">
            <Button variant="ghost" size="sm" onClick={onEdit}>
              Renomear
            </Button>
            <Button variant="ghost" size="sm" onClick={onDelete}>
              Excluir
            </Button>
          </div>
        )}
      </div>

      <ul className="mt-2 space-y-1">
        {(menu.items ?? []).map((item) => (
          <li
            key={item.id}
            className="flex items-center justify-between text-sm"
          >
            <span>
              {item.label}{" "}
              <span className="text-muted-foreground">→ {item.url}</span>
            </span>
            {canEdit && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => removeItem.mutate(item.id)}
              >
                Remover
              </Button>
            )}
          </li>
        ))}
        {(menu.items ?? []).length === 0 && (
          <li className="text-sm text-muted-foreground">Sem itens.</li>
        )}
      </ul>

      {canEdit && (
        <div className="mt-3 flex flex-wrap items-end gap-2">
          <div className="space-y-1">
            <Label className="text-xs">Texto</Label>
            <Input
              value={label}
              onChange={(event) => setLabel(event.target.value)}
              placeholder="Sobre"
              className="h-8 w-32"
            />
          </div>
          <div className="space-y-1">
            <Label className="text-xs">URL</Label>
            <Input
              value={url}
              onChange={(event) => setUrl(event.target.value)}
              placeholder="/pages/sobre"
              className="h-8 w-48"
            />
          </div>
          <Button
            size="sm"
            disabled={addItem.isPending || !label.trim() || !url.trim()}
            onClick={() => addItem.mutate()}
          >
            Adicionar
          </Button>
        </div>
      )}
    </div>
  )
}

function MenuDialog({
  storeId,
  menu,
  onClose,
  onSaved,
}: {
  storeId: string
  menu: ContentMenuPublic | null
  onClose: () => void
  onSaved: () => void
}) {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [name, setName] = useState(menu?.name ?? "")
  const [location, setLocation] = useState<MenuLocation>(
    menu?.location ?? "header",
  )

  const saveMutation = useMutation({
    mutationFn: () => {
      const requestBody = { name, location }
      return menu
        ? ContentService.updateMenu({ storeId, menuId: menu.id, requestBody })
        : ContentService.createMenu({ storeId, requestBody })
    },
    onSuccess: () => {
      showSuccessToast("Menu salvo")
      onSaved()
    },
    onError: handleError.bind(showErrorToast),
  })

  return (
    <Dialog open onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{menu ? "Editar menu" : "Novo menu"}</DialogTitle>
        </DialogHeader>
        <div className="space-y-3">
          <div className="space-y-1.5">
            <Label>Nome</Label>
            <Input
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="Rodapé"
            />
          </div>
          <div className="space-y-1.5">
            <Label>Local</Label>
            <Select
              value={location}
              onValueChange={(value) => setLocation(value as MenuLocation)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="header">Cabeçalho</SelectItem>
                <SelectItem value="footer">Rodapé</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancelar
          </Button>
          <Button
            onClick={() => saveMutation.mutate()}
            disabled={saveMutation.isPending || !name.trim()}
          >
            Salvar
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
