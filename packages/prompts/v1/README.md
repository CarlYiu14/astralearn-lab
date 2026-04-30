# Prompt bundle `v1`

Version **v1** is the first stable naming slice. Bump to **v2** when you make **breaking** instruction changes (new required JSON keys, different safety rules), not for small wording tweaks.

Files are plain **Markdown** so humans and tools can read them; the API can load them by path or embed hashes in audit metadata later.

| File | Used for (conceptually) |
|------|-------------------------|
| `course_qa_rag.md` | Retrieval QA system + user message skeleton. |
| `lesson_compile_outline.md` | Lesson compiler high-level instructions. |
| `graph_concept_extract.md` | Concept graph extraction from sampled chunks (JSON graph). |
