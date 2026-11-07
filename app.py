
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# PAGE CONFIG
st.set_page_config(
    page_title="US Top 50 | Music Analytics",
    page_icon="🎧",
    layout="wide"
)

# PURPLE + LAVENDER THEME
st.markdown("""
<style>
.stApp {
    background:#171020 !important;
    color:#FFFFFF !important;
}

[data-testid="stHeader"] {
    background:#171020 !important;
}

[data-testid="stSidebar"] {
    background:#241536 !important;
}

.stApp h1,.stApp h2,.stApp h3,
.stApp p,.stApp label,.stApp span {
    color:#F8F4FF !important;
}

[data-testid="stSidebar"] * {
    color:#FFFFFF !important;
}

/* KPI CARDS */
.kpi {
    background:linear-gradient(135deg,#35204C,#493064);
    border:1px solid #9470BC;
    border-radius:12px;
    padding:18px;
    text-align:center;
}

.kpi h2 {
    color:#D0B4F5 !important;
}

.kpi p {
    color:#FFFFFF !important;
}

/* ARTIST DROPDOWN */
[data-baseweb="select"] > div {
    background:#493064 !important;
    border-color:#B58AE8 !important;
    color:#FFFFFF !important;
}

[data-baseweb="select"] * {
    color:#FFFFFF !important;
}

[data-baseweb="popover"],
[data-baseweb="menu"],
[role="listbox"],
[role="option"] {
    background:#35204C !important;
    color:#FFFFFF !important;
}

/* DATE RANGE - PURPLE BACKGROUND */
[data-testid="stDateInput"] {
    background:#241536 !important;
}

[data-testid="stDateInput"] [data-baseweb="input"] {
    background-color:#493064 !important;
    border:1px solid #B58AE8 !important;
    border-radius:8px !important;
}

[data-testid="stDateInput"] input {
    background-color:#493064 !important;
    color:#FFFFFF !important;
    -webkit-text-fill-color:#FFFFFF !important;
    border:none !important;
    opacity:1 !important;
}

[data-testid="stDateInput"] button {
    background-color:#493064 !important;
    color:#FFFFFF !important;
}

[data-testid="stDateInput"] svg {
    color:#FFFFFF !important;
    fill:#FFFFFF !important;
}

/* DATE CALENDAR POPUP */
[data-baseweb="calendar"] {
    background:#35204C !important;
    color:#FFFFFF !important;
}

[data-baseweb="calendar"] * {
    color:#FFFFFF !important;
}

/* BUTTONS */
.stButton button,
.stDownloadButton button {
    background:#B58AE8 !important;
    color:#241536 !important;
    border:0 !important;
    border-radius:8px !important;
    font-weight:bold !important;
}

/* TABLE */
[data-testid="stDataFrame"] {
    border:1px solid #9470BC;
    border-radius:10px;
}

/* CHART TEXT */
.js-plotly-plot .plotly text {
    fill:#FFFFFF !important;
}

hr {
    border-color:#76529B !important;
}
</style>
""", unsafe_allow_html=True)


# CHART COLORS
COLORS = [
    "#B58AE8",
    "#895BC1",
    "#D0B4F5",
    "#65418A",
    "#E2C8FF"
]


# CHART STYLE
def chart_style(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#171020",
        plot_bgcolor="#241536",
        font=dict(color="#FFFFFF"),
        colorway=COLORS,
        height=400
    )
    return fig


# LOAD DATASET
file = Path("Atlantic_United_States.csv")

if not file.exists():
    st.error("Dataset not found. Check your CSV filename.")
    st.stop()

df = pd.read_csv(file)
df.columns = df.columns.str.strip().str.lower()

required = ["date", "position", "song", "artist"]

if any(c not in df.columns for c in required):
    st.error("Required columns missing: date, position, song, artist")
    st.stop()

df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["position"] = pd.to_numeric(df["position"], errors="coerce")

df = df.dropna(subset=["date", "position"]).copy()

df["song"] = df["song"].fillna("Unknown Song")
df["artist"] = df["artist"].fillna("Unknown Artist")

for c in ["popularity", "duration_ms", "is_explicit", "album_type"]:
    if c not in df.columns:
        df[c] = None

df["popularity"] = pd.to_numeric(
    df["popularity"], errors="coerce"
)

df["duration_ms"] = pd.to_numeric(
    df["duration_ms"], errors="coerce"
)

df["duration_minutes"] = df["duration_ms"] / 60000

if df.empty:
    st.error("No valid data found.")
    st.stop()


# SIDEBAR FILTERS
st.sidebar.title("🎧 Music Analytics")
st.sidebar.markdown("### Dashboard Filters")

min_date = df["date"].min().date()
max_date = df["date"].max().date()

date_range = st.sidebar.date_input(
    "📅 Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

selected_artists = st.sidebar.multiselect(
    "🎤 Select Artist",
    sorted(df["artist"].unique()),
    placeholder="Choose artist"
)


# FILTER DATA
data = df.copy()

if isinstance(date_range, (tuple, list)):
    if len(date_range) == 2:
        start_date, end_date = date_range

        data = data[
            data["date"].dt.date.between(
                start_date, end_date
            )
        ]

    elif len(date_range) == 1:
        data = data[
            data["date"].dt.date == date_range[0]
        ]

if selected_artists:
    data = data[
        data["artist"].isin(selected_artists)
    ]

if data.empty:
    st.warning("No matching records. Please change your filters.")
    st.stop()


# HEADER
st.markdown("""
<h1>🎧 US TOP 50</h1>
<h3 style="color:#D0B4F5 !important;">
Music Analytics Dashboard
</h3>
<p>Explore music trends, artist performance and chart rankings.</p>
""", unsafe_allow_html=True)


# KPI CARDS
st.header("📊 Dashboard Overview")

metrics = [
    ("Total Records", len(data)),
    ("Unique Songs", data["song"].nunique()),
    ("Total Artists", data["artist"].nunique()),
    (
        "Avg Popularity",
        round(data["popularity"].mean(), 1)
        if data["popularity"].notna().any()
        else "N/A"
    )
]

cols = st.columns(4)

for col, (label, value) in zip(cols, metrics):
    col.markdown(
        f"""
        <div class="kpi">
            <p>{label}</p>
            <h2>{value}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )


# SELECTED ARTIST SONGS
st.header("🎤 Selected Artist Songs")

if selected_artists:

    artist_songs = data[
        data["artist"].isin(selected_artists)
    ][["artist", "song", "position", "date"]].copy()

    artist_songs = artist_songs.drop_duplicates()

    artist_songs["date"] = (
        artist_songs["date"].dt.strftime("%Y-%m-%d")
    )

    artist_songs = artist_songs.sort_values(
        ["artist", "position"]
    )

    st.dataframe(
        artist_songs,
        use_container_width=True,
        hide_index=True
    )

else:
    st.info(
        "Select an artist from the sidebar to view their songs."
    )


# CHART RANKING TRENDS
st.header("📈 Chart Ranking Trends")

trend = (
    data.groupby("date", as_index=False)["position"]
    .mean()
)

fig = px.line(
    trend,
    x="date",
    y="position",
    markers=True,
    title="Average Chart Position Over Time"
)

fig.update_yaxes(autorange="reversed")

st.plotly_chart(
    chart_style(fig),
    use_container_width=True
)


# TOP ARTISTS
st.header("🎵 Top 10 Artists")

top = (
    data["artist"].value_counts()
    .head(10)
    .reset_index()
)

top.columns = ["Artist", "Appearances"]

fig = px.bar(
    top,
    x="Artist",
    y="Appearances",
    text="Appearances",
    color="Artist",
    color_discrete_sequence=COLORS
)

st.plotly_chart(
    chart_style(fig),
    use_container_width=True
)


# POPULARITY VS RANK
st.header("⭐ Popularity vs Chart Rank")

pop = data.dropna(subset=["popularity"])

if not pop.empty:

    fig = px.scatter(
        pop,
        x="position",
        y="popularity",
        color="artist",
        hover_data=["song"],
        title="Popularity Compared with Chart Position"
    )

    fig.update_xaxes(autorange="reversed")

    st.plotly_chart(
        chart_style(fig),
        use_container_width=True
    )

else:
    st.info("Popularity data unavailable.")


# EXPLICIT CONTENT
st.header("🔞 Explicit Content Analysis")

if data["is_explicit"].notna().any():

    explicit = (
        data["is_explicit"].astype(str).str.lower()
        .map({
            "true": "Explicit",
            "1": "Explicit",
            "yes": "Explicit",
            "false": "Non-Explicit",
            "0": "Non-Explicit",
            "no": "Non-Explicit"
        })
        .fillna("Unknown")
    )

    counts = explicit.value_counts()

    fig = px.pie(
        names=counts.index,
        values=counts.values,
        hole=0.5,
        color_discrete_sequence=COLORS
    )

    st.plotly_chart(
        chart_style(fig),
        use_container_width=True
    )

else:
    st.info("Explicit content data unavailable.")


# ALBUM TYPE
st.header("💿 Album Type Analysis")

album = data.dropna(subset=["album_type"])

if not album.empty:

    counts = album["album_type"].value_counts().reset_index()
    counts.columns = ["Album Type", "Count"]

    fig = px.bar(
        counts,
        x="Album Type",
        y="Count",
        text="Count",
        color="Album Type",
        color_discrete_sequence=COLORS
    )

    st.plotly_chart(
        chart_style(fig),
        use_container_width=True
    )

else:
    st.info("Album type data unavailable.")


# SONG DURATION
st.header("⏱️ Song Duration Analysis")

duration = data.dropna(subset=["duration_minutes"])

if not duration.empty:

    fig = px.histogram(
        duration,
        x="duration_minutes",
        nbins=20,
        title="Distribution of Song Durations",
        color_discrete_sequence=["#B58AE8"]
    )

    st.plotly_chart(
        chart_style(fig),
        use_container_width=True
    )

else:
    st.info("Song duration data unavailable.")


# COMPLETE DATASET
st.header("📋 Complete Music Dataset")

st.dataframe(
    data.sort_values(
        ["date", "position"],
        ascending=[False, True]
    ),
    use_container_width=True,
    hide_index=True
)


# DOWNLOAD
st.download_button(
    "⬇️ Download Filtered Dataset",
    data=data.to_csv(index=False).encode("utf-8"),
    file_name="US_Top_50_Filtered.csv",
    mime="text/csv"
)


# FOOTER
st.markdown("---")

st.markdown("""
<div style="text-align:center;padding:15px;">
<h3 style="color:#D0B4F5 !important;">
🎧 US TOP 50 | MUSIC ANALYTICS
</h3>
<p>Built with Python • Streamlit • Pandas • Plotly</p>
</div>
""", unsafe_allow_html=True)
