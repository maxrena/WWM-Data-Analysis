# WWM Data Analysis Project

**Version 1.6** - Multiple Match Support & Database Optimization

A comprehensive match analysis dashboard for WWM game statistics with interactive visualizations, PDF reporting, and OCR-based data extraction capabilities.

## Project Structure

```
WWM Data Analysis/
│
├── data/
│   ├── raw/                    # Raw CSV data files (player stats)
│   └── analysis.db             # SQLite database
│
├── notebooks/                  # Jupyter notebooks for analysis
│   ├── 01_exploratory_data_analysis.ipynb
│   ├── player_stats_analysis.ipynb
│   └── database_analysis.ipynb
│
├── src/                        # Source code modules
│   ├── __init__.py
│   ├── data_loader.py         # Data loading utilities
│   ├── preprocessing.py       # Data preprocessing functions
│   ├── visualization.py       # Visualization functions
│   ├── statistics.py          # Statistical analysis tools
│   ├── database.py            # Database management
│   └── config.py              # Configuration settings
│
├── scripts/                    # Utility scripts
│   ├── load_to_database.py    # Load CSV to database
│   ├── download_fonts.py      # Download Unicode fonts
│   ├── add_yb_match.py        # Add new YB team match data
│   ├── add_enemy_match.py     # Add new enemy team match data
│   ├── add_match.py           # Add both teams' match data
│   └── migrate_enemy_stats.py # Migrate enemy_stats to master table
│
├── fonts/                      # DejaVu Unicode fonts for PDF
│
├── outputs/                    # Output files
│   ├── figures/               # Saved visualizations
│   └── reports/               # Generated reports
│
├── app.py                     # Streamlit dashboard application
├── extractor.py               # v1.2 Data extraction UI (drag & drop)
├── watch.ps1                  # Auto-reload development script
├── requirements.txt           # Python dependencies
├── .gitignore                # Git ignore rules
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## Features

- **🆕 Drag & Drop Data Extraction**: Upload game screenshots and extract player statistics (v1.2)
- **🆕 Multiple Matches Per Day**: Track multiple matches with unique match IDs (v1.2)
- **🆕 Match Groups**: Date-based indexing for easy match lookup and comparison (v1.4)
- **Interactive Web Dashboard**: Streamlit-based UI with 4 different analysis views
- **SQLite Database**: Efficient data storage with indexed queries and match history tracking
- **Match History**: Track multiple matches over time with dated snapshots
- **Unicode Support**: Full support for Chinese and international characters
- **PDF Export**: Generate comprehensive match reports with all statistics
- **Data Visualization**: Interactive charts using Plotly
- **Team Comparison**: Head-to-head analysis between YB Team and Enemy Team
- **Auto-Reload**: Development watch script for automatic dashboard refresh

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/maxrena/WWM-Data-Analysis.git
   cd WWM-Data-Analysis
   ```

2. Create a virtual environment (recommended):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install required packages:
   ```powershell
   pip install -r requirements.txt
   ```

4. Download Unicode fonts for PDF support:
   ```powershell
   python scripts/download_fonts.py
   ```

### Running the Applications

**Option 1: Data Extractor (NEW in v1.2)**
```powershell
streamlit run extractor.py --server.port=8502
```
- Drag and drop game screenshots
- Extract player statistics (manual entry for now, OCR coming soon)
- Upload CSV files directly
- Save matches with unique IDs (supports multiple matches per day)
- Access at `http://localhost:8502`

**Option 2: Main Dashboard**
```powershell
streamlit run app.py
```

Or use the auto-reload watch script:
```powershell
.\watch.ps1
```

- Access at `http://localhost:8501`
- View comprehensive match statistics and visualizations
- Export PDF reports
- Navigate through 4 analysis pages:
   - **Overview**: Team statistics summary
   - **YB Team Stats**: Detailed YB team analysis
   - **Enemy Team Stats**: Detailed enemy team analysis
   - **Head-to-Head Comparison**: Direct team comparisons

## Version 1.2 Features

### 🆕 Data Extraction UI

The new `extractor.py` provides a user-friendly interface for adding match data:

1. **Drag & Drop Interface**
   - Upload screenshots for both teams simultaneously
   - Preview uploaded images
   - Support for multiple images per team

2. **Multiple Matches Per Day**
   - Each match gets a unique ID: `YYYYMMDD_HHMMSS`
   - Example: `20260118_143530` (Jan 18, 2026 at 2:35:30 PM)
   - Track unlimited matches on the same day

3. **Flexible Data Entry**
   - Upload screenshots (manual entry for now)
   - Upload CSV files directly
   - Edit data in interactive tables
   - Add/remove rows dynamically

4. **Match Management**
   - Set match date and time
   - Review data before saving
   - Download as CSV
   - Save directly to database
   - Automatic VIEW updates

### Usage Workflow

1. **Start the Data Extractor**:
   ```powershell
   streamlit run extractor.py --server.port=8502
   ```

2. **Upload Match Data**:
   - Select match date and time
   - Upload screenshots or CSV for YB team
   - Upload screenshots or CSV for enemy team
   - Enter player statistics manually (or wait for OCR feature)

3. **Review & Edit**:
   - Navigate to "Review & Save" page
   - Edit data in interactive tables
   - Add or remove players as needed

4. **Save to Database**:
   - Click "Save to Database" button
   - Data automatically saved with unique match ID
   - VIEWs updated to show latest match
   - Dated snapshot tables created

5. **View in Dashboard**:
   - Open main dashboard at `http://localhost:8501`
   - See your newly added match data immediately

4. Export PDF reports using the sidebar button

## Database Structure

The project uses a **master table + dated snapshots** architecture:

- **Master Tables**: `youngbuffalo_stats`, `enemy_all_stats` - contain all historical match data
- **Dated Tables**: `yb_stats_YYYYMMDD`, `enemy_stats_YYYYMMDD` - individual match snapshots
- **VIEWs**: `yb_stats`, `enemy_stats` - always show the latest match data

See [DATABASE.md](DATABASE.md) for complete documentation.

### Match Groups (NEW in v1.4)

Match groups provide date-based indexing for easy match lookup and comparison:

**Initialize match groups:**
```powershell
python scripts/manage_match_groups.py
```

**Use in Python:**
```python
from src.database import DataAnalysisDB

db = DataAnalysisDB()
db.connect()

# List all match dates
matches = db.list_all_match_dates(order='DESC')

# Get specific match by date
match_data = db.get_match_by_date('20260118', team='both')

# Update after adding new matches
db.update_match_groups()

db.close()
```

**Benefits:**
- Fast lookup of matches by date
- Pre-calculated statistics (averages, totals)
- Easy comparison across matches
- Automatic indexing

See [DATABASE.md](DATABASE.md) for more examples and SQL queries.

### Adding New Match Data

**Add both teams at once:**
```powershell
python scripts/add_match.py data/yb_20260119.csv data/enemy_20260119.csv 20260119
```

**Add YB team only:**
```powershell
python scripts/add_yb_match.py data/yb_20260119.csv 20260119
```

**Add enemy team only:**
```powershell
python scripts/add_enemy_match.py data/enemy_20260119.csv 20260119
```

The scripts will:
1. Create dated snapshot tables
2. Add data to master tables with match_date
3. Update VIEWs to show the latest match
4. Dashboard automatically displays the new data!

### Quick Start

### Quick Start

1. Explore the data in Jupyter notebooks:
   ```powershell
   jupyter notebook
   ```

2. Load data into database:
   ```powershell
   python scripts/load_to_database.py
   ```

3. Or use the modules in your own scripts:
   ```python
   from src.database import DataAnalysisDB
   from src.visualization import plot_distribution
   
   db = DataAnalysisDB()
   df = db.query("SELECT * FROM yb_stats")
   plot_distribution(df, 'defeated')
   ```

## Deployment

### Deploy to Render.com

1. Fork or push this repository to GitHub

2. Create a new Web Service on [Render.com](https://render.com)

3. Connect your GitHub repository

4. Use these settings:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt && python scripts/download_fonts.py`
   - **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`

5. Deploy! Your app will be live at `https://your-app.onrender.com`

**Note**: The `render.yaml` file is included for automatic configuration.

## Dashboard Pages

### 1. Overview
- Team size comparison
- Total statistics (Defeated, Damage, Assists, Tank, Heal, Siege Damage)
- Top performers from each team
- Visual comparisons

### 2. YB Team Stats
- Top 10 players by Defeated and Damage
- Team averages across all metrics
- Distribution visualizations
- Performance breakdowns

### 3. Enemy Team Stats
- Top 10 players by Defeated and Damage
- Team averages across all metrics
- Distribution visualizations
- Performance breakdowns

### 4. Head-to-Head Comparison
- Direct metric comparisons
- Combined top 10 players
- Statistical analysis
- Difference calculations

### 5. Player Rankings
- Top 20 overall players (combined teams)
- Rank by any metric (Defeated, Damage, Assist, Tank, Heal, Siege Damage)
- Team distribution in top rankings
- Color-coded team identification

## PDF Reports

The PDF export feature generates comprehensive reports including:
- Team overview with all metrics
- Top 10 players from both teams
- Average statistics comparison
- Head-to-head total and average comparisons
- Overall player rankings (Top 20 by Defeated, Top 10 by Damage)
- Full Unicode support for international player names

## Database Schema

### Match History Tables

**youngbuffalo_stats** (Master table with all match history)
- id (INTEGER, PRIMARY KEY)
- match_date (TEXT) - Format: YYYYMMDD
- player_name (TEXT)
- defeated (INTEGER)
- assist (INTEGER)
- defeated_2 (INTEGER)
- fun_coin (INTEGER)
- damage (INTEGER)
- tank (INTEGER)
- heal (INTEGER)
- siege_damage (INTEGER)

**yb_stats** (View showing latest match)
- Automatically shows data from the most recent match date
- Maintains backward compatibility with existing code

**yb_stats_YYYYMMDD** (Individual match tables)
- One table per match date (e.g., yb_stats_20260118)
- Contains the same columns as the view
- Preserved for historical reference

**enemy_stats** (Opponent team data)
- player_name (TEXT)
- defeated (INTEGER)
- assist (INTEGER)
- defeated_2 (INTEGER)
- fun_coin (INTEGER)
- damage (INTEGER)
- tank (INTEGER)
- heal (INTEGER)
- siege_damage (INTEGER)

**enemy_stats** (Opponent team data)
- player_name (TEXT)
- defeated (INTEGER)
- assist (INTEGER)
- defeated_2 (INTEGER)
- fun_coin (INTEGER)
- damage (INTEGER)
- tank (INTEGER)
- heal (INTEGER)
- siege_damage (INTEGER)

### Adding New Match Data

To add a new match to the history:

```powershell
python scripts/add_match_data.py data/raw/new_match.csv 20260125
```

This will:
- Add data to the master `youngbuffalo_stats` table
- Create a date-specific table (e.g., `yb_stats_20260125`)
- Update the `yb_stats` view to show the latest match

**yb_stats_YYYYMMDD** (Individual match tables)
- Same schema as yb_stats
- One table per match date
- Preserved for historical reference

## Available Modules

### database.py
- `DataAnalysisDB` - SQLite database management class
- `query()` - Execute SELECT queries
- `execute()` - Execute other SQL commands
- `load_csv_to_table()` - Import CSV to database

### data_loader.py
- `load_csv()` - Load CSV files
- `load_excel()` - Load Excel files
- `save_processed_data()` - Save processed data

### preprocessing.py
- `handle_missing_values()` - Handle missing data
- `remove_duplicates()` - Remove duplicate rows
- `normalize_column()` - Normalize numerical columns
- `encode_categorical()` - Encode categorical variables

### visualization.py
- `plot_distribution()` - Plot data distributions
- `plot_correlation_matrix()` - Create correlation heatmaps
- `plot_categorical_count()` - Count plots for categories
- `plot_time_series()` - Time series visualizations
- `plot_scatter()` - Scatter plots

### statistics.py
- `descriptive_statistics()` - Summary statistics
- `test_normality()` - Test for normal distribution
- `correlation_analysis()` - Correlation testing
- `t_test_independent()` - Independent t-test
- `anova_test()` - One-way ANOVA
- `chi_square_test()` - Chi-square test

### config.py
- Database configuration
- Application settings

## Technology Stack

- **Python 3.12**: Core programming language
- **Streamlit 1.28+**: Web dashboard framework
- **SQLite**: Lightweight database
- **Pandas**: Data manipulation
- **Plotly**: Interactive visualizations
- **FPDF2**: PDF generation with Unicode support
- **NumPy**: Numerical computing
- **Matplotlib & Seaborn**: Statistical visualizations

## Data Structure

Player statistics include:
- **Defeated**: Number of enemies defeated
- **Damage**: Total damage dealt
- **Assist**: Number of assists
- **Tank**: Damage absorbed/tanked
- **Heal**: Total healing done
- **Siege Damage**: Damage to objectives
- **Fun Coin**: In-game currency earned

## Contributing

Contributions are welcome! Please feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## Version History

### Version 1.0 (January 2026)
- Initial release
- Interactive Streamlit dashboard with 5 pages
- SQLite database integration
- PDF export with full Unicode support
- Player rankings and team comparisons
- 61 total players analyzed (30 YB, 31 Enemy)

## License

This project is provided as-is for educational and analytical purposes.

## Author

maxrena

## Repository

https://github.com/maxrena/WWM-Data-Analysis

For questions or issues, please refer to the inline documentation in each module or the example notebook.
