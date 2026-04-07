"""Tests for neuraprop_core.errors — exception hierarchy."""

from neuraprop_core.errors import (
    NeuraPropError,
    AuthenticationError,
    AuthorizationError,
    TenantNotFoundError,
    TenantSuspendedError,
    NotFoundError,
    ConflictError,
    ValidationError,
    IntegrationError,
    IntegrationTimeoutError,
    IntegrationAuthError,
    AgentError,
    AgentToolError,
    AgentEscalationError,
    RateLimitError,
)


class TestErrorHierarchy:
    def test_all_inherit_from_base(self):
        errors = [
            AuthenticationError, AuthorizationError,
            TenantNotFoundError, TenantSuspendedError,
            NotFoundError, ConflictError, ValidationError,
            IntegrationError, IntegrationTimeoutError, IntegrationAuthError,
            AgentError, AgentToolError, AgentEscalationError,
            RateLimitError,
        ]
        for cls in errors:
            err = cls("test message")
            assert isinstance(err, NeuraPropError)
            assert isinstance(err, Exception)

    def test_message_attribute(self):
        err = AuthenticationError("bad token")
        assert err.message == "bad token"
        assert str(err) == "bad token"

    def test_details_default_empty(self):
        err = NotFoundError("not found")
        assert err.details == {}

    def test_details_preserved(self):
        err = ValidationError("invalid", details={"field": "email"})
        assert err.details["field"] == "email"

    def test_integration_errors_inherit(self):
        assert issubclass(IntegrationTimeoutError, IntegrationError)
        assert issubclass(IntegrationAuthError, IntegrationError)

    def test_agent_errors_inherit(self):
        assert issubclass(AgentToolError, AgentError)
        assert issubclass(AgentEscalationError, AgentError)

    def test_rate_limit_has_retry_after(self):
        err = RateLimitError("too fast", retry_after_seconds=30)
        assert err.retry_after_seconds == 30
        assert err.details["retry_after_seconds"] == 30
