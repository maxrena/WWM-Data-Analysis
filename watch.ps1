# Auto-reload Streamlit when files change
# Usage: .\watch.ps1

# Activate virtual environment
& "F:/Github/WWM Data Analysis/.venv/Scripts/Activate.ps1"

# Run Streamlit with auto-reload (built-in feature)
# Streamlit automatically watches for file changes and reloads
streamlit run app.py --server.runOnSave true
