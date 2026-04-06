const integrations = [
  {
    name: "MetaTrader 5",
    description: "Connect your MT5 Manager API for account and trade management",
    status: "available",
    category: "Trading Platform",
  },
  {
    name: "cTrader",
    description: "Connect via cTrader Open API for account data and operations",
    status: "available",
    category: "Trading Platform",
  },
  {
    name: "Wise",
    description: "Process international payouts through Wise transfer API",
    status: "available",
    category: "Payment",
  },
  {
    name: "Veriff",
    description: "Automated KYC identity verification for traders",
    status: "available",
    category: "KYC",
  },
  {
    name: "Discord",
    description: "White-label Discord bot for your server",
    status: "available",
    category: "Channel",
  },
  {
    name: "Custom API",
    description: "Connect any system through our universal API layer",
    status: "available",
    category: "Universal",
  },
];

export default function IntegrationsPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold">Integrations</h1>
      <p className="mt-1 text-[var(--muted-foreground)]">
        Connect your trading platforms, payment systems, and communication channels
      </p>

      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {integrations.map((integration) => (
          <div
            key={integration.name}
            className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-5"
          >
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-semibold">{integration.name}</h3>
                <span className="text-xs text-[var(--muted-foreground)]">
                  {integration.category}
                </span>
              </div>
              <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900 dark:text-green-300">
                Available
              </span>
            </div>
            <p className="mt-2 text-sm text-[var(--muted-foreground)]">
              {integration.description}
            </p>
            <button className="mt-4 rounded-lg border border-[var(--border)] px-3 py-1.5 text-sm font-medium hover:bg-[var(--muted)]">
              Connect
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
