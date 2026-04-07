"""Tests for agent specialist routing and configuration."""

import pytest

from agents.specialists.base import BaseSpecialistAgent


class TestBaseSpecialist:
    def test_abstract_methods(self):
        """BaseSpecialistAgent cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseSpecialistAgent()

    def test_specialist_subclass_requirements(self):
        """Verify that all specialist agents implement required methods."""
        from agents.specialists.payout import PayoutAgent
        from agents.specialists.rules import RulesAgent
        from agents.specialists.account_kyc import AccountKYCAgent
        from agents.specialists.technical import TechnicalAgent
        from agents.specialists.billing import BillingAgent
        from agents.specialists.compliance import ComplianceAgent
        from agents.specialists.onboarding import OnboardingAgent

        agents = [
            PayoutAgent, RulesAgent, AccountKYCAgent,
            TechnicalAgent, BillingAgent, ComplianceAgent, OnboardingAgent,
        ]

        for agent_cls in agents:
            agent = agent_cls()
            assert hasattr(agent, "name")
            assert hasattr(agent, "description")
            assert hasattr(agent, "system_prompt_template")
            assert hasattr(agent, "get_tool_instances")
            assert hasattr(agent, "execute")

            # Verify name is a non-empty string
            assert isinstance(agent.name, str)
            assert len(agent.name) > 0

            # Verify tools are returned
            tools = agent.get_tool_instances()
            assert isinstance(tools, list)
            assert len(tools) > 0

    def test_all_specialist_names_unique(self):
        from agents.specialists.payout import PayoutAgent
        from agents.specialists.rules import RulesAgent
        from agents.specialists.account_kyc import AccountKYCAgent
        from agents.specialists.technical import TechnicalAgent
        from agents.specialists.billing import BillingAgent
        from agents.specialists.compliance import ComplianceAgent
        from agents.specialists.onboarding import OnboardingAgent

        agents = [
            PayoutAgent(), RulesAgent(), AccountKYCAgent(),
            TechnicalAgent(), BillingAgent(), ComplianceAgent(), OnboardingAgent(),
        ]

        names = [a.name for a in agents]
        assert len(names) == len(set(names)), f"Duplicate agent names: {names}"

    def test_all_tools_have_names_and_descriptions(self):
        from agents.specialists.payout import PayoutAgent
        from agents.specialists.rules import RulesAgent
        from agents.specialists.account_kyc import AccountKYCAgent
        from agents.specialists.technical import TechnicalAgent
        from agents.specialists.billing import BillingAgent
        from agents.specialists.compliance import ComplianceAgent
        from agents.specialists.onboarding import OnboardingAgent

        agents = [
            PayoutAgent(), RulesAgent(), AccountKYCAgent(),
            TechnicalAgent(), BillingAgent(), ComplianceAgent(), OnboardingAgent(),
        ]

        for agent in agents:
            for tool in agent.get_tool_instances():
                assert hasattr(tool, "name"), f"Tool in {agent.name} missing name"
                assert hasattr(tool, "description"), f"Tool {tool.name} missing description"
                assert isinstance(tool.name, str) and len(tool.name) > 0
                assert isinstance(tool.description, str) and len(tool.description) > 0

    def test_total_tool_count(self):
        """Verify the expected number of tools across all specialists."""
        from agents.specialists.payout import PayoutAgent
        from agents.specialists.rules import RulesAgent
        from agents.specialists.account_kyc import AccountKYCAgent
        from agents.specialists.technical import TechnicalAgent
        from agents.specialists.billing import BillingAgent
        from agents.specialists.compliance import ComplianceAgent
        from agents.specialists.onboarding import OnboardingAgent

        agents = [
            PayoutAgent(), RulesAgent(), AccountKYCAgent(),
            TechnicalAgent(), BillingAgent(), ComplianceAgent(), OnboardingAgent(),
        ]

        total = sum(len(a.get_tool_instances()) for a in agents)
        # 6 + 4 + 6 + 4 + 5 + 3 + 4 = 32 tools total
        assert total == 32, f"Expected 32 tools, got {total}"


class TestOrchestratorSpecialistMap:
    def test_all_specialists_registered(self):
        from agents.orchestrator.nodes import SPECIALISTS

        expected = {"payout", "rules", "account_kyc", "technical", "billing", "compliance", "onboarding"}
        assert set(SPECIALISTS.keys()) == expected

    def test_specialist_instances_valid(self):
        from agents.orchestrator.nodes import SPECIALISTS

        for name, agent in SPECIALISTS.items():
            assert hasattr(agent, "execute"), f"{name} missing execute method"
            assert hasattr(agent, "get_tool_instances"), f"{name} missing get_tool_instances"
