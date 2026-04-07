"use client";

import { useState } from "react";
import {
  Plug,
  Check,
  X,
  Settings,
  RefreshCw,
  ExternalLink,
  Wifi,
  WifiOff,
  Shield,
  CreditCard,
  Hash,
  Globe,
  Mail,
  Code2,
  BarChart3,
  ArrowRight,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
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

interface Integration {
  id: string;
  name: string;
  description: string;
  category: "trading" | "kyc" | "channel" | "universal";
  status: "connected" | "available" | "error";
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  details?: {
    apiEndpoint?: string;
    lastSync?: string;
    accountsManaged?: number;
    uptime?: string;
  };
}

const integrations: Integration[] = [
  {
    id: "mt4",
    name: "MetaTrader 4",
    description: "Connect your MT4 Manager API for account and trade management",
    category: "trading",
    status: "connected",
    icon: BarChart3,
    color: "#1a73e8",
    details: { apiEndpoint: "mt4-manager.yourfirm.com:443", lastSync: "2 min ago", accountsManaged: 1240, uptime: "99.9%" },
  },
  {
    id: "mt5",
    name: "MetaTrader 5",
    description: "Connect your MT5 Manager API for account data and operations",
    category: "trading",
    status: "connected",
    icon: BarChart3,
    color: "#0d6efd",
    details: { apiEndpoint: "mt5-manager.yourfirm.com:443", lastSync: "1 min ago", accountsManaged: 3820, uptime: "99.8%" },
  },
  {
    id: "ctrader",
    name: "cTrader",
    description: "Connect via cTrader Open API for account data and operations",
    category: "trading",
    status: "connected",
    icon: BarChart3,
    color: "#00b4d8",
    details: { apiEndpoint: "openapi.ctrader.com", lastSync: "5 min ago", accountsManaged: 890, uptime: "99.7%" },
  },
  {
    id: "match-trader",
    name: "Match-Trader",
    description: "REST API integration for Match-Trader platform management",
    category: "trading",
    status: "available",
    icon: BarChart3,
    color: "#7c3aed",
  },
  {
    id: "trade-locker",
    name: "TradeLocker",
    description: "JWT-based API for TradeLocker account and trade operations",
    category: "trading",
    status: "available",
    icon: BarChart3,
    color: "#059669",
  },
  {
    id: "veriff",
    name: "Veriff",
    description: "Automated KYC identity verification for trader onboarding",
    category: "kyc",
    status: "connected",
    icon: Shield,
    color: "#6366f1",
    details: { apiEndpoint: "station.veriff.com/v1", lastSync: "10 min ago", accountsManaged: 15200, uptime: "99.95%" },
  },
  {
    id: "discord",
    name: "Discord",
    description: "White-label Discord bot for your trading community server",
    category: "channel",
    status: "connected",
    icon: Hash,
    color: "#5865F2",
    details: { lastSync: "Live", accountsManaged: 8500, uptime: "99.9%" },
  },
  {
    id: "webchat",
    name: "Web Chat",
    description: "Embedded WebSocket chat widget for your website",
    category: "channel",
    status: "connected",
    icon: Globe,
    color: "#6366f1",
    details: { lastSync: "Live", accountsManaged: 4200, uptime: "99.8%" },
  },
  {
    id: "email",
    name: "Email (SES + SendGrid)",
    description: "Inbound via Amazon SES, outbound via SendGrid with templates",
    category: "channel",
    status: "connected",
    icon: Mail,
    color: "#8b5cf6",
    details: { lastSync: "3 min ago", accountsManaged: 2100, uptime: "99.9%" },
  },
  {
    id: "universal",
    name: "Universal API",
    description: "Connect any system through configurable API templates with JSONPath",
    category: "universal",
    status: "available",
    icon: Code2,
    color: "#f59e0b",
  },
];

const categoryLabels: Record<string, string> = {
  trading: "Trading Platforms",
  kyc: "KYC & Verification",
  channel: "Communication Channels",
  universal: "Universal",
};

export default function IntegrationsPage() {
  const [configDialog, setConfigDialog] = useState<string | null>(null);

  const connectedCount = integrations.filter((i) => i.status === "connected").length;
  const categories = ["trading", "kyc", "channel", "universal"] as const;

  const configTarget = integrations.find((i) => i.id === configDialog);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Integrations</h1>
          <p className="text-sm text-[var(--muted-foreground)]">
            Connect your trading platforms, KYC provider, and communication channels
          </p>
        </div>
        <Badge variant="success" className="text-sm">
          <Wifi className="mr-1.5 h-3.5 w-3.5" />
          {connectedCount} connected
        </Badge>
      </div>

      {categories.map((cat) => {
        const catIntegrations = integrations.filter((i) => i.category === cat);
        if (catIntegrations.length === 0) return null;

        return (
          <div key={cat}>
            <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-[var(--muted-foreground)]">
              {categoryLabels[cat]}
            </h2>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {catIntegrations.map((integration) => {
                const Icon = integration.icon;
                const isConnected = integration.status === "connected";

                return (
                  <Card key={integration.id} className="transition-all hover:shadow-md">
                    <CardContent className="p-5">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-3">
                          <div
                            className="flex h-10 w-10 items-center justify-center rounded-lg"
                            style={{ backgroundColor: `${integration.color}15` }}
                          >
                            <Icon className="h-5 w-5 text-[var(--foreground)]" />
                          </div>
                          <div>
                            <h3 className="text-sm font-semibold">{integration.name}</h3>
                            <span className="text-[10px] uppercase tracking-wider text-[var(--muted-foreground)]">
                              {integration.category}
                            </span>
                          </div>
                        </div>
                        {isConnected ? (
                          <Badge variant="success" className="text-[10px]">
                            <Check className="mr-1 h-3 w-3" />
                            Connected
                          </Badge>
                        ) : integration.status === "error" ? (
                          <Badge variant="danger" className="text-[10px]">
                            <WifiOff className="mr-1 h-3 w-3" />
                            Error
                          </Badge>
                        ) : (
                          <Badge variant="secondary" className="text-[10px]">Available</Badge>
                        )}
                      </div>

                      <p className="mt-3 text-xs text-[var(--muted-foreground)] leading-relaxed">
                        {integration.description}
                      </p>

                      {isConnected && integration.details && (
                        <div className="mt-3 grid grid-cols-2 gap-2 rounded-lg bg-[var(--muted)]/50 p-2.5">
                          {integration.details.accountsManaged && (
                            <div>
                              <p className="text-[10px] text-[var(--muted-foreground)]">Managed</p>
                              <p className="text-xs font-semibold">{integration.details.accountsManaged.toLocaleString()}</p>
                            </div>
                          )}
                          {integration.details.uptime && (
                            <div>
                              <p className="text-[10px] text-[var(--muted-foreground)]">Uptime</p>
                              <p className="text-xs font-semibold">{integration.details.uptime}</p>
                            </div>
                          )}
                          {integration.details.lastSync && (
                            <div>
                              <p className="text-[10px] text-[var(--muted-foreground)]">Last sync</p>
                              <p className="text-xs font-semibold">{integration.details.lastSync}</p>
                            </div>
                          )}
                        </div>
                      )}

                      <div className="mt-4">
                        {isConnected ? (
                          <div className="flex gap-2">
                            <Button variant="outline" size="sm" className="flex-1" onClick={() => setConfigDialog(integration.id)}>
                              <Settings className="mr-1.5 h-3.5 w-3.5" />
                              Configure
                            </Button>
                            <Button variant="ghost" size="sm">
                              <RefreshCw className="h-3.5 w-3.5" />
                            </Button>
                          </div>
                        ) : (
                          <Button size="sm" className="w-full">
                            <Plug className="mr-1.5 h-3.5 w-3.5" />
                            Connect
                          </Button>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>
        );
      })}

      {/* Configuration Dialog */}
      <Dialog open={!!configDialog} onOpenChange={(open) => !open && setConfigDialog(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Configure {configTarget?.name}</DialogTitle>
            <DialogDescription>Manage your connection settings and credentials</DialogDescription>
          </DialogHeader>
          {configTarget && (
            <div className="space-y-4 py-4">
              {configTarget.details?.apiEndpoint && (
                <div>
                  <label className="text-sm font-medium">API Endpoint</label>
                  <Input className="mt-1" value={configTarget.details.apiEndpoint} readOnly />
                </div>
              )}
              <div>
                <label className="text-sm font-medium">API Key</label>
                <Input className="mt-1" type="password" value="••••••••••••••••••••" readOnly />
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">Auto-sync</p>
                  <p className="text-xs text-[var(--muted-foreground)]">Sync data every 5 minutes</p>
                </div>
                <Switch defaultChecked />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">Enable webhooks</p>
                  <p className="text-xs text-[var(--muted-foreground)]">Receive real-time event notifications</p>
                </div>
                <Switch defaultChecked />
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setConfigDialog(null)}>Close</Button>
            <Button>Save Changes</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
