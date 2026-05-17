import posthog from 'posthog-js'

export function track(event: string, properties?: Record<string, unknown>) {
  if (import.meta.env.PROD) posthog.capture(event, properties)
}
