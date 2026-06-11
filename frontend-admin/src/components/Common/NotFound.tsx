import { Link } from "@tanstack/react-router"
import { Button } from "@/components/ui/button"

/** Fallback shown for unmatched admin routes. */
const NotFound = () => (
  <div className="flex min-h-svh flex-col items-center justify-center gap-4 p-6 text-center">
    <h1 className="text-4xl font-bold">404</h1>
    <p className="text-muted-foreground">Página não encontrada.</p>
    <Button asChild>
      <Link to="/">Voltar ao início</Link>
    </Button>
  </div>
)

export default NotFound
