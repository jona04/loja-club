/** Human-readable size/speed/duration formatting for the upload progress UI. */

/**
 * Format a byte count as a human-readable size (e.g. `1.4 MB`).
 *
 * @param bytes - The byte count.
 * @returns The formatted size string.
 */
export function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  const kb = bytes / 1024
  if (kb < 1024) return `${kb.toFixed(0)} KB`
  return `${(kb / 1024).toFixed(1)} MB`
}

/**
 * Format an upload speed (bytes/second) as `X MB/s`.
 *
 * @param bytesPerSecond - The speed in bytes per second.
 * @returns The formatted speed string.
 */
export function formatSpeed(bytesPerSecond: number): string {
  return `${formatBytes(bytesPerSecond)}/s`
}

/**
 * Format a duration in seconds as a short human string (e.g. `12s`, `1m05s`).
 *
 * @param seconds - The duration in seconds.
 * @returns The formatted duration string.
 */
export function formatDuration(seconds: number): string {
  const s = Math.max(0, Math.round(seconds))
  if (s < 60) return `${s}s`
  const m = Math.floor(s / 60)
  return `${m}m${String(s % 60).padStart(2, "0")}s`
}
