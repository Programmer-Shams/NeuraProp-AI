export default function ConversationsPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold">Conversations</h1>
      <p className="mt-1 text-[var(--muted-foreground)]">
        View and manage all support conversations across channels
      </p>

      <div className="mt-6 rounded-xl border border-[var(--border)] bg-[var(--card)] p-8 text-center">
        <p className="text-[var(--muted-foreground)]">
          No conversations yet. Conversations will appear here once traders start
          reaching out through your connected channels.
        </p>
      </div>
    </div>
  );
}
