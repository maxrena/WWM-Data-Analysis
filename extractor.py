"""
WWM Match Data Extractor - Version 1.3
Drag-and-drop interface for extracting player statistics from game screenshots
"""

import streamlit as st
import pandas as pd
from PIL import Image
import io
import re
from datetime import datetime
import sqlite3
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))
from database import DataAnalysisDB

# Page configuration
st.set_page_config(
    page_title="WWM Data Extractor v1.2",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .upload-box {
        border: 2px dashed #1f77b4;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background-color: #f0f2f6;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'yb_data' not in st.session_state:
    st.session_state.yb_data = None
if 'enemy_data' not in st.session_state:
    st.session_state.enemy_data = None
if 'match_id' not in st.session_state:
    st.session_state.match_id = None
if 'extraction_method' not in st.session_state:
    st.session_state.extraction_method = 'manual'

# Header
st.markdown('<p class="main-header">📸 WWM Match Data Extractor v1.2</p>', unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("🎮 Navigation")
page = st.sidebar.radio(
    "Select Mode",
    ["Upload & Extract", "Review & Save", "View Dashboard"]
)

if page == "View Dashboard":
    st.info("Opening main dashboard...")
    st.markdown("[🔗 Go to Main Dashboard](http://localhost:8501)", unsafe_allow_html=True)
    st.markdown("---")
    st.write("To return to data extraction, select 'Upload & Extract' from the sidebar.")

elif page == "Upload & Extract":
    st.header("📤 Upload Match Screenshots")
    
    # Match metadata
    col1, col2 = st.columns(2)
    with col1:
        match_date = st.date_input(
            "Match Date",
            value=datetime.now(),
            help="Select the date when this match was played"
        )
        match_date_str = match_date.strftime('%Y%m%d')
    
    with col2:
        match_time = st.time_input(
            "Match Time (optional)",
            value=datetime.now().time(),
            help="Time of the match for unique identification"
        )
        match_time_str = match_time.strftime('%H%M%S')
    
    # Generate match ID
    match_id = f"{match_date_str}_{match_time_str}"
    st.session_state.match_id = match_id
    st.info(f"📋 Match ID: `{match_id}`")
    
    st.markdown("---")
    
    # Two-column layout for team uploads
    col_yb, col_enemy = st.columns(2)
    
    # YB Team Upload
    with col_yb:
        st.subheader("🟢 My Team (YoungBuffalo)")
        
        yb_files = st.file_uploader(
            "Upload YB Team Screenshots",
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            key="yb_upload",
            help="Upload one or more screenshots of your team's statistics"
        )
        
        if yb_files:
            st.success(f"✅ {len(yb_files)} image(s) uploaded")
            
            # Show thumbnails
            with st.expander("Preview Images"):
                for i, file in enumerate(yb_files):
                    img = Image.open(file)
                    st.image(img, caption=f"Image {i+1}", width='stretch')
            
            # Manual data entry option
            st.markdown("### Enter Data Manually")
            st.write("Since OCR is not yet implemented, please enter the data manually:")
            
            num_players = st.number_input("Number of players", min_value=1, max_value=50, value=5, key="yb_num")
            
            if st.button("📝 Enter YB Team Data", key="yb_manual"):
                st.session_state.yb_data = pd.DataFrame({
                    'player_name': [''] * num_players,
                    'defeated': [0] * num_players,
                    'assist': [0] * num_players,
                    'defeated_2': [0] * num_players,
                    'fun_coin': [0] * num_players,
                    'damage': [0] * num_players,
                    'tank': [0] * num_players,
                    'heal': [0] * num_players,
                    'siege_damage': [0] * num_players
                })
    
    # Enemy Team Upload
    with col_enemy:
        st.subheader("🔴 Enemy Team")
        
        enemy_files = st.file_uploader(
            "Upload Enemy Team Screenshots",
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            key="enemy_upload",
            help="Upload one or more screenshots of enemy team's statistics"
        )
        
        if enemy_files:
            st.success(f"✅ {len(enemy_files)} image(s) uploaded")
            
            # Show thumbnails
            with st.expander("Preview Images"):
                for i, file in enumerate(enemy_files):
                    img = Image.open(file)
                    st.image(img, caption=f"Image {i+1}", width='stretch')
            
            # Manual data entry option
            st.markdown("### Enter Data Manually")
            st.write("Since OCR is not yet implemented, please enter the data manually:")
            
            num_players = st.number_input("Number of players", min_value=1, max_value=50, value=5, key="enemy_num")
            
            if st.button("📝 Enter Enemy Team Data", key="enemy_manual"):
                st.session_state.enemy_data = pd.DataFrame({
                    'player_name': [''] * num_players,
                    'defeated': [0] * num_players,
                    'assist': [0] * num_players,
                    'defeated_2': [0] * num_players,
                    'fun_coin': [0] * num_players,
                    'damage': [0] * num_players,
                    'tank': [0] * num_players,
                    'heal': [0] * num_players,
                    'siege_damage': [0] * num_players
                })
    
    st.markdown("---")
    
    # CSV Upload as alternative
    st.subheader("📁 Or Upload CSV Files Directly")
    col1, col2 = st.columns(2)
    
    with col1:
        yb_csv = st.file_uploader("YB Team CSV", type=['csv'], key="yb_csv")
        if yb_csv:
            st.session_state.yb_data = pd.read_csv(yb_csv)
            st.success("✅ YB Team data loaded from CSV")
    
    with col2:
        enemy_csv = st.file_uploader("Enemy Team CSV", type=['csv'], key="enemy_csv")
        if enemy_csv:
            st.session_state.enemy_data = pd.read_csv(enemy_csv)
            st.success("✅ Enemy Team data loaded from CSV")

elif page == "Review & Save":
    st.header("📊 Review & Save Match Data")
    
    if st.session_state.match_id:
        st.info(f"📋 Match ID: `{st.session_state.match_id}`")
    
    # Check if we have data
    has_yb = st.session_state.yb_data is not None
    has_enemy = st.session_state.enemy_data is not None
    
    if not has_yb and not has_enemy:
        st.warning("⚠️ No data to review. Please upload and extract data first.")
        if st.button("← Go to Upload & Extract"):
            st.session_state.page = "Upload & Extract"
            st.rerun()
    else:
        col1, col2 = st.columns(2)
        
        # YB Team Review
        with col1:
            st.subheader("🟢 YB Team Data")
            if has_yb:
                # Editable dataframe
                edited_yb = st.data_editor(
                    st.session_state.yb_data,
                    num_rows="dynamic",
                    width='stretch',
                    key="yb_editor"
                )
                st.session_state.yb_data = edited_yb
                
                st.success(f"✅ {len(edited_yb)} players")
            else:
                st.info("No YB team data available")
        
        # Enemy Team Review
        with col2:
            st.subheader("🔴 Enemy Team Data")
            if has_enemy:
                # Editable dataframe
                edited_enemy = st.data_editor(
                    st.session_state.enemy_data,
                    num_rows="dynamic",
                    width='stretch',
                    key="enemy_editor"
                )
                st.session_state.enemy_data = edited_enemy
                
                st.success(f"✅ {len(edited_enemy)} players")
            else:
                st.info("No enemy team data available")
        
        st.markdown("---")
        
        # Save options
        st.subheader("💾 Save Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Download as CSV", width='stretch'):
                if has_yb:
                    csv_yb = st.session_state.yb_data.to_csv(index=False)
                    st.download_button(
                        "⬇️ Download YB Team CSV",
                        csv_yb,
                        f"yb_team_{st.session_state.match_id}.csv",
                        "text/csv",
                        width='stretch'
                    )
                if has_enemy:
                    csv_enemy = st.session_state.enemy_data.to_csv(index=False)
                    st.download_button(
                        "⬇️ Download Enemy Team CSV",
                        csv_enemy,
                        f"enemy_team_{st.session_state.match_id}.csv",
                        "text/csv",
                        width='stretch'
                    )
        
        with col2:
            if st.button("💾 Save to Database", type="primary", width='stretch'):
                try:
                    db_path = Path('data/analysis.db')
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    match_date = st.session_state.match_id.split('_')[0]
                    
                    # Save YB team
                    if has_yb:
                        # Add to master table
                        df_yb = st.session_state.yb_data.copy()
                        df_yb['match_date'] = match_date
                        df_yb['match_id'] = st.session_state.match_id
                        
                        # Check if match_id column exists
                        cursor.execute("PRAGMA table_info(youngbuffalo_stats)")
                        columns = [col[1] for col in cursor.fetchall()]
                        if 'match_id' not in columns:
                            cursor.execute("ALTER TABLE youngbuffalo_stats ADD COLUMN match_id TEXT")
                        
                        df_yb.to_sql('youngbuffalo_stats', conn, if_exists='append', index=False)
                        
                        # Create dated table
                        dated_table = f"yb_stats_{st.session_state.match_id}"
                        st.session_state.yb_data.to_sql(dated_table, conn, if_exists='replace', index=False)
                        
                        st.success(f"✅ YB team data saved to database")
                    
                    # Save Enemy team
                    if has_enemy:
                        # Add to master table
                        df_enemy = st.session_state.enemy_data.copy()
                        df_enemy['match_date'] = match_date
                        df_enemy['match_id'] = st.session_state.match_id
                        
                        # Check if match_id column exists
                        cursor.execute("PRAGMA table_info(enemy_all_stats)")
                        columns = [col[1] for col in cursor.fetchall()]
                        if 'match_id' not in columns:
                            cursor.execute("ALTER TABLE enemy_all_stats ADD COLUMN match_id TEXT")
                        
                        df_enemy.to_sql('enemy_all_stats', conn, if_exists='append', index=False)
                        
                        # Create dated table
                        dated_table = f"enemy_stats_{st.session_state.match_id}"
                        st.session_state.enemy_data.to_sql(dated_table, conn, if_exists='replace', index=False)
                        
                        st.success(f"✅ Enemy team data saved to database")
                    
                    # Update VIEWs
                    if has_yb:
                        cursor.execute("DROP VIEW IF EXISTS yb_stats")
                        cursor.execute("SELECT MAX(match_date) FROM youngbuffalo_stats")
                        latest_date = cursor.fetchone()[0]
                        view_sql = f"""
                        CREATE VIEW yb_stats AS
                        SELECT 
                            player_name, defeated, assist, defeated_2, fun_coin,
                            damage, tank, heal, siege_damage
                        FROM youngbuffalo_stats
                        WHERE match_date = '{latest_date}'
                        """
                        cursor.execute(view_sql)
                    
                    if has_enemy:
                        cursor.execute("DROP VIEW IF EXISTS enemy_stats")
                        cursor.execute("SELECT MAX(match_date) FROM enemy_all_stats")
                        latest_date = cursor.fetchone()[0]
                        view_sql = f"""
                        CREATE VIEW enemy_stats AS
                        SELECT 
                            player_name, defeated, assist, defeated_2, fun_coin,
                            damage, tank, heal, siege_damage
                        FROM enemy_all_stats
                        WHERE match_date = '{latest_date}'
                        """
                        cursor.execute(view_sql)
                    
                    conn.commit()
                    conn.close()
                    
                    st.success("🎉 Match data saved successfully!")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"❌ Error saving to database: {e}")
        
        with col3:
            if st.button("🗑️ Clear Data", width='stretch'):
                st.session_state.yb_data = None
                st.session_state.enemy_data = None
                st.session_state.match_id = None
                st.rerun()

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: gray; padding: 1rem;'>
        WWM Data Extractor v1.2 | Build comprehensive match database with ease
    </div>
""", unsafe_allow_html=True)

