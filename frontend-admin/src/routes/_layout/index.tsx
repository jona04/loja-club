import { createFileRoute } from "@tanstack/react-router"

export const Route = createFileRoute("/_layout/")({
  component: Home,
})

function Home() {
  return (
    <div className="flex flex-col gap-2">
      <h1 className="text-2xl font-bold">Admin da plataforma</h1>
      <p className="text-muted-foreground">
        Operação de lojas, usuários, planos e templates. As telas entram nas
        próximas tasks (P4-ADMIN-02/03).
      </p>
    </div>
  )
}
