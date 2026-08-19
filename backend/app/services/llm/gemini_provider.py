import logging
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from app.services.llm.llm_provider import LLMProvider
from app.services.rag.state import AnswerOutput
from app.core.config import settings

logger = logging.getLogger(__name__)

class GeminiProvider(LLMProvider):
    def __init__(self):
        try:
            # We use Gemini 2.5 Flash as requested.
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0.2,
                google_api_key=settings.GEMINI_API_KEY
            )
            self.structured_llm = self.llm.with_structured_output(AnswerOutput)
        except Exception as e:
            logger.warning(f"Failed to initialize GeminiProvider: {e}")
            self.llm = None
            self.structured_llm = None

    async def generate_structured_answer(self, prompt: str, context: str, query: str) -> Dict[str, Any]:
        if not self.structured_llm:
            return {
                "answer": "Gemini API Key is missing. I cannot generate an answer.",
                "citations": [],
                "confidence_score": 0.0
            }
            
        prompt_template = PromptTemplate.from_template(prompt)
        
        try:
            chain = prompt_template | self.structured_llm
            result: AnswerOutput = await chain.ainvoke({
                "context": context,
                "query": query
            })
            
            return {
                "answer": result.answer,
                "citations": result.citations,
                "confidence_score": result.confidence_score
            }
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return {
                "answer": "An error occurred during generation.",
                "citations": [],
                "confidence_score": 0.0
            }

    async def astream_structured_answer(self, prompt: str, context: str, query: str):
        if not self.structured_llm:
            yield {
                "answer": "Gemini API Key is missing. I cannot generate an answer.",
                "citations": [],
                "confidence_score": 0.0
            }
            return
            
        prompt_template = PromptTemplate.from_template(prompt)
        chain = prompt_template | self.structured_llm
        
        try:
            async for chunk in chain.astream({
                "context": context,
                "query": query
            }):
                # Yield partial AnswerOutput if supported, else final
                if hasattr(chunk, "model_dump"):
                    yield chunk.model_dump()
                else:
                    yield chunk
        except Exception as e:
            logger.error(f"Gemini streaming failed: {e}")
            yield {
                "answer": "An error occurred during generation.",
                "citations": [],
                "confidence_score": 0.0
            }

gemini_provider = GeminiProvider()
