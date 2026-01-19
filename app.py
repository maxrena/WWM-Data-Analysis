"""
WWM Data Analysis Dashboard
Interactive web application for analyzing player statistics
Version 2.0 - Added OCR extraction, clipboard paste, and match filtering
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path
from datetime import datetime
import io
from PIL import Image
import sqlite3
import hashlib
import re
import numpy as np
try:
    import easyocr
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
from streamlit_paste_button import paste_image_button as pbutton

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))
from database import DataAnalysisDB

# Initialize EasyOCR reader (cached to avoid reloading)
@st.cache_resource
def get_ocr_reader():
    """Initialize and cache EasyOCR reader"""
    if OCR_AVAILABLE:
        try:
            # Initialize with English and Chinese support
            reader = easyocr.Reader(['en', 'ch_sim'], gpu=False)
            return reader
        except Exception as e:
            st.error(f"Error initializing OCR: {e}")
            return None
    return None

# OCR Helper Function
def extract_data_from_image(image):
    """Extract player statistics from game screenshot using EasyOCR with spatial sorting"""
    if not OCR_AVAILABLE:
        return None, "EasyOCR is not installed. Please install with: pip install easyocr"
    
    reader = get_ocr_reader()
    if reader is None:
        return None, "Failed to initialize OCR reader"
    
    try:
        # Convert PIL Image to numpy array for EasyOCR
        img_array = np.array(image)
        
        # Image preprocessing for better OCR accuracy
        # Convert to grayscale
        from PIL import ImageEnhance
        
        # Enhance contrast to make numbers more visible
        enhancer = ImageEnhance.Contrast(image)
        enhanced_image = enhancer.enhance(2.0)
        
        # Enhance brightness
        brightness_enhancer = ImageEnhance.Brightness(enhanced_image)
        enhanced_image = brightness_enhancer.enhance(1.2)
        
        # Convert enhanced image to array
        img_array = np.array(enhanced_image)
        
        # Perform OCR on the image with lower threshold
        results = reader.readtext(img_array, paragraph=False, min_size=5)
        
        if not results:
            return None, "No text detected in image. Please check image quality."
        
        # Extract detections with spatial coordinates
        detections = []
        for detection in results:
            bbox, text, confidence = detection
            if confidence > 0.1:  # Very low threshold to catch all numbers
                # Calculate center Y and left X for sorting
                y_coords = [point[1] for point in bbox]
                x_coords = [point[0] for point in bbox]
                center_y = sum(y_coords) / len(y_coords)
                left_x = min(x_coords)
                
                detections.append({
                    'text': text.strip(),
                    'x': left_x,
                    'y': center_y,
                    'confidence': confidence
                })
        
        # Sort detections by Y (top to bottom), then by X (left to right)
        detections.sort(key=lambda d: (d['y'], d['x']))
        
        # Group detections into rows based on Y-coordinate proximity
        rows = []
        current_row = []
        row_y_threshold = 30  # Increased tolerance for row grouping
        
        for det in detections:
            if not current_row:
                current_row.append(det)
            else:
                # Check if this detection is on the same row
                avg_y = sum(d['y'] for d in current_row) / len(current_row)
                if abs(det['y'] - avg_y) <= row_y_threshold:
                    current_row.append(det)
                else:
                    # Start new row
                    if current_row:
                        # Sort current row by X coordinate (left to right)
                        current_row.sort(key=lambda d: d['x'])
                        rows.append(current_row)
                    current_row = [det]
        
        # Add last row
        if current_row:
            current_row.sort(key=lambda d: d['x'])
            rows.append(current_row)
        
        # Extract player data from rows
        players_data = []
        debug_info = []  # For debugging
        
        for i, row in enumerate(rows):
            # Combine all text in the row
            row_texts = [d['text'] for d in row]
            row_combined = ' '.join(row_texts)
            
            # Extract all numbers from the row - be more aggressive
            all_numbers = []
            player_name_parts = []
            
            for text in row_texts:
                # Clean text - remove spaces and special chars from numbers
                cleaned = text.strip()
                
                # Try to extract as a whole number first
                if cleaned.replace(',', '').replace('.', '').isdigit():
                    # It's a pure number
                    num = cleaned.replace(',', '').replace('.', '')
                    all_numbers.append(num)
                else:
                    # Extract individual numbers from mixed text
                    nums = re.findall(r'\d+', cleaned)
                    if nums:
                        all_numbers.extend(nums)
                    
                    # Extract non-numeric parts for player name
                    non_numeric = re.sub(r'\d+', '', cleaned).strip()
                    if non_numeric and len(non_numeric) > 1:
                        player_name_parts.append(non_numeric)
            
            # Debug: collect row info
            debug_info.append(f"Row {i+1}: {row_combined} | Numbers: {all_numbers} ({len(all_numbers)} found)")
            
            # More lenient: accept rows with at least 4 numbers (can pad the rest)
            if len(all_numbers) >= 4:
                player_name = ' '.join(player_name_parts).strip() if player_name_parts else f"Player_{len(players_data)+1}"
                
                # Ensure we have exactly 8 stat fields
                while len(all_numbers) < 8:
                    all_numbers.append('0')
                
                # Take first 8 numbers as stats
                stats = all_numbers[:8]
                
                try:
                    players_data.append({
                        'player_name': player_name,
                        'defeated': int(stats[0]),
                        'assist': int(stats[1]),
                        'defeated_2': int(stats[2]),
                        'fun_coin': int(stats[3]),
                        'damage': int(stats[4]),
                        'tank': int(stats[5]),
                        'heal': int(stats[6]),
                        'siege_damage': int(stats[7])
                    })
                except (ValueError, IndexError) as e:
                    debug_info.append(f"  ⚠️ Row {i+1} parsing error: {e}")
                    continue
        
        if players_data:
            return pd.DataFrame(players_data), None
        else:
            # Return debug info to help diagnose the issue
            debug_msg = f"No valid player rows detected. Found {len(rows)} rows but none had enough stats (need 4+ numbers).\n\nDetected rows:\n" + "\n".join(debug_info)
            return None, debug_msg
    
    except Exception as e:
        return None, f"OCR Error: {str(e)}"

# Page configuration
st.set_page_config(
    page_title="WWM Data Analysis Dashboard v1.2",
    page_icon="⚔️",
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
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
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
    </style>
""", unsafe_allow_html=True)

# Initialize session state for data extractor
if 'yb_data' not in st.session_state:
    st.session_state.yb_data = None
if 'enemy_data' not in st.session_state:
    st.session_state.enemy_data = None
if 'match_id' not in st.session_state:
    st.session_state.match_id = None
if 'selected_match_id' not in st.session_state:
    st.session_state.selected_match_id = None
if 'yb_pasted_images' not in st.session_state:
    st.session_state.yb_pasted_images = []
if 'enemy_pasted_images' not in st.session_state:
    st.session_state.enemy_pasted_images = []
if 'last_yb_paste_id' not in st.session_state:
    st.session_state.last_yb_paste_id = None
if 'last_enemy_paste_id' not in st.session_state:
    st.session_state.last_enemy_paste_id = None

# Initialize database connection
@st.cache_resource
def get_database():
    """Get thread-safe database connection."""
    db = DataAnalysisDB('data/analysis.db')
    db.connect()
    return db

# Get database instance
db = get_database()

# Load data with fresh connections to avoid thread issues
@st.cache_data
def load_yb_stats(match_id=None):
    """Load YB team stats with thread-safe connection."""
    with DataAnalysisDB('data/analysis.db') as temp_db:
        if match_id:
            return temp_db.query(f"SELECT * FROM youngbuffalo_stats WHERE match_id = '{match_id}'")
        return temp_db.query("SELECT * FROM yb_stats")

@st.cache_data
def load_enemy_stats(match_id=None):
    """Load enemy team stats with thread-safe connection."""
    with DataAnalysisDB('data/analysis.db') as temp_db:
        if match_id:
            return temp_db.query(f"SELECT * FROM enemy_all_stats WHERE match_id = '{match_id}'")
        return temp_db.query("SELECT * FROM enemy_stats")

@st.cache_data
@st.cache_data
def get_available_matches():
    """Get list of available match dates and IDs from database"""
    with DataAnalysisDB('data/analysis.db') as temp_db:
        query = """
        SELECT DISTINCT match_id,
               substr(match_id, 1, 4) || '-' || substr(match_id, 5, 2) || '-' || substr(match_id, 7, 2) || ' ' ||
               substr(match_id, 10, 2) || ':' || substr(match_id, 12, 2) || ':' || substr(match_id, 14, 2) as match_datetime
        FROM youngbuffalo_stats
        ORDER BY match_id DESC
        """
        return temp_db.query(query)

# Header
st.markdown('<p class="main-header">⚔️ WWM Match Analysis Dashboard v1.2</p>', unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🎮 WWM Data Analysis v1.2")
st.sidebar.divider()

# Match selector in sidebar
st.sidebar.subheader("📅 Match Selection")
available_matches = get_available_matches()

if len(available_matches) > 0:
    match_options = ["Latest Match (All Data)"] + [
        f"{row['match_datetime']}" for _, row in available_matches.iterrows()
    ]
    
    selected_option = st.sidebar.selectbox(
        "Select Match to View",
        match_options,
        help="Choose a specific match or view all latest data"
    )
    
    if selected_option == "Latest Match (All Data)":
        st.session_state.selected_match_id = None
        st.sidebar.info("📊 Viewing latest data from all matches")
    else:
        # Extract match_id from the selected datetime string
        selected_index = match_options.index(selected_option) - 1
        st.session_state.selected_match_id = available_matches.iloc[selected_index]['match_id']
        st.sidebar.success(f"🎯 Viewing Match: {st.session_state.selected_match_id}")
else:
    st.sidebar.warning("⚠️ No matches found in database")
    st.session_state.selected_match_id = None

st.sidebar.divider()

# Main tabs
main_tab, extractor_tab = st.tabs(["📊 Dashboard", "📸 Data Extractor"])

# ==================== DASHBOARD TAB ====================
with main_tab:
    page = st.radio(
        "Select View",
        ["Overview", "YB Team Stats", "Enemy Team Stats", "Head-to-Head Comparison"],
        horizontal=True
    )

    # Overview Page
    if page == "Overview":
        st.header("📊 Match Overview")
        
        yb_df = load_yb_stats(st.session_state.selected_match_id)
        enemy_df = load_enemy_stats(st.session_state.selected_match_id)
        
        # Check if data exists
        if len(yb_df) == 0 and len(enemy_df) == 0:
            st.warning("⚠️ No data found for the selected match. Please select a different match or add data using the Data Extractor.")
            st.stop()
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "YB Team Size",
                len(yb_df),
                delta=None
            )
        
        with col2:
            st.metric(
                "Enemy Team Size",
                len(enemy_df),
                delta=None
            )
        
        with col3:
            yb_total_defeated = yb_df['defeated'].sum()
            enemy_total_defeated = enemy_df['defeated'].sum()
            st.metric(
                "YB Total Defeated",
                yb_total_defeated,
                delta=f"{yb_total_defeated - enemy_total_defeated:+d} vs Enemy"
            )
        
        with col4:
            yb_total_damage = yb_df['damage'].sum()
            enemy_total_damage = enemy_df['damage'].sum()
            st.metric(
                "YB Total Damage",
                f"{yb_total_damage:,}",
                delta=f"{((yb_total_damage - enemy_total_damage) / enemy_total_damage * 100):+.1f}%"
            )
        
        st.divider()
        
        # Team Comparison Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Total Defeated Comparison")
            comparison_data = pd.DataFrame({
                'Team': ['YB Team', 'Enemy Team'],
                'Total Defeated': [yb_total_defeated, enemy_total_defeated]
            })
            fig = px.bar(
                comparison_data,
                x='Team',
                y='Total Defeated',
                color='Team',
                color_discrete_map={'YB Team': '#2ecc71', 'Enemy Team': '#e74c3c'},
                text='Total Defeated'
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("💥 Total Damage Comparison")
            comparison_data = pd.DataFrame({
                'Team': ['YB Team', 'Enemy Team'],
                'Total Damage': [yb_total_damage, enemy_total_damage]
            })
            fig = px.bar(
                comparison_data,
                x='Team',
                y='Total Damage',
                color='Team',
                color_discrete_map={'YB Team': '#2ecc71', 'Enemy Team': '#e74c3c'},
                text='Total Damage'
            )
            fig.update_traces(textposition='outside', texttemplate='%{text:,}')
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Average Stats
        st.subheader("📈 Average Player Statistics")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**YB Team Averages**")
            yb_avg = yb_df[['defeated', 'assist', 'damage', 'tank', 'heal', 'siege_damage']].mean()
            st.dataframe(yb_avg.to_frame(name='Average').style.format("{:.2f}"), use_container_width=True)
        
        with col2:
            st.write("**Enemy Team Averages**")
            enemy_avg = enemy_df[['defeated', 'assist', 'damage', 'tank', 'heal', 'siege_damage']].mean()
            st.dataframe(enemy_avg.to_frame(name='Average').style.format("{:.2f}"), use_container_width=True)

    # YB Team Stats Page
    elif page == "YB Team Stats":
        st.header("🟢 YB Team Statistics")
        
        yb_df = load_yb_stats(st.session_state.selected_match_id)
        
        if len(yb_df) == 0:
            st.warning("⚠️ No YB Team data found for the selected match.")
            st.stop()
        
        # Top performers
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("🏆 Top by Defeated")
            top_defeated = yb_df.nlargest(5, 'defeated')[['player_name', 'defeated', 'damage']]
            st.dataframe(top_defeated, hide_index=True, use_container_width=True)
        
        with col2:
            st.subheader("💥 Top by Damage")
            top_damage = yb_df.nlargest(5, 'damage')[['player_name', 'damage', 'defeated']]
            st.dataframe(top_damage, hide_index=True, use_container_width=True)
        
        with col3:
            st.subheader("🤝 Top by Assist")
            top_assist = yb_df.nlargest(5, 'assist')[['player_name', 'assist', 'defeated']]
            st.dataframe(top_assist, hide_index=True, use_container_width=True)
        
        st.divider()
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Defeated Distribution")
            fig = px.histogram(yb_df, x='defeated', nbins=20, color_discrete_sequence=['#2ecc71'])
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Damage vs Defeated")
            fig = px.scatter(
                yb_df,
                x='defeated',
                y='damage',
                hover_data=['player_name'],
                color='defeated',
                size='damage',
                color_continuous_scale='Greens'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Full data table
        st.subheader("📋 Complete Team Stats")
        st.dataframe(
            yb_df.sort_values('defeated', ascending=False),
            hide_index=True,
            use_container_width=True,
            height=400
        )

    # Enemy Team Stats Page
    elif page == "Enemy Team Stats":
        st.header("🔴 Enemy Team Statistics")
        
        enemy_df = load_enemy_stats(st.session_state.selected_match_id)
        
        if len(enemy_df) == 0:
            st.warning("⚠️ No Enemy Team data found for the selected match.")
            st.stop()
        
        # Top performers
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("🏆 Top by Defeated")
            top_defeated = enemy_df.nlargest(5, 'defeated')[['player_name', 'defeated', 'damage']]
            st.dataframe(top_defeated, hide_index=True, use_container_width=True)
        
        with col2:
            st.subheader("💥 Top by Damage")
            top_damage = enemy_df.nlargest(5, 'damage')[['player_name', 'damage', 'defeated']]
            st.dataframe(top_damage, hide_index=True, use_container_width=True)
        
        with col3:
            st.subheader("🤝 Top by Assist")
            top_assist = enemy_df.nlargest(5, 'assist')[['player_name', 'assist', 'defeated']]
            st.dataframe(top_assist, hide_index=True, use_container_width=True)
        
        st.divider()
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Defeated Distribution")
            fig = px.histogram(enemy_df, x='defeated', nbins=20, color_discrete_sequence=['#e74c3c'])
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Damage vs Defeated")
            fig = px.scatter(
                enemy_df,
                x='defeated',
                y='damage',
                hover_data=['player_name'],
                color='defeated',
                size='damage',
                color_continuous_scale='Reds'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Full data table
        st.subheader("📋 Complete Team Stats")
        st.dataframe(
            enemy_df.sort_values('defeated', ascending=False),
            hide_index=True,
            use_container_width=True,
            height=400
        )

    # Head-to-Head Comparison Page
    elif page == "Head-to-Head Comparison":
        st.header("⚔️ Head-to-Head Analysis")
        
        yb_df = load_yb_stats(st.session_state.selected_match_id)
        enemy_df = load_enemy_stats(st.session_state.selected_match_id)
        
        if len(yb_df) == 0 or len(enemy_df) == 0:
            st.warning("⚠️ Insufficient data for head-to-head comparison.")
            st.stop()
        
        # Select metric for comparison
        metric = st.selectbox(
            "Select Metric to Compare",
            ["defeated", "damage", "assist", "tank", "heal", "siege_damage"]
        )
        
        # Top 10 from each team
        yb_top = yb_df.nlargest(10, metric)[['player_name', metric]].copy()
        yb_top['team'] = 'YB Team'
        
        enemy_top = enemy_df.nlargest(10, metric)[['player_name', metric]].copy()
        enemy_top['team'] = 'Enemy Team'
        
        combined = pd.concat([yb_top, enemy_top])
        
        # Bar chart comparison
        fig = px.bar(
            combined,
            x=metric,
            y='player_name',
            color='team',
            orientation='h',
            color_discrete_map={'YB Team': '#2ecc71', 'Enemy Team': '#e74c3c'},
            title=f'Top 10 Players by {metric.replace("_", " ").title()}'
        )
        fig.update_layout(height=600, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistical comparison
        st.subheader("📊 Statistical Comparison")
        
        col1, col2 = st.columns(2)
        
        metrics_to_compare = ['defeated', 'assist', 'damage', 'tank', 'heal', 'siege_damage']
        
        comparison_data = []
        for m in metrics_to_compare:
            comparison_data.append({
                'Metric': m.replace('_', ' ').title(),
                'YB Team': yb_df[m].sum(),
                'Enemy Team': enemy_df[m].sum(),
                'Difference': yb_df[m].sum() - enemy_df[m].sum()
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        
        with col1:
            st.write("**Total Comparison**")
            st.dataframe(
                comparison_df.style.format({
                    'YB Team': '{:,.0f}',
                    'Enemy Team': '{:,.0f}',
                    'Difference': '{:+,.0f}'
                }),
                hide_index=True,
                use_container_width=True
            )
        
        with col2:
            st.write("**Average Comparison**")
            avg_comparison_data = []
            for m in metrics_to_compare:
                avg_comparison_data.append({
                    'Metric': m.replace('_', ' ').title(),
                    'YB Team': yb_df[m].mean(),
                    'Enemy Team': enemy_df[m].mean(),
                    'Difference': yb_df[m].mean() - enemy_df[m].mean()
                })
            
            avg_comparison_df = pd.DataFrame(avg_comparison_data)
            st.dataframe(
                avg_comparison_df.style.format({
                    'YB Team': '{:.2f}',
                    'Enemy Team': '{:.2f}',
                    'Difference': '{:+.2f}'
                }),
                hide_index=True,
                use_container_width=True
            )


# ==================== DATA EXTRACTOR TAB ====================
with extractor_tab:
    st.header("📸 Match Data Extractor")
    
    extractor_page = st.radio(
        "Extractor Mode",
        ["Upload & Extract", "Review & Save"],
        horizontal=True
    )
    
    if extractor_page == "Upload & Extract":
        st.subheader("📤 Upload Match Screenshots")
        
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
            
            # Clipboard paste button
            st.write("📋 **Paste from Clipboard:**")
            col_paste, col_clear = st.columns([3, 1])
            
            with col_paste:
                paste_result = pbutton(
                    label="📸 Paste Image",
                    key="yb_paste",
                    errors="ignore"
                )
            
            with col_clear:
                if st.button("🗑️ Clear All", key="yb_clear"):
                    st.session_state.yb_pasted_images = []
                    st.rerun()
            
            if paste_result.image_data is not None:
                # Check if this is a new paste by comparing image hash
                img_bytes = io.BytesIO()
                paste_result.image_data.save(img_bytes, format='PNG')
                img_hash = hashlib.md5(img_bytes.getvalue()).hexdigest()
                
                if img_hash != st.session_state.last_yb_paste_id:
                    st.session_state.yb_pasted_images.append(paste_result.image_data)
                    st.session_state.last_yb_paste_id = img_hash
                    st.success(f"✅ Image pasted! Total: {len(st.session_state.yb_pasted_images)} image(s)")
                    st.rerun()
            
            # Show all pasted images
            if len(st.session_state.yb_pasted_images) > 0:
                with st.expander(f"Preview Pasted Images ({len(st.session_state.yb_pasted_images)})"):
                    for i, img in enumerate(st.session_state.yb_pasted_images):
                        col_img, col_del = st.columns([5, 1])
                        with col_img:
                            st.image(img, caption=f"Pasted Image {i+1}", use_container_width=True)
                        with col_del:
                            if st.button("❌", key=f"del_yb_{i}"):
                                st.session_state.yb_pasted_images.pop(i)
                                st.rerun()
            
            st.write("📁 **Or Upload Files:**")
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
                        st.image(img, caption=f"Image {i+1}", use_container_width=True)
                
                # Manual data entry option
                st.markdown("### Enter Data Manually")
                st.write("Please enter the data manually (OCR coming soon):")
                
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
                    st.success("✅ Empty table created. Go to 'Review & Save' to edit data.")
        
        # Enemy Team Upload
        with col_enemy:
            st.subheader("🔴 Enemy Team")
            
            # Clipboard paste button
            st.write("📋 **Paste from Clipboard:**")
            col_paste_e, col_clear_e = st.columns([3, 1])
            
            with col_paste_e:
                paste_result_enemy = pbutton(
                    label="📸 Paste Image",
                    key="enemy_paste",
                    errors="ignore"
                )
            
            with col_clear_e:
                if st.button("🗑️ Clear All", key="enemy_clear"):
                    st.session_state.enemy_pasted_images = []
                    st.rerun()
            
            if paste_result_enemy.image_data is not None:
                # Check if this is a new paste by comparing image hash
                img_bytes = io.BytesIO()
                paste_result_enemy.image_data.save(img_bytes, format='PNG')
                img_hash = hashlib.md5(img_bytes.getvalue()).hexdigest()
                
                if img_hash != st.session_state.last_enemy_paste_id:
                    st.session_state.enemy_pasted_images.append(paste_result_enemy.image_data)
                    st.session_state.last_enemy_paste_id = img_hash
                    st.success(f"✅ Image pasted! Total: {len(st.session_state.enemy_pasted_images)} image(s)")
                    st.rerun()
            
            # Show all pasted images
            if len(st.session_state.enemy_pasted_images) > 0:
                with st.expander(f"Preview Pasted Images ({len(st.session_state.enemy_pasted_images)})"):
                    for i, img in enumerate(st.session_state.enemy_pasted_images):
                        col_img, col_del = st.columns([5, 1])
                        with col_img:
                            st.image(img, caption=f"Pasted Image {i+1}", use_container_width=True)
                        with col_del:
                            if st.button("❌", key=f"del_enemy_{i}"):
                                st.session_state.enemy_pasted_images.pop(i)
                                st.rerun()
            
            st.write("📁 **Or Upload Files:**")
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
                        st.image(img, caption=f"Image {i+1}", use_container_width=True)
                
                # Manual data entry option
                st.markdown("### Enter Data Manually")
                st.write("Please enter the data manually (OCR coming soon):")
                
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
                    st.success("✅ Empty table created. Go to 'Review & Save' to edit data.")
        
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
        
        st.markdown("---")
        
        # OCR Extraction Button
        st.subheader("🤖 Extract Data with OCR")
        
        if not OCR_AVAILABLE:
            st.warning("⚠️ OCR functionality requires EasyOCR. Install with: `pip install easyocr`")
        else:
            st.info("✅ EasyOCR is ready. First-time use may download language models (~100MB).")
        
        col_extract1, col_extract2 = st.columns(2)
        
        with col_extract1:
            st.write("**YB Team Extraction**")
            total_yb_images = len(st.session_state.yb_pasted_images) + (len(yb_files) if yb_files else 0)
            st.info(f"📊 {total_yb_images} image(s) ready for extraction")
            
            if st.button("🔍 Extract YB Team Data", key="extract_yb", disabled=not OCR_AVAILABLE or total_yb_images == 0):
                with st.spinner("Extracting data from images..."):
                    all_yb_data = []
                    errors = []
                    
                    # Process pasted images
                    for i, img in enumerate(st.session_state.yb_pasted_images):
                        df, error = extract_data_from_image(img)
                        if df is not None:
                            all_yb_data.append(df)
                        else:
                            errors.append(f"Pasted Image {i+1}: {error}")
                    
                    # Process uploaded files
                    if yb_files:
                        for i, file in enumerate(yb_files):
                            img = Image.open(file)
                            df, error = extract_data_from_image(img)
                            if df is not None:
                                all_yb_data.append(df)
                            else:
                                errors.append(f"Uploaded Image {i+1}: {error}")
                    
                    if all_yb_data:
                        st.session_state.yb_data = pd.concat(all_yb_data, ignore_index=True)
                        st.success(f"✅ Extracted {len(st.session_state.yb_data)} players from YB Team images!")
                        st.info("👉 Go to 'Review & Save' to verify and save the data.")
                    
                    if errors:
                        with st.expander("⚠️ Extraction Warnings"):
                            for error in errors:
                                st.warning(error)
        
        with col_extract2:
            st.write("**Enemy Team Extraction**")
            total_enemy_images = len(st.session_state.enemy_pasted_images) + (len(enemy_files) if enemy_files else 0)
            st.info(f"📊 {total_enemy_images} image(s) ready for extraction")
            
            if st.button("🔍 Extract Enemy Team Data", key="extract_enemy", disabled=not OCR_AVAILABLE or total_enemy_images == 0):
                with st.spinner("Extracting data from images..."):
                    all_enemy_data = []
                    errors = []
                    
                    # Process pasted images
                    for i, img in enumerate(st.session_state.enemy_pasted_images):
                        df, error = extract_data_from_image(img)
                        if df is not None:
                            all_enemy_data.append(df)
                        else:
                            errors.append(f"Pasted Image {i+1}: {error}")
                    
                    # Process uploaded files
                    if enemy_files:
                        for i, file in enumerate(enemy_files):
                            img = Image.open(file)
                            df, error = extract_data_from_image(img)
                            if df is not None:
                                all_enemy_data.append(df)
                            else:
                                errors.append(f"Uploaded Image {i+1}: {error}")
                    
                    if all_enemy_data:
                        st.session_state.enemy_data = pd.concat(all_enemy_data, ignore_index=True)
                        st.success(f"✅ Extracted {len(st.session_state.enemy_data)} players from Enemy Team images!")
                        st.info("👉 Go to 'Review & Save' to verify and save the data.")
                    
                    if errors:
                        with st.expander("⚠️ Extraction Warnings"):
                            for error in errors:
                                st.warning(error)
    
    elif extractor_page == "Review & Save":
        st.subheader("📊 Review & Save Match Data")
        
        if st.session_state.match_id:
            st.info(f"📋 Match ID: `{st.session_state.match_id}`")
        
        # Check if we have data
        has_yb = st.session_state.yb_data is not None
        has_enemy = st.session_state.enemy_data is not None
        
        if not has_yb and not has_enemy:
            st.warning("⚠️ No data to review. Please upload and extract data first.")
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
                        use_container_width=True,
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
                        use_container_width=True,
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
                if st.button("📥 Download as CSV", use_container_width=True):
                    if has_yb:
                        csv_yb = st.session_state.yb_data.to_csv(index=False)
                        st.download_button(
                            "⬇️ Download YB Team CSV",
                            csv_yb,
                            f"yb_team_{st.session_state.match_id}.csv",
                            "text/csv",
                            use_container_width=True
                        )
                    if has_enemy:
                        csv_enemy = st.session_state.enemy_data.to_csv(index=False)
                        st.download_button(
                            "⬇️ Download Enemy Team CSV",
                            csv_enemy,
                            f"enemy_team_{st.session_state.match_id}.csv",
                            "text/csv",
                            use_container_width=True
                        )
            
            with col2:
                if st.button("💾 Save to Database", type="primary", use_container_width=True):
                    try:
                        db_path = Path('data/analysis.db')
                        # Use check_same_thread=False for Streamlit compatibility
                        conn = sqlite3.connect(db_path, check_same_thread=False)
                        cursor = conn.cursor()
                        
                        match_date = st.session_state.match_id.split('_')[0]
                        
                        # Save YB team
                        if has_yb:
                            # Add to master table
                            df_yb = st.session_state.yb_data.copy()
                            df_yb['match_date'] = match_date
                            df_yb['match_id'] = st.session_state.match_id
                            
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
                        
                        # Clear cache to refresh dashboard data
                        st.cache_data.clear()
                        
                        st.success("🎉 Match data saved successfully!")
                        st.balloons()
                        
                    except Exception as e:
                        st.error(f"❌ Error saving to database: {e}")
            
            with col3:
                if st.button("🗑️ Clear Data", use_container_width=True):
                    st.session_state.yb_data = None
                    st.session_state.enemy_data = None
                    st.session_state.match_id = None
                    st.rerun()


# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: gray; padding: 1rem;'>
        WWM Data Analysis Dashboard v1.2 | Built with Streamlit
    </div>
""", unsafe_allow_html=True)
