import { AxiosError } from "axios"
import type { ApiError } from "./client"

function extractErrorMessage(err: ApiError): string {
  if (err instanceof AxiosError) {
    return err.message
  }

  const body = err.body as any

  // Structured envelope: { error: { code, message, details? } } (P1-API-01).
  const apiError = body?.error
  if (apiError?.message) {
    const details = apiError.details
    if (Array.isArray(details) && details.length > 0) {
      return details[0].msg ?? apiError.message
    }
    return apiError.message
  }

  // Fallback for the raw FastAPI shape.
  const errDetail = body?.detail
  if (Array.isArray(errDetail) && errDetail.length > 0) {
    return errDetail[0].msg
  }
  return errDetail || "Something went wrong."
}

export const handleError = function (
  this: (msg: string) => void,
  err: ApiError,
) {
  const errorMessage = extractErrorMessage(err)
  this(errorMessage)
}

export const getInitials = (name: string): string => {
  return name
    .split(" ")
    .slice(0, 2)
    .map((word) => word[0])
    .join("")
    .toUpperCase()
}
