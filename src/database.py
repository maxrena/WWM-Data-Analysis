"""
Database utilities for WWM Data Analysis project.
Uses SQLite for efficient data analysis and querying.
"""

import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, List, Union


class DataAnalysisDB:
    """SQLite database manager for data analysis."""
    
    def __init__(self, db_path: str = "data/analysis.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        
    def connect(self):
        """Establish database connection with thread-safe settings."""
        # Use check_same_thread=False for Streamlit compatibility
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return self.conn
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def load_csv_to_table(
        self, 
        csv_path: Union[str, Path], 
        table_name: str,
        if_exists: str = 'replace'
    ) -> int:
        """
        Load CSV file into database table.
        
        Args:
            csv_path: Path to CSV file
            table_name: Name of the database table
            if_exists: How to behave if table exists ('fail', 'replace', 'append')
        
        Returns:
            Number of rows inserted
        """
        df = pd.read_csv(csv_path)
        
        if not self.conn:
            self.connect()
        
        df.to_sql(table_name, self.conn, if_exists=if_exists, index=False)
        print(f"[OK] Loaded {len(df)} rows into table '{table_name}'")
        
        return len(df)
    
    def query(self, sql: str) -> pd.DataFrame:
        """
        Execute SQL query and return results as DataFrame.
        
        Args:
            sql: SQL query string
        
        Returns:
            Query results as DataFrame
        """
        if not self.conn:
            self.connect()
        
        return pd.read_sql_query(sql, self.conn)
    
    def execute(self, sql: str) -> None:
        """
        Execute SQL statement (INSERT, UPDATE, DELETE, etc.).
        
        Args:
            sql: SQL statement
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute(sql)
        self.conn.commit()
        print(f"[OK] Executed: {sql[:50]}...")
    
    def list_tables(self) -> List[str]:
        """
        List all tables in the database.
        
        Returns:
            List of table names
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        return tables
    
    def table_info(self, table_name: str) -> pd.DataFrame:
        """
        Get information about table columns.
        
        Args:
            table_name: Name of the table
        
        Returns:
            DataFrame with column information
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = ['cid', 'name', 'type', 'notnull', 'dflt_value', 'pk']
        return pd.DataFrame(cursor.fetchall(), columns=columns)
    
    def get_table_stats(self, table_name: str) -> dict:
        """
        Get basic statistics about a table.
        
        Args:
            table_name: Name of the table
        
        Returns:
            Dictionary with table statistics
        """
        df = self.query(f"SELECT COUNT(*) as row_count FROM {table_name}")
        row_count = df['row_count'].iloc[0]
        
        columns = self.table_info(table_name)
        col_count = len(columns)
        
        return {
            'table_name': table_name,
            'row_count': row_count,
            'column_count': col_count,
            'columns': columns['name'].tolist()
        }
    
    def export_table_to_csv(
        self, 
        table_name: str, 
        output_path: Union[str, Path]
    ) -> None:
        """
        Export table to CSV file.
        
        Args:
            table_name: Name of the table to export
            output_path: Path for output CSV file
        """
        df = self.query(f"SELECT * FROM {table_name}")
        df.to_csv(output_path, index=False)
        print(f"[OK] Exported {len(df)} rows to {output_path}")
    
    def create_match_groups_table(self) -> None:
        """
        Create match_groups table for date-based match organization.
        This table stores metadata about each match date for easy indexing.
        """
        schema_sql = """
        CREATE TABLE IF NOT EXISTS match_groups (
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
        
        CREATE INDEX IF NOT EXISTS idx_match_date ON match_groups(match_date);
        CREATE INDEX IF NOT EXISTS idx_created_at ON match_groups(created_at);
        """
        
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        for statement in schema_sql.split(';'):
            if statement.strip():
                cursor.execute(statement)
        
        self.conn.commit()
        print("[OK] Created match_groups table with indexes")
    
    def update_match_groups(self) -> int:
        """
        Update match_groups table with statistics from all match dates.
        This indexes all matches by date for easy lookup.
        
        Returns:
            Number of match groups created/updated
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        # Get all unique match dates from both YB and enemy tables
        yb_dates_query = """
            SELECT DISTINCT match_date 
            FROM youngbuffalo_stats 
            WHERE match_date IS NOT NULL
        """
        
        enemy_dates_query = """
            SELECT DISTINCT match_date 
            FROM enemy_all_stats 
            WHERE match_date IS NOT NULL
        """
        
        # Combine all dates
        all_dates = set()
        try:
            cursor.execute(yb_dates_query)
            all_dates.update([row[0] for row in cursor.fetchall()])
        except sqlite3.OperationalError:
            pass  # Table might not exist
        
        try:
            cursor.execute(enemy_dates_query)
            all_dates.update([row[0] for row in cursor.fetchall()])
        except sqlite3.OperationalError:
            pass  # Table might not exist
        
        count = 0
        for match_date in sorted(all_dates):
            # Calculate YB stats
            yb_stats = cursor.execute("""
                SELECT 
                    COUNT(*) as player_count,
                    COALESCE(SUM(defeated), 0) as total_defeated,
                    COALESCE(AVG(damage), 0) as avg_damage
                FROM youngbuffalo_stats
                WHERE match_date = ?
            """, (match_date,)).fetchone()
            
            # Calculate enemy stats
            enemy_stats = cursor.execute("""
                SELECT 
                    COUNT(*) as player_count,
                    COALESCE(SUM(defeated), 0) as total_defeated,
                    COALESCE(AVG(damage), 0) as avg_damage
                FROM enemy_all_stats
                WHERE match_date = ?
            """, (match_date,)).fetchone()
            
            # Insert or replace match group
            cursor.execute("""
                INSERT OR REPLACE INTO match_groups (
                    match_date,
                    yb_player_count,
                    enemy_player_count,
                    yb_total_defeated,
                    enemy_total_defeated,
                    yb_avg_damage,
                    enemy_avg_damage,
                    has_yb_data,
                    has_enemy_data,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                match_date,
                yb_stats[0], enemy_stats[0],
                yb_stats[1], enemy_stats[1],
                yb_stats[2], enemy_stats[2],
                1 if yb_stats[0] > 0 else 0,
                1 if enemy_stats[0] > 0 else 0
            ))
            count += 1
        
        self.conn.commit()
        print(f"[OK] Updated {count} match groups")
        return count
    
    def get_match_by_date(self, match_date: str, team: str = 'both') -> dict:
        """
        Get all match data for a specific date.
        
        Args:
            match_date: Date in YYYYMMDD format
            team: Which team data to retrieve ('yb', 'enemy', or 'both')
        
        Returns:
            Dictionary with match data and metadata
        """
        if not self.conn:
            self.connect()
        
        result = {'match_date': match_date}
        
        # Get match group metadata
        group = self.query(f"SELECT * FROM match_groups WHERE match_date = '{match_date}'")
        if not group.empty:
            result['metadata'] = group.iloc[0].to_dict()
        
        # Get YB data
        if team in ['yb', 'both']:
            yb_data = self.query(f"SELECT * FROM youngbuffalo_stats WHERE match_date = '{match_date}'")
            result['yb_data'] = yb_data
        
        # Get enemy data
        if team in ['enemy', 'both']:
            enemy_data = self.query(f"SELECT * FROM enemy_all_stats WHERE match_date = '{match_date}'")
            result['enemy_data'] = enemy_data
        
        return result
    
    def list_all_match_dates(self, order: str = 'DESC') -> pd.DataFrame:
        """
        List all match dates with summary statistics.
        
        Args:
            order: Sort order ('ASC' or 'DESC')
        
        Returns:
            DataFrame with match dates and statistics
        """
        if not self.conn:
            self.connect()
        
        query = f"""
            SELECT 
                match_date,
                yb_player_count,
                enemy_player_count,
                yb_total_defeated,
                enemy_total_defeated,
                ROUND(yb_avg_damage, 2) as yb_avg_damage,
                ROUND(enemy_avg_damage, 2) as enemy_avg_damage,
                has_yb_data,
                has_enemy_data,
                created_at,
                updated_at
            FROM match_groups
            ORDER BY match_date {order}
        """
        
        return self.query(query)


def create_player_stats_schema(db: DataAnalysisDB) -> None:
    """
    Create optimized schema for player statistics.
    
    Args:
        db: Database instance
    """
    schema_sql = """
    CREATE TABLE IF NOT EXISTS player_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_name TEXT NOT NULL,
        defeated INTEGER,
        assist INTEGER,
        defeated_2 INTEGER,
        fun_coin INTEGER,
        damage INTEGER,
        tank INTEGER,
        heal INTEGER,
        siege_damage INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE INDEX IF NOT EXISTS idx_player_name ON player_stats(player_name);
    CREATE INDEX IF NOT EXISTS idx_defeated ON player_stats(defeated);
    CREATE INDEX IF NOT EXISTS idx_damage ON player_stats(damage);
    """
    
    if not db.conn:
        db.connect()
    
    cursor = db.conn.cursor()
    for statement in schema_sql.split(';'):
        if statement.strip():
            cursor.execute(statement)
    
    db.conn.commit()
    print("[OK] Created player_stats schema with indexes")
