import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="US Top 50 | Music Analytics",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# PROFESSIONAL DARK THEME
# ---------------------------------------------------------
st.markdown("""

/* ===== DARK THEME FIX ===== */

.stApp,
[data-testid="stAppViewContainer"] {
    background: #101411 !important;
    color: #FFFFFF !important;
}

[data-testid="stHeader"] {
    background: #101411 !important;
}

[data-testid="stSidebar"] {
    background: #151B18 !important;
}

[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

/* Main page text */
.stApp h1,
.stApp h2,
.stApp h3,
.stApp p,
.stApp label,
.stApp span {
    color: #F5F7F5;
}

/* Hero section */
.hero {
    background: linear-gradient(115deg, #1B3527, #10251B) !important;
    border: 1px solid #2B6844;
}

/* KPI cards */
.kpi-card {
    background: #1B241F !important;
    border: 1px solid #2B3B30;
}

/* Input fields */
.stApp input,
.stApp textarea,
[data-baseweb="select"] > div {
    background-color: #26332B !important;
    color: #FFFFFF !important;
}

/* Dropdown selected values */
[data-baseweb="tag"] {
    background-color: #1DB954 !important;
    color: #07130B !important;
}

[data-baseweb="tag"] * {
    color: #07130B !important;
}

/* Slider */
[data-testid="stSlider"] {
    color: #1DB954 !important;
}

/* Data tables */
[data-testid="stDataFrame"] {
    background: #1B241F !important;
    color: #FFFFFF !important;
}

/* Placeholder */
input::placeholder {
    color: #BFCBC2 !important;
    opacity: 1 !important;
}

""", unsafe_allow_html=True)

GREEN = "#1DB954"
MINT = "#8FE3A8"
PLOT_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#DCE6DE"),
    margin=dict(l=20, r=20, t=55, b=20),
    legend=dict(bgcolor="rgba(0,0,0,0)")
)

# ---------------------------------------------------------
# LOAD AND PREPARE DATA
# ---------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Atlantic_United_States.csv")

    required = ["date", "position", "song", "artist"]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError("Missing required dataset columns: " + ", ".join(missing))

    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    for col in ["position", "popularity", "duration_ms"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["song"] = df["song"].fillna("Unknown").astype(str)
    df["artist"] = df["artist"].fillna("Unknown").astype(str)
    df = df.drop_duplicates().dropna(subset=["date", "position"])
    df = df[df["position"].between(1, 50)].copy()

    if "popularity" not in df.columns:
        df["popularity"] = pd.NA
    if "duration_ms" not in df.columns:
        df["duration_ms"] = pd.NA
    if "duration_minutes" not in df.columns:
        df["duration_minutes"] = df["duration_ms"] / 60000

    return df


try:
    df = load_data()
except FileNotFoundError:
    st.error("The dataset file 'Atlantic_United_States.csv' was not found. Keep it in the same folder as app.py.")
    st.stop()
except Exception as error:
    st.error(f"Unable to load the dataset: {error}")
    st.stop()

if df.empty:
    st.error("The dataset does not contain any valid chart records.")
    st.stop()


# ---------------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------------
st.sidebar.markdown("## 🎧 Music Analytics")
st.sidebar.caption("US TOP 50 • INTERACTIVE DASHBOARD")
st.sidebar.markdown("---")
st.sidebar.markdown("### Filter your data")

# Date filter
min_date = df["date"].min().date()
max_date = df["date"].max().date()

date_range = st.sidebar.date_input(
    "📅 Chart date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Artist filter
available_artists = sorted(df["artist"].unique())

selected_artists = st.sidebar.multiselect(
    "🎤 Select artists",
    options=available_artists,
    placeholder="Choose artists"
)

# Song search
search_song = st.sidebar.text_input(
    "🎵 Search song",
    placeholder="Enter song name..."
)

# Chart position filter
position_range = st.sidebar.slider(
    "🏆 Chart position",
    min_value=1,
    max_value=50,
    value=(1, 50)
)

# Popularity filter
popularity_range = st.sidebar.slider(
    "⭐ Popularity score",
    min_value=0,
    max_value=100,
    value=(0, 100)
)

# Apply filters
data = df.copy()

if isinstance(date_range, (tuple, list)):
    if len(date_range) == 2:
        data = data[
            data["date"].dt.date.between(
                date_range[0], date_range[1]
            )
        ]
elif date_range:
    data = data[data["date"].dt.date == date_range]

if selected_artists:
    data = data[data["artist"].isin(selected_artists)]

if search_song.strip():
    data = data[
        data["song"].str.contains(
            search_song.strip(),
            case=False,
            na=False
        )
    ]

data = data[
    data["position"].between(
        position_range[0],
        position_range[1]
    )
]

if data["popularity"].notna().any():
    data = data[
        data["popularity"].between(
            popularity_range[0],
            popularity_range[1]
        )
    ]

st.sidebar.markdown("---")
st.sidebar.success(f"Showing {len(data):,} records")
st.sidebar.caption(f"Total dataset records: {len(df):,}")

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown("""
<div class="hero">
    <div class="hero-kicker">Music • Trends • Insights</div>
    <h1>US Top 50 Playlist Analytics</h1>
    <p>Explore chart movements, discover leading artists, and understand what makes tracks popular.</p>
</div>
""", unsafe_allow_html=True)

st.caption(
    f"Showing data from **{data['date'].min():%d %b %Y}** to "
    f"**{data['date'].max():%d %b %Y}**"
)

# ---------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------
st.markdown('<div class="section-heading">Dashboard overview</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">A quick snapshot of the selected chart data</div>', unsafe_allow_html=True)

avg_popularity = data["popularity"].mean()
best_rank = data["position"].min()

kpis = [
    ("CHART RECORDS", f"{len(data):,}", "Total selected entries"),
    ("UNIQUE SONGS", f"{data['song'].nunique():,}", "Distinct tracks"),
    ("ARTISTS", f"{data['artist'].nunique():,}", "Distinct performers"),
    ("AVG. POPULARITY", f"{avg_popularity:.1f}" if pd.notna(avg_popularity) else "N/A", "Average popularity score"),
]
cols = st.columns(4)
for col, (label, value, note) in zip(cols, kpis):
    with col:
        st.markdown(
            f"""<div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-note">{note}</div>
            </div>""",
            unsafe_allow_html=True
        )

# ---------------------------------------------------------
# CHART RANKING TRENDS
# ---------------------------------------------------------
st.markdown('<div class="section-heading">📈 Chart ranking trends</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Track how selected songs move through the Top 50 over time</div>', unsafe_allow_html=True)

song_options = sorted(data["song"].unique().tolist())
default_songs = song_options[:min(3, len(song_options))]
selected_songs = st.multiselect(
    "Choose tracks to compare",
    options=song_options,
    default=default_songs,
    key="trend_songs"
)

if selected_songs:
    trend_data = data[data["song"].isin(selected_songs)].sort_values("date")
    fig = px.line(
        trend_data,
        x="date",
        y="position",
        color="song",
        markers=True,
        hover_data={"artist": True, "popularity": True, "position": True}
    )
    fig.update_yaxes(autorange="reversed", title="Chart position", dtick=5)
    fig.update_xaxes(title="")
    fig.update_layout(**PLOT_LAYOUT, height=410, title="Song position over time")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Select one or more tracks to display their ranking trends.")

# ---------------------------------------------------------
# TOP SONGS AND ARTISTS
# ---------------------------------------------------------
left, right = st.columns([1.15, 1])

with left:
    st.markdown('<div class="section-heading">🏆 Top-performing songs</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Tracks with the most chart appearances</div>', unsafe_allow_html=True)

    song_stats = data.groupby(["song", "artist"]).agg(
        chart_days=("date", "nunique"),
        best_rank=("position", "min"),
        average_popularity=("popularity", "mean")
    ).reset_index()

    song_stats = song_stats.sort_values(
        ["chart_days", "best_rank"], ascending=[False, True]
    ).head(10)
    song_stats["average_popularity"] = song_stats["average_popularity"].round(1)
    song_stats = song_stats.rename(columns={
        "song": "Song",
        "artist": "Artist",
        "chart_days": "Chart Days",
        "best_rank": "Best Rank",
        "average_popularity": "Avg. Popularity"
    })
    st.dataframe(song_stats, use_container_width=True, hide_index=True)

with right:
    st.markdown('<div class="section-heading">🎤 Leading artists</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Artists ranked by playlist appearances</div>', unsafe_allow_html=True)

    artist_stats = data.groupby("artist").agg(
        appearances=("song", "size"),
        unique_songs=("song", "nunique")
    ).reset_index().nlargest(10, "appearances").sort_values("appearances")

    fig = px.bar(
        artist_stats,
        x="appearances",
        y="artist",
        orientation="h",
        text="appearances",
        color="appearances",
        color_continuous_scale=["#28583A", GREEN]
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(
        **PLOT_LAYOUT,
        height=420,
        title="Top 10 artists",
        xaxis_title="Playlist appearances",
        yaxis_title="",
        coloraxis_showscale=False
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# POPULARITY ANALYSIS
# ---------------------------------------------------------
st.markdown('<div class="section-heading">📊 Popularity and chart position</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Explore the relationship between a track’s popularity score and its chart rank</div>', unsafe_allow_html=True)

if data["popularity"].notna().any():
    fig = px.scatter(
        data.dropna(subset=["popularity"]),
        x="popularity",
        y="position",
        color="artist",
        hover_data=["song", "artist", "date"],
        opacity=0.72
    )
    fig.update_yaxes(autorange="reversed", title="Chart position")
    fig.update_xaxes(title="Popularity score")
    fig.update_layout(**PLOT_LAYOUT, height=420, title="Popularity score vs. chart position")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Popularity values are not available in the selected records.")

# ---------------------------------------------------------
# EXPLICIT CONTENT AND ALBUM TYPE
# ---------------------------------------------------------
left, right = st.columns(2)

with left:
    st.markdown('<div class="section-heading">🎧 Content classification</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Average popularity by explicit-content category</div>', unsafe_allow_html=True)

    if "is_explicit" in data.columns and data["popularity"].notna().any():
        explicit_map = {
            "true": "Explicit", "1": "Explicit", "yes": "Explicit",
            "false": "Non-Explicit", "0": "Non-Explicit", "no": "Non-Explicit"
        }
        content_data = data.copy()
        content_data["content_type"] = (
            content_data["is_explicit"].astype(str).str.lower().str.strip()
            .map(explicit_map).fillna("Unknown")
        )
        content_stats = content_data.groupby("content_type").agg(
            average_popularity=("popularity", "mean")
        ).reset_index()

        fig = px.bar(
            content_stats,
            x="content_type",
            y="average_popularity",
            color="content_type",
            color_discrete_sequence=[GREEN, "#6EAA83", "#64736A"]
        )
        fig.update_layout(
            **PLOT_LAYOUT,
            height=350,
            title="Average popularity by content type",
            xaxis_title="",
            yaxis_title="Average popularity",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Explicit-content or popularity data is not available.")

with right:
    st.markdown('<div class="section-heading">💿 Album type breakdown</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Track count and average popularity by album type</div>', unsafe_allow_html=True)

    if "album_type" in data.columns:
        album_stats = data.groupby("album_type", dropna=False).agg(
            average_popularity=("popularity", "mean"),
            songs=("song", "nunique")
        ).reset_index()
        album_stats["average_popularity"] = album_stats["average_popularity"].round(1)
        album_stats = album_stats.rename(columns={
            "album_type": "Album Type",
            "average_popularity": "Avg. Popularity",
            "songs": "Unique Songs"
        })
        st.dataframe(album_stats, use_container_width=True, hide_index=True)
    else:
        st.info("Album type information is not available in this dataset.")

# ---------------------------------------------------------
# DURATION ANALYSIS
# ---------------------------------------------------------
st.markdown('<div class="section-heading">⏱️ Song duration insights</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Compare track length with popularity scores</div>', unsafe_allow_html=True)

duration_data = data.dropna(subset=["duration_minutes", "popularity"])
if not duration_data.empty:
    fig = px.scatter(
        duration_data,
        x="duration_minutes",
        y="popularity",
        hover_data=["song", "artist"],
        color="popularity",
        color_continuous_scale=["#386447", GREEN],
        opacity=0.75
    )
    fig.update_layout(
        **PLOT_LAYOUT,
        height=390,
        title="Track duration vs. popularity",
        xaxis_title="Duration (minutes)",
        yaxis_title="Popularity score",
        coloraxis_showscale=False
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Duration and popularity values are not available for this selection.")

# ---------------------------------------------------------
# PLAYLIST ENTRIES AND EXITS
# ---------------------------------------------------------
st.markdown('<div class="section-heading">🔄 Playlist movement</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Daily count of tracks entering and leaving the Top 50</div>', unsafe_allow_html=True)

daily = data.groupby("date").apply(
    lambda frame: set(zip(frame["song"], frame["artist"]))
).sort_index()

movement_records = []
previous_tracks = set()

for chart_date, current_tracks in daily.items():
    movement_records.append({
        "date": chart_date,
        "New entries": len(current_tracks - previous_tracks),
        "Exits": len(previous_tracks - current_tracks)
    })
    previous_tracks = current_tracks

movement = pd.DataFrame(movement_records)
if not movement.empty:
    fig = px.line(
        movement,
        x="date",
        y=["New entries", "Exits"],
        markers=True,
        color_discrete_sequence=[GREEN, "#E39A72"]
    )
    fig.update_layout(
        **PLOT_LAYOUT,
        height=380,
        title="New entries and exits over time",
        xaxis_title="",
        yaxis_title="Number of tracks"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# DATA EXPLORER AND DOWNLOAD
# ---------------------------------------------------------
st.markdown('<div class="section-heading">🔎 Explore chart records</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Review the filtered records and export them for further analysis</div>', unsafe_allow_html=True)

with st.expander("Show filtered dataset", expanded=False):
    st.dataframe(data, use_container_width=True, hide_index=True, height=350)

csv_data = data.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Download filtered data (CSV)",
    data=csv_data,
    file_name="us_top_50_filtered_analysis.csv",
    mime="text/csv"
)

st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#829087;font-size:12px;'>"
    "US Top 50 Playlist Analytics · Built with Python, Pandas, Plotly & Streamlit"
    "</div>",
    unsafe_allow_html=True
)
