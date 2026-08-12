import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.models import Base
from sqlalchemy.orm import class_mapper

def analyze_models():
    print("--- Database Models Audit ---")
    models = [cls for cls in Base.__subclasses__()]
    for model in models:
        print(f"\nModel: {model.__name__} (Table: {model.__tablename__})")
        mapper = class_mapper(model)
        
        # Check Tenant Isolation
        has_workspace = 'workspace_id' in [c.name for c in mapper.columns]
        has_owner = 'owner_id' in [c.name for c in mapper.columns]
        if has_workspace:
            print("  - Tenant Isolation: YES (workspace_id)")
        elif has_owner:
            print("  - Tenant Isolation: YES (owner_id)")
        else:
            print("  - Tenant Isolation: NO (WARNING)")
            
        # Check Soft Deletes
        has_soft_delete = 'deleted_at' in [c.name for c in mapper.columns] or 'is_deleted' in [c.name for c in mapper.columns]
        print(f"  - Soft Delete: {'YES' if has_soft_delete else 'NO (WARNING)'}")
        
        # Check Audit Fields
        has_created_at = 'created_at' in [c.name for c in mapper.columns]
        has_updated_at = 'updated_at' in [c.name for c in mapper.columns]
        has_created_by = 'created_by' in [c.name for c in mapper.columns]
        has_updated_by = 'updated_by' in [c.name for c in mapper.columns]
        
        audit_status = []
        if has_created_at: audit_status.append('created_at')
        if has_updated_at: audit_status.append('updated_at')
        if has_created_by: audit_status.append('created_by')
        if has_updated_by: audit_status.append('updated_by')
        print(f"  - Audit Fields: {', '.join(audit_status) if audit_status else 'NONE'}")
        
        # Check Relationships
        for rel in mapper.relationships:
            print(f"  - Relationship: {rel.key} -> {rel.mapper.class_.__name__} (Cascade: {rel.cascade})")

if __name__ == "__main__":
    analyze_models()
