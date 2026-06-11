import type { ReactNode } from "react"

/** Centered wrapper for the admin login, flagging the internal environment. */
export function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-svh flex-col items-center justify-center gap-6 bg-muted p-6">
      <div className="flex flex-col items-center gap-1 text-center">
        <span className="text-xs font-semibold uppercase tracking-widest text-amber-600">
          Ambiente interno
        </span>
        <span className="text-lg font-bold">Loja Club · Admin</span>
      </div>
      <div className="w-full max-w-sm rounded-xl border bg-background p-6 shadow-sm">
        {children}
      </div>
    </div>
  )
}
