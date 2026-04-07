"""Rules/Challenge agent tools — query trading rules, challenge status, violations."""

from typing import Any

from agents.tools.base import BaseTool, ToolContext, ToolResult


class GetTradingRules(BaseTool):
    name = "rules_get_trading_rules"
    description = "Get the trading rules for a specific challenge type or funded account, including drawdown limits, profit targets, and restricted instruments."
    parameters = {
        "type": "object",
        "properties": {
            "challenge_type": {
                "type": "string",
                "description": "Challenge type (e.g., 'standard', 'aggressive', 'funded')",
            },
            "account_size": {
                "type": "string",
                "description": "Account size tier (e.g., '10k', '25k', '50k', '100k', '200k')",
            },
        },
        "required": [],
    }
    risk_level = "low"

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return True

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        # In production, these come from the firm's knowledge base via RAG
        challenge_type = params.get("challenge_type", "standard")
        return ToolResult(
            success=True,
            data={
                "challenge_type": challenge_type,
                "rules": {
                    "max_daily_loss": "5% of initial balance",
                    "max_total_drawdown": "10% of initial balance",
                    "profit_target": "8% for Phase 1, 5% for Phase 2",
                    "min_trading_days": 5,
                    "max_trading_days": 30,
                    "weekend_holding": "Allowed",
                    "news_trading": "Allowed with caution",
                    "ea_bots": "Allowed (must be original)",
                    "copy_trading": "Not allowed between funded accounts",
                    "restricted_instruments": [],
                    "max_lot_size": "Depends on account size",
                    "profit_split": "80/20 (trader/firm)",
                },
            },
        )


class GetChallengeStatus(BaseTool):
    name = "rules_get_challenge_status"
    description = "Get the current status of a trader's challenge or evaluation, including progress toward profit targets and rule compliance."
    parameters = {
        "type": "object",
        "properties": {
            "trader_id": {"type": "string", "description": "The trader's unique ID"},
            "account_id": {"type": "string", "description": "Challenge account ID"},
        },
        "required": ["trader_id"],
    }
    risk_level = "low"

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return bool(params.get("trader_id"))

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        return ToolResult(
            success=True,
            data={
                "trader_id": params["trader_id"],
                "challenge_type": "standard",
                "phase": 1,
                "account_size": 50000,
                "status": "active",
                "started_at": "2026-03-25",
                "days_traded": 8,
                "min_days_required": 5,
                "current_balance": 53200.00,
                "profit_target": 54000.00,  # 8% of 50k
                "profit_progress_pct": 80.0,
                "max_daily_loss_remaining": 2500.00,
                "max_drawdown_remaining": 4200.00,
                "violations": [],
                "on_track": True,
            },
        )


class GetRuleViolations(BaseTool):
    name = "rules_get_violations"
    description = "Get any rule violations recorded for a trader's account."
    parameters = {
        "type": "object",
        "properties": {
            "trader_id": {"type": "string", "description": "The trader's unique ID"},
            "account_id": {"type": "string", "description": "Trading account ID"},
        },
        "required": ["trader_id"],
    }
    risk_level = "low"

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return bool(params.get("trader_id"))

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        return ToolResult(
            success=True,
            data={
                "trader_id": params["trader_id"],
                "violations": [],
                "warnings": [
                    {
                        "type": "daily_loss_warning",
                        "date": "2026-04-02",
                        "details": "Daily loss reached 3.8% (limit 5%)",
                        "severity": "warning",
                    }
                ],
                "account_status": "active",
            },
        )


class CheckSpecificRule(BaseTool):
    name = "rules_check_specific"
    description = "Check details about a specific trading rule, such as lot size limits, holding restrictions, or instrument restrictions."
    parameters = {
        "type": "object",
        "properties": {
            "rule_topic": {
                "type": "string",
                "description": "The rule topic to look up (e.g., 'lot_size', 'weekend_holding', 'news_trading', 'ea_bots')",
            },
        },
        "required": ["rule_topic"],
    }
    risk_level = "low"

    async def validate(self, params: dict, context: ToolContext) -> bool:
        return bool(params.get("rule_topic"))

    async def execute(self, params: dict, context: ToolContext) -> ToolResult:
        # In production, this queries the firm's knowledge base
        return ToolResult(
            success=True,
            data={
                "rule_topic": params["rule_topic"],
                "answer": f"Information about '{params['rule_topic']}' will be retrieved from the firm's knowledge base.",
                "source": "knowledge_base",
                "note": "This answer is augmented with RAG retrieval from firm-specific documents.",
            },
        )


def get_rules_tools() -> list[BaseTool]:
    return [
        GetTradingRules(),
        GetChallengeStatus(),
        GetRuleViolations(),
        CheckSpecificRule(),
    ]
