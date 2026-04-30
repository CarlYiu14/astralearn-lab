import Link from "next/link";

export default function HomePage() {
  return (
    <main style={{ fontFamily: "Inter, sans-serif", padding: "2rem" }}>
      <h1>AstraLearn OS</h1>
      <p>Core scaffold is ready. Day 8 secures course APIs with JWT; sign in before using demos.</p>
      <p>
        Open <Link href="/courses">Courses</Link> to view the first UI flow, or{" "}
        <Link href="/dashboard">Dashboard</Link> for an authenticated course list + eval hints.
      </p>
      <p>
        Hobby playground: <Link href="/lab">Lab</Link>
      </p>
      <p>
        Day 8 auth: <Link href="/courses/demo/auth">Sign in (demo)</Link>
      </p>
      <p>
        Day 3 upload flow: <Link href="/courses/demo/documents">Documents (demo)</Link>
      </p>
      <p>
        Day 4 QA flow: <Link href="/courses/demo/qa">Course QA (demo)</Link>
      </p>
      <p>
        Day 5 graph flow: <Link href="/courses/demo/graph">Concept graph (demo)</Link>
      </p>
      <p>
        Day 6 lessons: <Link href="/courses/demo/lessons">Lesson compiler (demo)</Link>
      </p>
      <p>
        Day 6 assessment: <Link href="/courses/demo/assessment">Assessment (demo)</Link>
      </p>
    </main>
  );
}
