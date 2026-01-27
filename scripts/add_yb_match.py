"""
Add new match data to the master database.

This script:
1. Takes a CSV file with match data
2. Creates a dated table (e.g., yb_stats_20260119)
3. Adds the data to the master youngbuffalo_stats table with the match date
4. Updates the yb_stats VIEW to show the latest match data
5. Updates match groups index for easy date-based lookup

Usage:
    python scripts/add_yb_match.py <csv_file> [date]
    
    If date is not provided, today's date will be used (YYYYMMDD format)
"""

import sys
import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path

# Add src to path for database module
sys.path.append(str(Path(__file__).parent.parent / 'src'))

def add_yb_match(csv_file: str, match_date: str = None):
    """
    Add new YB team match data to the database.
    
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
        # Create dated table
        dated_table = f"yb_stats_{match_date}"
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
        print(f"\n📊 Adding data to master table: youngbuffalo_stats")
        df_master = df.copy()
        df_master['match_date'] = match_date
        
        # Reorder columns to have match_date first (after id)
        cols = ['match_date'] + [col for col in df_master.columns if col != 'match_date']
        df_master = df_master[cols]
        
        # Append to master table
        df_master.to_sql('youngbuffalo_stats', conn, if_exists='append', index=False)
        print(f"✓ Added {len(df)} rows to youngbuffalo_stats")
        
        # Update VIEW to show latest match
        print(f"\n🔄 Updating yb_stats VIEW to show latest match...")
        cursor.execute("DROP VIEW IF EXISTS yb_stats")
        
        # Find the latest match date
        cursor.execute("SELECT MAX(match_date) FROM youngbuffalo_stats")
        latest_date = cursor.fetchone()[0]
        
        # Create VIEW that shows only the latest match
        view_sql = f"""
        CREATE VIEW yb_stats AS
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
        FROM youngbuffalo_stats
        WHERE match_date = '{latest_date}'
        """
        cursor.execute(view_sql)
        print(f"✓ Updated yb_stats VIEW to show match from {latest_date}")
        
        # Create index on match_date if it doesn't exist
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_yb_match_date 
            ON youngbuffalo_stats(match_date)
        """)
        
        conn.commit()
        
        # Update match groups
        print(f"\n📑 Updating match groups index...")
        from database import DataAnalysisDB
        db = DataAnalysisDB()
        db.connect()
        db.create_match_groups_table()
        db.update_match_groups()
        db.close()
        
        # Show summary
        print(f"\n" + "="*60)
        print(f"✅ Successfully added match data for {match_date}")
        print(f"="*60)
        
        # Show statistics
        cursor.execute("SELECT COUNT(DISTINCT match_date) FROM youngbuffalo_stats")
        total_matches = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM youngbuffalo_stats")
        total_records = cursor.fetchone()[0]
        
        print(f"\n📊 Database Statistics:")
        print(f"   Total matches: {total_matches}")
        print(f"   Total player records: {total_records}")
        print(f"   Latest match: {latest_date}")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error: {e}")
        return False
        
    finally:
        conn.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/add_yb_match.py <csv_file> [YYYYMMDD]")
        print("\nExample:")
        print("  python scripts/add_yb_match.py data/yb_team_20260119.csv 20260119")
        print("  python scripts/add_yb_match.py data/yb_team.csv  # Uses today's date")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    match_date = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = add_yb_match(csv_file, match_date)
    sys.exit(0 if success else 1)
