"""
response_formatter.py

Responsibility: turn the raw LLM answer + retrieved chunks into a
clean, user-facing response with clearly listed source pages.
"""

from dataclasses import dataclass, field


@dataclass
class FormattedResponse:
    answer: str
    source_pages: list = field(default_factory=list)
    display_text: str = ""


def format_response(answer: str, chunks: list) -> FormattedResponse:
    """
    Build the final display text:

        <answer>

        Source: Page X, Page Y
    """
    # De-duplicate pages while preserving retrieval order
    seen = set()
    source_pages = []
    for c in chunks:
        if c.page not in seen:
            seen.add(c.page)
            source_pages.append(c.page)

    answer = answer.strip()

    if source_pages:
        pages_str = ", ".join(f"Page {p}" for p in source_pages)
        display_text = f"{answer}\n\nSource: {pages_str}"
    else:
        display_text = answer

    return FormattedResponse(
        answer=answer,
        source_pages=source_pages,
        display_text=display_text,
    )
