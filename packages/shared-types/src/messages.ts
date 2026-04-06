import type { AgentName, ChannelType } from "./entities";

export type SenderType = "trader" | "agent" | "system";
export type MessageDirection = "inbound" | "outbound";

export interface Attachment {
  id: string;
  filename: string;
  contentType: string;
  size: number;
  url: string;
}

export interface UnifiedMessage {
  id: string;
  firmId: string;
  channel: ChannelType;
  direction: MessageDirection;
  senderType: SenderType;
  senderChannelId: string;
  traderId: string | null;
  content: string;
  attachments: Attachment[];
  metadata: Record<string, unknown>;
  conversationId: string | null;
  replyToMessageId: string | null;
  createdAt: string;
  channelTimestamp: string | null;
}

export interface AgentResponse {
  conversationId: string;
  firmId: string;
  channel: ChannelType;
  agentName: AgentName;
  content: string;
  attachments: Attachment[];
  metadata: Record<string, unknown>;
  toolCallsMade: number;
  llmModel: string;
  totalLatencyMs: number;
}

export interface EscalationEvent {
  conversationId: string;
  firmId: string;
  traderId: string | null;
  agentName: AgentName;
  reason: string;
  summary: string;
  priority: "low" | "medium" | "high" | "critical";
  conversationHistory: UnifiedMessage[];
}
