export default function KnowledgeBasePage() {
  return (
    <div>
      <h1 className="text-2xl font-bold">Knowledge Base</h1>
      <p className="mt-1 text-[var(--muted-foreground)]">
        Manage documents, FAQs, and rules that power your AI agents
      </p>

      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-6">
          <h2 className="text-lg font-semibold">Documents</h2>
          <p className="mt-2 text-sm text-[var(--muted-foreground)]">
            Upload your trading rules, payout policies, and platform guides.
            The AI will learn from these documents.
          </p>
          <button className="mt-4 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700">
            Upload Document
          </button>
        </div>
        <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-6">
          <h2 className="text-lg font-semibold">FAQs</h2>
          <p className="mt-2 text-sm text-[var(--muted-foreground)]">
            Add frequently asked questions for instant, accurate responses.
          </p>
          <button className="mt-4 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700">
            Add FAQ
          </button>
        </div>
      </div>
    </div>
  );
}
