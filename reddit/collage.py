"""r/dataisbeautiful collage for saints-geography: where_local_saints_live.png (2400 x 3000).
Every number is read from the project's results (results/summary.json, results/concentration.csv,
results/dedication_counts.csv) or counted from data/saints.json. Run: python3 collage.py  (SAINTS=/path/to/saints-geography)
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
SAINTS = os.environ.get("SAINTS", "/home/claude/saints")
import numpy as np, pandas as pd
from house import *
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

S = json.load(open(os.path.join(SAINTS, "results/summary.json")))
CONC = pd.read_csv(os.path.join(SAINTS, "results/concentration.csv")).set_index("saint")
DC = pd.read_csv(os.path.join(SAINTS, "results/dedication_counts.csv")).set_index("dedication").churches
W = json.load(open(os.path.join(SAINTS, "data/saints.json")))
C = counties_km(os.path.join(SAINTS, "data/raw/counties.geojson"))

pts = np.array(W["pts"]); names = np.array(W["names"])
x, y = to_km(pts[:, 1], pts[:, 0]); sn = names[pts[:, 2].astype(int)]
assert len(pts) == S["n_hist"]

GROUPS = [("Northumbria", ["Cuthbert", "Aidan", "Oswald", "Wilfrid", "Hilda"], "#2C5DA8"),
          ("Mercia", ["Chad"], "#C2412D"),
          ("East Anglia", ["Edmund", "Botolph"], "#D99A0B"),
          ("Devon and Cornwall", ["Petroc"], "#1E9C8C"),
          ("Wales", ["David"], "#7A3E9D"),
          ("Scotland", ["Columba", "Ninian"], "#4F8A2A")]

fig = new_fig()
words(fig, 0.045, 0.972, [("Where do Britain's", FG)])
words(fig, 0.045, 0.924, [("local", GROUPS[0][2]), ("saints", GROUPS[4][2]), ("live?", FG)])
fig.text(0.045, 0.862, f"{S['n_hist']:,} churches in Great Britain with a dedication on OpenStreetMap (grey). The coloured dots are\n"
         "churches of saints who still keep to the old kingdoms and regions where they lived and preached.",
         family=SER, fontsize=14.5, color=FG, va="top", linespacing=1.15)

ax = fig.add_axes([-0.02, 0.25, 0.62, 0.575]); ax.set_facecolor(BGC)
C.plot(ax=ax, color=LAND, edgecolor=BGC, linewidth=0.5, zorder=0)
ax.scatter(x, y, s=1.5, color="#ADA494", lw=0, zorder=1, rasterized=True)
for g, ss, c in GROUPS:
    m = np.isin(sn, ss)
    ax.scatter(x[m], y[m], s=13, color=c, lw=0.35, edgecolor="white", zorder=3)
ax.set_xlim(-10, 660); ax.set_ylim(0, 1000); ax.set_aspect(1); ax.axis("off")


def note(txt, xy, xyt, ha="left"):
    ax.annotate(txt, xy=xy, xytext=xyt, family=MONO, fontsize=10.2, color=FG, ha=ha, va="center", zorder=8,
                arrowprops=dict(arrowstyle="-", color=FG, lw=.8), path_effects=halo(3))


note("Lindisfarne:\nAidan, Cuthbert", (412, 641), (500, 705), ha="left")
note("Chad's\nLichfield", (411, 309), (590, 420), ha="left")
note("Petroc's\nPadstow", (191, 75), (120, 160), ha="center")
note("St Davids", (175, 225), (40, 290), ha="center")

# key with church counts
fig.text(0.62, 0.8, "THE REGIONAL SAINTS (CHURCHES IN BRITAIN)", family=MONO, fontsize=11, color=MUT)
yy = 0.778
for g, ss, c in GROUPS:
    fig.lines.append(Line2D([0.632], [yy + 0.001], marker="o", ms=9, color=c, mec="white", mew=0.6, transform=fig.transFigure))
    fig.text(0.648, yy, g, family=SER, fontsize=12.5, color=FG, va="center", weight=600)
    txt = ", ".join(f"{s} {DC[s]}" for s in ss)
    if len(ss) > 3:
        txt = ", ".join(f"{s} {DC[s]}" for s in ss[:3]) + ",\n" + ", ".join(f"{s} {DC[s]}" for s in ss[3:])
    fig.text(0.648, yy - 0.0105, txt, family=MONO, fontsize=9.6, color=MUT, va="top", linespacing=1.25)
    yy -= 0.034 + (0.016 if len(ss) > 3 else 0)

# Wales's share of all the churches mapped, counted from the points
cty = np.array(W["counties"])[pts[:, 3].astype(int)]
nat = C.set_index("county").nation
wales_share = 100 * np.mean(nat.reindex(cty).values == "Wales")
loc = dict(S["local"]); nt = S["nation_top"]
items = [
    (f"{DC['Mary']:,}", FG,
     f"churches are dedicated to Mary, first in England\nand Wales. Scotland's first is Andrew ({nt['Scotland']['Andrew']})."),
    (f"{loc['Cornwall']}", "#9A6B32",
     f"saints have churches in Cornwall and nowhere\nelse in Britain. Gwynedd: {loc['Gwynedd']}. Dyfed: {loc['Dyfed']}."),
    (f"{CONC.top_share['Petroc']:.0f}%", GROUPS[3][2],
     f"of Petroc's {CONC.n['Petroc']} churches are in Devon, the highest\nshare in one county of any saint with 15 or more."),
    (f"{CONC.wales['David']:.0f}%", GROUPS[4][2],
     f"of David's {CONC.n['David']} churches are in Wales, which has\n{wales_share:.0f}% of all the churches on this map."),
]
headlines(fig, [0.62, 0.25, 0.37, 0.298], items, big=34, step=0.25, sub_off=0.125)

# bottom strip: top five in each nation
label(fig, 0.045, 0.232, "THE FIVE COMMONEST DEDICATIONS IN EACH NATION (REGIONAL SAINTS IN COLOUR)")
GC = {s: c for g, ss, c in GROUPS for s in ss}
for k, n in enumerate(["England", "Wales", "Scotland"]):
    a = fig.add_axes([0.13 + k * 0.315, 0.08, 0.17, 0.115]); a.axis("off")
    top5 = list(nt[n].items())[:5]; mx = top5[0][1]
    fig.text(0.045 + k * 0.315, 0.212, n, family=MONO, fontsize=12.5, color=FG, va="top")
    for i, (sname, v) in enumerate(top5):
        a.barh(4 - i, v / mx, height=.66, color=GC.get(sname, "#CBBFAE"))
        a.text(-0.04, 4 - i, sname, family=SER, fontsize=12, color=FG, ha="right", va="center")
        a.text(v / mx + 0.04, 4 - i, f"{v:,}", family=MONO, fontsize=10, color=MUT, va="center")
    a.set_xlim(0, 1.25); a.set_ylim(-.6, 4.6)

footer(fig, f"Data: © OpenStreetMap contributors (ODbL), Christian places of worship downloaded 26 October 2026; Church of England, Church\n"
       "in Wales, Church of Scotland, Scottish Episcopal and untagged churches. Dedication from the dedication tag or the name. Counties from\n"
       "ONS 2025 boundaries (OGL v3). Scotland is thinly covered. Analysis and chart: Tristan Hotham, with Python and matplotlib.")
fig.savefig(os.path.join(HERE, "where_local_saints_live.png"), dpi=200, facecolor=BGC)
print("written", wales_share)
