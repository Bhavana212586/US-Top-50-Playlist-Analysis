
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="US Top 50 | Music Analytics",
    page_icon="🎧",
    layout="wide"
)

# PURPLE + LAVENDER THEME
st.markdown("""
<style>
.stApp {background:#171020;color:#FFFFFF}
[data-testid="stSidebar"] {background:#241536}
.stApp p,.stApp label,.stApp h1,.stApp h2,
.stApp h3,.stApp span {color:#F8F4FF}
[data-testid="stSidebar"] * {color:#FFFFFF}
.kpi {
    background:#35204C;
    border:1px solid #9470BC;
    border-radius:12px;
    padding:18px;
    text-align:center;
}
.kpi h2 {color:#D0B4F5 !important}
.kpi p {color:#FFFFFF !important}
[data-baseweb="select"] > div {
    background:#493064;color:white;
}
[data-baseweb="select"] * {color:white !important}
.stTextInput input,.stDateInput input {
    background:#493064;color:white;
}
.stButton button,.stDownloadButton button {
    background:#B58AE8;color:#241536;
    border:0;font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

PURPLE = "#B58AE8"
COLORS = ["#B58AE8","#895BC1","#D0B4F5","#65418A"]

def chart_style(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#171020",
        plot_bgcolor="#241536",
        font_color="#FFFFFF",
        colorway=COLORS,
        height=400
    )
    return fig

# LOAD DATA
file = Path("Atlantic_United_States.csv")

if not file.exists():
    st.error("Dataset not found. Check the CSV filename.")
    st.stop()

df = pd.read_csv(file)
df.columns = df.columns.str.strip().str.lower()

required = ["date","position","song","artist"]
if any(c not in df.columns for c in required):
    st.error("Required columns missing: date, position, song, artist")
    st.stop()

df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["position"] = pd.to_numeric(df["position"], errors="coerce")
df = df.dropna(subset=["date","position"]).copy()

for c in ["popularity","duration_ms","is_explicit","album_type"]:
    if c not in df.columns:
        df[c] = None

df["popularity"] = pd.to_numeric(df["popularity"],errors="coerce")
df["duration_minutes"] = pd.to_numeric(
    df["duration_ms"],errors="coerce"
) / 60000

if df.empty:
    st.error("No valid data found.")
    st.stop()

# SIDEBAR FILTERS
st.sidebar.title("🎧 Music Filters")

dates = st.sidebar.date_input(
    "Date range",
    value=(df.date.min().date(),df.date.max().date())
)

artists = st.sidebar.multiselect(
    "Select Artists",sorted(df.artist.dropna().unique())
)

search = st.sidebar.text_input("Search Song")

position = st.sidebar.slider(
    "Chart Position",1,50,(1,50)
)

data = df.copy()

if isinstance(dates,(tuple,list)) and len(dates)==2:
    data = data[
        data.date.dt.date.between(dates[0],dates[1])
    ]

data = data[data.position.between(*position)]

if artists:
    data = data[data.artist.isin(artists)]

if search:
    data = data[
        data.song.str.contains(search,case=False,na=False)
    ]

if data.empty:
    st.warning("No matching records. Change your filters.")
    st.stop()

# HEADER
st.title("🎧 US TOP 50")
st.subheader("Music Analytics Dashboard")
st.caption("Explore music trends, artists and chart performance.")

# KPI CARDS
a,b,c,d = st.columns(4)

metrics = [
    ("Total Records",len(data)),
    ("Unique Songs",data.song.nunique()),
    ("Total Artists",data.artist.nunique()),
    ("Avg Popularity",round(data.popularity.mean(),1)
     if data.popularity.notna().any() else "N/A")
]

for col,(label,value) in zip([a,b,c,d],metrics):
    col.markdown(
        f'<div class="kpi"><p>{label}</p><h2>{value}</h2></div>',
        unsafe_allow_html=True
    )

# RANKING TREND
st.header("📈 Chart Ranking Trends")
trend = data.groupby("date",as_index=False).position.mean()
fig = px.line(trend,x="date",y="position",markers=True)
fig.update_yaxes(autorange="reversed")
st.plotly_chart(chart_style(fig),use_container_width=True)

# TOP ARTISTS
st.header("🎤 Top 10 Artists")
top = data.artist.value_counts().head(10).reset_index()
top.columns = ["Artist","Appearances"]
fig = px.bar(top,x="Artist",y="Appearances",text="Appearances")
st.plotly_chart(chart_style(fig),use_container_width=True)

# POPULARITY VS RANK
st.header("⭐ Popularity vs Rank")
pop = data.dropna(subset=["popularity"])
if not pop.empty:
    fig = px.scatter(
        pop,x="position",y="popularity",
        color="artist",hover_data=["song"]
    )
    fig.update_xaxes(autorange="reversed")
    st.plotly_chart(chart_style(fig),use_container_width=True)
else:
    st.info("Popularity data unavailable.")

# EXPLICIT CONTENT
st.header("🔞 Explicit Content Analysis")
if data.is_explicit.notna().any():
    explicit = data.is_explicit.astype(str).str.lower().map({
        "true":"Explicit","1":"Explicit","yes":"Explicit",
        "false":"Non-Explicit","0":"Non-Explicit","no":"Non-Explicit"
    }).fillna("Unknown")
    fig = px.pie(
        names=explicit.value_counts().index,
        values=explicit.value_counts().values,
        hole=0.5,color_discrete_sequence=COLORS
    )
    st.plotly_chart(chart_style(fig),use_container_width=True)
else:
    st.info("Explicit content data unavailable.")

# ALBUM TYPE
st.header("💿 Album Type Analysis")
album = data.dropna(subset=["album_type"])
if not album.empty:
    fig = px.bar(
        album.album_type.value_counts().reset_index(),
        x="album_type",y="count"
    )
    st.plotly_chart(chart_style(fig),use_container_width=True)
else:
    st.info("Album type data unavailable.")

# SONG DURATION
st.header("⏱️ Song Duration Analysis")
duration = data.dropna(subset=["duration_minutes"])
if not duration.empty:
    fig = px.histogram(duration,x="duration_minutes",nbins=20)
    st.plotly_chart(chart_style(fig),use_container_width=True)
else:
    st.info("Duration data unavailable.")

# SONG DATA
st.header("📋 Music Dataset")
st.dataframe(data,use_container_width=True,hide_index=True)

st.download_button(
    "⬇️ Download CSV",
    data=data.to_csv(index=False).encode("utf-8"),
    file_name="US_Top_50.csv",
    mime="text/csv"
)

st.markdown("---")
st.markdown(
    "<center>🎧 US Top 50 | Music Analytics Dashboard</center>",
    unsafe_allow_html=True
)
