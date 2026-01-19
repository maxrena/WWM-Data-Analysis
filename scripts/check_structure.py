import sqlite3
import pandas as pd

conn = sqlite3.connect('data/analysis.db')

print("=== youngbuffalo_stats structure ===")
df = pd.read_sql_query("PRAGMA table_info(youngbuffalo_stats)", conn)
print(df)

print("\n=== Sample data from youngbuffalo_stats ===")
df = pd.read_sql_query("SELECT * FROM youngbuffalo_stats LIMIT 3", conn)
print(df)

print("\n=== yb_stats_20260118 structure ===")
df = pd.read_sql_query("PRAGMA table_info(yb_stats_20260118)", conn)
print(df)

conn.close()
