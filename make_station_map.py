"""
make_station_map.py
Validation figure: GHCN-M v4 temperature monitoring stations used in the
Tidal Basin cherry blossom analysis, plotted relative to the reference site.

Run with the project venv:
  /path/to/.venv/bin/python make_station_map.py
"""

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import contextily as ctx
from shapely.geometry import Point

# ── Reference point: Tidal Basin cherry trees ────────────────────────────────
TIDAL_BASIN = (38.8890, -77.0370)   # lat, lon
RADIUS_KM   = 25.0

# ── Load station metadata ─────────────────────────────────────────────────────
df = pd.read_csv("data/ghcnm_station_meta.csv", comment="#")
df.columns = df.columns.str.strip()

# ── Build GeoDataFrame (WGS-84) ───────────────────────────────────────────────
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df["Lon"], df["Lat"]),
    crs="EPSG:4326",
)

# Add the Tidal Basin reference point
ref = gpd.GeoDataFrame(
    [{"Name": "Tidal Basin (ref)", "Dist_km": 0.0,
      "geometry": Point(TIDAL_BASIN[1], TIDAL_BASIN[0])}],
    crs="EPSG:4326",
)

# Project to Web Mercator for contextily basemap
gdf_m   = gdf.to_crs("EPSG:3857")
ref_m   = ref.to_crs("EPSG:3857")

# 25 km radius circle in projected CRS
ref_pt  = ref_m.geometry.iloc[0]
circle  = gpd.GeoDataFrame(
    geometry=[ref_pt.buffer(RADIUS_KM * 1000)],
    crs="EPSG:3857",
)

# ── Colour stations by distance ───────────────────────────────────────────────
cmap  = plt.cm.YlOrRd
norm  = plt.Normalize(vmin=0, vmax=RADIUS_KM)
colors = cmap(norm(gdf_m["Dist_km"]))

# ── Figure ────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(11, 10))

# 25 km boundary circle
circle.boundary.plot(ax=ax, color="#2196F3", linewidth=1.4,
                     linestyle="--", alpha=0.7, zorder=3)
circle.plot(ax=ax, color="#2196F3", alpha=0.04, zorder=2)

# Stations coloured by distance
gdf_m.plot(ax=ax, color=colors, markersize=60, zorder=5,
           edgecolor="white", linewidth=0.6)

# Tidal Basin reference star
ref_m.plot(ax=ax, marker="*", color="#e53935", markersize=220,
           zorder=6, edgecolor="white", linewidth=0.8)

# Station labels
for _, row in gdf_m.iterrows():
    x, y = row.geometry.x, row.geometry.y
    label = f"{row['Name'].replace('_', ' ').title()}\n{row['Dist_km']:.1f} km"
    ax.annotate(
        label, xy=(x, y), xytext=(5, 5),
        textcoords="offset points",
        fontsize=5.5, color="#333333",
        path_effects=[pe.withStroke(linewidth=1.8, foreground="white")],
        zorder=7,
    )

# Tidal Basin label
rx, ry = ref_m.geometry.iloc[0].x, ref_m.geometry.iloc[0].y
ax.annotate(
    "Tidal Basin\n(reference site)",
    xy=(rx, ry), xytext=(10, -18),
    textcoords="offset points",
    fontsize=8, fontweight="bold", color="#e53935",
    path_effects=[pe.withStroke(linewidth=2, foreground="white")],
    zorder=8,
)

# Basemap
try:
    ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron, zoom=10)
except Exception:
    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, zoom=10)

# Colorbar
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cb = fig.colorbar(sm, ax=ax, fraction=0.025, pad=0.02)
cb.set_label("Distance from Tidal Basin (km)", fontsize=9)
cb.ax.tick_params(labelsize=8)

# 25 km annotation
ax.annotate(
    "25 km radius",
    xy=(ref_m.geometry.iloc[0].x, ref_m.geometry.iloc[0].y + RADIUS_KM * 1000),
    xytext=(6, 4), textcoords="offset points",
    fontsize=8, color="#2196F3", alpha=0.9,
    path_effects=[pe.withStroke(linewidth=1.5, foreground="white")],
    zorder=7,
)

ax.set_axis_off()
ax.set_title(
    f"GHCN-M v4 Temperature Stations Within {RADIUS_KM:.0f} km of Tidal Basin  "
    f"(n = {len(df)})\n"
    "Used for IDW ensemble temperature anomaly — Washington D.C. cherry blossom analysis",
    fontsize=10, loc="left", pad=10,
)

plt.tight_layout()
OUT = "output/station_map.png"
plt.savefig(OUT, dpi=180, bbox_inches="tight", facecolor="white")
print(f"Saved {OUT}")
plt.show()
