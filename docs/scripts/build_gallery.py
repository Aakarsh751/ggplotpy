"""Generate the documentation gallery: render real-world plots to PNGs.

Uses external data (Palmer Penguins, Gapminder — committed under ``docs/data/``)
and R's own real datasets (ggplot2::mpg / diamonds / economics, datasets::iris),
exercising every major feature and several Python→R data conversions.

Run:  python docs/scripts/build_gallery.py
Output: docs/_static/gallery/*.png  +  a printed manifest.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

import ggplotpy
from ggplotpy import R, aes, geom_point, ggplot

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "docs" / "data"
OUT = ROOT / "docs" / "_static" / "gallery"
OUT.mkdir(parents=True, exist_ok=True)

ggplotpy.set_options(figure_size=(6.4, 4.2), dpi=110, format="png")


def _r_dataset(expr: str) -> pd.DataFrame:
    """Pull an R data frame (e.g. ggplot2::mpg) into pandas."""
    from ggplotpy.backend.inprocess import r
    from rpy2.robjects import conversion

    ro = r()
    with conversion.localconverter(conversion.get_conversion()):
        return conversion.get_conversion().rpy2py(ro.r(expr))


# --- datasets -----------------------------------------------------------------
penguins = pd.read_csv(DATA / "penguins.csv").dropna(
    subset=["bill_length_mm", "bill_depth_mm", "body_mass_g", "flipper_length_mm"]
)
gap = pd.read_csv(DATA / "gapminder.tsv", sep="\t")
mpg = _r_dataset("ggplot2::mpg")
diamonds = _r_dataset("ggplot2::diamonds").sample(4000, random_state=1)
economics = _r_dataset("ggplot2::economics")
iris = _r_dataset("datasets::iris")
iris.columns = [c.replace(".", "_") for c in iris.columns]  # Sepal.Length -> Sepal_Length

manifest: list[tuple[str, str]] = []
failures: list[str] = []


def save(name: str, plot, title: str) -> None:
    try:
        plot.save(str(OUT / f"{name}.png"))
        manifest.append((name, title))
    except Exception as e:  # noqa: BLE001
        failures.append(f"{name}: {type(e).__name__} {e}")


# --- 1. core geoms (external Penguins data) -----------------------------------
save(
    "scatter_smooth",
    ggplot(penguins)
    + aes(x="bill_length_mm", y="bill_depth_mm", color="species")
    + geom_point(size=2, alpha=0.8)
    + ggplotpy.geom_smooth(method="lm", se=False)
    + ggplotpy.labs(
        title="Penguin bill dimensions",
        subtitle="Palmer Station, Antarctica",
        x="Bill length (mm)",
        y="Bill depth (mm)",
        color="Species",
    )
    + ggplotpy.theme_minimal(),
    "Scatter + linear smooth, colored by group (Palmer Penguins)",
)

save(
    "histogram",
    ggplot(penguins)
    + aes(x="body_mass_g", fill="species")
    + ggplotpy.geom_histogram(bins=25, alpha=0.7, position="identity")
    + ggplotpy.labs(title="Body mass distribution", x="Body mass (g)")
    + ggplotpy.theme_minimal(),
    "Stacked histogram by species",
)

save(
    "density",
    ggplot(penguins)
    + aes(x="flipper_length_mm", fill="species")
    + ggplotpy.geom_density(alpha=0.6)
    + ggplotpy.labs(title="Flipper length density", x="Flipper length (mm)")
    + ggplotpy.theme_light(),
    "Overlaid kernel densities",
)

save(
    "boxplot",
    ggplot(penguins)
    + aes(x="species", y="body_mass_g", fill="species")
    + ggplotpy.geom_boxplot()
    + ggplotpy.geom_jitter(width=0.15, alpha=0.3, size=1)
    + ggplotpy.labs(title="Body mass by species", x=None, y="Body mass (g)")
    + ggplotpy.theme_minimal()
    + ggplotpy.theme(legend_position="none"),
    "Boxplot + jittered points",
)

save(
    "violin",
    ggplot(penguins)
    + aes(x="species", y="flipper_length_mm", fill="species")
    + ggplotpy.geom_violin(trim=False, alpha=0.7)
    + ggplotpy.labs(title="Flipper length by species", x=None)
    + ggplotpy.theme_minimal()
    + ggplotpy.theme(legend_position="none"),
    "Violin plot",
)

# --- 2. faceting --------------------------------------------------------------
save(
    "facet_wrap",
    ggplot(penguins.dropna(subset=["sex"]))
    + aes(x="bill_length_mm", y="body_mass_g", color="sex")
    + geom_point(alpha=0.8)
    + ggplotpy.facet_wrap("~ species")
    + ggplotpy.labs(title="Faceted by species")
    + ggplotpy.theme_bw(),
    "facet_wrap across species",
)

save(
    "facet_grid",
    ggplot(penguins.dropna(subset=["sex"]))
    + aes(x="bill_length_mm", y="bill_depth_mm", color="species")
    + geom_point(alpha=0.8)
    + ggplotpy.facet_grid("sex ~ island")
    + ggplotpy.labs(title="facet_grid: sex × island")
    + ggplotpy.theme_bw(),
    "facet_grid (rows × cols)",
)

# --- 3. scales (real ggplot2 datasets) ----------------------------------------
save(
    "scale_viridis",
    ggplot(diamonds)
    + aes(x="carat", y="price", color="depth")
    + geom_point(alpha=0.4, size=1)
    + ggplotpy.scale_color_viridis_c()
    + ggplotpy.labs(title="Diamonds: price vs carat", subtitle="color = depth (viridis)")
    + ggplotpy.theme_minimal(),
    "Continuous viridis color scale (diamonds)",
)

save(
    "scale_log",
    ggplot(gap[gap["year"] == 2007])
    + aes(x="gdpPercap", y="lifeExp", color="continent", size="pop")
    + geom_point(alpha=0.7)
    + ggplotpy.scale_x_log10()
    + ggplotpy.scale_size_continuous(range=(1, 12))
    + ggplotpy.labs(title="Gapminder 2007", subtitle="GDP per capita (log) vs life expectancy", x="GDP per capita")
    + ggplotpy.theme_minimal(),
    "Log scale + bubble sizing (Gapminder)",
)

save(
    "scale_brewer",
    ggplot(mpg)
    + aes(x="displ", y="hwy", color="class")
    + geom_point(size=2)
    + ggplotpy.scale_color_brewer(palette="Dark2")
    + ggplotpy.labs(title="Fuel economy by vehicle class", x="Engine displacement (L)", y="Highway mpg")
    + ggplotpy.theme_minimal(),
    "Brewer qualitative palette (mpg)",
)

# --- 4. time series & area ----------------------------------------------------
save(
    "timeseries",
    ggplot(economics)
    + aes(x="date", y="unemploy")
    + ggplotpy.geom_line(color="#2c3e50")
    + ggplotpy.labs(title="US unemployment over time", x=None, y="Unemployed (thousands)")
    + ggplotpy.theme_minimal(),
    "Time-series line (economics)",
)

save(
    "area",
    ggplot(economics)
    + aes(x="date", y="psavert")
    + ggplotpy.geom_area(fill="#3498db", alpha=0.5)
    + ggplotpy.labs(title="Personal savings rate", x=None, y="Savings rate (%)")
    + ggplotpy.theme_minimal(),
    "Area chart",
)

# --- 5. 2-D density (no hexbin needed) ----------------------------------------
save(
    "bin2d",
    ggplot(diamonds)
    + aes(x="carat", y="price")
    + ggplotpy.geom_bin2d(bins=30)
    + ggplotpy.scale_fill_viridis_c()
    + ggplotpy.labs(title="2-D binned density (diamonds)")
    + ggplotpy.theme_minimal(),
    "geom_bin2d heatmap",
)

# --- 6. bars / coords ---------------------------------------------------------
save(
    "bar_dodge",
    ggplot(penguins)
    + aes(x="island", fill="species")
    + ggplotpy.geom_bar(position=ggplotpy.position_dodge())
    + ggplotpy.labs(title="Penguin counts by island", x=None)
    + ggplotpy.theme_minimal(),
    "Dodged bar chart",
)

save(
    "coord_polar",
    ggplot(mpg)
    + aes(x="class", fill="class")
    + ggplotpy.geom_bar()
    + ggplotpy.coord_polar()
    + ggplotpy.labs(title="Vehicle classes (polar)")
    + ggplotpy.theme_minimal()
    + ggplotpy.theme(legend_position="none"),
    "Bar chart in polar coordinates",
)

# --- 7. themes montage (patchwork) --------------------------------------------
def _themed(theme, label):
    return (
        ggplot(iris)
        + aes(x="Sepal_Length", y="Petal_Length", color="Species")
        + geom_point()
        + theme()
        + ggplotpy.labs(title=label)
        + ggplotpy.theme(legend_position="none")
    )


try:
    montage = (
        (_themed(ggplotpy.theme_minimal, "theme_minimal") | _themed(ggplotpy.theme_bw, "theme_bw"))
        / (_themed(ggplotpy.theme_classic, "theme_classic") | _themed(ggplotpy.theme_dark, "theme_dark"))
    )
    montage.save(str(OUT / "themes_montage.png"), width=9, height=7)
    manifest.append(("themes_montage", "Built-in themes (patchwork 2×2)"))
except Exception as e:  # noqa: BLE001
    failures.append(f"themes_montage: {type(e).__name__} {e}")

# --- 8. patchwork dashboard ---------------------------------------------------
try:
    p1 = ggplot(penguins) + aes(x="bill_length_mm", y="body_mass_g", color="species") + geom_point() + ggplotpy.theme_minimal() + ggplotpy.theme(legend_position="none")
    p2 = ggplot(penguins) + aes(x="species", y="flipper_length_mm", fill="species") + ggplotpy.geom_boxplot() + ggplotpy.theme_minimal() + ggplotpy.theme(legend_position="none")
    p3 = ggplot(penguins) + aes(x="body_mass_g", fill="species") + ggplotpy.geom_density(alpha=0.6) + ggplotpy.theme_minimal()
    dash = (p1 | p2) / p3
    dash.save(str(OUT / "patchwork_dashboard.png"), width=9, height=7)
    manifest.append(("patchwork_dashboard", "Multi-panel dashboard (patchwork | and /)"))
except Exception as e:  # noqa: BLE001
    failures.append(f"patchwork_dashboard: {type(e).__name__} {e}")

# --- 9. data-conversion demos -------------------------------------------------
save(
    "conv_dict",
    ggplot({"month": list(range(1, 13)), "sales": [3, 5, 4, 7, 8, 6, 9, 11, 10, 8, 7, 12]})
    + aes(x="month", y="sales")
    + ggplotpy.geom_col(fill="#e67e22")
    + ggplotpy.scale_x_continuous(breaks=np.arange(1, 13))
    + ggplotpy.labs(title="From a Python dict", x="Month", y="Sales")
    + ggplotpy.theme_minimal(),
    "ggplot(dict) — dict of columns",
)

rng = np.random.default_rng(0)
arr = np.column_stack([rng.normal(size=200), rng.normal(size=200) * 0.5 + 1])
save(
    "conv_numpy",
    ggplot(arr)
    + aes(x="V1", y="V2")
    + geom_point(alpha=0.5, color="#9b59b6")
    + ggplotpy.geom_density2d(color="white")
    + ggplotpy.labs(title="From a NumPy 2-D array", subtitle="columns auto-named V1, V2")
    + ggplotpy.theme_dark(),
    "ggplot(np.ndarray) — 2-D array",
)

# --- 10. extensions & spatial (optional packages) -----------------------------
def _have_r(pkg: str) -> bool:
    from ggplotpy.backend.inprocess import r

    return bool(r().r(f'isTRUE(requireNamespace("{pkg}", quietly=TRUE))')[0])


# geom_hex needs the R 'hexbin' package
if _have_r("hexbin"):
    save(
        "hexbin",
        ggplot(diamonds)
        + aes(x="carat", y="price")
        + ggplotpy.geom_hex(bins=30)
        + ggplotpy.scale_fill_viridis_c()
        + ggplotpy.labs(title="Hexbin density (diamonds)")
        + ggplotpy.theme_minimal(),
        "geom_hex (needs R hexbin)",
    )

# ggrepel: non-overlapping text labels
try:
    import ggplotpy.ext as ext

    if _have_r("ggrepel"):
        cars = mpg.drop_duplicates(subset=["model"]).head(20)
        save(
            "ggrepel",
            ggplot(cars)
            + aes(x="displ", y="hwy", label="model")
            + geom_point(color="#3498db")
            + ext.ggrepel.geom_text_repel(size=3, max_overlaps=20)
            + ggplotpy.labs(title="Labeled points with ggrepel", x="Displacement (L)", y="Highway mpg")
            + ggplotpy.theme_minimal(),
            "ggrepel non-overlapping labels",
        )
except Exception as e:  # noqa: BLE001
    failures.append(f"ggrepel: {type(e).__name__} {e}")

# Spatial choropleth via GeoPandas -> sf (North Carolina SIDS, bundled with sf)
try:
    import geopandas as gpd

    if _have_r("sf"):
        from ggplotpy.backend.inprocess import r

        nc_path = str(r().r('system.file("shape/nc.shp", package="sf")')[0])
        nc = gpd.read_file(nc_path)
        save(
            "geom_sf_choropleth",
            ggplot(nc)
            + ggplotpy.geom_sf(aes(fill="SID74"))
            + ggplotpy.scale_fill_viridis_c(option="magma")
            + ggplotpy.labs(title="North Carolina: SIDS cases 1974",
                        subtitle="GeoPandas -> R sf -> geom_sf", fill="SID74")
            + ggplotpy.theme_minimal(),
            "geom_sf choropleth (GeoPandas -> sf)",
        )
except Exception as e:  # noqa: BLE001
    failures.append(f"geom_sf_choropleth: {type(e).__name__} {e}")

# --- 11. advanced statistical (ggdist / ggridges) -----------------------------
def _have_r2(pkg: str) -> bool:
    from ggplotpy.backend.inprocess import r

    return bool(r().r(f'isTRUE(requireNamespace("{pkg}", quietly=TRUE))')[0])


if _have_r2("ggdist"):
    try:
        import ggplotpy.ext as ext

        save(
            "ggdist_halfeye",
            ggplot(penguins)
            + aes(x="species", y="body_mass_g", fill="species")
            + ext.ggdist.stat_halfeye(adjust=0.6, width=0.5, justification=-0.2)
            + ggplotpy.geom_boxplot(width=0.12, alpha=0.5, outlier_color=R("NA"))
            + ggplotpy.labs(title="Raincloud / half-eye (ggdist)", x=None, y="Body mass (g)")
            + ggplotpy.theme_minimal()
            + ggplotpy.theme(legend_position="none"),
            "ggdist half-eye + boxplot",
        )
    except Exception as e:  # noqa: BLE001
        failures.append(f"ggdist_halfeye: {type(e).__name__} {e}")

if _have_r2("ggridges"):
    try:
        import ggplotpy.ext as ext

        save(
            "ridgeline",
            ggplot(diamonds)
            + aes(x="price", y="cut", fill="cut")
            + ext.ggridges.geom_density_ridges(alpha=0.7, scale=1.4)
            + ggplotpy.scale_fill_viridis_d()
            + ggplotpy.labs(title="Price distribution by cut (ggridges)", y=None)
            + ggplotpy.theme_minimal()
            + ggplotpy.theme(legend_position="none"),
            "Ridgeline plot (ggridges)",
        )
    except Exception as e:  # noqa: BLE001
        failures.append(f"ridgeline: {type(e).__name__} {e}")

# --- 12. ANIMATION (gganimate -> GIF) -----------------------------------------
# transition_time animates over a continuous variable (year); it renders cleanly
# under ggplot2 4.0 where transition_states' default wrap-tweening currently breaks.
if _have_r2("gganimate") and _have_r2("gifski"):
    try:
        from ggplotpy.core.animate import animate

        anim_plot = (
            ggplot(gap)
            + aes(x="gdpPercap", y="lifeExp", color="continent", size="pop")
            + geom_point(alpha=0.7)
            + ggplotpy.scale_x_log10()
            + ggplotpy.scale_size_continuous(range=(2, 12))
            + ggplotpy.labs(title="Gapminder — year: {frame_time}",
                        x="GDP per capita (log)", y="Life expectancy")
            + ggplotpy.theme_minimal()
            + R("gganimate::transition_time(year)")
        )
        gif = animate(anim_plot, width=640, height=420, fps=10, nframes=48)
        (OUT / "animation.gif").write_bytes(gif)
        manifest.append(("animation", "Animated Gapminder over time (gganimate -> GIF)"))
    except Exception as e:  # noqa: BLE001
        failures.append(f"animation: {type(e).__name__} {e}")

# --- report -------------------------------------------------------------------
print(f"\nGallery -> {OUT}")
print(f"Rendered: {len(manifest)}  Failures: {len(failures)}")
for name, title in manifest:
    print(f"  OK  {name}.png — {title}")
for f in failures:
    print(f"  FAIL {f}")
if failures:
    sys.exit(1)
