# Phase 2 — Question Answering Engine

Runtime CLI that answers questions against the Chroma knowledge base built by Phase 1.
The source PDF is never touched again — this phase only reads the existing `db/`.

## Pipeline

```
Question -> embed -> similarity search (top K) -> prompt builder (context + metadata)
         -> Azure GPT-4.1-mini -> response formatter -> answer + source pages
```

Retrieved chunks carry their metadata (page, chunk type, chunk id) into the
prompt as labeled blocks, so the model can distinguish table content from
prose and cite the correct page instead of guessing.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# edit .env: Azure endpoint/key, embedding deployment (must match Phase 1),
# chat deployment (gpt-4.1-mini)
```

Copy Phase 1's persisted database into this project:

```bash
cp -r ../phase1/db/* db/
```

`CHROMA_PATH` and `CHROMA_COLLECTION_NAME` in `.env` must match what Phase 1 used.

## Run

```bash
python app.py
```

```
Ask: > What is the Market B payment for XXS?

Market B payment for XXS is $1500.

Source: Page 125

[1.84s | 612 tokens | 5 chunks retrieved]
```

Every query is logged to `logs/queries.jsonl` (one JSON object per line:
question, retrieved chunks, source pages, token usage, response time) and
`logs/phase2.log` has the full run log.

## Module responsibilities

| File | Responsibility |
|---|---|
| `config.py` | Load & validate settings from `.env` |
| `retriever.py` | Load Phase 1's Chroma DB; embed question; similarity search |
| `prompt_builder.py` | Build system prompt + metadata-labeled context + question |
| `llm.py` | Azure GPT-4.1-mini chat client only |
| `qa_engine.py` | Orchestrates retrieve -> prompt -> LLM -> format; logs each query |
| `response_formatter.py` | Turn raw answer + chunks into "answer + Source: Page X" |
| `app.py` | CLI loop |

## Next steps

Once the CLI is verified reliable, wrap `qa_engine.ask(question, vectordb, llm)`
in a FastAPI `POST /ask` endpoint — the engine itself doesn't need to change.
From there, a Teams bot is just another thin caller of the same function.

## Current FY27 RAG behavior

The current Phase 2 application uses the existing Phase 1 Chroma database and
Azure OpenAI embedding deployment. It does not rebuild or modify the database.
The retriever adds query-side terminology support for the FY27 acceptance set,
including BP/Business Premium, W365/Windows 365, D365/Dynamics 365 and common
Business Applications workload wording. It retrieves extra candidates and then
keeps the configured top K results, with a small preference for table chunks.

The answer prompt is grounded: the model must use only retrieved rate-card
context, must not invent missing values, and must state source pages.

For local use, start the API from the `backend` folder:

```bash
uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

The API also serves `../frontend` automatically, so open:

`http://127.0.0.1:8000/`

No separate frontend server is required for local testing.

## FY27 acceptance questions

The project includes `../FY27_Chatbot_Test_Questions.docx` and
`fixed_answers.py`. All 60 supplied FY27 acceptance questions have a
deterministic answer path. Exact normalized matches are answered from the
verified rate-card answer map; all other questions continue through the
normal Chroma + Azure OpenAI RAG pipeline.
