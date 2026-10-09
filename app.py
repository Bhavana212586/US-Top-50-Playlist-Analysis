import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="US Top 50 Analysis", page_icon="🎵", layout="wide")


@st.cache_data
def load_data():
    df = pd.read_csv("Atlantic_United_States.csv")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    for col in ["position", "popularity", "duration_ms"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["song"] = df["song"].fillna("Unknown")
    df["artist"] = df["artist"].fillna("Unknown")
    df = df.drop_duplicates().dropna(subset=["date", "position"])
    df = df[df["position"].between(1, 50)].copy()
    df["duration_minutes"] = df["duration_ms"] / 60000
    return df


df = load_data()

st.title("🎵 US Top 50 Playlist Analysis")
st.write("Explore song rankings, popularity, and artist performance.")

# Filters
st.sidebar.header("Filters")

dates = st.sidebar.date_input(
    "Date Range",
    value=(df["date"].min().date(), df["date"].max().date())
)

data = df.copy()

if isinstance(dates, (tuple, list)) and len(dates) == 2:
    data = data[data["date"].dt.date.between(dates[0], dates[1])]

artists = st.sidebar.multiselect("Artists", sorted(data["artist"].unique()))
if artists:
    data = data[data["artist"].isin(artists)]

if data.empty:
    st.warning("No data available for these filters.")
    st.stop()

# KPIs
st.subheader("📌 Overview")

a, b, c, d = st.columns(4)
a.metric("Records", len(data))
b.metric("Songs", data["song"].nunique())
c.metric("Artists", data["artist"].nunique())
c.metric("Average Popularity", f"{data['popularity'].mean():.1f}")

# Song trends
st.subheader("📈 Song Ranking Trends")

songs = st.multiselect(
    "Choose songs",
    sorted(data["song"].unique()),
    default=sorted(data["song"].unique())[:3]
)

if songs:
    fig = px.line(
        data[data["song"].isin(songs)].sort_values("date"),
        x="date", y="position", color="song", markers=True
    )
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

# Top songs
st.subheader("🏆 Top Songs")

song_stats = data.groupby(["song", "artist"]).agg(
    chart_days=("date", "nunique"),
    best_rank=("position", "min"),
    average_popularity=("popularity", "mean")
).reset_index()

st.dataframe(
    song_stats.sort_values("chart_days", ascending=False).head(10),
    use_container_width=True
)

# Top artists
st.subheader("🎤 Top Artists")

artist_stats = data.groupby("artist").agg(
    appearances=("song", "size"),
    unique_songs=("song", "nunique")
).reset_index().nlargest(10, "appearances")

fig = px.bar(
    artist_stats, x="artist", y="appearances",
    title="Top 10 Artists by Playlist Appearances"
)
st.plotly_chart(fig, use_container_width=True)

# Popularity and ranking
st.subheader("📊 Popularity vs Rank")

fig = px.scatter(
    data, x="popularity", y="position",
    hover_data=["song", "artist"]
)
fig.update_yaxes(autorange="reversed")
st.plotly_chart(fig, use_container_width=True)

# Explicit content
st.subheader("🎧 Explicit vs Non-Explicit")

explicit_map = {
    "true": "Explicit", "1": "Explicit", "yes": "Explicit",
    "false": "Non-Explicit", "0": "Non-Explicit", "no": "Non-Explicit"
}

data["content_type"] = (
    data["is_explicit"].astype(str).str.lower().str.strip()
    .map(explicit_map).fillna("Unknown")
)

content_stats = data.groupby("content_type").agg(
    average_popularity=("popularity", "mean")
).reset_index()

fig = px.bar(
    content_stats, x="content_type", y="average_popularity",
    title="Popularity by Content Type"
)
st.plotly_chart(fig, use_container_width=True)

# Album type
st.subheader("💿 Album Type")

album_stats = data.groupby("album_type", dropna=False).agg(
    average_popularity=("popularity", "mean"),
    songs=("song", "nunique")
).reset_index()

st.dataframe(album_stats, use_container_width=True)

# Duration
st.subheader("⏱️ Song Duration vs Popularity")

fig = px.scatter(
    data, x="duration_minutes", y="popularity",
    hover_data=["song", "artist"]
)
st.plotly_chart(fig, use_container_width=True)

# Playlist entries and exits
st.subheader("🔄 Playlist Entries and Exits")

daily = data.groupby("date").apply(
    lambda x: set(zip(x["song"], x["artist"]))
).sort_index()

records = []
previous = set()

for date, current in daily.items():
    records.append({
        "date": date,
        "new_entries": len(current - previous),
        "exits": len(previous - current)
    })
    previous = current

entry_exit = pd.DataFrame(records)

if not entry_exit.empty:
    fig = px.line(
        entry_exit, x="date",
        y=["new_entries", "exits"]
    )
    st.plotly_chart(fig, use_container_width=True)

# Download
st.subheader("📥 Download Data")

st.download_button(
    "Download Filtered Dataset",
    data=data.to_csv(index=False).encode("utf-8"),
    file_name="us_top_50_analysis.csv",
    mime="text/csv"
)
