import type { Metadata } from "next"
import { Inter } from "next/font/google"
import type { ReactNode } from "react"

import "./globals.css"

const inter = Inter({ subsets: ["latin"], display: "swap" })

export const metadata: Metadata = {
  title: "Loja Club",
  description: "Storefront público das lojas Loja Club.",
}

/**
 * Root layout wrapping every storefront page.
 *
 * @param children - The page content to render inside the HTML shell.
 * @returns The HTML document shell for the storefront.
 */
export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="pt-BR" className={inter.className}>
      <body className="bg-white text-gray-900">{children}</body>
    </html>
  )
}
