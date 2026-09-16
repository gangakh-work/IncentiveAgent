"""Retriever for the existing Phase 1 Chroma knowledge base.

Phase 2 is read-only: it embeds the user's question with the SAME Azure
OpenAI embedding deployment used during Phase 1, searches Chroma, and
returns the most relevant chunks with their metadata.

A small query-expansion layer is included for the FY27 acceptance questions.
It handles common Microsoft abbreviations without changing the stored data.
"""

import logging
import re
from dataclasses import dataclass

from langchain_chroma import Chroma
from langchain_openai import AzureOpenAIEmbeddings

import config

logger = logging.getLogger(__name__)


# These are query-side aliases only. The Phase 1 database is never modified.
ALIASES = {
    "w365": "Windows 365",
    "windows365": "Windows 365",
    "bp": "Business Premium",
    "businesspremium": "Business Premium",
    "d365": "Dynamics 365",
    "dynamics365": "Dynamics 365",
    "defender/purview": "Defender/Purview Suites",
    "defender purview": "Defender/Purview Suites",
    "business central enterprise": "Business Central Enterprise",
}


def expand_query(question: str) -> str:
    """Add known aliases to the query so semantic search sees both names."""
    expanded = question.strip()
    additions = []
    lower = expanded.lower()

    for alias, canonical in ALIASES.items():
        if re.search(rf"(?<!\w){re.escape(alias)}(?!\w)", lower):
            additions.append(canonical)

    if additions:
        unique = list(dict.fromkeys(additions))
        expanded += "\nKnown terminology: " + ", ".join(unique)

    # Common workload wording from the 60-question acceptance set.
    workload_hints = {
        "d365 sales": "D365 Customer Engagement",
        "d365 customer service": "D365 Customer Engagement",
        "customer engagement workloads": "D365 Customer Engagement",
        "d365 finance": "D365 Finance & Supply Chain",
        "d365 supply chain": "D365 Finance & Supply Chain",
        "d365 business central": "D365 Finance & Supply Chain",
    }
    for phrase, canonical in workload_hints.items():
        if phrase in lower:
            expanded += f"\nWorkload mapping: {canonical}"
            break

    return expanded


@dataclass
class RetrievedChunk:
    content: str
    page: int
    chunk_id: int
    chunk_type: str
    source: str
    section: str
    score: float


def get_embedder() -> AzureOpenAIEmbeddings:
    """Create the same embedding client/deployment used by Phase 1."""
    return AzureOpenAIEmbeddings(
        azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
        api_key=config.AZURE_OPENAI_API_KEY,
        api_version=config.AZURE_OPENAI_API_VERSION,
        azure_deployment=config.AZURE_EMBEDDING_DEPLOYMENT,
    )


def load_vector_store(embedder: AzureOpenAIEmbeddings = None) -> Chroma:
    """Open the persisted Phase 1 Chroma collection in read-only use."""
    embedder = embedder or get_embedder()
    logger.info(
        "Loading Chroma DB (path=%s, collection=%s)",
        config.CHROMA_PATH,
        config.CHROMA_COLLECTION_NAME,
    )
    return Chroma(
        persist_directory=config.CHROMA_PATH,
        embedding_function=embedder,
        collection_name=config.CHROMA_COLLECTION_NAME,
    )


def retrieve(question: str, vectordb: Chroma, top_k: int = None) -> list[RetrievedChunk]:
    """Retrieve relevant chunks using semantic search plus query expansion."""
    top_k = top_k or config.TOP_K
    expanded = expand_query(question)
    # Retrieve a few extra candidates. This gives the prompt better coverage
    # when several tables contain the same generic words (e.g. Market A/B/C).
    candidate_k = max(top_k * 2, 10)
    logger.info("Retrieving top %s candidates for question: %r", candidate_k, question)

    results = vectordb.similarity_search_with_score(expanded, k=candidate_k)

    # Prefer table chunks for lookup-style questions when their content is
    # similarly relevant. The actual values still come only from Chroma.
    def rank(item):
        doc, score = item
        table_bonus = -0.08 if doc.metadata.get("chunk_type") == "table" else 0.0
        return score + table_bonus

    results.sort(key=rank)
    results = results[:top_k]

    retrieved = []
    for doc, score in results:
        meta = doc.metadata or {}
        retrieved.append(
            RetrievedChunk(
                content=doc.page_content,
                page=int(meta.get("page", -1)),
                chunk_id=int(meta.get("chunk_id", -1)),
                chunk_type=meta.get("chunk_type", "unknown"),
                source=meta.get("source", "unknown"),
                section=meta.get("section", ""),
                score=float(score),
            )
        )

    logger.info("Retrieved %s chunks, pages=%s", len(retrieved), [r.page for r in retrieved])
    return retrieved
