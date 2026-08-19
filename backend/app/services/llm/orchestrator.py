from app.services.llm.gemini_provider import gemini_provider
from app.services.llm.openai_provider import openai_provider
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def get_llm_provider():
    if getattr(settings, "OPENAI_API_KEY", None):
        logger.info("Using OpenAI Provider")
        return openai_provider
    elif settings.GEMINI_API_KEY:
        logger.info("Using Gemini Provider")
        return gemini_provider
    else:
        logger.warning("No LLM API keys found, falling back to Gemini (will fail)")
        return gemini_provider

llm_orchestrator = get_llm_provider()
