/**
 * Caching utilities for Saju calculations
 * @version 1.0.0 (v1.2.13)
 */

// ============================================================
// Solar Terms Cache
// ============================================================

interface SolarTermCacheEntry {
  value: number;
  timestamp: number;
}

const solarTermCache = new Map<string, SolarTermCacheEntry>();
const CACHE_TTL = 24 * 60 * 60 * 1000; // 24 hours

export function getCachedAstrologicalMonth(
  year: number,
  month: number,
  day: number,
  hour: number,
  minute: number,
  computeFn: () => number
): number {
  const key = `${year}-${month}-${day}-${hour}-${minute}`;
  const cached = solarTermCache.get(key);

  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.value;
  }

  const value = computeFn();
  solarTermCache.set(key, { value, timestamp: Date.now() });
  return value;
}

export function clearSolarTermCache(): void {
  solarTermCache.clear();
}

export function getSolarTermCacheSize(): number {
  return solarTermCache.size;
}

// ============================================================
// Ten Gods Calculation Cache
// ============================================================

const tenGodsCache = new Map<string, string>();

export function getCachedSipSin(
  dayGan: string,
  targetGan: string,
  computeFn: () => string
): string {
  const key = `${dayGan}-${targetGan}`;
  const cached = tenGodsCache.get(key);

  if (cached !== undefined) {
    return cached;
  }

  const value = computeFn();
  tenGodsCache.set(key, value);
  return value;
}

export function preWarmTenGodsCache(
  computeFn: (dayGan: string, targetGan: string) => string
): void {
  const gans = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계'];
  for (const day of gans) {
    for (const target of gans) {
      const key = `${day}-${target}`;
      if (!tenGodsCache.has(key)) {
        tenGodsCache.set(key, computeFn(day, target));
      }
    }
  }
}

export function clearTenGodsCache(): void {
  tenGodsCache.clear();
}

export function getTenGodsCacheSize(): number {
  return tenGodsCache.size;
}

// ============================================================
// Generic Memoization Helper
// ============================================================

export function memoize<T extends (...args: any[]) => any>(
  fn: T,
  keyFn?: (...args: Parameters<T>) => string
): T {
  const cache = new Map<string, ReturnType<T>>();

  return ((...args: Parameters<T>): ReturnType<T> => {
    const key = keyFn ? keyFn(...args) : JSON.stringify(args);

    if (cache.has(key)) {
      return cache.get(key)!;
    }

    const result = fn(...args);
    cache.set(key, result);
    return result;
  }) as T;
}
