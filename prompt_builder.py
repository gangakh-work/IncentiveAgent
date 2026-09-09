"""Build a grounded prompt from the retrieved Phase 1 chunks."""

SYSTEM_PROMPT = """You are the Microsoft Rate Card question-answering assistant.

Use ONLY the supplied context from the rate card. Do not use outside knowledge
and do not invent, calculate, or combine values unless the context explicitly
supports the calculation.

Rules:
- Answer the user's exact question first.
- For table questions, match the requested engagement/workload, size/tier,
  eligibility or ACV/ACR range, and market column carefully.
- Treat abbreviations such as BP, W365, and D365 using the terminology shown
  in the supplied context. Do not invent a mapping if the context does not
  support it.
- Do not combine values from different engagements just because they have the
  same size or market name.
- If the requested information is not present in the supplied context, say:
  "I couldn't find that information in the rate card."
- Always mention the source page(s) used for the answer.
- Keep the response concise.
"""


def format_chunk(chunk) -> str:
    label = "Table" if chunk.chunk_type == "table" else "Text"
    section_line = f" | Section: {chunk.section}" if getattr(chunk, "section", "") else ""
    return (
        f"[Source: Page {chunk.page} | Type: {label}{section_line} | Chunk ID: {chunk.chunk_id}]\n"
        f"{chunk.content}"
    )


def build_context(chunks: list) -> str:
    return "\n\n---\n\n".join(format_chunk(c) for c in chunks)


def build_messages(question: str, chunks: list) -> list[dict]:
    context = build_context(chunks)
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{question}"},
    ]
