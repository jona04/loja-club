/** Whether the browser can create a WebGL context (the 3D editor needs it). */
export function hasWebGL(): boolean {
  if (typeof window === "undefined") return false
  try {
    const canvas = document.createElement("canvas")
    return Boolean(
      window.WebGLRenderingContext &&
        (canvas.getContext("webgl") || canvas.getContext("experimental-webgl")),
    )
  } catch {
    return false
  }
}
