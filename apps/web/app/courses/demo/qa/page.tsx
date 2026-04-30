"use client";

import { useMemo, useState } from "react";

import { withAuthHeaders } from "@/lib/auth-token";

type CourseQAResponse = {
  answer: string;
  citations: Array<{ chunk_id: string; document_id: string; quote: string }>;
  confidence: "high" | "medium" | "low";
  mode: "llm" | "extractive";
  retrieved_chunk_ids: string[];
};

export default function CourseQADemoPage() {
  const apiBase = useMemo(
    () => process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000",
    []
  );
  const defaultCourseId = process.env.NEXT_PUBLIC_COURSE_ID ?? "";

  const [courseId, setCourseId] = useState(defaultCourseId);
  const [question, setQuestion] = useState("What are the key deadlines in this syllabus?");
  const [topK, setTopK] = useState(8);
  const [result, setResult] = useState<CourseQAResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function ask() {
    setError(null);
    setResult(null);

    if (!courseId) {
      setError("Set a course id (seed one with scripts/seed_dev_course.py).");
      return;
    }

    const res = await fetch(`${apiBase}/courses/${courseId}/qa`, {
      method: "POST",
      headers: withAuthHeaders({ "content-type": "application/json" }),
      body: JSON.stringify({ question, top_k: topK })
    });

    if (!res.ok) {
      const text = await res.text();
      setError(`QA failed (${res.status}): ${text}`);
      return;
    }

    setResult((await res.json()) as CourseQAResponse);
  }

  return (
    <main style={{ fontFamily: "Inter, sans-serif", padding: "2rem", maxWidth: 980 }}>
      <h1>Course QA</h1>
      <p style={{ color: "#444" }}>
        Day 4: vector retrieval over <code>document_chunks</code>, then JSON-grounded synthesis when{" "}
        <code>OPENAI_API_KEY</code> is configured. Day 8: course members only — use{" "}
        <a href="/courses/demo/auth">/courses/demo/auth</a>.
      </p>

      <section style={{ display: "grid", gap: 12, maxWidth: 760 }}>
        <label style={{ display: "grid", gap: 6 }}>
          <span>Course ID</span>
          <input
            value={courseId}
            onChange={(e) => setCourseId(e.target.value)}
            placeholder="00000000-0000-0000-0000-000000000000"
            style={{ padding: 10, borderRadius: 8, border: "1px solid #ccc" }}
          />
        </label>

        <label style={{ display: "grid", gap: 6 }}>
          <span>Question</span>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            rows={5}
            style={{ padding: 10, borderRadius: 8, border: "1px solid #ccc", resize: "vertical" }}
          />
        </label>

        <label style={{ display: "grid", gap: 6 }}>
          <span>top_k</span>
          <input
            type="number"
            min={1}
            max={24}
            value={topK}
            onChange={(e) => setTopK(Number(e.target.value))}
            style={{ padding: 10, borderRadius: 8, border: "1px solid #ccc", maxWidth: 200 }}
          />
        </label>

        <button type="button" onClick={ask} style={{ padding: "10px 14px", width: "fit-content" }}>
          Ask
        </button>
      </section>

      {error ? (
        <pre style={{ marginTop: 16, color: "#b00020", whiteSpace: "pre-wrap" }}>{error}</pre>
      ) : null}

      {result ? (
        <section style={{ marginTop: 22 }}>
          <h2>Answer</h2>
          <p style={{ color: "#444" }}>
            <strong>mode</strong>: {result.mode} · <strong>confidence</strong>: {result.confidence} ·{" "}
            <strong>retrieved</strong>: {result.retrieved_chunk_ids.length}
          </p>
          <pre
            style={{
              background: "#0b1020",
              color: "#e7ecff",
              padding: 12,
              borderRadius: 8,
              overflow: "auto",
              whiteSpace: "pre-wrap"
            }}
          >
            {result.answer}
          </pre>

          <h3 style={{ marginTop: 18 }}>Citations</h3>
          <pre style={{ background: "#0b1020", color: "#e7ecff", padding: 12, borderRadius: 8, overflow: "auto" }}>
            {JSON.stringify(result.citations, null, 2)}
          </pre>
        </section>
      ) : null}
    </main>
  );
}
