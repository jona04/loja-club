/** Studio template (clean catalog with a sidebar). */
import type { Template } from "@/lib/template-types"

import { Category } from "./Category"
import { Home } from "./Home"
import { Product } from "./Product"
import { StudioShell } from "./Shell"

export const template: Template = {
  Home,
  Category,
  Product,
  Shell: StudioShell,
}
