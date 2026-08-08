import pytest
from unittest.mock import AsyncMock, patch
from app.models.agent import AgentStatus, AgentType, AgentVisibility, Agent
from app.services.agent.agent_service import agent_service
import uuid

@pytest.fixture
def mock_db_session():
    return AsyncMock()

@pytest.mark.asyncio
@patch('app.services.agent.agent_service.agent_repo')
@patch('app.services.agent.agent_service.agent_prompt_repo')
@patch('app.services.agent.agent_service.agent_model_config_repo')
@patch('app.services.agent.agent_service.agent_escalation_rule_repo')
async def test_create_agent_with_defaults(
    mock_escalation, mock_model, mock_prompt, mock_agent_repo, mock_db_session
):
    workspace_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    agent_data = {
        "name": "Test Support Agent",
        "description": "A support agent for testing.",
        "agent_type": AgentType.SUPPORT
    }
    
    mock_agent = Agent(id=uuid.uuid4(), name="Test Support Agent", agent_type=AgentType.SUPPORT)
    mock_agent_repo.create = AsyncMock(return_value=mock_agent)
    mock_prompt.create = AsyncMock()
    mock_model.create = AsyncMock()
    mock_escalation.create = AsyncMock()
    
    agent = await agent_service.create_agent(mock_db_session, workspace_id, user_id, agent_data)
    
    assert agent is not None
    assert agent.name == "Test Support Agent"
    assert agent.agent_type == AgentType.SUPPORT
    
    # Verify defaults were requested
    assert mock_prompt.create.called
    assert mock_model.create.called
    assert mock_escalation.create.called
