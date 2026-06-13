/** Bazar template (vibrant marketplace) — home with category sections. */
import type { Template } from "@/lib/template-types"

import { Category } from "./Category"
import { CheckoutView } from "./CheckoutView"
import { Home } from "./Home"
import { Product } from "./Product"
import { BazarShell } from "./Shell"

export const template: Template = {
  Home,
  Category,
  Product,
  Shell: BazarShell,
  Checkout: CheckoutView,
}
