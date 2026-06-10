import { getCategories, getHome } from "@/lib/api"
import { resolveTemplate } from "@/lib/templates"

const PAGES: Record<string, { title: string; body: string[] }> = {
  sobre: {
    title: "Sobre a loja",
    body: [
      "Trabalhamos todos os dias para oferecer produtos selecionados, um atendimento próximo e uma experiência de compra simples e segura.",
      "Obrigado por visitar a nossa loja — é um prazer ter você por aqui. Qualquer dúvida, fale com a gente.",
    ],
  },
  privacidade: {
    title: "Política de Privacidade",
    body: [
      "A sua privacidade é importante para nós. Os dados que você compartilha são usados apenas para processar e acompanhar os seus pedidos e para melhorar a sua experiência de compra.",
      "Não vendemos os seus dados a terceiros. Em caso de dúvidas sobre como tratamos as suas informações, entre em contato com o nosso atendimento.",
    ],
  },
  termos: {
    title: "Termos de Uso",
    body: [
      "Ao navegar e comprar em nossa loja, você concorda com as condições desta página. Buscamos sempre clareza nas informações de produtos, preços e prazos.",
      "Em caso de dúvidas sobre um pedido, prazos ou condições, entre em contato com o nosso atendimento antes de finalizar a compra.",
    ],
  },
  trocas: {
    title: "Trocas e Devoluções",
    body: [
      "Quer trocar ou devolver um produto? É simples: entre em contato com o nosso atendimento e nós orientamos todo o processo, do começo ao fim.",
      "Trabalhamos para que a sua compra seja sempre tranquila — antes, durante e depois da entrega.",
    ],
  },
}

const FALLBACK = {
  title: "Página",
  body: [
    "Estamos preparando o conteúdo desta página. Enquanto isso, fique à vontade para explorar os nossos produtos.",
  ],
}

/**
 * Institutional page: presentable default copy inside the active template's
 * shell. The merchant's own content arrives with editable `content_pages` in a
 * later task.
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
  const page = PAGES[slug] ?? FALLBACK

  return (
    <Template.Shell
      store={home.store}
      categories={categories}
      locale={home.store.locale}
    >
      <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6 lg:px-8">
        <h1 className="mb-8 text-3xl font-semibold tracking-tight text-gray-900">
          {page.title}
        </h1>
        <div className="space-y-4 text-sm leading-relaxed text-gray-600">
          {page.body.map((paragraph) => (
            <p key={paragraph}>{paragraph}</p>
          ))}
        </div>
      </div>
    </Template.Shell>
  )
}
