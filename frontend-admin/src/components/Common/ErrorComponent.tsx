import { Link } from "@tanstack/react-router"
import { Button } from "@/components/ui/button"

/** Fallback shown when an admin route throws. */
const ErrorComponent = () => (
  <div className="flex min-h-svh flex-col items-center justify-center gap-4 p-6 text-center">
    <h1 className="text-2xl font-bold">Algo deu errado</h1>
    <p className="text-muted-foreground">Tente novamente em instantes.</p>
    <Button asChild>
      <Link to="/">Voltar ao início</Link>
    </Button>
  </div>
)

export default ErrorComponent
