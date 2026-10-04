IMDb MOVIE UNIVERSE — STREAMLIT DASHBOARD (FIXED)

This dashboard is built from the existing IMDb project notebook visualizations.
It does NOT require Power BI.

FILES
-----
app.py                  Main Streamlit dashboard
IMDb_Dashboard_Data.csv Project data used by the dashboard
requirements.txt        Python packages
run_dashboard.bat       Windows one-click launcher

QUICK START — WINDOWS
---------------------
1. Install Python 3.10+ if Python is not already installed.
2. Keep all files in the same folder.
3. Double-click run_dashboard.bat.
4. A browser window should open automatically.
5. If it does not, open the address shown in the terminal (normally http://localhost:8501).

MANUAL START
------------
Open Command Prompt in this folder and run:

    py -m pip install -r requirements.txt
    py -m streamlit run app.py

IMPORTANT
---------
The initial dashboard uses the notebook's original graph definitions and the supplied project data.
The sidebar filters recompute those same graph types rather than replacing them with Power BI visuals.

The dashboard contains:
- IMDb Rating Distribution (Plotly histogram + box)
- IMDb Rating Distribution (Plotly bar version)
- IMDb Rating Distribution by Genre (violin)
- Movie Age, Votes and IMDb Rating (3D scatter)
- Genre Popularity Across Years (animated bar chart)
- Runtime vs IMDb Rating (density heatmap)
- THE RATING BLOOM (top 15 rated movies with 50,000+ votes)
- IMDb Rating Landscape — Release Year × Runtime (3D surface)
- Movie Characteristics Comparison (bubble + correlation heatmap + radar)
- Sci-Fi Movies by Rating Category (treemap)

No additional analytical chart type was invented for the dashboard.

FIXES IN THIS VERSION
----------------------
- Removed the explanatory dashboard text that was appearing above the charts.
- Added unique keys to every Plotly chart so repeated notebook graphs do not trigger StreamlitDuplicateElementId.
- Kept all notebook graph families in the dashboard across the tabs.
- Added short two-line explanations below each graph.
- Previous dashboard files are unchanged.
