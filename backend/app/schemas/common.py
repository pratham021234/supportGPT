from typing import Generic, TypeVar, List, Optional, Any
from pydantic import BaseModel, Field

T = TypeVar("T")

class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(20, ge=1, le=100, description="Items per page")
    sort: Optional[str] = Field(None, description="Field to sort by")
    order: Optional[str] = Field("desc", description="Sort order (asc/desc)")

class FilterParams(BaseModel):
    search: Optional[str] = Field(None, description="Keyword search")
    status: Optional[str] = Field(None, description="Status filter")
    source_id: Optional[str] = Field(None, description="Source ID filter")
    # Custom filters can be added or inherited from this base class

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    pages: int
