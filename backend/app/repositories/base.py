from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from sqlalchemy import update, delete, func
from pydantic import BaseModel
from app.core.database import Base
from app.schemas.common import PaginationParams, FilterParams

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id)
        if hasattr(self.model, "is_deleted"):
            query = query.where(self.model.is_deleted == False)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        query = select(self.model)
        if hasattr(self.model, "is_deleted"):
            query = query.where(self.model.is_deleted == False)
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_paginated(
        self, db: AsyncSession, *, pagination: PaginationParams, filters: Optional[FilterParams] = None, **kwargs
    ) -> Dict[str, Any]:
        query = select(self.model)
        
        if hasattr(self.model, "is_deleted"):
            query = query.where(self.model.is_deleted == False)

        for key, value in kwargs.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
                
        if filters:
            if getattr(filters, "status", None) and hasattr(self.model, "status"):
                query = query.where(self.model.status == filters.status)
            if getattr(filters, "source_id", None) and hasattr(self.model, "source_id"):
                query = query.where(self.model.source_id == filters.source_id)
            if getattr(filters, "search", None):
                search_term = f"%{filters.search}%"
                if hasattr(self.model, "title"):
                    query = query.where(self.model.title.ilike(search_term))
                elif hasattr(self.model, "name"):
                    query = query.where(self.model.name.ilike(search_term))
                elif hasattr(self.model, "question"):
                    query = query.where(self.model.question.ilike(search_term))

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        if pagination.sort and hasattr(self.model, pagination.sort):
            sort_attr = getattr(self.model, pagination.sort)
            if pagination.order == "desc":
                query = query.order_by(sort_attr.desc())
            else:
                query = query.order_by(sort_attr.asc())
        elif hasattr(self.model, "created_at"):
            query = query.order_by(self.model.created_at.desc())
            
        skip = (pagination.page - 1) * pagination.limit
        query = query.offset(skip).limit(pagination.limit)
        
        result = await db.execute(query)
        items = list(result.scalars().all())
        
        pages = (total + pagination.limit - 1) // pagination.limit if total > 0 else 1
        
        return {
            "items": items,
            "total": total,
            "page": pagination.page,
            "pages": pages
        }

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        obj_data = db_obj.__dict__
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, id: Any) -> ModelType:
        obj = await self.get(db=db, id=id)
        if obj:
            if hasattr(self.model, "is_deleted"):
                obj.is_deleted = True
                obj.deleted_at = datetime.utcnow()
                db.add(obj)
            else:
                await db.delete(obj)
            await db.commit()
        return obj
