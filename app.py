import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.colors import sample_colorscale
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="IMDb Movie Universe",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = "IMDb_Dashboard_Data.csv"

# ---------- Dashboard styling ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Poppins:wght@500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp {
    background:
        radial-gradient(circle at 88% 4%, rgba(128, 90, 213, .16), transparent 26%),
        radial-gradient(circle at 8% 92%, rgba(59, 130, 246, .10), transparent 28%),
        linear-gradient(135deg, #f7f5ff 0%, #ffffff 48%, #f4f7ff 100%);
}
.block-container { padding-top: 1.4rem; padding-bottom: 2rem; max-width: 1500px; }

.hero {
    padding: 26px 30px;
    border-radius: 26px;
    background: linear-gradient(135deg, rgba(255,255,255,.93), rgba(241,238,255,.88));
    border: 1px solid rgba(111, 78, 190, .12);
    box-shadow: 0 18px 45px rgba(53, 37, 103, .10);
    margin-bottom: 18px;
}
.hero h1 { margin: 0; font-family: 'Poppins', sans-serif; font-size: 38px; color: #252046; }
.hero p { margin: 7px 0 0; color: #6d6787; font-size: 15px; }
.badge { display:inline-block; padding: 6px 11px; border-radius: 999px; background:#eee9ff; color:#6841c6; font-size:12px; font-weight:700; margin-bottom:10px; }

.kpi {
    background: rgba(255,255,255,.84);
    border: 1px solid rgba(106, 82, 175, .12);
    border-radius: 20px;
    padding: 18px 19px;
    box-shadow: 0 10px 30px rgba(60, 45, 110, .08);
    min-height: 106px;
}
.kpi .label { color:#7a7493; font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:.7px; }
.kpi .value { color:#29234c; font-family:'Poppins',sans-serif; font-size:28px; font-weight:800; margin-top:5px; }
.kpi .sub { color:#9b95b0; font-size:11px; margin-top:2px; }

.section-title { font-family:'Poppins',sans-serif; font-size:22px; font-weight:800; color:#2b254e; margin:18px 0 8px; }
.section-note { color:#7c7694; font-size:13px; margin-bottom:10px; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #17152f 0%, #211a46 55%, #17152f 100%);
}
[data-testid="stSidebar"] * { color: #f2efff !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stSlider label { color:#cfc8ed !important; font-weight:600; }

div[data-testid="stTabs"] button { font-weight:700; }
div[data-testid="stTabs"] button[aria-selected="true"] { color:#6d43ce; }

.footer { text-align:center; color:#9b96ad; font-size:11px; padding:18px 0 4px; }
</style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_data():
    df = pd.read_csv(DATA_PATH)
    numeric_cols = [
        "startYear", "runtimeMinutes", "movieAge", "isSciFi",
        "genreCount", "creditCount", "averageRating", "numVotes"
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["startYear"] = df["startYear"].round().astype("Int64")
    return df


df = load_data()

# ---------- Sidebar filters ----------
st.sidebar.markdown("## 🎬 IMDb Universe")
st.sidebar.markdown("---")

valid_years = df["startYear"].dropna().astype(int)
ymin, ymax = int(valid_years.min()), int(valid_years.max())
year_range = st.sidebar.slider("Release Year", ymin, ymax, (ymin, ymax))

all_genres = sorted({g.strip() for s in df["genres"].dropna() for g in str(s).split(",") if g.strip()})
genre_filter = st.sidebar.multiselect("Genres", all_genres, default=[])

sci_choice = st.sidebar.selectbox("Sci-Fi", ["All Movies", "Sci-Fi Only", "Non-Sci-Fi Only"])

runtime_valid = df["runtimeMinutes"].dropna()
rt_min = int(max(1, np.floor(runtime_valid.min())))
rt_max = int(np.ceil(runtime_valid.max()))
runtime_range = st.sidebar.slider("Runtime (minutes)", rt_min, min(rt_max, 400), (rt_min, min(rt_max, 400)))

if st.sidebar.button("Reset Filters", use_container_width=True):
    st.rerun()

# Apply filters without changing the underlying graph definitions.
filtered = df[
    df["startYear"].between(year_range[0], year_range[1], inclusive="both") &
    df["runtimeMinutes"].fillna(-1).between(runtime_range[0], runtime_range[1], inclusive="both")
].copy()

if genre_filter:
    pattern = "|".join([f"(?<![A-Za-z]){g}(?![A-Za-z])" for g in genre_filter])
    filtered = filtered[filtered["genres"].fillna("").str.contains(pattern, regex=True, na=False)]

if sci_choice == "Sci-Fi Only":
    filtered = filtered[filtered["isSciFi"] == 1]
elif sci_choice == "Non-Sci-Fi Only":
    filtered = filtered[filtered["isSciFi"] == 0]


def graph_note(title, line1, line2):
    st.markdown(f"**{title}**\n\n{line1}  \n{line2}")


# ---------- Exact notebook graph functions ----------
def rating_distribution(data):
    fig = px.histogram(
        data, x="averageRating", nbins=20, marginal="box",
        title="IMDb Rating Distribution of Movies (1990–2024)",
        color_discrete_sequence=["#4622e6"]
    )
    fig.update_layout(template="plotly_dark", xaxis_title="IMDb Rating", yaxis_title="Number of Movies", hoverlabel=dict(font_size=13))
    fig.update_traces(hovertemplate="IMDb Rating: %{x}<br>Number of Movies: %{y}<extra></extra>")
    return fig


def rating_distribution_bars(data):
    counts, bins = np.histogram(data["averageRating"].dropna(), bins=20)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=bins[:-1], y=counts, width=np.diff(bins),
        marker=dict(color=counts, colorscale="Turbo", showscale=True),
        hovertemplate="IMDb Rating: %{x:.1f}<br>Number of Movies: %{y}<extra></extra>"
    ))
    fig.update_layout(title="IMDb Rating Distribution of Movies (1990–2024)", template="plotly_white", xaxis_title="IMDb Rating", yaxis_title="Number of Movies")
    return fig


def genre_violin(data):
    genreData = data[["genres", "averageRating"]].dropna().copy()
    genreData = genreData.assign(genres=genreData["genres"].str.split(",")).explode("genres")
    genreData["genres"] = genreData["genres"].str.strip()
    fig = px.violin(
        genreData, x="genres", y="averageRating", box=True, points=False,
        color="genres", color_discrete_sequence=px.colors.sequential.Plasma,
        title="IMDb Rating Distribution by Genre (1990–2024)"
    )
    fig.update_layout(template="plotly_dark", xaxis_title="Movie Genre", yaxis_title="IMDb Rating", showlegend=False)
    return fig


def vote_age_rating_3d(data):
    sampleData = data.sample(min(8000, len(data)), random_state=42)
    fig = px.scatter_3d(
        sampleData, x="movieAge", y="numVotes", z="averageRating",
        color="averageRating", hover_name="primaryTitle",
        title="Movie Age, Votes and IMDb Rating (1990–2024)", color_continuous_scale="Plasma"
    )
    fig.update_layout(template="plotly_dark", scene=dict(xaxis_title="Movie Age", yaxis_title="Number of Votes", zaxis_title="IMDb Rating"))
    return fig


def genre_popularity(data):
    g = data[["startYear", "genres"]].dropna().copy()
    g["genres"] = g["genres"].str.split(",")
    g = g.explode("genres")
    g["genres"] = g["genres"].str.strip()
    g = g.groupby(["startYear", "genres"]).size().reset_index(name="movieCount")
    top = g["genres"].value_counts().head(10).index
    g = g[g["genres"].isin(top)]
    colors = ["#32105E","#4B3976","#5E5885","#706D91","#80809A","#92919F","#A3A2AA","#B2B1B8","#C0BFC4","#CBC9CD"]
    years = sorted(g["startYear"].unique())
    if not years:
        return go.Figure().update_layout(title="Genre Popularity Across Years (1990–2024)")
    frames = []
    for year in years:
        d = g[g["startYear"] == year].sort_values("movieCount", ascending=False).head(10).copy()
        d["rank"] = range(1, len(d) + 1)
        frames.append(go.Frame(name=str(int(year)), data=[go.Bar(
            x=d["movieCount"], y=d["rank"], orientation="h", text=d["genres"], textposition="inside",
            marker=dict(color=colors[:len(d)], line=dict(width=1)), hovertemplate="<b>%{text}</b><br>Movies: %{x}<extra></extra>"
        )]))
    d = g[g["startYear"] == years[0]].sort_values("movieCount", ascending=False).head(10).copy()
    d["rank"] = range(1, len(d) + 1)
    fig = go.Figure(data=[go.Bar(
        x=d["movieCount"], y=d["rank"], orientation="h", text=d["genres"], textposition="inside",
        marker=dict(color=colors[:len(d)], line=dict(width=1)), hovertemplate="<b>%{text}</b><br>Movies: %{x}<extra></extra>"
    )], frames=frames)
    steps = [dict(method="animate", args=[[str(int(y))], {"mode":"immediate", "frame":{"duration":1600,"redraw":True}, "transition":{"duration":700}}], label=str(int(y))) for y in years]
    fig.update_layout(
        title="Genre Popularity Across Years (1990–2024)", template="plotly_white",
        xaxis_title="Number of Movies", yaxis_title="Genre Rank",
        yaxis=dict(tickvals=list(range(1,11)), autorange="reversed"), margin=dict(l=100, r=40, t=80, b=150),
        updatemenus=[dict(type="buttons", bgcolor="#AAA0B8", font=dict(color="#211C25"), x=0.02, y=-0.20,
            buttons=[dict(label="▶ Play", method="animate", args=[None, {"fromcurrent":True, "frame":{"duration":1600,"redraw":True}, "transition":{"duration":700}}]),
                     dict(label="⏸ Pause", method="animate", args=[[None], {"mode":"immediate", "frame":{"duration":0,"redraw":False}, "transition":{"duration":0}}])])],
        sliders=[dict(active=0, x=0.20, y=-0.20, len=0.75, currentvalue={"prefix":"Year: "}, steps=steps)]
    )
    return fig


def runtime_heatmap(data):
    runtimeData = data.dropna(subset=["runtimeMinutes"])
    fig = px.density_heatmap(
        runtimeData, x="runtimeMinutes", y="averageRating", nbinsx=40, nbinsy=20,
        color_continuous_scale="Plasma", title="Runtime vs IMDb Rating (1990–2024)"
    )
    fig.update_layout(template="plotly_dark", xaxis_title="Runtime (Minutes)", yaxis_title="IMDb Rating")
    return fig


def rating_bloom(data):
    INK, MUTED, GRID = "#1E1B3A", "#6B6494", "#DDD6F0"
    GOLD, PINK = "#D98E04", "#D6246E"
    SCALE = [[0, "#4C1D95"], [0.3, "#A21CAF"], [0.6, "#E11D48"], [0.85, "#F97316"], [1, "#EAB308"]]
    FONT = "Segoe UI, Poppins, Arial"
    N = 15
    top = (data[data["numVotes"] >= 50000].sort_values(["averageRating", "numVotes"], ascending=False).head(N).reset_index(drop=True))
    if top.empty:
        return go.Figure().update_layout(title="THE RATING BLOOM")
    N = len(top)
    top["rank"] = np.arange(1, N + 1)
    lo, hi = top["averageRating"].min(), top["averageRating"].max()
    top["color"] = sample_colorscale(SCALE, ((top["averageRating"] - lo) / max(hi - lo, 1e-9)).tolist())
    W, H, R, HOLE = 1300, 980, 255, 0.24
    CX, CY = 0.5, 0.45
    step = 360 / N
    theta = top["rank"].sub(1) * step
    rmin, rmax = round(lo - 0.35, 2), round(hi + 0.06, 2)
    def spot(deg, radius_px):
        a = np.radians(90 - deg)
        return CX + radius_px / W * np.cos(a), CY + radius_px / H * np.sin(a)
    def px_radius(rating):
        return R * (HOLE + (1 - HOLE) * (rating - rmin) / (rmax - rmin))
    fig = go.Figure()
    fig.add_trace(go.Barpolar(r=top["averageRating"] + 0.05, theta=theta, width=step, marker=dict(color=top["color"], opacity=0.22, line=dict(width=0)), hoverinfo="skip"))
    fig.add_trace(go.Barpolar(
        r=top["averageRating"], theta=theta, width=step * 0.86,
        marker=dict(color=top["averageRating"], colorscale=SCALE, cmin=lo, cmax=hi, line=dict(color="white", width=2.5),
                    colorbar=dict(title=dict(text="<b>⭐ IMDb Rating</b>", font=dict(size=13, color=GOLD), side="top"), orientation="h", x=0.5, y=0.06, len=0.36, thickness=14, tickformat=".1f", tickfont=dict(size=12, color=INK), ticks="outside", tickcolor=MUTED, outlinecolor=GRID, bgcolor="rgba(0,0,0,0)")),
        customdata=np.c_[top["primaryTitle"], top["numVotes"], top["startYear"], top["genres"], top["rank"]],
        hovertemplate="<b style='font-size:15px'>#%{customdata[4]} · %{customdata[0]}</b><br>📅 %{customdata[2]:.0f}<br>⭐ IMDb Rating: <b>%{r:.1f}</b><br>🗳️ Votes: %{customdata[1]:,}<br>🎭 %{customdata[3]}<extra></extra>"
    ))
    for (_, m), deg in zip(top.iterrows(), theta):
        x, y = spot(deg, R + 24)
        c = np.cos(np.radians(90 - deg))
        fig.add_annotation(x=x, y=y, xref="paper", yref="paper", showarrow=False,
            xanchor="left" if c > 0.2 else "right" if c < -0.2 else "center",
            yanchor="bottom" if deg < 20 or deg > 340 else "top" if 160 < deg < 200 else "middle",
            align="left" if c > 0.2 else "right" if c < -0.2 else "center",
            text=(f"<span style='color:{m['color']}'><b>#{m['rank']}</b></span>  <span style='color:{INK}'><b>{m['primaryTitle']}</b></span><br>"
                  f"<span style='color:{m['color']}' >★ {m['averageRating']:.1f}</span><span style='color:{MUTED}'>  ·  {int(m['startYear'])}</span>"), font=dict(size=13, family=FONT))
    for v in np.arange(np.ceil(rmin * 5) / 5, hi + 0.001, 0.2):
        x, y = spot(-step / 2, px_radius(v))
        fig.add_annotation(x=x, y=y, xref="paper", yref="paper", text=f"<b>{v:.1f}</b>", showarrow=False, font=dict(size=10, color=MUTED), bgcolor="rgba(255,255,255,.85)", borderpad=1)
    fig.add_annotation(x=CX, y=CY, xref="paper", yref="paper", showarrow=False, align="center", text=f"<span style='font-size:30px'>🏆</span><br><b style='color:{GOLD}'>TOP {N}</b>", font=dict(size=14, family=FONT))
    fig.add_annotation(x=0.5, y=0.985, xref="paper", yref="paper", showarrow=False, yanchor="top", align="center", text=f"<span style='color:{PINK}'><b>THE</b></span> <span style='color:{GOLD}'><b>RATING BLOOM</b></span><br><span style='font-size:15px;color:{MUTED}'>The {N} highest-rated movies of 1990–2024 (50,000+ votes) · longer petal = higher rating · best movie at 12 o'clock, ranks run clockwise</span>", font=dict(size=34, family=FONT))
    fig.update_layout(
        width=W, height=H, margin=dict(l=0, r=0, t=0, b=0), showlegend=False,
        template="plotly_white", paper_bgcolor="white",
        font=dict(family=FONT, color=INK),
        polar=dict(
            bgcolor="#FAF8FF", hole=HOLE,
            domain=dict(x=[CX - R / W, CX + R / W], y=[CY - R / H, CY + R / H]),
            radialaxis=dict(
                range=[rmin, rmax],
                tickvals=np.arange(np.ceil(rmin * 5) / 5, hi + 0.001, 0.2),
                showticklabels=False, gridcolor=GRID, linecolor="rgba(0,0,0,0)"
            ),
            angularaxis=dict(rotation=90, direction="clockwise", showticklabels=False, showgrid=False, showline=False)
        ),
        hoverlabel=dict(bgcolor="white", bordercolor=PINK, font=dict(size=13, color=INK))
    )
    return fig


def rating_surface(data):
    data = data.dropna(subset=["startYear", "runtimeMinutes", "averageRating"]).copy()
    data["runtimeGroup"] = (data["runtimeMinutes"] // 10) * 10
    ratingData = data.groupby(["startYear", "runtimeGroup"])["averageRating"].mean().reset_index()
    surface = ratingData.pivot(index="runtimeGroup", columns="startYear", values="averageRating")
    fig = go.Figure(go.Surface(
        x=surface.columns, y=surface.index, z=surface.values,
        colorscale=[[0,"#24104F"],[0.25,"#5B2C83"],[0.5,"#9B4DCA"],[0.75,"#E26D9B"],[1,"#FFD166"]],
        colorbar=dict(title="IMDb Rating"),
        hovertemplate="Release Year: %{x}<br>Runtime: %{y} min<br>Average Rating: %{z:.2f}<extra></extra>"
    ))
    fig.update_layout(title=dict(text="IMDb Rating Landscape — Release Year × Runtime (1990–2024)", font=dict(size=24, color="#F5E9FF")), paper_bgcolor="#243447", plot_bgcolor="#243447", font=dict(color="#F5E9FF"), height=750,
        scene=dict(bgcolor="#31475C", xaxis=dict(title="🎬 Release Year", gridcolor="#71859A"), yaxis=dict(title="⏱ Runtime (Minutes)", gridcolor="#71859A"), zaxis=dict(title="⭐ Average IMDb Rating", gridcolor="#71859A"), camera=dict(eye=dict(x=1.6,y=1.6,z=1.2))), margin=dict(l=20,r=20,t=90,b=20))
    return fig


def characteristics_comparison(data):
    FONT="Poppins, Segoe UI, Arial, sans-serif"; INK="#2B2D42"; SOFT="#5C6378"; GRID="#E3DCCB"; PAPER="#FBF7EF"; PANEL="#FFFFFF"
    data=data.dropna(subset=["runtimeMinutes","averageRating","numVotes","movieAge"]).copy()
    data["logVotes"]=np.log10(data["numVotes"]+1)
    bubbleData=data.sort_values("numVotes",ascending=False).head(3000)
    heatData=data[["runtimeMinutes","movieAge","averageRating","logVotes"]].corr()
    data["ratingGroup"]=pd.cut(data["averageRating"],bins=[0,6,8,10],labels=["Low","Medium","High"])
    profile=data.groupby("ratingGroup",observed=True)[["runtimeMinutes","movieAge","logVotes","averageRating"]].mean()
    profile=((profile-profile.min())/(profile.max()-profile.min()))*100
    fig=make_subplots(rows=1,cols=3,column_widths=[0.36,0.32,0.32],horizontal_spacing=0.09,specs=[[{"type":"xy"},{"type":"xy"},{"type":"polar"}]],subplot_titles=["Runtime vs IMDb Rating","Characteristic Correlation","Rating Group Profiles"])
    fig.add_trace(go.Scatter(x=bubbleData["runtimeMinutes"],y=bubbleData["averageRating"],mode="markers",showlegend=False,marker=dict(size=7,color=bubbleData["movieAge"],colorscale="Sunsetdark",opacity=0.8,line=dict(color="#FFFFFF",width=0.6),colorbar=dict(title=dict(text="Movie Age (years)",font=dict(size=11)),orientation="h",thickness=10,len=0.28,x=0.11,y=-0.2,tickfont=dict(size=10,color=SOFT))),text=bubbleData["primaryTitle"],hovertemplate="<b>%{text}</b><br>Runtime: %{x:.0f} min<br>IMDb Rating: %{y:.1f}<extra></extra>"),row=1,col=1)
    heatLabels=["Runtime","Movie Age","IMDb Rating","Log Votes"]
    fig.add_trace(go.Heatmap(z=heatData.values,x=heatLabels,y=heatLabels,colorscale=[[0.0,"#E76F51"],[0.5,"#FBF7EF"],[1.0,"#159A9C"]],zmin=-1,zmax=1,showscale=False,xgap=4,ygap=4,text=np.round(heatData.values,2),texttemplate="%{text:.2f}",textfont=dict(size=13,color=INK),hovertemplate="%{y} × %{x}<br>Correlation: %{z:.2f}<extra></extra>"),row=1,col=2)
    labels=["Runtime","Movie Age","Log Votes","IMDb Rating"]
    radarColors={"Low":"#E76F51","Medium":"#7B61A8","High":"#159A9C"}
    for group in profile.index:
        values=profile.loc[group,["runtimeMinutes","movieAge","logVotes","averageRating"]].tolist(); values.append(values[0])
        fig.add_trace(go.Scatterpolar(r=values,theta=labels+[labels[0]],mode="lines+markers",fill="toself",opacity=0.65,name=f"{group} Rating",line=dict(color=radarColors[str(group)],width=3),marker=dict(size=7,color=radarColors[str(group)]),hovertemplate="<b>"+str(group)+" Rating</b><br>%{theta}: %{r:.1f}<extra></extra>"),row=1,col=3)
    fig.update_layout(title=dict(text="✦ Movie Characteristics Comparison — IMDb 1990–2024 ✦",x=0.5,xanchor="center",font=dict(size=26,color=INK,family=FONT)),paper_bgcolor=PAPER,plot_bgcolor=PANEL,font=dict(family=FONT,color=INK,size=12),height=720,margin=dict(l=70,r=70,t=110,b=110),legend=dict(orientation="h",x=0.85,xanchor="center",y=-0.08,bgcolor="rgba(0,0,0,0)",font=dict(size=12,color=INK)))
    fig.update_annotations(font=dict(size=16,color=INK,family=FONT))
    fig.update_xaxes(title_font=dict(size=13,color=INK),title_standoff=14,tickfont=dict(size=11,color=SOFT),showline=True,linecolor=GRID,zeroline=False)
    fig.update_yaxes(title_font=dict(size=13,color=INK),title_standoff=14,tickfont=dict(size=11,color=SOFT),showline=True,linecolor=GRID,zeroline=False)
    fig.update_xaxes(title_text="Runtime (Minutes)",gridcolor=GRID,row=1,col=1); fig.update_yaxes(title_text="IMDb Rating",range=[4,10],gridcolor=GRID,row=1,col=1)
    fig.update_xaxes(title_text="Movie Characteristics",showgrid=False,row=1,col=2); fig.update_yaxes(title_text="Movie Characteristics",showgrid=False,autorange="reversed",row=1,col=2)
    fig.update_polars(bgcolor=PANEL,domain=dict(x=[0.73,0.96]),radialaxis=dict(range=[0,100],showticklabels=False,gridcolor=GRID),angularaxis=dict(gridcolor=GRID,tickfont=dict(size=12,color=INK,family=FONT)))
    return fig


def scifi_treemap(data):
    sciFi=data[data["isSciFi"]==1].copy()
    sciFi["ratingGroup"]=pd.cut(sciFi["averageRating"],bins=[0,6,8,10],labels=["Low Rating","Medium Rating","High Rating"])
    sciFiData=sciFi.groupby(["ratingGroup","genres"],observed=True).size().reset_index(name="movieCount")
    fig=px.treemap(sciFiData,path=["ratingGroup","genres"],values="movieCount",color="movieCount",color_continuous_scale="Plasma",title="Sci-Fi Movies by Rating Category (1990–2024)")
    fig.update_layout(paper_bgcolor="#F5F1E8",plot_bgcolor="#EAF1F5",font=dict(color="#26364A"),title_font_size=24)
    return fig


# ---------- Header ----------
st.markdown(f"""
<div class="hero">
  <div class="badge">FOUNDATION OF DATA SCIENCE • IMDb 1990–2024</div>
  <h1>IMDb Movie Universe</h1>
</div>
""", unsafe_allow_html=True)

# ---------- KPI cards ----------
cols = st.columns(5)
metrics = [
    ("Movies", f"{len(filtered):,}", "filtered movies"),
    ("Avg Rating", f"{filtered['averageRating'].mean():.2f}" if len(filtered) else "—", "IMDb average"),
    ("IMDb Votes", f"{filtered['numVotes'].sum():,.0f}" if len(filtered) else "—", "total votes"),
    ("Sci-Fi", f"{int(filtered['isSciFi'].sum()):,}" if len(filtered) else "—", "Sci-Fi movies"),
    ("Median Runtime", f"{filtered['runtimeMinutes'].median():.0f} min" if len(filtered) else "—", "movie runtime"),
]
for col, (label, value, sub) in zip(cols, metrics):
    with col:
        st.markdown(f'<div class="kpi"><div class="label">{label}</div><div class="value">{value}</div><div class="sub">{sub}</div></div>', unsafe_allow_html=True)


# ---------- Dashboard pages ----------
tabs = st.tabs(["🏠 Overview", "⭐ Ratings", "🎭 Genres", "🔎 Relationships", "🏆 Top Movies", "🌌 Advanced", "🚀 Sci-Fi"])

with tabs[0]:
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(rating_distribution(filtered), use_container_width=True, config={"displaylogo":False}, key="overview_rating_distribution")
        graph_note("Rating Distribution", "Shows how IMDb ratings are distributed across the selected movies.", "The tallest bars indicate the rating range containing the largest number of movies.")
    with c2:
        st.plotly_chart(genre_violin(filtered), use_container_width=True, config={"displaylogo":False}, key="overview_genre_violin")
        graph_note("Genre Ratings", "Compares the spread of IMDb ratings across movie genres.", "The center and width of each violin show where ratings are concentrated and how widely they vary.")
    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(runtime_heatmap(filtered), use_container_width=True, config={"displaylogo":False}, key="overview_runtime_heatmap")
        graph_note("Runtime vs Rating", "Shows where runtime and IMDb rating combinations occur most often.", "Brighter regions represent combinations with more movies in the selected data.")
    with c4:
        st.plotly_chart(vote_age_rating_3d(filtered), use_container_width=True, config={"displaylogo":False}, key="overview_vote_age_3d")
        graph_note("Movie Age, Votes & Rating", "Connects movie age, IMDb vote count and rating in three dimensions.", "Point color represents IMDb rating, while position shows age and number of votes.")

with tabs[1]:
    st.plotly_chart(rating_distribution(filtered), use_container_width=True, config={"displaylogo":False}, key="ratings_histogram")
    graph_note("Rating Distribution", "Shows how IMDb ratings are distributed across the selected movies.", "The tallest bars indicate the rating range containing the largest number of movies.")
    st.plotly_chart(rating_distribution_bars(filtered), use_container_width=True, config={"displaylogo":False}, key="ratings_bars")
    graph_note("Rating Distribution by Bins", "Shows the number of movies within each IMDb rating range.", "It makes the concentration of ratings easy to compare across bins.")

with tabs[2]:
    st.plotly_chart(genre_violin(filtered), use_container_width=True, config={"displaylogo":False}, key="genres_violin")
    graph_note("Genre Ratings", "Compares the spread of IMDb ratings across movie genres.", "The center and width of each violin show where ratings are concentrated and how widely they vary.")
    st.plotly_chart(genre_popularity(filtered), use_container_width=True, config={"displaylogo":False}, key="genres_popularity")
    graph_note("Genre Popularity Across Years", "Tracks the number of movies in the most common genres across release years.", "Use Play or the year slider to see how genre volume changes over time.")

with tabs[3]:
    st.plotly_chart(vote_age_rating_3d(filtered), use_container_width=True, config={"displaylogo":False}, key="relationships_vote_age_3d")
    graph_note("Movie Age, Votes & Rating", "Connects movie age, IMDb vote count and rating in three dimensions.", "Point color represents IMDb rating, while position shows age and number of votes.")
    st.plotly_chart(runtime_heatmap(filtered), use_container_width=True, config={"displaylogo":False}, key="relationships_runtime_heatmap")
    graph_note("Runtime vs Rating", "Shows where runtime and IMDb rating combinations occur most often.", "Brighter regions represent combinations with more movies in the selected data.")

with tabs[4]:
    st.plotly_chart(rating_bloom(filtered), use_container_width=True, config={"displaylogo":False}, key="top_rating_bloom")
    graph_note("Rating Bloom", "Ranks the highest-rated movies with at least 50,000 IMDb votes.", "Longer petals represent higher ratings, while labels identify the movies and their ranks.")

with tabs[5]:
    st.plotly_chart(rating_surface(filtered), use_container_width=True, config={"displaylogo":False}, key="advanced_rating_surface")
    graph_note("IMDb Rating Landscape", "Shows average IMDb rating across release year and runtime groups.", "The 3D surface highlights how average ratings vary across both dimensions.")
    st.plotly_chart(characteristics_comparison(filtered), use_container_width=True, config={"displaylogo":False}, key="advanced_characteristics")
    graph_note("Movie Characteristics Comparison", "Combines runtime-rating relationships, feature correlations and rating-group profiles.", "Together, the three panels show relationships among key movie characteristics.")

with tabs[6]:
    st.plotly_chart(scifi_treemap(filtered), use_container_width=True, config={"displaylogo":False}, key="scifi_treemap")
    graph_note("Sci-Fi Rating Categories", "Breaks Sci-Fi movies into rating categories and genres.", "Larger boxes represent more movies in that rating-category and genre combination.")
