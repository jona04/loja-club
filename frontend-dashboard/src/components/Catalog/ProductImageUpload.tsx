import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { type ChangeEvent, useRef } from "react"

import { CatalogService, MediaService } from "@/client"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

interface ProductImageUploadProps {
  storeId: string
  productId: string
  canEdit: boolean
}

/**
 * Upload and manage a product's images.
 *
 * Lists the product's images (each with its CDN URL and processing status) and
 * uploads new ones (file → media pipeline → linked to the product). While any
 * image is still `processing` (the worker is building its variants), the list
 * is polled until every image is `ready`.
 *
 * @param props - Active store id, product id and whether the member can edit.
 * @returns The image management widget.
 */
export function ProductImageUpload({
  storeId,
  productId,
  canEdit,
}: ProductImageUploadProps) {
  const queryClient = useQueryClient()
  const { showErrorToast } = useCustomToast()
  const fileRef = useRef<HTMLInputElement>(null)

  const imagesQuery = useQuery({
    queryKey: ["product-images", storeId, productId],
    queryFn: () => CatalogService.listImages({ storeId, productId }),
    refetchInterval: (query) =>
      query.state.data?.some((image) => image.status === "processing")
        ? 2000
        : false,
  })

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const media = await MediaService.uploadMedia({
        storeId,
        formData: { file: file as unknown as string, owner_type: "product" },
      })
      await CatalogService.attachImage({
        storeId,
        productId,
        requestBody: {
          media_file_id: media.id,
          position: imagesQuery.data?.length ?? 0,
        },
      })
    },
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: ["product-images", storeId, productId],
      }),
    onError: handleError.bind(showErrorToast),
  })

  const onPick = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      uploadMutation.mutate(file)
    }
    event.target.value = ""
  }

  const images = imagesQuery.data ?? []

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="font-medium text-sm">Imagens ({images.length})</span>
        {canEdit && (
          <>
            <input
              ref={fileRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={onPick}
            />
            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled={uploadMutation.isPending}
              onClick={() => fileRef.current?.click()}
            >
              {uploadMutation.isPending ? "Enviando…" : "Adicionar imagem"}
            </Button>
          </>
        )}
      </div>
      {images.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {images.map((image) => (
            <div key={image.id} className="relative">
              <img
                src={image.variants?.thumbnail ?? image.url}
                alt=""
                className="h-16 w-16 rounded object-cover"
              />
              {image.status === "processing" && (
                <Badge
                  variant="secondary"
                  className="-bottom-1 absolute left-0 text-[10px]"
                >
                  processando
                </Badge>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
