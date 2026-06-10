/** Aurora template (premium minimalista) — home curada com destaques. */
import type { Template } from "@/lib/template-types"

import { Category } from "./Category"
import { Home } from "./Home"
import { Product } from "./Product"
import { AuroraShell } from "./Shell"

export const template: Template = {
  Home,
  Category,
  Product,
  Shell: AuroraShell,
}
