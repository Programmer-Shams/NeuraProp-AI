"use client";

import { useState } from "react";
import {
  AlertTriangle,
  Clock,
  CheckCircle2,
  XCircle,
  ArrowUpRight,
  MessageSquare,
  User,
  Bot,
  ChevronDown,
  Timer,
  Shield,
  DollarSign,
  HelpCircle,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

// --- Mock Data ---

interface Escalation {
  id: string;
  conversationId: string;
  trader: { name: string; email: string; initials: string; tier: string };
  reason: string;
  category: string;
  priority: "critical" | "high" | "medium" | "low";
  status: "open" | "in_review" | "resolved" | "dismissed";
  agent: string;
  summary: string;
  context: string[];
  createdAt: string;
  slaDeadline: string;
  slaRemaining: string;
}

const escalations: Escalation[] = [
  {
    id: "esc-1",
    conversationId: "conv-3",
    trader: { name: "Mike Torres", email: "mike@example.com", initials: "MT", tier: "Funded" },
    reason: "Trader disputes rule violation. Confidence below threshold.",
    category: "Rule Dispute",
    priority: "high",
    status: "open",
    agent: "Rules Agent",
    summary: "Trader claims daily loss limit was not breached. Account shows -4.8% but trader argues a pending trade reversal should offset. Rules Agent couldn't verify pending reversals.",
    context: [
      "Account MT5-19283 flagged for daily loss limit violation (-4.8%)",
      "Trader claims a pending swap reversal of +0.5% should be applied",
      "Rules Agent verified: firm's rules don't explicitly address pending reversals",
      "Trader is requesting manual review from compliance team",
    ],
    createdAt: "32 min ago",
    slaDeadline: "2h",
    slaRemaining: "1h 28m",
  },
  {
    id: "esc-2",
    conversationId: "conv-8",
    trader: { name: "Anna Weber", email: "anna@example.com", initials: "AW", tier: "Funded" },
    reason: "High-value payout requires manual approval ($15,000+)",
    category: "Payout Approval",
    priority: "critical",
    status: "open",
    agent: "Payout Agent",
    summary: "Withdrawal of $18,240 from funded account. Exceeds auto-approve threshold of $5,000. All eligibility checks passed. Trader has clean history.",
    context: [
      "Account MT5-44102 — funded $200K challenge, phase complete",
      "Profit: $22,800 — Withdrawable: $18,240 (80% split)",
      "KYC verified, no compliance flags, 3 previous successful payouts",
      "Auto-approve limit is $5,000 — this requires manual sign-off",
    ],
    createdAt: "1 hr ago",
    slaDeadline: "4h",
    slaRemaining: "3h",
  },
  {
    id: "esc-3",
    conversationId: "conv-12",
    trader: { name: "Carlos Reyes", email: "carlos@example.com", initials: "CR", tier: "Evaluation" },
    reason: "Compliance flag — potential prohibited trading pattern detected",
    category: "Compliance",
    priority: "critical",
    status: "in_review",
    agent: "Compliance Agent",
    summary: "Pattern detection flagged possible copy trading across two accounts. Compliance Agent cannot make autonomous decisions — requires human compliance officer review.",
    context: [
      "Accounts MT5-55201 and MT5-55202 show 94% trade correlation over 48h",
      "Both accounts opened within 5 minutes of each other",
      "IP addresses match for both accounts",
      "Firm policy: copy trading between own accounts is prohibited",
    ],
    createdAt: "2 hr ago",
    slaDeadline: "1h",
    slaRemaining: "Overdue",
  },
];

const priorityConfig: Record<string, { color: string; icon: React.ComponentType<{ className?: string }> }> = {
  critical: { color: "danger", icon: Shield },
  high: { color: "warning", icon: AlertTriangle },
  medium: { color: "default", icon: HelpCircle },
  low: { color: "secondary", icon: HelpCircle },
};

const statusConfig: Record<string, { variant: "default" | "success" | "warning" | "secondary" | "danger"; label: string }> = {
  open: { variant: "warning", label: "Open" },
  in_review: { variant: "default", label: "In Review" },
  resolved: { variant: "success", label: "Resolved" },
  dismissed: { variant: "secondary", label: "Dismissed" },
};

export default function EscalationsPage() {
  const [selectedEsc, setSelectedEsc] = useState<string | null>(null);
  const [priorityFilter, setPriorityFilter] = useState("all");

  const filtered = escalations.filter(
    (e) => priorityFilter === "all" || e.priority === priorityFilter
  );

  const selected = escalations.find((e) => e.id === selectedEsc);

  const openCount = escalations.filter((e) => e.status === "open").length;
  const criticalCount = escalations.filter((e) => e.priority === "critical").length;
  const overdueCount = escalations.filter((e) => e.slaRemaining === "Overdue").length;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Escalations</h1>
        <p className="text-sm text-[var(--muted-foreground)]">
          Review and resolve issues that require human attention
        </p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
        <Card>
          <CardContent className="flex items-center gap-3 p-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-50 dark:bg-amber-950">
              <AlertTriangle className="h-5 w-5 text-amber-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{openCount}</p>
              <p className="text-xs text-[var(--muted-foreground)]">Open</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-3 p-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-red-50 dark:bg-red-950">
              <Shield className="h-5 w-5 text-red-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{criticalCount}</p>
              <p className="text-xs text-[var(--muted-foreground)]">Critical</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-3 p-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-red-50 dark:bg-red-950">
              <Timer className="h-5 w-5 text-red-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{overdueCount}</p>
              <p className="text-xs text-[var(--muted-foreground)]">Overdue SLA</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-3 p-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50 dark:bg-emerald-950">
              <CheckCircle2 className="h-5 w-5 text-emerald-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">47</p>
              <p className="text-xs text-[var(--muted-foreground)]">Resolved this week</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filter */}
      <div className="flex items-center gap-3">
        <Select value={priorityFilter} onValueChange={setPriorityFilter}>
          <SelectTrigger className="w-[160px]">
            <SelectValue placeholder="All priorities" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All priorities</SelectItem>
            <SelectItem value="critical">Critical</SelectItem>
            <SelectItem value="high">High</SelectItem>
            <SelectItem value="medium">Medium</SelectItem>
            <SelectItem value="low">Low</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Split View */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-5">
        {/* Escalation List */}
        <div className={`space-y-3 ${selectedEsc ? "lg:col-span-2" : "lg:col-span-5"}`}>
          {filtered.map((esc) => {
            const status = statusConfig[esc.status];
            return (
              <Card
                key={esc.id}
                className={`cursor-pointer transition-all hover:shadow-md ${
                  selectedEsc === esc.id ? "ring-2 ring-brand-500" : ""
                }`}
                onClick={() => setSelectedEsc(esc.id)}
              >
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                      <Avatar className="mt-0.5 h-9 w-9">
                        <AvatarFallback className="bg-brand-100 text-xs text-brand-700 dark:bg-brand-900 dark:text-brand-300">
                          {esc.trader.initials}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-semibold">{esc.trader.name}</span>
                          <Badge variant={esc.priority === "critical" ? "danger" : esc.priority === "high" ? "warning" : "secondary"} className="text-[10px]">
                            {esc.priority}
                          </Badge>
                        </div>
                        <p className="mt-0.5 text-xs font-medium text-[var(--muted-foreground)]">{esc.category}</p>
                        <p className="mt-1 text-xs text-[var(--muted-foreground)] line-clamp-2">{esc.reason}</p>
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-1">
                      <Badge variant={status.variant} className="text-[10px]">{status.label}</Badge>
                      <div className="flex items-center gap-1 text-[10px] text-[var(--muted-foreground)]">
                        <Clock className="h-3 w-3" />
                        {esc.createdAt}
                      </div>
                      <span className={`text-[10px] font-medium ${esc.slaRemaining === "Overdue" ? "text-red-600" : "text-[var(--muted-foreground)]"}`}>
                        SLA: {esc.slaRemaining}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Detail Panel */}
        {selected && (
          <Card className="lg:col-span-3">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <CardTitle>{selected.category}</CardTitle>
                    <Badge variant={selected.priority === "critical" ? "danger" : "warning"}>
                      {selected.priority}
                    </Badge>
                  </div>
                  <CardDescription className="mt-1">
                    Escalated by {selected.agent} &middot; {selected.createdAt}
                  </CardDescription>
                </div>
                <div className={`text-right text-sm font-medium ${selected.slaRemaining === "Overdue" ? "text-red-600" : ""}`}>
                  <div className="flex items-center gap-1">
                    <Timer className="h-4 w-4" />
                    SLA: {selected.slaRemaining}
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-5">
              {/* Trader Info */}
              <div className="flex items-center gap-3 rounded-lg bg-[var(--muted)]/50 p-3">
                <Avatar>
                  <AvatarFallback className="bg-brand-100 text-brand-700 dark:bg-brand-900 dark:text-brand-300">
                    {selected.trader.initials}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <p className="text-sm font-medium">{selected.trader.name}</p>
                  <p className="text-xs text-[var(--muted-foreground)]">{selected.trader.email} &middot; {selected.trader.tier}</p>
                </div>
                <Button variant="ghost" size="sm" className="ml-auto">
                  <ArrowUpRight className="mr-1 h-3.5 w-3.5" />
                  View Profile
                </Button>
              </div>

              {/* Summary */}
              <div>
                <h4 className="text-sm font-semibold">AI Summary</h4>
                <p className="mt-1.5 text-sm text-[var(--muted-foreground)] leading-relaxed">{selected.summary}</p>
              </div>

              <Separator />

              {/* Context */}
              <div>
                <h4 className="text-sm font-semibold">Context & Evidence</h4>
                <ul className="mt-2 space-y-2">
                  {selected.context.map((item, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-[var(--muted-foreground)]">
                      <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-brand-500" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>

              <Separator />

              {/* Resolution */}
              <div>
                <h4 className="text-sm font-semibold">Resolution</h4>
                <Textarea placeholder="Add your resolution notes..." className="mt-2" rows={3} />
                <div className="mt-3 flex items-center gap-2">
                  <Button>
                    <CheckCircle2 className="mr-1.5 h-4 w-4" />
                    Resolve
                  </Button>
                  <Button variant="outline">
                    <MessageSquare className="mr-1.5 h-4 w-4" />
                    Reply to Trader
                  </Button>
                  <Button variant="ghost" className="text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950">
                    <XCircle className="mr-1.5 h-4 w-4" />
                    Dismiss
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
