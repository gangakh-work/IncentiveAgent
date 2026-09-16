"""
app.py

Phase 2 CLI entrypoint.

    python app.py

Ask questions interactively. Type 'exit' or 'quit' to stop.

This is deliberately the simplest possible interface. Once this works
reliably, wrapping qa_engine.ask() in a FastAPI POST /ask endpoint (or
a Teams bot) is a thin layer on top — the engine itself doesn't change.
"""

import logging
import os
import sys

# Disable Chroma's anonymous telemetry before importing anything that
# initializes a Chroma client. Prevents noisy SSL retry warnings against
# us.i.posthog.com on machines with corporate proxy/cert interception,
# and avoids the wasted retry delay on every question.
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

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
    # Keep third-party libs quieter in the console
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.getLogger("backoff").setLevel(logging.ERROR)


def main() -> None:
    setup_logging()
    logger = logging.getLogger("app")

    config.validate_config()

    logger.info("Loading knowledge base and model...")
    embedder = get_embedder()
    vectordb = load_vector_store(embedder)
    llm = get_llm()
    logger.info("Ready.")

    print("\nMicrosoft Rate Card — Question Answering Engine")
    print("Type your question, or 'exit' to quit.\n")

    while True:
        try:
            question = input("Ask: > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            print("Exiting.")
            break

        try:
            result = ask(question, vectordb, llm)
        except Exception as e:
            logger.exception(f"Error answering question: {e}")
            print(f"\nSomething went wrong: {e}\n")
            continue

        print(f"\n{result.formatted.display_text}\n")
        print(
            f"[{result.response_time_seconds:.2f}s | "
            f"{result.total_tokens} tokens | "
            f"{len(result.chunks)} chunks retrieved]\n"
        )


if __name__ == "__main__":
    main()
