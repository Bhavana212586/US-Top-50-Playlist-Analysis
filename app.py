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
    """Apply one clear, consistent style to every Plotly chart."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#171020",
        plot_bgcolor="#241536",
        font=dict(family="Arial, sans-serif", size=13, color="#FFFFFF"),
        colorway=COLORS,
        height=height,
        margin=dict(l=45, r=35, t=75, b=55),
        title=dict(
            x=0.02, xanchor="left",
            font=dict(size=19, color="#E2C8FF")
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="right", x=1,
            bgcolor="rgba(0,0,0,0)"
        ),
        hoverlabel=dict(
            bgcolor="#493064",
            bordercolor="#B58AE8",
            font=dict(color="#FFFFFF", size=13)
        ),
        hovermode="closest"
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        automargin=True,
        title_font=dict(size=13, color="#E2C8FF"),
        tickfont=dict(size=11, color="#FFFFFF")
    )
    # Make line charts and markers easier to see without changing chart data.
    fig.update_traces(
        selector=dict(type="scatter", mode="lines+markers"),
        line=dict(width=3, color="#B58AE8"),
        marker=dict(size=7, color="#E2C8FF", line=dict(width=1, color="#FFFFFF"))
    )
    fig.update_traces(
        selector=dict(type="scatter", mode="markers"),
        marker=dict(size=9, opacity=0.78)
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#493064",
        gridwidth=1,
        zeroline=False,
        automargin=True,
        title_font=dict(size=13, color="#E2C8FF"),
        tickfont=dict(size=11, color="#FFFFFF")
    )
    return fig


# --------------------------------------------------
# LOAD AND VALIDATE DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    candidates = [Path("Atlantic_United_States.csv"), Path("Atlantic_United_States (1).csv")]
    csv_path = next((p for p in candidates if p.exists()), None)
    if csv_path is None:
        return None, "Dataset not found. Keep Atlantic_United_States.csv in the same folder as app.py."

    raw = pd.read_csv(csv_path)
    raw.columns = raw.columns.str.strip().str.lower()
    required = ["date", "position", "song", "artist"]
    missing_cols = [c for c in required if c not in raw.columns]
    if missing_cols:
        return None, "Required columns missing: " + ", ".join(missing_cols)

    raw_rows = len(raw)
    raw["date"] = pd.to_datetime(raw["date"], format="%d-%m-%Y", errors="coerce")
    # Fallback for datasets that already use ISO date format.
    invalid = raw["date"].isna()
    if invalid.any():
        raw.loc[invalid, "date"] = pd.to_datetime(raw.loc[invalid, "date"], errors="coerce")
    raw["position"] = pd.to_numeric(raw["position"], errors="coerce")
    for col in ["popularity", "duration_ms", "total_tracks"]:
        if col not in raw.columns:
            raw[col] = pd.NA
        raw[col] = pd.to_numeric(raw[col], errors="coerce")
    for col in ["is_explicit", "album_type", "album_cover_url"]:
        if col not in raw.columns:
            raw[col] = pd.NA

    raw["song"] = raw["song"].fillna("Unknown Song").astype(str)
    raw["artist"] = raw["artist"].fillna("Unknown Artist").astype(str)
    invalid_rows = int(raw[["date", "position"]].isna().any(axis=1).sum())
    raw = raw.dropna(subset=["date", "position"]).copy()
    exact_duplicates = int(raw.duplicated().sum())
    clean = raw.drop_duplicates().copy()
    clean["duration_minutes"] = clean["duration_ms"] / 60000
    return (clean, raw_rows, exact_duplicates, invalid_rows, str(csv_path)), None


loaded, error = load_data()
if error:
    st.error(error)
    st.stop()

df, raw_record_count, duplicate_count, invalid_count, dataset_name = loaded
if df.empty:
    st.error("No valid records found in the dataset.")
    st.stop()

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------
st.sidebar.title("🎧 Music Analytics")
st.sidebar.markdown("### Dashboard Filters")
min_date, max_date = df["date"].min().date(), df["date"].max().date()
date_range = st.sidebar.date_input(
    "📅 Select Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date
)
selected_artists = st.sidebar.multiselect(
    "🎤 Select Artist", sorted(df["artist"].unique()), placeholder="Choose artist"
)

filtered = df.copy()
if isinstance(date_range, (tuple, list)):
    if len(date_range) == 2:
        filtered = filtered[filtered["date"].dt.date.between(date_range[0], date_range[1])]
    elif len(date_range) == 1:
        filtered = filtered[filtered["date"].dt.date == date_range[0]]
if selected_artists:
    filtered = filtered[filtered["artist"].isin(selected_artists)]
if filtered.empty:
    st.warning("No matching records. Please change your filters.")
    st.stop()

# --------------------------------------------------
# HEADER + KPIs
# --------------------------------------------------
st.markdown("""
<h1>🎧 US TOP 50</h1>
<h3 style="color:#D0B4F5 !important;">Music Analytics Dashboard</h3>
<p>Explore music trends, artist performance and chart rankings.</p>
""", unsafe_allow_html=True)

st.header("📊 Dashboard Overview")
metrics = [
    ("Total Records", f"{len(filtered):,}"),
    ("Unique Songs", f"{filtered['song'].nunique():,}"),
    ("Total Artists", f"{filtered['artist'].nunique():,}"),
    ("Avg Popularity", f"{filtered['popularity'].mean():.1f}" if filtered["popularity"].notna().any() else "N/A")
]
cols = st.columns(4)
for col, (label, value) in zip(cols, metrics):
    col.markdown(f'<div class="kpi"><p>{label}</p><h2>{value}</h2></div>', unsafe_allow_html=True)
st.caption(f"Showing {len(filtered):,} cleaned records from {filtered['date'].nunique():,} chart days. Filters apply to all sections below.")

# --------------------------------------------------
# AUTOMATIC INSIGHTS
# --------------------------------------------------
st.header("💡 Key Insights")
insight_cols = st.columns(3)
most_listed = filtered["artist"].value_counts()

song_presence = filtered.groupby(["song", "artist"], as_index=False).agg(
    chart_days=("date", "nunique"), avg_position=("position", "mean"), best_position=("position", "min")
)

pop_artist = filtered.dropna(subset=["popularity"]).groupby("artist")["popularity"].mean().sort_values(ascending=False)

insights = [
    ("Most Playlist Appearances", str(most_listed.index[0]) if not most_listed.empty else "N/A",
     f"↑ {int(most_listed.iloc[0]):,} records" if not most_listed.empty else "No artist data"),
    ("Longest Chart Presence", str(song_presence.sort_values(["chart_days", "best_position"], ascending=[False, True]).iloc[0]["song"]) if not song_presence.empty else "N/A",
     f"↑ {int(song_presence.sort_values(['chart_days', 'best_position'], ascending=[False, True]).iloc[0]['chart_days'])} chart days" if not song_presence.empty else "No song data"),
    ("Highest Avg. Artist Popularity", str(pop_artist.index[0]) if not pop_artist.empty else "N/A",
     f"↑ {pop_artist.iloc[0]:.1f} average" if not pop_artist.empty else "Popularity unavailable")
]

for col, (label, value, note) in zip(insight_cols, insights):
    with col:
        st.markdown(
            f'<div class="insight-card">'
            f'<p class="insight-label">{label}</p>'
            f'<p class="insight-value">{value}</p>'
            f'<span class="insight-note">{note}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

# --------------------------------------------------
# SELECTED ARTIST SONGS
# --------------------------------------------------
st.header("🎤 Selected Artist Songs")
if selected_artists:
    artist_songs = filtered[["artist", "song", "position", "date"]].drop_duplicates()
    artist_songs = artist_songs.sort_values(["artist", "position", "date"])
    artist_songs["date"] = artist_songs["date"].dt.strftime("%Y-%m-%d")
    st.dataframe(artist_songs, use_container_width=True, hide_index=True)
else:
    st.info("Select an artist from the sidebar to view their songs.")



# --------------------------------------------------
# MONTHLY CHART RANKING TRENDS - GROUPED BAR CHART
# --------------------------------------------------
st.header("📊 Monthly Chart Ranking Trends")

st.caption(
    "Compare the average chart position of multiple artists "
    "month by month. Each artist has a separate bar."
)

# Calculate monthly average position for each artist
monthly_artist = (
    filtered.groupby([
        pd.Grouper(key="date", freq="MS"),
        "artist"
    ])
    .agg(
        Average_Position=("position", "mean"),
        Total_Records=("position", "count")
    )
    .reset_index()
)

if not monthly_artist.empty:

    monthly_artist["Month"] = monthly_artist["date"].dt.strftime("%b %Y")

    artist_colors = [
        "#B58AE8", "#FF6384", "#36CFC9",
        "#FFC857", "#5DA9E9", "#A8D672",
        "#FF9966", "#C792EA"
    ]

    fig = px.bar(
        monthly_artist,
        x="Month",
        y="Average_Position",
        color="artist",
        barmode="group",
        text=monthly_artist["Average_Position"].round(1),
        hover_data=["Total_Records"],
        title="Artist-wise Monthly Average Chart Position",
        labels={
            "Month": "Month",
            "Average_Position": "Average Chart Position",
            "artist": "Artist",
            "Total_Records": "Total Song Records"
        },
        color_discrete_sequence=artist_colors,
        category_orders={
            "Month": monthly_artist["Month"].drop_duplicates().tolist(),
            "artist": selected_artists if selected_artists else
                      sorted(monthly_artist["artist"].unique())
        }
    )

    fig.update_traces(
        textposition="outside",
        cliponaxis=False
    )

    fig.update_layout(
        barmode="group",
        bargap=0.25,
        bargroupgap=0.12,
        xaxis_title="Month",
        yaxis_title="Average Chart Position",
        yaxis=dict(
            rangemode="tozero",
            gridcolor="#493064"
        ),
        legend_title="Selected Artists"
    )

    st.plotly_chart(
        chart_style(fig, 480),
        use_container_width=True
    )

else:
    st.info("No chart records available.")


# --------------------------------------------------
# INDIVIDUAL SONG RANKING MOVEMENT
# --------------------------------------------------
st.header("🔄 Song Ranking Changes Over Time")
st.caption("Choose one song to see how its chart position changed across the selected dates. A lower position number means a better rank.")
song_options = filtered[["song", "artist"]].drop_duplicates().sort_values(["song", "artist"])
song_options["label"] = song_options["song"] + " — " + song_options["artist"]
selected_song_label = st.selectbox("Choose a song to track", song_options["label"].tolist(), key="ranking_song")
selected_song_row = song_options[song_options["label"] == selected_song_label].iloc[0]
song_trend = filtered[(filtered["song"] == selected_song_row["song"]) & (filtered["artist"] == selected_song_row["artist"])].sort_values("date")
if not song_trend.empty:
    fig = px.line(song_trend, x="date", y="position", markers=True,
                  title=f"Ranking History: {selected_song_row['song']}",
                  labels={"date": "Chart Date", "position": "Chart Position"}, hover_data=["artist"])
    fig.update_yaxes(autorange="reversed", dtick=5)
    fig.update_xaxes(tickformat="%b %Y", tickangle=-35, nticks=10)
    st.plotly_chart(chart_style(fig), use_container_width=True)
    first_rank = int(song_trend.iloc[0]["position"])
    latest_rank = int(song_trend.iloc[-1]["position"])
    change = first_rank - latest_rank
    if change > 0:
        st.success(f"This song improved by {change} position(s) between its first and latest displayed chart dates.")
    elif change < 0:
        st.info(f"This song moved down by {abs(change)} position(s) between its first and latest displayed chart dates.")
    else:
        st.info("This song has the same position on its first and latest displayed chart dates.")

# --------------------------------------------------
# TOP ARTISTS
# --------------------------------------------------
st.header("🎵 Top 10 Artists by Playlist Appearances")
st.caption("This bar chart ranks the 10 artists with the most chart entries in the filtered data. Longer bars mean more appearances.")
top_artists = filtered["artist"].value_counts().head(10).rename_axis("Artist").reset_index(name="Appearances")
fig = px.bar(top_artists.sort_values("Appearances"), x="Appearances", y="Artist", orientation="h",
             text="Appearances", color="Artist", title="Artists with the Most Playlist Records",
             color_discrete_sequence=COLORS, labels={"Appearances": "Playlist Appearances"})
fig.update_traces(textposition="outside", cliponaxis=False)
st.plotly_chart(chart_style(fig, 470), use_container_width=True)

# --------------------------------------------------
# LONGEST CHART PRESENCE
# --------------------------------------------------
st.header("🏆 Songs with the Longest Chart Presence")
st.caption("This chart shows the 10 songs that appeared on the chart on the greatest number of distinct days. Longer bars mean more chart days.")
longest_songs = filtered.groupby(["song", "artist"], as_index=False).agg(
    **{"Chart Days": ("date", "nunique"), "Best Position": ("position", "min"), "Average Position": ("position", "mean")}
).sort_values(["Chart Days", "Best Position"], ascending=[False, True]).head(10)
fig = px.bar(longest_songs.sort_values("Chart Days"), x="Chart Days", y="song", orientation="h", color="artist",
             hover_data=["Best Position", "Average Position"], title="Top 10 Songs by Number of Distinct Chart Days",
             labels={"song": "Song", "Chart Days": "Distinct Chart Days", "artist": "Artist"})
st.plotly_chart(chart_style(fig, 470), use_container_width=True)
st.dataframe(longest_songs, use_container_width=True, hide_index=True)

# --------------------------------------------------
# ARTIST-WISE POPULARITY COMPARISON
# --------------------------------------------------
st.header("⭐ Artist-wise Popularity Comparison")
st.caption("Compare the average popularity score of artists. Higher bars indicate a higher average popularity score.")
artist_popularity = filtered.dropna(subset=["popularity"]).groupby("artist", as_index=False).agg(
    **{"Average Popularity": ("popularity", "mean"), "Songs/Records": ("song", "count"), "Unique Songs": ("song", "nunique")}
).sort_values("Average Popularity", ascending=False).head(15)
if not artist_popularity.empty:
    fig = px.bar(artist_popularity.sort_values("Average Popularity"), x="Average Popularity", y="artist", orientation="h",
                 color="Average Popularity", color_continuous_scale=["#65418A", "#D0B4F5"],
                 hover_data=["Songs/Records", "Unique Songs"], title="Top 15 Artists by Average Song Popularity",
                 labels={"artist": "Artist", "Average Popularity": "Average Popularity"})
    st.plotly_chart(chart_style(fig, 520), use_container_width=True)
    st.dataframe(artist_popularity, use_container_width=True, hide_index=True)
else:
    st.info("Popularity data unavailable for the selected filters.")


# --------------------------------------------------
# ARTIST POPULARITY COMPARISON - BAR CHART
# --------------------------------------------------
st.header("⭐ Artist Popularity Comparison")

st.caption(
    "Compare the average popularity scores of selected artists. "
    "Higher values indicate higher average popularity."
)

popularity_data = (
    filtered.dropna(subset=["popularity"])
    .groupby("artist", as_index=False)
    .agg(
        Average_Popularity=("popularity", "mean"),
        Total_Records=("popularity", "count"),
        Unique_Songs=("song", "nunique")
    )
    .sort_values("Average_Popularity", ascending=True)
)

if not popularity_data.empty:

    fig = px.bar(
        popularity_data,
        x="Average_Popularity",
        y="artist",
        orientation="h",
        color="artist",
        text=popularity_data["Average_Popularity"].round(1),
        hover_data=["Total_Records", "Unique_Songs"],
        title="Average Song Popularity by Artist",
        labels={
            "artist": "Artist",
            "Average_Popularity": "Average Popularity",
            "Total_Records": "Total Records",
            "Unique_Songs": "Unique Songs"
        },
        color_discrete_sequence=[
            "#B58AE8", "#FF6384", "#36CFC9",
            "#FFC857", "#5DA9E9", "#A8D672"
        ]
    )

    fig.update_traces(
        textposition="outside",
        cliponaxis=False
    )

    fig.update_layout(
        showlegend=False,
        xaxis_title="Average Popularity Score",
        yaxis_title="Artist",
        xaxis=dict(
            range=[0, 100],
            gridcolor="#493064"
        )
    )

    st.plotly_chart(
        chart_style(fig, 420),
        use_container_width=True
    )

else:
    st.info("Popularity data is unavailable.")


# --------------------------------------------------
# EXPLICIT CONTENT
# --------------------------------------------------
st.header("🔞 Explicit Content Analysis")
st.caption("This chart compares the number of explicit, non-explicit and unknown song records.")
explicit_map = {True: "Explicit", False: "Non-Explicit", "true": "Explicit", "false": "Non-Explicit", "1": "Explicit", "0": "Non-Explicit", "yes": "Explicit", "no": "Non-Explicit"}
explicit_values = filtered["is_explicit"].map(lambda x: explicit_map.get(x, explicit_map.get(str(x).strip().lower(), "Unknown")))
explicit_counts = explicit_values.value_counts().reset_index()
explicit_counts.columns = ["Content Type", "Records"]
if not explicit_counts.empty:
    fig = px.pie(explicit_counts, names="Content Type", values="Records", hole=0.5,
                 color_discrete_sequence=COLORS, title="Explicit vs Non-Explicit Records")
    st.plotly_chart(chart_style(fig), use_container_width=True)
else:
    st.info("Explicit content data unavailable.")

# --------------------------------------------------
# ALBUM TYPE
# --------------------------------------------------
st.header("💿 Album Type Analysis")
st.caption("This chart shows how many records belong to each album type, such as album, single or compilation (depending on the dataset).")
album = filtered.dropna(subset=["album_type"])
if not album.empty:
    counts = album["album_type"].astype(str).value_counts().rename_axis("Album Type").reset_index(name="Count")
    fig = px.bar(counts, x="Album Type", y="Count", text="Count", color="Album Type",
                 color_discrete_sequence=COLORS, title="Records by Album Type")
    st.plotly_chart(chart_style(fig), use_container_width=True)
else:
    st.info("Album type data unavailable.")

# --------------------------------------------------
# SONG DURATION
# --------------------------------------------------
st.header("⏱️ Song Duration Analysis")
st.caption("This histogram groups songs by their duration. Taller bars mean more song records fall within that duration range.")
duration = filtered.dropna(subset=["duration_minutes"])
if not duration.empty:
    fig = px.histogram(duration, x="duration_minutes", nbins=25, title="Distribution of Song Durations",
                       labels={"duration_minutes": "Duration (minutes)", "count": "Number of Records"},
                       color_discrete_sequence=["#B58AE8"])
    st.plotly_chart(chart_style(fig), use_container_width=True)
else:
    st.info("Song duration data unavailable.")

# --------------------------------------------------
# DATA QUALITY CHECK
# --------------------------------------------------
st.header("🔎 Data Validation")
with st.expander("View dataset quality checks"):
    quality = pd.DataFrame({
        "Check": ["Rows in original CSV", "Exact duplicate rows removed", "Invalid date/position rows removed", "Clean records available", "Unique songs", "Unique artists", "Distinct chart days", "Missing popularity values"],
        "Result": [raw_record_count, duplicate_count, invalid_count, len(df), df["song"].nunique(), df["artist"].nunique(), df["date"].nunique(), int(df["popularity"].isna().sum())]
    })
    st.dataframe(quality, use_container_width=True, hide_index=True)
    st.caption(f"Dataset: {dataset_name}. Exact duplicate rows are removed once before dashboard calculations. Records with invalid date or position are excluded.")

# --------------------------------------------------
# COMPLETE DATASET + DOWNLOAD
# --------------------------------------------------
st.header("📋 Complete Music Dataset")
st.dataframe(filtered.sort_values(["date", "position"], ascending=[False, True]), use_container_width=True, hide_index=True)
st.download_button("⬇️ Download Filtered Dataset", data=filtered.to_csv(index=False).encode("utf-8"),
                   file_name="US_Top_50_Filtered.csv", mime="text/csv")

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align:center;padding:15px;">
<h3 style="color:#D0B4F5 !important;">🎧 US TOP 50 | MUSIC ANALYTICS</h3>
<p>Built with Python • Streamlit • Pandas • Plotly</p>
</div>
""", unsafe_allow_html=True)
