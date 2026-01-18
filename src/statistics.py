"""
Statistical analysis utilities for the WWM Data Analysis project.
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Tuple, Optional


def descriptive_statistics(df: pd.DataFrame, columns: Optional[list] = None) -> pd.DataFrame:
    """
    Get descriptive statistics for numerical columns.
    
    Args:
        df: Input DataFrame
        columns: Specific columns to analyze (all numeric if None)
    
    Returns:
        pd.DataFrame: Descriptive statistics
    """
    if columns:
        return df[columns].describe()
    return df.describe()


def test_normality(data: pd.Series, alpha: float = 0.05) -> Tuple[bool, float]:
    """
    Test if data follows normal distribution using Shapiro-Wilk test.
    
    Args:
        data: Data to test
        alpha: Significance level
    
    Returns:
        Tuple of (is_normal, p_value)
    """
    stat, p_value = stats.shapiro(data.dropna())
    is_normal = p_value > alpha
    return is_normal, p_value


def correlation_analysis(
    df: pd.DataFrame,
    column1: str,
    column2: str,
    method: str = "pearson"
) -> Tuple[float, float]:
    """
    Compute correlation between two columns.
    
    Args:
        df: Input DataFrame
        column1: First column
        column2: Second column
        method: Correlation method ('pearson', 'spearman', 'kendall')
    
    Returns:
        Tuple of (correlation_coefficient, p_value)
    """
    if method == "pearson":
        corr, p_value = stats.pearsonr(df[column1].dropna(), df[column2].dropna())
    elif method == "spearman":
        corr, p_value = stats.spearmanr(df[column1].dropna(), df[column2].dropna())
    elif method == "kendall":
        corr, p_value = stats.kendalltau(df[column1].dropna(), df[column2].dropna())
    else:
        raise ValueError(f"Unknown method: {method}")
    
    return corr, p_value


def t_test_independent(
    group1: pd.Series,
    group2: pd.Series,
    alpha: float = 0.05
) -> dict:
    """
    Perform independent samples t-test.
    
    Args:
        group1: First group data
        group2: Second group data
        alpha: Significance level
    
    Returns:
        dict: Test results including statistic, p-value, and conclusion
    """
    stat, p_value = stats.ttest_ind(group1.dropna(), group2.dropna())
    
    return {
        "statistic": stat,
        "p_value": p_value,
        "significant": p_value < alpha,
        "interpretation": f"Groups are {'significantly different' if p_value < alpha else 'not significantly different'} at α={alpha}"
    }


def anova_test(df: pd.DataFrame, value_column: str, group_column: str, alpha: float = 0.05) -> dict:
    """
    Perform one-way ANOVA test.
    
    Args:
        df: Input DataFrame
        value_column: Column containing values
        group_column: Column containing group labels
        alpha: Significance level
    
    Returns:
        dict: Test results
    """
    groups = [group[value_column].dropna() for name, group in df.groupby(group_column)]
    stat, p_value = stats.f_oneway(*groups)
    
    return {
        "statistic": stat,
        "p_value": p_value,
        "significant": p_value < alpha,
        "interpretation": f"Groups are {'significantly different' if p_value < alpha else 'not significantly different'} at α={alpha}"
    }


def chi_square_test(
    df: pd.DataFrame,
    column1: str,
    column2: str,
    alpha: float = 0.05
) -> dict:
    """
    Perform chi-square test of independence for categorical variables.
    
    Args:
        df: Input DataFrame
        column1: First categorical column
        column2: Second categorical column
        alpha: Significance level
    
    Returns:
        dict: Test results
    """
    contingency_table = pd.crosstab(df[column1], df[column2])
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
    
    return {
        "chi2_statistic": chi2,
        "p_value": p_value,
        "degrees_of_freedom": dof,
        "significant": p_value < alpha,
        "interpretation": f"Variables are {'significantly associated' if p_value < alpha else 'not significantly associated'} at α={alpha}"
    }
