"""
WWM Data Analysis Project
A comprehensive toolkit for data analysis workflows.
"""

__version__ = "0.1.0"

from .data_loader import load_csv, load_excel, save_processed_data
from .preprocessing import (
    handle_missing_values,
    remove_duplicates,
    normalize_column,
    encode_categorical
)
from .visualization import (
    plot_distribution,
    plot_correlation_matrix,
    plot_categorical_count,
    plot_time_series,
    plot_scatter
)
from .statistics import (
    descriptive_statistics,
    test_normality,
    correlation_analysis,
    t_test_independent,
    anova_test,
    chi_square_test
)
from .database import DataAnalysisDB

__all__ = [
    # Data loading
    'load_csv',
    'load_excel',
    'save_processed_data',
    
    # Preprocessing
    'handle_missing_values',
    'remove_duplicates',
    'normalize_column',
    'encode_categorical',
    
    # Visualization
    'plot_distribution',
    'plot_correlation_matrix',
    'plot_categorical_count',
    'plot_time_series',
    'plot_scatter',
    
    # Statistics
    'descriptive_statistics',
    'test_normality',
    'correlation_analysis',
    't_test_independent',
    'anova_test',
    'chi_square_test',
    
    # Database
    'DataAnalysisDB',
]
