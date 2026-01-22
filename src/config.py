# Configuration file for data analysis project

# Project Information
PROJECT_NAME = "WWM Data Analysis"
VERSION = "1.3.0"

# Directory paths
DATA_DIR = "data"
RAW_DATA_DIR = "data/raw"
PROCESSED_DATA_DIR = "data/processed"
OUTPUT_DIR = "outputs"
FIGURES_DIR = "outputs/figures"
REPORTS_DIR = "outputs/reports"

# Visualization settings
PLOT_STYLE = "whitegrid"
FIGURE_SIZE = (12, 6)
DPI = 300
COLOR_PALETTE = "Set2"

# Data processing settings
MISSING_VALUE_THRESHOLD = 0.5  # Drop columns with >50% missing values
RANDOM_STATE = 42

# Statistical significance level
ALPHA = 0.05
