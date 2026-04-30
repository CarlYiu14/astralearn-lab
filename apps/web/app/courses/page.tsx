import Link from "next/link";

export default function CoursesPage() {
  return (
    <main style={{ fontFamily: "Inter, sans-serif", padding: "2rem", maxWidth: 820 }}>
      <h1>Courses</h1>
      <p style={{ color: "#444" }}>
        Day 8: course APIs require a Bearer token. Use <Link href="/courses/demo/auth">/courses/demo/auth</Link> in the
        browser, then call <code>GET /courses</code> (lists your enrollments) or open any course demo with{" "}
        <code>NEXT_PUBLIC_COURSE_ID</code> set to a course you belong to.
      </p>
      <p>
        <Link href="/courses/demo/auth">Go to auth demo</Link>
      </p>
    </main>
  );
}
