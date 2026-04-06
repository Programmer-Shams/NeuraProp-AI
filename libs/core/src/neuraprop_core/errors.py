"""Exception hierarchy for NeuraProp AI."""


class NeuraPropError(Exception):
    """Base exception for all NeuraProp errors."""

    def __init__(self, message: str, details: dict | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


# --- Auth Errors ---


class AuthenticationError(NeuraPropError):
    """Invalid or missing authentication credentials."""


class AuthorizationError(NeuraPropError):
    """Authenticated but not authorized for this action."""


# --- Tenant Errors ---


class TenantNotFoundError(NeuraPropError):
    """Firm/tenant not found or inactive."""


class TenantSuspendedError(NeuraPropError):
    """Firm/tenant is suspended."""


# --- Resource Errors ---


class NotFoundError(NeuraPropError):
    """Requested resource not found."""


class ConflictError(NeuraPropError):
    """Resource conflict (duplicate, already exists, etc.)."""


class ValidationError(NeuraPropError):
    """Input validation failed."""


# --- Integration Errors ---


class IntegrationError(NeuraPropError):
    """Error communicating with external integration."""


class IntegrationTimeoutError(IntegrationError):
    """External integration timed out."""


class IntegrationAuthError(IntegrationError):
    """Authentication with external integration failed."""


# --- Agent Errors ---


class AgentError(NeuraPropError):
    """Error in agent processing."""


class AgentToolError(AgentError):
    """Error executing an agent tool."""


class AgentEscalationError(AgentError):
    """Agent cannot resolve and needs escalation."""


# --- Rate Limiting ---


class RateLimitError(NeuraPropError):
    """Rate limit exceeded."""

    def __init__(self, message: str, retry_after_seconds: int = 60):
        self.retry_after_seconds = retry_after_seconds
        super().__init__(message, {"retry_after_seconds": retry_after_seconds})
