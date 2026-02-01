"""
Generic Match Data Insertion Function
Reusable utility for extracting and inserting match data for any match/date

This replaces the need for individual insert_match_XX.py scripts.
Usage example:
  python generic_match_insert.py --match-date 20260118 --match-id 03 --team yb \
    --data "Ztee:16:121:3:0:6896682:2071659:0:773143" \
    --data "Whiskey:16:74:3:9200:4021734:776496:0:206036" ...
"""

import sys
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple
import argparse
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from database import DataAnalysisDB
from match_ingest import normalize_match_id, insert_team_stats, validate_columns


class MatchDataInserter:
    """Generic match data insertion utility"""
    
    def __init__(self, db_path: str = "data/analysis.db"):
        """Initialize with database connection"""
        self.db = DataAnalysisDB(db_path)
        self.db.connect()
    
    def insert_match(
        self,
        match_date: str,
        match_id: str,
        team: str,
        player_data: List[Dict]
    ) -> Tuple[int, int]:
        """
        Insert match data for a team.
        
        Args:
            match_date: Date in YYYYMMDD format
            match_id: Session ID (e.g., '01', '02', '03')
            team: 'yb' or 'enemy'
            player_data: List of dicts with player stats
        
        Returns:
            Tuple of (session_rows_inserted, aggregate_rows_inserted)
        """
        
        df = pd.DataFrame(player_data)
        cleaned = validate_columns(df)
        match_key = normalize_match_id(match_date, match_id)
        insert_team_stats(self.db.conn, team, match_key, cleaned)
        session_rows = len(cleaned)
        agg_rows = len(cleaned)
        
        # Update match groups
        self.db.update_match_groups()
        
        return session_rows, agg_rows
    
    def close(self):
        """Close database connection"""
        self.db.close()


def main():
    """Command-line interface for match data insertion"""
    parser = argparse.ArgumentParser(
        description='Generic match data insertion utility'
    )
    parser.add_argument('--match-date', required=True, help='Date in YYYYMMDD format')
    parser.add_argument('--match-id', required=True, help='Session ID (01, 02, 03, etc.)')
    parser.add_argument('--team', required=True, choices=['yb', 'enemy'], help='Team')
    parser.add_argument('--json-file', help='JSON file with player data')
    
    args = parser.parse_args()
    
    # Load player data from JSON file
    if args.json_file:
        with open(args.json_file, 'r') as f:
            payload = json.load(f)
    else:
        print("Error: --json-file is required")
        sys.exit(1)

    if isinstance(payload, dict) and "players" in payload:
        player_data = payload["players"]
    else:
        player_data = payload
    
    # Insert data
    inserter = MatchDataInserter()
    session_rows, agg_rows = inserter.insert_match(
        match_date=args.match_date,
        match_id=args.match_id,
        team=args.team,
        player_data=player_data
    )
    
    print(f"✓ Inserted {session_rows} players into session table")
    print(f"✓ Inserted {agg_rows} players into aggregate table")
    
    inserter.close()


if __name__ == "__main__":
    main()
