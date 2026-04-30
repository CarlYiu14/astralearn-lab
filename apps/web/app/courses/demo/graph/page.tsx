"use client";

import { useMemo, useState } from "react";

import { withAuthHeaders } from "@/lib/auth-token";

type GraphNode = {
  id: string;
  slug: string;
  name: string;
  description: string | null;
  difficulty: number | null;
};

type GraphEdge = {
  id: string;
  from_node_id: string;
  to_node_id: string;
  edge_type: string;
  weight: number;
};

type GraphSnapshot = {
  nodes: GraphNode[];
  edges: GraphEdge[];
};

type ExtractResponse = {
  mode: "llm" | "heuristic";
  node_count: number;
  edge_count: number;
  chunks_sampled: number;
};

export default function CourseGraphDemoPage() {
  const apiBase = useMemo(
    () => process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000",
    []
  );
  const defaultCourseId = process.env.NEXT_PUBLIC_COURSE_ID ?? "";

  const [courseId, setCourseId] = useState(defaultCourseId);
  const [maxChunks, setMaxChunks] = useState<number | "">(48);
  const [snapshot, setSnapshot] = useState<GraphSnapshot | null>(null);
  const [extractInfo, setExtractInfo] = useState<ExtractResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const layout = useMemo(() => {
    if (!snapshot || snapshot.nodes.length === 0) {
      return { positions: new Map<string, { x: number; y: number }>(), cx: 260, cy: 260, r: 200 };
    }

    const cx = 260;
    const cy = 260;
    const r = 200;
    const n = snapshot.nodes.length;
    const positions = new Map<string, { x: number; y: number }>();

    snapshot.nodes.forEach((node, i) => {
      const angle = (2 * Math.PI * i) / n - Math.PI / 2;
      positions.set(node.id, { x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) });
    });

    return { positions, cx, cy, r };
  }, [snapshot]);

  async function loadGraph() {
    setError(null);
    setExtractInfo(null);
    if (!courseId) {
      setError("Set a course id.");
      return;
    }
    const res = await fetch(`${apiBase}/courses/${courseId}/graph`, { headers: withAuthHeaders() });
    if (!res.ok) {
      setError(await res.text());
      return;
    }
    setSnapshot((await res.json()) as GraphSnapshot);
  }

  async function extractGraph() {
    setError(null);
    setExtractInfo(null);
    if (!courseId) {
      setError("Set a course id.");
      return;
    }
    const mc = maxChunks === "" ? undefined : Number(maxChunks);
    const body = mc === undefined || !Number.isFinite(mc) ? {} : { max_chunks: mc };

    const res = await fetch(`${apiBase}/courses/${courseId}/graph/extract`, {
      method: "POST",
      headers: withAuthHeaders({ "content-type": "application/json" }),
      body: JSON.stringify(body)
    });
    if (!res.ok) {
      setError(await res.text());
      return;
    }
    setExtractInfo((await res.json()) as ExtractResponse);
    await loadGraph();
  }

  return (
    <main style={{ fontFamily: "Inter, sans-serif", padding: "2rem", maxWidth: 1100 }}>
      <h1>Concept graph</h1>
      <p style={{ color: "#444" }}>
        Day 5: sample indexed chunks, extract <code>concept_nodes</code> + <code>concept_edges</code>, then render a
        lightweight SVG preview. With <code>OPENAI_API_KEY</code>, extraction uses JSON structured output; otherwise a
        deterministic heuristic is used. Day 8: auth required; extract needs instructor or owner.
      </p>
      <p style={{ color: "#64748b", fontSize: 14 }}>
        <a href="/courses/demo/auth">Sign in</a> first.
      </p>

      <section style={{ display: "grid", gap: 12, maxWidth: 720 }}>
        <label style={{ display: "grid", gap: 6 }}>
          <span>Course ID</span>
          <input
            value={courseId}
            onChange={(e) => setCourseId(e.target.value)}
            style={{ padding: 10, borderRadius: 8, border: "1px solid #ccc" }}
          />
        </label>

        <label style={{ display: "grid", gap: 6 }}>
          <span>max_chunks (optional)</span>
          <input
            type="number"
            value={maxChunks}
            onChange={(e) => {
              const v = e.target.value;
              setMaxChunks(v === "" ? "" : Number(v));
            }}
            style={{ padding: 10, borderRadius: 8, border: "1px solid #ccc", maxWidth: 220 }}
          />
        </label>

        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <button type="button" onClick={extractGraph} style={{ padding: "10px 14px" }}>
            Extract graph
          </button>
          <button type="button" onClick={loadGraph} style={{ padding: "10px 14px" }}>
            Load graph
          </button>
        </div>
      </section>

      {error ? (
        <pre style={{ marginTop: 16, color: "#b00020", whiteSpace: "pre-wrap" }}>{error}</pre>
      ) : null}

      {extractInfo ? (
        <p style={{ marginTop: 14, color: "#0f172a" }}>
          <strong>Last extract</strong>: mode={extractInfo.mode}, nodes={extractInfo.node_count}, edges=
          {extractInfo.edge_count}, chunks_sampled={extractInfo.chunks_sampled}
        </p>
      ) : null}

      {snapshot && snapshot.nodes.length > 0 ? (
        <section style={{ marginTop: 22, display: "grid", gap: 16, gridTemplateColumns: "minmax(0, 1fr)" }}>
          <div style={{ border: "1px solid #e2e8f0", borderRadius: 12, overflow: "hidden" }}>
            <svg width="100%" viewBox="0 0 520 520" role="img" aria-label="Concept graph preview">
              <rect x="0" y="0" width="520" height="520" fill="#f8fafc" />
              {snapshot.edges.map((e) => {
                const a = layout.positions.get(e.from_node_id);
                const b = layout.positions.get(e.to_node_id);
                if (!a || !b) return null;
                const stroke = e.edge_type === "prerequisite" ? "#b45309" : "#64748b";
                return (
                  <line
                    key={e.id}
                    x1={a.x}
                    y1={a.y}
                    x2={b.x}
                    y2={b.y}
                    stroke={stroke}
                    strokeWidth={2}
                    opacity={0.85}
                  />
                );
              })}
              {snapshot.nodes.map((n) => {
                const p = layout.positions.get(n.id);
                if (!p) return null;
                return (
                  <g key={n.id}>
                    <circle cx={p.x} cy={p.y} r={10} fill="#0f172a" stroke="#e2e8f0" strokeWidth={2} />
                    <text
                      x={p.x}
                      y={p.y + 26}
                      textAnchor="middle"
                      fill="#0f172a"
                      fontSize="11"
                      style={{ fontFamily: "Inter, sans-serif" }}
                    >
                      {n.name.length > 28 ? `${n.name.slice(0, 28)}…` : n.name}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>

          <aside
            style={{
              border: "1px solid #e2e8f0",
              borderRadius: 12,
              padding: 12,
              maxHeight: 360,
              overflow: "auto"
            }}
          >
            <h2 style={{ marginTop: 0, fontSize: 16 }}>Edges</h2>
            <ul style={{ margin: 0, paddingLeft: 18, color: "#334155", fontSize: 13 }}>
              {snapshot.edges.map((e) => (
                <li key={e.id} style={{ marginBottom: 8 }}>
                  <strong>{e.edge_type}</strong>
                  <div style={{ wordBreak: "break-word" }}>
                    {e.from_node_id.slice(0, 8)}… → {e.to_node_id.slice(0, 8)}…
                  </div>
                </li>
              ))}
            </ul>
          </aside>
        </section>
      ) : snapshot && snapshot.nodes.length === 0 ? (
        <p style={{ marginTop: 18, color: "#64748b" }}>Graph is empty. Run extract after documents are processed.</p>
      ) : null}
    </main>
  );
}
