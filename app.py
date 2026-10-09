import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="US Top 50 Playlist Analysis",
    page_icon="🎵",
    layout="wide"
)


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

st.title("United States Top 50 Playlist Analysis")
st.write("Analysis of song popularity, chart rankings, artist performance, and playlist trends.")

# Dashboard filters
st.sidebar.header("Dashboard Filters")

date_range = st.sidebar.date_input(
    "Date Range",
    value=(df["date"].min().date(), df["date"].max().date())
)

filtered = df.copy()

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[
        filtered["date"].dt.date.between(start_date, end_date)
    ]

artists = sorted(filtered["artist"].unique())
selected_artists = st.sidebar.multiselect("Artists", artists)

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
    st.warning("No records match the selected filters.")
    st.stop()

# Key performance indicators
st.subheader("Key Performance Indicators")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Unique Songs", filtered["song"].nunique())
c2.metric("Unique Artists", filtered["artist"].nunique())

avg_pop = filtered["popularity"].mean()
c3.metric("Average Popularity", f"{avg_pop:.2f}" if pd.notna(avg_pop) else "N/A")

avg_rank = filtered["position"].mean()
c4.metric("Average Rank", f"{avg_rank:.2f}" if pd.notna(avg_rank) else "N/A")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Records", len(filtered))
c2.metric("Dates Covered", filtered["date"].nunique())

avg_duration = filtered["duration_minutes"].mean()
c3.metric(
    "Average Duration",
    f"{avg_duration:.2f} min" if pd.notna(avg_duration) else "N/A"
)

c4.metric("Best Rank", int(filtered["position"].min()))

# Song ranking trends
st.subheader("Song Ranking Trends")

song_options = sorted(filtered["song"].unique())

selected_songs = st.multiselect(
    "Choose Songs",
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

# Song performance metrics
st.subheader("Song Performance Analysis")

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

# Ranking stability
st.subheader("Ranking Stability")

volatility = song_metrics.dropna(subset=["rank_volatility"])

if not volatility.empty:
    fig = px.bar(
        volatility.nlargest(10, "rank_volatility"),
        x="song",
        y="rank_volatility",
        title="Songs with Highest Rank Volatility"
    )
    st.plotly_chart(fig, use_container_width=True)

# Artist performance
st.subheader("Artist Dominance")

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

# Popularity vs rank
st.subheader("Popularity vs Playlist Rank")

fig = px.scatter(
    filtered,
    x="popularity",
    y="position",
    hover_data=["song", "artist"],
    title="Popularity Compared with Playlist Position"
)
fig.update_yaxes(autorange="reversed")
st.plotly_chart(fig, use_container_width=True)

# Calculate correlations without requiring SciPy
correlation_data = filtered[["popularity", "position"]].dropna()

if len(correlation_data) >= 2:
    pearson = correlation_data["popularity"].corr(
        correlation_data["position"], method="pearson"
    )

    # Rank the values first, then calculate Pearson correlation
    ranked_data = correlation_data.rank()

    spearman = ranked_data["popularity"].corr(
        ranked_data["position"], method="pearson"
    )
else:
    pearson = float("nan")
    spearman = float("nan")

c1, c2 = st.columns(2)
c1.metric("Pearson Correlation", f"{pearson:.3f}" if pd.notna(pearson) else "N/A")
c2.metric("Spearman Correlation", f"{spearman:.3f}" if pd.notna(spearman) else "N/A")

# Explicit content analysis
st.subheader("Explicit vs Non-Explicit Songs")

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

# Album type analysis
st.subheader("Single vs Album Performance")

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

# Duration analysis
st.subheader("Song Duration vs Popularity")

fig = px.scatter(
    filtered,
    x="duration_minutes",
    y="popularity",
    hover_data=["song", "artist"],
    title="Song Duration Compared with Popularity"
)
st.plotly_chart(fig, use_container_width=True)

# Album size analysis
st.subheader("Album Size vs Popularity")

fig = px.scatter(
    filtered,
    x="total_tracks",
    y="popularity",
    hover_data=["song", "artist"],
    title="Album Track Count vs Popularity"
)
st.plotly_chart(fig, use_container_width=True)

# Playlist entries and exits
st.subheader("Playlist Entries and Exits")

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

# Download analysis
st.subheader("Download Analysis")

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
