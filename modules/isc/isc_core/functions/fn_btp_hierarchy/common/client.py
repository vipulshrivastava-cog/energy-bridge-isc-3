"""CDF client helpers — mirrors DQV ensure_client_name + workflow-injected client."""

from __future__ import annotations

import os
from typing import Any

from cognite.client import AsyncCogniteClient, ClientConfig, CogniteClient
from cognite.client.credentials import OAuthClientCredentials

PACKAGE_CLIENT_NAME = "fn-btp-hierarchy"
_CLIENT_NAME_HEADER = "x-cdp-app"


def apply_secret(secrets: dict[str, str] | None) -> None:
    """Map function secrets into env for OAuth fallback (local / direct calls)."""
    if secrets and "btp-hier-secret" in secrets:
        os.environ["CDF_CLIENT_SECRET"] = secrets["btp-hier-secret"]


def ensure_client_name(client: Any, client_name: str = PACKAGE_CLIENT_NAME) -> Any:
    """Best-effort SDK client name (DQV cognite_data_quality._client_name pattern)."""
    try:
        config = getattr(client, "config", None)
        if config is not None:
            config.client_name = client_name
        http_client = getattr(client, "_http_client", None)
        if http_client is not None:
            internal_config = getattr(http_client, "_config", None)
            headers = getattr(internal_config, "headers", None)
            if headers is not None and hasattr(headers, "__setitem__"):
                headers[_CLIENT_NAME_HEADER] = client_name
            session = getattr(http_client, "_session", None) or getattr(http_client, "session", None)
            session_headers = getattr(session, "headers", None)
            if session_headers is not None and hasattr(session_headers, "__setitem__"):
                session_headers[_CLIENT_NAME_HEADER] = client_name
    except Exception:
        pass
    return client


def _build_client_from_env() -> AsyncCogniteClient:
    cluster = os.environ["CDF_CLUSTER"]
    return AsyncCogniteClient(
        ClientConfig(
            client_name=PACKAGE_CLIENT_NAME,
            project=os.environ["CDF_PROJECT"],
            cluster=cluster,
            credentials=OAuthClientCredentials(
                token_url=(
                    f"https://login.microsoftonline.com/{os.environ['IDP_TENANT_ID']}"
                    "/oauth2/v2.0/token"
                ),
                client_id=os.environ["CDF_CLIENT_ID"],
                client_secret=os.environ["CDF_CLIENT_SECRET"],
                scopes=[f"https://{cluster}.cognitedata.com/.default"],
            ),
        )
    )


def resolve_async_client(client: CogniteClient | None) -> AsyncCogniteClient:
    """Prefer workflow-injected sync client config; fall back to env OAuth."""
    if client is not None:
        ensure_client_name(client)
        return AsyncCogniteClient(client.config)
    return _build_client_from_env()
