"""FastAPI application and endpoints for mock-data generation."""

import logging
from typing import Any

from fastapi import Depends, FastAPI, HTTPException
from google.genai.errors import APIError
from pydantic import BaseModel, Field

from core.ai_generator import (
    GeminiConfigurationError,
    generate_ai_dataset,
)
from core.auth import get_api_key
from core.generator import generate_mock_dataset

logger = logging.getLogger(__name__)
app = FastAPI(title="Dynamic Schema Mock Data Generator")


class GenerateRequest(BaseModel):
    schema: dict[str, str] = Field(min_length=1)
    count: int = Field(default=10, ge=1, le=1000)


class AIGenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=4000)
    count: int = Field(default=5, ge=1, le=1000)

    model_config = {"str_strip_whitespace": True}


@app.get("/")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/generate")
def generate(request: GenerateRequest) -> dict[str, list[dict[str, Any]]]:
    try:
        records = generate_mock_dataset(request.schema, request.count)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return {"data": records}


@app.post("/ai-generate")
def generate_with_ai(
    request: AIGenerateRequest,
    api_key: str = Depends(get_api_key),
) -> dict[str, list[dict[str, Any]]]:
    try:
        records = generate_ai_dataset(request.prompt, request.count)
    except GeminiConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except APIError as exc:
        logger.exception("Gemini request failed")
        raise HTTPException(
            status_code=502,
            detail="The AI generation provider could not complete the request.",
        ) from exc

    return {"data": records}
