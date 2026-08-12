import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch

from app.services.agent.agent_builder_service import agent_builder_service
from app.services.agent.prompt_version_service import prompt_version_service
from app.services.agent.knowledge_assignment_service import knowledge_assignment_service
from app.services.agent.agent_router import multi_agent_router
from app.services.rag.graph import agent_selection_node
from app.services.rag.state import RAGState

@pytest.mark.asyncio
async def test_agent_creation(db_session: AsyncSession):
    # Test AgentBuilderService
    agent = await agent_builder_service.create_agent(
        db_session, 
        workspace_id="ws1", 
        user_id="user1", 
        agent_data={"name": "Support Agent", "agent_type": "SUPPORT"}
    )
    assert agent.name == "Support Agent"
    assert agent.agent_type == "SUPPORT"

@pytest.mark.asyncio
async def test_knowledge_assignment(db_session: AsyncSession):
    # Test KnowledgeAssignmentService
    scope = await knowledge_assignment_service.assign_document(db_session, "agent1", "doc1")
    assert scope.agent_id == "agent1"
    assert scope.document_id == "doc1"
    
    scopes = await knowledge_assignment_service.get_agent_knowledge(db_session, "agent1")
    assert len(scopes) > 0

@pytest.mark.asyncio
async def test_agent_versioning(db_session: AsyncSession):
    # Mocking since db_session relies on actual agent existing
    with patch("app.repositories.agent_repo.agent_repo.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = AsyncMock(id="agent1", status="DRAFT")
        with patch("app.repositories.agent_repo.agent_prompt_repo.get_by_agent", new_callable=AsyncMock) as mock_prompt:
            mock_prompt.return_value = AsyncMock(system_prompt="Test")
            with patch("app.repositories.agent_repo.agent_version_repo.create", new_callable=AsyncMock) as mock_create:
                with patch("app.repositories.agent_repo.agent_repo.update", new_callable=AsyncMock) as mock_update:
                    await prompt_version_service.publish_agent_version(db_session, "agent1", "user1")
                    mock_create.assert_called_once()
                    mock_update.assert_called_once()

@pytest.mark.asyncio
async def test_agent_selection_node(db_session: AsyncSession):
    # Test that LangGraph assigns the right agent via the node
    state = RAGState(workspace_id="ws1", user_id="user1", query="help me with API", metadata={})
    
    with patch("app.services.agent.agent_router.multi_agent_router.route_query", new_callable=AsyncMock) as mock_route:
        mock_route.return_value = AsyncMock(id="agent_tech")
        
        result = await agent_selection_node(state)
        
        assert "metadata" in result
        assert result["metadata"]["agent_id"] == "agent_tech"

