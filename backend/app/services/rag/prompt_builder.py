import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid

from app.core.database import async_session_maker
from app.models.agent import AgentPrompt

logger = logging.getLogger(__name__)

class PromptBuilder:
    async def build_prompt(self, context: str, query: str, agent_routing: str, workspace_id: str) -> str:
        """
        Dynamically constructs the system prompt depending on agent routing.
        """
        base_instruction = "You are SupportGPT, a professional, helpful, and highly accurate enterprise AI support agent."
        
        async with async_session_maker() as db:
            try:
                # If agent_routing is a UUID, try to fetch the custom prompt
                agent_uuid = uuid.UUID(agent_routing)
                stmt = select(AgentPrompt).where(AgentPrompt.agent_id == agent_uuid, AgentPrompt.workspace_id == uuid.UUID(workspace_id))
                result = await db.execute(stmt)
                agent_prompt = result.scalar_one_or_none()
                
                if agent_prompt:
                    base_instruction = agent_prompt.system_prompt
                    if agent_prompt.behavior_rules:
                        base_instruction += f"\n\nBehavior Rules:\n{agent_prompt.behavior_rules}"
            except ValueError:
                # Fallback to defaults based on type string if not UUID
                agent_instructions = {
                    "SALES": "You are a Sales AI Assistant. Focus on features, benefits, and pricing. Be persuasive.",
                    "HR": "You are an HR Assistant. Maintain strict confidentiality and follow company policy strictly.",
                    "TECHNICAL": "You are a Technical Support Engineer. Provide step-by-step instructions, code snippets if applicable, and deep technical details.",
                    "SUPPORT": base_instruction
                }
                base_instruction = agent_instructions.get(agent_routing.upper(), base_instruction)
            except Exception as e:
                logger.error(f"Error fetching agent prompt: {str(e)}")
        
        prompt = f"""
{base_instruction}

You must answer the user's question using ONLY the provided knowledge base context.

CRITICAL RULES:
1. NEVER fabricate information, policies, or procedures.
2. If the context does not contain the answer, say "I could not find reliable information in the available knowledge base."
3. Always cite your sources using the SOURCE ID provided in the context.
4. Be concise but complete.
5. Provide a confidence_score (0.0 to 100.0) based on how well the context answers the query. If you are unsure, provide a low score.

CONTEXT:
{context}

USER QUESTION:
{query}
"""
        return prompt

prompt_builder = PromptBuilder()
