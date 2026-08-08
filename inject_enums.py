import sys
import os
import inspect
import enum

sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))
import app.models

enums = []
for name, obj in inspect.getmembers(app.models):
    if inspect.isclass(obj) and issubclass(obj, enum.Enum) and obj is not enum.Enum:
        values = ', '.join([f"'{v.value}'" for v in obj])
        enums.append(f"CREATE TYPE {obj.__name__.lower()} AS ENUM ({values});")

with open('backend/alembic/versions/0001_initial_schema.py', 'r') as f:
    content = f.read()

upgrade_def = 'def upgrade() -> None:\n'
enum_statements = '\n'.join([f'    op.execute("{e}")' for e in enums]) + '\n'
content = content.replace(upgrade_def, upgrade_def + enum_statements)

with open('backend/alembic/versions/0001_initial_schema.py', 'w') as f:
    f.write(content)

print("Enums injected successfully!")
