"use client"

import {
  formatBytes,
  formatDuration,
  formatSpeed,
} from "@/lib/customizer/format"
import type { UploadProgress } from "@/lib/customizer/upload-xhr"

/**
 * An upload progress bar with percentage, transferred size, speed and ETA. While
 * the server processes the request (after bytes are sent) it shows an
 * indeterminate "processing" state.
 *
 * @param props.progress - The current progress snapshot, or null to hide.
 * @param props.label - A short label for what is being sent.
 * @returns The progress bar, or null.
 */
export function ProgressBar({
  progress,
  label,
}: {
  progress: UploadProgress | null
  label?: string
}) {
  if (!progress) return null

  const processing = progress.phase === "processing"
  const pct =
    progress.percent < 0 ? null : Math.min(100, Math.round(progress.percent))
  const width = processing || pct === null ? 100 : pct

  return (
    <div className="space-y-1" aria-live="polite">
      <div className="flex items-center justify-between text-xs text-gray-600">
        <span>
          {processing ? "Processando no servidor…" : (label ?? "Enviando…")}
        </span>
        {!processing && pct !== null && <span>{pct}%</span>}
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-gray-200">
        <div
          className={`h-full rounded-full bg-black transition-[width] duration-150 ${processing ? "animate-pulse" : ""}`}
          style={{ width: `${width}%` }}
        />
      </div>
      {!processing && progress.total > 0 && (
        <div className="flex items-center justify-between text-[11px] text-gray-400">
          <span>
            {formatBytes(progress.loaded)} / {formatBytes(progress.total)}
            {progress.bytesPerSecond > 0 &&
              ` · ${formatSpeed(progress.bytesPerSecond)}`}
          </span>
          {progress.etaSeconds >= 0 && (
            <span>~{formatDuration(progress.etaSeconds)} restantes</span>
          )}
        </div>
      )}
    </div>
  )
}
