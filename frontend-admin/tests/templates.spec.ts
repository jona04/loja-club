import { expect, test } from "@playwright/test"
import { firstSuperuser, firstSuperuserPassword } from "./config.ts"

test.beforeEach(async ({ page }) => {
  await page.goto("/login")
  await page.getByTestId("email-input").fill(firstSuperuser)
  await page.getByTestId("password-input").fill(firstSuperuserPassword)
  await page.getByRole("button", { name: "Entrar" }).click()
  await expect(
    page.getByRole("heading", { name: "Admin da plataforma" }),
  ).toBeVisible()
  await page.getByRole("link", { name: "Templates" }).click()
  await expect(page.getByRole("heading", { name: "Templates" })).toBeVisible()
})

test("lists the seeded templates and opens the read-only schema detail", async ({
  page,
}) => {
  await expect(page.getByRole("row", { name: /Aurora/ })).toBeVisible()

  await page
    .getByRole("row", { name: /Aurora/ })
    .getByRole("button", { name: "Detalhes" })
    .click()
  await expect(page.getByText("settings_schema")).toBeVisible()
})

test("opens the create-template dialog", async ({ page }) => {
  await page.getByRole("button", { name: "Novo template" }).click()
  await expect(
    page.getByRole("heading", { name: "Novo template" }),
  ).toBeVisible()
})
