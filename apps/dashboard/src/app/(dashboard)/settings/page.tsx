"use client";

import { useState } from "react";
import {
  Building2,
  Palette,
  Key,
  Bot,
  Bell,
  Shield,
  Copy,
  Eye,
  EyeOff,
  Plus,
  Trash2,
  RotateCcw,
  Save,
  AlertTriangle,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogTrigger,
} from "@/components/ui/dialog";

// --- Mock Data ---

const apiKeys = [
  { id: "key-1", name: "Production API Key", prefix: "np_live_", created: "Feb 10, 2026", lastUsed: "2 min ago", status: "active" as const },
  { id: "key-2", name: "Development API Key", prefix: "np_test_", created: "Mar 1, 2026", lastUsed: "1 hr ago", status: "active" as const },
  { id: "key-3", name: "Webhook Signing Key", prefix: "np_whk_", created: "Mar 5, 2026", lastUsed: "5 min ago", status: "active" as const },
];

export default function SettingsPage() {
  const [showKeys, setShowKeys] = useState<Record<string, boolean>>({});

  const toggleKeyVisibility = (keyId: string) => {
    setShowKeys((prev) => ({ ...prev, [keyId]: !prev[keyId] }));
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Settings</h1>
        <p className="text-sm text-[var(--muted-foreground)]">
          Configure your firm profile, branding, and AI agent behavior
        </p>
      </div>

      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList>
          <TabsTrigger value="profile">Firm Profile</TabsTrigger>
          <TabsTrigger value="branding">Branding</TabsTrigger>
          <TabsTrigger value="agents">AI Agents</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="api-keys">API Keys</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
        </TabsList>

        {/* Firm Profile Tab */}
        <TabsContent value="profile">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building2 className="h-5 w-5" />
                Firm Profile
              </CardTitle>
              <CardDescription>Basic information about your prop trading firm</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label className="text-sm font-medium">Firm Name</label>
                  <Input className="mt-1" defaultValue="Alpha Capital Trading" />
                </div>
                <div>
                  <label className="text-sm font-medium">Firm Slug</label>
                  <Input className="mt-1" defaultValue="alpha-capital" disabled />
                  <p className="mt-1 text-[10px] text-[var(--muted-foreground)]">Used for email routing: support@alpha-capital.neuraprop.ai</p>
                </div>
                <div>
                  <label className="text-sm font-medium">Support Email</label>
                  <Input className="mt-1" defaultValue="support@alphacapital.com" />
                </div>
                <div>
                  <label className="text-sm font-medium">Website</label>
                  <Input className="mt-1" defaultValue="https://alphacapital.com" />
                </div>
                <div className="sm:col-span-2">
                  <label className="text-sm font-medium">Firm Description</label>
                  <Textarea className="mt-1" defaultValue="Alpha Capital is a leading proprietary trading firm offering evaluation challenges from $10K to $200K." rows={3} />
                </div>
                <div>
                  <label className="text-sm font-medium">Timezone</label>
                  <Select defaultValue="utc">
                    <SelectTrigger className="mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="utc">UTC</SelectItem>
                      <SelectItem value="est">Eastern (EST)</SelectItem>
                      <SelectItem value="cet">Central European (CET)</SelectItem>
                      <SelectItem value="gmt">GMT</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-medium">Default Language</label>
                  <Select defaultValue="en">
                    <SelectTrigger className="mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="en">English</SelectItem>
                      <SelectItem value="es">Spanish</SelectItem>
                      <SelectItem value="fr">French</SelectItem>
                      <SelectItem value="de">German</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="flex justify-end">
                <Button>
                  <Save className="mr-1.5 h-4 w-4" />
                  Save Changes
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Branding Tab */}
        <TabsContent value="branding">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Palette className="h-5 w-5" />
                Branding
              </CardTitle>
              <CardDescription>Customize how your AI agents appear to traders</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label className="text-sm font-medium">Bot Display Name</label>
                  <Input className="mt-1" defaultValue="Alpha Support" />
                </div>
                <div>
                  <label className="text-sm font-medium">Bot Avatar URL</label>
                  <Input className="mt-1" placeholder="https://yourfirm.com/bot-avatar.png" />
                </div>
                <div>
                  <label className="text-sm font-medium">Primary Brand Color</label>
                  <div className="mt-1 flex gap-2">
                    <input type="color" defaultValue="#6366f1" className="h-9 w-12 cursor-pointer rounded-lg border border-[var(--border)]" />
                    <Input defaultValue="#6366f1" className="flex-1" />
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium">Secondary Color</label>
                  <div className="mt-1 flex gap-2">
                    <input type="color" defaultValue="#8b5cf6" className="h-9 w-12 cursor-pointer rounded-lg border border-[var(--border)]" />
                    <Input defaultValue="#8b5cf6" className="flex-1" />
                  </div>
                </div>
                <div className="sm:col-span-2">
                  <label className="text-sm font-medium">Welcome Message</label>
                  <Textarea
                    className="mt-1"
                    defaultValue="Welcome to Alpha Capital Support! I'm your AI assistant. How can I help you today?"
                    rows={3}
                  />
                </div>
                <div className="sm:col-span-2">
                  <label className="text-sm font-medium">Fallback Message</label>
                  <Textarea
                    className="mt-1"
                    defaultValue="I'm not sure I can help with that. Let me connect you with our support team for further assistance."
                    rows={2}
                  />
                </div>
              </div>

              <Separator />

              <div>
                <h3 className="text-sm font-semibold">Preview</h3>
                <div className="mt-3 max-w-sm rounded-xl border border-[var(--border)] bg-[var(--card)] p-4 shadow-lg">
                  <div className="flex items-center gap-2 border-b border-[var(--border)] pb-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-600">
                      <Bot className="h-4 w-4 text-white" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold">Alpha Support</p>
                      <p className="text-[10px] text-emerald-600">Online</p>
                    </div>
                  </div>
                  <div className="mt-3 rounded-lg bg-brand-50 p-3 dark:bg-brand-950/50">
                    <p className="text-xs">Welcome to Alpha Capital Support! I&apos;m your AI assistant. How can I help you today?</p>
                  </div>
                </div>
              </div>

              <div className="flex justify-end">
                <Button>
                  <Save className="mr-1.5 h-4 w-4" />
                  Save Changes
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* AI Agents Tab */}
        <TabsContent value="agents">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bot className="h-5 w-5" />
                AI Agent Configuration
              </CardTitle>
              <CardDescription>Configure behavior, models, and thresholds for your AI agents</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label className="text-sm font-medium">Primary LLM Model</label>
                  <Select defaultValue="claude-sonnet">
                    <SelectTrigger className="mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="claude-sonnet">Claude Sonnet (Recommended)</SelectItem>
                      <SelectItem value="claude-opus">Claude Opus</SelectItem>
                      <SelectItem value="gpt-4o">GPT-4o</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-medium">Router Model</label>
                  <Select defaultValue="claude-haiku">
                    <SelectTrigger className="mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="claude-haiku">Claude Haiku (Fast + Cheap)</SelectItem>
                      <SelectItem value="claude-sonnet">Claude Sonnet</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-medium">Payout Auto-Approve Limit</label>
                  <Input className="mt-1" type="number" defaultValue="5000" />
                  <p className="mt-1 text-[10px] text-[var(--muted-foreground)]">Payouts above this amount require manual approval</p>
                </div>
                <div>
                  <label className="text-sm font-medium">Max Conversation Turns</label>
                  <Input className="mt-1" type="number" defaultValue="20" />
                  <p className="mt-1 text-[10px] text-[var(--muted-foreground)]">Auto-escalate after this many turns without resolution</p>
                </div>
              </div>

              <Separator />

              <div className="space-y-4">
                <h3 className="text-sm font-semibold">Agent Toggles</h3>
                {[
                  { name: "Payout Agent", desc: "Handle withdrawal requests and payout processing", enabled: true },
                  { name: "Rules Agent", desc: "Explain trading rules and check violations", enabled: true },
                  { name: "Account/KYC Agent", desc: "Manage accounts, resets, and KYC verification", enabled: true },
                  { name: "Technical Agent", desc: "Troubleshoot platform issues and connectivity", enabled: true },
                  { name: "Billing Agent", desc: "Handle billing inquiries, refunds, and subscriptions", enabled: true },
                  { name: "Compliance Agent", desc: "Monitor compliance issues and trading restrictions", enabled: true },
                  { name: "Onboarding Agent", desc: "Guide new traders through setup and challenges", enabled: true },
                ].map((agent) => (
                  <div key={agent.name} className="flex items-center justify-between rounded-lg border border-[var(--border)] p-3">
                    <div>
                      <p className="text-sm font-medium">{agent.name}</p>
                      <p className="text-xs text-[var(--muted-foreground)]">{agent.desc}</p>
                    </div>
                    <Switch defaultChecked={agent.enabled} />
                  </div>
                ))}
              </div>

              <div className="flex justify-end">
                <Button>
                  <Save className="mr-1.5 h-4 w-4" />
                  Save Changes
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Notifications Tab */}
        <TabsContent value="notifications">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5" />
                Notification Preferences
              </CardTitle>
              <CardDescription>Control when and how you get notified</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {[
                { title: "New Escalations", desc: "Get notified when an issue is escalated to humans", email: true, slack: true },
                { title: "Critical Compliance Alerts", desc: "Immediate alerts for compliance flags", email: true, slack: true },
                { title: "High-Value Payout Approvals", desc: "When a payout exceeds the auto-approve limit", email: true, slack: false },
                { title: "Daily Performance Summary", desc: "End-of-day overview of AI performance metrics", email: true, slack: false },
                { title: "Weekly Analytics Report", desc: "Comprehensive weekly breakdown of all metrics", email: true, slack: false },
                { title: "System Health Alerts", desc: "When integrations go down or error rates spike", email: true, slack: true },
              ].map((notif) => (
                <div key={notif.title} className="flex items-center justify-between rounded-lg border border-[var(--border)] p-4">
                  <div>
                    <p className="text-sm font-medium">{notif.title}</p>
                    <p className="text-xs text-[var(--muted-foreground)]">{notif.desc}</p>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-[var(--muted-foreground)]">Email</span>
                      <Switch defaultChecked={notif.email} />
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-[var(--muted-foreground)]">Slack</span>
                      <Switch defaultChecked={notif.slack} />
                    </div>
                  </div>
                </div>
              ))}
              <div className="flex justify-end pt-2">
                <Button>
                  <Save className="mr-1.5 h-4 w-4" />
                  Save Preferences
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* API Keys Tab */}
        <TabsContent value="api-keys">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Key className="h-5 w-5" />
                    API Keys
                  </CardTitle>
                  <CardDescription>Manage API keys for programmatic access to NeuraProp</CardDescription>
                </div>
                <Dialog>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="mr-1.5 h-4 w-4" />
                      Generate New Key
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Generate API Key</DialogTitle>
                      <DialogDescription>Create a new API key for programmatic access</DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                      <div>
                        <label className="text-sm font-medium">Key Name</label>
                        <Input className="mt-1" placeholder="e.g., Production API Key" />
                      </div>
                      <div>
                        <label className="text-sm font-medium">Environment</label>
                        <Select>
                          <SelectTrigger className="mt-1">
                            <SelectValue placeholder="Select environment" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="live">Live (Production)</SelectItem>
                            <SelectItem value="test">Test (Sandbox)</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                    <DialogFooter>
                      <Button variant="outline">Cancel</Button>
                      <Button>Generate Key</Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {apiKeys.map((key) => (
                  <div key={key.id} className="flex items-center justify-between rounded-lg border border-[var(--border)] p-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-medium">{key.name}</p>
                        <Badge variant="success" className="text-[10px]">{key.status}</Badge>
                      </div>
                      <div className="mt-1 flex items-center gap-2">
                        <code className="text-xs font-mono text-[var(--muted-foreground)]">
                          {showKeys[key.id] ? `${key.prefix}sk-abc123def456ghi789` : `${key.prefix}sk-••••••••••••`}
                        </code>
                        <button onClick={() => toggleKeyVisibility(key.id)} className="text-[var(--muted-foreground)] hover:text-[var(--foreground)]">
                          {showKeys[key.id] ? <EyeOff className="h-3.5 w-3.5" /> : <Eye className="h-3.5 w-3.5" />}
                        </button>
                        <button className="text-[var(--muted-foreground)] hover:text-[var(--foreground)]">
                          <Copy className="h-3.5 w-3.5" />
                        </button>
                      </div>
                      <p className="mt-1 text-[10px] text-[var(--muted-foreground)]">
                        Created {key.created} &middot; Last used {key.lastUsed}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button variant="ghost" size="sm">
                        <RotateCcw className="mr-1 h-3.5 w-3.5" />
                        Rotate
                      </Button>
                      <Button variant="ghost" size="sm" className="text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950">
                        <Trash2 className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security Tab */}
        <TabsContent value="security">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Security Settings
              </CardTitle>
              <CardDescription>Manage security and access controls</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                {[
                  { title: "Two-Factor Authentication", desc: "Require 2FA for all team members", enabled: true },
                  { title: "IP Allowlisting", desc: "Restrict API access to specific IP addresses", enabled: false },
                  { title: "Webhook Signature Verification", desc: "Verify HMAC signatures on all inbound webhooks", enabled: true },
                  { title: "Audit Logging", desc: "Log all tool executions and sensitive operations", enabled: true },
                  { title: "Row-Level Security", desc: "Enforce tenant data isolation at database level", enabled: true },
                  { title: "Rate Limiting", desc: "Sliding window rate limits on API endpoints", enabled: true },
                ].map((setting) => (
                  <div key={setting.title} className="flex items-center justify-between rounded-lg border border-[var(--border)] p-4">
                    <div>
                      <p className="text-sm font-medium">{setting.title}</p>
                      <p className="text-xs text-[var(--muted-foreground)]">{setting.desc}</p>
                    </div>
                    <Switch defaultChecked={setting.enabled} />
                  </div>
                ))}
              </div>

              <Separator />

              <div className="rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-900 dark:bg-red-950/50">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="h-5 w-5 shrink-0 text-red-600" />
                  <div>
                    <p className="text-sm font-medium text-red-900 dark:text-red-200">Danger Zone</p>
                    <p className="mt-1 text-xs text-red-700 dark:text-red-300">
                      These actions are destructive and cannot be undone.
                    </p>
                    <div className="mt-3 flex gap-2">
                      <Button variant="outline" size="sm" className="border-red-300 text-red-700 hover:bg-red-100 dark:border-red-800 dark:text-red-300">
                        Reset All Agent Settings
                      </Button>
                      <Button variant="outline" size="sm" className="border-red-300 text-red-700 hover:bg-red-100 dark:border-red-800 dark:text-red-300">
                        Delete All Data
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
