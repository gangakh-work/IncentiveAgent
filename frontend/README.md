# Incentives Assistant — Frontend

Two static pages, no build step, no login:

- `index.html` — landing page (hero, feature cards, how-it-works, closing CTA)
- `chat.html` — the actual Q&A interface

Design: neon purple/green on black, glass panels, glowing borders, Bricolage
Grotesque display font + Figtree body font, Tailwind via CDN. Adapted from a
reference KM Portal design — same layout language and interaction patterns,
new palette and copy for this project, no login/auth (not needed here).

## Running it

Just open `index.html` in a browser, or serve the folder:

```bash
python3 -m http.server 8000
```

Click "Open assistant" / "Enter the assistant" to get to `chat.html`.

## Wiring to your Phase 2 backend

The chat page expects two endpoints. Point `API_BASE` in `chat.html`
(currently `""`, i.e. same origin) at your API if it's hosted elsewhere.

### `GET /api/status`

```json
{ "engagement_count": 57 }
```

Used for the sidebar status pill ("Live · 57 engagements loaded"). Any
non-200 response or network failure shows "API not connected" and reveals
the amber "Not connected" banner.

### `POST /api/ask`

Request:
```json
{ "question": "What is the Market A payment for XXS under CSP ME3 Deployment Accelerator?" }
```

Response:
```json
{
  "answer": "The Market A payment for XXS is $2,500...",
  "matched_records": [
    {
      "engagement": "Frontier Accelerate for AI-Ready Productivity: CSP ME3 Deployment Accelerator",
      "page_ref": 23,
      "row": {
        "Size": "XXS",
        "Customer Eligibility": "50+ incremental Microsoft 365 E3 Seats",
        "Minimum Hours": "13",
        "Market A": "$2,500",
        "Market B": "$1,875",
        "Market C": "$1,250"
      }
    }
  ]
}
```

This maps directly to `qa_engine.QAResult` from the Phase 2 backend:
- `answer` = `result.formatted.answer`
- `matched_records` = `[{engagement: r.engagement, page_ref: r.page_ref, row: r.row} for r in result.matched_records]`

`matched_records` can be an empty list — the UI just shows the answer text
with no source card underneath (used for "I couldn't find that" responses).

### Wiring example (FastAPI, sketch)

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class AskRequest(BaseModel):
    question: str

@app.get("/api/status")
def status():
    return {"engagement_count": len(excel_data.engagement_names)}

@app.post("/api/ask")
def ask_endpoint(req: AskRequest):
    result = ask(req.question, excel_data, llm)
    return {
        "answer": result.formatted.answer,
        "matched_records": [
            {"engagement": r.engagement, "page_ref": r.page_ref, "row": r.row}
            for r in result.matched_records
        ],
    }

app.mount("/", StaticFiles(directory="frontend", html=True), name="static")
```

## What's client-side only (no backend needed)

- Saved chats and recent questions persist in `localStorage`, per-browser.
- "Clear" only clears the current view, not saved history.
- No auth, no session, no server-side state at all — this is intentional
  per the brief (no login required for this tool).

## Customizing

- Palette: `neon.purple` / `neon.green` in each file's `tailwind.config`.
- Suggested questions on the welcome screen: `data-suggest` buttons in
  `chat.html`, easy to swap for your own example queries.
- Copy: all landing page and welcome-screen text is plain HTML, no
  templating — just edit directly.
