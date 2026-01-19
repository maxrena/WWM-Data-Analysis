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
        print(f"✓ Loaded {len(df)} rows into table '{table_name}'")
        
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
        print(f"✓ Executed: {sql[:50]}...")
    
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
        print(f"✓ Exported {len(df)} rows to {output_path}")


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
    print("✓ Created player_stats schema with indexes")
