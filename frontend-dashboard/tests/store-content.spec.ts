import { expect, type Page, test } from "@playwright/test"

// Navigate to the content screen, passing the store gate: create a first store
// (fresh db) or pick one in the selector, then wait for the Pages tab.
async function openStoreContent(page: Page): Promise<void> {
  await page.goto("/store-content")
  const createCta = page.getByRole("button", { name: "Criar loja" })
  const selector = page.getByRole("heading", { name: "Selecione uma loja" })
  const screen = page.getByRole("tab", { name: "Páginas" })
  await expect(createCta.or(selector).or(screen).first()).toBeVisible()

  if (await createCta.isVisible()) {
    await createCta.click()
    await page.getByLabel("Nome da loja").fill(`Loja E2E ${Date.now()}`)
    await page.getByRole("button", { name: "Criar", exact: true }).click()
  } else if (await selector.isVisible()) {
    await page.getByRole("button").filter({ hasText: /-/ }).first().click()
  }
  await expect(screen).toBeVisible()
}

test.describe("Store content — pages CRUD", () => {
  test("creates a page, sees it listed, then deletes it", async ({ page }) => {
    await openStoreContent(page)
    const slug = `sobre-${Date.now()}`

    await page.getByRole("button", { name: "Nova página" }).click()
    await page.getByLabel("Slug").fill(slug)
    await page.getByLabel("Título").fill("Sobre a loja")
    await page.getByRole("button", { name: "Salvar" }).click()
    await expect(page.getByText("Página salva")).toBeVisible()

    // The new page appears in the list.
    await expect(page.getByRole("cell", { name: slug })).toBeVisible()

    // Deleting it removes the row.
    await page
      .getByRole("row")
      .filter({ hasText: slug })
      .getByRole("button", { name: "Excluir" })
      .click()
    await expect(page.getByText("Página excluída")).toBeVisible()
    await expect(page.getByRole("cell", { name: slug })).toHaveCount(0)
  })
})
