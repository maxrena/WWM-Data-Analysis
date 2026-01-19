"""
Add new enemy team match data to the master database.

This script:
1. Takes a CSV file with match data
2. Creates a dated table (e.g., enemy_stats_20260119)
3. Adds the data to the master enemy_all_stats table with the match date
4. Updates the enemy_stats VIEW to show the latest match data

Usage:
    python scripts/add_enemy_match.py <csv_file> [date]
    
    If date is not provided, today's date will be used (YYYYMMDD format)
"""

import sys
import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path

def add_enemy_match(csv_file: str, match_date: str = None):
    """
    Add new enemy team match data to the database.
    
    Args:
        csv_file: Path to CSV file with match data
        match_date: Date in YYYYMMDD format (default: today)
    """
    # Use today's date if not provided
    if match_date is None:
        match_date = datetime.now().strftime('%Y%m%d')
    
    # Validate date format
    try:
        datetime.strptime(match_date, '%Y%m%d')
    except ValueError:
        print(f"❌ Error: Invalid date format '{match_date}'. Use YYYYMMDD format.")
        return False
    
    # Check if CSV file exists
    csv_path = Path(csv_file)
    if not csv_path.exists():
        print(f"❌ Error: CSV file '{csv_file}' not found.")
        return False
    
    # Load CSV data
    print(f"📥 Loading data from {csv_file}...")
    df = pd.read_csv(csv_path)
    print(f"   Found {len(df)} players")
    
    # Connect to database
    db_path = Path('data/analysis.db')
    if not db_path.exists():
        print(f"❌ Error: Database '{db_path}' not found.")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if master table exists, create if not
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='enemy_all_stats'")
        if not cursor.fetchone():
            print(f"\n📊 Creating master table: enemy_all_stats")
            create_master_sql = """
            CREATE TABLE enemy_all_stats (
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
            cursor.execute("CREATE INDEX idx_enemy_match_date ON enemy_all_stats(match_date)")
            print(f"✓ Created enemy_all_stats master table")
        
        # Create dated table
        dated_table = f"enemy_stats_{match_date}"
        print(f"\n📊 Creating dated table: {dated_table}")
        
        # Check if table already exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{dated_table}'")
        if cursor.fetchone():
            print(f"⚠️  Warning: Table {dated_table} already exists. It will be replaced.")
            cursor.execute(f"DROP TABLE {dated_table}")
        
        # Create the dated table
        df.to_sql(dated_table, conn, if_exists='replace', index=False)
        print(f"✓ Created {dated_table} with {len(df)} rows")
        
        # Add data to master table
        print(f"\n📊 Adding data to master table: enemy_all_stats")
        df_master = df.copy()
        df_master['match_date'] = match_date
        
        # Reorder columns to have match_date first (after id)
        cols = ['match_date'] + [col for col in df_master.columns if col != 'match_date']
        df_master = df_master[cols]
        
        # Append to master table
        df_master.to_sql('enemy_all_stats', conn, if_exists='append', index=False)
        print(f"✓ Added {len(df)} rows to enemy_all_stats")
        
        # Update VIEW to show latest match
        print(f"\n🔄 Updating enemy_stats VIEW to show latest match...")
        cursor.execute("DROP VIEW IF EXISTS enemy_stats_view")
        
        # Find the latest match date
        cursor.execute("SELECT MAX(match_date) FROM enemy_all_stats")
        latest_date = cursor.fetchone()[0]
        
        # Check if current enemy_stats is a table or view
        cursor.execute("SELECT type FROM sqlite_master WHERE name='enemy_stats'")
        result = cursor.fetchone()
        
        if result and result[0] == 'table':
            # Backup current table if needed
            print(f"   Found existing enemy_stats table, backing up to enemy_stats_backup")
            cursor.execute("DROP TABLE IF EXISTS enemy_stats_backup")
            cursor.execute("CREATE TABLE enemy_stats_backup AS SELECT * FROM enemy_stats")
            cursor.execute("DROP TABLE enemy_stats")
        
        # Create VIEW that shows only the latest match
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
        WHERE match_date = '{latest_date}'
        """
        cursor.execute(view_sql)
        print(f"✓ Updated enemy_stats VIEW to show match from {latest_date}")
        
        conn.commit()
        
        # Show summary
        print(f"\n" + "="*60)
        print(f"✅ Successfully added enemy match data for {match_date}")
        print(f"="*60)
        
        # Show statistics
        cursor.execute("SELECT COUNT(DISTINCT match_date) FROM enemy_all_stats")
        total_matches = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM enemy_all_stats")
        total_records = cursor.fetchone()[0]
        
        print(f"\n📊 Database Statistics:")
        print(f"   Total matches: {total_matches}")
        print(f"   Total player records: {total_records}")
        print(f"   Latest match: {latest_date}")
        
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
    if len(sys.argv) < 2:
        print("Usage: python scripts/add_enemy_match.py <csv_file> [YYYYMMDD]")
        print("\nExample:")
        print("  python scripts/add_enemy_match.py data/enemy_team_20260119.csv 20260119")
        print("  python scripts/add_enemy_match.py data/enemy_team.csv  # Uses today's date")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    match_date = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = add_enemy_match(csv_file, match_date)
    sys.exit(0 if success else 1)
