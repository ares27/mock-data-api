# Dynamic Schema Mock Data Generator API

A lightweight FastAPI service for generating mock datasets in two ways:

- **Schema-based generation** uses Faker to populate fields of known types.
- **Natural-language generation** uses Google's Gemini Flash model to create
  fictional, contextually appropriate records.

## Architecture

- `main.py` exposes the FastAPI application and starts Uvicorn when run directly.
- `api/endpoints.py` defines the health check and generation endpoints, including
  request validation and error responses.
- `core/generator.py` maps schema field types to Faker providers.
- `core/ai_generator.py` calls Gemini through the official `google-genai` SDK
  and validates its JSON output.

## Setup

Use Python 3.10 or later. From the project directory, install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Set both `GEMINI_API_KEY` and `MASTER_API_KEY` before using `/ai-generate`.
`GEMINI_API_KEY` is used by Google GenAI; `MASTER_API_KEY` is the caller's
shared API key and must be sent in the `X-API-Key` header. The AI endpoint
returns `403 Forbidden` when the header is missing or does not match the
configured master key. The health check and Faker endpoint do not require
either key.

For local development, create a `.env` file in the project directory:

```dotenv
GEMINI_API_KEY=your-google-ai-api-key
MASTER_API_KEY=your-local-master-key
```

The included master key is for local testing only. Configure a unique,
high-entropy `MASTER_API_KEY` in production and do not commit `.env` files.
`main.py` loads the project `.env` file when starting the application.

PowerShell:

```powershell
$env:GEMINI_API_KEY = "your-api-key"
$env:MASTER_API_KEY = "your-local-master-key"
```

Command Prompt:

```bat
set GEMINI_API_KEY=your-api-key
set MASTER_API_KEY=your-local-master-key
```

Then start the API:

```powershell
python main.py
```

Or use Uvicorn's development reload:

```powershell
uvicorn main:app --reload
```

The service listens at `http://127.0.0.1:8000`. Interactive API documentation
is available at `http://127.0.0.1:8000/docs`.

## Endpoints

### Health check

```http
GET /
```

Example response:

```json
{ "status": "ok" }
```

### Generate from a schema

```http
POST /generate
Content-Type: application/json
```

The schema maps each output field name to a supported type: `name`, `email`,
`address`, `company`, `date`, `phone`, `text`, `integer`, or `price`. The
record count must be between 1 and 1,000 (default: 10).

```json
{
  "schema": {
    "full_name": "name",
    "email": "email",
    "company": "company",
    "annual_revenue": "price"
  },
  "count": 3
}
```

Both generation endpoints return records inside a `data` array:

```json
{
  "data": [
    {
      "full_name": "Jordan Smith",
      "email": "jordan@example.com",
      "company": "Example Group",
      "annual_revenue": 482.75
    }
  ]
}
```

### Generate from a natural-language prompt

```http
POST /ai-generate
Content-Type: application/json
X-API-Key: your-local-master-key
```

Provide a prompt and a record count between 1 and 1,000 (default: 5). Prompts
are limited to 4,000 characters. In Swagger UI (`/docs`), use the **Authorize**
button to enter the configured key for the `X-API-Key` security scheme.

```json
{
  "prompt": "Generate user profiles for a South African logistics company",
  "count": 5
}
```

The response contains a `data` array of JSON objects, with fields and values
chosen to fit the prompt. The model is instructed to return fictional records
as JSON only.

## Errors

- Invalid request bodies or record counts return `422 Unprocessable Entity`.
- A missing or invalid `X-API-Key` on `/ai-generate` returns
  `403 Forbidden`.
- An unset `GEMINI_API_KEY` returns `503 Service Unavailable` from
  `/ai-generate`.
- Invalid or empty model output returns `502 Bad Gateway`.
