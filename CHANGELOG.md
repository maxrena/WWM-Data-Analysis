# Changelog

All notable changes to WWM Data Analysis project will be documented in this file.

## [1.4.0] - 2026-01-27

### Added
- **🆕 Match Groups Feature**
  - Date-based indexing system for easy match lookup
  - New `match_groups` table with pre-calculated statistics
  - Methods: `create_match_groups_table()`, `update_match_groups()`, `get_match_by_date()`, `list_all_match_dates()`
  - Automatic indexing when adding new matches
  - Fast lookup by match date with indexed queries

- **New Scripts**
  - `scripts/manage_match_groups.py` - Initialize and manage match groups
  - `scripts/example_match_groups.py` - Comprehensive usage examples

- **Database Enhancements**
  - `match_groups` table stores metadata for each match date
  - Pre-calculated statistics: player counts, total defeats, average damage
  - Indexed by match_date for optimal performance
  - Auto-update integration in add_yb_match.py and add_enemy_match.py

- **Documentation**
  - `MATCH_GROUPS.md` - Quick reference guide
  - `IMPLEMENTATION_SUMMARY.md` - Complete implementation details
  - Updated `DATABASE.md` with match groups section
  - Updated `README.md` with v1.4 features

### Changed
- Enhanced `src/database.py` with match groups functionality
- Updated `scripts/add_yb_match.py` to auto-update match groups
- Updated `scripts/add_enemy_match.py` to auto-update match groups
- Fixed Unicode encoding issues for Windows compatibility (replaced ✓ with [OK])

### Benefits
- Fast date-based match lookup
- Easy comparison across matches
- Pre-calculated team statistics
- Automatic maintenance when adding matches

## [1.3.0] - 2026-01-22

### Fixed
- Replaced all deprecated `use_container_width=True` with `width='stretch'`
- Replaced all deprecated `use_container_width=False` with `width='content'`
- Updated all Streamlit components to use the new width parameter
- Eliminated deprecation warnings for Streamlit 1.53+

### Changed
- Updated 29 instances across app.py and extractor.py
- Improved compatibility with latest Streamlit version

## [1.2.0] - 2026-01-18

### Added
- **🆕 Data Extractor UI** (`extractor.py`)
  - Drag-and-drop interface for uploading match screenshots
  - Two-panel layout for YB Team and Enemy Team
  - Image preview functionality
  - Manual data entry option (OCR planned for future release)
  - CSV upload alternative
  - Interactive data editor for review and correction
  - Match ID system: `YYYYMMDD_HHMMSS` format
  - Support for multiple matches per day

- **Database Enhancements**
  - Added `match_id` column to `youngbuffalo_stats` table
  - Added `match_id` column to `enemy_all_stats` table
  - Indexes on `match_id` for improved query performance
  - Database version tracking table
  - Upgrade script: `scripts/upgrade_to_v12.py`

- **New Scripts**
  - `launch.ps1` - Interactive application launcher
  - `scripts/upgrade_to_v12.py` - Database upgrade script

- **Documentation**
  - Updated README.md with v1.2 features
  - Added detailed usage workflow for Data Extractor
  - Added version 1.2 feature documentation

### Changed
- Database schema now supports multiple matches per day via `match_id`
- Existing match data migrated to include default `match_id` (date + `_000000`)
- Updated README to reflect version 1.2 capabilities

### Technical Details
- Match ID format: `YYYYMMDD_HHMMSS`
- Example: `20260118_143530` represents January 18, 2026 at 2:35:30 PM
- Backward compatible with existing data (default time: `000000`)
- VIEWs (`yb_stats`, `enemy_stats`) still show latest match by date

### Future Plans
- OCR implementation for automatic data extraction from screenshots
- Image preprocessing for better OCR accuracy
- Batch upload support
- Match history comparison UI
- Player performance trends over time

---

## [1.1.0] - 2026-01-18

### Added
- Master table architecture for match history tracking
- `youngbuffalo_stats` master table with `match_date` column
- `enemy_all_stats` master table with `match_date` column
- Dated snapshot tables (e.g., `yb_stats_20260118`)
- VIEWs for backward compatibility
- Match data addition scripts:
  - `scripts/add_yb_match.py`
  - `scripts/add_enemy_match.py`
  - `scripts/add_match.py`
- `scripts/migrate_enemy_stats.py` for data migration
- DATABASE.md documentation
- Utility scripts for database inspection

### Removed
- Player Rankings page (due to styling issues)

---

## [1.0.0] - 2026-01-18

### Added
- Initial release
- Streamlit dashboard with 5 pages:
  - Overview
  - YB Team Stats
  - Enemy Team Stats
  - Head-to-Head Comparison
  - Player Rankings
- PDF export with Unicode support (DejaVu fonts)
- SQLite database with indexed tables
- Data visualization with Plotly
- Deployment configuration for Render.com
- Auto-reload watch script (`watch.ps1`)
- Font download script for Unicode support

### Features
- Interactive web dashboard
- Team comparison analytics
- Player statistics analysis
- PDF report generation
- Chinese character support in PDFs

### Database
- `yb_stats` table (30 players)
- `enemy_stats` table (31 players)
- Indexed columns for performance

---

## Version Numbering

- Major version (X.0.0): Significant changes, potential breaking changes
- Minor version (1.X.0): New features, backward compatible
- Patch version (1.0.X): Bug fixes, minor improvements
