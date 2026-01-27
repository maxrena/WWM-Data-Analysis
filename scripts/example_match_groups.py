"""
Example usage of the match_groups feature
Demonstrates how to find and query matches by date
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))
from database import DataAnalysisDB


def example_list_all_dates():
    """Example: List all match dates"""
    print("\n" + "=" * 60)
    print("Example 1: List All Match Dates")
    print("=" * 60)
    
    db = DataAnalysisDB()
    db.connect()
    
    # Get all match dates with statistics
    matches = db.list_all_match_dates(order='DESC')
    
    print(f"\nFound {len(matches)} match dates:")
    print(matches.to_string(index=False))
    
    db.close()


def example_get_specific_match():
    """Example: Get data for a specific match date"""
    print("\n" + "=" * 60)
    print("Example 2: Get Specific Match by Date")
    print("=" * 60)
    
    db = DataAnalysisDB()
    db.connect()
    
    # Get match data for January 18, 2026
    match_date = '20260118'
    match_data = db.get_match_by_date(match_date, team='both')
    
    print(f"\nMatch Date: {match_date}")
    
    if 'metadata' in match_data:
        print("\nMetadata:")
        for key, value in match_data['metadata'].items():
            print(f"  {key}: {value}")
    
    if 'yb_data' in match_data:
        yb_df = match_data['yb_data']
        print(f"\nYoungBuffalo Team ({len(yb_df)} players):")
        print(yb_df[['player_name', 'defeated', 'damage', 'heal']].to_string(index=False))
    
    if 'enemy_data' in match_data:
        enemy_df = match_data['enemy_data']
        print(f"\nEnemy Team ({len(enemy_df)} players):")
        print(enemy_df[['player_name', 'defeated', 'damage', 'heal']].head(10).to_string(index=False))
    
    db.close()


def example_compare_matches():
    """Example: Compare statistics across multiple matches"""
    print("\n" + "=" * 60)
    print("Example 3: Compare Match Statistics")
    print("=" * 60)
    
    db = DataAnalysisDB()
    db.connect()
    
    # Get all matches with their stats
    matches = db.list_all_match_dates(order='ASC')
    
    print("\nMatch Comparison:")
    print(f"{'Date':<12} {'YB Players':<12} {'Enemy Players':<15} {'YB Avg Dmg':<15} {'Enemy Avg Dmg':<15}")
    print("-" * 70)
    
    for _, row in matches.iterrows():
        print(f"{row['match_date']:<12} {row['yb_player_count']:<12} {row['enemy_player_count']:<15} "
              f"{row['yb_avg_damage']:<15,.0f} {row['enemy_avg_damage']:<15,.0f}")
    
    db.close()


def example_query_by_date():
    """Example: Custom SQL query using match groups"""
    print("\n" + "=" * 60)
    print("Example 4: Custom Query with Match Groups")
    print("=" * 60)
    
    db = DataAnalysisDB()
    db.connect()
    
    # Find matches where YB had more total defeats than enemy
    query = """
        SELECT 
            match_date,
            yb_total_defeated,
            enemy_total_defeated,
            (yb_total_defeated - enemy_total_defeated) as defeat_difference
        FROM match_groups
        WHERE yb_total_defeated > enemy_total_defeated
        ORDER BY defeat_difference DESC
    """
    
    results = db.query(query)
    
    if results.empty:
        print("\nNo matches where YB had more defeats than enemy.")
    else:
        print(f"\nMatches where YB won (more defeats):")
        print(results.to_string(index=False))
    
    db.close()


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("Match Groups - Usage Examples")
    print("=" * 60)
    
    example_list_all_dates()
    example_get_specific_match()
    example_compare_matches()
    example_query_by_date()
    
    print("\n" + "=" * 60)
    print("Quick Reference")
    print("=" * 60)
    print("""
Available Methods:
  
  db.list_all_match_dates(order='DESC')
    - List all match dates with statistics
    - order: 'ASC' or 'DESC'
  
  db.get_match_by_date(match_date, team='both')
    - Get detailed data for a specific date
    - match_date: 'YYYYMMDD' format
    - team: 'yb', 'enemy', or 'both'
  
  db.update_match_groups()
    - Refresh the match groups index
    - Run after adding new matches
    
Example Queries:
  
  # Get latest match
  SELECT * FROM match_groups ORDER BY match_date DESC LIMIT 1
  
  # Find high-damage matches
  SELECT * FROM match_groups 
  WHERE yb_avg_damage > 2000000 
  ORDER BY yb_avg_damage DESC
  
  # Get match count per month
  SELECT SUBSTR(match_date, 1, 6) as month, COUNT(*) as matches
  FROM match_groups
  GROUP BY month
    """)


if __name__ == "__main__":
    main()
