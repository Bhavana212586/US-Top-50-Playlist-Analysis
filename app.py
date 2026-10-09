```python
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="US Top 50 Playlist Analysis",
    page_icon="🎵",
    layout="wide"
)


# 1. LOAD AND CLEAN DATA
@st.cache_data
def load_data():
    df = pd.read_csv("Atlantic_United_States.csv")

    required = [
        "date", "position", "song", "artist", "popularity",
        "duration_ms", "album_type", "total_tracks", "is_explicit"
    ]

    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    for col in ["position", "popularity", "duration_ms", "total_tracks"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["song"] = df["song"].fillna("Unknown").astype(str).str.strip()
    df["artist"] = df["artist"].fillna("Unknown").astype(str).str.strip()

    df = df.drop_duplicates()
    df = df.dropna(subset=["date", "position"])
    df = df[df["position"].between(1, 50)].copy()

    df["duration_minutes"] = df["duration_ms"] / 60000

    return df


df = load_data()


# 2. DASHBOARD TITLE
st.title("🎵 United States Top 50 Playlist Analysis")
st.write(
    "Historical analysis of song rankings, popularity, "
    "artist performance, and playlist trends."
)


# 3. FILTERS
st.sidebar.header("Dashboard Filters")

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(df["date"].min().date(), df["date"].max().date())
)

filtered = df.copy()

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[
        filtered["date"].dt.date.between(start_date, end_date)
    ]

artist_options = sorted(filtered["artist"].unique())

selected_artists = st.sidebar.multiselect(
    "Select Artists",
    artist_options
)

if selected_artists:
    filtered = filtered[filtered["artist"].isin(selected_artists)]

rank_range = st.sidebar.slider(
    "Playlist Rank",
    min_value=1,
    max_value=50,
    value=(1, 50)
)

filtered = filtered[
    filtered["position"].between(rank_range[0], rank_range[1])
]

if filtered.empty:
    st.warning("No data available for the selected filters.")
    st.stop()


# 4. KEY PERFORMANCE INDICATORS
st.subheader("📌 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Unique Songs", filtered["song"].nunique())
col2.metric("Unique Artists", filtered["artist"].nunique())
col3.metric(
    "Average Popularity",
    f"{filtered['popularity'].mean():.2f}"
    if filtered["popularity"].notna().any() else "N/A"
)
col4.metric("Average Rank", f"{filtered['position'].mean():.2f}")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Records", len(filtered))
col2.metric("Dates Covered", filtered["date"].nunique())
col3.metric(
    "Average Duration",
    f"{filtered['duration_minutes'].mean():.2f} min"
    if filtered["duration_minutes"].notna().any() else "N/A"
)
col4.metric("Best Rank", int(filtered["position"].min()))


# 5. SONG RANKING TRENDS
st.subheader("📈 Song Ranking Trends")

song_options = sorted(filtered["song"].unique())

selected_songs = st.multiselect(
    "Choose Songs to Compare",
    song_options,
    default=song_options[:min(5, len(song_options))]
)

if selected_songs:
    trend = filtered[
        filtered["song"].isin(selected_songs)
    ].sort_values("date")

    fig = px.line(
        trend,
        x="date",
        y="position",
        color="song",
        title="Song Position Over Time",
        markers=True
    )

    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)


# 6. SONG PERFORMANCE
st.subheader("🏆 Song Performance Analysis")

song_metrics = filtered.groupby(["song", "artist"]).agg(
    days_on_chart=("date", "nunique"),
    average_rank=("position", "mean"),
    best_rank=("position", "min"),
    rank_volatility=("position", "std"),
    average_popularity=("popularity", "mean")
).reset_index()

tab1, tab2, tab3 = st.tabs(
    ["Chart Longevity", "Best Peak Rank", "Popularity"]
)

with tab1:
    st.dataframe(
        song_metrics.sort_values(
            "days_on_chart", ascending=False
        ).head(10),
        use_container_width=True
    )

with tab2:
    st.dataframe(
        song_metrics.sort_values("best_rank").head(10),
        use_container_width=True
    )

with tab3:
    st.dataframe(
        song_metrics.sort_values(
            "average_popularity", ascending=False
        ).head(10),
        use_container_width=True
    )

fig = px.scatter(
    song_metrics,
    x="days_on_chart",
    y="best_rank",
    hover_data=["song", "artist"],
    title="Chart Longevity vs Best Rank"
)

fig.update_yaxes(autorange="reversed")
st.plotly_chart(fig, use_container_width=True)


# 7. RANK VOLATILITY
st.subheader("📊 Ranking Stability")

volatility = song_metrics.dropna(subset=["rank_volatility"])

if not volatility.empty:
    fig = px.bar(
        volatility.nlargest(10, "rank_volatility"),
        x="song",
        y="rank_volatility",
        title="Songs with Highest Rank Volatility"
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Not enough ranking observations to calculate volatility.")


# 8. ARTIST PERFORMANCE
st.subheader("🎤 Artist Dominance")

artist_metrics = filtered.groupby("artist").agg(
    unique_songs=("song", "nunique"),
    appearances=("song", "size"),
    days_present=("date", "nunique"),
    average_rank=("position", "mean"),
    average_popularity=("popularity", "mean")
).reset_index()

artist_metrics["dominance_percent"] = (
    artist_metrics["appearances"] / len(filtered) * 100
)

artist_metrics = artist_metrics.sort_values(
    "appearances", ascending=False
)

fig = px.bar(
    artist_metrics.head(10),
    x="artist",
    y="appearances",
    title="Top 10 Artists by Playlist Appearances"
)

st.plotly_chart(fig, use_container_width=True)
st.dataframe(artist_metrics, use_container_width=True)


# 9. POPULARITY VS RANK
st.subheader("📉 Popularity vs Playlist Rank")

fig = px.scatter(
    filtered,
    x="popularity",
    y="position",
    hover_data=["song", "artist"],
    title="Popularity Compared with Playlist Position"
)

fig.update_yaxes(autorange="reversed")
st.plotly_chart(fig, use_container_width=True)

pearson = filtered["popularity"].corr(
    filtered["position"], method="pearson"
)

spearman = filtered["popularity"].corr(
    filtered["position"], method="spearman"
)

col1, col2 = st.columns(2)

col1.metric(
    "Pearson Correlation",
    f"{pearson:.3f}" if pd.notna(pearson) else "N/A"
)

col2.metric(
    "Spearman Correlation",
    f"{spearman:.3f}" if pd.notna(spearman) else "N/A"
)


# 10. EXPLICIT CONTENT ANALYSIS
st.subheader("🔞 Explicit vs Non-Explicit Songs")

explicit_map = {
    "true": "Explicit",
    "1": "Explicit",
    "yes": "Explicit",
    "false": "Non-Explicit",
    "0": "Non-Explicit",
    "no": "Non-Explicit"
}

explicit_df = filtered.copy()

explicit_df["content_type"] = (
    explicit_df["is_explicit"]
    .astype(str)
    .str.lower()
    .str.strip()
    .map(explicit_map)
    .fillna("Unknown")
)

explicit_metrics = explicit_df.groupby("content_type").agg(
    average_popularity=("popularity", "mean"),
    average_rank=("position", "mean"),
    appearances=("song", "size")
).reset_index()

st.dataframe(explicit_metrics, use_container_width=True)

fig = px.bar(
    explicit_metrics,
    x="content_type",
    y="average_popularity",
    title="Average Popularity by Content Type"
)

st.plotly_chart(fig, use_container_width=True)


# 11. ALBUM TYPE ANALYSIS
st.subheader("💿 Single vs Album Performance")

album_metrics = filtered.groupby("album_type", dropna=False).agg(
    average_popularity=("popularity", "mean"),
    average_rank=("position", "mean"),
    unique_songs=("song", "nunique")
).reset_index()

st.dataframe(album_metrics, use_container_width=True)

fig = px.bar(
    album_metrics,
    x="album_type",
    y="average_popularity",
    title="Popularity by Album Type"
)

st.plotly_chart(fig, use_container_width=True)


# 12. SONG DURATION ANALYSIS
st.subheader("⏱️ Song Duration vs Popularity")

fig = px.scatter(
    filtered,
    x="duration_minutes",
    y="popularity",
    hover_data=["song", "artist"],
    title="Song Duration Compared with Popularity"
)

st.plotly_chart(fig, use_container_width=True)


# 13. ALBUM SIZE ANALYSIS
st.subheader("💽 Album Size vs Popularity")

fig = px.scatter(
    filtered,
    x="total_tracks",
    y="popularity",
    hover_data=["song", "artist"],
    title="Album Track Count vs Popularity"
)

st.plotly_chart(fig, use_container_width=True)


# 14. PLAYLIST ENTRIES AND EXITS
st.subheader("🔄 Playlist Entries and Exits")

daily_songs = (
    filtered.groupby("date")
    .apply(lambda group: set(zip(group["song"], group["artist"])))
    .sort_index()
)

records = []
previous_songs = set()

for current_date, current_songs in daily_songs.items():
    records.append({
        "date": current_date,
        "new_entries": len(current_songs - previous_songs),
        "exits": len(previous_songs - current_songs)
    })

    previous_songs = current_songs

entry_exit = pd.DataFrame(records)

if not entry_exit.empty:
    fig = px.line(
        entry_exit,
        x="date",
        y=["new_entries", "exits"],
        title="Daily Playlist Entries and Exits"
    )

    st.plotly_chart(fig, use_container_width=True)


# 15. DOWNLOAD RESULTS
st.subheader("📥 Download Analysis")

st.download_button(
    "Download Cleaned Dataset",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="cleaned_playlist_data.csv",
    mime="text/csv"
)

st.download_button(
    "Download Song Metrics",
    data=song_metrics.to_csv(index=False).encode("utf-8"),
    file_name="song_performance.csv",
    mime="text/csv"
)

st.download_button(
    "Download Artist Metrics",
    data=artist_metrics.to_csv(index=False).encode("utf-8"),
    file_name="artist_performance.csv",
    mime="text/csv"
)

st.success("Playlist analysis completed successfully!")
```
