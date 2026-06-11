import { defineConfig, devices } from "@playwright/test"
import "dotenv/config"

// https://playwright.dev/docs/test-configuration
export default defineConfig({
  testDir: "./tests",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI ? "blob" : "html",
  use: {
    baseURL: "http://localhost:5181",
    trace: "on-first-retry",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
  ],
  // Admin dev server (distinct from the dashboard on 5180).
  webServer: {
    command: "bun run dev",
    url: "http://localhost:5181",
    reuseExistingServer: !process.env.CI,
  },
})
