"""Compliance tools — always routes to human review for actions."""

from agents.tools.base import BaseTool, ToolContext, ToolResult


class GetComplianceStatus(BaseTool):
    name = "compliance_get_status"
    description = "Get the compliance status and any flags on a trader's account."
    parameters = {
        "type": "object",
        "properties": {"trader_id": {"type": "string"}},
        "required": ["trader_id"],
    }
    risk_level = "low"

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return bool(params.get("trader_id"))

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        return ToolResult(success=True, data={
            "trader_id": params["trader_id"],
            "status": "clear",
            "flags": [],
            "jurisdiction": "US",
            "restrictions": [],
        })


class FlagComplianceIssue(BaseTool):
    name = "compliance_flag_issue"
    description = "Flag a compliance issue for human review. This ALWAYS creates a ticket for the compliance team."
    parameters = {
        "type": "object",
        "properties": {
            "trader_id": {"type": "string"},
            "issue_type": {"type": "string"},
            "description": {"type": "string"},
        },
        "required": ["trader_id", "issue_type", "description"],
    }
    risk_level = "critical"
    requires_approval = True

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return all(params.get(f) for f in ["trader_id", "issue_type", "description"])

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        return ToolResult(success=True, data={
            "ticket_id": "COMP-001",
            "status": "pending_review",
            "priority": "high",
        })


class CheckTradingRestrictions(BaseTool):
    name = "compliance_check_restrictions"
    description = "Check jurisdiction-based trading restrictions for a trader."
    parameters = {
        "type": "object",
        "properties": {
            "trader_id": {"type": "string"},
            "jurisdiction": {"type": "string", "description": "Country code"},
        },
        "required": ["trader_id"],
    }
    risk_level = "low"

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return bool(params.get("trader_id"))

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        return ToolResult(success=True, data={
            "trader_id": params["trader_id"],
            "jurisdiction": params.get("jurisdiction", "Unknown"),
            "restricted": False,
            "restrictions": [],
        })


def get_compliance_tools() -> list[BaseTool]:
    return [GetComplianceStatus(), FlagComplianceIssue(), CheckTradingRestrictions()]
