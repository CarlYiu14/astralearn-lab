"use client";

import { useMemo, useState } from "react";

import { withAuthHeaders } from "@/lib/auth-token";

type ProcessResponse = {
  id: string;
  course_id: string;
  status: string;
  chunk_count: number;
  char_count: number;
};

type UploadResponse = {
  id: string;
  course_id: string;
  title: string;
  status: string;
  file_path: string;
  created_at: string;
};

export default function DocumentUploadDemoPage() {
  const apiBase = useMemo(
    () => process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000",
    []
  );
  const defaultCourseId = process.env.NEXT_PUBLIC_COURSE_ID ?? "";

  const [courseId, setCourseId] = useState(defaultCourseId);
  const [file, setFile] = useState<File | null>(null);
  const [upload, setUpload] = useState<UploadResponse | null>(null);
  const [processResult, setProcessResult] = useState<ProcessResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function uploadFile() {
    setError(null);
    setProcessResult(null);
    setUpload(null);

    if (!courseId) {
      setError("Set a course id (create a course first).");
      return;
    }
    if (!file) {
      setError("Pick a .txt or .md file.");
      return;
    }

    const form = new FormData();
    form.append("file", file);

    const res = await fetch(`${apiBase}/courses/${courseId}/documents/upload`, {
      method: "POST",
      headers: withAuthHeaders(),
      body: form
    });

    if (!res.ok) {
      const text = await res.text();
      setError(`Upload failed (${res.status}): ${text}`);
      return;
    }

    setUpload((await res.json()) as UploadResponse);
  }

  async function processLatest() {
    setError(null);
    setProcessResult(null);

    if (!upload) {
      setError("Upload a document first.");
      return;
    }

    const res = await fetch(`${apiBase}/courses/${courseId}/documents/${upload.id}/process`, {
      method: "POST",
      headers: withAuthHeaders({ "content-type": "application/json" }),
      body: JSON.stringify({ mode: "sync", reprocess: true })
    });

    if (!res.ok) {
      const text = await res.text();
      setError(`Process failed (${res.status}): ${text}`);
      return;
    }

    setProcessResult((await res.json()) as ProcessResponse);
  }

  return (
    <main style={{ fontFamily: "Inter, sans-serif", padding: "2rem", maxWidth: 920 }}>
      <h1>Document upload</h1>
      <p style={{ color: "#444" }}>
        Day 3: uploads a course file, chunks it, and stores rows in <code>document_chunks</code> (placeholder embeddings
        for now). Day 8: sign in at <a href="/courses/demo/auth">/courses/demo/auth</a> — upload requires instructor or
        owner on the course.
      </p>

      <section style={{ display: "grid", gap: 12, maxWidth: 640 }}>
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
          <span>File</span>
          <input type="file" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
        </label>

        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <button type="button" onClick={uploadFile} style={{ padding: "10px 14px" }}>
            Upload
          </button>
          <button type="button" onClick={processLatest} style={{ padding: "10px 14px" }} disabled={!upload}>
            Process
          </button>
        </div>
      </section>

      {error ? (
        <pre style={{ marginTop: 16, color: "#b00020", whiteSpace: "pre-wrap" }}>{error}</pre>
      ) : null}

      {upload ? (
        <section style={{ marginTop: 20 }}>
          <h2>Upload</h2>
          <pre style={{ background: "#0b1020", color: "#e7ecff", padding: 12, borderRadius: 8, overflow: "auto" }}>
            {JSON.stringify(upload, null, 2)}
          </pre>
        </section>
      ) : null}

      {processResult ? (
        <section style={{ marginTop: 20 }}>
          <h2>Process</h2>
          <pre style={{ background: "#0b1020", color: "#e7ecff", padding: 12, borderRadius: 8, overflow: "auto" }}>
            {JSON.stringify(processResult, null, 2)}
          </pre>
        </section>
      ) : null}
    </main>
  );
}
