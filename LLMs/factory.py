import os
import logging
from .open_ai import AzureChat
from .open_router import OpenRouterLLM

logger = logging.getLogger(__name__)

def get_llm_instance(config):
    """Selects and initializes the LLM based on a config module."""
    provider = getattr(config, "LLM_PROVIDER", "OPEN_ROUTER").upper()
    if provider == "AZURE":
        logger.info("Using Azure OpenAI LLM.")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        if not api_key or not endpoint:
            raise ValueError("AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT must be set.")
        return AzureChat(
            model_id=config.AZURE_MODEL_ID,
            api_key=api_key,
            azure_endpoint=endpoint,
            system_message=config.SYSTEM_MESSAGE,
            temperature=config.TEMPERATURE,
            top_p=config.TOP_P,
        )
    elif provider == "OPEN_ROUTER":
        logger.info("Using OpenRouter LLM.")
        api_key = os.getenv("OPEN_ROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPEN_ROUTER_API_KEY must be set.")
        return OpenRouterLLM(
            api_key=api_key,
            model_id=config.OPEN_ROUTER_MODEL_ID,
            system_message=config.SYSTEM_MESSAGE,
            temperature=config.TEMPERATURE,
            top_p=config.TOP_P,
        )
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider}")
