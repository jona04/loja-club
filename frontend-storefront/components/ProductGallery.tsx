"use client"

import { useState } from "react"

import type { ProductImage } from "@/lib/api"

/**
 * Interactive product gallery: a large image with selectable thumbnails.
 *
 * @param images - The product images (first shown by default).
 * @param alt - Accessible label for the main image.
 * @returns The gallery.
 */
export function ProductGallery({
  images,
  alt,
}: {
  images: ProductImage[]
  alt: string
}) {
  const [active, setActive] = useState(0)
  const main = images[active]
  return (
    <div>
      <div className="aspect-square overflow-hidden rounded-2xl bg-gray-100">
        {main ? (
          <img
            src={main.url}
            alt={alt}
            className="h-full w-full object-cover"
          />
        ) : (
          <div className="flex h-full items-center justify-center text-sm text-gray-400">
            sem imagem
          </div>
        )}
      </div>
      {images.length > 1 ? (
        <div className="mt-3 flex flex-wrap gap-2">
          {images.map((image, index) => (
            <button
              key={image.url}
              type="button"
              onClick={() => setActive(index)}
              aria-label={`Imagem ${index + 1}`}
              className={`h-16 w-16 overflow-hidden rounded-lg border-2 transition ${
                index === active
                  ? "border-gray-900"
                  : "border-transparent opacity-60 hover:opacity-100"
              }`}
            >
              <img
                src={image.url}
                alt=""
                className="h-full w-full object-cover"
              />
            </button>
          ))}
        </div>
      ) : null}
    </div>
  )
}
