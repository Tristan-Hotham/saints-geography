"""Shared house style for the r/dataisbeautiful collages (light paper, Fraunces display, Source Serif 4 text, IBM Plex Mono notes).
Fonts are TTF conversions of the fontsource woff2 files, kept in ./fonts (set FONT_DIR to use another folder).
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import matplotlib.patheffects as pe

_HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.environ.get("FONT_DIR", os.path.join(_HERE, "fonts"))
for f in os.listdir(FONT_DIR):
    if f.endswith(".ttf"):
        fm.fontManager.addfont(os.path.join(FONT_DIR, f))
DISP = fm.FontProperties(fname=os.path.join(FONT_DIR, "fraunces-900-normal.ttf"))
SER = ["Source Serif 4", "Source Serif 4 Ext"]   # latin-ext fallback for ā, ō, ū
MONO = ["IBM Plex Mono", "IBM Plex Mono Ext"]
plt.rcParams.update({"font.family": SER, "axes.unicode_minus": False, "svg.fonttype": "none"})

BGC = "#F5F2EA"     # paper
FG = "#1E1B22"      # ink
MUT = "#6B655C"     # muted
LAND = "#E8E3D8"    # context land
EDGE = "#FFFFFF"

# counties (England ceremonial, Wales preserved, Scotland council areas) built from ONS 2025 boundaries, in the pub project
COUNTIES = os.environ.get("COUNTIES", "/home/claude/pubs/data/raw/counties.geojson")


def counties_km(path=COUNTIES, simplify=600):
    import geopandas as gpd
    c = gpd.read_file(path).to_crs(27700)
    c["geometry"] = c.geometry.simplify(simplify)
    c = c.set_geometry(c.geometry.scale(1e-3, 1e-3, origin=(0, 0)))
    return c


def to_km(lon, lat):
    from pyproj import Transformer
    t = Transformer.from_crs(4326, 27700, always_xy=True)
    x, y = t.transform(lon, lat)
    import numpy as np
    return np.asarray(x) / 1e3, np.asarray(y) / 1e3


def new_fig():
    return plt.figure(figsize=(12, 15), dpi=200, facecolor=BGC)


def words(fig, x, y, parts, size=50, gap=0.012):
    """Draw [(text, colour), ...] one after another on a line, measuring each word."""
    r = fig.canvas.get_renderer()
    for txt, col in parts:
        t = fig.text(x, y, txt, fontproperties=DISP, fontsize=size, color=col, va="top")
        bb = t.get_window_extent(renderer=r).transformed(fig.transFigure.inverted())
        x = bb.x1 + gap
    return x


def halo(w=3):
    return [pe.withStroke(linewidth=w, foreground=BGC)]


def headlines(fig, rect, items, big=38, small=12.5, step=None, sub_off=0.115):
    tx = fig.add_axes(rect); tx.axis("off"); tx.set_xlim(0, 1); tx.set_ylim(0, 1)
    step = step or 1 / len(items)
    for i, (b, c, txt) in enumerate(items):
        y = .99 - i * step
        tx.text(0, y, b, fontproperties=DISP, fontsize=big, color=c, va="top")
        tx.text(0, y - sub_off, txt, family=SER, fontsize=small, color=FG, va="top", linespacing=1.12)
    return tx


def footer(fig, text, y=0.048):
    fig.text(0.045, y, text, family=MONO, fontsize=9.6, color=MUT, va="top", linespacing=1.45)


def label(fig, x, y, s, size=11):
    fig.text(x, y, s, family=MONO, fontsize=size, color=MUT)
