```python
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="US Top 50 Playlist Analysis",
    page_icon="🎵",
    layout="wide"
)

# Load and clean data
@st.cache_data
def load_data():
    df = pd.read_csv("Atlantic_United_States.csv")

    required = [
        "date", "position", "song", "artist", "popularity",
        "duration_ms", "album_type", "total_tracks", "is_explicit"
    ]

    missing = [col for col in required if col not in df.columns]
    if missing:
        st.error(f"Missing columns: {missing}")
        st.stop()

    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    for col in ["position", "popularity", "duration_ms", "total_tracks"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.drop_duplicates()
    df = df.dropna(subset=["date", "position"])
    df = df[df["position"].between(1, 50)].copy()

    df["song"] = df["song"].fillna("Unknown")
    df["artist"] = df["artist"].fillna("Unknown")
    df["duration_minutes"] = df["duration_ms"] / 60000

    return df


df = load_data()

# Dashboard title
st.title("🎵 United States Top 50 Playlist Analysis")
st.write("Analysis of song popularity, chart rankings, artists, and playlist trends.")

# Filters
st.sidebar.header("Dashboard Filters")

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(df["date"].min().date(), df["date"].max().date())
)

filtered = df.copy()

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start, end = date_range
    filtered = filtered[filtered["date"].dt.date.between(start, end)]

artists = st.sidebar.multiselect(
    "Select Artists",
    sorted(filtered["artist"].unique())
)

if artists:
    filtered = filtered[filtered["artist"].isin(artists)]

if filtered.empty:
    st.warning("No data available for these filters.")
    st.stop()

# KPIs
st.subheader("📌 Key Performance Indicators")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Unique Songs", filtered["song"].nunique())
c2.metric("Unique Artists", filtered["artist"].nunique())
c3.metric("Average Popularity", round(filtered["popularity"].mean(), 2))
c4.metric("Average Playlist Rank", round(filtered["position"].mean(), 2))

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Records", len(filtered))
c2.metric("Dates Covered", filtered["date"].nunique())
c3.metric("Average Duration (min)", round(filtered["duration_minutes"].mean(), 2))
c4.metric("Best Rank", int(filtered["position"].min()))

# Song ranking trends
st.subheader("📈 Song Ranking Trends")

songs = st.multiselect(
    "Choose Songs",
    sorted(filtered["song"].unique()),
    default=sorted(filtered["song"].unique())[:5]
)

if songs:
    trend = filtered[filtered["song"].isin(songs)].sort_values("date")
    fig = px.line(
        trend, x="date", y="position", color="song",
        title="Song Position O
```
