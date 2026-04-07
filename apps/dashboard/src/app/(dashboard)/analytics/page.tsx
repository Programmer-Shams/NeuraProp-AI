"use client";

import {
  MessageSquare,
  Clock,
  DollarSign,
  TrendingUp,
  TrendingDown,
  Zap,
  Bot,
  Users,
  ArrowUpRight,
  ArrowDownRight,
} from "lucide-react";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";

// --- Mock Data ---

const volumeData = [
  { date: "Mar 1", total: 320, discord: 145, webchat: 112, email: 63 },
  { date: "Mar 4", total: 380, discord: 168, webchat: 135, email: 77 },
  { date: "Mar 7", total: 410, discord: 190, webchat: 140, email: 80 },
  { date: "Mar 10", total: 385, discord: 175, webchat: 130, email: 80 },
  { date: "Mar 13", total: 450, discord: 200, webchat: 160, email: 90 },
  { date: "Mar 16", total: 520, discord: 235, webchat: 182, email: 103 },
  { date: "Mar 19", total: 480, discord: 215, webchat: 170, email: 95 },
  { date: "Mar 22", total: 555, discord: 250, webchat: 195, email: 110 },
  { date: "Mar 25", total: 590, discord: 265, webchat: 205, email: 120 },
  { date: "Mar 28", total: 610, discord: 275, webchat: 215, email: 120 },
  { date: "Mar 31", total: 575, discord: 260, webchat: 200, email: 115 },
  { date: "Apr 3", total: 640, discord: 290, webchat: 225, email: 125 },
  { date: "Apr 6", total: 680, discord: 305, webchat: 240, email: 135 },
];

const responseTimeData = [
  { hour: "00:00", avg: 1.8, p95: 4.2 },
  { hour: "02:00", avg: 1.5, p95: 3.8 },
  { hour: "04:00", avg: 1.3, p95: 3.2 },
  { hour: "06:00", avg: 1.4, p95: 3.5 },
  { hour: "08:00", avg: 2.1, p95: 5.1 },
  { hour: "10:00", avg: 2.4, p95: 5.8 },
  { hour: "12:00", avg: 2.6, p95: 6.2 },
  { hour: "14:00", avg: 2.3, p95: 5.5 },
  { hour: "16:00", avg: 2.0, p95: 4.8 },
  { hour: "18:00", avg: 1.9, p95: 4.5 },
  { hour: "20:00", avg: 1.7, p95: 4.0 },
  { hour: "22:00", avg: 1.6, p95: 3.9 },
];

const intentDistribution = [
  { name: "Payout", value: 28, color: "#6366f1" },
  { name: "Rules", value: 22, color: "#8b5cf6" },
  { name: "Account/KYC", value: 18, color: "#a78bfa" },
  { name: "Technical", value: 14, color: "#c4b5fd" },
  { name: "Billing", value: 10, color: "#10b981" },
  { name: "Onboarding", value: 6, color: "#34d399" },
  { name: "Compliance", value: 2, color: "#f59e0b" },
];

const costData = [
  { date: "Mar 1", tokens: 1250000, cost: 18.75 },
  { date: "Mar 5", tokens: 1480000, cost: 22.20 },
  { date: "Mar 10", tokens: 1320000, cost: 19.80 },
  { date: "Mar 15", tokens: 1650000, cost: 24.75 },
  { date: "Mar 20", tokens: 1520000, cost: 22.80 },
  { date: "Mar 25", tokens: 1780000, cost: 26.70 },
  { date: "Mar 30", tokens: 1890000, cost: 28.35 },
  { date: "Apr 3", tokens: 1950000, cost: 29.25 },
  { date: "Apr 6", tokens: 2100000, cost: 31.50 },
];

const agentPerformance = [
  { agent: "Payout", resolved: 94, avgTime: 45, satisfaction: 4.6, conversations: 186 },
  { agent: "Rules", resolved: 91, avgTime: 32, satisfaction: 4.3, conversations: 142 },
  { agent: "Account/KYC", resolved: 88, avgTime: 55, satisfaction: 4.4, conversations: 128 },
  { agent: "Technical", resolved: 85, avgTime: 38, satisfaction: 4.1, conversations: 95 },
  { agent: "Billing", resolved: 96, avgTime: 42, satisfaction: 4.7, conversations: 72 },
  { agent: "Onboarding", resolved: 98, avgTime: 28, satisfaction: 4.8, conversations: 64 },
  { agent: "Compliance", resolved: 72, avgTime: 120, satisfaction: 3.9, conversations: 18 },
];

const satisfactionData = [
  { date: "Week 1", score: 4.2 },
  { date: "Week 2", score: 4.3 },
  { date: "Week 3", score: 4.4 },
  { date: "Week 4", score: 4.5 },
  { date: "Week 5", score: 4.3 },
  { date: "Week 6", score: 4.6 },
];

function MetricCard({
  title,
  value,
  change,
  changeType,
  icon: Icon,
}: {
  title: string;
  value: string;
  change: string;
  changeType: "up" | "down";
  icon: React.ComponentType<{ className?: string }>;
}) {
  return (
    <Card>
      <CardContent className="p-5">
        <div className="flex items-center justify-between">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-50 dark:bg-brand-950">
            <Icon className="h-4 w-4 text-brand-600" />
          </div>
          <div className={`flex items-center gap-1 text-xs font-medium ${changeType === "up" ? "text-emerald-600" : "text-red-500"}`}>
            {changeType === "up" ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
            {change}
          </div>
        </div>
        <p className="mt-3 text-2xl font-bold tracking-tight">{value}</p>
        <p className="text-xs text-[var(--muted-foreground)]">{title}</p>
      </CardContent>
    </Card>
  );
}

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Analytics</h1>
          <p className="text-sm text-[var(--muted-foreground)]">
            Track performance, costs, and insights across your AI support system
          </p>
        </div>
        <Select defaultValue="30d">
          <SelectTrigger className="w-[140px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="7d">Last 7 days</SelectItem>
            <SelectItem value="30d">Last 30 days</SelectItem>
            <SelectItem value="90d">Last 90 days</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Top Metrics */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <MetricCard title="Total Conversations" value="6,842" change="+18.2%" changeType="up" icon={MessageSquare} />
        <MetricCard title="Avg Response Time" value="1.2s" change="-24%" changeType="up" icon={Zap} />
        <MetricCard title="Resolution Rate" value="94.2%" change="+3.1%" changeType="up" icon={TrendingUp} />
        <MetricCard title="CSAT Score" value="4.5/5" change="+0.3" changeType="up" icon={Users} />
        <MetricCard title="Total LLM Cost" value="$243.30" change="+12%" changeType="down" icon={DollarSign} />
      </div>

      {/* Tabs for different analytics views */}
      <Tabs defaultValue="volume" className="space-y-4">
        <TabsList>
          <TabsTrigger value="volume">Volume</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="costs">Costs</TabsTrigger>
          <TabsTrigger value="satisfaction">Satisfaction</TabsTrigger>
        </TabsList>

        {/* Volume Tab */}
        <TabsContent value="volume" className="space-y-6">
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <Card className="lg:col-span-2">
              <CardHeader className="pb-2">
                <CardTitle className="text-base">Conversation Volume by Channel</CardTitle>
                <CardDescription>Daily conversation count broken down by channel</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[320px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={volumeData}>
                      <defs>
                        <linearGradient id="colorDiscord" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#5865F2" stopOpacity={0.15} />
                          <stop offset="95%" stopColor="#5865F2" stopOpacity={0} />
                        </linearGradient>
                        <linearGradient id="colorWebchat" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#6366f1" stopOpacity={0.15} />
                          <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                        </linearGradient>
                        <linearGradient id="colorEmail" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.15} />
                          <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                      <XAxis dataKey="date" tick={{ fontSize: 11 }} stroke="var(--muted-foreground)" />
                      <YAxis tick={{ fontSize: 11 }} stroke="var(--muted-foreground)" />
                      <Tooltip contentStyle={{ backgroundColor: "var(--card)", border: "1px solid var(--border)", borderRadius: "8px", fontSize: "12px" }} />
                      <Legend wrapperStyle={{ fontSize: "12px" }} />
                      <Area type="monotone" dataKey="discord" stackId="1" stroke="#5865F2" fill="url(#colorDiscord)" strokeWidth={2} />
                      <Area type="monotone" dataKey="webchat" stackId="1" stroke="#6366f1" fill="url(#colorWebchat)" strokeWidth={2} />
                      <Area type="monotone" dataKey="email" stackId="1" stroke="#8b5cf6" fill="url(#colorEmail)" strokeWidth={2} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">Intent Distribution</CardTitle>
                <CardDescription>Breakdown by issue type</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[180px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={intentDistribution} cx="50%" cy="50%" innerRadius={45} outerRadius={70} paddingAngle={3} dataKey="value">
                        {intentDistribution.map((entry, i) => (
                          <Cell key={i} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip contentStyle={{ backgroundColor: "var(--card)", border: "1px solid var(--border)", borderRadius: "8px", fontSize: "12px" }} formatter={(v) => [`${v}%`, ""]} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="mt-2 space-y-1.5">
                  {intentDistribution.map((item) => (
                    <div key={item.name} className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <div className="h-2 w-2 rounded-full" style={{ backgroundColor: item.color }} />
                        <span>{item.name}</span>
                      </div>
                      <span className="font-medium">{item.value}%</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Performance Tab */}
        <TabsContent value="performance" className="space-y-6">
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">Response Time Distribution</CardTitle>
                <CardDescription>Average and P95 response times by hour</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={responseTimeData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                      <XAxis dataKey="hour" tick={{ fontSize: 11 }} stroke="var(--muted-foreground)" />
                      <YAxis tick={{ fontSize: 11 }} stroke="var(--muted-foreground)" unit="s" />
                      <Tooltip contentStyle={{ backgroundColor: "var(--card)", border: "1px solid var(--border)", borderRadius: "8px", fontSize: "12px" }} />
                      <Legend wrapperStyle={{ fontSize: "12px" }} />
                      <Line type="monotone" dataKey="avg" stroke="#6366f1" strokeWidth={2} dot={{ r: 3 }} name="Average" />
                      <Line type="monotone" dataKey="p95" stroke="#f59e0b" strokeWidth={2} dot={{ r: 3 }} strokeDasharray="5 5" name="P95" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">Agent Performance</CardTitle>
                <CardDescription>Resolution rate, avg time, and satisfaction by agent</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {agentPerformance.map((agent) => (
                    <div key={agent.agent} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Bot className="h-4 w-4 text-brand-500" />
                          <span className="text-sm font-medium">{agent.agent}</span>
                        </div>
                        <div className="flex items-center gap-3 text-xs text-[var(--muted-foreground)]">
                          <span>{agent.conversations} convs</span>
                          <span>{agent.avgTime}s avg</span>
                          <span>{agent.satisfaction}/5</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <Progress value={agent.resolved} className="flex-1" />
                        <span className="text-xs font-semibold w-10 text-right">{agent.resolved}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Costs Tab */}
        <TabsContent value="costs" className="space-y-6">
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <Card className="lg:col-span-2">
              <CardHeader className="pb-2">
                <CardTitle className="text-base">LLM Cost Over Time</CardTitle>
                <CardDescription>Daily token usage and associated costs</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[320px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={costData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                      <XAxis dataKey="date" tick={{ fontSize: 11 }} stroke="var(--muted-foreground)" />
                      <YAxis yAxisId="cost" tick={{ fontSize: 11 }} stroke="var(--muted-foreground)" unit="$" />
                      <YAxis yAxisId="tokens" orientation="right" tick={{ fontSize: 11 }} stroke="var(--muted-foreground)" tickFormatter={(v) => `${(v / 1000000).toFixed(1)}M`} />
                      <Tooltip contentStyle={{ backgroundColor: "var(--card)", border: "1px solid var(--border)", borderRadius: "8px", fontSize: "12px" }} />
                      <Legend wrapperStyle={{ fontSize: "12px" }} />
                      <Bar yAxisId="cost" dataKey="cost" fill="#6366f1" radius={[4, 4, 0, 0]} barSize={20} name="Cost ($)" />
                      <Line yAxisId="tokens" type="monotone" dataKey="tokens" stroke="#f59e0b" strokeWidth={2} dot={{ r: 3 }} name="Tokens" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">Cost Breakdown</CardTitle>
                <CardDescription>Per-model cost allocation</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Claude Haiku (Router)</span>
                    <span className="text-sm font-semibold">$28.40</span>
                  </div>
                  <Progress value={12} />
                </div>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Claude Sonnet (Agents)</span>
                    <span className="text-sm font-semibold">$168.50</span>
                  </div>
                  <Progress value={69} />
                </div>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Embeddings</span>
                    <span className="text-sm font-semibold">$12.80</span>
                  </div>
                  <Progress value={5} />
                </div>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">GPT-4o (Fallback)</span>
                    <span className="text-sm font-semibold">$33.60</span>
                  </div>
                  <Progress value={14} />
                </div>
                <div className="mt-4 border-t border-[var(--border)] pt-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Total (30 days)</span>
                    <span className="text-lg font-bold">$243.30</span>
                  </div>
                  <p className="mt-1 text-xs text-[var(--muted-foreground)]">
                    $0.036 avg cost per conversation
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Satisfaction Tab */}
        <TabsContent value="satisfaction" className="space-y-6">
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">CSAT Trend</CardTitle>
                <CardDescription>Weekly customer satisfaction scores</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={satisfactionData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                      <XAxis dataKey="date" tick={{ fontSize: 11 }} stroke="var(--muted-foreground)" />
                      <YAxis domain={[3.5, 5]} tick={{ fontSize: 11 }} stroke="var(--muted-foreground)" />
                      <Tooltip contentStyle={{ backgroundColor: "var(--card)", border: "1px solid var(--border)", borderRadius: "8px", fontSize: "12px" }} />
                      <Line type="monotone" dataKey="score" stroke="#10b981" strokeWidth={2.5} dot={{ r: 4, fill: "#10b981" }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">Rating Distribution</CardTitle>
                <CardDescription>Breakdown of customer feedback ratings</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {[
                  { stars: 5, count: 412, pct: 62 },
                  { stars: 4, count: 156, pct: 23 },
                  { stars: 3, count: 58, pct: 9 },
                  { stars: 2, count: 25, pct: 4 },
                  { stars: 1, count: 14, pct: 2 },
                ].map((r) => (
                  <div key={r.stars} className="flex items-center gap-3">
                    <span className="w-12 text-sm font-medium">{r.stars} star</span>
                    <div className="flex-1">
                      <div className="h-3 w-full overflow-hidden rounded-full bg-[var(--muted)]">
                        <div
                          className={`h-full rounded-full ${r.stars >= 4 ? "bg-emerald-500" : r.stars === 3 ? "bg-amber-500" : "bg-red-500"}`}
                          style={{ width: `${r.pct}%` }}
                        />
                      </div>
                    </div>
                    <span className="w-16 text-right text-xs text-[var(--muted-foreground)]">{r.count} ({r.pct}%)</span>
                  </div>
                ))}
                <div className="mt-4 rounded-lg bg-[var(--muted)]/50 p-4 text-center">
                  <p className="text-3xl font-bold text-emerald-600">4.5</p>
                  <p className="text-xs text-[var(--muted-foreground)]">Average from 665 ratings</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
