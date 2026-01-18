"""
Data preprocessing utilities for the WWM Data Analysis project.
"""

import pandas as pd
import numpy as np
from typing import List, Optional, Union


def handle_missing_values(
    df: pd.DataFrame,
    strategy: str = "drop",
    fill_value: Optional[Union[int, float, str]] = None,
    columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Handle missing values in a DataFrame.
    
    Args:
        df: Input DataFrame
        strategy: Strategy to handle missing values ('drop', 'fill', 'forward', 'backward')
        fill_value: Value to fill if strategy is 'fill'
        columns: Specific columns to apply the strategy to
    
    Returns:
        pd.DataFrame: DataFrame with handled missing values
    """
    df_copy = df.copy()
    target_cols = columns if columns else df_copy.columns
    
    if strategy == "drop":
        df_copy = df_copy.dropna(subset=target_cols)
    elif strategy == "fill":
        df_copy[target_cols] = df_copy[target_cols].fillna(fill_value)
    elif strategy == "forward":
        df_copy[target_cols] = df_copy[target_cols].fillna(method='ffill')
    elif strategy == "backward":
        df_copy[target_cols] = df_copy[target_cols].fillna(method='bfill')
    else:
        raise ValueError(f"Unknown strategy: {strategy}")
    
    return df_copy


def remove_duplicates(
    df: pd.DataFrame,
    subset: Optional[List[str]] = None,
    keep: str = "first"
) -> pd.DataFrame:
    """
    Remove duplicate rows from a DataFrame.
    
    Args:
        df: Input DataFrame
        subset: Columns to consider for identifying duplicates
        keep: Which duplicates to keep ('first', 'last', False)
    
    Returns:
        pd.DataFrame: DataFrame without duplicates
    """
    return df.drop_duplicates(subset=subset, keep=keep)


def normalize_column(
    df: pd.DataFrame,
    column: str,
    method: str = "minmax"
) -> pd.DataFrame:
    """
    Normalize a numerical column.
    
    Args:
        df: Input DataFrame
        column: Column to normalize
        method: Normalization method ('minmax' or 'zscore')
    
    Returns:
        pd.DataFrame: DataFrame with normalized column
    """
    df_copy = df.copy()
    
    if method == "minmax":
        min_val = df_copy[column].min()
        max_val = df_copy[column].max()
        df_copy[column] = (df_copy[column] - min_val) / (max_val - min_val)
    elif method == "zscore":
        mean_val = df_copy[column].mean()
        std_val = df_copy[column].std()
        df_copy[column] = (df_copy[column] - mean_val) / std_val
    else:
        raise ValueError(f"Unknown method: {method}")
    
    return df_copy


def encode_categorical(
    df: pd.DataFrame,
    columns: List[str],
    method: str = "onehot"
) -> pd.DataFrame:
    """
    Encode categorical variables.
    
    Args:
        df: Input DataFrame
        columns: Columns to encode
        method: Encoding method ('onehot' or 'label')
    
    Returns:
        pd.DataFrame: DataFrame with encoded columns
    """
    df_copy = df.copy()
    
    if method == "onehot":
        df_copy = pd.get_dummies(df_copy, columns=columns, prefix=columns)
    elif method == "label":
        from sklearn.preprocessing import LabelEncoder
        le = LabelEncoder()
        for col in columns:
            df_copy[col] = le.fit_transform(df_copy[col].astype(str))
    else:
        raise ValueError(f"Unknown method: {method}")
    
    return df_copy
