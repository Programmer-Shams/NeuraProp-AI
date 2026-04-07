"""Universal API connector — allows firms to map custom API endpoints to NeuraProp actions.

Firms configure their own integrations via the admin dashboard by defining:
1. Base URL + auth headers
2. Action mappings (NeuraProp action → HTTP method + path + body template)
3. Response mappings (JSONPath extraction from API response)
"""

from typing import Any

import httpx
from jinja2 import Template

from neuraprop_core.logging import get_logger

logger = get_logger(__name__)


class ActionMapping:
    """Maps a NeuraProp action to an HTTP API call."""

    def __init__(
        self,
        action_name: str,
        method: str,
        path_template: str,
        body_template: str | None = None,
        headers: dict[str, str] | None = None,
        response_mapping: dict[str, str] | None = None,
    ):
        self.action_name = action_name
        self.method = method.upper()
        self.path_template = Template(path_template)
        self.body_template = Template(body_template) if body_template else None
        self.headers = headers or {}
        self.response_mapping = response_mapping or {}


class UniversalConnector:
    """Generic API connector that can be configured for any REST API.

    Firms define action mappings in the admin dashboard:

    Example mapping for "get_balance":
    {
        "action_name": "get_balance",
        "method": "GET",
        "path_template": "/api/accounts/{{ login }}/balance",
        "response_mapping": {
            "balance": "$.data.balance",
            "equity": "$.data.equity",
            "currency": "$.data.currency"
        }
    }
    """

    name = "Universal API"
    description = "Configurable connector for custom REST API integrations"

    def __init__(
        self,
        base_url: str,
        auth_headers: dict[str, str],
        action_mappings: list[dict[str, Any]],
        timeout: float = 15.0,
    ):
        self.base_url = base_url
        self.auth_headers = auth_headers
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None
        self._mappings: dict[str, ActionMapping] = {}

        for mapping in action_mappings:
            am = ActionMapping(
                action_name=mapping["action_name"],
                method=mapping.get("method", "GET"),
                path_template=mapping["path_template"],
                body_template=mapping.get("body_template"),
                headers=mapping.get("headers"),
                response_mapping=mapping.get("response_mapping"),
            )
            self._mappings[am.action_name] = am

    async def initialize(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={**self.auth_headers, "Content-Type": "application/json"},
            timeout=self.timeout,
        )
        logger.info("universal_connector_initialized", base_url=self.base_url)

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()

    async def execute_action(
        self,
        action_name: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a mapped action with the given parameters.

        Renders the path and body templates with params,
        makes the HTTP request, and extracts response fields.
        """
        if not self._client:
            raise RuntimeError("Universal connector not initialized")

        mapping = self._mappings.get(action_name)
        if not mapping:
            return {"success": False, "error": f"Unknown action: {action_name}"}

        # Render templates
        path = mapping.path_template.render(**params)
        headers = {**mapping.headers}

        kwargs: dict[str, Any] = {}
        if mapping.body_template and mapping.method in ("POST", "PUT", "PATCH"):
            body_str = mapping.body_template.render(**params)
            # Try to parse as JSON, fall back to string
            import json
            try:
                kwargs["json"] = json.loads(body_str)
            except json.JSONDecodeError:
                kwargs["content"] = body_str

        try:
            response = await self._client.request(
                mapping.method, path, headers=headers, **kwargs,
            )
            response.raise_for_status()
            data = response.json()

            # Apply response mapping if defined
            if mapping.response_mapping:
                result = {}
                for key, json_path in mapping.response_mapping.items():
                    result[key] = _extract_jsonpath(data, json_path)
                return {"success": True, "data": result}

            return {"success": True, "data": data}

        except httpx.HTTPStatusError as e:
            logger.error("universal_action_http_error", action=action_name, status=e.response.status_code)
            return {"success": False, "error": f"HTTP {e.response.status_code}", "status_code": e.response.status_code}
        except Exception as e:
            logger.exception("universal_action_error", action=action_name)
            return {"success": False, "error": str(e)}

    def list_actions(self) -> list[str]:
        return list(self._mappings.keys())

    async def health_check(self) -> dict[str, Any]:
        """Test connectivity to the configured API."""
        if not self._client:
            return {"status": "not_initialized"}
        try:
            response = await self._client.get("/")
            return {"status": "ok", "response_code": response.status_code}
        except Exception as e:
            return {"status": "error", "error": str(e)}


def _extract_jsonpath(data: Any, path: str) -> Any:
    """Simple JSONPath-like extraction.

    Supports: $.key, $.nested.key, $.array[0], $.array[*].field
    """
    if not path.startswith("$."):
        return data

    parts = path[2:].split(".")
    current = data

    for part in parts:
        if current is None:
            return None

        # Handle array indexing: key[0]
        if "[" in part:
            key, idx_str = part.split("[", 1)
            idx_str = idx_str.rstrip("]")

            if key:
                current = current.get(key) if isinstance(current, dict) else None
            if current is None:
                return None

            if idx_str == "*":
                # Return all elements
                return current if isinstance(current, list) else [current]

            try:
                idx = int(idx_str)
                current = current[idx] if isinstance(current, list) and len(current) > idx else None
            except (ValueError, IndexError):
                return None
        else:
            current = current.get(part) if isinstance(current, dict) else None

    return current
