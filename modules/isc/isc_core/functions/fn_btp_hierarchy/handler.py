"""
CDF Function entrypoint — keep this module minimal for Classic runtime validation.

Implementation lives in handlers/ and common/ (DQV _function_code layout).
"""

from __future__ import annotations


def handle(data=None, client=None, secrets=None, function_call_info=None):
    """Dispatch on hierarchy_type. Allowed args: data, client, secrets, function_call_info."""
    from common.client import apply_secret, ensure_client_name
    from handler_dispatch import dispatch

    ensure_client_name(client)
    apply_secret(secrets)
    return dispatch(data, function_call_info, client)
