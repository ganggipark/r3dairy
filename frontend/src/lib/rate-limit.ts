/**
 * Rate Limiter for Next.js API Routes
 * IP 기반 sliding window rate limiting
 */

interface RateLimitEntry {
  timestamps: number[]
}

const ipStore = new Map<string, RateLimitEntry>()

// Cleanup stale entries every 5 minutes
const CLEANUP_INTERVAL = 5 * 60 * 1000
let lastCleanup = Date.now()

function cleanup(windowMs: number) {
  const now = Date.now()
  if (now - lastCleanup < CLEANUP_INTERVAL) return
  lastCleanup = now
  const cutoff = now - windowMs
  for (const [ip, entry] of ipStore.entries()) {
    entry.timestamps = entry.timestamps.filter(t => t > cutoff)
    if (entry.timestamps.length === 0) ipStore.delete(ip)
  }
}

export interface RateLimitConfig {
  /** Time window in milliseconds (default: 60000 = 60s) */
  windowMs?: number
  /** Max requests per window (default: 10) */
  max?: number
}

export interface RateLimitResult {
  success: boolean
  remaining: number
  resetMs: number
}

/**
 * Check rate limit for a given IP address.
 * Returns { success: true } if under limit, { success: false } if exceeded.
 */
export function checkRateLimit(
  ip: string,
  config: RateLimitConfig = {}
): RateLimitResult {
  const windowMs = config.windowMs ?? 60_000
  const max = config.max ?? 10
  const now = Date.now()
  const cutoff = now - windowMs

  cleanup(windowMs)

  let entry = ipStore.get(ip)
  if (!entry) {
    entry = { timestamps: [] }
    ipStore.set(ip, entry)
  }

  // Remove timestamps outside the window
  entry.timestamps = entry.timestamps.filter(t => t > cutoff)

  if (entry.timestamps.length >= max) {
    const oldestInWindow = entry.timestamps[0]
    return {
      success: false,
      remaining: 0,
      resetMs: oldestInWindow + windowMs - now,
    }
  }

  entry.timestamps.push(now)
  return {
    success: true,
    remaining: max - entry.timestamps.length,
    resetMs: windowMs,
  }
}

/**
 * Get client IP from Next.js request headers.
 * Checks x-forwarded-for, x-real-ip, then falls back to '127.0.0.1'.
 */
export function getClientIp(headers: Headers): string {
  const forwarded = headers.get('x-forwarded-for')
  if (forwarded) return forwarded.split(',')[0].trim()
  const realIp = headers.get('x-real-ip')
  if (realIp) return realIp.trim()
  return '127.0.0.1'
}
