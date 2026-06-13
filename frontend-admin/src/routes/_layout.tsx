import { useQuery } from "@tanstack/react-query"
import { createFileRoute, Link, Outlet, redirect } from "@tanstack/react-router"

import { PlatformAdminService } from "@/client"
import { Button } from "@/components/ui/button"
import useAuth, { isLoggedIn } from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout")({
  component: Layout,
  beforeLoad: async () => {
    if (!isLoggedIn()) {
      throw redirect({ to: "/login" })
    }
  },
})

function Layout() {
  const { user, logout } = useAuth()
  const { data: me, isLoading } = useQuery({
    queryKey: ["platformMe"],
    queryFn: () => PlatformAdminService.getPlatformMe(),
  })

  if (isLoading) {
    return (
      <div className="flex min-h-svh items-center justify-center text-muted-foreground">
        Carregando…
      </div>
    )
  }

  if (!me?.is_platform_admin) {
    return (
      <div className="flex min-h-svh flex-col items-center justify-center gap-4 p-6 text-center">
        <h1 className="text-2xl font-bold">Acesso negado</h1>
        <p className="text-muted-foreground">
          Sua conta não tem permissão de administrador da plataforma.
        </p>
        <Button variant="outline" onClick={logout}>
          Sair
        </Button>
      </div>
    )
  }

  const roles = me.platform_roles ?? []

  return (
    <div className="flex min-h-svh flex-col">
      <div className="bg-amber-500 px-4 py-1 text-center text-xs font-semibold uppercase tracking-widest text-amber-950">
        Ambiente interno · Admin da plataforma Kriar
      </div>
      <header className="sticky top-0 z-10 flex h-14 items-center gap-3 border-b bg-background px-4">
        <span className="font-bold">Kriar · Admin</span>
        <nav className="ml-4 hidden gap-4 text-sm sm:flex">
          <Link
            to="/stores"
            className="text-muted-foreground hover:text-foreground"
          >
            Lojas
          </Link>
          <Link
            to="/users"
            className="text-muted-foreground hover:text-foreground"
          >
            Usuários
          </Link>
          <Link
            to="/plans"
            className="text-muted-foreground hover:text-foreground"
          >
            Planos
          </Link>
          <Link
            to="/templates"
            className="text-muted-foreground hover:text-foreground"
          >
            Templates
          </Link>
        </nav>
        <div className="ml-auto flex items-center gap-3 text-sm">
          <span className="text-muted-foreground">{user?.email}</span>
          {roles.length > 0 && (
            <span className="rounded bg-muted px-2 py-0.5 text-xs">
              {roles.join(", ")}
            </span>
          )}
          <Button variant="outline" size="sm" onClick={logout}>
            Sair
          </Button>
        </div>
      </header>
      <main className="flex-1 p-6 md:p-8">
        <div className="mx-auto max-w-7xl">
          <Outlet />
        </div>
      </main>
    </div>
  )
}

export default Layout
