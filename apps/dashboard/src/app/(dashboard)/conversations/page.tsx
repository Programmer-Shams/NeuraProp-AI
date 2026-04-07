"use client";

import { useState } from "react";
import {
  Search,
  Filter,
  MessageSquare,
  Hash,
  Mail,
  Globe,
  Clock,
  Bot,
  User,
  ArrowLeft,
  Send,
  MoreVertical,
  HandMetal,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";

// --- Mock Data ---

interface Conversation {
  id: string;
  trader: { name: string; email: string; initials: string };
  channel: "discord" | "webchat" | "email";
  intent: string;
  agent: string;
  status: "active" | "resolved" | "escalated" | "waiting";
  lastMessage: string;
  startedAt: string;
  messageCount: number;
  satisfaction?: number;
}

interface Message {
  id: string;
  role: "user" | "agent" | "system";
  content: string;
  agentName?: string;
  time: string;
  toolCalls?: string[];
}

const conversations: Conversation[] = [
  {
    id: "conv-1",
    trader: { name: "Alex Mitchell", email: "alex@example.com", initials: "AM" },
    channel: "discord",
    intent: "Payout Request",
    agent: "Payout Agent",
    status: "active",
    lastMessage: "I'd like to request a withdrawal from my funded account...",
    startedAt: "2 min ago",
    messageCount: 4,
  },
  {
    id: "conv-2",
    trader: { name: "Sarah Kim", email: "sarah@example.com", initials: "SK" },
    channel: "webchat",
    intent: "Account Reset",
    agent: "Account Agent",
    status: "resolved",
    lastMessage: "Your account has been successfully reset. You can now...",
    startedAt: "15 min ago",
    messageCount: 8,
    satisfaction: 5,
  },
  {
    id: "conv-3",
    trader: { name: "Mike Torres", email: "mike@example.com", initials: "MT" },
    channel: "email",
    intent: "Rule Clarification",
    agent: "Rules Agent",
    status: "escalated",
    lastMessage: "I believe my account was unfairly flagged for...",
    startedAt: "32 min ago",
    messageCount: 6,
  },
  {
    id: "conv-4",
    trader: { name: "James Liu", email: "james@example.com", initials: "JL" },
    channel: "discord",
    intent: "KYC Verification",
    agent: "Account Agent",
    status: "waiting",
    lastMessage: "I've uploaded my passport. How long until verification...",
    startedAt: "1 hr ago",
    messageCount: 3,
  },
  {
    id: "conv-5",
    trader: { name: "Emma Rodriguez", email: "emma@example.com", initials: "ER" },
    channel: "webchat",
    intent: "Billing Issue",
    agent: "Billing Agent",
    status: "resolved",
    lastMessage: "Your refund of $99 has been processed and should...",
    startedAt: "2 hr ago",
    messageCount: 12,
    satisfaction: 4,
  },
  {
    id: "conv-6",
    trader: { name: "David Park", email: "david@example.com", initials: "DP" },
    channel: "discord",
    intent: "Platform Error",
    agent: "Technical Agent",
    status: "active",
    lastMessage: "I keep getting a 'connection timeout' when trying to...",
    startedAt: "2 hr ago",
    messageCount: 5,
  },
  {
    id: "conv-7",
    trader: { name: "Lisa Chen", email: "lisa@example.com", initials: "LC" },
    channel: "email",
    intent: "New Challenge",
    agent: "Onboarding Agent",
    status: "resolved",
    lastMessage: "Your 100K Challenge account has been created. Here are...",
    startedAt: "3 hr ago",
    messageCount: 7,
    satisfaction: 5,
  },
];

const conversationMessages: Message[] = [
  { id: "msg-1", role: "user", content: "Hi, I'd like to request a withdrawal from my funded account. My account number is MT5-28491.", time: "2:45 PM" },
  { id: "msg-2", role: "agent", agentName: "Payout Agent", content: "Hello Alex! I'll help you with your withdrawal request. Let me check your account eligibility first.", time: "2:45 PM", toolCalls: ["check_payout_eligibility"] },
  { id: "msg-3", role: "agent", agentName: "Payout Agent", content: "Great news! Your account MT5-28491 is eligible for withdrawal. You have a current profit of $2,340.00 with a withdrawable amount of $1,872.00 (80% profit split).\n\nWould you like to proceed with the full withdrawable amount, or a specific amount?", time: "2:45 PM" },
  { id: "msg-4", role: "user", content: "I'd like to withdraw the full $1,872. Can you send it to my Wise account on file?", time: "2:46 PM" },
];

const channelIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  discord: Hash,
  webchat: Globe,
  email: Mail,
};

const statusConfig: Record<string, { variant: "default" | "success" | "warning" | "secondary"; label: string }> = {
  active: { variant: "default", label: "Active" },
  resolved: { variant: "success", label: "Resolved" },
  escalated: { variant: "warning", label: "Escalated" },
  waiting: { variant: "secondary", label: "Waiting" },
};

export default function ConversationsPage() {
  const [selectedConv, setSelectedConv] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  const filtered = conversations.filter((c) => {
    const matchesSearch =
      !searchQuery ||
      c.trader.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.intent.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === "all" || c.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const selected = conversations.find((c) => c.id === selectedConv);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Conversations</h1>
        <p className="text-sm text-[var(--muted-foreground)]">
          View and manage all support conversations across channels
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--muted-foreground)]" />
          <Input
            placeholder="Search by trader name or intent..."
            className="pl-9"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[160px]">
            <Filter className="mr-2 h-4 w-4" />
            <SelectValue placeholder="All statuses" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All statuses</SelectItem>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="waiting">Waiting</SelectItem>
            <SelectItem value="escalated">Escalated</SelectItem>
            <SelectItem value="resolved">Resolved</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Split View: List + Detail */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-5">
        {/* Conversation List */}
        <Card className={selectedConv ? "lg:col-span-2" : "lg:col-span-5"}>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">{filtered.length} conversations</CardTitle>
              <Badge variant="secondary">{conversations.filter((c) => c.status === "active").length} active</Badge>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y divide-[var(--border)]">
              {filtered.map((conv) => {
                const ChannelIcon = channelIcons[conv.channel] || MessageSquare;
                const status = statusConfig[conv.status];
                return (
                  <button
                    key={conv.id}
                    onClick={() => setSelectedConv(conv.id)}
                    className={`w-full px-6 py-4 text-left transition-colors hover:bg-[var(--muted)]/50 ${
                      selectedConv === conv.id ? "bg-[var(--muted)]/70" : ""
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <Avatar className="mt-0.5 h-9 w-9">
                        <AvatarFallback className="bg-brand-100 text-xs text-brand-700 dark:bg-brand-900 dark:text-brand-300">
                          {conv.trader.initials}
                        </AvatarFallback>
                      </Avatar>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-medium">{conv.trader.name}</span>
                            <ChannelIcon className="h-3.5 w-3.5 text-[var(--muted-foreground)]" />
                          </div>
                          <span className="text-[10px] text-[var(--muted-foreground)]">{conv.startedAt}</span>
                        </div>
                        <div className="mt-0.5 flex items-center gap-2">
                          <span className="text-xs font-medium text-[var(--muted-foreground)]">{conv.intent}</span>
                          <Badge variant={status.variant} className="text-[10px] py-0">{status.label}</Badge>
                        </div>
                        <p className="mt-1 truncate text-xs text-[var(--muted-foreground)]">{conv.lastMessage}</p>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Conversation Detail */}
        {selected && (
          <Card className="lg:col-span-3 flex flex-col">
            {/* Detail Header */}
            <CardHeader className="border-b border-[var(--border)] pb-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Button variant="ghost" size="icon" className="lg:hidden" onClick={() => setSelectedConv(null)}>
                    <ArrowLeft className="h-4 w-4" />
                  </Button>
                  <Avatar className="h-10 w-10">
                    <AvatarFallback className="bg-brand-100 text-sm text-brand-700 dark:bg-brand-900 dark:text-brand-300">
                      {selected.trader.initials}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold">{selected.trader.name}</h3>
                      <Badge variant={statusConfig[selected.status].variant} className="text-[10px]">
                        {statusConfig[selected.status].label}
                      </Badge>
                    </div>
                    <p className="text-xs text-[var(--muted-foreground)]">
                      {selected.trader.email} &middot; {selected.intent} &middot; {selected.messageCount} messages
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm">
                    <HandMetal className="mr-1.5 h-3.5 w-3.5" />
                    Take Over
                  </Button>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon">
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem>Assign to agent</DropdownMenuItem>
                      <DropdownMenuItem>View trader profile</DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem>Export conversation</DropdownMenuItem>
                      <DropdownMenuItem className="text-red-600">Close conversation</DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </div>
            </CardHeader>

            {/* Messages */}
            <CardContent className="flex-1 overflow-y-auto p-6">
              <div className="space-y-4">
                {conversationMessages.map((msg) => (
                  <div key={msg.id} className={`flex gap-3 ${msg.role === "user" ? "" : ""}`}>
                    <Avatar className="mt-0.5 h-7 w-7 shrink-0">
                      <AvatarFallback className={`text-[10px] ${msg.role === "agent" ? "bg-brand-100 text-brand-700 dark:bg-brand-900 dark:text-brand-300" : "bg-[var(--muted)]"}`}>
                        {msg.role === "agent" ? <Bot className="h-3.5 w-3.5" /> : <User className="h-3.5 w-3.5" />}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-medium">
                          {msg.role === "agent" ? msg.agentName : selected.trader.name}
                        </span>
                        <span className="text-[10px] text-[var(--muted-foreground)]">{msg.time}</span>
                      </div>
                      {msg.toolCalls && (
                        <div className="mt-1 mb-1.5 flex gap-1.5">
                          {msg.toolCalls.map((tool) => (
                            <Badge key={tool} variant="outline" className="text-[10px] font-mono">{tool}</Badge>
                          ))}
                        </div>
                      )}
                      <div className={`mt-1 rounded-lg px-3 py-2 text-sm ${
                        msg.role === "agent"
                          ? "bg-brand-50 dark:bg-brand-950/50"
                          : "bg-[var(--muted)]"
                      }`}>
                        <p className="whitespace-pre-wrap">{msg.content}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>

            {/* Reply Box */}
            <div className="border-t border-[var(--border)] p-4">
              <div className="flex gap-2">
                <Input placeholder="Type a message to intervene..." className="flex-1" />
                <Button size="icon">
                  <Send className="h-4 w-4" />
                </Button>
              </div>
              <p className="mt-1.5 text-[10px] text-[var(--muted-foreground)]">
                Sending a message will pause the AI agent and switch to human mode
              </p>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
