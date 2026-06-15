import type { NextConfig } from "next"

const nextConfig: NextConfig = {
  experimental: {
    serverActions: {
      // Customization uploads + the approval snapshot/composite are proxied to
      // the backend through Route Handlers (XHR, for progress), not Server
      // Actions — but keep a generous limit so any action covers the largest
      // art upload (`art_limits` ~30 MB) plus headroom (doc 31 §4). Default 1 MB.
      bodySizeLimit: "50mb",
    },
  },
}

export default nextConfig
