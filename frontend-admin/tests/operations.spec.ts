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
})

test("plans screen lists the seeded plans", async ({ page }) => {
  await page.getByRole("link", { name: "Planos" }).click()
  await expect(page.getByRole("heading", { name: "Planos" })).toBeVisible()
  await expect(
    page.getByRole("cell", { name: "Free", exact: true }),
  ).toBeVisible()
})

test("users screen asks confirmation before impersonating", async ({
  page,
}) => {
  await page.getByRole("link", { name: "Usuários" }).click()
  await expect(page.getByRole("heading", { name: "Usuários" })).toBeVisible()
  await expect(
    page.getByRole("cell", { name: firstSuperuser, exact: true }),
  ).toBeVisible()
  await page.getByRole("button", { name: "Impersonar" }).first().click()
  await expect(page.getByText("Esta ação é auditada.")).toBeVisible()
})

test("stores screen loads", async ({ page }) => {
  await page.getByRole("link", { name: "Lojas" }).click()
  await expect(page.getByRole("heading", { name: "Lojas" })).toBeVisible()
})
