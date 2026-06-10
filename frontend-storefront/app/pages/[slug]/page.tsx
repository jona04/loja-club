import { getCategories, getHome } from "@/lib/api"
import { resolveTemplate } from "@/lib/templates"

const TITLES: Record<string, string> = {
  sobre: "Sobre a loja",
  privacidade: "Política de Privacidade",
  termos: "Termos de Uso",
  trocas: "Trocas e Devoluções",
}

const LOREM =
  "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."

/**
 * Institutional page (placeholder): lorem content inside the active template's
 * shell. The merchant will fill these via the dashboard in a later task.
 *
 * @param params - Route params carrying the page `slug`.
 * @returns The institutional page.
 */
export default async function InstitutionalPage({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  const [home, categories] = await Promise.all([getHome(), getCategories()])
  const Template = resolveTemplate(home.theme.active_template_id)
  const title = TITLES[slug] ?? "Página"

  return (
    <Template.Shell
      store={home.store}
      categories={categories}
      locale={home.store.locale}
    >
      <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6 lg:px-8">
        <h1 className="mb-8 text-3xl font-semibold tracking-tight text-gray-900">
          {title}
        </h1>
        <div className="space-y-4 text-sm leading-relaxed text-gray-600">
          <p>{LOREM}</p>
          <p>{LOREM}</p>
          <p>{LOREM}</p>
        </div>
        <p className="mt-10 text-xs text-gray-400">
          Conteúdo de exemplo — o lojista poderá editar esta página pelo painel.
        </p>
      </div>
    </Template.Shell>
  )
}
