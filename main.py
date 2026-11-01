"""Application entry point for the mock-data and AI-generation APIs."""

import uvicorn
from dotenv import load_dotenv

load_dotenv()  # This loads variables from the .env file into os.environ

from api.endpoints import app

__all__ = ["app"]


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
