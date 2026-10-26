"""The geography of saints: church dedications across Great Britain.

Input: data/raw/osm_pubs_churches.json.gz (OpenStreetMap, Overpass API; rows: key, type P/C, lat, lon, name, old_name,
denomination, building, historic, heritage, start_date, dedication, addr). This script uses the churches (type C).
Output: results/ tables and data/saints.json for the web page.
"""
import gzip, json, sys
import numpy as np, pandas as pd, geopandas as gpd
from saints import saint

rows = json.load(gzip.open('data/raw/osm_pubs_churches.json.gz', 'rt'))
C = pd.DataFrame([r for r in rows if r[1] == 'C'], columns=['key', 't', 'lat', 'lon', 'name', 'old_name', 'denom', 'building',
                                                          'historic', 'heritage', 'start', 'dedication', 'addr'])
counties = gpd.read_file('data/raw/counties.geojson')[['county', 'nation', 'geometry']]
g = gpd.GeoDataFrame(C, geometry=gpd.points_from_xy(C.lon, C.lat), crs=4326)
g = gpd.sjoin(g, counties, how='left', predicate='within').drop(columns='index_right')
C = pd.DataFrame(g[g.county.notna()].drop(columns='geometry'))
C['saint'] = [saint(n, d) for n, d in zip(C.name, C.dedication)]
den = C.denom.replace({'roman_catholic': 'catholic', 'church_of_england': 'anglican', 'church_in_wales': 'anglican',
                       'scottish_episcopal': 'anglican', 'episcopal': 'anglican', 'church_of_scotland': 'anglican', 'presbyterian': 'presbyterian'})
C['denom2'] = np.where(den.isin(['anglican', 'catholic']), den, np.where(den == '', 'unknown', 'other'))
print('churches in GB', len(C), 'with dedication', C.saint.notna().sum(), file=sys.stderr)

D = C[C.saint.notna()].copy()
# Mainly the historic churches: established churches (Church of England, Church in Wales, Church of Scotland, Scottish
# Episcopal) or unknown denomination (OSM leaves many parish churches untagged). Roman Catholic and nonconformist chapels,
# mostly 19th and 20th century, are left out.
H = D[D.denom2.isin(['anglican', 'unknown'])]
top = H.saint.value_counts()

cty = H.groupby('county').size()
common = top[top >= 15].index
tab = H[H.saint.isin(common)].groupby(['saint', 'county']).size().unstack(fill_value=0)
lq = tab.div(cty, axis=1).div(top[common] / len(H), axis=0)
dist = []
for c in tab.columns:
    s = lq[c][tab[c] >= 4].sort_values(ascending=False)
    if len(s):
        dist.append({'county': c, 'saint': s.index[0], 'count': int(tab.loc[s.index[0], c]), 'lq': round(float(s.iloc[0]), 2),
                     'second': s.index[1] if len(s) > 1 else None, 'top': H[H.county == c].saint.value_counts().index[0],
                     'n': int(cty[c])})
dist = pd.DataFrame(dist)

# How concentrated is each saint? Share of its churches in its single most common county and nation split
conc = []
for sname, n in top[top >= 10].items():
    sub = H[H.saint == sname]
    vc = sub.county.value_counts()
    nat = sub.nation.value_counts(normalize=True)
    conc.append({'saint': sname, 'n': int(n), 'top_county': vc.index[0], 'top_share': round(100 * vc.iloc[0] / n, 1),
                 'england': round(100 * nat.get('England', 0), 1), 'wales': round(100 * nat.get('Wales', 0), 1),
                 'scotland': round(100 * nat.get('Scotland', 0), 1)})
conc = pd.DataFrame(conc).sort_values('top_share', ascending=False)

# saints whose every church in Britain lies in a single county
onec = H.groupby('saint').county.agg(['nunique', 'first', 'size'])
onec = onec[onec['nunique'] == 1]
local = onec.groupby('first').size().sort_values(ascending=False)
local_names = onec.reset_index().groupby('first').saint.apply(lambda x: sorted(x)[:40]).to_dict()
nat_top = {n: H[H.nation == n].saint.value_counts().head(12).to_dict() for n in ['England', 'Wales', 'Scotland']}
out = {'n_churches': int(len(C)), 'n_dedicated': int(len(D)), 'n_hist': int(len(H)), 'n_saints': int(top.size),
       'top': [[k, int(v)] for k, v in top.head(60).items()], 'nation_top': nat_top,
       'local': [[c, int(n)] for c, n in local.head(15).items()], 'local_names': {c: local_names[c] for c in local.head(15).index},
       'distinct': json.loads(dist.to_json(orient='records')), 'concentrated': json.loads(conc.head(40).to_json(orient='records'))}
json.dump(out, open('results/summary.json', 'w'), indent=1)
top.rename('churches').to_csv('results/dedication_counts.csv', index_label='dedication')
dist.to_csv('results/most_distinctive_by_county.csv', index=False)
conc.to_csv('results/concentration.csv', index=False)

names = list(top.index)
idx = {n: i for i, n in enumerate(names)}
ci = {c: i for i, c in enumerate(sorted(H.county.unique()))}
web = {'names': names, 'counts': [int(v) for v in top.values],
       'pts': [[round(a, 4), round(b, 4), idx[s], ci[c]] for a, b, s, c in zip(H.lat, H.lon, H.saint, H.county)],
       'distinct': json.loads(dist.to_json(orient='records')), 'conc': json.loads(conc.to_json(orient='records')), 'nation_top': nat_top,
       'local': [[c, int(n)] for c, n in local.head(15).items()], 'local_names': {c: local_names[c] for c in local.head(15).index},
       'n_hist': int(len(H)), 'n_churches': int(len(C)), 'counties': sorted(H.county.unique()), 'county_n': [int(cty[c]) for c in sorted(H.county.unique())]}
json.dump(web, open('data/saints.json', 'w'), separators=(',', ':'))
print(top.head(40).to_string())
print(dist.sort_values('lq', ascending=False).to_string())
print(conc.head(40).to_string())
print(json.dumps(nat_top, indent=0))
