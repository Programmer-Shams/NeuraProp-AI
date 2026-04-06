// ============================================
// Core Entity Types for NeuraProp AI
// ============================================

export type FirmStatus = "onboarding" | "active" | "suspended" | "churned";
export type PlanTier = "starter" | "growth" | "enterprise";
export type KYCStatus = "pending" | "verified" | "rejected" | "expired";
export type RiskTier = "standard" | "elevated" | "high";
export type ConversationStatus = "active" | "resolved" | "escalated" | "archived";
export type TicketPriority = "low" | "medium" | "high" | "critical";
export type TicketStatus = "open" | "in_progress" | "waiting_on_trader" | "resolved" | "closed";
export type AgentName =
  | "orchestrator"
  | "payout"
  | "rules"
  | "account_kyc"
  | "technical"
  | "billing"
  | "compliance"
  | "onboarding";
export type RiskLevel = "low" | "medium" | "high" | "critical";
export type AuditActionStatus = "success" | "failed" | "pending_approval" | "denied";

export interface Firm {
  id: string;
  name: string;
  slug: string;
  status: FirmStatus;
  planTier: PlanTier;
  settings: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

export interface FirmConfig {
  firmId: string;
  branding: BrandingConfig;
  agents: Record<AgentName, AgentConfig>;
  integrations: Record<string, IntegrationConfig>;
  autoApprovePayoutLimit: number;
  escalationEmail: string;
  supportedChannels: ChannelType[];
  features: Record<string, boolean>;
}

export interface BrandingConfig {
  logoUrl: string | null;
  primaryColor: string;
  botName: string;
  welcomeMessage: string;
}

export interface AgentConfig {
  enabled: boolean;
  systemPromptOverride: string | null;
  enabledTools: string[];
  riskThreshold: RiskLevel;
}

export interface IntegrationConfig {
  type: string;
  enabled: boolean;
  credentialRef: string;
  settings: Record<string, unknown>;
}

export interface Trader {
  id: string;
  firmId: string;
  externalId: string | null;
  email: string | null;
  displayName: string | null;
  kycStatus: KYCStatus;
  riskTier: RiskTier;
  profileData: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

export interface TraderAccount {
  id: string;
  traderId: string;
  firmId: string;
  platform: string;
  accountNumber: string;
  accountType: string;
  status: string;
  metadata: Record<string, unknown>;
}

export interface Conversation {
  id: string;
  firmId: string;
  traderId: string | null;
  channel: ChannelType;
  channelRef: string | null;
  status: ConversationStatus;
  currentAgent: AgentName | null;
  satisfaction: number | null;
  metadata: Record<string, unknown>;
  startedAt: string;
  resolvedAt: string | null;
  updatedAt: string;
}

export interface Message {
  id: string;
  conversationId: string;
  firmId: string;
  role: "user" | "assistant" | "system" | "tool";
  content: string;
  agentName: AgentName | null;
  toolCalls: ToolCallRecord[] | null;
  llmModel: string | null;
  llmTokens: { promptTokens: number; completionTokens: number } | null;
  llmLatencyMs: number | null;
  createdAt: string;
}

export interface ToolCallRecord {
  toolName: string;
  input: Record<string, unknown>;
  output: Record<string, unknown>;
  status: AuditActionStatus;
  durationMs: number;
}

export interface Ticket {
  id: string;
  firmId: string;
  conversationId: string;
  traderId: string | null;
  priority: TicketPriority;
  status: TicketStatus;
  assignedTo: string | null;
  summary: string;
  escalationReason: string | null;
  createdAt: string;
  updatedAt: string;
  resolvedAt: string | null;
}

export interface AuditLogEntry {
  id: string;
  firmId: string;
  conversationId: string | null;
  traderId: string | null;
  agentName: AgentName;
  actionType: string;
  actionInput: Record<string, unknown>;
  actionOutput: Record<string, unknown>;
  status: AuditActionStatus;
  riskLevel: RiskLevel;
  approvedBy: string | null;
  executionMs: number;
  createdAt: string;
}

export type ChannelType = "discord" | "web_chat" | "email";
