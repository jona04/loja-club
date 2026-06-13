"use client"

import { useCallback, useEffect, useRef, useState } from "react"

import {
  type CustomizationSession,
  type CustomizationState,
  saveCustomizationState,
  startCustomization,
} from "@/lib/customization-actions"

/** Debounce before autosaving the editor state (doc 31 §4). */
export const AUTOSAVE_DEBOUNCE_MS = 800

export type CustomizerStatus = "loading" | "ready" | "error"

export interface CustomizerController {
  session: CustomizationSession | null
  state: CustomizationState | null
  status: CustomizerStatus
  error: string | null
  saving: boolean
  /** Update the editor state; schedules a debounced autosave. */
  setState: (next: CustomizationState) => void
}

/**
 * Drives a customization session: starts (or resumes) it on mount and autosaves
 * the `state_json` (debounced) on every change. Restore is implicit — the
 * backend returns the guest's existing draft for the product.
 *
 * @param productId - The product being customized.
 * @returns The session controller (session, state, status, autosave setter).
 */
export function useCustomizer(productId: string): CustomizerController {
  const [session, setSession] = useState<CustomizationSession | null>(null)
  const [state, setStateInternal] = useState<CustomizationState | null>(null)
  const [status, setStatus] = useState<CustomizerStatus>("loading")
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null)
  // Only autosave after a user edit, never on the initial load.
  const dirty = useRef(false)

  useEffect(() => {
    let active = true
    setStatus("loading")
    startCustomization(productId)
      .then((s) => {
        if (!active) return
        setSession(s)
        setStateInternal(s.state_json)
        setStatus("ready")
      })
      .catch((e: Error) => {
        if (active) {
          setError(e.message)
          setStatus("error")
        }
      })
    return () => {
      active = false
    }
  }, [productId])

  useEffect(() => {
    if (!session || !state || !dirty.current) return
    if (timer.current) clearTimeout(timer.current)
    timer.current = setTimeout(() => {
      setSaving(true)
      saveCustomizationState(session.id, state)
        .then((s) => setSession(s))
        .catch((e: Error) => setError(e.message))
        .finally(() => setSaving(false))
    }, AUTOSAVE_DEBOUNCE_MS)
    return () => {
      if (timer.current) clearTimeout(timer.current)
    }
  }, [state, session])

  const setState = useCallback((next: CustomizationState) => {
    dirty.current = true
    setStateInternal(next)
  }, [])

  return { session, state, status, error, saving, setState }
}
