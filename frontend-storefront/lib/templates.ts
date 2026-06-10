/**
 * Template resolver (`P3-TPL-01`): maps a store's `active_template_id` to its
 * component tree. Unknown/missing ids fall back to the `base` template, so the
 * vitrine never breaks on a bad or not-yet-ported template.
 */
import type { Template } from "@/lib/template-types"
import { template as aurora } from "@/templates/aurora"

const TEMPLATES: Record<string, Template> = {
  aurora,
  // bazar / studio: P3-TPL-02 (fall back to Aurora until ported).
}

/**
 * Resolve the active template's component tree.
 *
 * @param id - The store's `active_template_id`.
 * @returns The matching template, or Aurora (the default) as a safe fallback.
 */
export function resolveTemplate(id: string): Template {
  return TEMPLATES[id] ?? aurora
}
