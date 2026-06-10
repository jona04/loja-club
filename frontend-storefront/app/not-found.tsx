/**
 * Shown when the host resolves to no published store, or a resource is missing.
 *
 * @returns The friendly "loja não encontrada" page.
 */
export default function NotFound() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 px-6 text-center">
      <div className="grid h-16 w-16 place-items-center rounded-full bg-gray-100 text-gray-400">
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth={1.5}
          className="h-7 w-7"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M15.75 10.5V6a3.75 3.75 0 1 0-7.5 0v4.5m11.356-1.993 1.263 12c.07.665-.45 1.243-1.119 1.243H4.25a1.125 1.125 0 0 1-1.12-1.243l1.264-12A1.125 1.125 0 0 1 5.513 7.5h12.974c.576 0 1.059.435 1.119 1.007Z"
          />
        </svg>
      </div>
      <h1 className="text-2xl font-bold tracking-tight text-gray-900">
        Loja não encontrada
      </h1>
      <p className="max-w-md text-gray-500">
        A loja ou página que você procura não existe ou está fora do ar.
      </p>
    </main>
  )
}
