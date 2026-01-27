"""
Manage Match Groups - Create and maintain date-based match groupings
This script creates a match_groups table that indexes all matches by date
for easy lookup and comparison.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))
from database import DataAnalysisDB


def main():
    """Initialize and update match groups."""
    print("=" * 60)
    print("Match Groups Manager")
    print("=" * 60)
    
    # Connect to database
    db = DataAnalysisDB()
    db.connect()
    
    # Create match_groups table
    print("\n1. Creating match_groups table...")
    db.create_match_groups_table()
    
    # Update with existing match data
    print("\n2. Indexing all existing matches...")
    count = db.update_match_groups()
    
    # Display summary
    print("\n" + "=" * 60)
    print("Match Groups Summary")
    print("=" * 60)
    
    groups = db.list_all_match_dates(order='DESC')
    
    if groups.empty:
        print("No match groups found.")
    else:
        print(f"\nTotal match dates: {len(groups)}")
        print(f"\nRecent matches:")
        print(groups.head(10).to_string(index=False))
        
        # Statistics
        total_yb = groups['yb_player_count'].sum()
        total_enemy = groups['enemy_player_count'].sum()
        print(f"\n📊 Overall Statistics:")
        print(f"   Total YB player records: {total_yb}")
        print(f"   Total Enemy player records: {total_enemy}")
        print(f"   Matches with YB data: {groups['has_yb_data'].sum()}")
        print(f"   Matches with Enemy data: {groups['has_enemy_data'].sum()}")
    
    # Close connection
    db.close()
    
    print("\n✓ Match groups successfully created and indexed!")
    print("\nYou can now easily find matches by date using:")
    print("  - db.list_all_match_dates()")
    print("  - db.get_match_by_date('20260118')")


if __name__ == "__main__":
    main()
