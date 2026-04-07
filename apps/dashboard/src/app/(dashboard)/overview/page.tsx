"use client";

import {
  MessageSquare,
  Clock,
  CheckCircle,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  ArrowUpRight,
  Bot,
  Users,
  Zap,
  Hash,
  Mail,
  Globe,
} from "lucide-react";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Progress } from "@/components/ui/progress";

// --- Mock Data ---

const conversationVolumeData = [
  { date: "Mar 1", conversations: 320, resolved: 295 },
  { date: "Mar 5", conversations: 410, resolved: 380 },
  { date: "Mar 10", conversations: 385, resolved: 360 },
  { date: "Mar 15", conversations: 520, resolved: 490 },
  { date: "Mar 20", conversations: 480, resolved: 455 },
  { date: "Mar 25", conversations: 590, resolved: 565 },
  { date: "Mar 30", conversations: 610, resolved: 585 },
  { date: "Apr 1", conversations: 550, resolved: 530 },
  { date: "Apr 5", conversations: 640, resolved: 610 },
];

const agentActivityData = [
  { agent: "Payout", handled: 186, avgTime: 45 },
  { agent: "Rules", handled: 142, avgTime: 32 },
  { agent: "Account", handled: 128, avgTime: 55 },
  { agent: "Technical", handled: 95, avgTime: 38 },
  { agent: "Billing", handled: 72, avgTime: 42 },
  { agent: "Onboarding", handled: 64, avgTime: 28 },
  { agent: "Compliance", handled: 18, avgTime: 120 },
];

const channelDistribution = [
  { name: "Discord", value: 45, color: "#5865F2" },
  { name: "Web Chat", value: 35, color: "#6366f1" },
  { name: "Email", value: 20, color: "#8b5cf6" },
];

const recentConversations = [
  { id: "conv-1", trader: "Alex M.", intent: "Payout", channel: "discord", status: "active", time: "2 min ago", agent: "Payout Agent" },
  { id: "conv-2", trader: "Sarah K.", intent: "Account Reset", channel: "webchat", status: "resolved", time: "8 min ago", agent: "Account Agent" },
  { id: "conv-3", trader: "Mike T.", intent: "Rule Violation", channel: "email", status: "escalated", time: "15 min ago", agent: "Rules Agent" },
  { id: "conv-4", trader: "James L.", intent: "KYC Verification", channel: "discord", status: "active", time: "18 min ago", agent: "Account Agent" },
  { id: "conv-5", trader: "Emma R.", intent: "Billing Refund", channel: "webchat", status: "resolved", time: "22 min ago", agent: "Billing Agent" },
];

const channelIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  discord: Hash,
  webchat: Globe,
  email: Mail,
};

const statusColors: Record<string, "success" | "warning" | "default"> = {
  active: "default",
  resolved: "success",
  escalated: "warning",
};

// --- Components ---

function StatCard({
  title,
  value,
  change,
  changeType,
  subtitle,
  icon: Icon,
}: {
  title: string;
  value: string;
  change: string;
  changeType: "up" | "down";
  subtitle: string;
  icon: React.ComponentType<{ className?: string }>;
}) {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-50 dark:bg-brand-950">
            <Icon className="h-5 w-5 text-brand-600" />
          </div>
          <div className={`flex items-center gap-1 text-xs font-medium ${changeType === "up" ? "text-emerald-600" : "text-red-500"}`}>
            {changeType === "up" ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
            {change}
          </div>
        </div>
        <div className="mt-4">
          <p className="text-2xl font-bold tracking-tight">{value}</p>
          <p className="text-xs text-[var(--muted-foreground)]">{subtitle}</p>
        </div>
      </CardContent>
    </Card>
  );
}

export default function OverviewPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Dashboard Overview</h1>
        <p className="text-sm text-[var(--muted-foreground)]">
          Monitor your AI support system performance in real-time
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Active Conversations"
          value="47"
          change="+12%"
          changeType="up"
          subtitle="Across all channels"
          icon={MessageSquare}
        />
        <StatCard
          title="Avg Response Time"
          value="1.2s"
          change="-18%"
          changeType="up"
          subtitle="Last 24 hours"
          icon={Zap}
        />
        <StatCard
          title="Resolution Rate"
          value="94.2%"
          change="+3.1%"
          changeType="up"
          subtitle="Last 7 days"
          icon={CheckCircle}
        />
        <StatCard
          title="Open Escalations"
          value="3"
          change="+1"
          changeType="down"
          subtitle="Awaiting review"
          icon={AlertTriangle}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Conversation Volume Chart */}
        <Card className="lg:col-span-2">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Conversation Volume</CardTitle>
              <Badge variant="secondary">Last 30 days</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-[280px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={conversationVolumeData}>
                  <defs>
                    <linearGradient id="colorConv" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.15} />
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorResolved" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.15} />
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                  <XAxis dataKey="date" tick={{ fontSize: 12 }} stroke="var(--muted-foreground)" />
                  <YAxis tick={{ fontSize: 12 }} stroke="var(--muted-foreground)" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "var(--card)",
                      border: "1px solid var(--border)",
                      borderRadius: "8px",
                      fontSize: "12px",
                    }}
                  />
                  <Area type="monotone" dataKey="conversations" stroke="#6366f1" fill="url(#colorConv)" strokeWidth={2} />
                  <Area type="monotone" dataKey="resolved" stroke="#10b981" fill="url(#colorResolved)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Channel Distribution */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Channel Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex h-[180px] items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={channelDistribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={75}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {channelDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "var(--card)",
                      border: "1px solid var(--border)",
                      borderRadius: "8px",
                      fontSize: "12px",
                    }}
                    formatter={(value) => [`${value}%`, ""]}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-2 space-y-2">
              {channelDistribution.map((ch) => (
                <div key={ch.name} className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <div className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: ch.color }} />
                    <span>{ch.name}</span>
                  </div>
                  <span className="font-medium">{ch.value}%</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Recent Conversations */}
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Recent Conversations</CardTitle>
              <a href="/conversations" className="flex items-center gap-1 text-xs font-medium text-brand-600 hover:text-brand-700">
                View all <ArrowUpRight className="h-3 w-3" />
              </a>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recentConversations.map((conv) => {
                const ChannelIcon = channelIcons[conv.channel] || MessageSquare;
                return (
                  <div key={conv.id} className="flex items-center gap-3 rounded-lg p-2 transition-colors hover:bg-[var(--muted)]/50">
                    <Avatar className="h-8 w-8">
                      <AvatarFallback className="bg-brand-100 text-xs text-brand-700 dark:bg-brand-900 dark:text-brand-300">
                        {conv.trader.split(" ").map(n => n[0]).join("")}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">{conv.trader}</span>
                        <ChannelIcon className="h-3 w-3 text-[var(--muted-foreground)]" />
                      </div>
                      <p className="truncate text-xs text-[var(--muted-foreground)]">{conv.intent} &middot; {conv.agent}</p>
                    </div>
                    <div className="flex flex-col items-end gap-1">
                      <Badge variant={statusColors[conv.status]} className="text-[10px]">
                        {conv.status}
                      </Badge>
                      <span className="text-[10px] text-[var(--muted-foreground)]">{conv.time}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Agent Performance */}
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Agent Performance</CardTitle>
              <Badge variant="secondary">Today</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-[220px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={agentActivityData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" horizontal={false} />
                  <XAxis type="number" tick={{ fontSize: 12 }} stroke="var(--muted-foreground)" />
                  <YAxis dataKey="agent" type="category" tick={{ fontSize: 12 }} stroke="var(--muted-foreground)" width={80} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "var(--card)",
                      border: "1px solid var(--border)",
                      borderRadius: "8px",
                      fontSize: "12px",
                    }}
                  />
                  <Bar dataKey="handled" fill="#6366f1" radius={[0, 4, 4, 0]} barSize={16} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-3 flex items-center justify-between border-t border-[var(--border)] pt-3">
              <div className="flex items-center gap-2 text-sm">
                <Bot className="h-4 w-4 text-[var(--muted-foreground)]" />
                <span className="text-[var(--muted-foreground)]">Total handled today:</span>
                <span className="font-semibold">705</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Users className="h-4 w-4 text-[var(--muted-foreground)]" />
                <span className="text-[var(--muted-foreground)]">Escalated:</span>
                <span className="font-semibold text-amber-600">3</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
