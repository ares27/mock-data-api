"""API key authentication dependencies."""

import hmac
import os
from typing import Annotated

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_api_key(
    api_key: Annotated[str | None, Security(api_key_header)],
) -> str:
    """Validate the caller's API key against the configured master key."""
    master_api_key = os.environ.get("MASTER_API_KEY")
    if (
        not api_key
        or not master_api_key
        or not hmac.compare_digest(
            api_key.encode("utf-8"),
            master_api_key.encode("utf-8"),
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API key",
        )

    return api_key
