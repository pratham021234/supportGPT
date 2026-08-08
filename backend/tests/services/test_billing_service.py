import pytest
import uuid
from unittest.mock import AsyncMock, patch
from app.models.billing import Plan, Subscription, SubscriptionStatus
from app.services.billing.billing_service import plan_enforcement_service, stripe_service

@pytest.fixture
def mock_db_session():
    return AsyncMock()

@pytest.mark.asyncio
@patch('app.services.billing.billing_service.subscription_repo')
@patch('app.services.billing.billing_service.plan_repo')
@patch('app.services.billing.billing_service.usage_record_repo')
async def test_plan_enforcement_allow(mock_usage_repo, mock_plan_repo, mock_sub_repo, mock_db_session):
    workspace_id = str(uuid.uuid4())
    
    mock_sub = Subscription(workspace_id=uuid.UUID(workspace_id), plan_id=uuid.uuid4())
    mock_plan = Plan(limits={"agents": 5})
    
    mock_sub_repo.get_by_workspace = AsyncMock(return_value=mock_sub)
    mock_plan_repo.get = AsyncMock(return_value=mock_plan)
    mock_usage_repo.get_usage_sum = AsyncMock(return_value=2.0) # Used 2, asking for 1, total 3 (limit 5)
    
    # Should not throw exception
    result = await plan_enforcement_service.check_limit(mock_db_session, workspace_id, "agents", 1.0)
    assert result is True

@pytest.mark.asyncio
@patch('app.services.billing.billing_service.subscription_repo')
@patch('app.services.billing.billing_service.plan_repo')
@patch('app.services.billing.billing_service.usage_record_repo')
async def test_plan_enforcement_deny(mock_usage_repo, mock_plan_repo, mock_sub_repo, mock_db_session):
    workspace_id = str(uuid.uuid4())
    
    mock_sub = Subscription(workspace_id=uuid.UUID(workspace_id), plan_id=uuid.uuid4())
    mock_plan = Plan(limits={"agents": 5})
    
    mock_sub_repo.get_by_workspace = AsyncMock(return_value=mock_sub)
    mock_plan_repo.get = AsyncMock(return_value=mock_plan)
    mock_usage_repo.get_usage_sum = AsyncMock(return_value=5.0) # Used 5, asking for 1, total 6 (limit 5)
    
    with pytest.raises(plan_enforcement_service.LimitExceededError):
        await plan_enforcement_service.check_limit(mock_db_session, workspace_id, "agents", 1.0)

@pytest.mark.asyncio
@patch('app.services.billing.billing_service.subscription_repo')
@patch('app.services.billing.billing_service.event_bus')
async def test_stripe_webhook_checkout(mock_event_bus, mock_sub_repo, mock_db_session):
    workspace_id = str(uuid.uuid4())
    
    payload = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "client_reference_id": workspace_id,
                "subscription": "sub_123",
                "customer": "cus_123"
            }
        }
    }
    
    mock_sub = Subscription(workspace_id=uuid.UUID(workspace_id), status=SubscriptionStatus.TRIAL)
    mock_sub_repo.get_by_workspace = AsyncMock(return_value=mock_sub)
    mock_sub_repo.update = AsyncMock()
    mock_event_bus.publish = AsyncMock()
    
    await stripe_service.process_webhook(mock_db_session, payload)
    
    assert mock_sub_repo.update.called
    # Ensure event was fired
    assert mock_event_bus.publish.called
