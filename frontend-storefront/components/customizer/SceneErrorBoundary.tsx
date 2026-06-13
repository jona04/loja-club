"use client"

import { Component, type ReactNode } from "react"

/**
 * Catches render/load failures from the 3D scene (e.g. the GLB fails to fetch
 * or decode) and shows a fallback instead of crashing the page.
 */
export class SceneErrorBoundary extends Component<
  { fallback: ReactNode; children: ReactNode },
  { failed: boolean }
> {
  state = { failed: false }

  static getDerivedStateFromError(): { failed: boolean } {
    return { failed: true }
  }

  render(): ReactNode {
    return this.state.failed ? this.props.fallback : this.props.children
  }
}
