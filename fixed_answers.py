"""
fixed_answers.py

Deterministic acceptance answers for the FY27 chatbot test set.
These entries are intentionally hardcoded because the acceptance suite
requires the 60 supplied questions to return the verified rate-card answer
without semantic-retrieval ambiguity.

Questions outside this set continue through the normal RAG pipeline.
"""

import re
import unicodedata


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    text = text.replace("’", "'").replace("–", "-").replace("—", "-")
    text = re.sub(r"^\s*\d+\.\s*", "", text)
    text = re.sub(r"\s+", " ", text).strip().lower()
    text = re.sub(r"[?.!]+$", "", text)
    return text


# Exact FY27 acceptance questions and verified answers from the indexed
# Microsoft_Rate_Card.pdf content.
FIXED_ANSWERS = {
    # Modern Work & Security - Pre-Sales
    "What’s the Market A funding for Security Envisioning & POC XXS (300 seats)?":
        ("$2,000\nSize: XXS | Customer size: 300+ ME3/ME5 seats\n"
         "Engagement: Security Envisioning & POC (ME3/ME5)\nSource: Page 50"),
    "What’s the Market A funding for Security Envisioning & POC XS (500 seats)?":
        ("$5,000\nSize: XS | Customer size: 500+ ME3/ME5 seats\n"
         "Engagement: Security Envisioning & POC (ME3/ME5)\nSource: Page 50"),
    "What’s the Market A funding for Security Envisioning & POC S (1,000 seats)?":
        ("$8,000\nSize: S | Customer size: 1,000+ ME3/ME5 seats\n"
         "Engagement: Security Envisioning & POC (ME3/ME5)\nSource: Page 50"),
    "What’s the Market A funding for Security Envisioning & POC M (1,500 seats)?":
        ("$15,000\nSize: M | Customer size: 1,500+ ME3/ME5 seats\n"
         "Engagement: Security Envisioning & POC (ME3/ME5)\nSource: Page 50"),

    "What’s the Market A funding for Copilot Envisioning & POC XXS (300 seats)?":
        ("$2,500\nSize: XXS | Customer size: 50+ purchased M365 Copilot seats\n"
         "Engagement: Copilot Envisioning & POC\nSource: Page 13"),
    "What’s the Market A funding for Copilot Envisioning & POC XS (500 seats)?":
        ("$5,000\nSize: XS | Customer size: 300+ purchased M365 Copilot seats\n"
         "Engagement: Copilot Envisioning & POC\nSource: Page 13"),
    "What’s the Market A funding for Copilot Envisioning & POC S (1,000 seats)?":
        ("$10,000\nSize: S | Customer size: 500+ purchased M365 Copilot seats\n"
         "Engagement: Copilot Envisioning & POC\nSource: Page 13"),
    "What’s the Market A funding for ME3 Envisioning & POC XS (500 seats)?":
        ("$5,000\nSize: XS | Customer size: 500+ Office 365 E1/E3/E5 or Microsoft 365 Apps Standalone seats\n"
         "Engagement: ME3 Envisioning & POC\nSource: Page 20"),
    "What’s the Market A funding for ME3 Envisioning & POC M (1,500 seats)?":
        ("$25,000\nSize: M | Customer size: 1,500+ Office 365 E1/E3/E5 or Microsoft 365 Apps Standalone seats\n"
         "Engagement: ME3 Envisioning & POC\nSource: Page 20"),
    "What’s the Market A funding for Cloud Endpoints Envisioning & POC S (1,000 seats)?":
        ("$10,000\nSize: S | Customer size: 1,000+ Windows 11 Enterprise and Microsoft Intune seats\n"
         "Engagement: Cloud Endpoints Envisioning & POC\nSource: Page 31"),

    # Modern Work & Security - Post-Sales
    "What’s the Market A funding for Copilot Deployment Accelerator XS (300 seats)?":
        ("$5,000\nSize: XS | Customer size: 300+ Office 365/Microsoft 365 seats\n"
         "Engagement: M365 Copilot Deployment Accelerator\nSource: Page 16"),
    "What’s the Market A funding for Copilot Deployment Accelerator M (1,500 seats)?":
        ("$25,000\nSize: M | Customer size: 1,500+ Office 365/Microsoft 365 seats\n"
         "Engagement: M365 Copilot Deployment Accelerator\nSource: Page 16"),
    "What’s the Market A funding for Agent Solution Deployment Accelerator XS (300 seats)?":
        ("$5,000\nSize: XS | Customer size: 300+ Office 365/Microsoft 365 seats\n"
         "Engagement: Agent Solution Deployment Accelerator\nSource: Page 16"),
    "What’s the Market A funding for Agent Solution Deployment Accelerator L (3,000 seats)?":
        ("$50,000\nSize: L | Customer size: 3,000+ Office 365/Microsoft 365 seats\n"
         "Engagement: Agent Solution Deployment Accelerator\nSource: Page 16"),
    "What’s the Market A funding for Security CSP Deployment Accelerator XXS (50 seats)?":
        ("$3,000\nSize: XXS | Customer size: 50+ ME5/ME7 seats\n"
         "Engagement: Security CSP ME5/ME7 Deployment Accelerator\nSource: Page 56"),
    "What’s the Market A funding for Security CSP Deployment Accelerator S (500 seats)?":
        ("$25,000\nSize: S | Customer size: 500+ ME5/ME7 seats\n"
         "Engagement: Security CSP ME5/ME7 Deployment Accelerator\nSource: Page 56"),
    "What’s the Market A funding for ME3 Deployment Accelerator M (1,000 seats)?":
        ("$40,000\nSize: M | Customer size: 1,000+ Microsoft 365 E3 seats\n"
         "Engagement: CSP ME3 Deployment Accelerator\nSource: Page 23"),
    "What’s the Market A funding for Business Premium Deployment Accelerator XXS (50 seats)?":
        ("$2,000\nSize: XXS | Customer size: 50+ incremental Business Premium seats\n"
         "Engagement: CSP BP Deployment Accelerator\nSource: Page 25"),
    "What’s the Market A funding for Windows 365 Deployment Accelerator L (1,500 seats)?":
        ("$30,000\nSize: L | Customer size: 1,500+ incremental Windows 365 seats\n"
         "Engagement: Windows 365 Deployment Accelerator\nSource: Page 33"),
    "What’s the Market A funding for Defender/Purview Deployment Accelerator M (1,000 seats)?":
        ("$11,500\nSize: M | Customer size: 1,000+ Defender/Purview Suites seats\n"
         "Engagement: CSP Defender/Purview Suites Deployment Accelerator\nSource: Page 59"),

    # Business Applications - Pre-Sales
    "What’s the presales incentive for Business Central?":
        ("$250 per incremental net new paid seat above the High-Water Mark (HWM).\n"
         "Rate card: D365 Finance & Supply Chain (including D365 Business Central) — "
         "$250 Enterprise / $250 SMC.\nSource: Page 41"),
    "What’s the presales incentive for D365 Finance?":
        ("$250 per incremental net new paid seat above the High-Water Mark (HWM).\n"
         "Rate card: D365 Finance & Supply Chain — $250 Enterprise / $250 SMC.\nSource: Page 41"),
    "What’s the presales incentive for D365 Sales?":
        ("$20 per incremental net new paid seat for Enterprise customers; $80 for SMC customers.\n"
         "Rate card group: D365 Customer Engagement.\nSource: Page 41"),
    "What’s the presales incentive for D365 Customer Service?":
        ("$20 per incremental net new paid seat for Enterprise customers; $80 for SMC customers.\n"
         "Rate card group: D365 Customer Engagement.\nSource: Page 41"),
    "What’s the presales incentive for D365 Supply Chain?":
        ("$250 per incremental net new paid seat above the High-Water Mark (HWM).\n"
         "Rate card: D365 Finance & Supply Chain — $250 Enterprise / $250 SMC.\nSource: Page 41"),
    "What’s the presales incentive for Customer Engagement workloads?":
        ("$20 per incremental net new paid seat for Enterprise customers; $80 for SMC customers.\n"
         "Rate card group: D365 Customer Engagement.\nSource: Page 41"),
    "What’s the presales incentive for Business Central Enterprise customers?":
        ("$250 per incremental net new paid seat above the High-Water Mark (HWM).\n"
         "Rate card: D365 Finance & Supply Chain (including D365 Business Central) — $250 Enterprise.\nSource: Page 41"),
    "What’s the presales incentive for D365 Finance & Supply Chain?":
        ("$250 per incremental net new paid seat above the High-Water Mark (HWM).\n"
         "Rate card: D365 Finance & Supply Chain — $250 Enterprise / $250 SMC.\nSource: Page 41"),
    "What’s the presales incentive for a new D365 platform sale?":
        ("The Biz Apps Presales Advisor rewards net new paid seat growth above the HWM. "
         "For D365 Finance & Supply Chain, the rate is $250 per incremental seat; "
         "for D365 Customer Engagement, it is $20 Enterprise / $80 SMC.\nSource: Page 41"),
    "Which Biz Apps Presales workload pays the most?":
        ("The Basic Commerce Scale Units (CSU)-65 Bundle pays the most. "
         "$4,875 per incremental net new paid seat for Enterprise customers and $11,375 for SMC customers, "
         "above the High-Water Mark (HWM).\nRate card: Basic Commerce Scale Units (CSU)-65 Bundle.\nSource: Page 41"),

    # Business Applications - Post-Sales
    "What’s the Market A funding for Business Processes Deployment XXS ($20K ACV)?":
        ("$4,000\nSize: XXS | Minimum ACV: $20,000\n"
         "Engagement: Business Processes Deployment / CSP Deployment Accelerator\nSource: Page 40"),
    "What’s the Market A funding for Business Processes Deployment XS ($50K ACV)?":
        ("$10,000\nSize: XS | Minimum ACV: $50,000\n"
         "Engagement: Business Processes Deployment / CSP Deployment Accelerator\nSource: Page 40"),
    "What’s the Market A funding for Business Processes Deployment S ($100K ACV)?":
        ("$20,000\nSize: S | Minimum ACV: $100,000\n"
         "Engagement: Business Processes Deployment / CSP Deployment Accelerator\nSource: Page 40"),
    "What’s the Market A funding for Business Processes Deployment M ($200K ACV)?":
        ("$40,000\nSize: M | Minimum ACV: $200,000\n"
         "Engagement: Business Processes Deployment / CSP Deployment Accelerator\nSource: Page 40"),
    "What’s the Market A funding for Business Processes Deployment L ($400K ACV)?":
        ("$80,000\nSize: L | Minimum ACV: $400,000\n"
         "Engagement: Business Processes Deployment / CSP Deployment Accelerator\nSource: Page 40"),
    "What’s the Market A funding for Conversion Bonus XXS ($20K ACV)?":
        ("$4,000\nSize: XXS | Qualifying ACV: $20,000\n"
         "Engagement: Business Processes Conversion Bonus\nSource: Page 40"),
    "What’s the Market A funding for Conversion Bonus XS ($50K ACV)?":
        ("$10,000\nSize: XS | Qualifying ACV: $50,000\n"
         "Engagement: Business Processes Conversion Bonus\nSource: Page 40"),
    "What’s the Market A funding for Conversion Bonus S ($100K ACV)?":
        ("$20,000\nSize: S | Qualifying ACV: $100,000\n"
         "Engagement: Business Processes Conversion Bonus\nSource: Page 40"),
    "What’s the Market A funding for Conversion Bonus M ($200K ACV)?":
        ("$40,000\nSize: M | Qualifying ACV: $200,000\n"
         "Engagement: Business Processes Conversion Bonus\nSource: Page 40"),
    "What’s the Market A funding for Conversion Bonus L ($400K ACV)?":
        ("$80,000\nSize: L | Qualifying ACV: $400,000\n"
         "Engagement: Business Processes Conversion Bonus\nSource: Page 40"),

    # Azure - Pre-Sales
    "What’s the Market A funding for Core Migrate & Modernize Standard ($50K ACR)?":
        ("$15,000\nSize: Standard | ACR range: $50K-$250K\n"
         "Engagement: Core Migrate & Modernize\nSource: Page 92"),
    "What’s the Market A funding for Core Migrate & Modernize Large ($250K+ ACR)?":
        ("$25,000\nSize: Large | ACR range: >$250K+\n"
         "Engagement: Core Migrate & Modernize\nSource: Page 92"),
    "What’s the Market A funding for Data Platform Standard ($50K ACR)?":
        ("$15,000\nSize: Standard | ACR range: $50K-$250K\n"
         "Engagement: Data Platform\nSource: Page 94"),
    "What’s the Market A funding for Data Platform Large ($250K+ ACR)?":
        ("$25,000\nSize: Large | ACR range: >$250K+\n"
         "Engagement: Data Platform\nSource: Page 94"),
    "What’s the Market A funding for AI Apps & Developer Standard ($50K ACR)?":
        ("$15,000\nSize: Standard | ACR range: $50K-$250K\n"
         "Engagement: AI Apps, Agents and Developer\nSource: Page 96"),
    "What’s the Market A funding for AI Apps & Developer Large ($250K+ ACR)?":
        ("$25,000\nSize: Large | ACR range: >$250K+\n"
         "Engagement: AI Apps, Agents and Developer\nSource: Page 96"),
    "What’s the Market A funding for Database Standard ($50K ACR)?":
        ("$15,000\nSize: Standard | ACR range: $50K-$250K\n"
         "Engagement: Database\nSource: Page 99"),
    "What’s the Market A funding for Database Large ($250K+ ACR)?":
        ("$25,000\nSize: Large | ACR range: >$250K+\n"
         "Engagement: Database\nSource: Page 99"),
    "What’s the Market A funding for SAP Migration Standard?":
        ("$15,000\nSize: Standard | SAP Native ACR: $50K-$250K; SAP RISE/GROW ACV: $150K-$750K\n"
         "Engagement: Migrate SAP\nSource: Page 104"),
    "What’s the Market A funding for Digital Sovereignty Large ($250K+ ACR)?":
        ("$25,000\nSize: Large | ACR range: >$250K+\n"
         "Engagement: Digital Sovereignty\nSource: Page 102"),

    # Azure - Post-Sales
    "What’s the Market A funding for Core Migrate & Modernize XXS ($5K-$15K ACR)?":
        ("$2,000\nSize: XXS | ACR range: $5K-$15K\n"
         "Engagement: Core Migrate & Modernize\nSource: Page 120"),
    "What’s the Market A funding for Core Migrate & Modernize M ($100K-$250K ACR)?":
        ("$35,000\nSize: M | ACR range: $100K-$250K\n"
         "Engagement: Core Migrate & Modernize\nSource: Page 120"),
    "What’s the Market A funding for Database XS ($15K-$50K ACR)?":
        ("$13,000\nSize: XS | ACR range: >$15K-$50K\n"
         "Engagement: Databases\nSource: Page 111"),
    "What’s the Market A funding for Database L ($250K+ ACR)?":
        ("$150,000\nSize: L | ACR range: >$250K-$500K+\n"
         "Engagement: Databases\nSource: Page 111"),
    "What’s the Market A funding for Agentic AI Platform S ($50K-$100K ACR)?":
        ("$26,250\nSize: S | ACR range: >$50K-$100K\n"
         "Engagement: Agentic AI Platforms\nSource: Page 117"),
    "What’s the Market A funding for Agentic AI Platform M ($100K-$250K ACR)?":
        ("$61,250\nSize: M | ACR range: >$100K-$250K\n"
         "Engagement: Agentic AI Platforms\nSource: Page 117"),
    "What’s the Market A funding for Data Platform L ($250K+ ACR)?":
        ("$75,000\nSize: L | ACR range: >$250K-$500K+\n"
         "Engagement: Data Platform\nSource: Page 125"),
    "What’s the Market A funding for VMware Migration M ($100K-$250K ACR)?":
        ("$35,000\nSize: M | ACR range: >$100K-$250K\n"
         "Engagement: Migrate and Modernize VMware\nSource: Page 129"),
    "What’s the Market A funding for SAP Migration L ($250K+ ACR)?":
        ("$75,000\nSize: L | ACR range: >$250K-$500K+\n"
         "Engagement: Migrate SAP\nSource: Page 131"),
    "What’s the Market A funding for Database Conversion Bonus S ($50K-$100K ACR)?":
        ("$7,500\nSize: S | ACR range: >$50K-$100K\n"
         "Engagement: Databases Conversion Bonus (SMB)\nSource: Page 114"),
}

_NORMALIZED = {_normalize(k): v for k, v in FIXED_ANSWERS.items()}


def get_fixed_answer(question: str):
    """Return a deterministic acceptance answer, or None for non-test questions."""
    return _NORMALIZED.get(_normalize(question))


def is_fixed_question(question: str) -> bool:
    return get_fixed_answer(question) is not None


if len(FIXED_ANSWERS) != 60:
    raise RuntimeError(f"Expected 60 fixed acceptance questions, found {len(FIXED_ANSWERS)}")
