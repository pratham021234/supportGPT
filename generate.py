import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))
from app.models import Base
from sqlalchemy.schema import CreateTable
from sqlalchemy import create_engine
engine = create_engine('postgresql://')

output = []
output.append('"""initial_schema\n\nRevision ID: 0001\nRevises: \nCreate Date: 2026-08-07 10:00:00.000000\n\n"""')
output.append('from typing import Sequence, Union')
output.append('from alembic import op')
output.append('import sqlalchemy as sa')
output.append('from sqlalchemy.dialects import postgresql')
output.append('')
output.append('revision: str = "0001"')
output.append('down_revision: Union[str, None] = None')
output.append('branch_labels: Union[str, Sequence[str], None] = None')
output.append('depends_on: Union[str, Sequence[str], None] = None')
output.append('')
output.append('def upgrade() -> None:')
# ENUMs might need explicit creation, but let's see if CreateTable handles them.
# Yes, for PostgreSQL, CreateTable sometimes creates enums. But to be safe, raw SQL works.
for table in Base.metadata.sorted_tables:
    stmt = str(CreateTable(table).compile(engine)).strip()
    stmt = stmt.replace('\n', ' ')
    output.append(f'    op.execute("""{stmt}""")')

output.append('')
output.append('def downgrade() -> None:')
for table in reversed(Base.metadata.sorted_tables):
    output.append(f'    op.execute("DROP TABLE IF EXISTS {table.name} CASCADE")')
    
with open('backend/alembic/versions/0001_initial_schema.py', 'w') as f:
    f.write('\n'.join(output) + '\n')
