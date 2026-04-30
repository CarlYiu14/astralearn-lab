# Concept graph extraction (course-scoped)

You receive **short excerpts** from course documents (plain text). Propose a **small directed graph** of teaching concepts for this course.

## Output rules

- Return **JSON only** (no markdown fences) matching the caller’s schema: nodes have stable `id` strings; edges reference those ids.
- Prefer **5–20 nodes** unless the excerpts clearly justify more.
- Each node needs a **concise label** (2–6 words) and a **one-sentence description** grounded in the excerpts.
- Edges should represent **prerequisite / builds-on** relationships, not loose associations.
- If excerpts are too thin to justify a graph, return the **minimum valid empty graph** the schema allows.

## Safety

- Do not invent reading assignments, URLs, or policies not present in the excerpts.
- If content looks like private personal data, refuse graph construction and return an empty graph with a short reason in the schema’s designated field (if any).
