/**
 * Shown when the host resolves to no published store, or a resource is missing.
 *
 * @returns The friendly "loja não encontrada" page.
 */
export default function NotFound() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-3 px-4 text-center">
      <h1 className="text-2xl font-semibold">Loja não encontrada</h1>
      <p className="max-w-md text-gray-600">
        A loja ou página que você procura não existe ou está fora do ar.
      </p>
    </main>
  )
}
