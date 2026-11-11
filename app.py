import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(page_title="US Top 50 | Music Analytics", page_icon="🎧", layout="wide")

# --------------------------------------------------
# PURPLE + LAVENDER THEME
# --------------------------------------------------
st.markdown("""
<style>
.stApp { background: #171020 !important; color: #FFFFFF !important; }
[data-testid="stHeader"] { background: #171020 !important; }
[data-testid="stSidebar"] { background: #241536 !important; }
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p,
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #FFFFFF !important; }
[data-testid="stSidebar"] [data-testid="stDateInput"] input {
 background: #FFFFFF !important; color: #321744 !important;
 -webkit-text-fill-color: #321744 !important; opacity: 1 !important; font-weight: 600 !important;
}
[data-testid="stSidebar"] [data-testid="stDateInput"] button { background: #FFFFFF !important; color: #321744 !important; }
[data-testid="stSidebar"] [data-testid="stDateInput"] button svg { color: #321744 !important; fill: #321744 !important; }
[data-testid="stSidebar"] [data-baseweb="select"] > div { background: #FFFFFF !important; border-color: #B58AE8 !important; }
[data-testid="stSidebar"] [data-baseweb="select"] *, [data-testid="stSidebar"] [data-baseweb="select"] svg { color: #321744 !important; fill: #321744 !important; }
[data-baseweb="popover"], [data-baseweb="popover"] [role="listbox"] { background: #35204C !important; }
[data-baseweb="popover"] [role="option"], [data-baseweb="popover"] [role="option"] * { background: #35204C !important; color: #FFFFFF !important; }
[data-baseweb="popover"] [role="option"]:hover, [data-baseweb="popover"] [role="option"]:hover * { background: #65418A !important; color: #FFFFFF !important; }
.kpi { background: linear-gradient(135deg,#35204C,#493064); border: 1px solid #9470BC; border-radius: 12px; padding: 17px; text-align: center; min-height: 105px; }
.kpi p { color: #FFFFFF !important; margin-bottom: 5px; }
.kpi h2 { color: #D0B4F5 !important; margin: 0; }
.stButton button, .stDownloadButton button { background: #B58AE8 !important; color: #241536 !important; border: 0 !important; border-radius: 8px !important; font-weight: bold !important; }
[data-testid="stDataFrame"] { border: 1px solid #9470BC; border-radius: 10px; }
.js-plotly-plot .plotly text { fill: #FFFFFF !important; }
hr { border-color: #76529B !important; }
/* KEY INSIGHTS: force readable contrast on Streamlit metric text */
.insight-card {
    background: linear-gradient(135deg, #35204C, #493064);
    border: 1px solid #9470BC;
    border-radius: 14px;
    padding: 18px 18px 16px 18px;
    min-height: 158px;
    height: 100%;
}
.insight-label {
    color: #E2C8FF !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    line-height: 1.4 !important;
    margin: 0 0 12px 0 !important;
}
.insight-value {
    color: #FFFFFF !important;
    font-size: clamp(1.15rem, 2vw, 1.75rem) !important;
    font-weight: 700 !important;
    line-height: 1.25 !important;
    overflow-wrap: anywhere;
    margin: 0 0 12px 0 !important;
}
.insight-note {
    display: inline-block;
    color: #FFFFFF !important;
    background: #65418A !important;
    border: 1px solid #B58AE8;
    border-radius: 20px;
    padding: 4px 10px;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    line-height: 1.3 !important;
}

</style>
""", unsafe_allow_html=True)

COLORS = ["#B58AE8", "#895BC1", "#D0B4F5", "#65418A", "#E2C8FF"]


def chart_style(fig, height=420):
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="#171020", plot_bgcolor="#241536",
        font=dict(color="#FFFFFF"), colorway=COLORS, height=height,
        margin=dict(l=35, r=25, t=65, b=45), legend_title_text=""
    )
    fig.update_xaxes(showgrid=False, automargin=True)
    fig.update_yaxes(gridcolor="#493064", automargin=True)
    return fig


# --------------------------------------------------
# LOAD AND VALIDATE DATA
# --------------------------------------------------
@st.cache_data
