"use client";

import Link from "next/link";
import type { CSSProperties } from "react";
import { useCallback, useEffect, useMemo, useState } from "react";

import { readAccessToken, withAuthHeaders } from "@/lib/auth-token";

type CourseRow = {
  id: string;
  title: string;
  code: string | null;
  term: string | null;
  description: string | null;
};

export default function DashboardPage() {
  const apiBase = useMemo(
    () => process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000",
    []
  );
  const [courses, setCourses] = useState<CourseRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setError(null);
    const t = readAccessToken();
    if (!t) {
      setCourses(null);
      setError("No access token. Sign in at /courses/demo/auth first.");
      return;
    }
    const res = await fetch(`${apiBase}/courses`, { headers: withAuthHeaders() });
    if (!res.ok) {
      setError(await res.text());
      setCourses(null);
      return;
    }
    setCourses((await res.json()) as CourseRow[]);
  }, [apiBase]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <main style={{ fontFamily: "Inter, sans-serif", padding: "2rem", maxWidth: 960 }}>
      <h1>Instructor / learner hub</h1>
      <p style={{ color: "#475569" }}>
        Lists courses where you are a member. This page is a thin shell over the authenticated API — useful as the
        anchor for future analytics, roster tools, and eval dashboards.
      </p>

      <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 20 }}>
        <button type="button" onClick={() => load()} style={btn}>
          Refresh courses
        </button>
        <Link href="/courses/demo/auth" style={{ ...btn, display: "inline-block", textDecoration: "none" }}>
          Auth
        </Link>
        <Link href="/courses/demo/documents" style={{ ...btn, display: "inline-block", textDecoration: "none" }}>
          Documents
        </Link>
        <Link href="/courses/demo/qa" style={{ ...btn, display: "inline-block", textDecoration: "none" }}>
          QA
        </Link>
        <Link href="/courses/demo/lessons" style={{ ...btn, display: "inline-block", textDecoration: "none" }}>
          Lessons
        </Link>
        <Link href="/courses/demo/assessment" style={{ ...btn, display: "inline-block", textDecoration: "none" }}>
          Assessment
        </Link>
      </div>

      {error ? <pre style={{ color: "#b00020", whiteSpace: "pre-wrap" }}>{error}</pre> : null}

      {!courses ? (
        !error ? <p style={{ color: "#64748b" }}>Loading…</p> : null
      ) : courses.length === 0 ? (
        <p style={{ color: "#64748b" }}>No courses yet. Create one via API or seed script.</p>
      ) : (
        <section style={{ display: "grid", gap: 12 }}>
          {courses.map((c) => (
            <article key={c.id} style={card}>
              <h2 style={{ margin: "0 0 8px", fontSize: 18 }}>{c.title}</h2>
              <p style={{ margin: 0, color: "#64748b", fontSize: 14 }}>
                {c.code ?? "—"} · {c.term ?? "—"}
              </p>
              <p style={{ margin: "8px 0 0", color: "#334155" }}>{c.description ?? ""}</p>
              <p style={{ margin: "10px 0 0", fontFamily: "ui-monospace, monospace", fontSize: 12 }}>id: {c.id}</p>
            </article>
          ))}
        </section>
      )}

      <section style={{ marginTop: 32, padding: 16, background: "#f8fafc", borderRadius: 12, border: "1px solid #e2e8f0" }}>
        <h2 style={{ marginTop: 0, fontSize: 16 }}>Golden QA (CLI)</h2>
        <p style={{ margin: "0 0 8px", color: "#475569", fontSize: 14 }}>
          After seeding + ingest, run <code>python scripts/run_golden_qa.py</code> with{" "}
          <code>GOLDEN_EMAIL</code>, <code>GOLDEN_PASSWORD</code>, <code>GOLDEN_COURSE_ID</code>. See{" "}
          <code>docs/eval/README.md</code>.
        </p>
      </section>
    </main>
  );
}

const btn: CSSProperties = {
  padding: "10px 14px",
  borderRadius: 8,
  border: "1px solid #cbd5e1",
  background: "#fff",
  cursor: "pointer",
  color: "#0f172a"
};

const card: CSSProperties = {
  border: "1px solid #e2e8f0",
  borderRadius: 12,
  padding: 16,
  background: "#fff"
};
