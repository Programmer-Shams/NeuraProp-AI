"""Initial schema with all core tables and RLS policies.

Revision ID: 0001
Revises: None
Create Date: 2026-04-06
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # ==================== FIRMS ====================
    op.create_table(
        "firms",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), unique=True, nullable=False),
        sa.Column("status", sa.String(20), server_default="onboarding"),
        sa.Column("plan_tier", sa.String(20), server_default="starter"),
        sa.Column("settings", postgresql.JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )

    # ==================== FIRM_CONFIGS ====================
    op.create_table(
        "firm_configs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("firm_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("firms.id"), nullable=False),
        sa.Column("branding", postgresql.JSONB, server_default="{}"),
        sa.Column("agent_configs", postgresql.JSONB, server_default="{}"),
        sa.Column("auto_approve_payout_limit", sa.Integer, server_default="0"),
        sa.Column("escalation_email", sa.String(255)),
        sa.Column("supported_channels", postgresql.JSONB, server_default="[]"),
        sa.Column("features", postgresql.JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("idx_firm_configs_firm", "firm_configs", ["firm_id"])

    # ==================== FIRM_INTEGRATIONS ====================
    op.create_table(
        "firm_integrations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("firm_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("firms.id"), nullable=False),
        sa.Column("integration_type", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("enabled", sa.Boolean, server_default="true"),
        sa.Column("credential_ref", sa.String(500)),
        sa.Column("settings", postgresql.JSONB, server_default="{}"),
        sa.Column("health_status", sa.String(20), server_default="'unknown'"),
        sa.Column("last_health_check", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.UniqueConstraint("firm_id", "integration_type", "name"),
    )
    op.create_index("idx_firm_integrations_firm", "firm_integrations", ["firm_id"])

    # ==================== FIRM_USERS ====================
    op.create_table(
        "firm_users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("firm_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("firms.id"), nullable=False),
        sa.Column("clerk_user_id", sa.String(255), unique=True, nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255)),
        sa.Column("role", sa.String(20), server_default="'admin'"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("idx_firm_users_firm", "firm_users", ["firm_id"])

    # ==================== TRADERS ====================
    op.create_table(
        "traders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("firm_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("firms.id"), nullable=False),
        sa.Column("external_id", sa.String(255)),
        sa.Column("email", sa.String(255)),
        sa.Column("display_name", sa.String(255)),
        sa.Column("kyc_status", sa.String(20), server_default="'pending'"),
        sa.Column("risk_tier", sa.String(20), server_default="'standard'"),
        sa.Column("profile_data", postgresql.JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.UniqueConstraint("firm_id", "external_id"),
        sa.UniqueConstraint("firm_id", "email"),
    )
    op.create_index("idx_traders_firm", "traders", ["firm_id"])

    # ==================== TRADER_ACCOUNTS ====================
    op.create_table(
        "trader_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("trader_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("traders.id"), nullable=False),
        sa.Column("firm_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("firms.id"), nullable=False),
        sa.Column("platform", sa.String(50), nullable=False),
        sa.Column("account_number", sa.String(100), nullable=False),
        sa.Column("account_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), server_default="'active'"),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.UniqueConstraint("firm_id", "platform", "account_number"),
    )
    op.create_index("idx_trader_accounts_trader", "trader_accounts", ["trader_id"])
    op.create_index("idx_trader_accounts_firm", "trader_accounts", ["firm_id"])

    # ==================== TRADER_CHANNEL_IDENTITIES ====================
    op.create_table(
        "trader_channel_identities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("trader_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("traders.id"), nullable=False),
        sa.Column("firm_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("firms.id"), nullable=False),
        sa.Column("channel", sa.String(20), nullable=False),
        sa.Column("channel_user_id", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.UniqueConstraint("firm_id", "channel", "channel_user_id"),
    )
    op.create_index("idx_tci_trader", "trader_channel_identities", ["trader_id"])
    op.create_index("idx_tci_firm", "trader_channel_identities", ["firm_id"])

    # ==================== CONVERSATIONS ====================
    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("firm_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("firms.id"), nullable=False),
        sa.Column("trader_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("traders.id")),
        sa.Column("channel", sa.String(20), nullable=False),
        sa.Column("channel_ref", sa.String(255)),
        sa.Column("status", sa.String(20), server_default="'active'"),
        sa.Column("current_agent", sa.String(50)),
        sa.Column("satisfaction", sa.SmallInteger),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("resolved_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("idx_conversations_firm", "conversations", ["firm_id"])
    op.create_index("idx_conversations_trader", "conversations", ["trader_id"])
    op.create_index("idx_conversations_status", "conversations", ["firm_id", "status"])

    # ==================== MESSAGES ====================
    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id"), nullable=False),
        sa.Column("firm_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("agent_name", sa.String(50)),
        sa.Column("tool_calls", postgresql.JSONB),
        sa.Column("llm_model", sa.String(100)),
        sa.Column("llm_tokens", postgresql.JSONB),
        sa.Column("llm_latency_ms", sa.Integer),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("idx_messages_conversation", "messages", ["conversation_id"])
    op.create_index("idx_messages_firm", "messages", ["firm_id"])

    # ==================== KB_DOCUMENTS ====================
    op.create_table(
        "kb_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("firm_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("firms.id"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("source_type", sa.String(20), nullable=False),
        sa.Column("source_url", sa.String(2000)),
        sa.Column("s3_key", sa.String(500)),
        sa.Column("content_type", sa.String(100)),
        sa.Column("file_size", sa.Integer),
        sa.Column("status", sa.String(20), server_default="'processing'"),
        sa.Column("chunk_count", sa.Integer, server_default="0"),
        sa.Column("tags", postgresql.JSONB, server_default="[]"),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("idx_kb_documents_firm", "kb_documents", ["firm_id"])

    # ==================== KB_CHUNKS (with pgvector) ====================
    op.create_table(
        "kb_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("firm_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("firms.id"), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("kb_documents.id")),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("chunk_index", sa.Integer),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("idx_kb_chunks_firm", "kb_chunks", ["firm_id"])
    op.create_index("idx_kb_chunks_document", "kb_chunks", ["document_id"])

    # Add vector column separately (Alembic doesn't natively support pgvector type)
    op.execute("ALTER TABLE kb_chunks ADD COLUMN embedding vector(1536)")
    op.execute("""
        CREATE INDEX idx_kb_chunks_embedding ON kb_chunks
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    """)

    # ==================== KB_FAQS ====================
    op.create_table(
        "kb_faqs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("firm_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("firms.id"), nullable=False),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("answer", sa.Text, nullable=False),
        sa.Column("category", sa.String(100)),
        sa.Column("tags", postgresql.JSONB, server_default="[]"),
        sa.Column("enabled", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("idx_kb_faqs_firm", "kb_faqs", ["firm_id"])

    # ==================== TICKETS ====================
    op.create_table(
        "tickets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("firm_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("firms.id"), nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id"), nullable=False),
        sa.Column("trader_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("traders.id")),
        sa.Column("priority", sa.String(20), server_default="'medium'"),
        sa.Column("status", sa.String(20), server_default="'open'"),
        sa.Column("assigned_to", postgresql.UUID(as_uuid=True)),
        sa.Column("summary", sa.Text, nullable=False),
        sa.Column("escalation_reason", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("resolved_at", sa.DateTime(timezone=True)),
    )
    op.create_index("idx_tickets_firm", "tickets", ["firm_id"])
    op.create_index("idx_tickets_status", "tickets", ["firm_id", "status"])
    op.create_index("idx_tickets_conversation", "tickets", ["conversation_id"])

    # ==================== TICKET_NOTES ====================
    op.create_table(
        "ticket_notes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("ticket_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tickets.id"), nullable=False),
        sa.Column("firm_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("author_id", postgresql.UUID(as_uuid=True)),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("idx_ticket_notes_ticket", "ticket_notes", ["ticket_id"])

    # ==================== ACTIONS_AUDIT_LOG ====================
    op.create_table(
        "actions_audit_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("firm_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True)),
        sa.Column("trader_id", postgresql.UUID(as_uuid=True)),
        sa.Column("agent_name", sa.String(50), nullable=False),
        sa.Column("action_type", sa.String(100), nullable=False),
        sa.Column("action_input", postgresql.JSONB),
        sa.Column("action_output", postgresql.JSONB),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("risk_level", sa.String(20)),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True)),
        sa.Column("execution_ms", sa.Integer),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("idx_audit_firm", "actions_audit_log", ["firm_id"])
    op.create_index("idx_audit_conversation", "actions_audit_log", ["conversation_id"])
    op.create_index("idx_audit_type", "actions_audit_log", ["action_type"])
    op.create_index("idx_audit_created", "actions_audit_log", ["firm_id", "created_at"])

    # ==================== ANALYTICS_EVENTS ====================
    op.create_table(
        "analytics_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("firm_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("event_data", postgresql.JSONB, server_default="{}"),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True)),
        sa.Column("trader_id", postgresql.UUID(as_uuid=True)),
        sa.Column("agent_name", sa.String(50)),
        sa.Column("channel", sa.String(20)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("idx_analytics_firm", "analytics_events", ["firm_id"])
    op.create_index("idx_analytics_type", "analytics_events", ["event_type"])
    op.create_index("idx_analytics_created", "analytics_events", ["firm_id", "created_at"])

    # ==================== API_KEYS ====================
    op.create_table(
        "api_keys",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("firm_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("firms.id"), nullable=False),
        sa.Column("key_hash", sa.String(64), unique=True, nullable=False),
        sa.Column("key_prefix", sa.String(30), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("environment", sa.String(10), server_default="'live'"),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("last_used_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("idx_api_keys_firm", "api_keys", ["firm_id"])
    op.create_index("idx_api_keys_hash", "api_keys", ["key_hash"])

    # ==================== ROW-LEVEL SECURITY ====================
    tenant_tables = [
        "firm_configs", "firm_integrations", "firm_users",
        "traders", "trader_accounts", "trader_channel_identities",
        "conversations", "messages",
        "kb_documents", "kb_chunks", "kb_faqs",
        "tickets", "ticket_notes",
        "actions_audit_log", "analytics_events",
        "api_keys",
    ]

    for table in tenant_tables:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"""
            CREATE POLICY {table}_firm_isolation ON {table}
            USING (firm_id = current_setting('app.current_firm_id', true)::uuid)
        """)


def downgrade() -> None:
    tenant_tables = [
        "api_keys", "analytics_events", "actions_audit_log",
        "ticket_notes", "tickets",
        "kb_faqs", "kb_chunks", "kb_documents",
        "messages", "conversations",
        "trader_channel_identities", "trader_accounts", "traders",
        "firm_users", "firm_integrations", "firm_configs",
    ]
    for table in tenant_tables:
        op.execute(f"DROP POLICY IF EXISTS {table}_firm_isolation ON {table}")

    tables_to_drop = [
        "api_keys", "analytics_events", "actions_audit_log",
        "ticket_notes", "tickets",
        "kb_faqs", "kb_chunks", "kb_documents",
        "messages", "conversations",
        "trader_channel_identities", "trader_accounts", "traders",
        "firm_users", "firm_integrations", "firm_configs", "firms",
    ]
    for table in tables_to_drop:
        op.drop_table(table)

    op.execute("DROP EXTENSION IF EXISTS vector")
    op.execute("DROP EXTENSION IF EXISTS pgcrypto")
