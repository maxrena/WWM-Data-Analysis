"""
Update database to version 1.2 - Add match_id support

This script adds match_id column to master tables to support multiple matches per day.
"""

import sqlite3
from pathlib import Path

def upgrade_to_v12():
    """Upgrade database to version 1.2"""
    db_path = Path('data/analysis.db')
    if not db_path.exists():
        print("❌ Database not found")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("🔄 Upgrading database to version 1.2...")
        
        # Check and add match_id to youngbuffalo_stats
        cursor.execute("PRAGMA table_info(youngbuffalo_stats)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'match_id' not in columns:
            print("  Adding match_id to youngbuffalo_stats...")
            cursor.execute("ALTER TABLE youngbuffalo_stats ADD COLUMN match_id TEXT")
            
            # Update existing records with match_id based on match_date
            cursor.execute("""
                UPDATE youngbuffalo_stats 
                SET match_id = match_date || '_000000'
                WHERE match_id IS NULL
            """)
            print("  ✓ Updated existing YB records with default match_id")
        else:
            print("  ℹ️  match_id already exists in youngbuffalo_stats")
        
        # Check and add match_id to enemy_all_stats
        cursor.execute("PRAGMA table_info(enemy_all_stats)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'match_id' not in columns:
            print("  Adding match_id to enemy_all_stats...")
            cursor.execute("ALTER TABLE enemy_all_stats ADD COLUMN match_id TEXT")
            
            # Update existing records with match_id based on match_date
            cursor.execute("""
                UPDATE enemy_all_stats 
                SET match_id = match_date || '_000000'
                WHERE match_id IS NULL
            """)
            print("  ✓ Updated existing enemy records with default match_id")
        else:
            print("  ℹ️  match_id already exists in enemy_all_stats")
        
        # Create indexes on match_id
        print("  Creating indexes on match_id...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_yb_match_id ON youngbuffalo_stats(match_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_enemy_match_id ON enemy_all_stats(match_id)")
        print("  ✓ Indexes created")
        
        # Create version table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS db_version (
                version TEXT PRIMARY KEY,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("INSERT OR REPLACE INTO db_version (version) VALUES ('1.2')")
        
        conn.commit()
        
        print("\n✅ Database upgraded to version 1.2!")
        print("\n📊 New features:")
        print("   - match_id column supports multiple matches per day")
        print("   - Format: YYYYMMDD_HHMMSS (e.g., 20260118_143000)")
        print("   - Existing data updated with default match_id")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        conn.close()


if __name__ == "__main__":
    print("="*60)
    print("Database Upgrade to Version 1.2")
    print("="*60)
    print("\nThis will add match_id support for multiple matches per day.")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n\nUpgrade cancelled.")
        import sys
        sys.exit(0)
    
    success = upgrade_to_v12()
    import sys
    sys.exit(0 if success else 1)
