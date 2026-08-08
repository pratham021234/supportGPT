import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from fastapi import UploadFile
from io import BytesIO

from app.models.knowledge import SourceType, KnowledgeSource, Document, FAQ
from app.schemas.knowledge import KnowledgeSourceCreate, KnowledgeSourceUpdate, FAQCreate, FAQUpdate
from app.services.knowledge_service import knowledge_service
from app.core.exceptions import NotFoundException

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.mark.asyncio
async def test_create_and_get_knowledge_source(mock_db):
    workspace_id = str(uuid4())
    user_id = str(uuid4())
    
    source_in = KnowledgeSourceCreate(
        name="Test Source",
        description="A test knowledge source",
        source_type=SourceType.PDF
    )
    
    with patch("app.services.knowledge_service.knowledge_source_repo") as mock_repo:
        created_source = KnowledgeSource(id=uuid4(), name="Test Source", source_type=SourceType.PDF, workspace_id=workspace_id)
        mock_repo.create = AsyncMock(return_value=created_source)
        mock_repo.get_by_workspace = AsyncMock(return_value=[created_source])
        
        # Create
        source = await knowledge_service.create_source(mock_db, workspace_id, user_id, source_in)
        assert source.name == "Test Source"
        assert source.source_type == SourceType.PDF
        
        # Get
        sources = await knowledge_service.get_workspace_sources(mock_db, workspace_id)
        assert len(sources) == 1
        assert sources[0].id == source.id

@pytest.mark.asyncio
async def test_upload_document(mock_db):
    workspace_id = str(uuid4())
    user_id = str(uuid4())
    
    with patch("app.services.storage_service.StorageService.save_file", return_value="mock/path/file.pdf"), \
         patch("app.services.knowledge_service.KnowledgeService._queue_document_processing", return_value=None), \
         patch("app.services.knowledge_service.document_repo") as mock_repo:
        
        doc_mock = Document(id=uuid4(), title="test.pdf", storage_path="mock/path/file.pdf", workspace_id=workspace_id)
        mock_repo.create = AsyncMock(return_value=doc_mock)
        mock_repo.update = AsyncMock(return_value=doc_mock)
        mock_repo.get_by_workspace = AsyncMock(return_value=[doc_mock])
        
        file_content = b"Dummy PDF content"
        headers = {"content-type": "application/pdf"}
        file = UploadFile(filename="test.pdf", file=BytesIO(file_content), headers=headers)
        
        # Upload
        document = await knowledge_service.upload_document(mock_db, workspace_id, user_id, file)
        
        assert document.title == "test.pdf"
        assert document.storage_path == "mock/path/file.pdf"
        
        # Get documents
        documents = await knowledge_service.get_workspace_documents(mock_db, workspace_id)
        assert len(documents) == 1

@pytest.mark.asyncio
async def test_create_and_update_faq(mock_db):
    workspace_id = str(uuid4())
    user_id = str(uuid4())
    
    faq_in = FAQCreate(
        question="How do I reset password?",
        answer="Go to settings.",
        category="General"
    )
    
    with patch("app.services.knowledge_service.faq_repo") as mock_repo:
        faq_mock = FAQ(id=uuid4(), question="How do I reset password?", answer="Go to settings.", workspace_id=workspace_id)
        mock_repo.create = AsyncMock(return_value=faq_mock)
        
        faq = await knowledge_service.create_faq(mock_db, workspace_id, user_id, faq_in)
        assert faq.question == "How do I reset password?"
        
        # Update FAQ
        faq_update = FAQUpdate(answer="Go to security settings.")
        
        # For update we need get to return the faq
        mock_repo.get = AsyncMock(return_value=faq_mock)
        updated_mock = FAQ(id=faq_mock.id, question="How do I reset password?", answer="Go to security settings.", workspace_id=workspace_id)
        mock_repo.update = AsyncMock(return_value=updated_mock)
        
        updated_faq = await knowledge_service.update_faq(mock_db, str(faq.id), workspace_id, faq_update)
        assert updated_faq.answer == "Go to security settings."
        
        # Multi-tenant isolation test
        wrong_workspace_id = str(uuid4())
        with pytest.raises(NotFoundException):
            await knowledge_service.update_faq(mock_db, str(faq.id), wrong_workspace_id, faq_update)
