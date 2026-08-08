import logging
import json
import google.generativeai as genai
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from app.core.config import settings
from app.repositories.analytics_repo import knowledge_gap_repo, GapStatus

logger = logging.getLogger(__name__)

class BusinessInsightsEngine:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None

    async def generate_knowledge_recommendations(self, db: AsyncSession, workspace_id: str) -> List[Dict[str, Any]]:
        """
        Analyzes the open Knowledge Gaps using Gemini and generates actionable recommendations.
        """
        gaps = await knowledge_gap_repo.get_by_workspace(db, workspace_id)
        open_gaps = [g for g in gaps if g.status == GapStatus.OPEN]
        
        if not open_gaps:
            return []
            
        # Sort by occurrences (impact) and take top 20
        open_gaps = sorted(open_gaps, key=lambda x: x.occurrences, reverse=True)[:20]
        
        if not self.model:
            # Fallback if no LLM
            return [{
                "title": "Address High-Volume Gap",
                "description": f"Customers frequently ask: '{open_gaps[0].query}'.",
                "action": "Create documentation to cover this topic.",
                "impact": "HIGH"
            }]
            
        gap_data = "\n".join([f"- Query: '{g.query}' (Occurrences: {g.occurrences}, Escalations: {g.escalation_count}, Avg Confidence: {g.confidence_average})" for g in open_gaps])
        
        prompt = f"""
        You are a Principal Business Intelligence AI. Analyze the following knowledge gaps (questions where the AI had low confidence or escalated).
        
        Gaps:
        {gap_data}
        
        Identify 3 critical missing documentation pieces or systemic issues.
        Return ONLY a JSON array of objects with the following schema:
        {{
            "title": "Short title of the issue",
            "description": "What customers are asking and why it's a problem",
            "action": "Specific recommendation (e.g., 'Create a guide for X')",
            "impact": "HIGH, MEDIUM, or LOW"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            content = response.text.replace("```json", "").replace("```", "").strip()
            recommendations = json.loads(content)
            return recommendations
        except Exception as e:
            logger.error(f"InsightsEngine LLM error: {e}")
            return []

insights_engine = BusinessInsightsEngine()
