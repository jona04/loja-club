import { expect, test } from "@playwright/test"
import { firstSuperuser, firstSuperuserPassword } from "./config.ts"

test("unauthenticated visitors land on the login form", async ({ page }) => {
  await page.goto("/")
  await expect(page.getByTestId("email-input")).toBeVisible()
  await expect(page.getByTestId("password-input")).toBeVisible()
})

test("a platform admin logs in and reaches the admin shell", async ({
  page,
}) => {
  await page.goto("/login")
  await page.getByTestId("email-input").fill(firstSuperuser)
  await page.getByTestId("password-input").fill(firstSuperuserPassword)
  await page.getByRole("button", { name: "Entrar" }).click()

  await expect(
    page.getByRole("heading", { name: "Admin da plataforma" }),
  ).toBeVisible()
  await expect(page.getByRole("button", { name: "Sair" })).toBeVisible()
})
