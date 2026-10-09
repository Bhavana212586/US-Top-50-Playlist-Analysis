import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
page_title="US Top 50 Music Analytics",
page_icon="🎵",
layout="wide"
)

@st.cache_data
def load_data():
df = pd.read_csv("Atlantic_United_States.csv")
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["duration_minutes"] = df["duration_ms"] / 60000
df["artist"] = df["artist"].fillna("Unknown").astype(str).str.strip()
df["song"] = df["song"].fillna("Unknown").astype(str).str.strip()
df["position"] = pd.to_numeric(df["position"], errors="coerce")
df["popularity"] = pd.to_numeric(df["popularity"], errors="coerce")
df["total_tracks"] = pd.to_numeric(df["total_tracks"], errors="coerce")
df = df.dropna(subset=["date", "position"])
df = df[df["position"].between(1, 50)]
return df

df = load_data()

st.title("🎵 United States Top 50 Playlist Analytics")
st.write("Historical Playlist Performance and Song Popularity Trend Analysis")

st.sidebar.header("Dashboard Filters")

date_min = df["date"].min().date()
date_max = df["date"].max().date()

date_range = st.sidebar.date_input(
"Select Date Range",
value=(date_min, date_max),
min_value=date_min,
max_value=date_max
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
"Playlist Rank Range",
1, 50, (1, 50)
)

filtered = filtered[
filtered["position"].between(rank_range[0], rank_range[1])
]

album_options = sorted(filtered["album_type"].dropna().unique())

selected_albums = st.sidebar.multiselect(
"Album Type",
album_options,
default=album_options
)

if selected_albums:
filtered = filtered[filtered["album_type"].isin(selected_albums)]

if filtered.empty:
st.warning("No data matches your selected filters.")
st.stop()

# KPI cards

c1, c2, c3, c4 = st.columns(4)

c1.metric("Unique Songs", filtered["song"].nunique())
c2.metric("Unique Artists", filtered["artist"].nunique())
c3.metric(
"Average Popularity",
round(filtered["popularity"].mean(), 2)
)
c4.metric("Average Rank", round(filtered["position"].mean(), 2))

# Song ranking trends

st.subheader("📈 Song Ranking Trends")

song_options = sorted(filtered["song"].unique())

selected_songs = st.multiselect(
"Choose Songs to Compare",
song_options,
default=song_options[:min(5, len(song_options))]
)

if selected_songs:
trend = filtered[filtered["song"].isin(selected_songs)]

```
fig = px.line(
    trend,
    x="date",
    y="position",
    color="song",
    markers=True,
    title="Song Position Over Time"
)
fig.update_yaxes(autorange="reversed")
st.plotly_chart(fig, use_container_width=True)
```

# Song performance

st.subheader("🏆 Song Performance")

song_metrics = (
filtered.groupby(["song", "artist"])
.agg(
days_on_chart=("date", "nunique"),
average_rank=("position", "mean"),
best_rank=("position", "min"),
rank_volatility=("position", "std"),
average_popularity=("popularity", "mean")
)
.reset_index()
)

st.dataframe(
song_metrics.sort_values("days_on_chart", ascending=False),
use_container_width=True
)

# Artist dominance

st.subheader("🎤 Artist Dominance")

artist_metrics = (
filtered.groupby("artist")
.agg(
unique_songs=("song", "nunique"),
total_appearances=("song", "size"),
average_rank=("position", "mean"),
average_popularity=("popularity", "mean")
)
.reset_index()
.sort_values("total_appearances", ascending=False)
)

artist_metrics["dominance_index"] = (
artist_metrics["total_appearances"] / len(filtered) * 100
)

fig = px.bar(
artist_metrics.head(10),
x="artist",
y="total_appearances",
title="Top 10 Artists by Playlist Appearances"
)
st.plotly_chart(fig, use_container_width=True)
st.dataframe(artist_metrics, use_container_width=True)

# Popularity vs rank

st.subheader("📊 Popularity vs Playlist Rank")

fig = px.scatter(
filtered,
x="popularity",
y="position",
hover_data=["song", "artist", "date"],
title="Popularity Score vs Playlist Position"
)
fig.update_yaxes(autorange="reversed")
st.plotly_chart(fig, use_container_width=True)

pearson = filtered["popularity"].corr(filtered["position"])
spearman = filtered["popularity"].corr(
filtered["position"], method="spearman"
)

st.write(f"**Pearson correlation:** {pearson:.3f}")
st.write(f"**Spearman correlation:** {spearman:.3f}")

# Explicit content analysis

st.subheader("🔞 Explicit vs Non-Explicit Performance")

explicit_metrics = (
filtered.groupby("is_explicit")
.agg(
average_popularity=("popularity", "mean"),
average_rank=("position", "mean"),
song_appearances=("song", "size")
)
.reset_index()
)

st.dataframe(explicit_metrics, use_container_width=True)

fig = px.bar(
explicit_metrics,
x="is_explicit",
y="average_popularity",
title="Average Popularity by Explicit Content"
)
st.plotly_chart(fig, use_container_width=True)

# Album type comparison

st.subheader("💿 Single vs Album Performance")

album_metrics = (
filtered.groupby("album_type")
.agg(
average_popularity=("popularity", "mean"),
average_rank=("position", "mean"),
unique_songs=("song", "nunique")
)
.reset_index()
)

st.dataframe(album_metrics, use_container_width=True)

# Duration analysis

st.subheader("⏱️ Song Duration vs Popularity")

fig = px.scatter(
filtered,
x="duration_minutes",
y="popularity",
hover_data=["song", "artist"],
title="Duration vs Popularity"
)
st.plotly_chart(fig, use_container_width=True)

# Album size analysis

st.subheader("💽 Album Size vs Popularity")

fig = px.scatter(
filtered,
x="total_tracks",
y="popularity",
hover_data=["song", "artist"],
title="Total Album Tracks vs Popularity"
)
st.plotly_chart(fig, use_container_width=True)

# Download filtered data

st.subheader("📥 Export Results")

st.download_button(
"Download Filtered Dataset",
data=filtered.to_csv(index=False).encode("utf-8"),
file_name="filtered_us_top_50.csv",
mime="text/csv"
)
