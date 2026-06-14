"use client"

import { useRef, useState } from "react"

import { Panels } from "@/components/customizer/Panels"
import { approveCustomizationViaToken } from "@/lib/customization-actions"
import type { CustomizationSession } from "@/lib/customizer/session-types"
import { snapshotFormData } from "@/lib/customizer/snapshot"
import { useSessionImages } from "@/lib/customizer/use-session-images"

/**
 * The read-only public view of a shared (assisted) customization session
 * (doc 30 §9): the same 3D preview, but not editable. Approval requires
 * confirming the pre-registered contact (no account); the backend matches it.
 *
 * @param props.token - The session's public token (from the link).
 * @param props.session - The server-fetched session.
 * @returns The public viewer + approval form.
 */
export function PublicCustomizer({
  token,
  session,
}: {
  token: string
  session: CustomizationSession
}) {
  const [aspect, setAspect] = useState(2.5)
  const [email, setEmail] = useState("")
  const [phone, setPhone] = useState("")
  const [approving, setApproving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [approved, setApproved] = useState(session.status === "approved")
  const captureRef = useRef<(() => string) | null>(null)

  // Newly loaded by useSessionImages inside Panels via the session uploads —
  // here we keep a stable images map by reusing Panels' own loader.
  const onApprove = async () => {
    if (!captureRef.current) return
    setApproving(true)
    setError(null)
    try {
      const fd = await snapshotFormData(captureRef.current, { email, phone })
      await approveCustomizationViaToken(token, fd)
      setApproved(true)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setApproving(false)
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="mb-1 text-2xl font-bold tracking-tight">
        Sua personalização
      </h1>
      <p className="mb-6 text-sm text-gray-500">
        Confira a prévia. Para aprovar, confirme seu contato.
      </p>

      <PublicPanels
        session={session}
        aspect={aspect}
        setAspect={setAspect}
        captureRef={captureRef}
      />

      {approved ? (
        <div className="mt-6 rounded-md border border-green-200 bg-green-50 p-4 text-sm text-green-800">
          Personalização aprovada! Entraremos em contato para concluir o pedido.
        </div>
      ) : (
        <div className="mt-6 space-y-3 rounded-md border p-4">
          <p className="text-sm font-medium">Aprovar (confirme seu contato)</p>
          <div className="grid gap-3 sm:grid-cols-2">
            <input
              type="email"
              placeholder="E-mail cadastrado"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="rounded-md border px-3 py-2 text-sm"
            />
            <input
              type="tel"
              placeholder="Telefone (opcional)"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="rounded-md border px-3 py-2 text-sm"
            />
          </div>
          <button
            type="button"
            disabled={approving || (!email && !phone)}
            onClick={onApprove}
            className="rounded-md bg-black px-5 py-3 text-sm font-medium text-white disabled:opacity-50"
          >
            {approving ? "Aprovando…" : "Aprovar"}
          </button>
          {error && <p className="text-sm text-red-600">{error}</p>}
        </div>
      )}
    </div>
  )
}

/** Wraps `Panels` in read-only mode with the session's uploaded images. */
function PublicPanels({
  session,
  aspect,
  setAspect,
  captureRef,
}: {
  session: CustomizationSession
  aspect: number
  setAspect: (a: number) => void
  captureRef: React.RefObject<(() => string) | null>
}) {
  const images = useSessionImages(session.uploads)
  return (
    <Panels
      session={session}
      layers={session.state_json.layers}
      images={images}
      aspect={aspect}
      selectedId={null}
      readOnly
      onAspect={setAspect}
      captureRef={captureRef}
    />
  )
}
