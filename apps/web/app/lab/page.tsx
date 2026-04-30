"use client";

import Link from "next/link";
import type { CSSProperties } from "react";
import { useMemo, useState } from "react";

const cardStyle: CSSProperties = {
  border: "1px solid #e2e8f0",
  borderRadius: 12,
  padding: 16,
  background: "#fff"
};

const focusIdeas = [
  "Tighten one API error message so the UI can show a clearer hint.",
  "Improve one demo page with better defaults and less typing.",
  "Add one contract test for an edge case payload.",
  "Refactor one service function name for readability.",
  "Polish one prompt template with stricter output constraints."
];

const kitPreview = [
  {
    id: "quickstart-ai-study.json",
    topic: "Retrieval + adaptive quizzes",
    level: "easy",
    keyPoints: ["Ground answers in chunks", "Keep lessons focused", "Adapt after mistakes"],
    prompts: ["Why citations improve trust", "Design a 5-minute lesson", "One QA failure mode"]
  },
  {
    id: "language-learning-starter.json",
    topic: "Vocabulary and explainable QA",
    level: "easy",
    keyPoints: ["Short context per term", "One example sentence", "Prioritize weak terms"],
    prompts: ["Define retrieval grounding", "Write a technical sentence", "Revisit missed words"]
  },
  {
    id: "data-science-basics.json",
    topic: "From framing to interpretable decisions",
    level: "medium",
    keyPoints: ["Frame problem first", "Start with baselines", "Track data risks"],
    prompts: ["Risk of biased data", "Two baseline metrics", "When simple beats complex"]
  },
  {
    id: "algorithms-playground.json",
    topic: "Complexity and trade-off thinking",
    level: "hard",
    keyPoints: ["Define IO clearly", "Compare brute vs optimized", "Explain complexity plainly"],
    prompts: ["Hash map advantage", "Binary search edge case", "Readability vs optimization"]
  },
  {
    id: "prompt-design-basics.json",
    topic: "Structured output prompt habits",
    level: "medium",
    keyPoints: ["State format constraints", "Separate goal vs style", "Add fallback behavior"],
    prompts: ["Rewrite vague prompt", "Ambiguous constraint failure", "Safe low-evidence fallback"]
  }
];

export default function LabPage() {
  const [checked, setChecked] = useState<Record<string, boolean>>({});
  const [seed, setSeed] = useState<number>(0);
  const [levelFilter, setLevelFilter] = useState<string>("all");
  const [selectedKit, setSelectedKit] = useState<string>(kitPreview[0].id);
  const [expandedKit, setExpandedKit] = useState<string>(kitPreview[0].id);

  const idea = useMemo(() => {
    const idx = Math.abs(seed) % focusIdeas.length;
    return focusIdeas[idx];
  }, [seed]);
  const filteredKits = useMemo(
    () => kitPreview.filter((k) => levelFilter === "all" || k.level === levelFilter),
    [levelFilter]
  );
  const currentKitIds = filteredKits.map((k) => k.id);
  const activeSelectedKit = currentKitIds.includes(selectedKit) ? selectedKit : currentKitIds[0] ?? kitPreview[0].id;
  const activeKit = filteredKits.find((k) => k.id === activeSelectedKit) ?? filteredKits[0] ?? kitPreview[0];
  const quickstartCommand = "npm run hobby:quickstart";

  const toggle = (k: string) => {
    setChecked((prev) => ({ ...prev, [k]: !prev[k] }));
  };

  return (
    <main style={{ fontFamily: "Inter, sans-serif", padding: "2rem", maxWidth: 960 }}>
      <h1>Hobby Lab</h1>
      <p style={{ color: "#475569" }}>
        A lightweight playground for one-session experiments. Nothing here writes progress logs or usage history.
      </p>

      <article style={{ ...cardStyle, marginBottom: 12, background: "#f8fafc" }}>
        <h2 style={{ marginTop: 0 }}>Today focus</h2>
        <p style={{ margin: "6px 0 10px" }}>{idea}</p>
        <button
          type="button"
          onClick={() => setSeed((v) => v + 1)}
          style={{ padding: "8px 12px", borderRadius: 8, border: "1px solid #cbd5e1", background: "#fff" }}
        >
          Next idea
        </button>
      </article>

      <article style={{ ...cardStyle, marginBottom: 12 }}>
        <h2 style={{ marginTop: 0 }}>Session checklist (local only)</h2>
        <label style={{ display: "block", marginBottom: 6 }}>
          <input type="checkbox" checked={!!checked.schemas} onChange={() => toggle("schemas")} /> Run
          ` validate:schemas `
        </label>
        <label style={{ display: "block", marginBottom: 6 }}>
          <input type="checkbox" checked={!!checked.unit} onChange={() => toggle("unit")} /> Run ` test:api:unit `
        </label>
        <label style={{ display: "block" }}>
          <input type="checkbox" checked={!!checked.sdk} onChange={() => toggle("sdk")} /> Run ` sdk:ts:check ` only
          if API contract changed
        </label>
      </article>

      <section style={{ display: "grid", gap: 12 }}>
        <article style={cardStyle}>
          <h2 style={{ marginTop: 0 }}>Fast API Flow</h2>
          <p>Sign in, list courses, and run QA in one pass.</p>
          <p>
            <Link href="/courses/demo/auth">Auth</Link> · <Link href="/dashboard">Dashboard</Link> ·{" "}
            <Link href="/courses/demo/qa">QA</Link>
          </p>
        </article>

        <article style={cardStyle}>
          <h2 style={{ marginTop: 0 }}>Content Pipeline</h2>
          <p>Upload a document, process chunks, then compile lessons.</p>
          <p>
            <Link href="/courses/demo/documents">Documents</Link> ·{" "}
            <Link href="/courses/demo/lessons">Lessons</Link>
          </p>
        </article>

        <article style={cardStyle}>
          <h2 style={{ marginTop: 0 }}>Learning Loop</h2>
          <p>Try adaptive assessment + concept graph in one session.</p>
          <p>
            <Link href="/courses/demo/assessment">Assessment</Link> ·{" "}
            <Link href="/courses/demo/graph">Concept graph</Link>
          </p>
        </article>

        <article style={cardStyle}>
          <h2 style={{ marginTop: 0 }}>Hobby Kits</h2>
          <p>Use reusable mini materials from `packages/hobby-kits` for quick experiments.</p>
          <p style={{ margin: "0 0 6px", fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace", fontSize: 13 }}>
            npm run hobby:kits
          </p>
          <p style={{ margin: "0 0 6px", fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace", fontSize: 13 }}>
            {quickstartCommand}
          </p>
          <label style={{ display: "block", fontSize: 13, color: "#475569", marginBottom: 6 }}>
            Level:
            <select
              value={levelFilter}
              onChange={(e) => setLevelFilter(e.target.value)}
              style={{ marginLeft: 8, border: "1px solid #cbd5e1", borderRadius: 6, padding: "4px 6px" }}
            >
              <option value="all">all</option>
              <option value="easy">easy</option>
              <option value="medium">medium</option>
              <option value="hard">hard</option>
            </select>
          </label>
          <label style={{ display: "block", fontSize: 13, color: "#475569", marginBottom: 6 }}>
            Pick a kit:
            <select
              value={activeSelectedKit}
              onChange={(e) => setSelectedKit(e.target.value)}
              style={{ marginLeft: 8, border: "1px solid #cbd5e1", borderRadius: 6, padding: "4px 6px" }}
            >
              {filteredKits.map((k) => (
                <option key={k.id} value={k.id}>
                  {k.id}
                </option>
              ))}
            </select>
          </label>
          <p style={{ margin: 0, fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace", fontSize: 13 }}>
            {`npm run hobby:kit -- --kit ${activeSelectedKit}`}
          </p>
          <p style={{ margin: "6px 0 0", fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace", fontSize: 13 }}>
            {`npm run hobby:drill -- --kit ${activeSelectedKit} --count 3`}
          </p>
          <p style={{ margin: "6px 0 0", fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace", fontSize: 13 }}>
            {`npm run hobby:golden -- --kit ${activeSelectedKit} --limit 6`}
          </p>
          <p style={{ margin: "6px 0 0", fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace", fontSize: 13 }}>
            {`npm run hobby:golden:pack -- --level ${levelFilter === "all" ? "all" : levelFilter} --per-kit-limit 3`}
          </p>
          <p style={{ margin: "6px 0 0", fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace", fontSize: 13 }}>
            {"npm run hobby:kit:new -- --title 'My New Kit' --topic 'Your Topic' --level easy"}
          </p>
          <div style={{ marginTop: 10, fontSize: 14, color: "#334155" }}>
            {filteredKits.map((k) => (
              <div key={k.id} style={{ marginBottom: 8 }}>
                <button
                  type="button"
                  onClick={() => setExpandedKit(expandedKit === k.id ? "" : k.id)}
                  style={{
                    border: "1px solid #cbd5e1",
                    borderRadius: 6,
                    background: "#fff",
                    padding: "4px 8px",
                    marginRight: 8
                  }}
                >
                  {expandedKit === k.id ? "Hide" : "Show"}
                </button>
                <strong>{k.id}</strong> [{k.level}] - {k.topic}
                {expandedKit === k.id ? (
                  <div style={{ marginTop: 6, paddingLeft: 8 }}>
                    <div style={{ marginBottom: 4 }}>
                      <strong>Key points:</strong> {k.keyPoints.join(" / ")}
                    </div>
                    <div>
                      <strong>Prompts:</strong> {k.prompts.join(" / ")}
                    </div>
                  </div>
                ) : null}
              </div>
            ))}
          </div>
          <p style={{ marginTop: 10, color: "#475569", fontSize: 13 }}>
            Active kit: <strong>{activeKit.id}</strong>
          </p>
        </article>
      </section>
    </main>
  );
}
