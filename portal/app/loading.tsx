export default function Loading() {
  return (
    <main className="loading-shell" aria-busy="true" aria-label="Loading the AI-Human Workspace portal">
      <div className="loading-line loading-line-short" />
      <div className="loading-line loading-line-title" />
      <div className="loading-line loading-line-copy" />
      <div className="loading-block" />
    </main>
  );
}
