import logging
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from app.services.llm.llm_provider import LLMProvider
from app.services.rag.state import AnswerOutput
from app.core.config import settings

logger = logging.getLogger(__name__)

class OpenAIProvider(LLMProvider):
    def __init__(self):
        try:
            # Check if OPENAI_API_KEY exists on settings, default to None if missing
            api_key = getattr(settings, "OPENAI_API_KEY", None)
            
            if api_key:
                self.llm = ChatOpenAI(
                    model="gpt-4o-mini",
                    temperature=0.2,
                    api_key=api_key
                )
                self.structured_llm = self.llm.with_structured_output(AnswerOutput)
            else:
                self.llm = None
                self.structured_llm = None
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAIProvider: {e}")
            self.llm = None
            self.structured_llm = None

    async def generate_structured_answer(self, prompt: str, context: str, query: str) -> Dict[str, Any]:
        if not self.structured_llm:
            return {
                "answer": "OpenAI API Key is missing. I cannot generate an answer.",
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
            logger.error(f"OpenAI generation failed: {e}")
            return {
                "answer": "An error occurred during generation.",
                "citations": [],
                "confidence_score": 0.0
            }

    async def astream_structured_answer(self, prompt: str, context: str, query: str):
        if not self.structured_llm:
            yield {
                "answer": "OpenAI API Key is missing. I cannot generate an answer.",
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
                if hasattr(chunk, "model_dump"):
                    yield chunk.model_dump()
                else:
                    yield chunk
        except Exception as e:
            logger.error(f"OpenAI streaming failed: {e}")
            yield {
                "answer": "An error occurred during generation.",
                "citations": [],
                "confidence_score": 0.0
            }

openai_provider = OpenAIProvider()
