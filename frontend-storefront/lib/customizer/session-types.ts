/**
 * Shared DTO types for the customization editor (mirror the backend
 * `SessionPublic` / `UploadPublic`). Kept out of the `"use server"` actions file
 * so both server reads and client components can import them.
 */

import type { EditorLayer } from "@/lib/customizer/types"

/** A printable region in the model's UV space (normalized 0..1). */
export interface UvRect {
  u0: number
  v0: number
  u1: number
  v1: number
}

/** A printable area of the model version (UV region + limits). */
export interface PrintableArea {
  id?: string
  label?: string
  uv_rect: UvRect
  max_layers?: number
  [key: string]: unknown
}

/** The pinned catalog version the editor renders against. */
export interface SessionVersion {
  id: string
  version: number
  glb_url: string
  printable_areas: PrintableArea[]
  text_config: { fonts?: string[]; min_size?: number; max_size?: number }
  art_limits: { mimes?: string[]; max_bytes?: number; min_dimension?: number }
}

/** The editor state contract (doc 30 §4). */
export interface CustomizationState {
  schema_version: number
  model: { model_id: string; version_id: string }
  layers: EditorLayer[]
}

/** A customization session as the editor sees it (mirrors `SessionPublic`). */
export interface CustomizationSession {
  id: string
  product_id: string
  status: string
  state_json: CustomizationState
  version: SessionVersion
  uploads: UploadPublic[]
  snapshot_url: string | null
  expires_at: string
  approved_at: string | null
}

/** A customer upload, with a short-lived presigned read URL. */
export interface UploadPublic {
  id: string
  mime: string
  size_bytes: number
  width: number | null
  height: number | null
  url: string
  low_resolution: boolean
}
