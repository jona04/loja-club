"use client"

import { useCallback, useEffect, useRef, useState } from "react"

import {
  type CustomizationSession,
  type CustomizationState,
  saveCustomizationState,
  startCustomization,
} from "@/lib/customization-actions"

/** Debounce before autosaving the editor state (doc 31 §4). */
export const AUTOSAVE_DEBOUNCE_MS = 1500

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
  // The session id for autosave, as a ref so the save effect doesn't depend on
  // (and re-fire on) the session object — that would loop forever.
  const sessionIdRef = useRef<string | null>(null)

  useEffect(() => {
    sessionIdRef.current = session?.id ?? null
  }, [session])

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

  // Debounced autosave. Depends only on `state` (the thing edits change); the
  // session id comes from a ref, and we never write the save response back to
  // state/session, so a save can't trigger another save.
  useEffect(() => {
    if (!state || !dirty.current) return
    const sessionId = sessionIdRef.current
    if (!sessionId) return
    if (timer.current) clearTimeout(timer.current)
    timer.current = setTimeout(() => {
      dirty.current = false
      setSaving(true)
      saveCustomizationState(sessionId, state)
        .catch((e: Error) => setError(e.message))
        .finally(() => setSaving(false))
    }, AUTOSAVE_DEBOUNCE_MS)
    return () => {
      if (timer.current) clearTimeout(timer.current)
    }
  }, [state])

  const setState = useCallback((next: CustomizationState) => {
    dirty.current = true
    setStateInternal(next)
  }, [])

  return { session, state, status, error, saving, setState }
}
