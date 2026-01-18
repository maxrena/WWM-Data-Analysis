"""
Data loading utilities for the WWM Data Analysis project.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Union, Optional


def load_csv(
    filepath: Union[str, Path],
    **kwargs
) -> pd.DataFrame:
    """
    Load a CSV file into a pandas DataFrame.
    
    Args:
        filepath: Path to the CSV file
        **kwargs: Additional arguments to pass to pd.read_csv()
    
    Returns:
        pd.DataFrame: Loaded data
    """
    return pd.read_csv(filepath, **kwargs)


def load_excel(
    filepath: Union[str, Path],
    sheet_name: Optional[Union[str, int]] = 0,
    **kwargs
) -> pd.DataFrame:
    """
    Load an Excel file into a pandas DataFrame.
    
    Args:
        filepath: Path to the Excel file
        sheet_name: Name or index of the sheet to load
        **kwargs: Additional arguments to pass to pd.read_excel()
    
    Returns:
        pd.DataFrame: Loaded data
    """
    return pd.read_excel(filepath, sheet_name=sheet_name, **kwargs)


def save_processed_data(
    df: pd.DataFrame,
    filename: str,
    output_dir: Union[str, Path] = "data/processed",
    file_format: str = "csv"
) -> None:
    """
    Save processed data to a file.
    
    Args:
        df: DataFrame to save
        filename: Name of the output file
        output_dir: Directory to save the file in
        file_format: Format to save in ('csv' or 'parquet')
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    filepath = output_path / filename
    
    if file_format == "csv":
        df.to_csv(filepath, index=False)
    elif file_format == "parquet":
        df.to_parquet(filepath, index=False)
    else:
        raise ValueError(f"Unsupported format: {file_format}")
    
    print(f"Data saved to {filepath}")
