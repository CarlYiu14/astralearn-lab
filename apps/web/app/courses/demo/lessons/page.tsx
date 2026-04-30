"use client";

import type { CSSProperties } from "react";
import { useMemo, useState } from "react";

import { withAuthHeaders } from "@/lib/auth-token";

type CompileResponse = {
  mode: "sync" | "async";
  lesson_unit_id?: string;
  job_id?: string;
};

type LessonSummary = {
  id: string;
  title: string;
  status: string;
  source_document_id: string;
  published_at?: string | null;
};

export default function LessonsDemoPage() {
  const apiBase = useMemo(
    () => process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000",
    []
  );
  const defaultCourseId = process.env.NEXT_PUBLIC_COURSE_ID ?? "";

  const [courseId, setCourseId] = useState(defaultCourseId);
  const [documentId, setDocumentId] = useState("");
  const [runAsync, setRunAsync] = useState(false);
  const [compileResult, setCompileResult] = useState<CompileResponse | null>(null);
  const [lessons, setLessons] = useState<LessonSummary[] | null>(null);
  const [lessonId, setLessonId] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function compileLesson() {
    setError(null);
    setCompileResult(null);
    if (!courseId || !documentId) {
      setError("courseId and documentId are required.");
      return;
    }
    const res = await fetch(`${apiBase}/courses/${courseId}/lessons/compile`, {
      method: "POST",
      headers: withAuthHeaders({ "content-type": "application/json" }),
      body: JSON.stringify({ source_document_id: documentId, run_async: runAsync })
    });
    if (!res.ok) {
      setError(await res.text());
      return;
    }
    setCompileResult((await res.json()) as CompileResponse);
  }

  async function loadLessons(status?: "draft" | "published" | "all") {
    setError(null);
    if (!courseId) {
      setError("courseId is required.");
      return;
    }
    const qs = status && status !== "all" ? `?status=${encodeURIComponent(status)}` : "";
    const res = await fetch(`${apiBase}/courses/${courseId}/lessons${qs}`, { headers: withAuthHeaders() });
    if (!res.ok) {
      setError(await res.text());
      return;
    }
    setLessons((await res.json()) as LessonSummary[]);
  }

  async function publishLesson(mode: "publish" | "unpublish") {
    setError(null);
    if (!courseId || !lessonId) {
      setError("courseId and lessonId are required.");
      return;
    }
    const path =
      mode === "publish"
        ? `${apiBase}/courses/${courseId}/lessons/${lessonId}/publish`
        : `${apiBase}/courses/${courseId}/lessons/${lessonId}/unpublish`;
    const res = await fetch(path, { method: "POST", headers: withAuthHeaders() });
    if (!res.ok) {
      setError(await res.text());
      return;
    }
    await loadLessons();
  }

  return (
    <main style={{ fontFamily: "Inter, sans-serif", padding: "2rem", maxWidth: 980 }}>
      <h1>Lesson compiler</h1>
      <p style={{ color: "#444" }}>
        Day 6-7: compile a micro-lesson, publish it, and optionally enqueue async compilation. If{" "}
        <code>INTERNAL_API_KEY</code> is enabled on the API, poll job status with a trusted client that can send{" "}
        <code>X-Internal-Key</code> (avoid putting secrets in the browser). Day 8: JWT on all calls —{" "}
        <a href="/courses/demo/auth">/courses/demo/auth</a>.
      </p>

      <section style={{ display: "grid", gap: 12, maxWidth: 720 }}>
        <label style={{ display: "grid", gap: 6 }}>
          <span>Course ID</span>
          <input value={courseId} onChange={(e) => setCourseId(e.target.value)} style={inputStyle} />
        </label>
        <label style={{ display: "grid", gap: 6 }}>
          <span>Source document ID</span>
          <input value={documentId} onChange={(e) => setDocumentId(e.target.value)} style={inputStyle} />
        </label>
        <label style={{ display: "flex", gap: 10, alignItems: "center" }}>
          <input type="checkbox" checked={runAsync} onChange={(e) => setRunAsync(e.target.checked)} />
          <span>run_async (enqueue job)</span>
        </label>
        <label style={{ display: "grid", gap: 6 }}>
          <span>Lesson ID (for publish)</span>
          <input value={lessonId} onChange={(e) => setLessonId(e.target.value)} style={inputStyle} />
        </label>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <button type="button" onClick={compileLesson} style={btnStyle}>
            Compile
          </button>
          <button type="button" onClick={() => loadLessons()} style={btnStyle}>
            List lessons
          </button>
          <button type="button" onClick={() => loadLessons("published")} style={btnStyle}>
            List published
          </button>
          <button type="button" onClick={() => publishLesson("publish")} style={btnStyle}>
            Publish
          </button>
          <button type="button" onClick={() => publishLesson("unpublish")} style={btnStyle}>
            Unpublish
          </button>
        </div>
      </section>

      {error ? <pre style={{ marginTop: 16, color: "#b00020", whiteSpace: "pre-wrap" }}>{error}</pre> : null}

      {compileResult ? (
        <section style={{ marginTop: 18 }}>
          <h2>Compile result</h2>
          <pre style={preStyle}>{JSON.stringify(compileResult, null, 2)}</pre>
          {compileResult.mode === "async" && compileResult.job_id ? (
            <p style={{ color: "#334155" }}>
              Poll job: <code>{`${apiBase}/internal/jobs/${compileResult.job_id}`}</code>
            </p>
          ) : null}
        </section>
      ) : null}

      {lessons ? (
        <section style={{ marginTop: 18 }}>
          <h2>Lessons</h2>
          <pre style={preStyle}>{JSON.stringify(lessons, null, 2)}</pre>
        </section>
      ) : null}
    </main>
  );
}

const inputStyle: CSSProperties = { padding: 10, borderRadius: 8, border: "1px solid #ccc" };
const btnStyle: CSSProperties = { padding: "10px 14px" };
const preStyle: CSSProperties = {
  background: "#0b1020",
  color: "#e7ecff",
  padding: 12,
  borderRadius: 8,
  overflow: "auto"
};
