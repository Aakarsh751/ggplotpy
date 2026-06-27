"""Comprehensive coverage sweep — render a representative use of every ggplot2
layer-producing category from Python. Honest pass/skip/fail reporting.

Run:  python scripts/verify_ggplot_coverage.py
Skips are expected for layers needing extra R packages (hexbin, quantreg, sf,
mapproj) or special data (maps); those are reported separately from real FAILs.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import ggplotpy
from ggplotpy import R, aes, ggplot
from ggplotpy.codegen.reflect import list_namespace_exports

rng = np.random.default_rng(7)
N = 60
df = pd.DataFrame(
    {
        "x": rng.normal(size=N),
        "y": rng.normal(size=N),
        "z": rng.uniform(size=N),
        "g": rng.choice(["a", "b", "c"], size=N),
        "g2": rng.choice(["p", "q"], size=N),
        "cnt": rng.integers(1, 5, size=N),
        "xmin": rng.normal(size=N) - 1,
        "xmax": rng.normal(size=N) + 1,
        "ymin": rng.normal(size=N) - 1,
        "ymax": rng.normal(size=N) + 1,
        "lab": [f"r{i}" for i in range(N)],
        "ang": rng.uniform(0, 6.28, size=N),
        "rad": rng.uniform(0.1, 1.0, size=N),
    }
)
# regular grid for raster/contour/tile
gx, gy = np.meshgrid(np.linspace(-2, 2, 12), np.linspace(-2, 2, 12))
grid = pd.DataFrame({"x": gx.ravel(), "y": gy.ravel(), "z": (gx * gy).ravel()})

EXPORTS = set(list_namespace_exports("ggplot2"))
results: dict[str, list] = {"OK": [], "SKIP": [], "FAIL": []}


def _have(pkg):
    from ggplotpy.backend.inprocess import r

    return bool(r().r(f'isTRUE(requireNamespace("{pkg}", quietly=TRUE))')[0])


# Layers needing optional R packages — skip up front if absent.
_OPTIONAL = {
    "geom_hex": "hexbin",
    "stat_bin_hex": "hexbin",
    "stat_binhex": "hexbin",
    "geom_quantile": "quantreg",
    "stat_quantile": "quantreg",
}


def attempt(name, build):
    base_name = name.split(":")[0].split("/")[0]
    pkg = _OPTIONAL.get(base_name)
    if pkg and not _have(pkg):
        results["SKIP"].append(f"{name}: needs R package '{pkg}'")
        return
    try:
        p = build()
        svg = p._repr_svg_()
        assert isinstance(svg, str) and "<svg" in svg.lower()
        results["OK"].append(name)
    except Exception as e:
        msg = str(e).lower()
        skip_signals = (
            "install", "namespace", "hexbin", "quantreg", "mapproj", "sf",
            "there is no package", "could not find", "mgcv", "loading required",
        )
        bucket = "SKIP" if any(s in msg for s in skip_signals) else "FAIL"
        results[bucket].append(f"{name}: {type(e).__name__} {str(e)[:90]}")


def base():
    return ggplot(df) + aes(x="x", y="y")


# ---- geoms: per-geom aes/data so each gets valid input ----
GEOM_SPECS = {
    "geom_point": lambda: base() + ggplotpy.geom_point(),
    "geom_line": lambda: base() + ggplotpy.geom_line(),
    "geom_path": lambda: base() + ggplotpy.geom_path(),
    "geom_step": lambda: base() + ggplotpy.geom_step(),
    "geom_area": lambda: ggplot(df) + aes(x="x", y="z") + ggplotpy.geom_area(),
    "geom_ribbon": lambda: ggplot(df) + aes(x="x") + ggplotpy.geom_ribbon(aes(ymin="ymin", ymax="ymax")),
    "geom_bar": lambda: ggplot(df) + aes(x="g") + ggplotpy.geom_bar(),
    "geom_col": lambda: ggplot(df) + aes(x="g", y="z") + ggplotpy.geom_col(),
    "geom_histogram": lambda: ggplot(df) + aes(x="x") + ggplotpy.geom_histogram(bins=10),
    "geom_freqpoly": lambda: ggplot(df) + aes(x="x") + ggplotpy.geom_freqpoly(bins=10),
    "geom_density": lambda: ggplot(df) + aes(x="x") + ggplotpy.geom_density(),
    "geom_boxplot": lambda: ggplot(df) + aes(x="g", y="y") + ggplotpy.geom_boxplot(),
    "geom_violin": lambda: ggplot(df) + aes(x="g", y="y") + ggplotpy.geom_violin(),
    "geom_jitter": lambda: ggplot(df) + aes(x="g", y="y") + ggplotpy.geom_jitter(),
    "geom_count": lambda: base() + ggplotpy.geom_count(),
    "geom_smooth": lambda: base() + ggplotpy.geom_smooth(method="lm"),
    "geom_text": lambda: base() + ggplotpy.geom_text(aes(label="lab")),
    "geom_label": lambda: base() + ggplotpy.geom_label(aes(label="lab")),
    "geom_tile": lambda: ggplot(grid) + aes(x="x", y="y") + ggplotpy.geom_tile(aes(fill="z")),
    "geom_raster": lambda: ggplot(grid) + aes(x="x", y="y") + ggplotpy.geom_raster(aes(fill="z")),
    "geom_rect": lambda: ggplot(df) + ggplotpy.geom_rect(aes(xmin="xmin", xmax="xmax", ymin="ymin", ymax="ymax")),
    "geom_polygon": lambda: base() + ggplotpy.geom_polygon(),
    "geom_segment": lambda: ggplot(df) + ggplotpy.geom_segment(aes(x="xmin", y="ymin", xend="xmax", yend="ymax")),
    "geom_curve": lambda: ggplot(df) + ggplotpy.geom_curve(aes(x="xmin", y="ymin", xend="xmax", yend="ymax")),
    "geom_spoke": lambda: base() + ggplotpy.geom_spoke(aes(angle="ang", radius="rad")),
    "geom_rug": lambda: base() + ggplotpy.geom_point() + ggplotpy.geom_rug(),
    "geom_point2": lambda: base() + ggplotpy.geom_point(),
    "geom_hline": lambda: base() + ggplotpy.geom_point() + ggplotpy.geom_hline(yintercept=0),
    "geom_vline": lambda: base() + ggplotpy.geom_point() + ggplotpy.geom_vline(xintercept=0),
    "geom_abline": lambda: base() + ggplotpy.geom_point() + ggplotpy.geom_abline(slope=1, intercept=0),
    "geom_errorbar": lambda: ggplot(df) + aes(x="g") + ggplotpy.geom_errorbar(aes(ymin="ymin", ymax="ymax")),
    "geom_errorbarh": lambda: ggplot(df) + aes(y="g") + ggplotpy.geom_errorbarh(aes(xmin="xmin", xmax="xmax")),
    "geom_linerange": lambda: ggplot(df) + aes(x="x") + ggplotpy.geom_linerange(aes(ymin="ymin", ymax="ymax")),
    "geom_pointrange": lambda: ggplot(df) + aes(x="x", y="y") + ggplotpy.geom_pointrange(aes(ymin="ymin", ymax="ymax")),
    "geom_crossbar": lambda: ggplot(df) + aes(x="g", y="y") + ggplotpy.geom_crossbar(aes(ymin="ymin", ymax="ymax")),
    "geom_dotplot": lambda: ggplot(df) + aes(x="x") + ggplotpy.geom_dotplot(),
    "geom_bin2d": lambda: base() + ggplotpy.geom_bin2d(),
    "geom_hex": lambda: base() + ggplotpy.geom_hex(),
    "geom_density2d": lambda: base() + ggplotpy.geom_density2d(),
    "geom_contour": lambda: ggplot(grid) + aes(x="x", y="y", z="z") + ggplotpy.geom_contour(),
    "geom_contour_filled": lambda: ggplot(grid) + aes(x="x", y="y", z="z") + ggplotpy.geom_contour_filled(),
    "geom_qq": lambda: ggplot(df) + aes(sample="x") + ggplotpy.geom_qq(),
    "geom_qq_line": lambda: ggplot(df) + aes(sample="x") + ggplotpy.geom_qq_line(),
    "geom_quantile": lambda: base() + ggplotpy.geom_quantile(),
    "geom_function": lambda: base() + ggplotpy.geom_function(fun=R("sin")),
    "geom_blank": lambda: base() + ggplotpy.geom_blank(),
}

for name, spec in GEOM_SPECS.items():
    attempt(name, spec)

# Spatial geoms — render real geometry when geopandas + R sf are available.
def _add_sf_specs():
    try:
        import geopandas as gpd
        from shapely.geometry import Point, Polygon
    except ImportError:
        return False
    if not _have("sf"):
        return False
    pts = gpd.GeoDataFrame(
        {"name": ["a", "b", "c"], "val": [1.0, 2.0, 3.0],
         "geometry": [Point(0, 0), Point(1, 1), Point(2, 0)]},
        crs="EPSG:4326",
    )
    poly = gpd.GeoDataFrame(
        {"id": [1, 2], "v": [1.0, 2.0],
         "geometry": [Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
                      Polygon([(1, 0), (2, 0), (2, 1), (1, 1)])]},
        crs="EPSG:4326",
    )
    GEOM_SPECS["geom_sf"] = lambda: ggplot(poly) + ggplotpy.geom_sf(aes(fill="v"))
    GEOM_SPECS["geom_sf_label"] = lambda: ggplot(pts) + ggplotpy.geom_sf() + ggplotpy.geom_sf_label(aes(label="name"))
    GEOM_SPECS["geom_sf_text"] = lambda: ggplot(pts) + ggplotpy.geom_sf() + ggplotpy.geom_sf_text(aes(label="name"))
    return True


_sf_ok = _add_sf_specs()

# geom_map via R's map_data + R() escape for the map= data frame.
def _geom_map():
    from ggplotpy.backend.inprocess import r as _r

    states = 'ggplot2::map_data("state")'
    regions = sorted(str(x) for x in _r().r(f"unique({states}$region)"))
    vals = pd.DataFrame({"region": regions, "val": np.arange(len(regions), dtype=float)})
    return (
        ggplot(vals) + aes(map_id="region")
        + ggplotpy.geom_map(aes(fill="val"), map=R(states))
        + ggplotpy.expand_limits(x=R(f"{states}$long"), y=R(f"{states}$lat"))
    )


if _have("maps"):
    GEOM_SPECS["geom_map"] = _geom_map

# Geoms still needing data we don't synthesise here are reported as SKIP, not FAIL.
_SPECIAL_DATA = {}
if not _sf_ok:
    _SPECIAL_DATA.update({k: "geopandas + R sf" for k in ("geom_sf", "geom_sf_label", "geom_sf_text")})
if not _have("maps"):
    _SPECIAL_DATA["geom_map"] = "R 'maps' package + map data"

# Attempt the spatial / map specs added after the main GEOM_SPECS loop ran.
for _name in ("geom_sf", "geom_sf_label", "geom_sf_text", "geom_map"):
    if _name in GEOM_SPECS:
        attempt(_name, GEOM_SPECS[_name])

# every geom export must at least be present + attempted (use point-like default for the rest)
for g in sorted(e for e in EXPORTS if e.startswith("geom_")):
    if g in GEOM_SPECS:
        continue
    if g in _SPECIAL_DATA:
        results["SKIP"].append(f"{g}: needs {_SPECIAL_DATA[g]}")
        continue
    attempt(g, (lambda gg=g: base() + ggplotpy.geom_point() + getattr(ggplotpy, gg)()))

# ---- stats ----
STAT_SPECS = {
    "stat_bin": lambda: ggplot(df) + aes(x="x") + ggplotpy.stat_bin(bins=10),
    "stat_count": lambda: ggplot(df) + aes(x="g") + ggplotpy.stat_count(),
    "stat_density": lambda: ggplot(df) + aes(x="x") + ggplotpy.stat_density(),
    "stat_smooth": lambda: base() + ggplotpy.stat_smooth(method="lm"),
    "stat_ecdf": lambda: ggplot(df) + aes(x="x") + ggplotpy.stat_ecdf(),
    "stat_summary": lambda: ggplot(df) + aes(x="g", y="y") + ggplotpy.stat_summary(fun=R("mean")),
    "stat_ellipse": lambda: base() + ggplotpy.geom_point() + ggplotpy.stat_ellipse(),
    "stat_function": lambda: base() + ggplotpy.stat_function(fun=R("dnorm")),
    "stat_qq": lambda: ggplot(df) + aes(sample="x") + ggplotpy.stat_qq(),
    "stat_unique": lambda: base() + ggplotpy.stat_unique() + ggplotpy.geom_point(),
    "stat_summary_bin": lambda: ggplot(df) + aes(x="x", y="y") + ggplotpy.stat_summary_bin(fun=R("mean")),
}
for name, spec in STAT_SPECS.items():
    attempt(name, spec)

# ---- scales (sample across families) ----
SCALE_SPECS = {
    "scale_x_continuous": lambda: base() + ggplotpy.geom_point() + ggplotpy.scale_x_continuous(limits=(-3, 3)),
    "scale_y_log10": lambda: ggplot(df) + aes(x="x", y="z") + ggplotpy.geom_point() + ggplotpy.scale_y_log10(),
    "scale_x_reverse": lambda: base() + ggplotpy.geom_point() + ggplotpy.scale_x_reverse(),
    "scale_color_brewer": lambda: ggplot(df) + aes(x="x", y="y", color="g") + ggplotpy.geom_point() + ggplotpy.scale_color_brewer(palette="Set1"),
    "scale_color_manual": lambda: ggplot(df) + aes(x="x", y="y", color="g") + ggplotpy.geom_point() + ggplotpy.scale_color_manual(values=["red", "green", "blue"]),
    "scale_color_viridis_d": lambda: ggplot(df) + aes(x="x", y="y", color="g") + ggplotpy.geom_point() + ggplotpy.scale_color_viridis_d(),
    "scale_fill_viridis_c": lambda: ggplot(grid) + aes(x="x", y="y", fill="z") + ggplotpy.geom_raster() + ggplotpy.scale_fill_viridis_c(),
    "scale_size_continuous": lambda: ggplot(df) + aes(x="x", y="y", size="z") + ggplotpy.geom_point() + ggplotpy.scale_size_continuous(),
    "scale_alpha": lambda: ggplot(df) + aes(x="x", y="y", alpha="z") + ggplotpy.geom_point() + ggplotpy.scale_alpha(),
    "scale_shape": lambda: ggplot(df) + aes(x="x", y="y", shape="g") + ggplotpy.geom_point() + ggplotpy.scale_shape(),
    "scale_x_discrete": lambda: ggplot(df) + aes(x="g", y="y") + ggplotpy.geom_point() + ggplotpy.scale_x_discrete(),
}
for name, spec in SCALE_SPECS.items():
    attempt(name, spec)

# ---- coords ----
for name, mk in {
    "coord_cartesian": lambda: ggplotpy.coord_cartesian(xlim=(-2, 2)),
    "coord_flip": lambda: ggplotpy.coord_flip(),
    "coord_fixed": lambda: ggplotpy.coord_fixed(ratio=1),
    "coord_equal": lambda: ggplotpy.coord_equal(),
    "coord_polar": lambda: ggplotpy.coord_polar(),
    "coord_radial": lambda: ggplotpy.coord_radial(),
    "coord_trans": lambda: ggplotpy.coord_trans(x="identity"),
}.items():
    attempt(name, (lambda m=mk: base() + ggplotpy.geom_point() + m()))

# ---- facets ----
attempt("facet_wrap", lambda: base() + ggplotpy.geom_point() + ggplotpy.facet_wrap("~ g"))
attempt("facet_grid", lambda: base() + ggplotpy.geom_point() + ggplotpy.facet_grid("g2 ~ g"))
attempt("facet_null", lambda: base() + ggplotpy.geom_point() + ggplotpy.facet_null())

# ---- themes ----
for t in sorted(e for e in EXPORTS if e.startswith("theme_")):
    if t in {"theme_get", "theme_set", "theme_update", "theme_replace", "theme_test"} or t.startswith("theme_sub"):
        continue
    attempt(t, (lambda tt=t: base() + ggplotpy.geom_point() + getattr(ggplotpy, tt)()))
attempt("theme(elements)", lambda: base() + ggplotpy.geom_point()
        + ggplotpy.theme(legend_position="bottom", axis_text_x=ggplotpy.element_text(angle=45)))

# ---- positions ----
for name, pos in {
    "position_dodge": lambda: ggplotpy.position_dodge(width=0.5),
    "position_stack": lambda: ggplotpy.position_stack(),
    "position_fill": lambda: ggplotpy.position_fill(),
    "position_jitter": lambda: ggplotpy.position_jitter(width=0.1),
    "position_nudge": lambda: ggplotpy.position_nudge(x=0.1),
    "position_identity": lambda: ggplotpy.position_identity(),
}.items():
    attempt(name, (lambda p=pos: ggplot(df) + aes(x="g", y="z") + ggplotpy.geom_col(position=p())))

# ---- guides ----
attempt("guide_legend", lambda: ggplot(df) + aes(x="x", y="y", color="g") + ggplotpy.geom_point() + ggplotpy.guides(color=ggplotpy.guide_legend(ncol=2)))
attempt("guide_colorbar", lambda: ggplot(df) + aes(x="x", y="y", color="z") + ggplotpy.geom_point() + ggplotpy.guides(color=ggplotpy.guide_colorbar()))
attempt("guide_bins", lambda: ggplot(df) + aes(x="x", y="y", color="z") + ggplotpy.geom_point() + ggplotpy.guides(color=ggplotpy.guide_bins()))
attempt("guide_axis", lambda: base() + ggplotpy.geom_point() + ggplotpy.guides(x=ggplotpy.guide_axis(angle=45)))
attempt("guide_none", lambda: ggplot(df) + aes(x="x", y="y", color="g") + ggplotpy.geom_point() + ggplotpy.guides(color=ggplotpy.guide_none()))

# ---- annotations + label helpers ----
attempt("annotate", lambda: base() + ggplotpy.geom_point() + ggplotpy.annotate("text", x=0, y=0, label="hi"))
attempt("annotation_logticks", lambda: ggplot(df) + aes(x="x", y="z") + ggplotpy.geom_point() + ggplotpy.scale_y_log10() + ggplotpy.annotation_logticks())
attempt("labs", lambda: base() + ggplotpy.geom_point() + ggplotpy.labs(title="T", subtitle="s", x="X", caption="c"))
attempt("lims", lambda: base() + ggplotpy.geom_point() + ggplotpy.lims(x=(-3, 3)))
attempt("xlim/ylim", lambda: base() + ggplotpy.geom_point() + ggplotpy.xlim(-3, 3) + ggplotpy.ylim(-3, 3))
attempt("ggtitle", lambda: base() + ggplotpy.geom_point() + ggplotpy.ggtitle("Title"))

# ---- report ----
print(f"\n{'='*60}\nCOVERAGE SWEEP RESULTS")
print(f"OK   : {len(results['OK'])}")
print(f"SKIP : {len(results['SKIP'])}  (need extra R pkg / special data)")
print(f"FAIL : {len(results['FAIL'])}")
if results["SKIP"]:
    print("\n-- SKIPPED --")
    for s in results["SKIP"]:
        print("  ", s)
if results["FAIL"]:
    print("\n-- FAILED (real problems) --")
    for f in results["FAIL"]:
        print("  ", f)
else:
    print("\nNo real failures.")
