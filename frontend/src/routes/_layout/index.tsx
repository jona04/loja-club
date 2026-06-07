import { createFileRoute, Link } from "@tanstack/react-router"

import { Card, CardContent } from "@/components/ui/card"
import { useActiveStore } from "@/hooks/useActiveStore"
import useAuth from "@/hooks/useAuth"
import { buildMenu } from "@/lib/menu"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
  head: () => ({
    meta: [
      {
        title: "Dashboard - Loja Club",
      },
    ],
  }),
})

function Dashboard() {
  const { user: currentUser } = useAuth()
  const { activeStore, permissions } = useActiveStore()
  const shortcuts = buildMenu(permissions).filter(
    (module) => module.path !== "/",
  )

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h1 className="max-w-sm truncate text-2xl font-bold tracking-tight">
          Olá, {currentUser?.full_name || currentUser?.email} 👋
        </h1>
        {activeStore && (
          <p className="text-muted-foreground">
            Loja atual:{" "}
            <span className="font-medium text-foreground">
              {activeStore.name}
            </span>
          </p>
        )}
      </div>

      {shortcuts.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {shortcuts.map((module) => (
            <Link key={module.path} to={module.path}>
              <Card className="transition-colors hover:bg-accent">
                <CardContent className="flex items-center gap-3 p-6">
                  <module.icon className="size-5 text-muted-foreground" />
                  <span className="font-medium">{module.title}</span>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
