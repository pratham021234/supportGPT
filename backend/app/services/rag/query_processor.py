import re
import logging
from typing import Dict, Any, Tuple
from pydantic import BaseModel, Field

# Assuming we have gemini set up
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from app.core.config import settings

logger = logging.getLogger(__name__)

class QueryIntent(BaseModel):
    normalized_query: str = Field(description="The cleaned and normalized version of the user query.")
    intent: str = Field(description="The intent of the query, e.g., 'SUPPORT', 'TROUBLESHOOTING', 'BILLING', 'SALES', 'GENERAL'.")
    language: str = Field(description="The detected ISO 639-1 language code (e.g. 'en', 'es').")
    keywords: list[str] = Field(description="A list of 3-5 important keywords for search.")
    agent_routing: str = Field(description="The agent this should be routed to, e.g., 'TECHNICAL', 'SALES', 'HR', 'SUPPORT'.")

class QueryProcessor:
    def __init__(self):
        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0.0,
                google_api_key=settings.GEMINI_API_KEY
            ).with_structured_output(QueryIntent)
        except Exception as e:
            logger.warning(f"Failed to initialize LLM for QueryProcessor: {e}")
            self.llm = None
            
        self.prompt = PromptTemplate.from_template("""
        Analyze the following customer query and extract the intent, language, keywords, and agent routing.
        
        Rules:
        - intent: SUPPORT, TROUBLESHOOTING, BILLING, SALES, GENERAL
        - agent_routing: TECHNICAL, SALES, HR, SUPPORT
        - language: 'en', 'es', 'fr', 'de', etc.
        
        Query: {query}
        """)

    def _basic_normalize(self, query: str) -> str:
        # Remove extra whitespace and noise
        q = re.sub(r'\s+', ' ', query).strip()
        return q

    async def process_query(self, query: str) -> Dict[str, Any]:
        """
        Normalizes query, extracts intent, language, keywords, and routing.
        """
        norm_query = self._basic_normalize(query)
        
        if not self.llm:
            # Fallback
            return {
                "normalized_query": norm_query,
                "intent": "GENERAL",
                "language": "en",
                "keywords": norm_query.split()[:5],
                "agent_routing": "SUPPORT"
            }
            
        try:
            chain = self.prompt | self.llm
            result: QueryIntent = await chain.ainvoke({"query": query})
            
            return result.model_dump()
        except Exception as e:
            logger.error(f"LLM Query Processing failed: {e}")
            return {
                "normalized_query": norm_query,
                "intent": "GENERAL",
                "language": "en",
                "keywords": norm_query.split()[:5],
                "agent_routing": "SUPPORT"
            }

query_processor = QueryProcessor()
