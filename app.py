"""
Excelra Indication Expansion / Drug Repurposing Demo
Interactive sales demonstration tool showcasing GRIP-based repurposing workflow
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import json
import base64
from pathlib import Path
from PIL import Image

# =============================================================================
# PAGE CONFIG
# =============================================================================
# Load page icon
icon_path = Path(__file__).parent / "assets" / "repurpose2.png"
page_icon = Image.open(icon_path) if icon_path.exists() else "🔬"

st.set_page_config(
    page_title="Excelra | Indication Expansion & Drug Repurposing",
    page_icon=page_icon,
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# BRAND COLOURS (from Excelra Brand Guidelines)
# =============================================================================
# Primary Colours
DEEP_BLUE = "#0A1E4A"      # Trust, intelligence, depth
VIOLET = "#A24DBE"          # Innovation, creativity
MAGENTA = "#E04F8A"         # Vibrancy, energy
TURQUOISE = "#00A6A6"       # Brand turquoise/teal

# Secondary Colours
LIGHT_BLUE = "#B3E0F2"      # Highlights, backgrounds
SOFT_LAVENDER = "#E3D9F2"   # Balance, calmness
WHITE = "#FFFFFF"           # Clarity, openness

# Additional UI colours
LIGHT_PINK = "#F7D6E6"      # Soft magenta tint
VIOLET_LIGHT = "#F3E8F7"    # Soft violet tint
TURQUOISE_LIGHT = "#E0F5F5" # Soft turquoise tint

# =============================================================================
# ASSET LOADING FUNCTIONS
# =============================================================================

def get_base64_image(image_path):
    """Convert image to base64 for embedding in HTML"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return None

def get_image_html(image_name, width="24px", height="24px"):
    """Get HTML img tag for an asset image"""
    image_path = Path(__file__).parent / "assets" / image_name
    b64 = get_base64_image(image_path)
    if b64:
        return f'<img src="data:image/png;base64,{b64}" width="{width}" height="{height}" style="vertical-align: middle;">'
    return ""

def load_image_as_base64(image_name):
    """Load image and return base64 string"""
    image_path = Path(__file__).parent / "assets" / image_name
    return get_base64_image(image_path)

# =============================================================================
# CUSTOM CSS
# =============================================================================
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {{ font-family: 'Poppins', sans-serif !important; }}
    
    /* White background */
    .stApp {{ background: {WHITE}; }}
    
    /* Hide Streamlit elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .stDeployButton {{display: none;}}
    
    /* Sidebar - Light/Off-white for professional look */
    section[data-testid="stSidebar"] {{ 
        background: #F8F9FA; 
        min-width: 280px;
        max-width: 280px;
        border-right: 1px solid #E8E8E8;
    }}
    section[data-testid="stSidebar"] * {{ color: {DEEP_BLUE} !important; }}
    section[data-testid="stSidebar"] hr {{ border-color: rgba(10, 30, 74, 0.1); }}
    
    /* Sidebar button styling - light theme */
    section[data-testid="stSidebar"] .stButton > button {{
        background: {WHITE};
        border: 1px solid #E0E0E0;
        color: {DEEP_BLUE} !important;
        width: 100%;
        text-align: left;
        padding: 0.75rem 1rem;
        margin-bottom: 0.25rem;
        border-radius: 8px;
        transition: all 0.2s ease;
    }}
    section[data-testid="stSidebar"] .stButton > button:hover {{
        background: {SOFT_LAVENDER};
        border-color: {VIOLET};
        box-shadow: 0 2px 8px rgba(162, 77, 190, 0.15);
    }}
    
    /* Page header - Off-white with wave background */
    .page-header {{
        background: linear-gradient(135deg, #F8F9FA 0%, {SOFT_LAVENDER} 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(10, 30, 74, 0.08);
        position: relative;
        overflow: hidden;
        border: 1px solid #E8E8E8;
    }}
    .page-header::after {{
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        bottom: 0;
        width: 60%;
        background-image: var(--wave-bg);
        background-position: right center;
        background-repeat: no-repeat;
        background-size: auto 280%;
        opacity: 0.4;
        pointer-events: none;
    }}
    .page-header h1 {{
        color: {DEEP_BLUE} !important;
        font-size: 1.6rem;
        font-weight: 600;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
        position: relative;
        z-index: 1;
    }}
    .page-header p {{
        color: #666 !important;
        font-size: 0.95rem;
        margin: 0.4rem 0 0 0;
        position: relative;
        z-index: 1;
    }}
    
    /* Metric cards - with turquoise accent */
    .metric-card {{
        background: {WHITE};
        border-radius: 10px;
        padding: 1.25rem;
        border: 1px solid #E8E8E8;
        border-left: 4px solid {LIGHT_BLUE};
        min-height: 100px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: transform 0.2s, box-shadow 0.2s;
    }}
    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        border-left-color: {MAGENTA};
    }}
    .metric-card h3 {{
        color: {DEEP_BLUE} !important;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
        margin: 0 0 0.4rem 0;
    }}
    .metric-card .value {{
        color: {DEEP_BLUE} !important;
        font-size: 1.4rem;
        font-weight: 700;
        margin: 0;
        line-height: 1.2;
    }}
    .metric-card .subtext {{
        color: #666 !important;
        font-size: 0.75rem;
        margin-top: 0.3rem;
    }}
    
    /* Section headers - with turquoise underline */
    .section-header {{
        color: {DEEP_BLUE} !important;
        font-size: 1.15rem;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid {LIGHT_BLUE};
        display: inline-flex;
        align-items: center;
        gap: 10px;
    }}
    
    /* Workflow steps */
    .workflow-step {{
        text-align: center;
        padding: 1rem 0.5rem;
        background: {WHITE};
        border-radius: 10px;
        border: 1px solid #E8E8E8;
        border-top: 3px solid #E8E8E8;
        transition: all 0.3s;
    }}
    .workflow-step.active {{
        border-top-color: {LIGHT_BLUE};
        background: linear-gradient(180deg, rgba(179, 224, 242, 0.2) 0%, {WHITE} 100%);
        box-shadow: 0 4px 16px rgba(179, 224, 242, 0.3);
    }}
    .workflow-step.complete {{
        border-top-color: {MAGENTA};
        background: linear-gradient(180deg, {LIGHT_PINK} 0%, {WHITE} 100%);
    }}
    .workflow-step .step-icon {{
        margin-bottom: 0.5rem;
    }}
    .workflow-step .step-icon img {{
        width: 32px;
        height: 32px;
    }}
    .workflow-step .step-title {{
        font-size: 0.8rem;
        font-weight: 600;
        color: {DEEP_BLUE};
        margin-bottom: 0.3rem;
    }}
    .workflow-step .step-desc {{
        font-size: 0.65rem;
        color: #666;
    }}
    
    /* Tier badges */
    .tier-badge {{
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }}
    .tier-i {{ background: {LIGHT_PINK}; color: {MAGENTA}; border: 1px solid {MAGENTA}; }}
    .tier-ii {{ background: {VIOLET_LIGHT}; color: {VIOLET}; border: 1px solid {VIOLET}; }}
    .tier-iii {{ background: rgba(179, 224, 242, 0.4); color: {DEEP_BLUE}; border: 1px solid {LIGHT_BLUE}; }}
    
    /* Info box - with turquoise accent */
    .info-box {{
        background: linear-gradient(135deg, #F8FAFC 0%, rgba(179, 224, 242, 0.2) 100%);
        border-radius: 10px;
        padding: 1.25rem;
        border-left: 4px solid {LIGHT_BLUE};
        margin: 1rem 0;
    }}
    .info-box h4 {{
        color: {DEEP_BLUE};
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .info-box p {{
        color: #4A5568;
        font-size: 0.85rem;
        margin: 0;
        line-height: 1.5;
    }}
    
    /* Asset card */
    .asset-card {{
        background: {WHITE};
        border-radius: 12px;
        padding: 1.5rem;
        border: 2px solid #E8E8E8;
        transition: all 0.3s;
        cursor: pointer;
    }}
    .asset-card:hover {{
        border-color: {LIGHT_BLUE};
        box-shadow: 0 4px 20px rgba(179, 224, 242, 0.3);
    }}
    .asset-card.selected {{
        border-color: {MAGENTA};
        background: linear-gradient(180deg, {LIGHT_PINK} 0%, {WHITE} 100%);
    }}
    .asset-card h4 {{
        color: {DEEP_BLUE};
        font-size: 1rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
    }}
    .asset-card .asset-meta {{
        font-size: 0.8rem;
        color: #666;
    }}
    
    /* Progress bar - gradient with turquoise */
    .progress-container {{
        background: #E8E8E8;
        border-radius: 10px;
        height: 8px;
        overflow: hidden;
        margin: 1rem 0;
    }}
    .progress-bar {{
        background: linear-gradient(90deg, {LIGHT_BLUE} 0%, {MAGENTA} 100%);
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease-out;
    }}
    
    /* Button styling */
    .stButton > button {{
        background: linear-gradient(135deg, {MAGENTA} 0%, {VIOLET} 100%);
        color: white;
        border: none;
        padding: 0.6rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }}
    .stButton > button:hover {{
        background: linear-gradient(135deg, {VIOLET} 0%, {MAGENTA} 100%);
        box-shadow: 0 4px 12px rgba(162, 77, 190, 0.3);
    }}
    
    /* Primary button with turquoise option */
    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, {LIGHT_BLUE} 0%, {MAGENTA} 100%);
    }}
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background: transparent;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: rgba(179, 224, 242, 0.2);
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 1rem;
        font-weight: 500;
        border: 1px solid {LIGHT_BLUE};
        border-bottom: none;
    }}
    .stTabs [aria-selected="true"] {{
        background: {MAGENTA} !important;
        color: white !important;
        border-color: {MAGENTA} !important;
    }}
    
    /* Differentiator item */
    .diff-item {{
        display: flex;
        align-items: center;
        padding: 0.75rem;
        background: rgba(179, 224, 242, 0.1);
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 3px solid {LIGHT_BLUE};
    }}
    .diff-item img {{
        width: 28px;
        height: 28px;
        margin-right: 1rem;
    }}
    .diff-item .diff-content {{
        flex: 1;
    }}
    .diff-item .diff-title {{
        font-weight: 600;
        color: {DEEP_BLUE};
        font-size: 0.9rem;
    }}
    .diff-item .diff-desc {{
        font-size: 0.75rem;
        color: #666;
    }}
    
    /* Logo container */
    .logo-container {{
        padding: 1rem;
        text-align: center;
        margin-bottom: 0.5rem;
    }}
    
    /* Slogan styling */
    .slogan-text {{
        color: {LIGHT_BLUE} !important;
        font-size: 0.8rem;
        font-style: italic;
        text-align: center;
        margin-bottom: 1rem;
    }}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SAMPLE DATA - Based on "Repurposing Shelved Phase II Asset Using Multi-OMICS"
# =============================================================================

@st.cache_data
def load_sample_data():
    """Load sample data simulating the Japanese Pharma Phase II sleep disorder case"""
    
    # Asset information
    asset_info = {
        "compound_id": "EXC-7842",
        "compound_name": "Somnolexin",
        "target": "Orexin Receptor 2 (OX2R)",
        "modality": "Small Molecule",
        "original_indication": "Sleep Disorders (Insomnia)",
        "development_stage": "Phase II (Terminated)",
        "termination_reason": "Efficacy endpoints not met in pivotal trial",
        "available_data": ["Lipidomic data", "siRNA knockdown data", "Metabolomic profiling", "Phase II clinical samples"],
        "moa": "Selective OX2R antagonist with demonstrated CNS penetration"
    }
    
    # Tiered indication results
    indications = pd.DataFrame([
        # Tier I - Strong evidence (6 sources)
        {"indication": "Retinal Degeneration", "mesh_category": "Eye Diseases", "tier": "I", 
         "clinical_trials": True, "adverse_events": True, "literature": True, "pathways": True, "omics": True, "interactome": True,
         "score": 6, "evidence_status": "Clinical + Preclinical", "confidence": "High",
         "rationale": "OX2R expression in retinal ganglion cells; orexin signalling linked to neuroprotection"},
        {"indication": "Cystic Fibrosis", "mesh_category": "Respiratory Diseases", "tier": "I",
         "clinical_trials": True, "adverse_events": True, "literature": True, "pathways": True, "omics": True, "interactome": False,
         "score": 5, "evidence_status": "Clinical + Preclinical", "confidence": "High",
         "rationale": "Metabolomic overlap with CF pathways; lipid dysregulation rescue potential"},
        {"indication": "Insulin Resistance", "mesh_category": "Metabolic Diseases", "tier": "I",
         "clinical_trials": True, "adverse_events": True, "literature": True, "pathways": True, "omics": True, "interactome": False,
         "score": 5, "evidence_status": "Clinical + Preclinical", "confidence": "High",
         "rationale": "Orexin-metabolic axis; lipidomic signatures consistent with insulin sensitisation"},
        
        # Tier II - Moderate evidence (4 sources)
        {"indication": "Atherosclerosis", "mesh_category": "Cardiovascular Diseases", "tier": "II",
         "clinical_trials": False, "adverse_events": True, "literature": True, "pathways": True, "omics": True, "interactome": False,
         "score": 4, "evidence_status": "Preclinical", "confidence": "Medium",
         "rationale": "Lipid metabolism modulation; anti-inflammatory pathway engagement"},
        {"indication": "Non-Alcoholic Fatty Liver Disease", "mesh_category": "Digestive Diseases", "tier": "II",
         "clinical_trials": False, "adverse_events": True, "literature": True, "pathways": True, "omics": True, "interactome": False,
         "score": 4, "evidence_status": "Preclinical", "confidence": "Medium",
         "rationale": "Hepatic lipid accumulation pathways; metabolomic evidence of steatosis markers"},
        {"indication": "HIV-Associated Lipodystrophy", "mesh_category": "Immune Diseases", "tier": "II",
         "clinical_trials": False, "adverse_events": True, "literature": True, "pathways": True, "omics": False, "interactome": True,
         "score": 4, "evidence_status": "Preclinical", "confidence": "Medium",
         "rationale": "Adipocyte differentiation pathways; metabolic syndrome overlap"},
        {"indication": "Schizophrenia", "mesh_category": "Mental Disorders", "tier": "II",
         "clinical_trials": False, "adverse_events": True, "literature": True, "pathways": True, "omics": True, "interactome": False,
         "score": 4, "evidence_status": "Preclinical", "confidence": "Medium",
         "rationale": "CNS target with orexin dysregulation in psychosis; existing CNS safety profile"},
        
        # Tier III - Emerging evidence (3 sources)
        {"indication": "Parkinson's Disease", "mesh_category": "Neurodegenerative Diseases", "tier": "III",
         "clinical_trials": False, "adverse_events": True, "literature": True, "pathways": True, "omics": False, "interactome": False,
         "score": 3, "evidence_status": "Literature", "confidence": "Low",
         "rationale": "Orexin neuron loss in PD; potential for sleep-motor symptom dual benefit"},
        {"indication": "Chronic Kidney Disease", "mesh_category": "Urological Diseases", "tier": "III",
         "clinical_trials": False, "adverse_events": True, "literature": True, "pathways": False, "omics": True, "interactome": False,
         "score": 3, "evidence_status": "Literature", "confidence": "Low",
         "rationale": "Metabolic crosstalk; renal lipid handling pathways"},
        {"indication": "Type 2 Diabetes", "mesh_category": "Metabolic Diseases", "tier": "III",
         "clinical_trials": False, "adverse_events": False, "literature": True, "pathways": True, "omics": True, "interactome": False,
         "score": 3, "evidence_status": "Literature", "confidence": "Low",
         "rationale": "Glucose-orexin axis; metabolic syndrome overlap with insulin resistance"},
    ])
    
    # Evidence matrix for heatmap
    evidence_matrix = indications[["indication", "clinical_trials", "adverse_events", "literature", "pathways", "omics", "interactome"]].copy()
    evidence_matrix.columns = ["Indication", "Clinical Trials", "Adverse Events", "Literature", "Pathways", "Omics", "Interactome"]
    
    # Database sources
    databases = {
        "Public Databases": ["DrugBank", "ChEMBL", "ClinicalTrials.gov", "DisGeNET", "OMIM", "KEGG", "Reactome", 
                            "STRING", "IntAct", "PharmGKB", "CTD", "SIDER", "OFFSIDES", "GEO", "TCGA"],
        "Proprietary": ["GOSTAR", "CTOD", "GRID"],
        "Omics Sources": ["Lipidomics (Client)", "Metabolomics (Client)", "siRNA (Client)", "Phase II Samples (Client)"]
    }
    
    return asset_info, indications, evidence_matrix, databases


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def render_metric_card(title, value, subtext=None, icon_name=None):
    """Render a styled metric card with optional icon"""
    icon_html = ""
    if icon_name:
        icon_html = get_image_html(icon_name, "32px", "32px")
    
    subtext_html = f'<p class="subtext">{subtext}</p>' if subtext else ''
    return f"""
    <div class="metric-card">
        <h3>{icon_html} {title}</h3>
        <p class="value">{value}</p>
        {subtext_html}
    </div>
    """

def render_tier_badge(tier):
    """Render a tier badge"""
    tier_class = f"tier-{tier.lower()}"
    return f'<span class="tier-badge {tier_class}">Tier {tier}</span>'

def render_workflow_step(icon_name, title, desc, status="pending"):
    """Render a workflow step card with custom icon"""
    status_class = status if status in ["active", "complete"] else ""
    icon_html = get_image_html(icon_name, "44px", "44px")
    return f"""
    <div class="workflow-step {status_class}">
        <div class="step-icon">{icon_html}</div>
        <div class="step-title">{title}</div>
        <div class="step-desc">{desc}</div>
    </div>
    """

def create_evidence_heatmap(evidence_df):
    """Create an interactive evidence heatmap - subtle and readable design"""
    cols = ["Clinical Trials", "Adverse Events", "Literature", "Pathways", "Omics", "Interactome"]
    z_data = evidence_df[cols].astype(int).values
    
    # Subtle colorscale - light lavender for positive, very light grey for negative
    colorscale = [[0, '#FAFAFA'], [1, SOFT_LAVENDER]]
    
    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=cols,
        y=evidence_df["Indication"].tolist(),
        colorscale=colorscale,
        showscale=False,
        hoverongaps=False,
        hovertemplate="<b>%{y}</b><br>%{x}: %{z}<extra></extra>",
        xgap=3,  # Add gaps between cells
        ygap=3
    ))
    
    # Add text annotations - using dots/circles for a cleaner look
    for i, row in enumerate(z_data):
        for j, val in enumerate(row):
            fig.add_annotation(
                x=cols[j],
                y=evidence_df["Indication"].iloc[i],
                text="●" if val == 1 else "○",
                showarrow=False,
                font=dict(size=16, color=VIOLET if val == 1 else "#E0E0E0", family="Poppins")
            )
    
    fig.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(
            side="top", 
            tickangle=0,
            tickfont=dict(size=11, color=DEEP_BLUE, family="Poppins"),
            gridcolor="white",
            gridwidth=2
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(size=11, color=DEEP_BLUE, family="Poppins"),
            gridcolor="white",
            gridwidth=2
        ),
        font=dict(family="Poppins", size=11, color=DEEP_BLUE),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig

def create_sankey_diagram(indications_df):
    """Create a Sankey diagram showing evidence flow"""
    sources = []
    targets = []
    values = []
    
    evidence_types = ["Clinical Trials", "Adverse Events", "Literature", "Pathways", "Omics", "Interactome"]
    evidence_cols = ["clinical_trials", "adverse_events", "literature", "pathways", "omics", "interactome"]
    
    # Node labels
    labels = evidence_types + indications_df["indication"].tolist()
    
    # Node colors - using brand colours
    node_colors = [VIOLET] * 6 + [MAGENTA if t == "I" else VIOLET if t == "II" else LIGHT_BLUE 
                                 for t in indications_df["tier"]]
    
    # Create links
    for i, (_, row) in enumerate(indications_df.iterrows()):
        for j, col in enumerate(evidence_cols):
            if row[col]:
                sources.append(j)
                targets.append(6 + i)
                values.append(1)
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=25,
            line=dict(color="white", width=1),
            label=labels,
            color=node_colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color="rgba(162, 77, 190, 0.3)"
        ),
        textfont=dict(size=14, color=DEEP_BLUE, family="Poppins")
    )])
    
    fig.update_layout(
        height=500,
        margin=dict(l=10, r=10, t=30, b=10),
        font=dict(family="Poppins", size=14, color=DEEP_BLUE),
        paper_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig

def create_tier_distribution_chart(indications_df):
    """Create a donut chart showing tier distribution"""
    tier_counts = indications_df["tier"].value_counts().sort_index()
    
    # Brand colours for tiers
    colors = [MAGENTA, VIOLET, LIGHT_BLUE]
    
    fig = go.Figure(data=[go.Pie(
        labels=[f"Tier {t}" for t in tier_counts.index],
        values=tier_counts.values,
        hole=0.6,
        marker=dict(colors=colors),
        textinfo="label+value",
        textposition="outside",
        textfont=dict(size=12, family="Poppins", color=DEEP_BLUE)
    )])
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=False,
        font=dict(family="Poppins", color=DEEP_BLUE),
        paper_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(
            text=f"<b>10</b><br>Indications",
            x=0.5, y=0.5,
            font=dict(size=14, color=DEEP_BLUE, family="Poppins"),
            showarrow=False
        )]
    )
    
    return fig


# =============================================================================
# PAGE FUNCTIONS
# =============================================================================

def page_overview():
    """Overview page - Demo introduction and case context"""
    # Header with icon and wave background
    repurpose_icon = get_image_html("repurpose.png", "48px", "48px")
    wave_b64 = load_image_as_base64("Wave.png")
    
    wave_style = ""
    if wave_b64:
        wave_style = f"--wave-bg: url('data:image/png;base64,{wave_b64}');"
    
    st.markdown(f"""
    <div class="page-header" style="{wave_style}">
        <h1>{repurpose_icon} Indication Expansion & Drug Repurposing</h1>
        <p>Interactive demonstration of the GRIP-powered repurposing workflow</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Demo case introduction
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f'<p class="section-header">Demo Case: Shelved Phase II Asset</p>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #F8FAFC 0%, {SOFT_LAVENDER} 100%); 
                    padding: 1.5rem; border-radius: 12px; border-left: 4px solid {MAGENTA};">
            <p style="color: #4A5568; font-size: 0.95rem; line-height: 1.6; margin: 0;">
                A <strong>Japanese large pharma</strong> has a shelved compound that failed Phase II trials for 
                <strong>sleep disorders</strong>. They have multi-omics data from the clinical programme and need 
                to identify alternative indications to recover their R&D investment.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Asset summary
        st.markdown(f"""
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div style="background: #F8F9FA; padding: 1rem; border-radius: 8px;">
                <p style="font-size: 0.7rem; color: #666; text-transform: uppercase; margin: 0 0 0.3rem 0;">Compound</p>
                <p style="font-size: 1rem; color: {DEEP_BLUE}; font-weight: 600; margin: 0;">EXC-7842 (Somnolexin)</p>
            </div>
            <div style="background: #F8F9FA; padding: 1rem; border-radius: 8px;">
                <p style="font-size: 0.7rem; color: #666; text-transform: uppercase; margin: 0 0 0.3rem 0;">Target</p>
                <p style="font-size: 1rem; color: {DEEP_BLUE}; font-weight: 600; margin: 0;">Orexin Receptor 2 (OX2R)</p>
            </div>
            <div style="background: #F8F9FA; padding: 1rem; border-radius: 8px;">
                <p style="font-size: 0.7rem; color: #666; text-transform: uppercase; margin: 0 0 0.3rem 0;">Original Indication</p>
                <p style="font-size: 1rem; color: {DEEP_BLUE}; font-weight: 600; margin: 0;">Sleep Disorders (Insomnia)</p>
            </div>
            <div style="background: #F8F9FA; padding: 1rem; border-radius: 8px;">
                <p style="font-size: 0.7rem; color: #666; text-transform: uppercase; margin: 0 0 0.3rem 0;">Stage</p>
                <p style="font-size: 1rem; color: {MAGENTA}; font-weight: 600; margin: 0;">Phase II (Terminated)</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Available data card
        data_icon = get_image_html("Data acquisition.png", "32px", "32px")
        st.markdown(f'<p class="section-header">{data_icon} Available Data</p>', unsafe_allow_html=True)
        
        data_types = [
            ("lipidomimc.png", "Lipidomic profiling"),
            ("metabolomic.png", "Metabolomics"),
            ("Gene.png", "siRNA knockdown"),
            ("Clinical.png", "Phase II samples")
        ]
        
        for icon_file, label in data_types:
            icon_html = get_image_html(icon_file, "28px", "28px")
            # Fallback if icon not found
            if not icon_html:
                icon_html = "•"
            st.markdown(f"""<div style="display: flex; align-items: center; padding: 0.6rem; background: #F8F9FA; border-radius: 6px; margin-bottom: 0.5rem; border-left: 3px solid {VIOLET};">{icon_html}<span style="margin-left: 0.75rem; font-size: 0.85rem; color: {DEEP_BLUE};">{label}</span></div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Workflow preview
    st.markdown(f'<p class="section-header">Workflow Steps</p>', unsafe_allow_html=True)
    
    workflow_steps = [
        ("Input.png", "1. Configure Asset", "Set up compound and data inputs"),
        ("Network.png", "2. Run GRIP Analysis", "Query 40+ databases for drug-disease associations"),
        ("ranking.png", "3. View Ranked Results", "Tiered indication shortlist with evidence scores"),
        ("deep_dive.png", "4. Explore Deep-Dive", "Scientific rationale and next steps")
    ]
    
    step_cols = st.columns(4)
    for i, (col, (icon, title, desc)) in enumerate(zip(step_cols, workflow_steps)):
        with col:
            icon_html = get_image_html(icon, "44px", "44px")
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background: {WHITE}; border-radius: 10px; 
                        border: 1px solid #E8E8E8; border-top: 3px solid {MAGENTA}; min-height: 140px;
                        display: flex; flex-direction: column; justify-content: flex-start; align-items: center;">
                <div style="margin-bottom: 0.5rem;">{icon_html}</div>
                <p style="font-size: 0.85rem; font-weight: 600; color: {DEEP_BLUE}; margin: 0 0 0.3rem 0;">{title}</p>
                <p style="font-size: 0.7rem; color: #666; margin: 0;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Slogan at bottom center
    slogan_b64 = load_image_as_base64("Slogan.png")
    if slogan_b64:
        st.markdown(f"""
        <div style="text-align: center; margin-top: 2rem; padding: 1rem;">
            <img src="data:image/png;base64,{slogan_b64}" style="width: 300px; opacity: 0.9;">
        </div>
        """, unsafe_allow_html=True)


def page_asset_input():
    """Asset input/selection page - interactive configuration"""
    input_icon = get_image_html("Input.png", "48px", "48px")
    wave_b64 = load_image_as_base64("Wave.png")
    
    wave_style = ""
    if wave_b64:
        wave_style = f"--wave-bg: url('data:image/png;base64,{wave_b64}');"
    
    st.markdown(f"""
    <div class="page-header" style="{wave_style}">
        <h1>{input_icon} Asset Configuration</h1>
        <p>Configure the compound and analysis parameters</p>
    </div>
    """, unsafe_allow_html=True)
    
    asset_info, _, _, _ = load_sample_data()
    
    # Two column layout
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        compound_icon = get_image_html("deep_dive.png", "32px", "32px")
        st.markdown(f'<p class="section-header">{compound_icon} Compound Details</p>', unsafe_allow_html=True)
        
        # Compound selection (simulated)
        compound = st.selectbox(
            "Select Compound",
            ["EXC-7842 (Somnolexin)", "EXC-3901 (Cardivex)", "EXC-5523 (Neurolin)"],
            index=0,
            help="Select the compound for repurposing analysis"
        )
        
        # Show compound details based on selection
        if "EXC-7842" in compound:
            st.markdown(f"""
            <div style="background: #F8F9FA; padding: 1rem; border-radius: 8px; margin-top: 0.5rem;">
                <p style="margin: 0 0 0.5rem 0;"><strong>Target:</strong> Orexin Receptor 2 (OX2R)</p>
                <p style="margin: 0 0 0.5rem 0;"><strong>Modality:</strong> Small Molecule</p>
                <p style="margin: 0 0 0.5rem 0;"><strong>Original Indication:</strong> Sleep Disorders</p>
                <p style="margin: 0;"><strong>Stage:</strong> <span style="color: {MAGENTA};">Phase II (Terminated)</span></p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Data sources
        data_icon = get_image_html("Data acquisition.png", "32px", "32px")
        st.markdown(f'<p class="section-header">{data_icon} Available Data</p>', unsafe_allow_html=True)
        
        # Checkboxes for data selection
        st.markdown("Select data sources to include:")
        col_data1, col_data2 = st.columns(2)
        with col_data1:
            data_lipidomics = st.checkbox("Lipidomic profiling", value=True)
            data_metabolomics = st.checkbox("Metabolomics", value=True)
        with col_data2:
            data_sirna = st.checkbox("siRNA knockdown data", value=True)
            data_clinical = st.checkbox("Phase II clinical samples", value=True)
        
        selected_data_count = sum([data_lipidomics, data_metabolomics, data_sirna, data_clinical])
    
    with col_right:
        flow_icon = get_image_html("flow.png", "32px", "32px")
        st.markdown(f'<p class="section-header">{flow_icon} Analysis Parameters</p>', unsafe_allow_html=True)
        
        # Repurposing strategy
        strategy = st.selectbox(
            "Repurposing Strategy",
            ["Drug-Centric", "Target-Centric", "Disease-Centric", "Multi-Pronged"],
            index=0,
            help="Drug-centric: Find new indications for this compound. Target-centric: Find indications based on target biology."
        )
        
        # Therapeutic area focus
        ta_options = ["All Therapeutic Areas", "Oncology", "CNS / Neurology", "Metabolic / Endocrine", 
                      "Cardiovascular", "Rare Disease", "Autoimmune / Inflammation", "Ophthalmology"]
        therapeutic_areas = st.multiselect(
            "Therapeutic Area Focus",
            ta_options,
            default=["All Therapeutic Areas"],
            help="Filter results to specific therapeutic areas"
        )
        
        # Evidence threshold - using selectbox for better visibility
        threshold_options = {
            "≥2 sources (Exploratory)": 2,
            "≥3 sources (Standard)": 3, 
            "≥4 sources (High Confidence)": 4,
            "≥5 sources (Very High Confidence)": 5
        }
        selected_threshold = st.selectbox(
            "Minimum Evidence Sources",
            options=list(threshold_options.keys()),
            index=1,  # Default to Standard (≥3)
            help="Minimum number of evidence sources required for inclusion"
        )
        evidence_threshold = threshold_options[selected_threshold]
        
        # Additional options
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Additional Options:**")
        include_rare = st.checkbox("Include rare disease indications", value=True)
        include_pediatric = st.checkbox("Include paediatric indications", value=False)
        competitive_filter = st.checkbox("Filter by competitive landscape", value=False)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Summary and Run button
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"""
        <div style="background: {VIOLET_LIGHT}; padding: 1rem; border-radius: 8px;">
            <p style="margin: 0; font-size: 0.85rem; color: {DEEP_BLUE};">
                <strong>Configuration Summary:</strong> {compound.split(' ')[0]} | {strategy} strategy | 
                {len(therapeutic_areas)} TA(s) | ≥{evidence_threshold} evidence sources | {selected_data_count} data source(s)
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Show Start icon above the button
        start_icon = get_image_html("Start.png", "32px", "32px")
        st.markdown(f'<div style="text-align: center; margin-bottom: 0.5rem;">{start_icon}</div>', unsafe_allow_html=True)
        if st.button("Run Analysis", use_container_width=True, type="primary"):
            st.session_state.analysis_step = 0  # Reset analysis progress
            st.session_state.page = "analysis"
            st.rerun()


def page_analysis():
    """Analysis workflow page with manual step progression"""
    analysis_icon = get_image_html("Analysis.png", "48px", "48px")
    wave_b64 = load_image_as_base64("Wave.png")
    
    wave_style = ""
    if wave_b64:
        wave_style = f"--wave-bg: url('data:image/png;base64,{wave_b64}');"
    
    st.markdown(f"""
    <div class="page-header" style="{wave_style}">
        <h1>{analysis_icon} GRIP Analysis</h1>
        <p>Processing multi-pronged repurposing workflow</p>
    </div>
    """, unsafe_allow_html=True)
    
    asset_info, _, _, databases = load_sample_data()
    
    # Workflow steps with custom icons
    workflow_steps = [
        ("Input.png", "Data Ingestion", "Loading compound & omics data"),
        ("Data acquisition.png", "GRIP Scan", "Querying 40+ databases"),
        ("Network.png", "Association Mining", "Drug-disease pair identification"),
        ("Bar_chart.png", "Frequency Scoring", "Multi-source evidence aggregation"),
        ("metabolomic.png", "Omics Integration", "Client data overlay"),
        ("ranking.png", "Prioritisation", "Tiered ranking & validation")
    ]
    
    # Initialize progress
    if 'analysis_step' not in st.session_state:
        st.session_state.analysis_step = 0
    
    # Render workflow steps
    step_cols = st.columns(6)
    for i, (col, (icon, title, desc)) in enumerate(zip(step_cols, workflow_steps)):
        with col:
            if i < st.session_state.analysis_step:
                status = "complete"
            elif i == st.session_state.analysis_step:
                status = "active"
            else:
                status = "pending"
            st.markdown(render_workflow_step(icon, title, desc, status), unsafe_allow_html=True)
    
    # Progress bar
    progress = (st.session_state.analysis_step / len(workflow_steps)) * 100
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-bar" style="width: {progress}%;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Status area - show current step details
    if st.session_state.analysis_step < len(workflow_steps):
        current_step = workflow_steps[st.session_state.analysis_step]
        current_icon = get_image_html(current_step[0], "32px", "32px")
        
        st.markdown(f"""
        <div class="info-box">
            <h4>{current_icon} {current_step[1]}</h4>
            <p>{current_step[2]}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show relevant details based on step
        if st.session_state.analysis_step == 0:  # Data Ingestion
            st.markdown("**Loading client data:**")
            data_cols = st.columns(4)
            with data_cols[0]:
                st.metric("Compound", "EXC-7842")
            with data_cols[1]:
                st.metric("Target", "OX2R")
            with data_cols[2]:
                st.metric("Modality", "Small Molecule")
            with data_cols[3]:
                st.metric("Data Files", "4 files")
        
        elif st.session_state.analysis_step == 1:  # GRIP Scan
            st.markdown("**Databases being queried:**")
            db_cols = st.columns(3)
            for i, (category, dbs) in enumerate(databases.items()):
                with db_cols[i % 3]:
                    st.markdown(f"*{category}*")
                    for db in dbs[:5]:
                        st.markdown(f"- {db}")
                    if len(dbs) > 5:
                        st.markdown(f"- *...and {len(dbs) - 5} more*")
        
        elif st.session_state.analysis_step == 2:  # Association Mining
            st.markdown("**Drug-Disease Associations Found:**")
            assoc_cols = st.columns(3)
            with assoc_cols[0]:
                st.metric("Initial Pairs", "1,847")
            with assoc_cols[1]:
                st.metric("After Filtering", "312")
            with assoc_cols[2]:
                st.metric("Unique Indications", "89")
        
        elif st.session_state.analysis_step == 3:  # Frequency Scoring
            st.markdown("**Multi-source evidence aggregation:**")
            score_cols = st.columns(3)
            with score_cols[0]:
                st.metric("6-Source Matches", "1")
            with score_cols[1]:
                st.metric("5-Source Matches", "2")
            with score_cols[2]:
                st.metric("4-Source Matches", "4")
        
        elif st.session_state.analysis_step == 4:  # Omics Integration
            st.markdown("**Client Data Processing:**")
            omics_cols = st.columns(4)
            with omics_cols[0]:
                st.metric("Lipidomic Features", "1,247")
            with omics_cols[1]:
                st.metric("Metabolites", "892")
            with omics_cols[2]:
                st.metric("siRNA Hits", "156")
            with omics_cols[3]:
                st.metric("Clinical Samples", "48")
            
            st.markdown("**Omics-enhanced associations:** +47 additional drug-disease pairs identified")
        
        elif st.session_state.analysis_step == 5:  # Prioritisation
            st.markdown("**Final Tiered Ranking:**")
            tier_cols = st.columns(3)
            with tier_cols[0]:
                st.markdown(f"""
                <div style="background: {LIGHT_PINK}; padding: 1rem; border-radius: 8px; text-align: center;">
                    <p style="font-size: 2rem; font-weight: 700; color: {MAGENTA}; margin: 0;">3</p>
                    <p style="font-size: 0.8rem; color: {DEEP_BLUE}; margin: 0;">Tier I (High Confidence)</p>
                </div>
                """, unsafe_allow_html=True)
            with tier_cols[1]:
                st.markdown(f"""
                <div style="background: {VIOLET_LIGHT}; padding: 1rem; border-radius: 8px; text-align: center;">
                    <p style="font-size: 2rem; font-weight: 700; color: {VIOLET}; margin: 0;">4</p>
                    <p style="font-size: 0.8rem; color: {DEEP_BLUE}; margin: 0;">Tier II (Medium)</p>
                </div>
                """, unsafe_allow_html=True)
            with tier_cols[2]:
                st.markdown(f"""
                <div style="background: {LIGHT_BLUE}; padding: 1rem; border-radius: 8px; text-align: center;">
                    <p style="font-size: 2rem; font-weight: 700; color: {DEEP_BLUE}; margin: 0;">3</p>
                    <p style="font-size: 0.8rem; color: {DEEP_BLUE}; margin: 0;">Tier III (Emerging)</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.session_state.analysis_step > 0:
                if st.button("⬅️ Previous Step", use_container_width=True):
                    st.session_state.analysis_step -= 1
                    st.rerun()
        
        with col3:
            if st.session_state.analysis_step < len(workflow_steps) - 1:
                if st.button("Next Step ➡️", use_container_width=True, type="primary"):
                    st.session_state.analysis_step += 1
                    st.rerun()
            else:
                # Show repurpose icon above the button
                repurpose_icon = get_image_html("repurpose2.png", "32px", "32px")
                st.markdown(f'<div style="text-align: center; margin-bottom: 0.5rem;">{repurpose_icon}</div>', unsafe_allow_html=True)
                if st.button("View Results", use_container_width=True, type="primary"):
                    st.session_state.page = "results"
                    st.rerun()
    
    else:
        # Analysis complete - should not reach here normally
        st.success("✅ Analysis Complete - Click 'Results Dashboard' in the sidebar to view results.")


def page_results():
    """Results dashboard page"""
    ranking_header_icon = get_image_html("ranking.png", "48px", "48px")
    wave_b64 = load_image_as_base64("Wave.png")
    
    wave_style = ""
    if wave_b64:
        wave_style = f"--wave-bg: url('data:image/png;base64,{wave_b64}');"
    
    st.markdown(f"""
    <div class="page-header" style="{wave_style}">
        <h1>{ranking_header_icon} Repurposing Results Dashboard</h1>
        <p>Prioritised indication shortlist for EXC-7842 (Somnolexin)</p>
    </div>
    """, unsafe_allow_html=True)
    
    asset_info, indications, evidence_matrix, _ = load_sample_data()
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(render_metric_card("Total Indications", "10", "Across 3 tiers", "total.png"), unsafe_allow_html=True)
    with col2:
        st.markdown(render_metric_card("Tier I (High)", "3", "Strong multi-source evidence", "tier1.png"), unsafe_allow_html=True)
    with col3:
        st.markdown(render_metric_card("Tier II (Medium)", "4", "Moderate evidence", "tier2.png"), unsafe_allow_html=True)
    with col4:
        st.markdown(render_metric_card("Lead Indication", "Retinal Degeneration", "Score: 6/6 sources", "Novel.png"), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["Ranked Indications", "Evidence Heatmap", "Evidence Flow", "Indication Deep-Dive"])
    
    with tab1:
        ranking_icon = get_image_html("ranking.png", "32px", "32px")
        st.markdown(f'<p class="section-header">{ranking_icon} Tiered Indication Ranking</p>', unsafe_allow_html=True)
        
        # Filter options
        col1, col2 = st.columns([1, 3])
        with col1:
            tier_filter = st.selectbox("Filter by Tier", ["All Tiers", "Tier I", "Tier II", "Tier III"])
        
        # Filter data
        if tier_filter != "All Tiers":
            filtered_df = indications[indications["tier"] == tier_filter.split()[-1]]
        else:
            filtered_df = indications
        
        # Display table with styling
        for _, row in filtered_df.iterrows():
            tier_color = MAGENTA if row["tier"] == "I" else VIOLET if row["tier"] == "II" else DEEP_BLUE
            
            with st.container():
                cols = st.columns([0.5, 2, 1.5, 1, 1, 3])
                
                with cols[0]:
                    st.markdown(f"""
                    <div style="background: {tier_color}; color: white; padding: 0.5rem; 
                                border-radius: 8px; text-align: center; font-weight: 600;">
                        {row['score']}
                    </div>
                    """, unsafe_allow_html=True)
                
                with cols[1]:
                    st.markdown(f"**{row['indication']}**")
                    st.caption(row['mesh_category'])
                
                with cols[2]:
                    st.markdown(render_tier_badge(row['tier']), unsafe_allow_html=True)
                
                with cols[3]:
                    st.markdown(f"*{row['evidence_status']}*")
                
                with cols[4]:
                    confidence_color = MAGENTA if row['confidence'] == "High" else VIOLET if row['confidence'] == "Medium" else "#888"
                    st.markdown(f"<span style='color: {confidence_color}; font-weight: 500;'>{row['confidence']}</span>", 
                               unsafe_allow_html=True)
                
                with cols[5]:
                    st.caption(row['rationale'][:80] + "..." if len(row['rationale']) > 80 else row['rationale'])
                
                st.markdown("<hr style='margin: 0.5rem 0; border-color: #EEE;'>", unsafe_allow_html=True)
    
    with tab2:
        heatmap_icon = get_image_html("heatmap.png", "32px", "32px")
        st.markdown(f'<p class="section-header">{heatmap_icon} Multi-Source Evidence Matrix</p>', unsafe_allow_html=True)
        
        st.markdown("""
        Evidence presence across 6 data source categories. Coloured cells indicate positive evidence.
        """)
        
        fig = create_evidence_heatmap(evidence_matrix)
        st.plotly_chart(fig, use_container_width=True)
        
        # Legend with brand icons
        clinical_icon = get_image_html("Clinical.png", "20px", "20px")
        adverse_icon = get_image_html("adverse.png", "20px", "20px")
        literature_icon = get_image_html("books.png", "20px", "20px")
        pathways_icon = get_image_html("flow.png", "20px", "20px")
        omics_icon = get_image_html("metabolomic.png", "20px", "20px")
        interactome_icon = get_image_html("Network.png", "20px", "20px")
        
        st.markdown(f"""
        <div style="display: flex; gap: 2rem; justify-content: center; margin-top: 1rem; flex-wrap: wrap; align-items: center;">
            <span><strong>Data Sources:</strong></span>
            <span style="display: inline-flex; align-items: center; gap: 0.3rem;">{clinical_icon} Clinical Trials</span>
            <span style="display: inline-flex; align-items: center; gap: 0.3rem;">{adverse_icon} Adverse Events</span>
            <span style="display: inline-flex; align-items: center; gap: 0.3rem;">{literature_icon} Literature</span>
            <span style="display: inline-flex; align-items: center; gap: 0.3rem;">{pathways_icon} Pathways</span>
            <span style="display: inline-flex; align-items: center; gap: 0.3rem;">{omics_icon} Omics</span>
            <span style="display: inline-flex; align-items: center; gap: 0.3rem;">{interactome_icon} Interactome</span>
        </div>
        """, unsafe_allow_html=True)
    
    with tab3:
        flow_icon = get_image_html("flow.png", "32px", "32px")
        st.markdown(f'<p class="section-header">{flow_icon} Evidence Flow Diagram</p>', unsafe_allow_html=True)
        
        st.markdown("""
        Sankey diagram showing how evidence from different sources supports each candidate indication.
        """)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            fig = create_sankey_diagram(indications)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            pie_icon = get_image_html("Pie_chart.png", "32px", "32px")
            st.markdown(f'<p class="section-header">{pie_icon} Tier Distribution</p>', unsafe_allow_html=True)
            fig2 = create_tier_distribution_chart(indications)
            st.plotly_chart(fig2, use_container_width=True)
    
    with tab4:
        deep_dive_icon = get_image_html("deep_dive.png", "32px", "32px")
        st.markdown(f'<p class="section-header">{deep_dive_icon} Indication Deep-Dive</p>', unsafe_allow_html=True)
        
        selected_indication = st.selectbox(
            "Select indication for detailed view",
            indications["indication"].tolist()
        )
        
        ind_data = indications[indications["indication"] == selected_indication].iloc[0]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #F8F9FA 0%, {WHITE} 100%); 
                        padding: 1.5rem; border-radius: 12px; border: 1px solid #E8E8E8;">
                <h3 style="color: {DEEP_BLUE}; margin: 0 0 1rem 0;">{selected_indication}</h3>
                <p><strong>MeSH Category:</strong> {ind_data['mesh_category']}</p>
                <p><strong>Evidence Status:</strong> {ind_data['evidence_status']}</p>
                <p><strong>Confidence:</strong> {ind_data['confidence']}</p>
                <hr style="border-color: #EEE;">
                <h4 style="color: {VIOLET};">Scientific Rationale</h4>
                <p>{ind_data['rationale']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(render_tier_badge(ind_data['tier']), unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background: {DEEP_BLUE}; color: white; padding: 1.5rem; 
                        border-radius: 12px; text-align: center; margin-top: 1rem;">
                <p style="font-size: 3rem; font-weight: 700; margin: 0; color: {MAGENTA};">{ind_data['score']}/6</p>
                <p style="margin: 0.5rem 0 0 0;">Evidence Sources</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Evidence breakdown
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Evidence Breakdown:**")
        
        evidence_items = [
            ("Clinical Trials", ind_data['clinical_trials'], "Clinical.png"),
            ("Adverse Events", ind_data['adverse_events'], "adverse.png"),
            ("Literature", ind_data['literature'], "books.png"),
            ("Pathways", ind_data['pathways'], "flow.png"),
            ("Omics", ind_data['omics'], "metabolomic.png"),
            ("Interactome", ind_data['interactome'], "Network.png")
        ]
        
        ev_cols = st.columns(6)
        for i, (name, present, icon) in enumerate(evidence_items):
            with ev_cols[i]:
                bg_color = LIGHT_PINK if present else "#F8F8F8"
                border_color = MAGENTA if present else "#EEE"
                text_color = MAGENTA if present else "#CCC"
                icon_html = get_image_html(icon, "32px", "32px")
                st.markdown(f"""
                <div style="text-align: center; padding: 1rem; background: {bg_color}; 
                            border-radius: 8px; border: 1px solid {border_color};">
                    {icon_html}
                    <p style="font-size: 0.7rem; color: {DEEP_BLUE if present else '#999'}; margin: 0.5rem 0 0 0; font-weight: 500;">
                        {name}
                    </p>
                    <p style="font-size: 1.2rem; color: {text_color}; margin: 0;">
                        {'✓' if present else '—'}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        # Recommended next steps
        st.markdown("<br>", unsafe_allow_html=True)
        start_icon = get_image_html("Start.png", "28px", "28px")
        st.markdown(f"""
        <div class="info-box">
            <h4>{start_icon} Recommended Next Steps</h4>
            <p>
            1. <strong>Validate hypothesis</strong> with targeted literature review<br>
            2. <strong>Design PoC study</strong> using recommended disease models<br>
            3. <strong>Assess IP landscape</strong> for freedom-to-operate<br>
            4. <strong>Evaluate regulatory pathway</strong> and development timeline
            </p>
        </div>
        """, unsafe_allow_html=True)


# =============================================================================
# SIDEBAR NAVIGATION
# =============================================================================

def render_sidebar():
    """Render sidebar navigation with brand assets"""
    with st.sidebar:
        # Logo in white container for visibility
        logo_b64 = load_image_as_base64("Logo.png")
        
        if logo_b64:
            st.markdown(f"""
            <div class="logo-container">
                <img src="data:image/png;base64,{logo_b64}" style="width: 160px;">
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <p style="color: {VIOLET}; font-size: 0.7rem; text-transform: uppercase; 
                  letter-spacing: 1px; margin-bottom: 0.75rem; font-weight: 600;">Navigation</p>
        """, unsafe_allow_html=True)
        
        # Navigation buttons
        pages = [
            ("Home.png", "Overview", "overview"),
            ("Input.png", "Asset Configuration", "asset"),
            ("Analysis.png", "Run Analysis", "analysis"),
            ("ranking.png", "Results Dashboard", "results")
        ]
        
        for icon_name, label, page_key in pages:
            if st.button(f"{label}", key=f"nav_{page_key}", use_container_width=True):
                if page_key == "analysis":
                    st.session_state.analysis_step = 0
                st.session_state.page = page_key
                st.rerun()
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Demo info box - updated for light theme
        st.markdown(f"""
        <div style="background: {SOFT_LAVENDER}; padding: 1rem; border-radius: 8px; 
                    border: 1px solid {VIOLET};">
            <p style="font-size: 0.75rem; color: {VIOLET}; margin: 0 0 0.5rem 0; font-weight: 600;">
                DEMO CASE
            </p>
            <p style="font-size: 0.7rem; color: {DEEP_BLUE}; margin: 0; line-height: 1.4;">
                Shelved Phase II Asset<br>
                <span style="color: {MAGENTA};">Sleep Disorders → Multi-OMICS Repurposing</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>" * 3, unsafe_allow_html=True)
        
        # Footer
        st.markdown(f"""
        <p style="font-size: 0.65rem; color: #888; text-align: center;">
            Sales Demo Tool<br>
            © 2024 Excelra
        </p>
        """, unsafe_allow_html=True)


# =============================================================================
# MAIN APP
# =============================================================================

def main():
    """Main application entry point"""
    
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = "overview"
    
    if 'analysis_step' not in st.session_state:
        st.session_state.analysis_step = 0
    
    # Render sidebar
    render_sidebar()
    
    # Route to appropriate page
    if st.session_state.page == "overview":
        page_overview()
    elif st.session_state.page == "asset":
        page_asset_input()
    elif st.session_state.page == "analysis":
        page_analysis()
    elif st.session_state.page == "results":
        page_results()


if __name__ == "__main__":
    main()
