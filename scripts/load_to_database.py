"""
Script to load player stats data into SQLite database.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from database import DataAnalysisDB
import pandas as pd


def main():
    """Load player stats CSV into database."""
    
    # Paths
    csv_path = Path(__file__).parent.parent / 'data' / 'raw' / 'player_stats.csv'
    db_path = Path(__file__).parent.parent / 'data' / 'analysis.db'
    
    print("=" * 60)
    print("Loading Player Stats into Database")
    print("=" * 60)
    
    # Read CSV to clean column names
    df = pd.read_csv(csv_path)
    
    # Clean column names for database (remove spaces, use snake_case)
    column_mapping = {
        'Player Info': 'player_name',
        'Defeated': 'defeated',
        'Assist': 'assist',
        'Fun Coin': 'fun_coin',
        'Damage': 'damage',
        'Tank': 'tank',
        'Heal': 'heal',
        'Siege Damage': 'siege_damage'
    }
    
    # Handle duplicate 'Defeated' column
    df.columns = ['Player Info', 'Defeated', 'Assist', 'Defeated_2', 
                  'Fun Coin', 'Damage', 'Tank', 'Heal', 'Siege Damage']
    
    # Rename columns
    df = df.rename(columns={
        'Player Info': 'player_name',
        'Defeated': 'defeated',
        'Assist': 'assist',
        'Defeated_2': 'defeated_2',
        'Fun Coin': 'fun_coin',
        'Damage': 'damage',
        'Tank': 'tank',
        'Heal': 'heal',
        'Siege Damage': 'siege_damage'
    })
    
    print(f"\nData loaded: {len(df)} players")
    print(f"Columns: {', '.join(df.columns)}")
    
    # Create database and load data
    with DataAnalysisDB(db_path) as db:
        # Load data
        df.to_sql('yb_stats', db.conn, if_exists='replace', index=False)
        print(f"\n✓ Loaded {len(df)} rows into 'yb_stats' table")
        
        # Create indexes for better query performance
        print("\nCreating indexes...")
        db.execute("CREATE INDEX IF NOT EXISTS idx_player_name ON yb_stats(player_name);")
        db.execute("CREATE INDEX IF NOT EXISTS idx_defeated ON yb_stats(defeated DESC);")
        db.execute("CREATE INDEX IF NOT EXISTS idx_damage ON yb_stats(damage DESC);")
        
        # Show summary
        print("\n" + "=" * 60)
        print("Database Summary")
        print("=" * 60)
        
        stats = db.get_table_stats('yb_stats')
        print(f"Table: {stats['table_name']}")
        print(f"Rows: {stats['row_count']}")
        print(f"Columns: {stats['column_count']}")
        
        # Show top 5 players by defeated
        print("\n" + "=" * 60)
        print("Top 5 Players by Defeated")
        print("=" * 60)
        top_players = db.query("""
            SELECT player_name, defeated, damage, assist
            FROM yb_stats
            ORDER BY defeated DESC
            LIMIT 5
        """)
        print(top_players.to_string(index=False))
        
        print("\n✓ Database setup complete!")
        print(f"Database location: {db_path}")


if __name__ == "__main__":
    main()
