import {
  Contact,
  FileText,
  LayoutDashboard,
  type LucideIcon,
  Package,
  Palette,
  Settings,
  ShoppingCart,
  Sparkles,
  Truck,
  Users,
} from "lucide-react"

export interface MenuModule {
  title: string
  path: string
  icon: LucideIcon
  /** Base permission to see the module; null means always visible to members. */
  permission: string | null
}

/** The dashboard's modular menu. Add modules here as their screens land. */
export const MENU_MODULES: MenuModule[] = [
  { title: "Dashboard", path: "/", icon: LayoutDashboard, permission: null },
  {
    title: "Produtos",
    path: "/products",
    icon: Package,
    permission: "catalog.product.view",
  },
  {
    title: "Pedidos",
    path: "/orders",
    icon: ShoppingCart,
    permission: "orders.view",
  },
  {
    title: "Personalizações",
    path: "/customizations",
    icon: Sparkles,
    permission: "customization.sessions.view",
  },
  {
    title: "Clientes",
    path: "/customers",
    icon: Contact,
    permission: "customers.view",
  },
  {
    title: "Frete",
    path: "/shipping",
    icon: Truck,
    permission: "shipping.view",
  },
  {
    title: "Layout",
    path: "/store-layout",
    icon: Palette,
    permission: "layout.view",
  },
  {
    title: "Conteúdo",
    path: "/store-content",
    icon: FileText,
    permission: "layout.view",
  },
  {
    title: "Configurações",
    path: "/store-settings",
    icon: Settings,
    permission: "settings.view",
  },
  { title: "Equipe", path: "/team", icon: Users, permission: "team.view" },
]

/**
 * Plan-gating hook (Phase 5). MVP: every plan allows every module.
 *
 * @param _module - The module being checked (used by the Phase 5 gate).
 * @returns Always true in the MVP.
 */
function planAllowsModule(_module: MenuModule): boolean {
  return true
}

/**
 * Build the visible menu modules from the active member's permissions.
 *
 * A module shows when it requires no base permission (always) or the member
 * holds it, and the plan allows it (Phase 5 hook). Visibility is UX only — the
 * real authorization lives in the backend (`require_permission`).
 *
 * @param permissions - The member's permission keys in the active store.
 * @returns The modules to render in the sidebar, in declaration order.
 */
export function buildMenu(permissions: string[]): MenuModule[] {
  return MENU_MODULES.filter(
    (module) =>
      (module.permission === null || permissions.includes(module.permission)) &&
      planAllowsModule(module),
  )
}
