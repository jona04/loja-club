"use client"

import { useRef, useState } from "react"

import { Panels } from "@/components/customizer/Panels"
import { ProgressBar } from "@/components/customizer/ProgressBar"
import { regionAspect } from "@/lib/customizer/aspect"
import { formatBytes } from "@/lib/customizer/format"
import type { CustomizationSession } from "@/lib/customizer/session-types"
import {
  APPROVE_PAYLOAD_LIMIT_BYTES,
  appendComposite,
  formDataBytes,
  snapshotFormData,
} from "@/lib/customizer/snapshot"
import { type UploadProgress, xhrUpload } from "@/lib/customizer/upload-xhr"
import { useSessionImages } from "@/lib/customizer/use-session-images"

/**
 * The read-only public view of a shared (assisted) customization session
 * (doc 30 §9): the same 3D preview, but not editable. Approval requires
 * confirming the pre-registered contact (no account); the backend matches it.
 * Approval also captures the snapshot + the production composite (same as the
 * customer editor).
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
  const [approveProgress, setApproveProgress] = useState<UploadProgress | null>(
    null,
  )
  const [error, setError] = useState<string | null>(null)
  const [approved, setApproved] = useState(session.status === "approved")
  const captureRef = useRef<(() => string) | null>(null)

  const images = useSessionImages(session.uploads)
  const layers = session.state_json.layers
  const maxFontSize = session.version.text_config.max_size ?? 96

  const onApprove = async () => {
    if (!captureRef.current) return
    setApproving(true)
    setError(null)
    setApproveProgress(null)
    try {
      const uv = session.version.printable_areas[0]?.uv_rect ?? {
        u0: 0,
        v0: 0,
        u1: 1,
        v1: 1,
      }
      const fd = await snapshotFormData(captureRef.current, { email, phone })
      await appendComposite(
        fd,
        { layers, images, maxFontSize },
        regionAspect(uv, aspect),
      )
      if (formDataBytes(fd) > APPROVE_PAYLOAD_LIMIT_BYTES) {
        setError(
          `A arte ficou grande demais (${formatBytes(formDataBytes(fd))}). Peça para reduzir as imagens.`,
        )
        return
      }
      await xhrUpload(
        `/api/customizer/p/${token}/approve`,
        fd,
        setApproveProgress,
      )
      setApproved(true)
    } catch (e) {
      console.error("[customizer] public approve failed:", e)
      setError((e as Error).message)
    } finally {
      setApproving(false)
      setApproveProgress(null)
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

      <Panels
        session={session}
        layers={layers}
        images={images}
        aspect={aspect}
        selectedId={null}
        readOnly
        onAspect={setAspect}
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
          <ProgressBar progress={approveProgress} label="Enviando sua arte…" />
          {error && <p className="text-sm text-red-600">{error}</p>}
        </div>
      )}
    </div>
  )
}
