"""
config.py

Central configuration for Phase 2 (Question Answering Engine).
All secrets are loaded from environment variables (.env file).
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Azure OpenAI settings
# ---------------------------------------------------------------------------
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-06-01")

# Embedding deployment MUST match whatever Phase 1 used to build the DB —
# querying with a different embedding model than the one used to build
# the index produces meaningless similarity scores.
AZURE_EMBEDDING_DEPLOYMENT = os.getenv(
    "AZURE_EMBEDDING_DEPLOYMENT", "text-embedding-3-small"
)

# Chat completion deployment name (your Azure deployment of gpt-4.1-mini,
# or whatever chat model you deployed).
AZURE_CHAT_DEPLOYMENT = os.getenv("AZURE_CHAT_DEPLOYMENT", "gpt-4.1-mini")

# ---------------------------------------------------------------------------
# Chroma settings (must match Phase 1)
# ---------------------------------------------------------------------------
CHROMA_PATH = os.getenv("CHROMA_PATH", "db")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "rate_card")

# ---------------------------------------------------------------------------
# Retrieval / generation settings
# ---------------------------------------------------------------------------
TOP_K = int(os.getenv("TOP_K", 5))
TEMPERATURE = float(os.getenv("TEMPERATURE", 0))
# GPT-5/o-series reasoning models spend part of this budget on internal
# reasoning tokens before writing the visible answer, so this needs to be
# noticeably higher than you'd use for a classic chat model or you'll get
# an empty response.
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 2000))

# Newer models (GPT-5, o-series) require max_completion_tokens instead of
# max_tokens, and often reject a non-default temperature. Set these to
# "true" in .env when using such a model.
USE_MAX_COMPLETION_TOKENS = os.getenv("USE_MAX_COMPLETION_TOKENS", "true").lower() == "true"
FIX_TEMPERATURE = os.getenv("FIX_TEMPERATURE", "true").lower() == "true"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_PATH = os.getenv("LOG_PATH", "logs/phase2.log")
QUERY_LOG_PATH = os.getenv("QUERY_LOG_PATH", "logs/queries.jsonl")


def validate_config() -> None:
    """Fail fast and loud if required secrets are missing."""
    missing = []
    if not AZURE_OPENAI_ENDPOINT:
        missing.append("AZURE_OPENAI_ENDPOINT")
    if not AZURE_OPENAI_API_KEY:
        missing.append("AZURE_OPENAI_API_KEY")

    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}. "
            f"Create a .env file (see .env.example)."
        )

    import os as _os
    if not _os.path.isdir(CHROMA_PATH) or not _os.listdir(CHROMA_PATH):
        raise EnvironmentError(
            f"No Chroma database found at '{CHROMA_PATH}'. "
            f"Run Phase 1 (main.py) first, or copy its db/ folder here."
        )
