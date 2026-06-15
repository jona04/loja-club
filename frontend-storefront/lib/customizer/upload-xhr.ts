"use client"

/** A snapshot of an in-flight upload, for the progress bar. */
export interface UploadProgress {
  /** Bytes sent so far. */
  loaded: number
  /** Total bytes to send (0 if not computable). */
  total: number
  /** 0..100, or -1 when not computable / indeterminate. */
  percent: number
  /** Average upload speed in bytes/second. */
  bytesPerSecond: number
  /** Estimated seconds remaining, or -1 when unknown. */
  etaSeconds: number
  /** `uploading` = bytes in flight; `processing` = server is responding. */
  phase: "uploading" | "processing"
}

/**
 * POST multipart form data via XMLHttpRequest, reporting upload progress.
 *
 * Server Actions cannot report progress, so heavy customization operations POST
 * to same-origin Route Handlers through this helper. Progress covers the
 * browser → Next leg (the slow part for big files); after 100% the request is in
 * the `processing` phase (Next → backend → S3, not visible to the client).
 *
 * @param url - Same-origin Route Handler URL.
 * @param formData - The multipart body.
 * @param onProgress - Called with each progress snapshot.
 * @returns The parsed JSON response.
 * @throws Error (with `status`) carrying the backend's message on a non-2xx.
 */
export function xhrUpload<T>(
  url: string,
  formData: FormData,
  onProgress?: (p: UploadProgress) => void,
): Promise<T> {
  return new Promise<T>((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open("POST", url)
    const startedAt = performance.now()

    xhr.upload.onprogress = (e: ProgressEvent) => {
      if (!onProgress) return
      const elapsed = (performance.now() - startedAt) / 1000
      const bps = elapsed > 0 ? e.loaded / elapsed : 0
      const computable = e.lengthComputable && e.total > 0
      const percent = computable ? (e.loaded / e.total) * 100 : -1
      const etaSeconds = computable && bps > 0 ? (e.total - e.loaded) / bps : -1
      onProgress({
        loaded: e.loaded,
        total: computable ? e.total : 0,
        percent,
        bytesPerSecond: bps,
        etaSeconds,
        phase: percent >= 100 ? "processing" : "uploading",
      })
    }

    // Bytes are out; now we wait on the server (Next → backend → S3).
    xhr.upload.onload = () => {
      onProgress?.({
        loaded: 0,
        total: 0,
        percent: 100,
        bytesPerSecond: 0,
        etaSeconds: -1,
        phase: "processing",
      })
    }

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          resolve(JSON.parse(xhr.responseText) as T)
        } catch {
          reject(new Error("Resposta inválida do servidor."))
        }
        return
      }
      let message = `Falha no envio (${xhr.status}).`
      try {
        const body = JSON.parse(xhr.responseText) as {
          error?: { message?: string }
        }
        if (body?.error?.message) message = body.error.message
      } catch {
        /* keep the generic message */
      }
      const err = new Error(message) as Error & { status?: number }
      err.status = xhr.status
      reject(err)
    }

    xhr.onerror = () => reject(new Error("Erro de rede ao enviar."))
    xhr.ontimeout = () => reject(new Error("Tempo de envio esgotado."))
    xhr.send(formData)
  })
}
