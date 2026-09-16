"""
server.py

FastAPI wrapper around the existing Chroma-based qa_engine.ask().

Project structure:

    project-root/
    ├── index.html       # Landing page
    ├── chat.html        # Chat page
    ├── logo.png         # Logo
    ├── server.py
    ├── config.py
    ├── qa_engine.py
    ├── retriever.py
    ├── requirements.txt
    └── db/
"""

import logging
import os
import sys
from pathlib import Path

# -------------------------------------------------------------------
# SQLite fix for Chroma on Linux/Azure
# This must happen before importing qa_engine/retriever/Chroma.
# -------------------------------------------------------------------

if sys.platform.startswith("linux"):
    import pysqlite3

    sys.modules["sqlite3"] = pysqlite3

os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

import config
from llm import get_llm
from qa_engine import ask
from retriever import get_embedder, load_vector_store


# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

INDEX_HTML = BASE_DIR / "index.html"
CHAT_HTML = BASE_DIR / "chat.html"
LOGO_PNG = BASE_DIR / "logo.png"


# -------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------

def setup_logging() -> None:
    os.makedirs(
        os.path.dirname(config.LOG_PATH) or ".",
        exist_ok=True,
    )

    os.makedirs(
        os.path.dirname(config.QUERY_LOG_PATH) or ".",
        exist_ok=True,
    )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(config.LOG_PATH),
            logging.StreamHandler(sys.stdout),
        ],
    )

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.getLogger("backoff").setLevel(logging.ERROR)


setup_logging()
logger = logging.getLogger("server")


# -------------------------------------------------------------------
# FastAPI application
# -------------------------------------------------------------------

app = FastAPI(
    title="Microsoft Rate Card API",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str


# -------------------------------------------------------------------
# Load existing pipeline once at startup
# -------------------------------------------------------------------

logger.info("Validating configuration...")
config.validate_config()

logger.info("Loading knowledge base and model...")

embedder = get_embedder()
vectordb = load_vector_store(embedder)
llm = get_llm()

logger.info("Backend ready.")


# -------------------------------------------------------------------
# API endpoints
# -------------------------------------------------------------------

@app.get("/api/status")
def status():
    try:
        count = vectordb._collection.count()

        data = vectordb._collection.get(
            include=["metadatas"]
        )

        sections = {
            (metadata or {}).get("section")
            for metadata in (data.get("metadatas") or [])
            if (metadata or {}).get("section")
        }

        engagement_count = len(sections) or count

    except Exception:
        count = None
        engagement_count = None

    return {
        "status": "ok",
        "chunk_count": count,
        "engagement_count": engagement_count,
    }


@app.post("/api/ask")
def ask_question(request: AskRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    logger.info("Received question: %s", question)

    try:
        result = ask(
            question,
            vectordb,
            llm,
        )

        chunks = [
            {
                "page": chunk.page,
                "chunk_id": chunk.chunk_id,
                "chunk_type": chunk.chunk_type,
                "source": chunk.source,
                "section": chunk.section,
            }
            for chunk in result.chunks
        ]

        is_fixed = any(
            chunk.chunk_type == "fixed_acceptance"
            for chunk in result.chunks
        )

        question_lower = question.lower().strip()
        answer_lower = (
            result.formatted.answer or ""
        ).lower()

        is_presales_question = (
            "presales incentive" in question_lower
            or "presales advisor" in question_lower
            or "biz apps presales" in question_lower
            or (
                "presales" in question_lower
                and "incentive" in question_lower
            )
        )

        is_presales_answer = (
            "incremental net new paid seat" in answer_lower
            or "high-water mark" in answer_lower
            or (
                "hwm" in answer_lower
                and "paid seat" in answer_lower
            )
        )

        answer_kind = (
            "presales"
            if (
                is_presales_question
                or is_presales_answer
            )
            else "funding"
        )

        response = {
            "answer": result.formatted.answer,
            "display_text": result.formatted.display_text,
            "source_pages": result.formatted.source_pages,
            "chunks": chunks,
            "matched_records": [],
            "is_fixed_acceptance": is_fixed,
            "answer_kind": answer_kind,
            "response_time_seconds": result.response_time_seconds,
            "prompt_tokens": result.prompt_tokens,
            "completion_tokens": result.completion_tokens,
            "total_tokens": result.total_tokens,
        }

        logger.info(
            "Question completed | %.2fs | %s tokens",
            result.response_time_seconds,
            result.total_tokens,
        )

        return response

    except Exception as exc:
        logger.exception("Error processing question")

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# -------------------------------------------------------------------
# Frontend routes
# -------------------------------------------------------------------

@app.get("/", include_in_schema=False)
def landing_page():
    """
    Displays the landing page.
    """
    if not INDEX_HTML.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Landing page not found: {INDEX_HTML}",
        )

    return FileResponse(
        str(INDEX_HTML),
        media_type="text/html",
    )


@app.get("/chat.html", include_in_schema=False)
def chat_page():
    """
    Displays the chat page.
    """
    if not CHAT_HTML.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Chat page not found: {CHAT_HTML}",
        )

    return FileResponse(
        str(CHAT_HTML),
        media_type="text/html",
    )


@app.get("/logo.png", include_in_schema=False)
def logo():
    """
    Serves the logo image.
    """
    if not LOGO_PNG.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Logo not found: {LOGO_PNG}",
        )

    return FileResponse(
        str(LOGO_PNG),
        media_type="image/png",
    )