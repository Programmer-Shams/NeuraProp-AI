export default function EscalationsPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold">Escalations</h1>
      <p className="mt-1 text-[var(--muted-foreground)]">
        Review and resolve issues that require human attention
      </p>

      <div className="mt-6 rounded-xl border border-[var(--border)] bg-[var(--card)] p-8 text-center">
        <p className="text-[var(--muted-foreground)]">
          No open escalations. When AI agents cannot resolve an issue, it will
          appear here with full context for your team to review.
        </p>
      </div>
    </div>
  );
}
