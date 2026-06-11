import { expect, type Page, test } from "@playwright/test"

const ANNOUNCEMENT_LABEL = "Texto da barra de anúncio"
const PERSONALIZATION_TITLE = "Personalização do template"

// Navigate to the layout screen, passing the store gate: create a first store
// (fresh db) or pick one in the selector (retry), then wait for the screen.
async function openStoreLayout(page: Page): Promise<void> {
  await page.goto("/store-layout")
  const createCta = page.getByRole("button", { name: "Criar loja" })
  const selector = page.getByRole("heading", { name: "Selecione uma loja" })
  const screen = page.getByText(PERSONALIZATION_TITLE)
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

test.describe("Store layout — schema-driven personalization", () => {
  test("edits a template setting, saves and persists it", async ({ page }) => {
    await openStoreLayout(page)

    // Each template links to its navigable preview (the demo store on the storefront).
    await expect(
      page.getByRole("link", { name: "Ver preview" }).first(),
    ).toHaveAttribute("href", /-demo\./)

    const field = page.getByLabel(ANNOUNCEMENT_LABEL)
    await field.fill("Frete grátis acima de R$99")
    await page.getByRole("button", { name: "Salvar personalização" }).click()
    await expect(page.getByText("Personalização salva")).toBeVisible()

    // The override survives a reload (persisted per store × template).
    await page.reload()
    await openStoreLayout(page)
    await expect(page.getByLabel(ANNOUNCEMENT_LABEL)).toHaveValue(
      "Frete grátis acima de R$99",
    )
  })
})
