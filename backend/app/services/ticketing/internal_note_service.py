import logging
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.models.ticket import TicketComment
from app.repositories.ticket_repo import ticket_comment_repo, TicketCommentInternalCreate, ticket_activity_repo, TicketActivityInternalCreate

logger = logging.getLogger(__name__)

class InternalNoteService:
    async def add_private_note(self, db: AsyncSession, ticket_id: str, author_id: str, content: str) -> TicketComment:
        """Adds a private note to a ticket, invisible to the customer."""
        comment_in = TicketCommentInternalCreate(
            ticket_id=ticket_id,
            author_id=author_id,
            content=content,
            is_internal=True
        )
        comment = await ticket_comment_repo.create(db, obj_in=comment_in)
        
        activity_in = TicketActivityInternalCreate(
            ticket_id=ticket_id,
            actor_id=author_id,
            action="PRIVATE_NOTE_ADDED"
        )
        await ticket_activity_repo.create(db, obj_in=activity_in)
        
        return comment

internal_note_service = InternalNoteService()
