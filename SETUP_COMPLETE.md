# Database Structure Summary

## ✅ Completed Setup

Your database now has a **master table architecture** for tracking match history!

## 📊 Current Structure

### YB Team (YoungBuffalo)
- ✅ **youngbuffalo_stats** - Master table with ALL matches (30 records from 1 match)
- ✅ **yb_stats_20260118** - Dated snapshot table
- ✅ **yb_stats** - VIEW showing latest match (backward compatible)

### Enemy Team  
- ✅ **enemy_all_stats** - Master table with ALL matches (31 records from 1 match)
- ✅ **enemy_stats_20260118** - Dated snapshot table
- ✅ **enemy_stats** - VIEW showing latest match (backward compatible)

## 🎮 How to Add New Match Data

### Option 1: Add Both Teams (Recommended)
```bash
python scripts/add_match.py data/yb_new.csv data/enemy_new.csv 20260119
```

### Option 2: Add Teams Separately
```bash
# YB Team
python scripts/add_yb_match.py data/yb_new.csv 20260119

# Enemy Team
python scripts/add_enemy_match.py data/enemy_new.csv 20260119
```

### What Happens When You Add Data:
1. Creates new dated table: `yb_stats_20260119`
2. Adds records to master table with `match_date = '20260119'`
3. Updates VIEW to show the latest match
4. Dashboard automatically displays the new data!

## 📖 Documentation

- **DATABASE.md** - Complete database documentation with SQL query examples
- **README.md** - Updated with database info and usage instructions

## 🔍 Utility Scripts

- `scripts/check_db.py` - List all tables and row counts
- `scripts/check_structure.py` - Show table structures
- `scripts/check_view.py` - Check if VIEWs exist

## 🚀 Dashboard Compatibility

Your dashboard (`app.py`) still works perfectly! It uses the `yb_stats` and `enemy_stats` VIEWs which automatically show the latest match data.

**No code changes needed!**

## 📝 CSV File Format

When adding new data, your CSV files should have these columns:
- player_name
- defeated
- assist
- defeated_2
- fun_coin
- damage
- tank
- heal
- siege_damage

## 🎯 Next Steps

1. When you have new match data, save it as CSV files
2. Run the appropriate script to add it to the database
3. The dashboard will automatically show the latest match!

## 📈 Query Examples

### Get all matches:
```sql
SELECT DISTINCT match_date FROM youngbuffalo_stats ORDER BY match_date DESC;
```

### Compare player performance over time:
```sql
SELECT match_date, player_name, defeated, damage
FROM youngbuffalo_stats
WHERE player_name = 'Rain'
ORDER BY match_date;
```

### Team averages by match:
```sql
SELECT 
    match_date,
    AVG(defeated) as avg_defeated,
    AVG(damage) as avg_damage
FROM youngbuffalo_stats
GROUP BY match_date
ORDER BY match_date DESC;
```

---

**All changes pushed to GitHub!** 🎉
