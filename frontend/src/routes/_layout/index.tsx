import { createFileRoute } from "@tanstack/react-router"

import { useActiveStore } from "@/hooks/useActiveStore"
import useAuth from "@/hooks/useAuth"

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
  const { activeStore } = useActiveStore()

  return (
    <div className="space-y-2">
      <h1 className="text-2xl truncate max-w-sm">
        Hi, {currentUser?.full_name || currentUser?.email} 👋
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
  )
}
