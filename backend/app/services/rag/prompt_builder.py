import logging

logger = logging.getLogger(__name__)

class PromptBuilder:
    def build_prompt(self, context: str, query: str, agent_type: str, workspace_id: str) -> str:
        """
        Dynamically constructs the system prompt depending on agent routing.
        """
        agent_instructions = {
            "SALES": "You are a Sales AI Assistant. Focus on features, benefits, and pricing. Be persuasive.",
            "HR": "You are an HR Assistant. Maintain strict confidentiality and follow company policy strictly.",
            "TECHNICAL": "You are a Technical Support Engineer. Provide step-by-step instructions, code snippets if applicable, and deep technical details.",
            "SUPPORT": "You are SupportGPT, a professional, helpful, and highly accurate enterprise AI support agent."
        }
        
        base_instruction = agent_instructions.get(agent_type.upper(), agent_instructions["SUPPORT"])
        
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
