import type {
  Conversation,
  Firm,
  FirmConfig,
  Message,
  Ticket,
  Trader,
  AuditLogEntry,
} from "./entities";

// ============================================
// API Request/Response Types
// ============================================

// Pagination
export interface PaginationParams {
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortOrder?: "asc" | "desc";
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// Firms
export interface CreateFirmRequest {
  name: string;
  slug: string;
  planTier?: string;
}

export interface UpdateFirmRequest {
  name?: string;
  status?: string;
  planTier?: string;
  settings?: Record<string, unknown>;
}

export type FirmResponse = Firm;
export type FirmConfigResponse = FirmConfig;

// Traders
export interface CreateTraderRequest {
  externalId?: string;
  email?: string;
  displayName?: string;
  profileData?: Record<string, unknown>;
}

export type TraderResponse = Trader;
export type TraderListResponse = PaginatedResponse<Trader>;

// Conversations
export interface ConversationListParams extends PaginationParams {
  status?: string;
  channel?: string;
  agentName?: string;
  traderId?: string;
}

export type ConversationResponse = Conversation & {
  trader: Trader | null;
  messageCount: number;
  lastMessageAt: string | null;
};

export type ConversationDetailResponse = Conversation & {
  trader: Trader | null;
  messages: Message[];
};

// Tickets
export interface CreateTicketRequest {
  conversationId: string;
  priority: string;
  summary: string;
  escalationReason?: string;
}

export interface UpdateTicketRequest {
  status?: string;
  priority?: string;
  assignedTo?: string | null;
}

export type TicketResponse = Ticket & {
  conversation: Conversation | null;
  trader: Trader | null;
};

// Analytics
export interface AnalyticsOverview {
  activeConversations: number;
  totalConversationsToday: number;
  avgResponseTimeMs: number;
  resolutionRate: number;
  escalationRate: number;
  topIntents: { intent: string; count: number }[];
  channelBreakdown: { channel: string; count: number }[];
  agentBreakdown: { agent: string; count: number }[];
  satisfactionAvg: number | null;
}

export interface AnalyticsTimeSeries {
  period: string;
  conversationCount: number;
  avgResponseTimeMs: number;
  resolutionRate: number;
  escalationRate: number;
}

// Audit
export type AuditLogResponse = PaginatedResponse<AuditLogEntry>;

// Inbound Message (from channels)
export interface InboundMessageRequest {
  channel: string;
  senderChannelId: string;
  content: string;
  attachments?: { filename: string; contentType: string; url: string }[];
  metadata?: Record<string, unknown>;
  conversationId?: string;
}

// API Error
export interface ApiError {
  error: string;
  message: string;
  details?: Record<string, unknown>;
}
