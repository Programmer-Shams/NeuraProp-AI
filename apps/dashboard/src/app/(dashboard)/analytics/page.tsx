export default function AnalyticsPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold">Analytics</h1>
      <p className="mt-1 text-[var(--muted-foreground)]">
        Track performance, costs, and insights across your AI support system
      </p>

      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-6">
          <h2 className="text-lg font-semibold">Conversation Volume</h2>
          <p className="mt-4 text-sm text-[var(--muted-foreground)]">
            Charts will render here once data is available.
          </p>
        </div>
        <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-6">
          <h2 className="text-lg font-semibold">Cost Analysis</h2>
          <p className="mt-4 text-sm text-[var(--muted-foreground)]">
            LLM token usage and cost per conversation breakdown.
          </p>
        </div>
        <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-6">
          <h2 className="text-lg font-semibold">Intent Distribution</h2>
          <p className="mt-4 text-sm text-[var(--muted-foreground)]">
            See which types of issues traders contact support about most.
          </p>
        </div>
        <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-6">
          <h2 className="text-lg font-semibold">Agent Performance</h2>
          <p className="mt-4 text-sm text-[var(--muted-foreground)]">
            Resolution rates, response times, and satisfaction per agent.
          </p>
        </div>
      </div>
    </div>
  );
}
