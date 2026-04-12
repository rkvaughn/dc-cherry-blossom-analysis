
# Technical Specification: Sakura Peak Bloom "Organic Branch" with Temperature Overlay

## Goal
Transform a standard scientific scatter plot of Washington D.C. Sakura peak bloom dates into an editorial-quality "organic" visualization. The final figure represents a 10-year rolling mean as a tapering tree branch, individual data points as flowers connected by Bezier "twigs," and a **secondary smoothed temperature line** layered directly in front of the branch to show climate correlation.

## 1. Data Requirements
* **`Year`**: Integer.
* **`DOY`**: Day of Year (Integer/Float) representing the peak bloom date.
* **`Rolling_Mean`**: A 10-year centered rolling average of the `DOY`.
* **`Temp_Anomaly`**: Local temperature anomaly data.
* **`Temp_Rolling`**: A smoothed version (e.g., 5 or 10-year mean) of the temperature anomaly for the secondary line.

## 2. Visual Design Language (NYT Aesthetic)
* **Color Palette**:
    * **Background**: `#F9F7F2` (Soft Paper/Cream).
    * **Branch**: `#4E342E` (Deep Umber).
    * **Temperature Line**: `#263238` (Deep Charcoal) or `#1A237E` (Midnight Blue). 
    * **Blossoms**: `#F8BBD0` (Fill) with `#F48FB1` (Edge).
* **Layering Hierarchy (Z-Order)**:
    1.  Grid/Background (`zorder=1`)
    2.  Bezier Twigs (`zorder=2`)
    3.  **The Branch** (Rolling Mean Bloom) (`zorder=3`)
    4.  **Temperature Line** (`zorder=4`) — *Positioned in front of the branch.*
    5.  Blossoms (Actual Data Points) (`zorder=5`)
* **Typography**: Serif for titles (e.g., *Georgia*); Sans-Serif for labels (e.g., *Franklin Gothic*).

## 3. Core Implementation Logic

### A. The Tapering Branch
Use `LineCollection` to create a "growth" effect where the line thickness tapers from the past (thick) to the present (thin).

### B. The Temperature Overlay
Since temperature and bloom dates use different units, the temperature line should be **normalized** to the Y-axis range of the bloom dates or plotted on a invisible twin axis that aligns visually with the branch. To keep it "in front," ensure its `zorder` is exactly one level higher than the branch.

### C. Bezier Twigs & Blossoms
Connect each individual bloom year to the *branch* (not the temperature line) using a quadratic Bezier curve to maintain the botanical metaphor.

## 4. Revised Implementation Block (Python)

```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.path import Path
import matplotlib.patches as patches
from scipy.interpolate import make_interp_spline

def apply_organic_viz_with_temp(ax, df):
    # 1. Setup Smoothing for both Bloom and Temp
    years_fine = np.linspace(df['Year'].min(), df['Year'].max(), 500)
    
    # Smooth Bloom Branch
    spl_bloom = make_interp_spline(df['Year'], df['Rolling_Mean'].dropna(), k=3)
    y_bloom_smooth = spl_bloom(years_fine)
    
    # Smooth Temp Line (Normalized to visual space or secondary axis)
    spl_temp = make_interp_spline(df['Year'], df['Temp_Rolling'].dropna(), k=3)
    y_temp_smooth = spl_temp(years_fine)

    # 2. Plot Tapering Branch (Z-Order 3)
    points = np.array([years_fine, y_bloom_smooth]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    widths = np.linspace(7.0, 1.8, len(segments)) # Growth taper
    lc = LineCollection(segments, linewidths=widths, color='#4E342E', zorder=3, capstyle='round')
    ax.add_collection(lc)

    # 3. Plot Temperature Line In Front (Z-Order 4)
    # Using a thinner, high-contrast line to "cut" through the branch
    ax.plot(years_fine, y_temp_smooth, color='#263238', linewidth=1.5, 
            alpha=0.9, zorder=4, label="Temp Anomaly (Normalized)")

    # 4. Draw Twigs and Blossoms
    def draw_twig(start, end):
        mid_x, mid_y = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
        ctrl_x = mid_x + (1.2 if end[1] > start[1] else -1.2)
        path = Path([start, (ctrl_x, mid_y), end], [Path.MOVETO, Path.CURVE3, Path.CURVE3])
        return patches.PathPatch(path, facecolor='none', edgecolor='#5D4037', lw=0.8, alpha=0.3, zorder=2)

    for _, row in df.iterrows():
        if np.isnan(row['Rolling_Mean']): continue
        
        # Twig connects Flower to the Branch (Rolling_Mean)
        ax.add_patch(draw_twig((row['Year'], row['Rolling_Mean']), (row['Year'], row['DOY'])))
        
        # Blossom Clusters (Z-Order 5)
        ax.scatter(row['Year'], row['DOY'], s=150, color='#F8BBD0', edgecolors='#F48FB1', 
                   alpha=0.6, linewidth=0.5, zorder=5)
        ax.scatter(row['Year'], row['DOY'], s=20, color='white', alpha=0.4, zorder=6)

    # 5. NYT Styling
    ax.set_facecolor('#F9F7F2')
    ax.invert_yaxis()
    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.set_title("The Warming Branch", loc='left', fontsize=26, fontfamily='serif', fontweight='bold')
```

## 5. Agent Instructions / Tasks
1.  **Layering Check**: Ensure the temperature line has a higher `zorder` than the branch but remains behind the scatter points (blossoms).
2.  **Normalization**: If `Temp_Rolling` is in degrees Celsius, create a helper function to scale it so it overlays meaningfully on the `DOY` Y-axis (e.g., mapping $0^\circ C$ to the mean bloom date).
3.  **Visual Distinction**: Use a solid, crisp line style for the temperature to distinguish its "data" nature from the "organic" hand-drawn look of the branch.
4.  **Invert Y-Axis**: Keep `ax.invert_yaxis()` so that both warming temperatures and earlier blooms trend "upward" visually.