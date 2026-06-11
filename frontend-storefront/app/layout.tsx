import type { Metadata } from "next"
import { Inter, Plus_Jakarta_Sans } from "next/font/google"
import type { ReactNode } from "react"

import "./globals.css"

const inter = Inter({ subsets: ["latin"], display: "swap" })
const jakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-jakarta",
})

export const metadata: Metadata = {
  title: "Loja Club",
  description: "Storefront público das lojas Loja Club.",
}

/**
 * Root layout wrapping every storefront page. Loads Font Awesome (used by the
 * templates' icons) and the Inter font.
 *
 * @param children - The page content to render inside the HTML shell.
 * @returns The HTML document shell for the storefront.
 */
export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="pt-BR" className={`${inter.className} ${jakarta.variable}`}>
      <body className="bg-white text-gray-900">
        <link
          rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css"
          crossOrigin="anonymous"
          referrerPolicy="no-referrer"
        />
        {children}
      </body>
    </html>
  )
}
