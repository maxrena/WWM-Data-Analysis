"""
Visualization utilities for the WWM Data Analysis project.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List, Tuple


# Set default style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


def plot_distribution(
    df: pd.DataFrame,
    column: str,
    bins: int = 30,
    kde: bool = True,
    save_path: Optional[str] = None
) -> None:
    """
    Plot the distribution of a numerical column.
    
    Args:
        df: Input DataFrame
        column: Column to plot
        bins: Number of bins for histogram
        kde: Whether to overlay KDE plot
        save_path: Path to save the figure
    """
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x=column, bins=bins, kde=kde)
    plt.title(f'Distribution of {column}')
    plt.xlabel(column)
    plt.ylabel('Frequency')
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()


def plot_correlation_matrix(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    annot: bool = True,
    save_path: Optional[str] = None
) -> None:
    """
    Plot correlation matrix heatmap.
    
    Args:
        df: Input DataFrame
        columns: Columns to include (numeric columns if None)
        annot: Whether to annotate cells with values
        save_path: Path to save the figure
    """
    if columns:
        corr = df[columns].corr()
    else:
        corr = df.select_dtypes(include=[np.number]).corr()
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr, annot=annot, cmap='coolwarm', center=0, 
                square=True, linewidths=1, fmt='.2f')
    plt.title('Correlation Matrix')
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()


def plot_categorical_count(
    df: pd.DataFrame,
    column: str,
    top_n: Optional[int] = None,
    save_path: Optional[str] = None
) -> None:
    """
    Plot count of categorical variable.
    
    Args:
        df: Input DataFrame
        column: Categorical column to plot
        top_n: Show only top N categories
        save_path: Path to save the figure
    """
    if top_n:
        value_counts = df[column].value_counts().head(top_n)
    else:
        value_counts = df[column].value_counts()
    
    plt.figure(figsize=(12, 6))
    value_counts.plot(kind='bar')
    plt.title(f'Count of {column}')
    plt.xlabel(column)
    plt.ylabel('Count')
    plt.xticks(rotation=45, ha='right')
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()


def plot_time_series(
    df: pd.DataFrame,
    date_column: str,
    value_column: str,
    save_path: Optional[str] = None
) -> None:
    """
    Plot time series data.
    
    Args:
        df: Input DataFrame
        date_column: Column containing dates
        value_column: Column containing values to plot
        save_path: Path to save the figure
    """
    plt.figure(figsize=(14, 6))
    plt.plot(df[date_column], df[value_column], linewidth=2)
    plt.title(f'{value_column} Over Time')
    plt.xlabel(date_column)
    plt.ylabel(value_column)
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, alpha=0.3)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()


def plot_scatter(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    hue: Optional[str] = None,
    save_path: Optional[str] = None
) -> None:
    """
    Create scatter plot.
    
    Args:
        df: Input DataFrame
        x_column: Column for x-axis
        y_column: Column for y-axis
        hue: Column for color coding
        save_path: Path to save the figure
    """
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x=x_column, y=y_column, hue=hue, alpha=0.6)
    plt.title(f'{y_column} vs {x_column}')
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()
