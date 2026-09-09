"""
server.py

Thin FastAPI wrapper around the existing Chroma-based qa_engine.ask().
No changes to retriever.py, qa_engine.py, prompt_builder.py, llm.py,
response_formatter.py, or config.py — this file only exposes the
existing CLI pipeline over HTTP so the frontend can call it.

Run:
    uvicorn server:app --host 0.0.0.0 --port 8000
"""

import logging
import os
import sys

os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import config
from llm import get_llm
from qa_engine import ask
from retriever import get_embedder, load_vector_store


def setup_logging() -> None:
    os.makedirs(os.path.dirname(config.LOG_PATH) or ".", exist_ok=True)
    os.makedirs(os.path.dirname(config.QUERY_LOG_PATH) or ".", exist_ok=True)
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

app = FastAPI(title="Microsoft Rate Card API", version="1.0.0")

# Allow the frontend to call this API. If you serve the frontend from
# this same app (see the static mount below), CORS doesn't matter for
# that case — this is here for when the frontend is hosted separately.
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
# Load the existing pipeline once at startup — identical to what
# app.py does for the CLI.
# -------------------------------------------------------------------

logger.info("Validating configuration...")
config.validate_config()

logger.info("Loading knowledge base and model...")
embedder = get_embedder()
vectordb = load_vector_store(embedder)
llm = get_llm()
logger.info("Backend ready.")


@app.get("/api/status")
def status():
    try:
        count = vectordb._collection.count()
        data = vectordb._collection.get(include=["metadatas"])
        sections = {
            (m or {}).get("section")
            for m in (data.get("metadatas") or [])
            if (m or {}).get("section")
        }
        engagement_count = len(sections) or count
    except Exception:
        count = None
        engagement_count = None
    return {"status": "ok", "chunk_count": count, "engagement_count": engagement_count}


@app.post("/api/ask")
def ask_question(request: AskRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    logger.info(f"Received question: {question}")

    try:
        result = ask(question, vectordb, llm)

        chunks = [
            {
                "page": c.page,
                "chunk_id": c.chunk_id,
                "chunk_type": c.chunk_type,
                "source": c.source,
                "section": c.section,
            }
            for c in result.chunks
        ]

        # Keep the original compact frontend behavior: source chunks are
        # metadata for debugging/citations, not UI rows. The frontend
        # renders a small fact card from the answer itself. This is also
        # important for the 60-question deterministic path: it should not
        # dump the underlying Chroma/source chunk as a large table.
        is_fixed = any(c.chunk_type == "fixed_acceptance" for c in result.chunks)
        # Presales incentive questions are rate-card statements, not
        # Market A funding lookups. Tell the UI which compact card to use.
        # Classify presales by the QUESTION, not by whether the answer was
        # fixed. RAG can also answer presales questions, and those must
        # never be rendered as Amount + Market A.
        q_lower = question.lower().strip()
        # Classify from the question/answer semantics, not only an exact
        # prefix. This prevents presales rates such as "$250 per incremental
        # net new paid seat" from being rendered as Market A funding.
        answer_lower = (result.formatted.answer or "").lower()
        is_presales_question = (
            "presales incentive" in q_lower
            or "presales advisor" in q_lower
            or "biz apps presales" in q_lower
            or "presales" in q_lower and "incentive" in q_lower
        )
        is_presales_answer = (
            "incremental net new paid seat" in answer_lower
            or "high-water mark" in answer_lower
            or "hwm" in answer_lower and "paid seat" in answer_lower
        )
        answer_kind = "presales" if (is_presales_question or is_presales_answer) else "funding"
        matched_records = []

        response = {
            "answer": result.formatted.answer,
            "display_text": result.formatted.display_text,
            "source_pages": result.formatted.source_pages,
            "chunks": chunks,
            "matched_records": matched_records,
            "is_fixed_acceptance": is_fixed,
            "answer_kind": answer_kind,
            "response_time_seconds": result.response_time_seconds,
            "prompt_tokens": result.prompt_tokens,
            "completion_tokens": result.completion_tokens,
            "total_tokens": result.total_tokens,
        }

        logger.info(
            f"Question completed | {result.response_time_seconds:.2f}s | "
            f"{result.total_tokens} tokens"
        )
        return response

    except Exception as exc:
        logger.exception("Error processing question")
        raise HTTPException(status_code=500, detail=str(exc))


# -------------------------------------------------------------------
# Optional: serve a frontend from the same origin if a "frontend"
# folder is present next to this file. Set FRONTEND_DIR in .env to
# point elsewhere, or omit it entirely if you're hosting the frontend
# separately and only need the API.
# -------------------------------------------------------------------

_configured_frontend = os.getenv("FRONTEND_DIR", "")
if _configured_frontend:
    FRONTEND_DIR = os.path.abspath(_configured_frontend)
else:
    FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
    logger.info(f"Serving frontend from {FRONTEND_DIR}")
else:
    logger.info(f"No frontend directory found at {FRONTEND_DIR} — running API-only.")