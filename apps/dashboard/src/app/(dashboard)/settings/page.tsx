export default function SettingsPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold">Settings</h1>
      <p className="mt-1 text-[var(--muted-foreground)]">
        Configure your firm profile, branding, and AI agent behavior
      </p>

      <div className="mt-6 space-y-6">
        {/* Firm Profile */}
        <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-6">
          <h2 className="text-lg font-semibold">Firm Profile</h2>
          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="text-sm font-medium">Firm Name</label>
              <input
                type="text"
                className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-sm"
                placeholder="Your Trading Firm"
              />
            </div>
            <div>
              <label className="text-sm font-medium">Support Email</label>
              <input
                type="email"
                className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-sm"
                placeholder="support@yourfirm.com"
              />
            </div>
          </div>
        </div>

        {/* Branding */}
        <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-6">
          <h2 className="text-lg font-semibold">Branding</h2>
          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="text-sm font-medium">Bot Name</label>
              <input
                type="text"
                className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-sm"
                placeholder="Support Bot"
              />
            </div>
            <div>
              <label className="text-sm font-medium">Primary Color</label>
              <input
                type="color"
                defaultValue="#6366f1"
                className="mt-1 h-10 w-full rounded-lg border border-[var(--border)]"
              />
            </div>
          </div>
        </div>

        {/* API Keys */}
        <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-6">
          <h2 className="text-lg font-semibold">API Keys</h2>
          <p className="mt-1 text-sm text-[var(--muted-foreground)]">
            Manage API keys for programmatic access
          </p>
          <button className="mt-4 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700">
            Generate New Key
          </button>
        </div>
      </div>
    </div>
  );
}
