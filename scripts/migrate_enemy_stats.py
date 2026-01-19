"""
Migrate enemy_stats to master table structure.

This script:
1. Takes the current enemy_stats table
2. Renames it to enemy_stats_20260118 (or specified date)
3. Creates enemy_all_stats master table
4. Copies data to master table with match_date
5. Creates enemy_stats VIEW pointing to latest match
"""

import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime

def migrate_enemy_stats(match_date: str = '20260118'):
    """
    Migrate enemy_stats table to master table structure.
    
    Args:
        match_date: Date for the current data (default: 20260118)
    """
    db_path = Path('data/analysis.db')
    if not db_path.exists():
        print(f"❌ Error: Database '{db_path}' not found.")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if enemy_stats exists and is a table
        cursor.execute("SELECT type FROM sqlite_master WHERE name='enemy_stats'")
        result = cursor.fetchone()
        
        if not result:
            print("❌ Error: enemy_stats table not found")
            return False
        
        if result[0] == 'view':
            print("ℹ️  enemy_stats is already a VIEW. Migration may have already been done.")
            return True
        
        print(f"📊 Starting migration of enemy_stats...")
        
        # Get current data
        df = pd.read_sql_query("SELECT * FROM enemy_stats", conn)
        print(f"   Found {len(df)} players in enemy_stats")
        
        # Rename current table to dated version
        dated_table = f"enemy_stats_{match_date}"
        print(f"\n📋 Renaming enemy_stats to {dated_table}...")
        cursor.execute(f"DROP TABLE IF EXISTS {dated_table}")
        cursor.execute(f"ALTER TABLE enemy_stats RENAME TO {dated_table}")
        print(f"✓ Renamed to {dated_table}")
        
        # Create master table
        print(f"\n📊 Creating master table: enemy_all_stats")
        create_master_sql = """
        CREATE TABLE IF NOT EXISTS enemy_all_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_date TEXT NOT NULL,
            player_name TEXT NOT NULL,
            defeated INTEGER,
            assist INTEGER,
            defeated_2 INTEGER,
            fun_coin INTEGER,
            damage INTEGER,
            tank INTEGER,
            heal INTEGER,
            siege_damage INTEGER
        )
        """
        cursor.execute(create_master_sql)
        print(f"✓ Created enemy_all_stats")
        
        # Copy data to master table
        print(f"\n📥 Copying data to enemy_all_stats...")
        df_master = df.copy()
        df_master['match_date'] = match_date
        
        # Reorder columns
        cols = ['match_date'] + [col for col in df_master.columns if col != 'match_date']
        df_master = df_master[cols]
        
        df_master.to_sql('enemy_all_stats', conn, if_exists='append', index=False)
        print(f"✓ Added {len(df)} rows to enemy_all_stats with match_date={match_date}")
        
        # Create indexes
        print(f"\n🔍 Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_enemy_match_date ON enemy_all_stats(match_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_enemy_player ON enemy_all_stats(player_name)")
        print(f"✓ Created indexes")
        
        # Create VIEW
        print(f"\n👁️  Creating enemy_stats VIEW...")
        view_sql = f"""
        CREATE VIEW enemy_stats AS
        SELECT 
            player_name,
            defeated,
            assist,
            defeated_2,
            fun_coin,
            damage,
            tank,
            heal,
            siege_damage
        FROM enemy_all_stats
        WHERE match_date = '{match_date}'
        """
        cursor.execute(view_sql)
        print(f"✓ Created enemy_stats VIEW showing match from {match_date}")
        
        conn.commit()
        
        # Verify
        print(f"\n✅ Migration complete!")
        print(f"\n📊 New Database Structure:")
        print(f"   - enemy_all_stats (master table with all matches)")
        print(f"   - enemy_stats_{match_date} (dated snapshot)")
        print(f"   - enemy_stats (VIEW showing latest match)")
        
        # Show stats
        cursor.execute("SELECT COUNT(*) FROM enemy_all_stats")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT match_date) FROM enemy_all_stats")
        matches = cursor.fetchone()[0]
        print(f"\n📈 Statistics:")
        print(f"   Total records: {total}")
        print(f"   Total matches: {matches}")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        conn.close()


if __name__ == "__main__":
    import sys
    
    match_date = sys.argv[1] if len(sys.argv) > 1 else '20260118'
    
    print("="*60)
    print("Enemy Stats Migration Script")
    print("="*60)
    print(f"\nThis will migrate enemy_stats to the master table structure.")
    print(f"Current data will be tagged with date: {match_date}")
    print("\nPress Ctrl+C to cancel, or Enter to continue...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n\nMigration cancelled.")
        sys.exit(0)
    
    success = migrate_enemy_stats(match_date)
    sys.exit(0 if success else 1)
