"use client";

import type { CSSProperties } from "react";
import { useMemo, useState } from "react";

import { withAuthHeaders } from "@/lib/auth-token";

type NextQuestionResponse = {
  question: {
    id: string;
    difficulty: number;
    q_type: string;
    prompt: string;
  } | null;
  target_difficulty: number;
  ability_theta: number;
};

type SubmitResponse = {
  is_correct: boolean;
  score: number;
  q_type: string;
  ability_theta: number;
};

export default function AssessmentDemoPage() {
  const apiBase = useMemo(
    () => process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000",
    []
  );
  const defaultCourseId = process.env.NEXT_PUBLIC_COURSE_ID ?? "";

  const [courseId, setCourseId] = useState(defaultCourseId);
  const [sessionId, setSessionId] = useState("");
  const [questionId, setQuestionId] = useState("");
  const [prompt, setPrompt] = useState("");
  const [answer, setAnswer] = useState("");
  const [lastResult, setLastResult] = useState<SubmitResponse | null>(null);
  const [nextMeta, setNextMeta] = useState<{ target: number; theta: number } | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function createSession() {
    setError(null);
    setLastResult(null);
    if (!courseId) {
      setError("courseId is required.");
      return;
    }
    const res = await fetch(`${apiBase}/courses/${courseId}/assessment/sessions`, {
      method: "POST",
      headers: withAuthHeaders({ "content-type": "application/json" }),
      body: JSON.stringify({})
    });
    if (!res.ok) {
      setError(await res.text());
      return;
    }
    const data = (await res.json()) as { session_id: string };
    setSessionId(data.session_id);
  }

  async function nextQuestion() {
    setError(null);
    setLastResult(null);
    if (!courseId || !sessionId) {
      setError("Create a session first.");
      return;
    }
    const res = await fetch(`${apiBase}/courses/${courseId}/assessment/sessions/${sessionId}/next-question`, {
      method: "POST",
      headers: withAuthHeaders()
    });
    if (!res.ok) {
      setError(await res.text());
      return;
    }
    const data = (await res.json()) as NextQuestionResponse;
    setNextMeta({ target: data.target_difficulty, theta: data.ability_theta });
    if (!data.question) {
      setPrompt("No more questions (or bank is exhausted).");
      setQuestionId("");
      return;
    }
    setQuestionId(data.question.id);
    setPrompt(data.question.prompt);
  }

  async function submit() {
    setError(null);
    setLastResult(null);
    if (!courseId || !sessionId || !questionId) {
      setError("Need courseId, sessionId, and a question id from next-question.");
      return;
    }
    const res = await fetch(`${apiBase}/courses/${courseId}/assessment/sessions/${sessionId}/submit`, {
      method: "POST",
      headers: withAuthHeaders({ "content-type": "application/json" }),
      body: JSON.stringify({ question_id: questionId, user_answer: answer })
    });
    if (!res.ok) {
      setError(await res.text());
      return;
    }
    setLastResult((await res.json()) as SubmitResponse);
  }

  return (
    <main style={{ fontFamily: "Inter, sans-serif", padding: "2rem", maxWidth: 980 }}>
      <h1>Adaptive assessment (MVP)</h1>
      <p style={{ color: "#444" }}>
        Day 6-7: practice sessions seed questions from indexed chunks, adapt difficulty using the last attempt, and
        maintain an online 1PL-style <code>ability_theta</code> estimate after each graded submit. Day 8: sessions bind
        to the signed-in user — <a href="/courses/demo/auth">auth demo</a>.
      </p>

      <section style={{ display: "grid", gap: 12, maxWidth: 760 }}>
        <label style={{ display: "grid", gap: 6 }}>
          <span>Course ID</span>
          <input value={courseId} onChange={(e) => setCourseId(e.target.value)} style={input} />
        </label>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <button type="button" onClick={createSession} style={btn}>
            Create session
          </button>
          <button type="button" onClick={nextQuestion} style={btn}>
            Next question
          </button>
        </div>
        <div style={{ color: "#334155" }}>
          <strong>session_id</strong>: {sessionId || "—"}
        </div>
        {nextMeta ? (
          <div style={{ color: "#334155" }}>
            <strong>last next-question</strong>: target_difficulty={nextMeta.target}, ability_theta={nextMeta.theta}
          </div>
        ) : null}

        <label style={{ display: "grid", gap: 6 }}>
          <span>Answer</span>
          <textarea value={answer} onChange={(e) => setAnswer(e.target.value)} rows={4} style={input} />
        </label>
        <button type="button" onClick={submit} style={btn}>
          Submit
        </button>
      </section>

      {error ? <pre style={{ marginTop: 16, color: "#b00020", whiteSpace: "pre-wrap" }}>{error}</pre> : null}

      {prompt ? (
        <section style={{ marginTop: 18 }}>
          <h2>Prompt</h2>
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
            {prompt}
          </pre>
        </section>
      ) : null}

      {lastResult ? (
        <section style={{ marginTop: 18 }}>
          <h2>Result</h2>
          <pre
            style={{
              background: "#0b1020",
              color: "#e7ecff",
              padding: 12,
              borderRadius: 8,
              overflow: "auto"
            }}
          >
            {JSON.stringify(lastResult, null, 2)}
          </pre>
        </section>
      ) : null}
    </main>
  );
}

const input: CSSProperties = { padding: 10, borderRadius: 8, border: "1px solid #ccc", resize: "vertical" };
const btn: CSSProperties = { padding: "10px 14px" };
