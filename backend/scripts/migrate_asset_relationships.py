"""
Migration script to add AssetRelationship table for CMDB functionality.
Run this script to add the asset_relationships table to existing databases.
Handles existing tables by checking schema and recreating if needed.
"""

from sqlalchemy import text, inspect
import sys
import os

# Fix import paths - try multiple approaches
try:
    # Try absolute import first
    from app.database.database import engine
except ImportError:
    try:
        # Try relative import from scripts directory
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from app.database.database import engine
    except ImportError:
        # Fallback: add parent directory to path
        backend_dir = os.path.dirname(os.path.dirname(__file__))
        sys.path.insert(0, backend_dir)
        from app.database.database import engine

def check_table_exists_and_valid(conn):
    """
    Check if table exists and has all required columns.
    Returns: (exists: bool, is_valid: bool, missing_columns: list)
    """
    inspector = inspect(conn)
    
    # Check if table exists
    tables = inspector.get_table_names(schema='asset')
    if 'asset_relationships' not in tables:
        return False, False, []
    
    # Table exists, check columns
    columns = inspector.get_columns('asset_relationships', schema='asset')
    column_names = [col['name'] for col in columns]
    
    expected_columns = [
        'id', 'source_asset_id', 'target_asset_id', 'relationship_type',
        'description', 'criticality', 'metadata_', 'created_by',
        'created_at', 'updated_at'
    ]
    
    missing_columns = [col for col in expected_columns if col not in column_names]
    
    return True, len(missing_columns) == 0, missing_columns

def drop_table(conn):
    """Drop the asset_relationships table and all its constraints."""
    print("Dropping existing asset_relationships table...")
    
    # Drop indexes first
    drop_indexes_sql = """
    DROP INDEX IF EXISTS asset.idx_asset_relationships_source;
    DROP INDEX IF EXISTS asset.idx_asset_relationships_target;
    DROP INDEX IF EXISTS asset.idx_asset_relationships_type;
    DROP INDEX IF EXISTS asset.idx_asset_relationships_metadata_gin;
    """
    
    try:
        conn.execute(text(drop_indexes_sql))
    except Exception as e:
        print(f"  Note: Some indexes may not exist: {e}")
    
    # Drop table (this will cascade to constraints)
    drop_table_sql = "DROP TABLE IF EXISTS asset.asset_relationships CASCADE;"
    conn.execute(text(drop_table_sql))
    print("✓ Table dropped")

def create_table(conn):
    """Create the asset_relationships table with correct schema."""
    print("Creating asset_relationships table...")
    
    create_table_sql = """
    CREATE TABLE asset.asset_relationships (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        source_asset_id UUID NOT NULL,
        target_asset_id UUID NOT NULL,
        relationship_type VARCHAR(50) NOT NULL,
        description TEXT,
        criticality FLOAT DEFAULT 3.0,
        metadata_ JSONB DEFAULT '{}'::jsonb,
        created_by VARCHAR(255),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

        CONSTRAINT fk_source_asset FOREIGN KEY (source_asset_id)
            REFERENCES asset.assets(id) ON DELETE CASCADE,
        CONSTRAINT fk_target_asset FOREIGN KEY (target_asset_id)
            REFERENCES asset.assets(id) ON DELETE CASCADE,
        CONSTRAINT chk_relationship_type CHECK (relationship_type IN (
            'parent_of', 'child_of', 'depends_on', 'depended_by',
            'connected_to', 'runs_on', 'backs_up_to'
        )),
        CONSTRAINT chk_criticality CHECK (criticality >= 1 AND criticality <= 5),
        CONSTRAINT no_self_relationship CHECK (source_asset_id != target_asset_id)
    );
    """
    
    conn.execute(text(create_table_sql))
    print("✓ Table created")

def create_indexes(conn):
    """Create indexes for the asset_relationships table."""
    print("Creating indexes...")
    
    index_sql = """
    CREATE INDEX idx_asset_relationships_source
        ON asset.asset_relationships(source_asset_id);

    CREATE INDEX idx_asset_relationships_target
        ON asset.asset_relationships(target_asset_id);

    CREATE INDEX idx_asset_relationships_type
        ON asset.asset_relationships(relationship_type);
    """
    
    conn.execute(text(index_sql))
    print("✓ Indexes created")
    
    # Add GIN index for metadata
    try:
        gin_index_sql = """
        CREATE INDEX idx_asset_relationships_metadata_gin
            ON asset.asset_relationships USING gin (metadata_);
        """
        conn.execute(text(gin_index_sql))
        print("✓ GIN index for metadata created")
    except Exception as e:
        print(f"⚠ GIN index creation skipped: {e}")

def migrate():
    """
    Add AssetRelationship table for CMDB relationships between assets.
    Handles existing tables by checking schema and recreating if needed.
    """
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # Check if table exists and is valid
            exists, is_valid, missing_cols = check_table_exists_and_valid(conn)
            
            if exists:
                if is_valid:
                    print("✓ asset_relationships table already exists with correct schema")
                    print("  Skipping migration (table is valid)")
                    trans.commit()
                    return
                else:
                    print(f"⚠ Table exists but is missing columns: {missing_cols}")
                    print("  Dropping and recreating table...")
                    drop_table(conn)
            
            # Create table
            create_table(conn)
            
            # Create indexes (only after table is confirmed created)
            create_indexes(conn)
            
            trans.commit()
            print("\n✓ Migration completed successfully!")
            
        except Exception as e:
            trans.rollback()
            print(f"\n✗ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            raise

def verify_migration():
    """
    Verify that the migration was successful.
    """
    try:
        inspector = inspect(engine)
        
        # Check if table exists
        tables = inspector.get_table_names(schema='asset')
        if 'asset_relationships' not in tables:
            print("✗ asset_relationships table not found")
            return False
        
        print("✓ asset_relationships table exists")
        
        # Check columns
        columns = inspector.get_columns('asset_relationships', schema='asset')
        column_names = [col['name'] for col in columns]
        expected_columns = [
            'id', 'source_asset_id', 'target_asset_id', 'relationship_type',
            'description', 'criticality', 'metadata_', 'created_by',
            'created_at', 'updated_at'
        ]
        
        missing_columns = [col for col in expected_columns if col not in column_names]
        if missing_columns:
            print(f"✗ Missing columns: {missing_columns}")
            return False
        else:
            print("✓ All expected columns present")
        
        # Check indexes
        indexes = inspector.get_indexes('asset_relationships', schema='asset')
        index_names = [idx['name'] for idx in indexes]
        print(f"✓ Indexes found: {len(index_names)}")
        
        # Check foreign keys
        fks = inspector.get_foreign_keys('asset_relationships', schema='asset')
        print(f"✓ Foreign keys found: {len(fks)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== AssetRelationship Migration ===\n")
    
    try:
        migrate()
        
        print("\n=== Verification ===\n")
        if verify_migration():
            print("\n✓✓✓ Migration and verification successful! ✓✓✓")
        else:
            print("\n✗ Migration verification failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗✗✗ Migration failed: {e} ✗✗✗")
        sys.exit(1)
