import Link from "next/link"

import type { HomeProps } from "@/lib/template-types"

import { AuroraProductCard } from "./AuroraProductCard"
import { AuroraShell } from "./Shell"

/**
 * Aurora home (faithful to the template): full-bleed hero, circular category
 * strip, the "Novidades Selecionadas" grid (hover "Adicionar"), an editorial
 * band and trust indicators.
 *
 * @param home - Store identity, theme and highlights.
 * @param categories - Categories for the strip.
 * @returns The rendered Aurora home.
 */
export function Home({ home, categories }: HomeProps) {
  const { store, theme, featured_products: featured } = home
  const headline = theme.headline || "A Essência do Minimalismo"

  return (
    <AuroraShell store={store} categories={categories} locale={store.locale}>
      <section className="group relative h-[600px] w-full overflow-hidden bg-gray-100 md:h-[700px] lg:h-[800px]">
        {theme.banner_image_url ? (
          <img
            src={theme.banner_image_url}
            alt=""
            className="h-full w-full object-cover object-center transition-transform duration-1000 group-hover:scale-105"
          />
        ) : (
          <div className="h-full w-full bg-brand-900" />
        )}
        <div className="absolute inset-0 bg-black/20" />
        <div className="absolute inset-0 flex flex-col items-center justify-center px-4 text-center">
          <h1 className="mb-4 text-4xl font-light tracking-tight text-white drop-shadow-sm md:text-5xl lg:text-6xl">
            {headline}
          </h1>
          <p className="mb-8 max-w-2xl text-lg font-light text-white/90 drop-shadow-sm md:text-xl">
            {store.description ||
              "Descubra nossa nova coleção de peças atemporais desenhadas para trazer calma e sofisticação ao seu espaço."}
          </p>
          <Link
            href="/products"
            className="inline-block bg-white px-8 py-4 text-sm font-medium tracking-wide text-brand-900 shadow-lg transition-colors hover:bg-gray-100"
          >
            Explorar Coleção
          </Link>
        </div>
        <div className="absolute bottom-8 left-1/2 flex -translate-x-1/2 space-x-2">
          <div className="h-1 w-12 rounded-full bg-white" />
          <div className="h-1 w-2 rounded-full bg-white/50" />
          <div className="h-1 w-2 rounded-full bg-white/50" />
        </div>
      </section>

      {categories.length ? (
        <section className="border-b border-gray-50 bg-white py-16">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="no-scrollbar flex space-x-8 overflow-x-auto pb-4 md:space-x-12 lg:justify-center">
              {categories.map((category) => (
                <Link
                  key={category.id}
                  href={`/categories/${category.slug}`}
                  className="group flex w-24 flex-shrink-0 flex-col items-center md:w-32"
                >
                  <span className="mb-4 grid h-20 w-20 place-items-center overflow-hidden rounded-full bg-gray-50 text-2xl font-light text-brand-900 transition-transform duration-300 group-hover:-translate-y-1 group-hover:shadow-md md:h-24 md:w-24">
                    {category.name.charAt(0).toUpperCase()}
                  </span>
                  <span className="text-center text-xs font-medium text-gray-700 group-hover:text-brand-900 md:text-sm">
                    {category.name}
                  </span>
                </Link>
              ))}
            </div>
          </div>
        </section>
      ) : null}

      <section className="bg-white py-20 md:py-28">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mb-12 flex items-center justify-between">
            <h2 className="text-2xl font-semibold tracking-tight text-brand-900 md:text-3xl">
              Novidades Selecionadas
            </h2>
            <Link
              href="/products"
              className="hidden items-center text-sm font-medium text-gray-600 transition-colors hover:text-brand-900 md:inline-flex"
            >
              Ver todos <i className="fa-solid fa-arrow-right ml-2 text-xs" />
            </Link>
          </div>
          {featured.length ? (
            <div className="grid grid-cols-2 gap-x-6 gap-y-12 sm:gap-y-16 lg:grid-cols-4">
              {featured.map((product, i) => (
                <AuroraProductCard
                  key={product.id}
                  product={product}
                  locale={store.locale}
                  badge={i === 0}
                />
              ))}
            </div>
          ) : (
            <div className="rounded-sm border border-dashed border-gray-200 py-16 text-center">
              <p className="text-gray-500">Novidades em breve por aqui.</p>
            </div>
          )}
          <div className="mt-12 text-center md:hidden">
            <Link
              href="/products"
              className="inline-flex w-full items-center justify-center rounded-sm border border-gray-300 px-6 py-3 text-sm font-medium text-brand-900 hover:bg-gray-50"
            >
              Ver todos os produtos
            </Link>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-12 sm:px-6 md:py-20 lg:px-8">
        <div className="relative overflow-hidden rounded-sm bg-brand-50">
          <div className="grid grid-cols-1 items-center md:grid-cols-2">
            <div className="order-2 flex flex-col justify-center p-10 md:order-1 md:p-16 lg:p-24">
              <span className="mb-4 block text-xs font-bold uppercase tracking-widest text-gray-500">
                Coleção em destaque
              </span>
              <h2 className="mb-6 text-3xl font-light leading-tight text-brand-900 md:text-4xl">
                Peças atemporais,
                <br />
                escolhidas a dedo
              </h2>
              <p className="mb-8 max-w-md text-gray-600">
                Uma curadoria de produtos pensada para trazer aconchego e
                personalidade ao seu dia a dia, com qualidade que dura.
              </p>
              <div>
                <Link
                  href="/products"
                  className="inline-flex items-center border-b border-brand-900 pb-1 text-sm font-medium text-brand-900 transition-colors hover:border-gray-600 hover:text-gray-600"
                >
                  Explorar a coleção completa
                </Link>
              </div>
            </div>
            <div className="order-1 h-[400px] w-full md:order-2 md:h-full">
              {theme.banner_image_url ? (
                <img
                  src={theme.banner_image_url}
                  alt=""
                  className="h-full w-full object-cover"
                />
              ) : (
                <div className="h-full w-full bg-brand-100" />
              )}
            </div>
          </div>
        </div>
      </section>

      <section className="border-t border-gray-100 py-12">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 gap-y-8 text-center sm:grid-cols-3 sm:gap-x-8 sm:text-left">
            {[
              {
                icon: "fa-truck-fast",
                title: "Entrega para todo o Brasil",
                text: "Enviamos com opções de entrega rápida e segura.",
              },
              {
                icon: "fa-shield-halved",
                title: "Compra Segura",
                text: "Ambiente protegido e seus dados sempre seguros.",
              },
              {
                icon: "fa-rotate-left",
                title: "Troca Facilitada",
                text: "Até 30 dias para devolução ou troca sem complicações.",
              },
            ].map((item) => (
              <div
                key={item.icon}
                className="flex flex-col items-center gap-4 sm:flex-row sm:items-start"
              >
                <div className="text-2xl text-gray-400">
                  <i className={`fa-solid ${item.icon}`} />
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-brand-900">
                    {item.title}
                  </h4>
                  <p className="mt-1 text-sm text-gray-500">{item.text}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </AuroraShell>
  )
}
