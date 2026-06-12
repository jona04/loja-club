import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

/**
 * Add two numbers.
 *
 * Placeholder pure unit until real utilities exist; only proves the unit layer
 * runs.
 *
 * @param a - First addend.
 * @param b - Second addend.
 * @returns The sum of `a` and `b`.
 */
function add(a: number, b: number): number {
  return a + b
}

/**
 * Minimal component used to prove React Testing Library renders and queries.
 *
 * @param props - Component props.
 * @param props.name - Name shown in the greeting.
 * @returns A paragraph greeting `name`.
 */
function Hello({ name }: { name: string }) {
  return <p>Olá, {name}</p>
}

describe("unit sample", () => {
  it("runs a pure unit assertion", () => {
    expect(add(2, 3)).toBe(5)
  })

  it("renders a component with Testing Library", () => {
    render(<Hello name="Kriar" />)
    expect(screen.getByText("Olá, Kriar")).toBeInTheDocument()
  })
})
