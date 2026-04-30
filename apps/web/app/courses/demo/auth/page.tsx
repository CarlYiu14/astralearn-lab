"use client";

import Link from "next/link";
import type { CSSProperties } from "react";
import { useMemo, useState } from "react";

import {
  clearAllTokens,
  readAccessToken,
  readRefreshToken,
  writeTokens
} from "@/lib/auth-token";

type MeResponse = { id: string; email: string; name: string | null; role: string };

type TokenBundle = {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  refresh_expires_in: number;
};

type AuditRow = {
  id: string;
  created_at: string;
  actor_user_id: string | null;
  action: string;
  course_id: string | null;
  resource_type: string | null;
  resource_id: string | null;
  detail: Record<string, unknown> | null;
  ip_address: string | null;
  user_agent: string | null;
};

export default function AuthDemoPage() {
  const apiBase = useMemo(
    () => process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000",
    []
  );

  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("dev@local.test");
  const [password, setPassword] = useState("devpassword123");
  const [name, setName] = useState("");
  const [me, setMe] = useState<MeResponse | null>(null);
  const [audit, setAudit] = useState<AuditRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function submitAuth() {
    setError(null);
    setMe(null);
    setAudit(null);
    const path = mode === "login" ? "/auth/login" : "/auth/register";
    const body =
      mode === "login"
        ? { email, password }
        : { email, password, name: name.trim() || null };
    const res = await fetch(`${apiBase}${path}`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body)
    });
    if (!res.ok) {
      setError(await res.text());
      return;
    }
    const data = (await res.json()) as TokenBundle;
    writeTokens(data.access_token, data.refresh_token);
    await loadMe(data.access_token);
  }

  async function rotateAccess() {
    setError(null);
    const rt = readRefreshToken();
    if (!rt) {
      setError("No refresh token in sessionStorage.");
      return;
    }
    const res = await fetch(`${apiBase}/auth/refresh`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ refresh_token: rt })
    });
    if (!res.ok) {
      setError(await res.text());
      return;
    }
    const data = (await res.json()) as TokenBundle;
    writeTokens(data.access_token, data.refresh_token);
    await loadMe(data.access_token);
  }

  async function loadMe(token?: string) {
    setError(null);
    const t = token ?? readAccessToken();
    if (!t) {
      setMe(null);
      return;
    }
    const res = await fetch(`${apiBase}/auth/me`, { headers: { Authorization: `Bearer ${t}` } });
    if (!res.ok) {
      setError(await res.text());
      setMe(null);
      return;
    }
    setMe((await res.json()) as MeResponse);
  }

  async function loadAudit() {
    setError(null);
    const t = readAccessToken();
    if (!t) {
      setError("Sign in first.");
      return;
    }
    const res = await fetch(`${apiBase}/auth/audit/me?limit=30`, {
      headers: { Authorization: `Bearer ${t}` }
    });
    if (!res.ok) {
      setError(await res.text());
      return;
    }
    setAudit((await res.json()) as AuditRow[]);
  }

  async function logout() {
    setError(null);
    const rt = readRefreshToken();
    const at = readAccessToken();
    if (rt) {
      await fetch(`${apiBase}/auth/logout`, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          ...(at ? { Authorization: `Bearer ${at}` } : {})
        },
        body: JSON.stringify({ refresh_token: rt })
      });
    }
    clearAllTokens();
    setMe(null);
    setAudit(null);
  }

  async function logoutEverywhere() {
    setError(null);
    const at = readAccessToken();
    if (!at) {
      setError("Need access token to revoke all sessions.");
      return;
    }
    const res = await fetch(`${apiBase}/auth/logout`, {
      method: "POST",
      headers: { "content-type": "application/json", Authorization: `Bearer ${at}` },
      body: JSON.stringify({ revoke_all_sessions: true })
    });
    if (!res.ok) {
      setError(await res.text());
      return;
    }
    clearAllTokens();
    setMe(null);
    setAudit(null);
  }

  return (
    <main style={{ fontFamily: "Inter, sans-serif", padding: "2rem", maxWidth: 720 }}>
      <h1>Auth (Day 8–9)</h1>
      <p style={{ color: "#444" }}>
        Day 9 adds opaque <strong>refresh tokens</strong> (stored hashed, rotated on use) and an <strong>audit log</strong>.
        Tokens live in <code>sessionStorage</code> (<code>astr_access_token</code>, <code>astr_refresh_token</code>).
        Production apps should prefer httpOnly cookies for refresh. Seed: <code>python scripts/seed_dev_course.py</code>.
      </p>

      <div style={{ display: "flex", gap: 10, marginBottom: 16, flexWrap: "wrap" }}>
        <button type="button" style={tabBtn(mode === "login")} onClick={() => setMode("login")}>
          Login
        </button>
        <button type="button" style={tabBtn(mode === "register")} onClick={() => setMode("register")}>
          Register
        </button>
        <button type="button" style={btn} onClick={() => loadMe()}>
          Refresh /me
        </button>
        <button type="button" style={btn} onClick={rotateAccess}>
          Rotate (POST /auth/refresh)
        </button>
        <button type="button" style={btn} onClick={loadAudit}>
          Load my audit
        </button>
        <button type="button" style={btn} onClick={logout}>
          Log out (revoke refresh)
        </button>
        <button type="button" style={btn} onClick={logoutEverywhere}>
          Revoke all sessions
        </button>
      </div>

      <section style={{ display: "grid", gap: 12 }}>
        <label style={label}>
          <span>Email</span>
          <input value={email} onChange={(e) => setEmail(e.target.value)} style={input} autoComplete="email" />
        </label>
        <label style={label}>
          <span>Password</span>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={input}
            autoComplete={mode === "login" ? "current-password" : "new-password"}
          />
        </label>
        {mode === "register" ? (
          <label style={label}>
            <span>Name (optional)</span>
            <input value={name} onChange={(e) => setName(e.target.value)} style={input} />
          </label>
        ) : null}
        <button type="button" onClick={submitAuth} style={btn}>
          {mode === "login" ? "Sign in" : "Create account"}
        </button>
      </section>

      {error ? <pre style={{ marginTop: 16, color: "#b00020", whiteSpace: "pre-wrap" }}>{error}</pre> : null}

      {me ? (
        <section style={{ marginTop: 20 }}>
          <h2>Current user</h2>
          <pre style={pre}>{JSON.stringify(me, null, 2)}</pre>
        </section>
      ) : (
        <p style={{ marginTop: 16, color: "#64748b" }}>Sign in to load profile, or use Refresh /me.</p>
      )}

      {audit ? (
        <section style={{ marginTop: 20 }}>
          <h2>Recent audit (you as actor)</h2>
          <pre style={pre}>{JSON.stringify(audit, null, 2)}</pre>
        </section>
      ) : null}

      <nav style={{ marginTop: 28, display: "flex", flexDirection: "column", gap: 8 }}>
        <Link href="/courses/demo/documents">Documents demo</Link>
        <Link href="/courses/demo/qa">QA demo</Link>
        <Link href="/courses/demo/graph">Graph demo</Link>
        <Link href="/courses/demo/lessons">Lessons demo</Link>
        <Link href="/courses/demo/assessment">Assessment demo</Link>
      </nav>
    </main>
  );
}

const label: CSSProperties = { display: "grid", gap: 6 };
const input: CSSProperties = { padding: 10, borderRadius: 8, border: "1px solid #ccc" };
const btn: CSSProperties = { padding: "10px 14px", width: "fit-content" };
const tabBtn = (active: boolean): CSSProperties => ({
  ...btn,
  border: active ? "2px solid #0f172a" : "1px solid #ccc",
  fontWeight: active ? 600 : 400
});
const pre: CSSProperties = {
  background: "#0b1020",
  color: "#e7ecff",
  padding: 12,
  borderRadius: 8,
  overflow: "auto",
  fontSize: 12
};
