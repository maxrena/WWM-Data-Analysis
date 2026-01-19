"""
WWM Data Analysis Dashboard
Interactive web application for analyzing player statistics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path
from datetime import datetime
from fpdf import FPDF
import io
from PIL import Image
import sqlite3

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))
from database import DataAnalysisDB

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

# Initialize database connection
@st.cache_resource
def get_database():
    db = DataAnalysisDB('data/analysis.db')
    db.connect()
    return db

db = get_database()

# Load data
@st.cache_data
def load_yb_stats():
    return db.query("SELECT * FROM yb_stats")

@st.cache_data
def load_enemy_stats():
    return db.query("SELECT * FROM enemy_stats")

# Header
st.markdown('<p class="main-header">⚔️ WWM Match Analysis Dashboard v1.2</p>', unsafe_allow_html=True)

# Main tabs
tab1, tab2 = st.tabs(["📊 Dashboard", "📸 Data Extractor"])

# ==================== DASHBOARD TAB ====================
with tab1:

# PDF Export Function
def generate_pdf_report():
    """Generate comprehensive PDF report of match statistics"""
    pdf = FPDF()
    pdf.add_page()
    
    # Add Unicode font support - use absolute paths
    fonts_dir = Path(__file__).parent / 'fonts'
    pdf.add_font('DejaVu', '', str(fonts_dir / 'DejaVuSans.ttf'), uni=True)
    pdf.add_font('DejaVu', 'B', str(fonts_dir / 'DejaVuSans-Bold.ttf'), uni=True)
    
    # Title
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 10, 'WWM Match Analysis Report', ln=True, align='C')
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 10, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', ln=True, align='C')
    pdf.ln(10)
    
    yb_df = load_yb_stats()
    enemy_df = load_enemy_stats()
    
    # ===== OVERVIEW SECTION =====
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, '1. Team Overview', ln=True)
    pdf.set_font('Arial', '', 10)
    pdf.ln(5)
    
    pdf.cell(90, 8, 'Metric', 1)
    pdf.cell(45, 8, 'YB Team', 1)
    pdf.cell(45, 8, 'Enemy Team', 1, ln=True)
    
    metrics = [
        ('Team Size', len(yb_df), len(enemy_df)),
        ('Total Defeated', yb_df['defeated'].sum(), enemy_df['defeated'].sum()),
        ('Total Damage', yb_df['damage'].sum(), enemy_df['damage'].sum()),
        ('Total Assists', yb_df['assist'].sum(), enemy_df['assist'].sum()),
        ('Total Tank', yb_df['tank'].sum(), enemy_df['tank'].sum()),
        ('Total Heal', yb_df['heal'].sum(), enemy_df['heal'].sum()),
        ('Total Siege Damage', yb_df['siege_damage'].sum(), enemy_df['siege_damage'].sum()),
    ]
    
    for metric, yb_val, enemy_val in metrics:
        pdf.cell(90, 8, metric, 1)
        pdf.cell(45, 8, f'{yb_val:,}', 1)
        pdf.cell(45, 8, f'{enemy_val:,}', 1, ln=True)
    
    pdf.ln(10)
    
    # ===== YB TEAM STATS SECTION =====
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, '2. YB Team Statistics', ln=True)
    pdf.ln(5)
    
    # Top 10 YB Players by Defeated
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Top 10 Players by Defeated', ln=True)
    pdf.set_font('Arial', 'B', 9)
    
    pdf.cell(55, 7, 'Player', 1)
    pdf.cell(25, 7, 'Defeated', 1)
    pdf.cell(30, 7, 'Damage', 1)
    pdf.cell(25, 7, 'Assist', 1)
    pdf.cell(25, 7, 'Tank', 1)
    pdf.cell(20, 7, 'Heal', 1, ln=True)
    
    top_yb = yb_df.nlargest(10, 'defeated')
    for _, row in top_yb.iterrows():
        player_name = str(row['player_name'])[:20]
        pdf.set_font('DejaVu', '', 9)
        pdf.cell(55, 7, player_name, 1)
        pdf.set_font('Arial', '', 9)
        pdf.cell(25, 7, f"{int(row['defeated'])}", 1)
        pdf.cell(30, 7, f"{int(row['damage']):,}", 1)
        pdf.cell(25, 7, f"{int(row['assist'])}", 1)
        pdf.cell(25, 7, f"{int(row['tank']):,}", 1)
        pdf.cell(20, 7, f"{int(row['heal']):,}", 1, ln=True)
    
    pdf.ln(8)
    
    # YB Team Averages
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'YB Team Average Stats', ln=True)
    pdf.set_font('Arial', '', 9)
    
    pdf.cell(60, 7, 'Metric', 1)
    pdf.cell(40, 7, 'Average', 1, ln=True)
    
    for col in ['defeated', 'damage', 'assist', 'tank', 'heal', 'siege_damage']:
        pdf.cell(60, 7, col.replace('_', ' ').title(), 1)
        pdf.cell(40, 7, f"{yb_df[col].mean():,.2f}", 1, ln=True)
    
    pdf.add_page()
    
    # ===== ENEMY TEAM STATS SECTION =====
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, '3. Enemy Team Statistics', ln=True)
    pdf.ln(5)
    
    # Top 10 Enemy Players by Defeated
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Top 10 Players by Defeated', ln=True)
    pdf.set_font('Arial', 'B', 9)
    
    pdf.cell(55, 7, 'Player', 1)
    pdf.cell(25, 7, 'Defeated', 1)
    pdf.cell(30, 7, 'Damage', 1)
    pdf.cell(25, 7, 'Assist', 1)
    pdf.cell(25, 7, 'Tank', 1)
    pdf.cell(20, 7, 'Heal', 1, ln=True)
    
    top_enemy = enemy_df.nlargest(10, 'defeated')
    for _, row in top_enemy.iterrows():
        player_name = str(row['player_name'])[:20]
        pdf.set_font('DejaVu', '', 9)
        pdf.cell(55, 7, player_name, 1)
        pdf.set_font('Arial', '', 9)
        pdf.cell(25, 7, f"{int(row['defeated'])}", 1)
        pdf.cell(30, 7, f"{int(row['damage']):,}", 1)
        pdf.cell(25, 7, f"{int(row['assist'])}", 1)
        pdf.cell(25, 7, f"{int(row['tank']):,}", 1)
        pdf.cell(20, 7, f"{int(row['heal']):,}", 1, ln=True)
    
    pdf.ln(8)
    
    # Enemy Team Averages
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Enemy Team Average Stats', ln=True)
    pdf.set_font('Arial', '', 9)
    
    pdf.cell(60, 7, 'Metric', 1)
    pdf.cell(40, 7, 'Average', 1, ln=True)
    
    for col in ['defeated', 'damage', 'assist', 'tank', 'heal', 'siege_damage']:
        pdf.cell(60, 7, col.replace('_', ' ').title(), 1)
        pdf.cell(40, 7, f"{enemy_df[col].mean():,.2f}", 1, ln=True)
    
    pdf.ln(10)
    
    # ===== HEAD-TO-HEAD COMPARISON SECTION =====
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, '4. Head-to-Head Comparison', ln=True)
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Total Stats Comparison', ln=True)
    pdf.set_font('Arial', '', 9)
    
    pdf.cell(60, 7, 'Metric', 1)
    pdf.cell(35, 7, 'YB Team', 1)
    pdf.cell(35, 7, 'Enemy Team', 1)
    pdf.cell(35, 7, 'Difference', 1, ln=True)
    
    metrics_compare = ['defeated', 'damage', 'assist', 'tank', 'heal', 'siege_damage']
    for metric in metrics_compare:
        yb_total = yb_df[metric].sum()
        enemy_total = enemy_df[metric].sum()
        diff = yb_total - enemy_total
        
        pdf.cell(60, 7, metric.replace('_', ' ').title(), 1)
        pdf.cell(35, 7, f"{yb_total:,.0f}", 1)
        pdf.cell(35, 7, f"{enemy_total:,.0f}", 1)
        pdf.cell(35, 7, f"{diff:+,.0f}", 1, ln=True)
    
    pdf.ln(8)
    
    # Average Comparison
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Average Stats Comparison', ln=True)
    pdf.set_font('Arial', '', 9)
    
    pdf.cell(60, 7, 'Metric', 1)
    pdf.cell(35, 7, 'YB Team', 1)
    pdf.cell(35, 7, 'Enemy Team', 1)
    pdf.cell(35, 7, 'Difference', 1, ln=True)
    
    for metric in metrics_compare:
        yb_avg = yb_df[metric].mean()
        enemy_avg = enemy_df[metric].mean()
        diff = yb_avg - enemy_avg
        
        pdf.cell(60, 7, metric.replace('_', ' ').title(), 1)
        pdf.cell(35, 7, f"{yb_avg:.2f}", 1)
        pdf.cell(35, 7, f"{enemy_avg:.2f}", 1)
        pdf.cell(35, 7, f"{diff:+.2f}", 1, ln=True)
    
    # Footer
    pdf.ln(15)
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(0, 10, 'End of Report', ln=True, align='C')
    
    # Return PDF as bytes
    return bytes(pdf.output())

# Sidebar
st.sidebar.title("🎮 WWM Data Analysis v1.2")
st.sidebar.divider()

# PDF Export Button
st.sidebar.subheader("📄 Export")
if st.sidebar.button("📥 Download PDF Report", use_container_width=True):
    try:
        pdf_bytes = generate_pdf_report()
        st.sidebar.download_button(
            label="💾 Save PDF",
            data=pdf_bytes,
            file_name=f"wwm_match_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        st.sidebar.success("✅ PDF ready for download!")
    except Exception as e:
        st.sidebar.error(f"Error generating PDF: {e}")

# Create tabs
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
    
    yb_df = load_yb_stats()
    enemy_df = load_enemy_stats()
    
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
    
    yb_df = load_yb_stats()
    
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
    
    enemy_df = load_enemy_stats()
    
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
    
    yb_df = load_yb_stats()
    enemy_df = load_enemy_stats()
    
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
                        conn = sqlite3.connect(db_path)
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
