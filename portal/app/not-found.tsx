import Link from "next/link";

export default function NotFound() {
  return (
    <main className="message-page">
      <p className="eyebrow">AI-Human Workspace</p>
      <h1>This page is not in the approved portal.</h1>
      <p>Return to the start page and use the current company resources.</p>
      <Link className="button button-primary" href="/">Return to start</Link>
    </main>
  );
}
