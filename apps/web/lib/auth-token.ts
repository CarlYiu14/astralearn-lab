const ACCESS_KEY = "astr_access_token";
const REFRESH_KEY = "astr_refresh_token";

export function readAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return sessionStorage.getItem(ACCESS_KEY);
}

export function readRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return sessionStorage.getItem(REFRESH_KEY);
}

export function writeAccessToken(token: string): void {
  sessionStorage.setItem(ACCESS_KEY, token);
}

export function writeTokens(access: string, refresh: string): void {
  sessionStorage.setItem(ACCESS_KEY, access);
  sessionStorage.setItem(REFRESH_KEY, refresh);
}

export function clearAccessToken(): void {
  sessionStorage.removeItem(ACCESS_KEY);
}

export function clearAllTokens(): void {
  sessionStorage.removeItem(ACCESS_KEY);
  sessionStorage.removeItem(REFRESH_KEY);
}

/** Merge Authorization when an access token exists (client-side demos). */
export function withAuthHeaders(base: Record<string, string> = {}): Record<string, string> {
  const t = readAccessToken();
  if (!t) return base;
  return { ...base, Authorization: `Bearer ${t}` };
}
