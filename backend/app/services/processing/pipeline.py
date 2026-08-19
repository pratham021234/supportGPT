import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.processing import JobStatus, JobType
from app.models.knowledge import DocumentStatus, DocumentChunk
from app.repositories.processing_repo import (
    processing_job_repo, extraction_result_repo,
    ExtractionResultInternalCreate
)
from app.repositories.knowledge_repo import document_repo
from app.services.extractors.engine import extraction_service
from app.services.extractors.cleaner import TextCleaner
from app.services.extractors.metadata import metadata_extractor_service
from app.services.extractors.lang_detect import LanguageDetector
from app.services.extractors.crawler import website_crawler
from app.services.processing.chunking.service import chunking_service
from app.services.processing.metadata import metadata_service
from app.core.database import async_session_maker

logger = logging.getLogger(__name__)

class DocumentProcessingService:
    async def run_pipeline(self, job_id: str, file_path: str, source_type: str, workspace_id: str, document_id: str):
        """
        Background worker process for document processing.
        Because this runs in a background task, we must instantiate our own DB session.
        """
        async with async_session_maker() as db:
            job = await processing_job_repo.get(db, id=job_id)
            if not job:
                logger.error(f"Processing job {job_id} not found.")
                return
            
            doc = await document_repo.get(db, id=document_id)
            if not doc:
                logger.error(f"Document {document_id} not found.")
                return

            try:
                # Update status
                await processing_job_repo.update(db, db_obj=job, obj_in={
                    "status": JobStatus.PROCESSING,
                    "started_at": datetime.utcnow(),
                    "progress": 10
                })

                # 1. Extraction
                logger.info(f"Extracting content for job {job_id}")
                raw_text, page_count, metadata = extraction_service.process_file(file_path, source_type)
                
                # Normalize metadata
                metadata = metadata_extractor_service.extract_standard_metadata(metadata)
                
                await processing_job_repo.update(db, db_obj=job, obj_in={"progress": 40})

                # 2. Cleaning
                cleaned_text = TextCleaner.clean(raw_text)
                await processing_job_repo.update(db, db_obj=job, obj_in={"progress": 50})

                # 3. Language Detection
                lang = LanguageDetector.detect(cleaned_text)
                await processing_job_repo.update(db, db_obj=job, obj_in={"progress": 60})

                # Determine counts
                char_count = len(cleaned_text)
                word_count = len(cleaned_text.split())

                # Save ExtractionResult
                extraction_in = ExtractionResultInternalCreate(
                    document_id=document_id,
                    raw_text=raw_text,
                    cleaned_text=cleaned_text,
                    detected_language=lang,
                    page_count=page_count,
                    character_count=char_count,
                    word_count=word_count,
                    metadata_=metadata
                )
                await extraction_result_repo.create(db, obj_in=extraction_in)
                await processing_job_repo.update(db, db_obj=job, obj_in={"progress": 80})

                # 4. Chunking
                base_metadata = metadata_service.generate_document_metadata(
                    file_name=doc.file_name if 'doc' in locals() and doc else "Unknown",
                    source_type=source_type,
                    workspace_id=workspace_id,
                    language=lang,
                    page_count=page_count,
                    extra_meta=metadata
                )
                
                # Fetch settings for chunking (fallback to defaults if not provided in doc metadata)
                chunk_strategy = "PARAGRAPH"
                max_tokens = 1000
                overlap = 200
                if doc and doc.metadata_:
                    chunk_strategy = doc.metadata_.get("chunk_strategy", chunk_strategy)
                    max_tokens = int(doc.metadata_.get("chunk_size", max_tokens))
                    overlap = int(doc.metadata_.get("chunk_overlap", overlap))

                chunks = chunking_service.process_and_store(
                    db=db,
                    workspace_id=workspace_id,
                    document_id=document_id,
                    text=cleaned_text,
                    file_type=doc.file_type if doc else source_type,
                    base_metadata=base_metadata,
                    strategy_name=chunk_strategy
                )
                
                # Save Chunks via service
                await chunking_service.save_chunks(db, workspace_id, document_id, chunks)
                
                await db.commit()
                
                # Update Document Status
                doc = await document_repo.get(db, id=document_id)
                if doc:
                    await document_repo.update(db, db_obj=doc, obj_in={"status": DocumentStatus.INDEXING, "language": lang})

                # Complete Job
                await processing_job_repo.update(db, db_obj=job, obj_in={
                    "status": JobStatus.COMPLETED,
                    "progress": 100,
                    "completed_at": datetime.utcnow()
                })
                logger.info(f"Processing job {job_id} completed successfully.")

            except Exception as e:
                logger.error(f"Job {job_id} failed: {str(e)}")
                await db.rollback()
                await processing_job_repo.update(db, db_obj=job, obj_in={
                    "status": JobStatus.FAILED,
                    "failed_at": datetime.utcnow(),
                    "error_message": str(e)
                })
                    await document_repo.update(db, db_obj=doc, obj_in={"status": DocumentStatus.FAILED})

    async def run_website_pipeline(self, job_id: str, url: str, workspace_id: str, document_id: str):
        """
        Background worker process for website crawling and processing.
        """
        async with async_session_maker() as db:
            job = await processing_job_repo.get(db, id=job_id)
            if not job:
                logger.error(f"Processing job {job_id} not found.")
                return

            try:
                await processing_job_repo.update(db, db_obj=job, obj_in={
                    "status": JobStatus.PROCESSING,
                    "started_at": datetime.utcnow(),
                    "progress": 10
                })

                logger.info(f"Crawling website for job {job_id}")
                pages = await website_crawler.crawl(url)
                await processing_job_repo.update(db, db_obj=job, obj_in={"progress": 40})

                if not pages:
                    raise Exception("No content found or website inaccessible")

                # Aggregate content
                raw_text = "\n\n".join([page["content"] for page in pages])
                page_count = len(pages)
                metadata = {"crawled_pages": page_count, "url": url}
                
                cleaned_text = TextCleaner.clean(raw_text)
                await processing_job_repo.update(db, db_obj=job, obj_in={"progress": 50})

                lang = LanguageDetector.detect(cleaned_text)
                await processing_job_repo.update(db, db_obj=job, obj_in={"progress": 60})

                char_count = len(cleaned_text)
                word_count = len(cleaned_text.split())

                extraction_in = ExtractionResultInternalCreate(
                    document_id=document_id,
                    raw_text=raw_text,
                    cleaned_text=cleaned_text,
                    detected_language=lang,
                    page_count=page_count,
                    character_count=char_count,
                    word_count=word_count,
                    metadata_=metadata
                )
                await extraction_result_repo.create(db, obj_in=extraction_in)
                await processing_job_repo.update(db, db_obj=job, obj_in={"progress": 80})

                doc = await document_repo.get(db, id=document_id)
                base_metadata = metadata_service.generate_document_metadata(
                    file_name=url,
                    source_type="WEBSITE",
                    workspace_id=workspace_id,
                    language=lang,
                    page_count=page_count,
                    extra_meta=metadata
                )
                
                chunk_strategy = "PARAGRAPH"
                max_tokens = 1000
                overlap = 200
                if doc and doc.metadata_:
                    chunk_strategy = doc.metadata_.get("chunk_strategy", chunk_strategy)
                    max_tokens = int(doc.metadata_.get("chunk_size", max_tokens))
                    overlap = int(doc.metadata_.get("chunk_overlap", overlap))

                chunks = chunking_service.process_and_store(
                    db=db,
                    workspace_id=workspace_id,
                    document_id=document_id,
                    text=cleaned_text,
                    file_type="WEBSITE",
                    base_metadata=base_metadata,
                    strategy_name=chunk_strategy
                )
                
                # Save Chunks via service
                await chunking_service.save_chunks(db, workspace_id, document_id, chunks)
                
                await db.commit()
                
                doc = await document_repo.get(db, id=document_id)
                if doc:
                    await document_repo.update(db, db_obj=doc, obj_in={"status": DocumentStatus.INDEXING, "language": lang})

                await processing_job_repo.update(db, db_obj=job, obj_in={
                    "status": JobStatus.COMPLETED,
                    "progress": 100,
                    "completed_at": datetime.utcnow()
                })
                logger.info(f"Website processing job {job_id} completed successfully.")

            except Exception as e:
                logger.error(f"Job {job_id} failed: {str(e)}")
                await db.rollback()
                await processing_job_repo.update(db, db_obj=job, obj_in={
                    "status": JobStatus.FAILED,
                    "failed_at": datetime.utcnow(),
                    "error_message": str(e)
                })
                doc = await document_repo.get(db, id=document_id)
                if doc:
                    await document_repo.update(db, db_obj=doc, obj_in={"status": DocumentStatus.FAILED})

document_processing_service = DocumentProcessingService()
