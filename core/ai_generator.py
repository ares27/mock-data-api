"""Generate natural-language-driven mock records with Gemini Flash."""

import json
import os
from typing import Any

from google import genai
from google.genai import types

GEMINI_MODEL = "gemini-2.5-flash"
_client: genai.Client | None = None


class GeminiConfigurationError(RuntimeError):
    """Raised when the Gemini API key is not configured."""


def _get_client() -> genai.Client:
    global _client

    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise GeminiConfigurationError(
                "GEMINI_API_KEY is not configured."
            )
        _client = genai.Client(api_key=api_key)

    return _client


def generate_ai_dataset(prompt: str, count: int = 5) -> list[dict[str, Any]]:
    """Generate exactly ``count`` fictional records matching ``prompt``."""
    if not prompt.strip():
        raise ValueError("prompt must not be empty")
    if not 1 <= count <= 1000:
        raise ValueError("count must be between 1 and 1000")

    response = _get_client().models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=(
                "Generate fictional mock data only. Return a JSON array containing "
                "exactly the requested number of records. Each record must be a "
                "JSON object. Use realistic, contextually appropriate field names "
                "and values. Return no prose or markdown."
            ),
            response_mime_type="application/json",
            temperature=0.4,
        ),
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response")

    records = json.loads(response.text)
    if (
        not isinstance(records, list)
        or len(records) != count
        or any(not isinstance(record, dict) for record in records)
    ):
        raise ValueError(
            f"Gemini response must be a JSON array of exactly {count} objects"
        )

    return records
