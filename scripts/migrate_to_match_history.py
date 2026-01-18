"""
Migrate existing yb_stats to match history structure
Renames current yb_stats table to yb_stats_20260118 and creates new master table
"""

import sqlite3
from datetime import datetime
from pathlib import Path

# Database path
db_path = Path(__file__).parent.parent / 'data' / 'analysis.db'

print("Starting database migration...")

with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    
    # Get today's date
    match_date = datetime.now().strftime('%Y%m%d')
    old_table = f'yb_stats_{match_date}'
    
    # Check if yb_stats exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='yb_stats'")
    if cursor.fetchone():
        # Rename current yb_stats to yb_stats_YYYYMMDD
        print(f"Renaming 'yb_stats' to '{old_table}'...")
        cursor.execute(f"ALTER TABLE yb_stats RENAME TO {old_table}")
        
        # Create master YoungBuffalo stats table with match_date column
        print("Creating master 'youngbuffalo_stats' table...")
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS youngbuffalo_stats (
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
                siege_damage INTEGER,
                UNIQUE(match_date, player_name)
            )
        """)
        
        # Copy data from old table to master table
        print(f"Copying data from '{old_table}' to 'youngbuffalo_stats'...")
        cursor.execute(f"""
            INSERT INTO youngbuffalo_stats 
                (match_date, player_name, defeated, assist, defeated_2, fun_coin, 
                 damage, tank, heal, siege_damage)
            SELECT 
                '{match_date}',
                player_name, defeated, assist, defeated_2, fun_coin,
                damage, tank, heal, siege_damage
            FROM {old_table}
        """)
        
        # Create indexes
        print("Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_yb_match_date ON youngbuffalo_stats(match_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_yb_player_name ON youngbuffalo_stats(player_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_yb_defeated ON youngbuffalo_stats(defeated DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_yb_damage ON youngbuffalo_stats(damage DESC)")
        
        # Create a view that mimics the old yb_stats for backward compatibility
        print("Creating 'yb_stats' view for backward compatibility...")
        cursor.execute(f"""
            CREATE VIEW IF NOT EXISTS yb_stats AS
            SELECT 
                player_name, defeated, assist, defeated_2, fun_coin,
                damage, tank, heal, siege_damage
            FROM youngbuffalo_stats
            WHERE match_date = '{match_date}'
        """)
        
        conn.commit()
        
        # Show results
        cursor.execute("SELECT COUNT(*) FROM youngbuffalo_stats")
        count = cursor.fetchone()[0]
        print(f"\n✓ Migration complete!")
        print(f"✓ Master table 'youngbuffalo_stats' has {count} rows")
        print(f"✓ Match-specific table '{old_table}' preserved")
        print(f"✓ View 'yb_stats' created for backward compatibility")
        
        # Show unique match dates
        cursor.execute("SELECT DISTINCT match_date FROM youngbuffalo_stats ORDER BY match_date")
        dates = [row[0] for row in cursor.fetchall()]
        print(f"\nMatch dates in database: {', '.join(dates)}")
        
    else:
        print("No 'yb_stats' table found. Nothing to migrate.")

print("\nMigration complete!")
