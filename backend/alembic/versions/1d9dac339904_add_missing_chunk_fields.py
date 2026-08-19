"""Add missing chunk fields

Revision ID: 1d9dac339904
Revises: 9b4aab65159a
Create Date: 2026-08-18 18:20:13.043774

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d9dac339904'
down_revision: Union[str, Sequence[str], None] = '9b4aab65159a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('document_chunks', sa.Column('character_count', sa.Integer(), nullable=True))
    op.add_column('document_chunks', sa.Column('section', sa.String(length=255), nullable=True))
    op.add_column('document_chunks', sa.Column('page_number', sa.Integer(), nullable=True))
    op.add_column('document_chunks', sa.Column('parent_heading', sa.String(length=500), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('document_chunks', 'character_count')
    op.drop_column('document_chunks', 'section')
    op.drop_column('document_chunks', 'page_number')
    op.drop_column('document_chunks', 'parent_heading')
