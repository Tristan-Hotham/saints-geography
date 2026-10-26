# The geography of saints

**Read the post and map any saint:** https://tristan-hotham.github.io/saints-geography/

**Archived data and code:** [doi:10.5281/zenodo.23676497](https://doi.org/10.5281/zenodo.23676497)

This project maps church dedications across Great Britain from OpenStreetMap, to show where each saint's following lies.

## Findings

- The analysis maps 17,116 dedicated churches with 708 different dedications.
- Mary leads in England (2,351) and Wales (130). In Wales, David is second (71). In Scotland, Andrew is first (50), ahead of Mary.
- Regional saints keep their old territories. Cuthbert, Aidan, Oswald, Wilfrid and Hilda belong to the old Northumbria, Chad to Mercia, Botolph and Edmund to East Anglia, Petroc to Devon and Cornwall, and Columba and Ninian to Scotland.
- Cornwall has 98 dedications found nowhere else in Britain, more than any other county. Gwynedd (54) and Dyfed (41) come next.

## Method

1. Churches are features tagged `amenity=place_of_worship` and `religion=christian`, downloaded through the Overpass API on 26 October 2026.
2. The dedication comes from the `dedication` tag, or else from the name, including Welsh forms (`saints.py`).
3. The analysis keeps churches of the Church of England, Church in Wales, Church of Scotland and Scottish Episcopal Church, plus churches with no denomination tagged. Roman Catholic and nonconformist churches are left out.
4. Counties are ceremonial (England), preserved (Wales) and council areas (Scotland). Distinctiveness is the location quotient among saints with 15 or more churches, needing 4 or more churches in the county.

Scottish parish churches are often named after the parish, not a saint, so Scotland is thinly covered.

## Files

| Path | What it is |
|---|---|
| `analysis.py`, `saints.py` | Analysis and dedication parsing |
| `data/raw/osm_pubs_churches.json.gz` | The OpenStreetMap extract (pubs and churches; this project uses the churches) |
| `data/raw/counties.geojson` | Counties from ONS 2025 boundaries |
| `results/dedication_counts.csv` | Churches per dedication |
| `results/most_distinctive_by_county.csv` | Most over-represented saint per county |
| `results/concentration.csv` | How concentrated each saint is, with its nation split |
| `results/summary.json` | Headline figures, top saints by nation, saints found in only one county |
| `index.html`, `data/` | The web page and its data |

## Sources and licences

- Churches: © OpenStreetMap contributors, Open Database Licence (the extract and derived data are under the ODbL).
- Boundaries: Office for National Statistics, Open Government Licence v3. Contains OS data © Crown copyright and database right.
- Base map: © Esri.

Code is MIT licensed.

AI use: written with drafting, data and coding help from Claude (Anthropic).

Tristan Hotham, independent researcher, 2026.
