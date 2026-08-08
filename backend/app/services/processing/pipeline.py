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
from app.services.extractors.lang_detect import LanguageDetector
from app.services.extractors.crawler import website_crawler
from app.services.processing.chunker import semantic_chunker
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
                base_metadata = {
                    "source_type": source_type,
                    "language": lang
                }
                chunks = semantic_chunker.chunk_text(cleaned_text, base_metadata)
                
                # Save Chunks
                for chunk_result in chunks:
                    chunk = DocumentChunk(
                        workspace_id=workspace_id,
                        document_id=document_id,
                        chunk_index=chunk_result.metadata.get("chunk_index", 0),
                        content=chunk_result.content,
                        token_count=chunk_result.token_count,
                        chunk_type="TEXT",
                        metadata_=chunk_result.metadata
                    )
                    db.add(chunk)
                
                await db.commit()
                
                # Update Document Status
                doc = await document_repo.get(db, id=document_id)
                if doc:
                    await document_repo.update(db, db_obj=doc, obj_in={"status": DocumentStatus.READY, "language": lang})

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

                base_metadata = {
                    "source_type": "WEBSITE",
                    "language": lang
                }
                chunks = semantic_chunker.chunk_text(cleaned_text, base_metadata)
                
                for chunk_result in chunks:
                    chunk = DocumentChunk(
                        workspace_id=workspace_id,
                        document_id=document_id,
                        chunk_index=chunk_result.metadata.get("chunk_index", 0),
                        content=chunk_result.content,
                        token_count=chunk_result.token_count,
                        chunk_type="TEXT",
                        metadata_=chunk_result.metadata
                    )
                    db.add(chunk)
                
                await db.commit()
                
                doc = await document_repo.get(db, id=document_id)
                if doc:
                    await document_repo.update(db, db_obj=doc, obj_in={"status": DocumentStatus.READY, "language": lang})

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
