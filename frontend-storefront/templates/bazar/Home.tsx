import Link from "next/link"

import type { HomeProps } from "@/lib/template-types"

import { BazarProductCard } from "./BazarProductCard"
import { BazarShell } from "./Shell"

const TILE_COLORS = [
  "bg-blue-50 text-blue-500 group-hover:bg-blue-500",
  "bg-rose-50 text-rose-500 group-hover:bg-rose-500",
  "bg-emerald-50 text-emerald-500 group-hover:bg-emerald-500",
  "bg-purple-50 text-purple-500 group-hover:bg-purple-500",
  "bg-amber-50 text-amber-500 group-hover:bg-amber-500",
  "bg-pink-50 text-pink-500 group-hover:bg-pink-500",
  "bg-cyan-50 text-cyan-500 group-hover:bg-cyan-500",
  "bg-orange-50 text-orange-500 group-hover:bg-orange-500",
]

/**
 * Bazar home (faithful to the template): a bold hero, a colorful category strip
 * and per-category sections (the marketplace signature), then a closing CTA.
 *
 * @param home - Store identity, theme, highlights and category sections.
 * @param categories - Categories for the strip.
 * @returns The rendered Bazar home.
 */
export function Home({ home, categories }: HomeProps) {
  const { store, theme, featured_products: featured, category_sections } = home
  const sections = category_sections

  return (
    <BazarShell store={store} categories={categories} locale={store.locale}>
      <section className="bg-white pb-8">
        <div className="mx-auto mt-4 max-w-[1400px] px-4 sm:px-6 lg:px-8">
          <div className="group relative h-[300px] w-full overflow-hidden rounded-3xl shadow-float md:h-[450px] lg:h-[500px]">
            {theme.banner_image_url ? (
              <img
                src={theme.banner_image_url}
                alt=""
                className="h-full w-full object-cover"
              />
            ) : (
              <div className="h-full w-full bg-gradient-to-r from-indigo-600 to-indigo-900" />
            )}
            <div className="absolute inset-0 flex items-center bg-gradient-to-r from-black/60 via-black/40 to-transparent">
              <div className="max-w-2xl p-8 text-white md:p-16">
                <span className="mb-4 inline-block rounded-md bg-rose-500 px-3 py-1 text-xs font-bold uppercase tracking-wider text-white">
                  Oferta Especial
                </span>
                <h1 className="mb-4 text-4xl font-extrabold leading-tight md:text-5xl lg:text-6xl">
                  {theme.headline || "Festival de Ofertas"}
                </h1>
                <p className="mb-8 max-w-lg text-lg text-gray-100 opacity-90 md:text-xl">
                  {store.description ||
                    "Descubra milhares de produtos com preços imbatíveis. Renove sua casa, seu estilo e sua vida."}
                </p>
                <Link
                  href="/products"
                  className="inline-flex items-center gap-2 rounded-xl bg-white px-8 py-4 font-bold text-indigo-900 shadow-xl transition-all hover:scale-105 hover:bg-gray-50"
                >
                  Aproveitar Ofertas <i className="fa-solid fa-arrow-right" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {categories.length ? (
        <section className="border-b border-gray-100 bg-white py-8">
          <div className="mx-auto max-w-[1400px] px-4 sm:px-6 lg:px-8">
            <h2 className="mb-4 text-lg font-bold text-gray-900">
              Explore por Categorias
            </h2>
            <div className="hide-scrollbar flex gap-4 overflow-x-auto pb-4 sm:gap-6">
              {categories.map((category, i) => (
                <Link
                  key={category.id}
                  href={`/categories/${category.slug}`}
                  className="group flex min-w-[80px] flex-col items-center gap-3"
                >
                  <div
                    className={`flex h-16 w-16 items-center justify-center rounded-2xl text-2xl transition-all duration-300 group-hover:text-white group-hover:shadow-lg sm:h-20 sm:w-20 ${
                      TILE_COLORS[i % TILE_COLORS.length]
                    }`}
                  >
                    <i className="fa-solid fa-tag" />
                  </div>
                  <span className="text-center text-xs font-medium leading-tight text-gray-700 sm:text-sm">
                    {category.name}
                  </span>
                </Link>
              ))}
            </div>
          </div>
        </section>
      ) : null}

      {sections.length ? (
        sections.map((section, i) => (
          <section
            key={section.category.id}
            className={`py-12 ${i % 2 === 0 ? "bg-gray-50" : "bg-white"}`}
          >
            <div className="mx-auto max-w-[1400px] px-4 sm:px-6 lg:px-8">
              <div className="mb-8 flex items-end justify-between">
                <div>
                  <h2 className="flex items-center gap-3 text-2xl font-extrabold text-gray-900 md:text-3xl">
                    <i className="fa-solid fa-bolt text-xl text-indigo-500" />{" "}
                    {section.category.name}
                  </h2>
                  {section.category.description ? (
                    <p className="mt-2 text-gray-500">
                      {section.category.description}
                    </p>
                  ) : null}
                </div>
                <Link
                  href={`/categories/${section.category.slug}`}
                  className="hidden items-center gap-2 font-bold text-indigo-600 transition hover:text-indigo-800 sm:inline-flex"
                >
                  Ver todos <i className="fa-solid fa-arrow-right-long" />
                </Link>
              </div>
              <div className="grid grid-cols-2 gap-4 md:grid-cols-4 lg:grid-cols-5 lg:gap-6">
                {section.products.map((product, j) => (
                  <BazarProductCard
                    key={product.id}
                    product={product}
                    locale={store.locale}
                    badge={j === 0}
                  />
                ))}
              </div>
            </div>
          </section>
        ))
      ) : (
        <section className="bg-gray-50 py-12">
          <div className="mx-auto max-w-[1400px] px-4 sm:px-6 lg:px-8">
            <h2 className="mb-8 text-2xl font-extrabold text-gray-900 md:text-3xl">
              Destaques
            </h2>
            {featured.length ? (
              <div className="grid grid-cols-2 gap-4 md:grid-cols-4 lg:grid-cols-5 lg:gap-6">
                {featured.map((product, j) => (
                  <BazarProductCard
                    key={product.id}
                    product={product}
                    locale={store.locale}
                    badge={j === 0}
                  />
                ))}
              </div>
            ) : (
              <p className="text-gray-500">Novidades em breve por aqui.</p>
            )}
          </div>
        </section>
      )}

      <section className="bg-white py-16">
        <div className="mx-auto max-w-2xl px-4 text-center sm:px-6">
          <div className="mb-6 inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-indigo-50 text-3xl text-indigo-500">
            <i className="fa-solid fa-boxes-stacked" />
          </div>
          <h2 className="mb-4 text-3xl font-extrabold text-gray-900">
            Procurando algo específico?
          </h2>
          <p className="mb-8 text-lg text-gray-500">
            Temos dezenas de categorias e milhares de produtos esperando por
            você.
          </p>
          <Link
            href="/products"
            className="inline-flex w-full items-center justify-center gap-3 rounded-xl bg-gray-900 px-8 py-4 text-lg font-bold text-white shadow-lg transition-colors hover:bg-indigo-600 sm:w-auto"
          >
            Ver todas as categorias <i className="fa-solid fa-grip" />
          </Link>
        </div>
      </section>
    </BazarShell>
  )
}
