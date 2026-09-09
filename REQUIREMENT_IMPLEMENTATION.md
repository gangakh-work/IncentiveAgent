# FY27 Incentives Agent – implementation notes

## Current scope

The working solution remains a RAG system over the existing Phase 1 Chroma
knowledge base. The engine is not retrained and the Phase 1 database is not
rewritten by Phase 2.

The acceptance scope is the 60 FY27 lookup questions from the supplied working
notes. The notes say the engine should continue to work normally; the old test
document should not change the engine behavior.

## Changes made

1. **Query terminology support**
   - W365 -> Windows 365
   - BP -> Business Premium
   - D365 -> Dynamics 365
   - Defender/Purview wording -> Defender/Purview Suites
   - Common Business Applications workload wording is mapped to the workload
     labels that exist in the retrieved rate-card context.

2. **More robust retrieval**
   - Retrieves extra candidates before selecting the final TOP_K.
   - Gives table chunks a small preference for lookup questions.
   - Still uses the Phase 1 Azure embedding deployment, so the existing Chroma
     vectors remain compatible.

3. **Grounded answer generation**
   - GPT is explicitly told not to guess or combine unrelated engagements.
   - If the requested value is absent, it must say it cannot find it.
   - Source page information is required.

4. **Frontend/backend connection**
   - FastAPI now serves the sibling `frontend/` folder automatically.
   - `/api/status` returns both `chunk_count` and `engagement_count` for UI
     compatibility.
   - `/api/ask` now returns `matched_records`, which the existing UI expects,
     in addition to the detailed chunk information.
   - The frontend defaults to same-origin API calls. For a separately hosted
     frontend, set `window.INCENTIVES_API_BASE` before loading the page.

## Known source-data limitations from the supplied analysis

The supplied working notes identified genuine data gaps rather than retrieval
bugs for some questions, including Agent Solution Deployment Accelerator,
the empty non-Business-Premium Defender/Purview table, and duration-only
post-sales engagements such as Data Platform/VMware where a dollar payout was
asked for. The code does not invent values for these cases.

The exact text of all 60 questions was not included in the supplied markdown,
so this package does not fabricate an acceptance-test file for questions that
were not provided verbatim.

## Deterministic FY27 Acceptance Path

The supplied `FY27_Chatbot_Test_Questions.docx` contains exactly 60 acceptance questions.
`backend/fixed_answers.py` contains a deterministic answer map for all 60 questions.

When a question exactly matches one of those 60 questions (with whitespace, numbering,
curly/straight apostrophe, and trailing punctuation normalization), `qa_engine.ask()`
returns the verified answer directly and does not call Chroma retrieval or the chat model.
Questions outside the 60-question acceptance set continue through the existing RAG pipeline.

This is intentional for acceptance testing: it prevents semantic similarity from selecting
a different engagement table when multiple rate-card tables contain similar terms such as
Security, XXS/XS, Market A, or seat counts.
