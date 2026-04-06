import {
  MessageSquare,
  Clock,
  CheckCircle,
  AlertTriangle,
} from "lucide-react";

function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
}: {
  title: string;
  value: string;
  subtitle: string;
  icon: React.ComponentType<{ className?: string }>;
}) {
  return (
    <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-[var(--muted-foreground)]">{title}</p>
          <p className="mt-1 text-3xl font-bold">{value}</p>
          <p className="mt-1 text-sm text-[var(--muted-foreground)]">{subtitle}</p>
        </div>
        <Icon className="h-8 w-8 text-brand-500 opacity-80" />
      </div>
    </div>
  );
}

export default function OverviewPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold">Dashboard Overview</h1>
      <p className="mt-1 text-[var(--muted-foreground)]">
        Monitor your AI support system performance
      </p>

      {/* Stats Grid */}
      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Active Conversations"
          value="--"
          subtitle="Across all channels"
          icon={MessageSquare}
        />
        <StatCard
          title="Avg Response Time"
          value="--"
          subtitle="Last 24 hours"
          icon={Clock}
        />
        <StatCard
          title="Resolution Rate"
          value="--"
          subtitle="Last 7 days"
          icon={CheckCircle}
        />
        <StatCard
          title="Open Escalations"
          value="--"
          subtitle="Awaiting review"
          icon={AlertTriangle}
        />
      </div>

      {/* Placeholder sections */}
      <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-6">
          <h2 className="text-lg font-semibold">Recent Conversations</h2>
          <p className="mt-4 text-sm text-[var(--muted-foreground)]">
            No conversations yet. Connect your first channel to get started.
          </p>
        </div>
        <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-6">
          <h2 className="text-lg font-semibold">Agent Activity</h2>
          <p className="mt-4 text-sm text-[var(--muted-foreground)]">
            Agent performance metrics will appear here once conversations begin.
          </p>
        </div>
      </div>
    </div>
  );
}
