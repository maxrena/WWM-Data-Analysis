# Match Groups Quick Reference

## What are Match Groups?

Match Groups is a date-based indexing system that makes it easy to find and compare matches across different dates. Instead of scanning through all player records, you can quickly look up matches by date and get pre-calculated statistics.

## Quick Start

### 1. Initialize Match Groups (First Time)

```bash
python scripts/manage_match_groups.py
```

This creates the `match_groups` table and indexes all existing matches.

### 2. Using Match Groups in Python

```python
from src.database import DataAnalysisDB

db = DataAnalysisDB()
db.connect()

# List all matches
matches = db.list_all_match_dates(order='DESC')
print(matches)

# Get specific match
match = db.get_match_by_date('20260118', team='both')
print(match['metadata'])  # Statistics
print(match['yb_data'])   # YB team players
print(match['enemy_data']) # Enemy team players

db.close()
```

### 3. Using Match Groups in SQL

```sql
-- Find latest match
SELECT * FROM match_groups 
ORDER BY match_date DESC LIMIT 1;

-- Find matches with high damage
SELECT match_date, yb_avg_damage, enemy_avg_damage
FROM match_groups
WHERE yb_avg_damage > 2000000
ORDER BY yb_avg_damage DESC;

-- Compare team performance
SELECT 
    match_date,
    yb_total_defeated - enemy_total_defeated as defeat_diff
FROM match_groups
WHERE yb_total_defeated > enemy_total_defeated;

-- Monthly match count
SELECT 
    SUBSTR(match_date, 1, 6) as month,
    COUNT(*) as matches
FROM match_groups
GROUP BY month;
```

## Match Groups Table Structure

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| match_date | TEXT | Match date (YYYYMMDD) |
| yb_player_count | INTEGER | Number of YB players |
| enemy_player_count | INTEGER | Number of enemy players |
| yb_total_defeated | INTEGER | Total YB team defeats |
| enemy_total_defeated | INTEGER | Total enemy team defeats |
| yb_avg_damage | REAL | Average YB damage |
| enemy_avg_damage | REAL | Average enemy damage |
| has_yb_data | INTEGER | 1 if YB data exists |
| has_enemy_data | INTEGER | 1 if enemy data exists |
| created_at | TIMESTAMP | Group creation time |
| updated_at | TIMESTAMP | Last update time |

## Automatic Updates

Match groups are automatically updated when you add new matches using:
- `scripts/add_yb_match.py`
- `scripts/add_enemy_match.py`
- `scripts/add_match.py`

## Manual Update

If you need to manually refresh the index:

```python
from src.database import DataAnalysisDB

db = DataAnalysisDB()
db.connect()
db.update_match_groups()
db.close()
```

Or run the management script:

```bash
python scripts/manage_match_groups.py
```

## Benefits

✅ **Fast Lookup** - Find matches by date instantly  
✅ **Pre-calculated Stats** - Averages and totals already computed  
✅ **Easy Comparison** - Compare matches without complex queries  
✅ **Automatic Indexing** - Updates when you add new matches  
✅ **Efficient** - Indexed on match_date for fast queries  

## Examples

### Find Best Match by Average Damage

```python
db = DataAnalysisDB()
db.connect()

query = """
    SELECT match_date, 
           (yb_avg_damage + enemy_avg_damage) / 2 as combined_avg
    FROM match_groups
    ORDER BY combined_avg DESC
    LIMIT 1
"""
best_match = db.query(query)
print(f"Best match: {best_match.iloc[0]['match_date']}")

db.close()
```

### List Matches from Last Week

```python
from datetime import datetime, timedelta

db = DataAnalysisDB()
db.connect()

# Get date 7 days ago
week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')

query = f"""
    SELECT * FROM match_groups
    WHERE match_date >= '{week_ago}'
    ORDER BY match_date DESC
"""
recent_matches = db.query(query)
print(recent_matches)

db.close()
```

### Compare Team Performance Over Time

```python
db = DataAnalysisDB()
db.connect()

matches = db.list_all_match_dates(order='ASC')

for _, match in matches.iterrows():
    yb_win = match['yb_total_defeated'] > match['enemy_total_defeated']
    status = "WIN" if yb_win else "LOSS"
    print(f"{match['match_date']}: {status} "
          f"(YB: {match['yb_total_defeated']} vs "
          f"Enemy: {match['enemy_total_defeated']})")

db.close()
```

## See Also

- [DATABASE.md](../DATABASE.md) - Complete database documentation
- [README.md](../README.md) - Project overview
- `scripts/example_match_groups.py` - More usage examples
