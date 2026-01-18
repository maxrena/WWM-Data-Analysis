"""
Add new match data to YoungBuffalo stats history
Usage: python scripts/add_match_data.py <csv_file> [match_date]
"""

import sys
import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path

def add_match_data(csv_path, match_date=None):
    """
    Add match data to the youngbuffalo_stats table
    
    Args:
        csv_path: Path to CSV file with match data
        match_date: Match date in YYYYMMDD format (defaults to today)
    """
    if match_date is None:
        match_date = datetime.now().strftime('%Y%m%d')
    
    # Read CSV
    df = pd.read_csv(csv_path)
    
    # Add match_date column
    df.insert(0, 'match_date', match_date)
    
    # Database path
    db_path = Path(__file__).parent.parent / 'data' / 'analysis.db'
    
    print(f"Adding match data for date: {match_date}")
    print(f"Players: {len(df)}")
    
    with sqlite3.connect(db_path) as conn:
        # Check if this match date already exists
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM youngbuffalo_stats WHERE match_date = ?",
            (match_date,)
        )
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0:
            print(f"\n⚠ Warning: Match date {match_date} already has {existing_count} records")
            response = input("Replace existing data? (yes/no): ")
            if response.lower() != 'yes':
                print("Cancelled.")
                return
            
            # Delete existing records for this date
            cursor.execute(
                "DELETE FROM youngbuffalo_stats WHERE match_date = ?",
                (match_date,)
            )
            print(f"Deleted {existing_count} existing records")
        
        # Insert new data
        df.to_sql('youngbuffalo_stats', conn, if_exists='append', index=False)
        
        # Create match-specific table for this date
        table_name = f'yb_stats_{match_date}'
        df_without_date = df.drop(columns=['match_date'])
        df_without_date.to_sql(table_name, conn, if_exists='replace', index=False)
        
        print(f"\n✓ Added {len(df)} records to 'youngbuffalo_stats'")
        print(f"✓ Created table '{table_name}'")
        
        # Update the yb_stats view to show latest match
        cursor.execute("DROP VIEW IF EXISTS yb_stats")
        cursor.execute(f"""
            CREATE VIEW yb_stats AS
            SELECT 
                player_name, defeated, assist, defeated_2, fun_coin,
                damage, tank, heal, siege_damage
            FROM youngbuffalo_stats
            WHERE match_date = (SELECT MAX(match_date) FROM youngbuffalo_stats)
        """)
        print(f"✓ Updated 'yb_stats' view to show latest match ({match_date})")
        
        # Show summary
        cursor.execute("SELECT DISTINCT match_date FROM youngbuffalo_stats ORDER BY match_date DESC")
        dates = [row[0] for row in cursor.fetchall()]
        print(f"\nAll match dates: {', '.join(dates)}")
        
        cursor.execute("SELECT COUNT(*) FROM youngbuffalo_stats")
        total = cursor.fetchone()[0]
        print(f"Total records in master table: {total}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/add_match_data.py <csv_file> [match_date]")
        print("Example: python scripts/add_match_data.py data/raw/player_stats.csv 20260118")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    match_date = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not Path(csv_file).exists():
        print(f"Error: File '{csv_file}' not found")
        sys.exit(1)
    
    add_match_data(csv_file, match_date)
