import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch
import uuid

from app.services.billing.billing_service import (
    stripe_service,
    plan_enforcement_service,
    feature_gate_service,
    revenue_analytics_service,
    plan_service
)
from app.repositories.billing_repo import Plan

@pytest.mark.asyncio
async def test_feature_gate_service(db_session: AsyncSession):
    with patch("app.repositories.billing_repo.subscription_repo.get_by_workspace", new_callable=AsyncMock) as mock_sub:
        with patch("app.repositories.billing_repo.plan_repo.get", new_callable=AsyncMock) as mock_plan:
            mock_sub.return_value = type('obj', (object,), {'plan_id': 'plan1'})()
            mock_plan.return_value = Plan(features=["sso", "advanced_analytics"])
            
            has_sso = await feature_gate_service.has_feature(db_session, "ws1", "sso")
            assert has_sso is True
            
            has_custom = await feature_gate_service.has_feature(db_session, "ws1", "custom_models")
            assert has_custom is False

@pytest.mark.asyncio
async def test_plan_enforcement_service(db_session: AsyncSession):
    with patch("app.repositories.billing_repo.subscription_repo.get_by_workspace", new_callable=AsyncMock) as mock_sub:
        with patch("app.repositories.billing_repo.plan_repo.get", new_callable=AsyncMock) as mock_plan:
            with patch("app.repositories.billing_repo.usage_record_repo.get_usage_sum", new_callable=AsyncMock) as mock_usage:
                mock_sub.return_value = type('obj', (object,), {'plan_id': 'plan1'})()
                mock_plan.return_value = Plan(limits={"agents": 5})
                mock_usage.return_value = 5 # currently at limit
                
                with pytest.raises(plan_enforcement_service.LimitExceededError):
                    await plan_enforcement_service.check_limit(db_session, "ws1", "agents", 1)

@pytest.mark.asyncio
async def test_stripe_webhook_processing(db_session: AsyncSession):
    with patch("app.repositories.billing_repo.subscription_repo.get_by_workspace", new_callable=AsyncMock) as mock_sub:
        with patch("app.repositories.billing_repo.subscription_repo.update", new_callable=AsyncMock) as mock_update:
            with patch("app.repositories.billing_repo.invoice_repo.create", new_callable=AsyncMock) as mock_inv:
                mock_sub.return_value = type('obj', (object,), {'id': 'sub1'})()
                
                payload = {
                    "type": "checkout.session.completed",
                    "data": {
                        "object": {
                            "client_reference_id": "ws1",
                            "subscription": "sub_123",
                            "customer": "cus_123"
                        }
                    }
                }
                
                await stripe_service.process_webhook(db_session, payload)
                mock_update.assert_called_once()
                mock_inv.assert_called_once()
