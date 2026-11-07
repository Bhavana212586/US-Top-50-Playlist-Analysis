
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="US Top 50 | Music Analytics",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# SPOTIFY DARK THEME
# ==========================================

st.markdown("""
<style>
.stApp {
    background-color: #101411 !important;
    color: #FFFFFF !important;
}

[data-testid="stHeader"] {
    background-color: #101411 !important;
}

[data-testid="stSidebar"] {
    background-color: #151B18 !important;
}

[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

.stApp h1, .stApp h2, .stApp h3,
.stApp p, .stApp label, .stApp span {
    color: #F5F7F5;
}

.hero {
    background: linear-gradient(115deg, #1B3527, #10251B);
    padding: 30px;
    border-radius: 16px;
    border: 1px solid #2B6844;
    margin-bottom: 25px;
}

.hero h1 {
    color: #FFFFFF !important;
    font-size: 34px;
    margin-bottom: 8px;
}

.hero p {
    color: #B8CBBF !important;
    font-size: 15px;
}

.kpi-card {
    background: #1B241F;
    border: 1px solid #2B3B30;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    min-height: 115px;
}

.kpi-card h4 {
    color: #A9B9AE !important;
    font-size: 14px;
    margin: 0;
}

.kpi-card h2 {
    color: #1DB954 !important;
    font-size: 29px;
    margin: 12px 0 0 0;
}

.section-title {
    color: #1DB954 !important;
    font-size: 22px;
    font-weight: 700;
    margin-top: 25px;
    margin-bottom: 15px;
}

div[data-testid="stMetric"] {
    background: #1B241F;
    border: 1px solid #2B3B30;
    padding: 15px;
    border-radius: 12px;
}

div[data-testid="stMetricLabel"] {
    color: #A9B9AE !important;
}

div[data-testid="stMetricValue"] {
    color: #1DB954 !important;
}

.stButton button {
    background-color: #1DB954;
    color: #07130B;
    border-radius: 8px;
    border: none;
    font-weight: bold;
}

.stDownloadButton button {
    background-color: #1DB954;
    color: #07130B;
    border: none;
    font-weight: bold;
}

.stDownloadButton button:hover,
.stButton button:hover {
    background-color: #1ED760;
    color: #07130B;
}

input, textarea {
    background-color: #26332B !important;
    color: white !important;
}

[data-baseweb="select"] > div {
    background-color: #26332B !important;
    color: white !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid #2B3B30;
    border-radius: 10px;
}

hr {
    border-color: #34443A;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# COLOR SETTINGS
# ==========================================

GREEN = "#1DB954"
DARK = "#101411"
GRID = "#29362E"

def style_chart(fig, height=400):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#F5F7F5", size=12),
        height=height,
        margin=dict(l=20, r=20, t=50, b=30),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        ),
        xaxis=dict(
            gridcolor=GRID,
            zerolinecolor=GRID
        ),
        yaxis=dict(
            gridcolor=GRID,
            zerolinecolor=GRID
        )
    )
    return fig


# ==========================================
# LOAD DATASET
# ==========================================

@st.cache_data
def load_data():
    possible_paths = [
        Path("Atlantic_United_States.csv"),
        Path("data/Atlantic_United_States.csv")
    ]

    for path in possible_paths:
        if path.exists():
            df = pd.read_csv(path)
            return df

    return None


df = load_data()

if df is None:
    st.error(
        "Dataset not found! Please upload "
        "Atlantic_United_States.csv to your project repository."
    )
    st.stop()


# ==========================================
# DATA CLEANING
# ==========================================

df.columns = df.columns.str.strip().str.lower()

required_columns = ["date", "position", "song", "artist"]

missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    st.error(f"Missing required columns: {missing_columns}")
    st.stop()

df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["position"] = pd.to_numeric(df["position"], errors="coerce")

df["song"] = df["song"].fillna("Unknown Song").astype(str)
df["artist"] = df["artist"].fillna("Unknown Artist").astype(str)

df = df.dropna(subset=["date", "position"]).copy()

optional_columns = [
    "popularity",
    "duration_ms",
    "is_explicit",
    "album_type"
]

for col in optional_columns:
    if col not in df.columns:
        df[col] = None

df["popularity"] = pd.to_numeric(
    df["popularity"], errors="coerce"
)

df["duration_ms"] = pd.to_numeric(
    df["duration_ms"], errors="coerce"
)

df["duration_minutes"] = df["duration_ms"] / 60000

if df.empty:
    st.error("No valid records found in the dataset.")
    st.stop()


# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.markdown("""
# 🎧 Music Analytics

**US TOP 50 • INTERACTIVE DASHBOARD**

---
""")

st.sidebar.markdown("### 🎛️ Filter your data")

min_date = df["date"].min().date()
max_date = df["date"].max().date()

date_range = st.sidebar.date_input(
    "📅 Chart date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, (tuple, list)):
    if len(date_range) == 2:
        start_date, end_date = date_range
    elif len(date_range) == 1:
        start_date = end_date = date_range[0]
    else:
        start_date, end_date = min_date, max_date
else:
    start_date = end_date = date_range

artists = sorted(df["artist"].unique().tolist())

selected_artists = st.sidebar.multiselect(
    "🎤 Select artists",
    artists,
    placeholder="Choose artists"
)

song_search = st.sidebar.text_input(
    "🎵 Search song",
    placeholder="Enter song name..."
)

position_range = st.sidebar.slider(
    "🏆 Chart position",
    min_value=1,
    max_value=50,
    value=(1, 50)
)

if df["popularity"].notna().any():
    min_pop = int(df["popularity"].min())
    max_pop = int(df["popularity"].max())

    popularity_range = st.sidebar.slider(
        "⭐ Popularity score",
        min_value=min_pop,
        max_value=max_pop,
        value=(min_pop, max_pop)
    )
else:
    popularity_range = None

st.sidebar.markdown("---")
st.sidebar.caption("🎧 US Top 50 Music Analytics")


# ==========================================
# APPLY FILTERS
# ==========================================

filtered_df = df[
    (df["date"].dt.date >= start_date) &
    (df["date"].dt.date <= end_date) &
    (df["position"].between(
        position_range[0], position_range[1]
    ))
].copy()

if selected_artists:
    filtered_df = filtered_df[
        filtered_df["artist"].isin(selected_artists)
    ]

if song_search:
    filtered_df = filtered_df[
        filtered_df["song"].str.contains(
            song_search,
            case=False,
            na=False
        )
    ]

if popularity_range is not None:
    filtered_df = filtered_df[
        filtered_df["popularity"].between(
            popularity_range[0],
            popularity_range[1]
        )
    ]

if filtered_df.empty:
    st.warning("No records match your selected filters.")
    st.info("Try changing your filters.")
    st.stop()


# ==========================================
# HERO SECTION
# ==========================================

st.markdown("""
<div class="hero">
    <h1>🎧 US TOP 50 | MUSIC ANALYTICS</h1>
    <p>
        Explore music trends, artist performance,
        popularity scores and chart rankings.
        Discover insights from the United States Top 50 playlist.
    </p>
</div>
""", unsafe_allow_html=True)


# ==========================================
# KPI METRICS
# ==========================================

total_records = len(filtered_df)
unique_songs = filtered_df["song"].nunique()
unique_artists = filtered_df["artist"].nunique()

avg_popularity = filtered_df["popularity"].mean()

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <h4>📊 Total Records</h4>
        <h2>{total_records:,}</h2>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <h4>🎵 Unique Songs</h4>
        <h2>{unique_songs:,}</h2>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <h4>🎤 Total Artists</h4>
        <h2>{unique_artists:,}</h2>
    </div>
    """, unsafe_allow_html=True)

with k4:
    popularity_text = (
        f"{avg_popularity:.1f}"
        if pd.notna(avg_popularity)
        else "N/A"
    )

    st.markdown(f"""
    <div class="kpi-card">
        <h4>⭐ Average Popularity</h4>
        <h2>{popularity_text}</h2>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# CHART 1: RANKING TRENDS
# ==========================================

st.markdown(
    '<div class="section-title">📈 Chart Ranking Trends</div>',
    unsafe_allow_html=True
)

daily_ranking = (
    filtered_df.groupby("date", as_index=False)
    .agg({"position": "mean"})
)

fig1 = px.line(
    daily_ranking,
    x="date",
    y="position",
    markers=True,
    title="Average Chart Position Over Time"
)

fig1.update_traces(
    line=dict(color=GREEN, width=3),
    marker=dict(size=7)
)

fig1.update_yaxes(autorange="reversed")

style_chart(fig1, 400)

st.plotly_chart(fig1, use_container_width=True)


# ==========================================
# CHART 2: TOP ARTISTS
# ==========================================

st.markdown(
    '<div class="section-title">🎤 Top 10 Artists</div>',
    unsafe_allow_html=True
)

top_artists = (
    filtered_df.groupby("artist")
    .size()
    .reset_index(name="appearances")
    .sort_values("appearances", ascending=False)
    .head(10)
)

fig2 = px.bar(
    top_artists.sort_values("appearances"),
    x="appearances",
    y="artist",
    orientation="h",
    title="Top 10 Artists by Chart Appearances"
)

fig2.update_traces(
    marker_color=GREEN,
    text="appearances",
    textposition="outside"
)

style_chart(fig2, 430)

st.plotly_chart(fig2, use_container_width=True)


# ==========================================
# CHART 3: POPULARITY VS RANK
# ==========================================

st.markdown(
    '<div class="section-title">⭐ Popularity vs Chart Rank</div>',
    unsafe_allow_html=True
)

popularity_data = filtered_df.dropna(
    subset=["popularity"]
)

if not popularity_data.empty:

    fig3 = px.scatter(
        popularity_data,
        x="position",
        y="popularity",
        color="artist",
        hover_data=["song"],
        title="Song Popularity Compared with Chart Position",
        opacity=0.75
    )

    fig3.update_xaxes(autorange="reversed")

    style_chart(fig3, 450)

    st.plotly_chart(fig3, use_container_width=True)

else:
    st.info("Popularity information is not available.")


# ==========================================
# CHART 4: EXPLICIT CONTENT
# ==========================================

st.markdown(
    '<div class="section-title">🔞 Explicit Content Analysis</div>',
    unsafe_allow_html=True
)

def convert_explicit(value):
    if pd.isna(value):
        return "Unknown"

    if isinstance(value, str):
        value = value.strip().lower()

        if value in ["true", "yes", "1"]:
            return "Explicit"

        if value in ["false", "no", "0"]:
            return "Non-Explicit"

        return "Unknown"

    if value == 1 or value is True:
        return "Explicit"

    if value == 0 or value is False:
        return "Non-Explicit"

    return "Unknown"


explicit_df = filtered_df.copy()

explicit_df["explicit_status"] = (
    explicit_df["is_explicit"].apply(convert_explicit)
)

explicit_counts = (
    explicit_df["explicit_status"]
    .value_counts()
    .reset_index()
)

explicit_counts.columns = ["Content Type", "Count"]

fig4 = px.pie(
    explicit_counts,
    names="Content Type",
    values="Count",
    hole=0.55,
    title="Explicit vs Non-Explicit Songs"
)

fig4.update_traces(
    textposition="inside",
    textinfo="percent+label"
)

style_chart(fig4, 400)

st.plotly_chart(fig4, use_container_width=True)


# ==========================================
# CHART 5: ALBUM TYPE
# ==========================================

st.markdown(
    '<div class="section-title">💿 Album Type Analysis</div>',
    unsafe_allow_html=True
)

album_data = filtered_df.dropna(
    subset=["album_type"]
).copy()

if not album_data.empty:

    album_counts = (
        album_data["album_type"]
        .value_counts()
        .reset_index()
    )

    album_counts.columns = ["Album Type", "Count"]

    fig5 = px.bar(
        album_counts,
        x="Album Type",
        y="Count",
        title="Songs by Album Type",
        text="Count"
    )

    fig5.update_traces(
        marker_color=GREEN,
        textposition="outside"
    )

    style_chart(fig5, 400)

    st.plotly_chart(fig5, use_container_width=True)

else:
    st.info("Album type information is not available.")


# ==========================================
# CHART 6: SONG DURATION
# ==========================================

st.markdown(
    '<div class="section-title">⏱️ Song Duration Analysis</div>',
    unsafe_allow_html=True
)

duration_data = filtered_df.dropna(
    subset=["duration_minutes"]
)

if not duration_data.empty:

    fig6 = px.histogram(
        duration_data,
        x="duration_minutes",
        nbins=25,
        title="Distribution of Song Durations",
        labels={
            "duration_minutes": "Duration (minutes)"
        }
    )

    fig6.update_traces(
        marker_color=GREEN,
        opacity=0.85
    )

    style_chart(fig6, 400)

    st.plotly_chart(fig6, use_container_width=True)

else:
    st.info("Song duration information is not available.")


# ==========================================
# CHART 7: NEW ENTRIES AND EXITS
# ==========================================

st.markdown(
    '<div class="section-title">🆕 New Entries and Exits</div>',
    unsafe_allow_html=True
)

daily_songs = (
    df.groupby("date")["song"]
    .apply(set)
    .sort_index()
)

dates = list(daily_songs.index)

entry_records = []
exit_records = []

for i in range(1, len(dates)):

    previous_songs = daily_songs.iloc[i - 1]
    current_songs = daily_songs.iloc[i]

    new_songs = current_songs - previous_songs
    exited_songs = previous_songs - current_songs

    entry_records.append({
        "date": dates[i],
        "New Entries": len(new_songs),
        "Exited Songs": len(exited_songs)
    })

if entry_records:

    movement_df = pd.DataFrame(entry_records)

    movement_df = movement_df[
        (movement_df["date"].dt.date >= start_date) &
        (movement_df["date"].dt.date <= end_date)
    ]

    if not movement_df.empty:

        fig7 = go.Figure()

        fig7.add_trace(go.Bar(
            x=movement_df["date"],
            y=movement_df["New Entries"],
            name="New Entries",
            marker_color=GREEN
        ))

        fig7.add_trace(go.Bar(
            x=movement_df["date"],
            y=movement_df["Exited Songs"],
            name="Exited Songs",
            marker_color="#E85D75"
        ))

        fig7.update_layout(
            barmode="group",
            title="Daily Song Entries and Exits"
        )

        style_chart(fig7, 400)

        st.plotly_chart(fig7, use_container_width=True)

    else:
        st.info("No song movement data for this date range.")

else:
    st.info("More than one chart date is required to analyze entries and exits.")


# ==========================================
# FILTERED DATA TABLE
# ==========================================

st.markdown(
    '<div class="section-title">📋 Detailed Music Data</div>',
    unsafe_allow_html=True
)

display_columns = [
    "date",
    "position",
    "song",
    "artist",
    "popularity",
    "duration_ms",
    "is_explicit",
    "album_type"
]

display_columns = [
    col for col in display_columns
    if col in filtered_df.columns
]

display_df = filtered_df[display_columns].copy()

display_df = display_df.sort_values(
    ["date", "position"],
    ascending=[False, True]
)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# CSV DOWNLOAD
# ==========================================

csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered Dataset",
    data=csv_data,
    file_name="US_Top_50_Filtered_Data.csv",
    mime="text/csv",
    use_container_width=True
)


# ==========================================
# FOOTER
# ==========================================

st.markdown("---")

st.markdown("""
<div style="text-align:center; padding:15px;">
    <h4 style="color:#1DB954;">
        🎧 US TOP 50 | MUSIC ANALYTICS
    </h4>
    <p style="color:#A9B9AE;">
        Interactive Music Data Analysis Dashboard
    </p>
    <p style="color:#728078; font-size:12px;">
        Built with Python • Streamlit • Pandas • Plotly
    </p>
</div>
""", unsafe_allow_html=True)
