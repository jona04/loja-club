import { expect, test } from "@playwright/test"
import { apiUrl } from "./config.ts"

test("a user without a platform role is denied access", async ({
  page,
  request,
}) => {
  const email = `no-admin-${Date.now()}@example.com`
  const password = "changethis123"
  const res = await request.post(`${apiUrl}/api/v1/users/signup`, {
    data: { email, password, full_name: "No Admin" },
  })
  expect(res.ok()).toBeTruthy()

  await page.goto("/login")
  await page.getByTestId("email-input").fill(email)
  await page.getByTestId("password-input").fill(password)
  await page.getByRole("button", { name: "Entrar" }).click()

  await expect(
    page.getByRole("heading", { name: "Acesso negado" }),
  ).toBeVisible()
})
