"""
Add new match data for both YB and Enemy teams.

This script adds data for both teams from the same match.

Usage:
    python scripts/add_match.py <yb_csv> <enemy_csv> [date]
    
    If date is not provided, today's date will be used (YYYYMMDD format)
"""

import sys
from pathlib import Path
from datetime import datetime

# Import the individual add functions
import add_yb_match
import add_enemy_match


def add_match(yb_csv: str, enemy_csv: str, match_date: str = None):
    """
    Add match data for both teams.
    
    Args:
        yb_csv: Path to YB team CSV file
        enemy_csv: Path to enemy team CSV file
        match_date: Date in YYYYMMDD format (default: today)
    """
    # Use today's date if not provided
    if match_date is None:
        match_date = datetime.now().strftime('%Y%m%d')
    
    print("="*60)
    print(f"Adding Match Data for {match_date}")
    print("="*60)
    
    # Add YB team data
    print("\n🟢 Adding YB Team Data...")
    print("-" * 60)
    yb_success = add_yb_match.add_yb_match(yb_csv, match_date)
    
    if not yb_success:
        print("\n❌ Failed to add YB team data. Aborting.")
        return False
    
    # Add Enemy team data
    print("\n🔴 Adding Enemy Team Data...")
    print("-" * 60)
    enemy_success = add_enemy_match.add_enemy_match(enemy_csv, match_date)
    
    if not enemy_success:
        print("\n❌ Failed to add enemy team data.")
        print("⚠️  YB team data was added successfully, but enemy data failed.")
        return False
    
    # Success summary
    print("\n" + "="*60)
    print(f"✅ Match data for {match_date} added successfully!")
    print("="*60)
    print("\n📊 Both teams' data have been added to:")
    print(f"   - Master tables: youngbuffalo_stats, enemy_all_stats")
    print(f"   - Dated tables: yb_stats_{match_date}, enemy_stats_{match_date}")
    print(f"   - VIEWs updated: yb_stats, enemy_stats")
    print("\n🎮 The dashboard will now show the latest match data!")
    
    return True


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/add_match.py <yb_csv> <enemy_csv> [YYYYMMDD]")
        print("\nExample:")
        print("  python scripts/add_match.py data/yb_20260119.csv data/enemy_20260119.csv 20260119")
        print("  python scripts/add_match.py data/yb_new.csv data/enemy_new.csv  # Uses today")
        sys.exit(1)
    
    yb_csv = sys.argv[1]
    enemy_csv = sys.argv[2]
    match_date = sys.argv[3] if len(sys.argv) > 3 else None
    
    success = add_match(yb_csv, enemy_csv, match_date)
    sys.exit(0 if success else 1)
