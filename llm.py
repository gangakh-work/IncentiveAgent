"""
llm.py

Responsibility: build the AzureChatOpenAI client. Nothing else —
no prompt logic, no retrieval logic lives here.
"""

import logging

from langchain_openai import AzureChatOpenAI

import config

logger = logging.getLogger(__name__)


def get_llm() -> AzureChatOpenAI:
    """Build and return the Azure OpenAI chat client for gpt-4.1-mini."""
    logger.info(
        f"Initializing AzureChatOpenAI "
        f"(deployment={config.AZURE_CHAT_DEPLOYMENT}, temp={config.TEMPERATURE})"
    )

    # Newer models (GPT-5, o-series, and other reasoning models) reject the
    # legacy `max_tokens` param and require `max_completion_tokens` instead.
    # They also frequently only support the default temperature (1) and
    # reject explicit temperature=0. config.py controls this via
    # USE_MAX_COMPLETION_TOKENS / FIX_TEMPERATURE so you don't have to
    # edit code when swapping models.
    kwargs = {
        "azure_endpoint": config.AZURE_OPENAI_ENDPOINT,
        "api_key": config.AZURE_OPENAI_API_KEY,
        "api_version": config.AZURE_OPENAI_API_VERSION,
        "azure_deployment": config.AZURE_CHAT_DEPLOYMENT,
    }

    if config.USE_MAX_COMPLETION_TOKENS:
        kwargs["max_completion_tokens"] = config.MAX_TOKENS
    else:
        kwargs["max_tokens"] = config.MAX_TOKENS

    if not config.FIX_TEMPERATURE:
        kwargs["temperature"] = config.TEMPERATURE
    # else: don't pass temperature to the constructor at all. Newer
    # langchain-openai versions require temperature to be a float if
    # passed (rejecting None), but still default it to 0.7 internally
    # and send it on every call. So instead of setting it, we strip it
    # from the client's model_kwargs/params after construction.

    llm = AzureChatOpenAI(**kwargs)

    if config.FIX_TEMPERATURE:
        # Remove temperature from whichever internal attribute this
        # langchain-openai version uses to store default request params,
        # so the field is omitted from the outgoing API payload entirely.
        if hasattr(llm, "temperature"):
            object.__setattr__(llm, "temperature", None)
        if hasattr(llm, "model_kwargs") and isinstance(llm.model_kwargs, dict):
            llm.model_kwargs.pop("temperature", None)

    return llm
