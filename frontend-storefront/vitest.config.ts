import path from "node:path"
import react from "@vitejs/plugin-react-swc"
import { defineConfig } from "vitest/config"

// Unit/component tests (vitest + Testing Library). Picks up co-located
// `*.test.{ts,tsx}` under app/components/lib; the 3D canvas is mocked (jsdom
// has no WebGL).
export default defineConfig({
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "."),
    },
  },
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./test/setup.ts"],
    include: ["{app,components,lib}/**/*.test.{ts,tsx}"],
  },
})
