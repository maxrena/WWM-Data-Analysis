# Database Structure Documentation

## Overview

The database uses a **master table + dated snapshots** architecture to track match history over time.

## Table Structure

### YB Team (YoungBuffalo)

1. **youngbuffalo_stats** (Master Table)
   - Contains ALL match data from all dates
   - Columns: `id`, `match_date`, `player_name`, `defeated`, `assist`, `defeated_2`, `fun_coin`, `damage`, `tank`, `heal`, `siege_damage`
   - Primary key: `id` (auto-increment)
   - Indexed on: `match_date`

2. **yb_stats_YYYYMMDD** (Dated Snapshots)
   - Individual tables for each match date
   - Example: `yb_stats_20260118`, `yb_stats_20260119`
   - Contains only data from that specific date
   - No `match_date` column (date is in table name)

3. **yb_stats** (VIEW)
   - Virtual table showing the LATEST match
   - Always shows data from the most recent `match_date` in `youngbuffalo_stats`
   - Used by the dashboard for backward compatibility

### Enemy Team

1. **enemy_all_stats** (Master Table)
   - Contains ALL enemy match data from all dates
   - Same structure as `youngbuffalo_stats`
   - Columns: `id`, `match_date`, `player_name`, `defeated`, `assist`, `defeated_2`, `fun_coin`, `damage`, `tank`, `heal`, `siege_damage`

2. **enemy_stats_YYYYMMDD** (Dated Snapshots)
   - Individual tables for each match date
   - Example: `enemy_stats_20260118`, `enemy_stats_20260119`

3. **enemy_stats** (VIEW)
   - Virtual table showing the LATEST enemy match
   - Always shows data from the most recent `match_date` in `enemy_all_stats`

## Adding New Match Data

### For YB Team

```bash
python scripts/add_yb_match.py <csv_file> [YYYYMMDD]
```

**Examples:**
```bash
# Use today's date
python scripts/add_yb_match.py data/yb_team_new.csv

# Specify date
python scripts/add_yb_match.py data/yb_team_20260119.csv 20260119
```

**What it does:**
1. Creates `yb_stats_YYYYMMDD` table
2. Adds data to `youngbuffalo_stats` master table with `match_date`
3. Updates `yb_stats` VIEW to show the latest match

### For Enemy Team

```bash
python scripts/add_enemy_match.py <csv_file> [YYYYMMDD]
```

**Examples:**
```bash
# Use today's date
python scripts/add_enemy_match.py data/enemy_team_new.csv

# Specify date
python scripts/add_enemy_match.py data/enemy_team_20260119.csv 20260119
```

**What it does:**
1. Creates `enemy_stats_YYYYMMDD` table
2. Adds data to `enemy_all_stats` master table with `match_date`
3. Updates `enemy_stats` VIEW to show the latest match

## Migration

If you have existing `enemy_stats` table, migrate it first:

```bash
python scripts/migrate_enemy_stats.py [YYYYMMDD]
```

This will:
1. Rename `enemy_stats` → `enemy_stats_20260118`
2. Create `enemy_all_stats` master table
3. Create `enemy_stats` VIEW

## Querying Data

### Get Latest Match (Default)
```sql
-- YB Team (latest)
SELECT * FROM yb_stats;

-- Enemy Team (latest)
SELECT * FROM enemy_stats;
```

### Get Specific Match
```sql
-- YB Team for specific date
SELECT * FROM youngbuffalo_stats WHERE match_date = '20260118';

-- Or use the dated table directly
SELECT * FROM yb_stats_20260118;
```

### Get All Matches
```sql
-- All YB matches
SELECT * FROM youngbuffalo_stats;

-- All enemy matches
SELECT * FROM enemy_all_stats;
```

### Get Match History
```sql
-- List all YB match dates
SELECT DISTINCT match_date FROM youngbuffalo_stats ORDER BY match_date DESC;

-- Count players per match
SELECT match_date, COUNT(*) as player_count 
FROM youngbuffalo_stats 
GROUP BY match_date 
ORDER BY match_date DESC;
```

### Compare Across Matches
```sql
-- Player performance over time
SELECT match_date, player_name, defeated, damage
FROM youngbuffalo_stats
WHERE player_name = 'Rain'
ORDER BY match_date;

-- Team averages by match
SELECT 
    match_date,
    AVG(defeated) as avg_defeated,
    AVG(damage) as avg_damage,
    COUNT(*) as players
FROM youngbuffalo_stats
GROUP BY match_date
ORDER BY match_date DESC;
```

## Dashboard Compatibility

The dashboard uses `yb_stats` and `enemy_stats` VIEWs, which automatically show the latest match data. No code changes needed!

## CSV File Format

Both YB and Enemy CSV files should have these columns:
- `player_name` (TEXT)
- `defeated` (INTEGER)
- `assist` (INTEGER)
- `defeated_2` (INTEGER)
- `fun_coin` (INTEGER)
- `damage` (INTEGER)
- `tank` (INTEGER)
- `heal` (INTEGER)
- `siege_damage` (INTEGER)

## Utility Scripts

- `scripts/check_db.py` - List all tables and row counts
- `scripts/check_structure.py` - Show table structures and sample data
- `scripts/check_view.py` - Check if yb_stats VIEW exists

## Benefits of This Structure

1. ✅ **Historical Tracking** - Keep all match data over time
2. ✅ **Easy Comparison** - Compare performance across dates
3. ✅ **Backward Compatible** - Existing dashboard code still works
4. ✅ **Flexible** - Add new matches without losing old data
5. ✅ **Efficient** - Indexed for fast queries
6. ✅ **Organized** - Each match has its own dated table for easy reference
## Match Groups (Date-Based Indexing)

### Overview

The `match_groups` table provides a centralized index of all matches by date, making it easy to:
- Find all matches for a specific date
- Compare statistics across different match dates
- Query match metadata without scanning full player tables

### Match Groups Table Structure

```sql
CREATE TABLE match_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_date TEXT NOT NULL UNIQUE,
    yb_player_count INTEGER DEFAULT 0,
    enemy_player_count INTEGER DEFAULT 0,
    yb_total_defeated INTEGER DEFAULT 0,
    enemy_total_defeated INTEGER DEFAULT 0,
    yb_avg_damage REAL DEFAULT 0,
    enemy_avg_damage REAL DEFAULT 0,
    has_yb_data INTEGER DEFAULT 0,
    has_enemy_data INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Using Match Groups

**Initialize/Update Match Groups:**
```bash
python scripts/manage_match_groups.py
```

**In Python Code:**
```python
from database import DataAnalysisDB

db = DataAnalysisDB()
db.connect()

# List all match dates with statistics
matches = db.list_all_match_dates(order='DESC')

# Get specific match by date
match_data = db.get_match_by_date('20260118', team='both')

# Update index after adding new matches
db.update_match_groups()

db.close()
```

**SQL Queries:**
```sql
-- Find latest match
SELECT * FROM match_groups ORDER BY match_date DESC LIMIT 1;

-- Find matches with high average damage
SELECT * FROM match_groups 
WHERE yb_avg_damage > 2000000 
ORDER BY yb_avg_damage DESC;

-- Compare YB vs Enemy performance
SELECT 
    match_date,
    yb_total_defeated - enemy_total_defeated as defeat_diff,
    yb_avg_damage - enemy_avg_damage as damage_diff
FROM match_groups
ORDER BY match_date DESC;

-- Get monthly match counts
SELECT 
    SUBSTR(match_date, 1, 6) as month,
    COUNT(*) as match_count
FROM match_groups
GROUP BY month;
```

### Benefits

- **Fast Lookup**: Indexed by date for instant retrieval
- **Statistics at a Glance**: Pre-calculated averages and totals
- **Easy Filtering**: Find matches by criteria without scanning player tables
- **Maintenance**: Auto-updates with `db.update_match_groups()`