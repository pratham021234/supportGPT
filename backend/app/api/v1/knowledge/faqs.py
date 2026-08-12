from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.dependencies.db import get_db
from app.dependencies.authz import require_permission
from app.models.workspace import WorkspaceMember
from app.schemas.knowledge import FAQCreate, FAQUpdate, FAQResponse
from app.schemas.common import PaginationParams, FilterParams, PaginatedResponse
from app.services.knowledge_service import knowledge_service

router = APIRouter()

@router.post("/", response_model=FAQResponse, status_code=status.HTTP_201_CREATED)
async def create_faq(
    obj_in: FAQCreate,
    member: WorkspaceMember = Depends(require_permission("knowledge:create")),
    db: AsyncSession = Depends(get_db)
):
    return await knowledge_service.create_faq(db, str(member.workspace_id), str(member.user_id), obj_in)

@router.get("/", response_model=PaginatedResponse[FAQResponse])
async def list_faqs(
    pagination: PaginationParams = Depends(),
    filters: FilterParams = Depends(),
    member: WorkspaceMember = Depends(require_permission("knowledge:read")),
    db: AsyncSession = Depends(get_db)
):
    return await knowledge_service.get_workspace_faqs_paginated(db, str(member.workspace_id), pagination, filters)

@router.patch("/{faq_id}", response_model=FAQResponse)
async def update_faq(
    faq_id: str,
    obj_in: FAQUpdate,
    member: WorkspaceMember = Depends(require_permission("knowledge:manage")),
    db: AsyncSession = Depends(get_db)
):
    return await knowledge_service.update_faq(db, faq_id, str(member.workspace_id), obj_in)

@router.delete("/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_faq(
    faq_id: str,
    member: WorkspaceMember = Depends(require_permission("knowledge:delete")),
    db: AsyncSession = Depends(get_db)
):
    await knowledge_service.delete_faq(db, faq_id, str(member.workspace_id))
