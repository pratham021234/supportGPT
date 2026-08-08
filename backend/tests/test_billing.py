import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.billing.billing_service import plan_enforcement_service, stripe_service
from app.models.billing import SubscriptionStatus

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture
def workspace_id():
    return str(uuid.uuid4())

@pytest.mark.asyncio
async def test_plan_enforcement_allow(mock_db, workspace_id):
    mock_sub = MagicMock(plan_id=uuid.uuid4())
    mock_plan = MagicMock(limits={"agents": 5})
    
    with patch("app.repositories.billing_repo.subscription_repo.get_by_workspace", return_value=mock_sub), \
         patch("app.repositories.billing_repo.plan_repo.get", return_value=mock_plan), \
         patch("app.repositories.billing_repo.usage_record_repo.get_usage_sum", return_value=3):
             
        # 3 + 1 <= 5, should return True
        result = await plan_enforcement_service.check_limit(mock_db, workspace_id, "agents", 1)
        assert result == True

@pytest.mark.asyncio
async def test_plan_enforcement_deny(mock_db, workspace_id):
    mock_sub = MagicMock(plan_id=uuid.uuid4())
    mock_plan = MagicMock(limits={"agents": 5})
    
    with patch("app.repositories.billing_repo.subscription_repo.get_by_workspace", return_value=mock_sub), \
         patch("app.repositories.billing_repo.plan_repo.get", return_value=mock_plan), \
         patch("app.repositories.billing_repo.usage_record_repo.get_usage_sum", return_value=5):
             
        # 5 + 1 > 5, should raise
        with pytest.raises(plan_enforcement_service.LimitExceededError):
            await plan_enforcement_service.check_limit(mock_db, workspace_id, "agents", 1)

@pytest.mark.asyncio
async def test_stripe_webhook_checkout_completed(mock_db, workspace_id):
    mock_sub = MagicMock()
    
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
    
    with patch("app.repositories.billing_repo.subscription_repo.get_by_workspace", return_value=mock_sub), \
         patch("app.repositories.billing_repo.subscription_repo.update") as mock_update, \
         patch("app.repositories.billing_repo.invoice_repo.create") as mock_invoice_create:
             
        await stripe_service.process_webhook(mock_db, payload)
        
        # Verify subscription was activated
        mock_update.assert_called_once()
        args, kwargs = mock_update.call_args
        obj_in = kwargs.get("obj_in")
        assert obj_in["status"] == SubscriptionStatus.ACTIVE
        assert obj_in["stripe_subscription_id"] == "sub_123"
        
        # Verify an initial invoice was generated
        mock_invoice_create.assert_called_once()
